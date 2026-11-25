"""Sweep runner: detect, refine, eliminate, in resumable stages.

    python -m skywatch.sweep.run detect    [--kind blind|control|seeded] [--regions ID ...]
    python -m skywatch.sweep.run refine    [--top 20]
    python -m skywatch.sweep.run sensors   [--kind blind]     thermal, radar, night lights
    python -m skywatch.sweep.run eliminate

Each stage writes one JSON-lines file per region under ``output/candidates/
<stage>/`` and skips regions already done unless ``--force`` is given, so an
interrupted sweep continues where it stopped.
"""
from __future__ import annotations

import argparse
import json
import logging
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from ..core import config, io
from ..core.models import Candidate, Region, load_candidates, save_candidates
from . import regions as region_defs

log = logging.getLogger("skywatch.sweep")

CAND_DIR = config.OUTPUT / "candidates"
REGION_DIR = config.OUTPUT / "regions"


def all_regions(kind: str | None = None, ids: Sequence[str] | None = None) -> list[Region]:
    """Blind and control regions plus seeded regions from reports when available."""
    found = list(region_defs.REGIONS)
    seeded_file = config.OUTPUT / "seeded_regions.json"
    if seeded_file.exists():
        for raw in json.loads(seeded_file.read_text()):
            raw["bbox"] = tuple(raw["bbox"])
            raw["season"] = tuple(raw["season"])
            found.append(Region(**raw))
    if kind:
        found = [r for r in found if r.kind == kind]
    if ids:
        wanted = set(ids)
        found = [r for r in found if r.id in wanted]
    return found


def _figure(region: Region, diag: dict[str, Any], candidates: list[Candidate], path: Path) -> None:
    """Overview picture: first year, last year, break-year map, candidates."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ..detect.optical_change import season_middle, season_window

    grid, years = diag["grid"], diag["years"]
    first = io.s2_composite(grid, *season_window(years[0], region.season), max_scenes=3,
                            prefer_date=season_middle(years[0], region.season))
    last = io.s2_composite(grid, *season_window(years[-1], region.season), max_scenes=3,
                           prefer_date=season_middle(years[-1], region.season))
    step = 4 if grid.width > 1200 else 2
    stretch = None
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.4))
    for ax, comp, year in ((axes[0], first, years[0]), (axes[1], last, years[-1])):
        if comp is None:
            ax.set_title(f"{year}: no data")
            continue
        rgb = io.rgb_image(comp["red"][::step, ::step], comp["green"][::step, ::step],
                           comp["blue"][::step, ::step], stretch=stretch)
        if stretch is None:
            finite = np.dstack([comp["red"], comp["green"], comp["blue"]])[::step * 2, ::step * 2]
            finite = finite[np.isfinite(finite)]
            if finite.size:
                stretch = (float(np.percentile(finite, 1)), float(np.percentile(finite, 99)))
                rgb = io.rgb_image(comp["red"][::step, ::step], comp["green"][::step, ::step],
                                   comp["blue"][::step, ::step], stretch=stretch)
        ax.imshow(rgb)
        ax.set_title(f"{year}  ({', '.join(comp['dates'][:3])})", fontsize=9)
    year_map = np.where(diag["step_year"] > 0, diag["step_year"], diag["transient_year"]).astype(float)
    year_map[year_map == 0] = np.nan
    im = axes[2].imshow(year_map[::step, ::step], cmap="turbo", vmin=years[0], vmax=years[-1],
                        interpolation="nearest")
    axes[2].set_facecolor("#111")
    fig.colorbar(im, ax=axes[2], fraction=0.04, label="year the change appeared")
    for cand in candidates[:40]:
        col, row = grid.lonlat_to_xy(cand.lon, cand.lat)
        axes[1].plot(col / step, row / step, "o", ms=9, mfc="none", mec="cyan", mew=1.2)
    axes[2].set_title(f"changes found: {diag['n_blobs']} blobs", fontsize=9)
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle(f"{region.id}  {region.name}   Contains modified Copernicus Sentinel data", fontsize=10)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=70)
    plt.close(fig)


def detect_region(region: Region, res: float = 20.0, max_candidates: int = 120,
                  force: bool = False) -> dict[str, Any]:
    """Run the optical change detector on one region and save raw candidates."""
    from ..detect.optical_change import detect_changes, detect_event_change

    out = CAND_DIR / "raw" / f"{region.id}.jsonl"
    summary_file = REGION_DIR / f"{region.id}.json"
    if summary_file.exists() and not force:
        return json.loads(summary_file.read_text())
    started = time.time()
    diag: dict[str, Any] = {}
    summary: dict[str, Any] = {"region": region.id, "name": region.name, "kind": region.kind,
                               "biome": region.biome, "bbox": list(region.bbox),
                               "area_km2": region_defs.area_km2(region), "res_m": res}
    try:
        candidates = detect_changes(region, res=res, max_candidates=max_candidates, diagnostics=diag)
    except Exception as exc:
        summary.update({"status": "failed", "error": f"{type(exc).__name__}: {exc}",
                        "trace": traceback.format_exc()[-1500:]})
        REGION_DIR.mkdir(parents=True, exist_ok=True)
        summary_file.with_suffix(".failed.json").write_text(json.dumps(summary, indent=1))
        return summary
    event_date = (region.expect or {}).get("event_date") or (region.seed or {}).get("datetime")
    if event_date:
        try:
            events = detect_event_change(region, str(event_date)[:10])
            summary["event_date"] = str(event_date)[:10]
            summary["n_event_candidates"] = len(events)
            candidates = events + candidates
        except Exception as exc:
            summary["event_error"] = f"{type(exc).__name__}: {exc}"
    save_candidates(out, candidates)
    kinds: dict[str, int] = {}
    for cand in candidates:
        kinds[cand.measurements["kind"]] = kinds.get(cand.measurements["kind"], 0) + 1
    summary.update({
        "status": "ok" if diag else "skipped_too_few_years",
        "years": diag.get("years", []), "n_blobs_total": diag.get("n_blobs", 0),
        "n_candidates_kept": len(candidates), "kinds": kinds,
        "step_fraction": diag.get("step_fraction"), "transient_fraction": diag.get("transient_fraction"),
        "valid_fraction": diag.get("valid_fraction"), "seconds": round(time.time() - started, 1)})
    if diag:
        try:
            _figure(region, diag, candidates, REGION_DIR / f"{region.id}.png")
        except Exception as exc:
            summary["figure_error"] = f"{type(exc).__name__}: {exc}"
    REGION_DIR.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(json.dumps(summary, indent=1))
    return summary


def refine_region(region: Region, top: int = 20, force: bool = False) -> int:
    """Tighten onset dates of the top candidates of one region; save them."""
    from ..detect.optical_change import refine_onset

    out = CAND_DIR / "refined" / f"{region.id}.jsonl"
    if out.exists() and not force:
        return len(load_candidates(out))
    raw = load_candidates(CAND_DIR / "raw" / f"{region.id}.jsonl")
    events = [c for c in raw if c.detector == "optical_event"][:max(top // 2, 5)]
    yearly = [c for c in raw if c.detector != "optical_event"]
    candidates = events + yearly[:max(top - len(events), 0)]

    def one(cand: Candidate) -> Candidate:
        try:
            return refine_onset(cand)
        except Exception as exc:
            cand.measurements["onset_note"] = f"refine failed: {type(exc).__name__}"
            return cand

    with ThreadPoolExecutor(3) as pool:
        refined = list(pool.map(one, candidates))
    save_candidates(out, refined)
    return len(refined)


def sensors_region(region: Region, force: bool = False, radar: bool = False) -> dict[str, Any]:
    """Run the non-optical detectors on one region: thermal, radar, night lights.

    These look for the signatures that have no onset date: persistent thermal
    anomalies, bright radar targets in empty terrain and isolated lights.
    Each detector that fails or is unavailable is recorded with its reason.
    """
    out = CAND_DIR / "sensors" / f"{region.id}.jsonl"
    note = CAND_DIR / "sensors" / f"{region.id}.json"
    if note.exists() and not force:
        return json.loads(note.read_text())
    found: list[Candidate] = []
    report: dict[str, Any] = {"region": region.id}
    jobs: list[tuple[str, Any]] = []
    from ..detect import landsat, sar
    jobs.append(("thermal", lambda: landsat.detect_thermal_anomalies(region)))
    if radar:
        jobs.append(("radar", lambda: sar.detect_bright_scatterers(region, "2024-01-01", "2026-11-01")))
    try:
        from ..detect import nightlights
        jobs.append(("lights", lambda: nightlights.detect_isolated_lights(region)))
    except Exception as exc:
        report["lights"] = f"not available: {type(exc).__name__}"
    for name, job in jobs:
        started = time.time()
        try:
            result = job()
            found.extend(result)
            report[name] = {"candidates": len(result), "seconds": round(time.time() - started, 1)}
        except Exception as exc:
            report[name] = {"error": f"{type(exc).__name__}: {str(exc)[:200]}"}
    save_candidates(out, found)
    note.write_text(json.dumps(report, indent=1))
    return report


def _refine_job(region: Region, top: int, force: bool) -> tuple[str, int]:
    return region.id, refine_region(region, top, force)


def _eliminate_job(region: Region, force: bool) -> tuple[str, int]:
    return region.id, eliminate_region(region, force)


def eliminate_region(region: Region, force: bool = False, confirm: bool = True) -> int:
    """Run sensor confirmation and every elimination check; save final candidates."""
    from ..eliminate.engine import run_all

    out = CAND_DIR / "final" / f"{region.id}.jsonl"
    if out.exists() and not force:
        return len(load_candidates(out))
    candidates = load_candidates(CAND_DIR / "refined" / f"{region.id}.jsonl")
    # Undated finds from the other sensors: the strongest few of each kind.
    extra = load_candidates(CAND_DIR / "sensors" / f"{region.id}.jsonl")
    for detector, keep in (("landsat_thermal", 4), ("sar_bright", 4), ("viirs_light", 3)):
        candidates += [c for c in extra if c.detector == detector][:keep]
    done = run_all(candidates, workers=4, confirm=confirm, progress=False)
    save_candidates(out, done)
    return len(done)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("stage", choices=["detect", "refine", "sensors", "eliminate"])
    parser.add_argument("--kind", choices=["blind", "control", "seeded"])
    parser.add_argument("--regions", nargs="*")
    parser.add_argument("--res", type=float, default=20.0)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.WARNING, format="%(asctime)s %(name)s %(message)s")
    chosen = all_regions(args.kind, args.regions)
    print(f"{args.stage}: {len(chosen)} regions", flush=True)
    if args.stage == "detect":
        with ProcessPoolExecutor(args.workers) as pool:
            futures = {pool.submit(detect_region, r, args.res, 120, args.force): r for r in chosen}
            for future in as_completed(futures):
                s = future.result()
                print(f"{s['region']:<20} {s.get('status'):<8} years={len(s.get('years', []))} "
                      f"blobs={s.get('n_blobs_total')} kept={s.get('n_candidates_kept')} "
                      f"{s.get('seconds')}s {s.get('error', '')}", flush=True)
    elif args.stage == "sensors":
        with ProcessPoolExecutor(args.workers) as pool:
            for future in as_completed([pool.submit(sensors_region, r, args.force) for r in chosen]):
                print(json.dumps(future.result()), flush=True)
    elif args.stage == "refine":
        ready = [r for r in chosen if (CAND_DIR / "raw" / f"{r.id}.jsonl").exists()]
        with ProcessPoolExecutor(args.workers) as pool:
            for future in as_completed([pool.submit(_refine_job, r, args.top, args.force) for r in ready]):
                print(*future.result(), flush=True)
    else:
        # One process only: the Wikidata client paces its requests per process.
        for region in chosen:
            if (CAND_DIR / "refined" / f"{region.id}.jsonl").exists():
                print(*_eliminate_job(region, args.force), flush=True)


if __name__ == "__main__":
    main()
