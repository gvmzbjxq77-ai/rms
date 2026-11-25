"""Recorded-event and restricted-area checks: aviation accidents, meteorites, ranges.

Three elimination checks compare a candidate with catalogues of known events
and places: the NTSB aviation accident database (plus Wikidata accident
items), the Meteoritical Society "Meteorite Landings" table, and a curated
list of launch sites, rocket-stage drop zones and weapons ranges. Each
catalogue has stated coverage limits; a catalogue that is unavailable or
does not cover the candidate period yields ``not_run``, never a pass.
"""
from __future__ import annotations

import json
import math
import shutil
import time
import zipfile
from datetime import date
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd
import requests

from skywatch.core import config
from skywatch.core.models import Candidate, CheckResult
from skywatch.eliminate import wikidata
from skywatch.eliminate.wikidata import footprint_radius_km, haversine_km, onset_window, valid_point

RECORDS_DIR = config.DATA / "records"
CACHE_DIR = config.CACHE / "records"
RANGES_PATH = config.DATA / "reference" / "ranges.json"

NTSB_URL = "https://data.ntsb.gov/avdata/FileDirectory/DownloadFile?fileID=avall.zip"
NTSB_CSV = RECORDS_DIR / "ntsb_aviation.csv"
NTSB_META = RECORDS_DIR / "ntsb_aviation.meta.json"
NTSB_COLUMNS = ("event_id", "ntsb_no", "date", "latitude", "longitude", "aircraft", "damage",
                "injury_severity", "fatalities", "location", "country")
METEORITE_URL = ("https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/"
                 "data/2019/2019-06-11/meteorites.csv")
METEORITE_CSV = RECORDS_DIR / "meteorite_landings.csv"

#: An accident closer than this (plus the capped footprint radius) can explain.
AVIATION_RADIUS_KM = 2.0
#: Days added on both sides of the onset window before comparing dates.
AVIATION_PAD_DAYS = 30
#: Records out to this distance are reported as context in evidence.
CONTEXT_RADIUS_KM = 50.0
#: Catalogue coordinates are often rounded to an arc-minute or coarser.
METEORITE_RADIUS_KM = 3.0
#: Recovered mass (g) from which a locality is worth a human look for an undated feature.
METEORITE_LARGE_MASS_G = 1.0e5
FOOTPRINT_CAP_KM = 1.0
#: Just outside an approximate circle the answer is uncertain: min(20 %, 10 km).
RANGE_MARGIN_FRACTION = 0.2
RANGE_MARGIN_MAX_KM = 10.0
RANGE_KINDS = ("launch_site", "drop_zone", "test_range", "bombing_range")
#: Signatures a falling rocket stage can produce (impact scar, burn scar, fire).
DROP_ZONE_SIGNATURES = ("crash", "landing_trace", "thermal", "unknown")
WIKIDATA_RADIUS_KM = 10.0

NTSB_COVERAGE = (
    "NTSB aviation database (avall, 2008 to the download date): civil aviation accidents and selected incidents in the "
    "United States, its territories and international waters, plus foreign events involving US-registered, US-operated "
    "or US-manufactured aircraft in which the NTSB took part. It holds no military losses and almost no other foreign "
    "accidents, and records without coordinates cannot be matched.")
WIKIDATA_COVERAGE = (
    "Wikidata: only accidents notable enough to have an item with coordinates within "
    f"{WIKIDATA_RADIUS_KM:.0f} km; far from complete anywhere.")
AVIATION_CAVEAT = ("Outside the United States the absence of a record is weak evidence: most general-aviation and all "
                   "military crashes abroad are in neither catalogue.")
METEORITE_COVERAGE = (
    "Meteorite Landings table (Meteoritical Society / NASA open data, as mirrored for TidyTuesday 2019-06-11): about "
    "38,000 located meteorites, mostly finds; the year is the fall or find year, coordinates are often rounded to an "
    "arc-minute or worse, masses are recovered masses, and the table stops in the early 2010s. Later falls are only "
    "covered by Wikidata meteorite items, which the wikidata_nearby check evaluates.")
RANGES_COVERAGE = ("Curated list of approximate circles (data/reference/ranges.json); not exhaustive, so a point outside "
                   "every circle may still lie in an unlisted or mis-sized military or space area.")

_SESSION_HEADERS = {"User-Agent": config.USER_AGENT}
_DAMAGE_RANK = {"DEST": 3, "SUBS": 2, "MINR": 1, "NONE": 0}
_tables: dict[str, Any] = {}
_failures: dict[str, str] = {}


class RecordsUnavailable(RuntimeError):
    """A reference catalogue could not be downloaded, parsed or read."""


# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------

def clear_cache() -> None:
    """Forget in-memory tables and remembered failures (files on disk are kept)."""
    _tables.clear()
    _failures.clear()


def _download(url: str, dest: Path, timeout: tuple[float, float] = (15.0, 180.0), attempts: int = 3) -> Path:
    """Stream ``url`` to ``dest`` atomically, with retries; raise ``RecordsUnavailable`` on failure."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    error = "no attempt made"
    for attempt in range(attempts):
        try:
            with requests.get(url, headers=_SESSION_HEADERS, timeout=timeout, stream=True) as response:
                if response.status_code != 200:
                    raise requests.HTTPError(f"HTTP {response.status_code}")
                with tmp.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1 << 20):
                        handle.write(chunk)
            if tmp.stat().st_size == 0:
                raise requests.HTTPError("empty reply")
            tmp.replace(dest)
            return dest
        except (requests.RequestException, OSError) as exc:
            error = f"{type(exc).__name__}: {str(exc)[:200]}"
            tmp.unlink(missing_ok=True)
            if attempt + 1 < attempts:
                time.sleep(2.0 * (attempt + 1))
    raise RecordsUnavailable(f"download of {url} failed after {attempts} attempts: {error}")


def _distances_km(lat: float, lon: float, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    """Vectorised great-circle distance in km from one point to many."""
    p1 = math.radians(lat)
    p2 = np.radians(lats.astype(np.float64))
    dphi = p2 - p1
    dlmb = np.radians(lons.astype(np.float64) - lon)
    a = np.sin(dphi / 2) ** 2 + math.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.minimum(1.0, np.sqrt(a)))


def _clean(value: Any) -> Any:
    """Make a pandas/numpy scalar JSON-friendly (NaN -> None)."""
    if value is None:
        return None
    if isinstance(value, (np.floating, float)):
        return None if math.isnan(float(value)) else float(value)
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _not_run(check: str, category: Any, reason: str, source: str, **evidence: Any) -> list[CheckResult]:
    return [CheckResult(check, category, "not_run", reason, source, dict(evidence))]


def _window_evidence(candidate: Candidate, window: tuple[date, date] | None) -> dict[str, Any]:
    return {"onset_window": [candidate.absent_until, candidate.present_from],
            "padded_window": [window[0].isoformat(), window[1].isoformat()] if window else None}


# --------------------------------------------------------------------------
# NTSB aviation accident table
# --------------------------------------------------------------------------

def _dms_to_degrees(text: Any) -> float:
    """Convert legacy NTSB strings such as '332739N' or '1120457W' to signed degrees (NaN if unusable)."""
    if not isinstance(text, str):
        return math.nan
    raw = text.strip().upper()
    if len(raw) < 6 or raw[-1] not in "NSEW" or not raw[:-1].isdigit():
        return math.nan
    digits = raw[:-1]
    seconds, minutes, degrees = int(digits[-2:]), int(digits[-4:-2]), int(digits[:-4])
    if minutes >= 60 or seconds >= 60:
        return math.nan
    value = degrees + minutes / 60.0 + seconds / 3600.0
    return -value if raw[-1] in "SW" else value


def ntsb_frame(events: dict[str, Sequence[Any]], aircraft: dict[str, Sequence[Any]]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build the compact accident table from the parsed ``events`` and ``aircraft`` tables.

    Returns the table (``NTSB_COLUMNS``, one row per event with usable
    coordinates, sorted by date) and counts describing what was dropped.
    """
    ev = pd.DataFrame({key: list(events[key]) for key in (
        "ev_id", "ntsb_no", "ev_date", "dec_latitude", "dec_longitude", "latitude", "longitude",
        "ev_highest_injury", "inj_tot_f", "ev_city", "ev_state", "ev_country") if key in events})
    for key in ("ntsb_no", "dec_latitude", "dec_longitude", "latitude", "longitude", "ev_highest_injury",
                "inj_tot_f", "ev_city", "ev_state", "ev_country"):
        if key not in ev:
            ev[key] = None
    ev = ev.dropna(subset=["ev_id"]).drop_duplicates(subset=["ev_id"])
    lat = pd.to_numeric(ev["dec_latitude"], errors="coerce")
    lon = pd.to_numeric(ev["dec_longitude"], errors="coerce")
    lat = lat.where(lat.notna(), ev["latitude"].map(_dms_to_degrees))
    lon = lon.where(lon.notna(), ev["longitude"].map(_dms_to_degrees))
    ac = pd.DataFrame({key: list(aircraft[key]) for key in ("ev_id", "acft_make", "acft_model", "damage") if key in aircraft})
    for key in ("acft_make", "acft_model", "damage"):
        if key not in ac:
            ac[key] = None
    ac["name"] = (ac["acft_make"].fillna("").astype(str).str.strip() + " "
                  + ac["acft_model"].fillna("").astype(str).str.strip()).str.strip()
    ac["rank"] = ac["damage"].map(_DAMAGE_RANK)
    names = ac[ac["name"] != ""].groupby("ev_id")["name"].agg(lambda s: " / ".join(dict.fromkeys(s)))
    worst = ac.dropna(subset=["rank"]).sort_values("rank").groupby("ev_id")["damage"].last()
    place = (ev["ev_city"].fillna("").astype(str).str.strip() + ", " + ev["ev_state"].fillna("").astype(str).str.strip())
    table = pd.DataFrame({
        "event_id": ev["ev_id"].astype(str),
        "ntsb_no": ev["ntsb_no"],
        "date": ev["ev_date"].astype(str).str.slice(0, 10),
        "latitude": lat.round(5),
        "longitude": lon.round(5),
        "aircraft": ev["ev_id"].map(names),
        "damage": ev["ev_id"].map(worst),
        "injury_severity": ev["ev_highest_injury"],
        "fatalities": pd.to_numeric(ev["inj_tot_f"], errors="coerce"),
        "location": place.str.strip(", "),
        "country": ev["ev_country"],
    })
    dated = pd.to_datetime(table["date"], errors="coerce").notna()
    located = (table["latitude"].between(-90, 90) & table["longitude"].between(-180, 180)
               & ~((table["latitude"].abs() < 1e-6) & (table["longitude"].abs() < 1e-6)))
    stats = {"events": int(len(table)), "events_with_coordinates": int((located & dated).sum()),
             "dropped_no_coordinates": int((~located).sum()), "dropped_no_date": int((~dated).sum())}
    table = table[located & dated].sort_values(["date", "event_id"]).reset_index(drop=True)
    if len(table):
        stats["first_date"], stats["last_date"] = str(table["date"].iloc[0]), str(table["date"].iloc[-1])
    return table[list(NTSB_COLUMNS)], stats


def build_ntsb_table(force: bool = False) -> Path:
    """Download the NTSB ``avall`` Access database and write the compact CSV.

    Output: ``NTSB_CSV`` (columns ``NTSB_COLUMNS``) and ``NTSB_META``. Needs
    the pure-python ``access-parser`` package; takes about a minute and about
    2 GB of memory. Raises ``RecordsUnavailable`` if the download or the
    parsing fails; an existing CSV is kept unless ``force`` is set.
    """
    if NTSB_CSV.exists() and not force:
        return NTSB_CSV
    try:
        from access_parser import AccessParser  # optional dependency, only needed to (re)build the table
    except ImportError as exc:
        raise RecordsUnavailable("the 'access-parser' package is needed to read the NTSB Access database") from exc
    archive = CACHE_DIR / "avall.zip"
    if force or not archive.exists():
        _download(NTSB_URL, archive)
    workdir = CACHE_DIR / "ntsb_extract"
    try:
        shutil.rmtree(workdir, ignore_errors=True)
        workdir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as bundle:
            members = [m for m in bundle.infolist() if m.filename.lower().endswith(".mdb") and "/" not in m.filename
                       and "\\" not in m.filename]
            if not members:
                raise RecordsUnavailable("no .mdb file inside the NTSB archive")
            mdb = Path(bundle.extract(members[0], workdir))
        database = AccessParser(str(mdb))
        events = database.parse_table("events")
        aircraft = database.parse_table("aircraft")
        del database
        table, stats = ntsb_frame(events, aircraft)
    except RecordsUnavailable:
        raise
    except Exception as exc:  # the parser raises many library-specific errors
        raise RecordsUnavailable(f"could not parse the NTSB database: {type(exc).__name__}: {str(exc)[:200]}") from exc
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if table.empty:
        raise RecordsUnavailable("the NTSB database yielded no located events")
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    tmp = NTSB_CSV.with_suffix(".csv.part")
    table.to_csv(tmp, index=False)
    tmp.replace(NTSB_CSV)
    stats.update({"source": NTSB_URL, "built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "coverage": NTSB_COVERAGE})
    NTSB_META.write_text(json.dumps(stats, indent=1))
    _tables.pop("ntsb", None)
    _failures.pop("ntsb", None)
    return NTSB_CSV


def load_ntsb(build: bool = True) -> pd.DataFrame:
    """The compact NTSB table (``NTSB_COLUMNS``; ``date`` as ISO strings), built on first use.

    Raises ``RecordsUnavailable`` when the CSV is missing and cannot be built
    (the failure is remembered for the process so later calls fail fast).
    """
    if "ntsb" in _tables:
        return _tables["ntsb"]
    if "ntsb" in _failures:
        raise RecordsUnavailable(_failures["ntsb"])
    try:
        if not NTSB_CSV.exists():
            if not build:
                raise RecordsUnavailable(f"{NTSB_CSV} has not been built")
            build_ntsb_table()
        frame = pd.read_csv(NTSB_CSV, dtype={"event_id": str, "ntsb_no": str, "date": str})
        missing = [c for c in NTSB_COLUMNS if c not in frame.columns]
        if missing or frame.empty:
            raise RecordsUnavailable(f"{NTSB_CSV} is empty or lacks columns {missing}")
    except RecordsUnavailable as exc:
        _failures["ntsb"] = str(exc)
        raise
    except (OSError, ValueError) as exc:
        _failures["ntsb"] = f"cannot read {NTSB_CSV}: {exc}"
        raise RecordsUnavailable(_failures["ntsb"]) from exc
    frame["day"] = pd.to_datetime(frame["date"], errors="coerce").dt.date
    _tables["ntsb"] = frame
    return frame


def _severe(record: dict[str, Any]) -> bool | None:
    """True: destroyed or fatal; False: clearly minor; None: in between or unknown."""
    damage, injury = record.get("damage"), record.get("injury_severity")
    fatalities = record.get("fatalities") or 0
    if damage == "DEST" or injury == "FATL" or fatalities > 0:
        return True
    if damage in ("MINR", "NONE") and injury in ("MINR", "NONE", None):
        return False
    if damage is None and injury is None:
        return True  # nothing recorded (typical of foreign investigations): do not discount it
    return None


def _ntsb_records(frame: pd.DataFrame, lat: float, lon: float, limit_km: float) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """NTSB records within the context radius (nearest first) and the nearest record overall."""
    dist = _distances_km(lat, lon, frame["latitude"].to_numpy(), frame["longitude"].to_numpy())
    if not len(dist):
        return [], None
    order = np.argsort(dist)

    def record(index: int) -> dict[str, Any]:
        row = frame.iloc[int(index)]
        rec = {key: _clean(row[key]) for key in NTSB_COLUMNS}
        rec.update({"source": "ntsb", "id": rec["event_id"], "distance_km": round(float(dist[index]), 3), "day": row["day"],
                    "label": f"NTSB {rec.get('ntsb_no') or rec['event_id']}: {rec.get('aircraft') or 'aircraft'}, "
                             f"{rec.get('location') or '?'} ({rec.get('country') or '?'})"})
        return rec

    near = [record(i) for i in order[:200] if dist[i] <= max(limit_km, CONTEXT_RADIUS_KM)]
    return near, record(order[0])


def _wikidata_records(lat: float, lon: float) -> list[dict[str, Any]]:
    """Wikidata aviation-accident items around the point, as accident records."""
    out: list[dict[str, Any]] = []
    for item in wikidata.nearby_items(lat, lon, WIKIDATA_RADIUS_KM):
        if "aviation_accident" not in item.get("categories", ()):
            continue
        span = wikidata.date_interval(item.get("date"), item.get("date_precision"))
        out.append({"source": "wikidata", "id": item["qid"], "label": f"Wikidata {item['qid']}: {item['label']}",
                    "date": item.get("date"), "date_precision": item.get("date_precision"), "span": span,
                    "day": span[0] if span and span[0] == span[1] else None,
                    "latitude": item.get("lat"), "longitude": item.get("lon"), "distance_km": item["distance_km"],
                    "aircraft": None, "damage": None, "injury_severity": None, "fatalities": None})
    return out


def _public(record: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in record.items() if k not in ("day", "span", "event_id")}


def _in_window(record: dict[str, Any], window: tuple[date, date]) -> bool | None:
    """Whether the record date falls in the window; None when the record has no usable date."""
    span = record.get("span") or ((record["day"], record["day"]) if record.get("day") else None)
    if span is None:
        return None
    return wikidata.intervals_overlap(span, window)


def check_aviation_accident(candidate: Candidate) -> list[CheckResult]:
    """Check ``aviation_accident`` (category "event"): a recorded crash at this place and time.

    ``explains``: a record within ``AVIATION_RADIUS_KM`` (plus capped footprint)
    dated inside the onset window padded by ``AVIATION_PAD_DAYS``, and either
    severe (aircraft destroyed or fatal) or of unrecorded severity.
    ``inconclusive``: a matching record of lesser severity (substantial damage
    or serious injury only), a severe record in range when the candidate has
    no onset window, or an undated record in range. ``does_not_explain``
    otherwise, with the nearest records and the coverage limits in evidence.
    ``not_run`` when neither the NTSB table nor Wikidata is available.
    """
    name, category = "aviation_accident", "event"
    source = "NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items"
    if not valid_point(candidate.lat, candidate.lon):
        return _not_run(name, category, "candidate has invalid coordinates", source)
    limit = AVIATION_RADIUS_KM + min(footprint_radius_km(candidate), FOOTPRINT_CAP_KM)
    window = onset_window(candidate, pad_days=AVIATION_PAD_DAYS)
    used: list[str] = []
    failed: dict[str, str] = {}
    records: list[dict[str, Any]] = []
    nearest_ntsb: dict[str, Any] | None = None
    try:
        frame = load_ntsb()
        near, nearest_ntsb = _ntsb_records(frame, candidate.lat, candidate.lon, limit)
        records.extend(near)
        used.append("ntsb")
    except RecordsUnavailable as exc:
        failed["ntsb"] = str(exc)
    try:
        records.extend(_wikidata_records(candidate.lat, candidate.lon))
        used.append("wikidata")
    except (wikidata.WikidataError, ValueError) as exc:
        failed["wikidata"] = str(exc)
    if not used:
        return _not_run(name, category, "no accident catalogue available: " + "; ".join(f"{k}: {v}" for k, v in failed.items()),
                        source, sources_failed=failed)
    records.sort(key=lambda r: r["distance_km"])
    in_range = [r for r in records if r["distance_km"] <= limit]
    coverage = " ".join(([NTSB_COVERAGE] if "ntsb" in used else ["NTSB table unavailable: " + failed.get("ntsb", "")])
                        + ([WIKIDATA_COVERAGE] if "wikidata" in used else ["Wikidata unavailable: " + failed.get("wikidata", "")])
                        + [AVIATION_CAVEAT])
    evidence: dict[str, Any] = {
        "radius_km": round(limit, 3), "pad_days": AVIATION_PAD_DAYS, **_window_evidence(candidate, window),
        "sources_used": used, "sources_failed": failed, "coverage": coverage,
        "records_in_radius": [_public(r) for r in in_range[:10]],
        "nearest_record": _public(records[0]) if records else (_public(nearest_ntsb) if nearest_ntsb else None),
        "nearest_ntsb_record": _public(nearest_ntsb) if nearest_ntsb else None,
    }
    matches: list[dict[str, Any]] = []
    lesser: list[dict[str, Any]] = []
    undated: list[dict[str, Any]] = []
    if window is not None:
        timed = [r for r in records if _in_window(r, window)]
        evidence["nearest_in_window"] = _public(timed[0]) if timed else None
        for rec in in_range:
            hit = _in_window(rec, window)
            if hit is None:
                undated.append(rec)
            elif hit:
                severity = _severe(rec)
                if severity:
                    matches.append(rec)
                elif severity is None:
                    lesser.append(rec)
        evidence["matches"] = [_public(r) for r in matches]
        evidence["lesser_matches"] = [_public(r) for r in lesser]
        if matches:
            best = matches[0]
            detail = (f"{best['label']} on {best.get('date')} lies {best['distance_km']:.2f} km away, within {limit:.1f} km "
                      f"and inside the onset window padded by {AVIATION_PAD_DAYS} days")
            return [CheckResult(name, category, "explains", detail, source, evidence)]
        if lesser or undated:
            rec = (lesser or undated)[0]
            why = ("is in range and in the window, but the recorded severity (no destroyed aircraft, no fatality) makes a "
                   "satellite-visible scar doubtful" if lesser else "is in range but has no usable date")
            return [CheckResult(name, category, "inconclusive", f"{rec['label']} at {rec['distance_km']:.2f} km {why}",
                                source, evidence)]
        tail = (f"; nearest record in the window: {timed[0]['label']} at {timed[0]['distance_km']:.1f} km"
                if timed else "; no record in the window within the context radius")
        other = f"; {len(in_range)} record(s) in range are dated outside the window" if in_range else ""
        detail = (f"no recorded accident within {limit:.1f} km dated {window[0]} to {window[1]}{other}{tail}. "
                  f"Coverage is limited: {AVIATION_CAVEAT}")
        return [CheckResult(name, category, "does_not_explain", detail, source, evidence)]
    severe = [r for r in in_range if _severe(r)]
    if severe:
        rec = severe[0]
        detail = (f"{rec['label']} ({rec.get('date')}) lies {rec['distance_km']:.2f} km away, but the candidate has no dated "
                  "onset window to compare with")
        return [CheckResult(name, category, "inconclusive", detail, source, evidence)]
    nearest = evidence["nearest_record"]
    detail = (f"no severe recorded accident within {limit:.1f} km (candidate has no onset window; "
              + (f"nearest record: {nearest['label']} at {nearest['distance_km']:.1f} km" if nearest else "no record found")
              + f"). Coverage is limited: {AVIATION_CAVEAT}")
    return [CheckResult(name, category, "does_not_explain", detail, source, evidence)]


# --------------------------------------------------------------------------
# Meteorite landings
# --------------------------------------------------------------------------

def load_meteorites(download: bool = True) -> pd.DataFrame:
    """Located records of the Meteorite Landings table (downloaded once and kept on disk).

    Columns: ``name, id, name_type, class, mass`` (g), ``fall`` ("Fell" or
    "Found"), ``year`` (NaN if unknown or implausible), ``lat``, ``long``.
    Rows without coordinates or at (0, 0) are dropped. The catalogue end year
    is in ``frame.attrs["coverage_end_year"]``. Raises ``RecordsUnavailable``.
    """
    if "meteorites" in _tables:
        return _tables["meteorites"]
    if "meteorites" in _failures:
        raise RecordsUnavailable(_failures["meteorites"])
    try:
        if not METEORITE_CSV.exists():
            if not download:
                raise RecordsUnavailable(f"{METEORITE_CSV} has not been downloaded")
            _download(METEORITE_URL, METEORITE_CSV, timeout=(15.0, 90.0))
        frame = pd.read_csv(METEORITE_CSV)
        missing = [c for c in ("name", "mass", "fall", "year", "lat", "long") if c not in frame.columns]
        if missing:
            raise RecordsUnavailable(f"{METEORITE_CSV} lacks columns {missing}")
    except RecordsUnavailable as exc:
        _failures["meteorites"] = str(exc)
        raise
    except (OSError, ValueError) as exc:
        _failures["meteorites"] = f"cannot read {METEORITE_CSV}: {exc}"
        raise RecordsUnavailable(_failures["meteorites"]) from exc
    frame["lat"] = pd.to_numeric(frame["lat"], errors="coerce")
    frame["long"] = pd.to_numeric(frame["long"], errors="coerce")
    frame["mass"] = pd.to_numeric(frame["mass"], errors="coerce")
    year = pd.to_numeric(frame["year"], errors="coerce")
    frame["year"] = year.where((year >= 1) & (year <= date.today().year))
    ok = (frame["lat"].between(-90, 90) & frame["long"].between(-180, 180)
          & ~((frame["lat"].abs() < 1e-9) & (frame["long"].abs() < 1e-9)))
    frame = frame[ok].reset_index(drop=True)
    if frame.empty:
        _failures["meteorites"] = f"{METEORITE_CSV} holds no located records"
        raise RecordsUnavailable(_failures["meteorites"])
    falls = frame.loc[frame["fall"] == "Fell", "year"].dropna()
    frame.attrs["coverage_end_year"] = int(falls.max()) if len(falls) else None
    _tables["meteorites"] = frame
    return frame


def check_meteorite(candidate: Candidate) -> list[CheckResult]:
    """Check ``meteorite_record`` (category "event") against the Meteorite Landings table.

    Dated candidate: ``explains`` when an observed fall ("Fell") within
    ``METEORITE_RADIUS_KM`` (plus capped footprint) has a year inside the onset
    window; ``not_run`` when the window extends beyond the last fall year of
    the table (the catalogue cannot speak for that period); otherwise
    ``does_not_explain``. Undated candidate: ``inconclusive`` when a meteorite
    of at least ``METEORITE_LARGE_MASS_G`` is recorded in range (a known large
    find or fall locality deserves a look), otherwise ``does_not_explain``.
    The nearest records are always in evidence.
    """
    name, category = "meteorite_record", "event"
    source = "Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com)"
    if not valid_point(candidate.lat, candidate.lon):
        return _not_run(name, category, "candidate has invalid coordinates", source)
    try:
        frame = load_meteorites()
    except RecordsUnavailable as exc:
        return _not_run(name, category, f"meteorite table unavailable: {exc}", source, error=str(exc))
    limit = METEORITE_RADIUS_KM + min(footprint_radius_km(candidate), FOOTPRINT_CAP_KM)
    dist = _distances_km(candidate.lat, candidate.lon, frame["lat"].to_numpy(), frame["long"].to_numpy())
    order = np.argsort(dist)[:200]
    records: list[dict[str, Any]] = []
    for index in order:
        if dist[index] > CONTEXT_RADIUS_KM and records:
            break
        row = frame.iloc[int(index)]
        year = _clean(row["year"])
        records.append({"name": str(row["name"]), "fall": _clean(row["fall"]), "year": int(year) if year is not None else None,
                        "mass_g": _clean(row["mass"]), "class": _clean(row.get("class")),
                        "lat": float(row["lat"]), "lon": float(row["long"]), "distance_km": round(float(dist[index]), 3)})
        if dist[index] > CONTEXT_RADIUS_KM:
            break
    in_range = [r for r in records if r["distance_km"] <= limit]
    end_year = frame.attrs.get("coverage_end_year")
    window = onset_window(candidate)
    evidence: dict[str, Any] = {
        "radius_km": round(limit, 3), **_window_evidence(candidate, window), "catalogue_last_fall_year": end_year,
        "coverage": METEORITE_COVERAGE, "records_in_radius": in_range[:10],
        "nearest_record": records[0] if records else None,
        "n_records_within_context_km": sum(r["distance_km"] <= CONTEXT_RADIUS_KM for r in records),
        "context_radius_km": CONTEXT_RADIUS_KM,
    }
    nearest = records[0] if records else None
    near_txt = (f"nearest record: {nearest['name']} ({nearest['fall']}, {nearest['year']}) at {nearest['distance_km']:.1f} km"
                if nearest else "no record found")
    if window is not None:
        matches = [r for r in in_range if r["fall"] == "Fell" and r["year"] is not None
                   and window[0].year <= r["year"] <= window[1].year]
        evidence["matches"] = matches
        if matches:
            best = matches[0]
            detail = (f"observed fall {best['name']} ({best['year']}, {best['mass_g']} g) is recorded {best['distance_km']:.2f} km away, "
                      f"within {limit:.1f} km and in the onset window years")
            return [CheckResult(name, category, "explains", detail, source, evidence)]
        if end_year is None or window[1].year > end_year:
            detail = (f"the table's last recorded fall year is {end_year}; it cannot speak for an onset window ending "
                      f"{window[1]} ({near_txt})")
            return [CheckResult(name, category, "not_run", detail, source, evidence)]
        detail = f"no observed fall within {limit:.1f} km in {window[0].year}-{window[1].year} ({near_txt})"
        return [CheckResult(name, category, "does_not_explain", detail, source, evidence)]
    large = [r for r in in_range if (r["mass_g"] or 0.0) >= METEORITE_LARGE_MASS_G]
    evidence["large_records_in_radius"] = large
    if large:
        best = large[0]
        detail = (f"{best['name']} ({best['fall']}, {best['year']}, {best['mass_g'] / 1000.0:.0f} kg recovered) is recorded "
                  f"{best['distance_km']:.2f} km away; a large meteorite locality may account for an undated feature here, "
                  "but the table cannot show that it does")
        return [CheckResult(name, category, "inconclusive", detail, source, evidence)]
    detail = f"no large recorded meteorite within {limit:.1f} km of this undated feature ({near_txt})"
    return [CheckResult(name, category, "does_not_explain", detail, source, evidence)]


# --------------------------------------------------------------------------
# Launch sites, drop zones and weapons ranges
# --------------------------------------------------------------------------

def load_ranges() -> list[dict[str, Any]]:
    """Validated entries of ``RANGES_PATH`` (name, country, kind, lat, lon, radius_km, confidence, diffuse, note).

    Raises ``RecordsUnavailable`` if the file is missing, unreadable or holds no valid entry.
    """
    if "ranges" in _tables:
        return _tables["ranges"]
    try:
        raw = json.loads(RANGES_PATH.read_text())
        entries = raw["entries"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise RecordsUnavailable(f"cannot read {RANGES_PATH}: {type(exc).__name__}: {exc}") from exc
    valid: list[dict[str, Any]] = []
    for entry in entries if isinstance(entries, list) else []:
        try:
            lat, lon, radius = float(entry["lat"]), float(entry["lon"]), float(entry["radius_km"])
            ok = (valid_point(lat, lon) and math.isfinite(radius) and radius > 0 and entry["kind"] in RANGE_KINDS
                  and bool(entry["name"]))
        except (KeyError, TypeError, ValueError):
            ok = False
        if ok:
            valid.append({**entry, "lat": lat, "lon": lon, "radius_km": radius,
                          "confidence": str(entry.get("confidence", "low")), "diffuse": bool(entry.get("diffuse", False))})
    if not valid:
        raise RecordsUnavailable(f"{RANGES_PATH} holds no valid entry")
    _tables["ranges"] = valid
    return valid


def _range_explains(entry: dict[str, Any], signature: str) -> tuple[bool, str]:
    """Whether being inside this entry is a sufficient explanation, with the reason when it is not."""
    if entry["diffuse"]:
        return False, "the area is shared with unrelated land use"
    if entry["confidence"] not in ("high", "medium"):
        return False, "the listed geometry has low confidence"
    if entry["kind"] == "drop_zone" and signature not in DROP_ZONE_SIGNATURES:
        return False, f"a rocket-stage drop zone does not account for a '{signature}' signature"
    return True, ""


def check_ranges(candidate: Candidate) -> list[CheckResult]:
    """Check ``military_or_rocket_range`` (category "infrastructure") against the curated list.

    ``explains``: the candidate centre is inside a listed circle of a closed
    launch site or range with medium or high geometry confidence (for a drop
    zone, only crash, landing-trace, thermal or unknown signatures).
    ``inconclusive``: inside a diffuse or low-confidence area, or within the
    uncertainty margin just outside a circle. ``does_not_explain`` otherwise,
    with the nearest entry in evidence. ``not_run`` if the list is unreadable.
    """
    name, category = "military_or_rocket_range", "infrastructure"
    source = "SKYWATCH curated list data/reference/ranges.json (approximate geometries)"
    if not valid_point(candidate.lat, candidate.lon):
        return _not_run(name, category, "candidate has invalid coordinates", source)
    try:
        entries = load_ranges()
    except RecordsUnavailable as exc:
        return _not_run(name, category, f"range list unavailable: {exc}", source, error=str(exc))
    scored: list[dict[str, Any]] = []
    for entry in entries:
        dist = haversine_km(candidate.lat, candidate.lon, entry["lat"], entry["lon"])
        margin = min(RANGE_MARGIN_FRACTION * entry["radius_km"], RANGE_MARGIN_MAX_KM)
        scored.append({**entry, "distance_km": round(dist, 2), "distance_to_edge_km": round(dist - entry["radius_km"], 2),
                       "margin_km": round(margin, 2)})
    scored.sort(key=lambda e: e["distance_to_edge_km"])
    inside = [e for e in scored if e["distance_to_edge_km"] <= 0]
    margin_hits = [e for e in scored if 0 < e["distance_to_edge_km"] <= e["margin_km"]]
    evidence: dict[str, Any] = {"inside": inside, "within_margin": margin_hits, "nearest_entry": scored[0],
                                "signature": candidate.signature, "n_entries": len(entries), "coverage": RANGES_COVERAGE}
    sufficient = [e for e in inside if _range_explains(e, candidate.signature)[0]]
    if sufficient:
        best = sufficient[0]
        detail = (f"inside {best['name']} ({best['kind']}, {best['country']}): {best['distance_km']:.1f} km from the centre of an "
                  f"approximate {best['radius_km']:.0f} km circle (geometry confidence {best['confidence']}); conventional military "
                  "or space activity is the overwhelmingly likely cause")
        evidence["entry"] = best
        return [CheckResult(name, category, "explains", detail, source, evidence)]
    if inside:
        best = inside[0]
        detail = (f"inside the approximate circle of {best['name']} ({best['kind']}), but {_range_explains(best, candidate.signature)[1]}, "
                  "so this is a caution rather than an explanation")
        evidence["entry"] = best
        return [CheckResult(name, category, "inconclusive", detail, source, evidence)]
    if margin_hits:
        best = margin_hits[0]
        detail = (f"{best['distance_to_edge_km']:.1f} km outside the approximate circle of {best['name']} ({best['kind']}), within its "
                  f"{best['margin_km']:.1f} km uncertainty margin; the real boundary may include this point")
        evidence["entry"] = best
        return [CheckResult(name, category, "inconclusive", detail, source, evidence)]
    best = scored[0]
    detail = (f"outside every listed launch site, drop zone and range; nearest is {best['name']} ({best['kind']}), "
              f"{best['distance_to_edge_km']:.0f} km beyond its approximate edge. The list is not exhaustive")
    return [CheckResult(name, category, "does_not_explain", detail, source, evidence)]


def check_records(candidate: Candidate) -> list[CheckResult]:
    """Run the three record checks: aviation accident, meteorite record, military or rocket range."""
    return check_aviation_accident(candidate) + check_meteorite(candidate) + check_ranges(candidate)
