"""Tamper-evident manifests and OpenTimestamps proofs for published evidence.

What a proof shows, and what it does not
----------------------------------------
* ``manifest`` hashes every evidence file with SHA-256. Changing one byte of
  any listed file changes its hash and therefore the manifest hash.
* ``stamp`` asks public OpenTimestamps calendar servers to commit to the
  SHA-256 of one file (normally ``manifest.json``). Only a salted SHA-256
  digest ever leaves this machine; file contents, names and paths never do.
* A fresh proof is PENDING. It holds a calendar's promise to include the
  digest in a Bitcoin transaction and proves nothing by itself to a sceptic
  who does not trust that calendar. ``upgrade``, run hours later, replaces the
  promise with the Merkle path to a Bitcoin block header.
* An upgraded proof, verified against the Bitcoin block chain, shows that
  these exact bytes existed NO LATER THAN the time of that block (accurate to
  a few hours). It does not show when the bytes were first created, who
  created them, or that anything they say is true. A timestamp on a wrong
  analysis is still a wrong analysis.
* Full verification needs the header of the attested block from a Bitcoin
  node or a block explorer. Neither is reachable from this environment, so
  this module reports proofs as ``bitcoin_anchored`` (a block-header
  attestation is present in the proof) but never as verified. Anyone can
  finish the check elsewhere with ``ots verify <file>.ots``.

Only the two calendars in ``CALENDARS`` are reachable here, so a proof has at
most two independent calendar commitments instead of the client default of
several. Calendar requests are made by the OpenTimestamps client itself, which
sends its own generic ``OpenTimestamps-Client`` user agent.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from skywatch.core import config

#: The only calendar servers this environment may contact.
CALENDARS: tuple[str, ...] = (
    "https://alice.btc.calendar.opentimestamps.org",
    "https://bob.btc.calendar.opentimestamps.org",
)

MANIFEST_NAME = "manifest.json"
MANIFEST_SCHEMA = "skywatch-manifest/1"

_CACHE = config.CACHE / "provenance" / "ots"
_CHUNK = 1 << 20
#: (minimum calendars that must reply, per-calendar timeout in seconds).
#: The last attempt accepts a single calendar rather than failing outright.
_STAMP_ATTEMPTS: tuple[tuple[int, int], ...] = ((2, 15), (2, 30), (1, 30))
_UPGRADE_TIMEOUT_S = 20


# --------------------------------------------------------------------------
# Manifests
# --------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    """Hex SHA-256 of a file, read in chunks."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while chunk := handle.read(_CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(obj: Any) -> bytes:
    """Deterministic UTF-8 JSON: sorted keys, no whitespace, ASCII escapes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _manifest_digest(files: list[dict[str, Any]]) -> str:
    core = {"schema": MANIFEST_SCHEMA, "hash": "sha256", "files": files}
    return hashlib.sha256(canonical_json(core)).hexdigest()


def manifest(paths: Sequence[Path], root: Path) -> dict[str, Any]:
    """Hash ``paths`` into a manifest keyed by POSIX paths relative to ``root``.

    Returns ``{"schema", "hash", "files": [{"path", "sha256", "size"}, ...],
    "manifest_sha256"}`` with files sorted by path and duplicates removed.
    ``manifest_sha256`` is the SHA-256 of ``canonical_json`` of the other three
    keys, so it changes if any file, name or size changes. The manifest holds
    no time and no absolute path, so it is identical on every machine.
    Raises ``FileNotFoundError`` for a missing file and ``ValueError`` for a
    path outside ``root``.
    """
    base = Path(root).resolve()
    entries: dict[str, dict[str, Any]] = {}
    for raw in paths:
        path = Path(raw)
        if not path.is_file():
            raise FileNotFoundError(f"not a file: {path}")
        resolved = path.resolve()
        try:
            rel = resolved.relative_to(base).as_posix()
        except ValueError as exc:
            raise ValueError(f"{path} is not inside manifest root {root}") from exc
        entries[rel] = {"path": rel, "sha256": sha256_file(resolved),
                        "size": resolved.stat().st_size}
    files = [entries[key] for key in sorted(entries)]
    return {"schema": MANIFEST_SCHEMA, "hash": "sha256", "files": files,
            "manifest_sha256": _manifest_digest(files)}


def _is_bookkeeping(rel: Path) -> bool:
    """Manifest and proof files, which a manifest must not list."""
    name = rel.name
    if name == MANIFEST_NAME or name.endswith((".ots", ".ots.bak")):
        return True
    if ".ots." in name and name.endswith(".bak"):
        return True
    return len(rel.parts) == 1 and name.startswith("manifest.") and name.endswith(".json")


def _evidence_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.rglob("*")
                  if p.is_file() and not _is_bookkeeping(p.relative_to(directory)))


def _proof_path(path: Path) -> Path:
    path = Path(path)
    return path if path.name.endswith(".ots") else path.with_name(path.name + ".ots")


def write_manifest(directory: Path) -> Path:
    """Write ``manifest.json`` covering every file under ``directory``.

    Subdirectories are included; ``manifest.json``, superseded manifests
    (``manifest.<hash>.json``) and proof files (``*.ots``, ``*.ots.bak``) are
    not. Re-running on unchanged files leaves the manifest byte-identical. If
    the files changed and the old manifest already has a proof, both are kept
    as ``manifest.<first 12 hex of the old file's SHA-256>.json`` (+ ``.ots``)
    so an earlier timestamp is never destroyed.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"not a directory: {directory}")
    data = manifest(_evidence_files(directory), directory)
    text = json.dumps(data, indent=1, sort_keys=True) + "\n"
    target = directory / MANIFEST_NAME
    if target.exists():
        if target.read_text() == text:
            return target
        old_proof = _proof_path(target)
        if old_proof.exists():
            stem = f"manifest.{sha256_file(target)[:12]}.json"
            target.rename(directory / stem)
            old_proof.rename(directory / (stem + ".ots"))
            old_backup = old_proof.with_name(old_proof.name + ".bak")
            if old_backup.exists():
                old_backup.rename(directory / (stem + ".ots.bak"))
    tmp = directory / (MANIFEST_NAME + ".tmp")
    tmp.write_text(text)
    tmp.replace(target)
    return target


def check_manifest(directory: Path) -> dict[str, Any]:
    """Compare the files under ``directory`` with its ``manifest.json``.

    Returns ``{"ok", "changed", "missing", "unlisted", "manifest_sha256_ok",
    "n_files", "detail"}``. ``ok`` is True only when every listed file is
    present with the recorded hash and size, nothing unlisted exists, and the
    manifest's own hash is consistent. A missing or unreadable manifest gives
    ``ok`` False with the reason in ``detail``.
    """
    directory = Path(directory)
    result: dict[str, Any] = {"ok": False, "changed": [], "missing": [], "unlisted": [],
                              "manifest_sha256_ok": False, "n_files": 0, "detail": ""}
    target = directory / MANIFEST_NAME
    try:
        recorded = json.loads(target.read_text())
        listed = {str(f["path"]): f for f in recorded["files"]}
        digest_ok = recorded["manifest_sha256"] == _manifest_digest(recorded["files"])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result["detail"] = f"manifest unreadable: {type(exc).__name__}: {exc}"
        return result
    on_disk = {p.relative_to(directory).as_posix(): p for p in _evidence_files(directory)}
    for rel, entry in sorted(listed.items()):
        path = on_disk.get(rel)
        if path is None:
            result["missing"].append(rel)
        elif path.stat().st_size != entry.get("size") or sha256_file(path) != entry.get("sha256"):
            result["changed"].append(rel)
    result["unlisted"] = sorted(set(on_disk) - set(listed))
    result["manifest_sha256_ok"] = digest_ok
    result["n_files"] = len(listed)
    result["ok"] = digest_ok and not (result["changed"] or result["missing"] or result["unlisted"])
    result["detail"] = ("all files match the manifest" if result["ok"] else
                        f"{len(result['changed'])} changed, {len(result['missing'])} missing, "
                        f"{len(result['unlisted'])} unlisted, manifest hash "
                        f"{'consistent' if digest_ok else 'INCONSISTENT'}")
    return result


# --------------------------------------------------------------------------
# OpenTimestamps
# --------------------------------------------------------------------------

def _client() -> str | None:
    """Path of the ``ots`` command installed beside this interpreter."""
    beside = Path(sys.executable).parent / "ots"
    if beside.exists():
        return str(beside)
    return shutil.which("ots")


def _run(args: list[str], timeout_s: float) -> tuple[int, str]:
    """Run the client restricted to ``CALENDARS``; return (exit code, log tail)."""
    client = _client()
    if client is None:
        return 127, "OpenTimestamps client (ots) is not installed"
    _CACHE.mkdir(parents=True, exist_ok=True)
    command = [client, "--no-default-whitelist"]
    for url in CALENDARS:
        command += ["-l", url]
    command += ["--cache", str(_CACHE), "--no-bitcoin", *args]
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout_s,
                              check=False)
    except subprocess.TimeoutExpired:
        return 124, f"ots client timed out after {timeout_s:.0f} s"
    except OSError as exc:
        return 126, f"could not run ots client: {exc}"
    lines = [line.strip() for line in (done.stderr + "\n" + done.stdout).splitlines() if line.strip()]
    return done.returncode, " | ".join(lines[-4:])


def info(path: Path) -> dict[str, Any]:
    """Parse what a proof currently attests, without any network access.

    ``path`` is the stamped file or its ``.ots`` proof. Returns ``{"status",
    "proof", "file_sha256", "matches_file", "pending_calendars",
    "bitcoin_block_heights", "other_attestations", "calendar_claimed_utc",
    "detail"}``. ``status`` is ``"missing"`` (no proof file), ``"invalid"``
    (not a parseable proof), ``"mismatch"`` (the file beside the proof no
    longer has the stamped hash: it was edited after stamping),
    ``"bitcoin_anchored"`` (a Bitcoin block-header attestation is present, NOT
    verified against the chain here) or ``"pending"`` (calendar promises only).
    ``matches_file`` is None when the stamped file is not beside the proof.
    ``calendar_claimed_utc`` maps calendar URL to the submission time the
    calendar wrote into its commitment: an unauthenticated hint, not evidence.
    """
    proof = _proof_path(Path(path))
    result: dict[str, Any] = {
        "status": "missing", "proof": str(proof), "file_sha256": None, "matches_file": None,
        "pending_calendars": [], "bitcoin_block_heights": [], "other_attestations": [],
        "calendar_claimed_utc": {}, "detail": "",
    }
    if not proof.is_file():
        result["detail"] = f"no proof file at {proof}"
        return result
    try:
        from opentimestamps.core.notary import (  # type: ignore[import-untyped]
            BitcoinBlockHeaderAttestation, PendingAttestation)
        from opentimestamps.core.op import OpAppend, OpPrepend, OpSHA256  # type: ignore[import-untyped]
        from opentimestamps.core.serialize import (  # type: ignore[import-untyped]
            StreamDeserializationContext)
        from opentimestamps.core.timestamp import DetachedTimestampFile  # type: ignore[import-untyped]
    except ImportError as exc:
        result.update(status="invalid", detail=f"opentimestamps library unavailable: {exc}")
        return result
    try:
        with proof.open("rb") as handle:
            ctx = StreamDeserializationContext(handle)
            detached = DetachedTimestampFile.deserialize(ctx)
            ctx.assert_eof()
    except Exception as exc:  # the library raises several unrelated error types
        result.update(status="invalid",
                      detail=f"not a valid OpenTimestamps proof: {type(exc).__name__}: {exc}")
        return result

    result["file_sha256"] = detached.file_digest.hex()
    sha256_proof = isinstance(detached.file_hash_op, OpSHA256)
    original = proof.with_name(proof.name[:-len(".ots")])
    if original.is_file() and sha256_proof:
        result["matches_file"] = sha256_file(original) == result["file_sha256"]

    pending: list[str] = []
    heights: list[int] = []
    other: list[str] = []
    claimed: dict[str, str] = {}
    stack: list[tuple[Any, tuple[Any, Any]]] = [(detached.timestamp, (None, None))]
    while stack:
        node, tail = stack.pop()
        for attestation in node.attestations:
            if isinstance(attestation, BitcoinBlockHeaderAttestation):
                heights.append(int(attestation.height))
            elif isinstance(attestation, PendingAttestation):
                uri = str(attestation.uri)
                pending.append(uri)
                stamp_op, nonce_op = tail
                if (isinstance(stamp_op, OpPrepend) and len(stamp_op[0]) == 4
                        and isinstance(nonce_op, OpAppend)):
                    seconds = int.from_bytes(stamp_op[0], "big")
                    claimed[uri] = datetime.fromtimestamp(seconds, timezone.utc).strftime(
                        "%Y-%m-%dT%H:%M:%SZ")
            else:
                other.append(type(attestation).__name__)
        for op, child in node.ops.items():
            stack.append((child, (tail[1], op)))

    result["pending_calendars"] = sorted(set(pending))
    result["bitcoin_block_heights"] = sorted(set(heights))
    result["other_attestations"] = sorted(set(other))
    result["calendar_claimed_utc"] = claimed
    if not sha256_proof:
        result.update(status="invalid", detail="proof does not commit to a SHA-256 file hash")
    elif result["matches_file"] is False:
        result.update(status="mismatch", detail=(
            f"{original.name} no longer has the stamped SHA-256: it was changed after "
            "the proof was made, so the proof does not cover its current contents"))
    elif heights:
        result.update(status="bitcoin_anchored", detail=(
            f"Bitcoin block-header attestation at height(s) {sorted(set(heights))}; the bytes "
            "existed no later than that block's time. Not verified against the chain here "
            "(no Bitcoin node or block explorer reachable): run `ots verify` elsewhere."))
    elif pending:
        result.update(status="pending", detail=(
            f"pending at {len(set(pending))} calendar(s): a promise to anchor the digest in "
            "Bitcoin, not yet a proof; run upgrade() after a few hours"))
    else:
        result.update(status="invalid", detail="proof contains no usable attestation")
    return result


def stamp(path: Path) -> dict[str, Any]:
    """Create ``<path>.ots`` by submitting the file's digest to ``CALENDARS``.

    Returns ``{"status", "proof", "calendars", "detail", "file_sha256",
    "requested_utc"}``. ``status`` is ``"pending"`` for a fresh proof and
    ``"failed"`` when no proof could be made (missing file, client missing, no
    calendar reachable). ``calendars`` lists the calendars that actually
    committed, read back from the proof. An existing proof is never
    overwritten: if it still matches the file its current state is returned
    (``"pending"`` or ``"bitcoin_anchored"``); if the file has changed since,
    the result is ``"failed"`` and both files are left untouched.
    ``requested_utc`` is this machine's clock, recorded for convenience only.
    """
    path = Path(path)
    proof = _proof_path(path)
    result: dict[str, Any] = {
        "status": "failed", "proof": str(proof), "calendars": [], "detail": "",
        "file_sha256": None,
        "requested_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if path.name.endswith(".ots"):
        result["detail"] = "refusing to stamp a proof file"
        return result
    if not path.is_file():
        result["detail"] = f"not a file: {path}"
        return result
    result["file_sha256"] = sha256_file(path)

    if proof.exists():
        current = info(proof)
        result["calendars"] = current["pending_calendars"]
        if current["status"] in ("pending", "bitcoin_anchored"):
            result["status"] = current["status"]
            result["detail"] = "existing proof kept (not re-stamped): " + current["detail"]
        else:
            result["detail"] = ("existing proof kept and nothing stamped: " + current["detail"]
                                + ". Move the old proof aside to stamp the current contents.")
        return result

    log = ""
    for attempt, (minimum, timeout_s) in enumerate(_STAMP_ATTEMPTS):
        if attempt:
            time.sleep(2.0 * attempt)
        args = ["stamp", "--timeout", str(timeout_s), "-m", str(minimum)]
        for url in CALENDARS:
            args += ["-c", url]
        code, log = _run([*args, str(path)], timeout_s + 30)
        if code == 0 and proof.exists():
            break
        if proof.exists():          # partial file written by a failed attempt of ours
            proof.unlink()
        if code in (126, 127):      # client missing: retrying cannot help
            break
    if not proof.exists():
        result["detail"] = f"no calendar accepted the digest after {attempt + 1} attempt(s): {log}"
        return result

    current = info(proof)
    result["calendars"] = current["pending_calendars"]
    if current["status"] != "pending" or current["matches_file"] is not True:
        result["detail"] = "client wrote a proof that does not check out: " + current["detail"]
        return result
    result["status"] = "pending"
    result["detail"] = (
        f"digest committed by {len(result['calendars'])} of {len(CALENDARS)} calendars. PENDING: "
        "this becomes a Bitcoin-anchored proof only after upgrade(), typically some hours later.")
    return result


def upgrade(path: Path) -> dict[str, Any]:
    """Ask the calendars for the Bitcoin attestation and rewrite the proof.

    ``path`` is the stamped file or its ``.ots`` proof. Returns the ``info``
    dictionary plus ``"changed"`` (the proof file was rewritten; the previous
    version is kept as ``<proof>.bak``) and ``"client"`` (last client log
    lines). ``status`` is ``"bitcoin_anchored"``, ``"pending"`` (not yet
    anchored, or the calendars could not be reached: the proof is unchanged
    and still valid as a pending proof), ``"mismatch"``, or ``"failed"`` (no
    proof, or not parseable).
    """
    proof = _proof_path(Path(path))
    before = info(proof)
    if before["status"] in ("missing", "invalid"):
        return {**before, "status": "failed", "changed": False, "client": ""}
    if before["bitcoin_block_heights"] and not before["pending_calendars"]:
        return {**before, "changed": False, "client": "already anchored; nothing to upgrade"}
    backup = proof.with_name(proof.name + ".bak")
    if backup.exists():             # the client refuses to overwrite a backup
        tag = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup.rename(proof.with_name(f"{proof.name}.{tag}.bak"))
    original = proof.read_bytes()
    code, log = _run(["upgrade", "--timeout", str(_UPGRADE_TIMEOUT_S), str(proof)],
                     _UPGRADE_TIMEOUT_S * len(CALENDARS) + 40)
    if not proof.exists():          # client moved the proof aside, then failed to rewrite it
        proof.write_bytes(original)
    after = info(proof)
    if after["status"] in ("missing", "invalid"):
        proof.write_bytes(original)
        after = info(proof)
    changed = proof.read_bytes() != original
    if after["status"] == "pending":
        after["detail"] += f" (upgrade attempt: exit {code}; {log or 'no client output'})"
    return {**after, "changed": changed, "client": log}


def stamp_directory(directory: Path) -> dict[str, Any]:
    """Write the directory manifest and stamp it.

    Returns the ``stamp`` result plus ``"manifest"`` (path), ``"manifest_sha256"``
    and ``"n_files"``. One proof on the manifest covers every listed file. An
    empty directory is not stamped (``status`` ``"failed"``).
    """
    target = write_manifest(Path(directory))
    data = json.loads(target.read_text())
    extra = {"manifest": str(target), "manifest_sha256": data["manifest_sha256"],
             "n_files": len(data["files"])}
    if not data["files"]:
        return {"status": "failed", "proof": str(_proof_path(target)), "calendars": [],
                "detail": "directory holds no evidence files; nothing to attest",
                "file_sha256": None, "requested_utc": None, **extra}
    return {**stamp(target), **extra}
