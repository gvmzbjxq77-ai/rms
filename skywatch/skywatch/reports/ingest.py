"""Witness-report ingestion: public NUFORC copies and the GEIPAN case catalogue.

Everything here is an UNVERIFIED CLAIM made by a witness (NUFORC) or a case
summary written by an investigating agency about such a claim (GEIPAN). The
module never treats a report as a fact: tags label what a report CLAIMS, and
a matched report only says "somebody reported something near this place and
time", never that the report and a surface feature share a cause.

Sources ingested (see ``SOURCE_FILES``) and sources that could not be
(``SOURCES_NOT_INGESTED``). nuforc.org itself is never contacted.

Normalised record (one JSON object per line in ``REPORTS_PATH``):

``id``                      stable identifier (``nuforc-<hash>`` / ``geipan-<case id>``)
``source``                  ``"nuforc"`` or ``"geipan"``
``source_file``             which public copy the record came from
``datetime``                ISO 8601; date only when the time is unknown
``date_precision``          ``minute`` | ``day`` | ``month`` | ``year``
``time_basis``              ``utc`` | ``local`` (witness clock, zone unknown)
``lat``, ``lon``            geocode of the named place, NOT of the event site
``location_precision_km``   honest radius within which the true site may lie
``country``                 ISO 3166 alpha-2 when known, else ``""``
``place``                   city / commune as given by the source
``shape``, ``duration_s``   as claimed by the witness (may be null)
``text``                    the source's summary text
``official_class``          GEIPAN class A-D, else null
``official_identification`` GEIPAN's own conclusion, else null
``tags``                    subset of ``TAGS`` from the keyword rules below

Tag rules (``TAG_RULES``): the text is lower-cased, accents are removed and
apostrophes normalised; every ``NEGATION_RULES`` phrase ("no trace", "aucune
trace") and every per-tag ``exclude`` phrase ("landing lights", "traces de
condensation") is deleted; the tag is set when any ``include`` pattern still
matches. The rules are deliberately simple and readable, so they both miss
claims and mislabel some texts; they are a filter for human reading, not a
classifier.
"""
from __future__ import annotations

import hashlib
import html
import io as stdio
import json
import logging
import re
import time
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from http import HTTPStatus
from pathlib import Path
from typing import Any, Sequence
from urllib.parse import urlparse

import numpy as np
import pandas as pd
import requests

from ..core import config, io
from ..core.models import Candidate, CheckResult, Region

logger = logging.getLogger(__name__)

REPORTS_DIR: Path = config.DATA / "reports"
REPORTS_PATH: Path = REPORTS_DIR / "reports.jsonl"
SUMMARY_PATH: Path = REPORTS_DIR / "summary.json"
RAW_DIR: Path = config.CACHE / "reports"

TAGS: tuple[str, ...] = ("landing", "physical_trace", "crash_retrieval", "close_encounter")

#: Public copies that are downloaded. ``parts`` maps a cache file name to a URL.
SOURCE_FILES: dict[str, dict[str, Any]] = {
    "nuforc_planetsig_2014": {
        "source": "nuforc",
        "about": "NUFORC reports to 2014, geocoded to the named city (planetsig/ufo-reports).",
        "parts": {
            "planetsig_scrubbed.csv": "https://raw.githubusercontent.com/planetsig/ufo-reports/"
                                      "master/csv-data/ufo-scrubbed-geocoded-time-standardized.csv",
        },
    },
    "nuforc_tidytuesday_2023": {
        "source": "nuforc",
        "about": "NUFORC reports to mid-2023 with a city gazetteer (rfordatascience/tidytuesday "
                 "2023-06-20).",
        "parts": {
            "tidytuesday_ufo_sightings.csv": "https://raw.githubusercontent.com/rfordatascience/"
                                             "tidytuesday/master/data/2023/2023-06-20/"
                                             "ufo_sightings.csv",
            "tidytuesday_places.csv": "https://raw.githubusercontent.com/rfordatascience/"
                                      "tidytuesday/master/data/2023/2023-06-20/places.csv",
        },
    },
    "geipan": {
        "source": "geipan",
        "about": "GEIPAN (CNES) case catalogue export, classes A-D, commune-level coordinates.",
        "parts": {"geipan_export_cas.xlsx": "https://www.geipan.fr/fr/cnes/export/cas"},
    },
}

#: Sources named in the project plan that this environment cannot reach.
SOURCES_NOT_INGESTED: dict[str, str] = {
    "nuforc.org (live database, reports after mid-2023)":
        "The site blocks automated access and must not be contacted; no newer public copy "
        "fetchable from raw.githubusercontent.com was found, so NUFORC coverage ends where "
        "the newest ingested copy ends.",
    "US National Archives UAP records (NARA record group 615)":
        "Host is not on the network allowlist of this environment; not attempted.",
    "Published physical-trace catalogues (e.g. Phillips trace-case catalogue, CUFOS)":
        "Not available from any allowlisted host; not attempted.",
    "GEIPAN witness-statement export (/fr/cnes/export/temoignages)":
        "Reachable but not ingested: the case export already carries one summary, class and "
        "coordinate per case, and per-witness rows would double count the same events.",
}

#: Radius (km) within which the true site may lie, by kind of geocode.
PRECISION_CITY_KM = 10.0        # a named town: the witness was somewhere in or near it
PRECISION_BIG_CITY_KM = 20.0    # a city above BIG_CITY_POPULATION inhabitants
PRECISION_COMMUNE_KM = 5.0      # GEIPAN commune coordinate, rounded to 0.01 degree
PRECISION_VEHICLE_KM = 50.0     # GEIPAN aeronautical / maritime observations
BIG_CITY_POPULATION = 250_000

#: GEIPAN classes the agency itself identified (A) or probably identified (B)
#: as conventional. They are kept in the data but never matched or seeded.
MATCH_EXCLUDED_CLASSES: tuple[str, ...] = ("A", "B")

#: First year with a usable Sentinel-2 "before" image for a seeded search.
S2_ERA_START_YEAR = 2016
SEED_WINDOW_DAYS = 61
COVERAGE_RADIUS_KM = 100.0
COVERAGE_MIN_REPORTS = 5
_EARTH_RADIUS_KM = 6371.0088
_KM_PER_DEG = 111.195

NEGATION_RULES: tuple[str, ...] = (
    r"\b(?:no|not|never|without|nothing|didn't|did not|doesn't|does not|don't|couldn't|"
    r"could not|wasn't|was not) (?:\w+ ){0,3}?(?:land\w*|traces?|marks?|markings?|crash\w*|"
    r"debris|burn\w*|imprints?|wreckage|residue|crater|evidence)\b",
    r"\b(?:aucune?|pas de|pas d'|sans|ni|absence de|absence d') ?(?:\w+ ){0,2}?(?:traces?|"
    r"atterri\w*|empreintes?|debris|marques?|brulures?|cratere|indices?)\b",
    r"\bn'(?:a|ont|est|ait|avait) (?:pas|jamais|rien) (?:\w+ ){0,2}?(?:atterri\w*|laisse\w*|"
    r"pose\w*|ecrase\w*)\b",
)

TAG_RULES: dict[str, dict[str, tuple[str, ...]]] = {
    "landing": {
        "include": (
            r"\bland(?:ed|ing|s)\b",
            r"\b(?:to|it|did|would|could|might|may|will|and|then) land\b",
            r"\btouch(?:ed|es|ing)? down\b",
            r"\b(?:sitting|resting|parked|sat|settled|set down|came down|descended|lowered) "
            r"(?:\w+ ){0,3}?(?:on|to|onto|in) (?:the |a |my |our )?(?:ground|field|road|pasture|"
            r"yard|lawn|meadow)\b",
            r"\b(?:objets?|engins?|pan|phenomenes?|boules?|soucoupes?|disques?|spheres?|formes?|"
            r"masses?|ovnis?|lumieres?|appareils? inconnus?)\b(?: \w+){0,6}? (?:atterri\w*|"
            r"se pos(?:e|er|a|ait|ant|ent)\b|s'(?:est|etait|etre) posee?\b)",
            r"\batterrissage (?:d'un|de l'|du|d'une|de la) (?:objet|engin|ovni|pan|phenomene|"
            r"soucoupe|boule)\b",
            r"\bposee?s? (?:au|sur le|a meme le) sol\b",
            r"\bposee?s? (?:dans|sur) (?:un|le|une|la) (?:champ|pre|prairie|clairiere|jardin|"
            r"route|chemin)\b",
        ),
        "exclude": (
            r"\blanding (?:lights?|gear|strip|pattern|approach)\b",
            r"\b(?:air)?(?:planes?|liners?)\b(?: \w+){0,3}? land(?:ed|ing|s)?\b",
            r"\b(?:jets?|helicopters?|airport|runway)\b(?: \w+){0,3}? land(?:ed|ing|s)?\b",
            r"\bland(?:ing|ed)? (?:at|on) (?:the )?(?:\w+ ){0,3}?(?:airport|runway|airfield|"
            r"air force base|afb)\b",
            r"\b(?:phares?|feux|phase|piste|train|procedure|approche|zone|trajectoire|couloir|"
            r"axe|tour) d'atterrissage\b",
            r"\b(?:avions?|helicopteres?|aeronefs?|vols?|ballons?|lanternes?)\b(?: \w+){0,6}? "
            r"(?:d')?(?:atterri\w*|se pos\w+)",
            r"\bse pos\w+ (?:des|la|une|cette|les|plusieurs) questions?\b",
            r"\batterri\w* (?:a|sur|de) (?:l'|la |le )?(?:aeroport|aerodrome|piste|base)\w*",
        ),
    },
    "physical_trace": {
        "include": (
            r"\b(?:burn(?:ed|t)?|scorch(?:ed)?|singed|charred|flattened|swirled|depressed|dead) "
            r"(?:\w+ ){0,2}?(?:marks?|circles?|rings?|patch(?:es)?|spots?|grass|ground|soil|area|"
            r"crops?|vegetation|earth)\b",
            r"\b(?:ground|grass|soil|crops?|vegetation|earth|field) (?:was |were |is |had been )?"
            r"(?:burn(?:ed|t)|scorched|flattened|charred|swirled|depressed|singed)\b",
            r"\b(?:ground|landing|physical) (?:traces?|evidence|marks?|markings?)\b",
            r"\btrace evidence\b",
            r"\bimprints?\b",
            r"\bindentations?\b",
            r"\bdepressions? in the (?:ground|field|grass|soil|snow)\b",
            r"\bcrop circles?\b",
            r"\b(?:marks?|markings?|rings?|circles?|holes?|impressions?) (?:\w+ ){0,2}?"
            r"(?:on|in) the (?:ground|field|grass|snow|lawn|soil|dirt|pasture|crops?)\b",
            r"\bleft (?:behind )?(?:a |an |some |strange |three |four |several |burn )*"
            r"(?:marks?|rings?|circles?|residue|traces?|burns?|imprints?|impressions?)\b",
            r"\bresidue\b",
            r"\btraces? (?:au|sur le|dans le|sur la|dans la|sur l'|dans l'|sur du|sur un|"
            r"dans un|sur une) ?(?:sol|terrain|champ|pre|prairie|herbe|neige|terre|vegetation|"
            r"pelouse|goudron|bitume)\b",
            r"\btraces? (?:de brulures?|circulaires?|physiques?|d'atterrissage|d'ecrasement|"
            r"rectangulaires?|ovales?|rondes?|suspectes?|materielles?|d'impact|de pas)\b",
            r"\b(?:laiss\w+|relev\w+|constat\w+|decouv\w+|retrouv\w+) (?:des |de |d'une |"
            r"une |les |plusieurs |d'|deux |trois |quatre )?traces? (?:\w+ ){0,4}?(?:sol|terrain|"
            r"champ|pre|prairie|herbes?|neige|terre|vegetation|pelouse|jardin)\b",
            r"\bsol (?:brule|calcine|tasse|ecrase|noirci)\b",
            r"\b(?:herbes?|vegetation|terre|cultures?|luzerne|ble|mais|pelouse) (?:\w+ ){0,2}?"
            r"(?:brulee?s?|couchee?s?|ecrasee?s?|aplatie?s?|calcinee?s?|roussie?s?|"
            r"dessechee?s?|noircie?s?)\b",
            r"\bempreintes?\b",
            r"\bbrulures? (?:au|sur le|du) sol\b",
            r"\bprelevements? (?:de |d')(?:sol|terre|vegetaux|vegetation|echantillons)\b",
        ),
        "exclude": (
            r"\btraces? (?:de condensation|lumineuses?|blanches?|dans le ciel|de fumee|"
            r"nuageuses?|d'avions?|persistantes?|de lumiere|rouges?|oranges?|vertes?|"
            r"sur (?:la|les|une|des) photos?)\b",
            r"\bfinger ?prints?\b",
            r"\btraces? (?:radars?|gps|ads-?b)\b",
            r"\b(?:vols?|avions?|satellites?|trajectoires?|iss|station)\b(?: \w+){0,6}? "
            r"traces? au sol\b",
        ),
    },
    "crash_retrieval": {
        "include": (
            r"\bcrash(?:ed|es|ing)?\b",
            r"\b(?:impact(?:ed)?|slammed|plunged|plummeted|smashed) (?:\w+ ){0,3}?(?:the |into "
            r"the |into a )?(?:ground|earth|field|woods|forest|hill|mountain|desert|lake|ocean|"
            r"sea|water)\b",
            r"\b(?:fell|fall|fallen|falling|dropped) (?:\w+ ){0,2}?(?:to|into|onto) "
            r"(?:the )?(?:earth|ground|woods|field|forest|lake|ocean|sea)\b",
            r"\b(?:found|recovered|collected|scattered|field of|pieces of|burning|flaming|"
            r"falling|metal|metallic|strange|unknown) debris\b",
            r"\bdebris (?:field|fell|falling|found|recovered|scattered|on the ground|"
            r"in (?:the|a|my|our) (?:field|yard|woods|road))\b",
            r"\b(?:retrouv\w+|recuper\w+|ramass\w+|decouv\w+) (?:des |de |les |un |plusieurs )?"
            r"debris\b",
            r"\bdebris (?:retrouves?|recuperes?|ramasses?|au sol|tombes?|dans (?:le|un) champ)\b",
            r"\bwreckage\b",
            r"\bcrater\b",
            r"\bimpact (?:site|crater|point)\b",
            r"\bhit the (?:ground|earth|water)\b",
            r"\b(?:came|went|gone|going|coming) down (?:in|into|on) ",
            r"\bretriev(?:al|ed|e|ing)\b",
            r"\brecover(?:ed|y|ing) (?:\w+ ){0,3}?(?:craft|object|debris|wreckage|saucer|disc|"
            r"disk|ufo|material|pieces?)\b",
            r"\bs'ecras\w+",
            r"\bs'(?:est|etait|etre) ecrasee?\b",
            r"\becrasement\b",
            r"\bcratere\b",
            r"\bchute (?:au sol|d'un objet|d'un engin|d'une boule|d'un debris|de debris|"
            r"de l'objet|d'un corps)\b",
            r"\bimpact (?:au|sur le) sol\b",
            r"\b(?:tombe\w*|chute\w*|retombe\w*) (?:\w+ ){0,3}?(?:au|sur le|dans le|dans un|"
            r"dans la|dans une) (?:sol|champ|pre|foret|bois|jardin|mer|lac|riviere|etang)\b",
            r"\brecuper\w+ (?:\w+ ){0,3}?(?:objet|debris|engin|fragments?|morceaux?)\b",
        ),
        "exclude": (
            r"\bcrash course\b",
            r"\brisques? (?:\w+ ){0,2}?de crash\b",
            r"\brisk of (?:a )?crash\w*",
            r"\bdebris (?:spatial|spatiaux|de satellites?|satellitaires?|portes? par le vent|"
            r"legers?|de fusees?|orbital|orbitaux|d'un etage|l'etage)\b",
            r"\b(?:space|orbital|rocket|satellite) debris\b",
            r"\b(?:rentrees?|retombees?) (?:atmospheriques? |dans l'atmosphere )?(?:de |d'un |"
            r"d'une |du |des )?(?:gros |petits? )?debris\b",
            r"\bobjet spatial \(debris\)",
            r"\b(?:\"|')debris(?:\"|')",
            r"\btraces? d'ecrasement\b",
        ),
    },
    "close_encounter": {
        "include": (
            r"\b(?:aliens|beings|humanoids?|occupants?|creatures?|extraterrestrials?)\b",
            r"\b(?:an|the|small|tall|grey|gray|little) aliens?\b",
            r"\b(?:a|the|small|tall|grey|gray|strange|one|two|three|little) beings?\b",
            r"\babduct(?:ed|ion|ions|ing)?\b",
            r"\bclose encounter\b",
            r"\bmissing time\b",
            r"\bparaly[sz]ed\b",
            r"\b(?:within|less than|only|about|approximately|around) \d+ ?(?:feet|foot|ft|yards|"
            r"yds|meters|metres) (?:away|from (?:me|us|my|our|the (?:car|house|ground|witness)))",
            r"\bhover(?:ed|ing|s)? (?:\w+ ){0,3}?(?:above|over) (?:the |my |our |a )?(?:ground|"
            r"car|house|field|road|truck|yard|trees?|treetops?|tree line|roof|barn|pasture|"
            r"backyard|lawn)\b",
            r"\brencontres? rapprochees?\b",
            r"\brr ?[1-4]\b",
            r"\b(?:etres|humanoides?|entites?|creatures?|occupants?|extraterrestres?)\b",
            r"\bpetits? etres?\b",
            r"\betres? (?:vivants?|humanoides?|etranges?)\b",
            r"\ba (?:quelques|une dizaine de|\d+) metres (?:du temoin|des temoins|de lui|"
            r"d'elle|d'eux|de moi|de nous|du sol|de la voiture|du vehicule)\b",
        ),
        "exclude": (
            r"\bhuman beings?\b",
            r"\betres? humains?\b",
        ),
    },
}

#: Weight of each claim when ranking reports for a ground search.
TAG_WEIGHTS: dict[str, float] = {"physical_trace": 3.0, "landing": 2.0, "crash_retrieval": 2.0,
                                 "close_encounter": 0.5}
HOAX_PATTERN = r"hoax|canular|prank|not a serious report"

#: NUFORC staff remarks in double parentheses are not witness claims.
EDITOR_NOTE_PATTERN = r"\(\(.*?(?:\)\)|$)"
#: A staff remark that itself proposes a conventional cause or a hoax.
EDITOR_EXPLAINED_PATTERN = (r"\(\([^)]*(?:hoax|debris|meteor|rocket|launch|starlink|satellite|"
                            r"venus|jupiter|sirius|mars\b|star\b|planet|balloon|lantern|"
                            r"aircraft|contrail|iss\b|missile|flare|drone)")
_NEGATION_RE = re.compile("|".join(NEGATION_RULES))
_EDITOR_NOTE_RE = re.compile(EDITOR_NOTE_PATTERN)
_EXCLUDE_RE = {tag: re.compile("|".join(rule["exclude"])) for tag, rule in TAG_RULES.items()}
_INCLUDE_RE = {tag: re.compile("|".join(rule["include"])) for tag, rule in TAG_RULES.items()}

#: Changes whenever a rule changes; ``build`` re-normalises when it differs.
RULES_VERSION = hashlib.sha1(json.dumps(
    [TAG_RULES, NEGATION_RULES, EDITOR_NOTE_PATTERN], sort_keys=True).encode()).hexdigest()[:12]

_COLUMNS: tuple[str, ...] = (
    "id", "source", "source_file", "datetime", "date_precision", "time_basis", "lat", "lon",
    "location_precision_km", "country", "place", "shape", "duration_s", "text",
    "official_class", "official_identification", "tags")


class ReportsUnavailable(RuntimeError):
    """No normalised report file exists and none could be built."""


# --------------------------------------------------------------------------
# Text rules
# --------------------------------------------------------------------------

def _fold(text: str) -> str:
    """Lower-case, strip accents and normalise apostrophes for rule matching."""
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text.lower())


def tag_text(text: str | None) -> list[str]:
    """Tags a report text CLAIMS, by the documented keyword rules (see module docstring)."""
    if not text or not isinstance(text, str):
        return []
    folded = _NEGATION_RE.sub(" ", _EDITOR_NOTE_RE.sub(" ", _fold(text)))
    return [tag for tag in TAGS
            if _INCLUDE_RE[tag].search(_EXCLUDE_RE[tag].sub(" ", folded))]


def _tag_series(text: pd.Series) -> list[list[str]]:
    """Vectorised ``tag_text`` for a whole column."""
    folded = (text.fillna("").astype(str)
              .str.replace("[’‘`]", "'", regex=True)
              .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
              .str.lower().str.replace(r"\s+", " ", regex=True)
              .str.replace(_EDITOR_NOTE_RE, " ", regex=True)
              .str.replace(_NEGATION_RE, " ", regex=True))
    hits = np.zeros((len(folded), len(TAGS)), dtype=bool)
    for k, tag in enumerate(TAGS):
        cleaned = folded.str.replace(_EXCLUDE_RE[tag], " ", regex=True)
        hits[:, k] = cleaned.str.contains(_INCLUDE_RE[tag], regex=True).to_numpy(dtype=bool)
    return [[TAGS[k] for k in np.flatnonzero(row)] for row in hits]


def _clean_text(series: pd.Series) -> pd.Series:
    """Unescape HTML entities and collapse whitespace; missing becomes ''."""
    out = series.fillna("").astype(str).map(html.unescape)
    return out.str.replace(r"\s+", " ", regex=True).str.strip()


def _slug(place: str, limit: int = 24) -> str:
    """Uppercase ASCII letters, digits and hyphens only."""
    folded = unicodedata.normalize("NFKD", place or "")
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch)).upper()
    slug = re.sub(r"[^A-Z0-9]+", "-", folded).strip("-")[:limit].strip("-")
    return slug or "SITE"


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------

def _fetch(url: str, dest: Path, force: bool) -> Path:
    """Download ``url`` to ``dest`` (cached); raise ``RuntimeError`` with the reason on failure."""
    host = urlparse(url).hostname or ""
    if host not in config.ALLOWED_HOSTS or host.endswith("nuforc.org"):
        raise RuntimeError(f"host {host!r} is not allowed")
    if dest.exists() and dest.stat().st_size > 0 and not force:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    reason = "no attempt made"
    for attempt in range(4):
        try:
            response = requests.get(url, headers={"User-Agent": config.USER_AGENT},
                                    timeout=(15, 240))
            if response.status_code == HTTPStatus.OK and response.content:
                tmp = dest.with_suffix(dest.suffix + ".part")
                tmp.write_bytes(response.content)
                tmp.replace(dest)
                return dest
            reason = f"HTTP {response.status_code}"
            if (HTTPStatus.BAD_REQUEST <= response.status_code < HTTPStatus.INTERNAL_SERVER_ERROR
                    and response.status_code != HTTPStatus.TOO_MANY_REQUESTS):
                break
        except requests.RequestException as exc:
            reason = type(exc).__name__ + ": " + str(exc)[:200]
        time.sleep(2.0 * (attempt + 1))
    if dest.exists() and dest.stat().st_size > 0:
        logger.warning("refresh of %s failed (%s); using the cached copy", url, reason)
        return dest
    raise RuntimeError(f"download failed for {url}: {reason}")


# --------------------------------------------------------------------------
# Normalisers (pure functions: raw table in, normalised frame out)
# --------------------------------------------------------------------------

def _hash_ids(prefix: str, *columns: pd.Series) -> list[str]:
    joined = columns[0].astype(str)
    for column in columns[1:]:
        joined = joined + "|" + column.astype(str)
    return [prefix + hashlib.sha1(value.encode("utf-8")).hexdigest()[:12] for value in joined]


def _finalise(frame: pd.DataFrame) -> pd.DataFrame:
    """Order columns, null out impossible coordinates, add tags."""
    frame = frame.copy()
    for column in ("lat", "lon", "duration_s", "location_precision_km"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    bad = (~frame["lat"].between(-90, 90) | ~frame["lon"].between(-180, 180)
           | ((frame["lat"] == 0) & (frame["lon"] == 0)))
    frame.loc[bad, ["lat", "lon", "location_precision_km"]] = np.nan
    frame.loc[frame["duration_s"] < 0, "duration_s"] = np.nan
    frame["tags"] = _tag_series(frame["text"]) if len(frame) else []
    return frame.loc[:, list(_COLUMNS)].reset_index(drop=True)


def normalise_planetsig(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalise the header-less 11-column planetsig NUFORC table (local witness time)."""
    names = ["datetime", "city", "state", "country", "shape", "duration_s", "duration_text",
             "comments", "date_posted", "latitude", "longitude"]
    raw = raw.iloc[:, :11].copy()
    raw.columns = names[:raw.shape[1]]
    stamp = raw["datetime"].fillna("").astype(str).str.strip()
    midnight = stamp.str.contains(r" 24:\d\d$", regex=True)
    stamp = stamp.str.replace(r" 24:(\d\d)$", r" 00:\1", regex=True)
    when = pd.to_datetime(stamp, format="%m/%d/%Y %H:%M", errors="coerce")
    when = when + pd.to_timedelta(midnight.astype(int), unit="D")
    city = raw["city"].fillna("").astype(str)
    place = city.str.replace(r"\s*\(.*?\)", "", regex=True).str.strip().str.title()
    text = _clean_text(raw["comments"])
    out = pd.DataFrame({
        "id": _hash_ids("nuforc-", stamp, city, raw["state"].fillna(""), text),
        "source": "nuforc",
        "source_file": "nuforc_planetsig_2014",
        "datetime": when.dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "date_precision": "minute",
        "time_basis": "local",
        "lat": pd.to_numeric(raw["latitude"], errors="coerce"),
        "lon": pd.to_numeric(raw["longitude"], errors="coerce"),
        "location_precision_km": PRECISION_CITY_KM,
        "country": raw["country"].fillna("").astype(str).str.strip().str.upper(),
        "place": place,
        "shape": raw["shape"].fillna("").astype(str).str.strip().str.lower(),
        "duration_s": pd.to_numeric(raw["duration_s"], errors="coerce"),
        "text": text,
        "official_class": None,
        "official_identification": None,
    })
    out["_state"] = raw["state"].fillna("").astype(str).str.strip().str.lower().to_numpy()
    out = out[when.notna().to_numpy()]
    state = out.pop("_state")
    final = _finalise(out)
    final["_state"] = state.to_numpy()
    return final


def normalise_tidytuesday(sightings: pd.DataFrame, places: pd.DataFrame) -> pd.DataFrame:
    """Normalise the TidyTuesday 2023 NUFORC table; coordinates come from its city gazetteer."""
    key = ["city", "state", "country_code"]
    gazetteer = places.drop_duplicates(subset=key)[key + ["latitude", "longitude", "population"]]
    merged = sightings.merge(gazetteer, on=key, how="left", validate="many_to_one")
    when = pd.to_datetime(merged["reported_date_time_utc"], errors="coerce", utc=True)
    population = pd.to_numeric(merged["population"], errors="coerce")
    precision = np.where(population.to_numpy() >= BIG_CITY_POPULATION, PRECISION_BIG_CITY_KM,
                         PRECISION_CITY_KM)
    text = _clean_text(merged["summary"].replace("NA", ""))
    stamp = when.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out = pd.DataFrame({
        "id": _hash_ids("nuforc-", stamp, merged["city"], merged["state"], text),
        "source": "nuforc",
        "source_file": "nuforc_tidytuesday_2023",
        "datetime": stamp,
        "date_precision": "minute",
        "time_basis": "utc",
        "lat": pd.to_numeric(merged["latitude"], errors="coerce"),
        "lon": pd.to_numeric(merged["longitude"], errors="coerce"),
        "location_precision_km": precision,
        "country": merged["country_code"].fillna("").astype(str).str.strip().str.upper(),
        "place": merged["city"].fillna("").astype(str).str.strip(),
        "shape": merged["shape"].replace("NA", "").fillna("").astype(str).str.strip().str.lower(),
        "duration_s": pd.to_numeric(merged["duration_seconds"], errors="coerce"),
        "text": text,
        "official_class": None,
        "official_identification": None,
    })
    out["_state"] = merged["state"].fillna("").astype(str).str.strip().str.lower().to_numpy()
    out = out[when.notna().to_numpy()]
    state = out.pop("_state")
    final = _finalise(out)
    final["_state"] = state.to_numpy()
    return final


_XLSX_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def read_xlsx_table(data: bytes) -> pd.DataFrame:
    """First worksheet of an .xlsx file as strings, header from row one (stdlib only)."""
    with zipfile.ZipFile(stdio.BytesIO(data)) as archive:
        names = archive.namelist()
        sheets = sorted(n for n in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", n))
        if not sheets:
            raise ValueError("no worksheet in xlsx file")
        parts = {n: archive.read(n) for n in [sheets[0]] + [s for s in names
                                                           if s == "xl/sharedStrings.xml"]}
    for blob in parts.values():
        if b"<!DOCTYPE" in blob[:4096] or b"<!ENTITY" in blob[:4096]:
            raise ValueError("xlsx part declares a DTD; refusing to parse")
    shared: list[str] = []
    if "xl/sharedStrings.xml" in parts:
        for item in ET.fromstring(parts["xl/sharedStrings.xml"]).iter(_XLSX_NS + "si"):
            shared.append("".join(node.text or "" for node in item.iter(_XLSX_NS + "t")))
    rows: list[dict[int, str]] = []
    for row in ET.fromstring(parts[sheets[0]]).iter(_XLSX_NS + "row"):
        cells: dict[int, str] = {}
        for position, cell in enumerate(row.iter(_XLSX_NS + "c")):
            ref = re.match(r"[A-Z]+", cell.get("r") or "")
            index = position
            if ref:
                index = 0
                for letter in ref.group(0):
                    index = index * 26 + ord(letter) - 64
                index -= 1
            value = cell.find(_XLSX_NS + "v")
            if cell.get("t") == "s" and value is not None and value.text is not None:
                cells[index] = shared[int(value.text)]
            elif cell.get("t") == "inlineStr":
                cells[index] = "".join(n.text or "" for n in cell.iter(_XLSX_NS + "t"))
            else:
                cells[index] = (value.text or "") if value is not None else ""
        rows.append(cells)
    if not rows:
        return pd.DataFrame()
    width = max(max(r) for r in rows if r) + 1
    header = [rows[0].get(i, f"col{i}").strip() for i in range(width)]
    body = [[r.get(i, "") for i in range(width)] for r in rows[1:]]
    return pd.DataFrame(body, columns=header, dtype=object)


def _geipan_place(title: str) -> str:
    """Commune name from a GEIPAN case title such as 'MARIGOT (LE) (972) --.--.1937'."""
    name = re.sub(r"^(?:\[[^\]]*\]\s*)+", "", title or "").strip()
    name = re.sub(r"\s*\([0-9AB]{2,3}\)\s*[-\d.]*\s*$", "", name)
    article = re.search(r"\s*\((LE|LA|LES|L')\)\s*$", name)
    if article:
        lead = article.group(1)
        name = (lead if lead.endswith("'") else lead + " ") + name[:article.start()]
    return name.strip().title() or "Unknown"


def normalise_geipan(raw: pd.DataFrame) -> pd.DataFrame:
    """Normalise the GEIPAN case export (French headers); partial dates keep their precision."""
    def col(name: str) -> pd.Series:
        if name in raw.columns:
            return raw[name].fillna("").astype(str).str.strip()
        return pd.Series([""] * len(raw), index=raw.index, dtype=object)

    parts = col("Observation date").str.extract(r"^(?P<d>[\d-]{1,2})/(?P<m>[\d-]{1,2})/(?P<y>\d{4})$")
    year = pd.to_numeric(parts["y"], errors="coerce")
    month = pd.to_numeric(parts["m"], errors="coerce")
    day = pd.to_numeric(parts["d"], errors="coerce")
    precision = np.where(month.isna(), "year", np.where(day.isna(), "month", "day"))
    stamp = pd.to_datetime(pd.DataFrame({"year": year, "month": month.fillna(1),
                                         "day": day.fillna(1)}), errors="coerce")
    kind = col("Type de cas")
    vehicle = kind.str.contains("ronautique|maritime", regex=True)
    region = col("Region")
    identification = (col("Phenomenon") + " | " + col("Identification")).str.strip(" |")
    out = pd.DataFrame({
        "id": "geipan-" + col("ID Etude de Cas"),
        "source": "geipan",
        "source_file": "geipan",
        "datetime": stamp.dt.strftime("%Y-%m-%d"),
        "date_precision": precision,
        "time_basis": "local",
        "lat": pd.to_numeric(col("Latitude"), errors="coerce"),
        "lon": pd.to_numeric(col("Longitude"), errors="coerce"),
        "location_precision_km": np.where(vehicle, PRECISION_VEHICLE_KM, PRECISION_COMMUNE_KM),
        "country": np.where(region.str.strip() == "Autre", "", "FR"),
        "place": col("Titre du Cas").map(_geipan_place),
        "shape": "",
        "duration_s": np.nan,
        "text": _clean_text(col("Détails")),
        "official_class": col("Classification").str.upper().where(
            col("Classification").str.upper().isin(list("ABCD")), None),
        "official_identification": identification.where(identification != "", None),
    })
    out = out[stamp.notna().to_numpy() & (col("ID Etude de Cas") != "").to_numpy()]
    return _finalise(out)


def _dedupe_nuforc(newer: pd.DataFrame, older: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Drop rows of ``older`` that repeat a ``newer`` report.

    Same report = same place name, same first 60 normalised characters
    of text (at least 12), and timestamps within 36 hours (one copy is in
    UTC, the other in local time).
    """
    def keyed(frame: pd.DataFrame) -> pd.DataFrame:
        norm_text = (frame["text"].str.lower().str.replace(r"[^a-z0-9]+", "", regex=True)
                     .str[:60])
        norm_place = frame["place"].str.lower().str.replace(r"[^a-z0-9]+", "", regex=True)
        return pd.DataFrame({"k_place": norm_place, "k_state": frame["_state"],
                             "k_text": norm_text,
                             "when": pd.to_datetime(frame["datetime"].str[:19], errors="coerce"),
                             "row": np.arange(len(frame))})

    if newer.empty or older.empty:
        return older, 0
    old_keys = keyed(older)
    old_keys = old_keys[old_keys["k_text"].str.len() >= 12]
    new_keys = keyed(newer).drop_duplicates(subset=["k_place", "k_text", "when"])
    pairs = old_keys.merge(new_keys, on=["k_place", "k_text"], suffixes=("", "_new"))
    close = (pairs["when"] - pairs["when_new"]).abs() <= pd.Timedelta(hours=36)
    drop = np.unique(pairs.loc[close, "row"].to_numpy())
    keep = np.ones(len(older), dtype=bool)
    keep[drop] = False
    return older[keep].reset_index(drop=True), int(drop.size)


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def _read_csv(path: Path, header: int | None) -> pd.DataFrame:
    return pd.read_csv(path, header=header, dtype=str, keep_default_na=False, na_values=[],
                       on_bad_lines="skip", encoding="utf-8", encoding_errors="replace")


def _load_source(name: str, force: bool) -> pd.DataFrame:
    """Download one source's parts and normalise them."""
    spec = SOURCE_FILES[name]
    paths = {part: _fetch(url, RAW_DIR / part, force) for part, url in spec["parts"].items()}
    if name == "nuforc_planetsig_2014":
        return normalise_planetsig(_read_csv(paths["planetsig_scrubbed.csv"], None))
    if name == "nuforc_tidytuesday_2023":
        return normalise_tidytuesday(_read_csv(paths["tidytuesday_ufo_sightings.csv"], 0),
                                     _read_csv(paths["tidytuesday_places.csv"], 0))
    return normalise_geipan(read_xlsx_table(paths["geipan_export_cas.xlsx"].read_bytes()))


def _date_range(frame: pd.DataFrame) -> tuple[str | None, str | None]:
    if frame.empty:
        return None, None
    days = frame["datetime"].str[:10]
    return str(days.min()), str(days.max())


def summarise(frame: pd.DataFrame) -> dict[str, Any]:
    """Counts per source and per tag, and the date range per source, for normalised reports."""
    sources: dict[str, dict[str, Any]] = {}
    for source, part in frame.groupby("source", sort=True):
        low, high = _date_range(part)
        recent = part[part["datetime"].str[:4] >= str(S2_ERA_START_YEAR)]
        sources[str(source)] = {
            "count": int(len(part)), "date_min": low, "date_max": high,
            "geocoded": int(part["lat"].notna().sum()),
            "since_2016": int(len(recent)),
        }
        classes = part["official_class"].dropna()
        if len(classes):
            sources[str(source)]["official_class"] = {
                str(k): int(v) for k, v in classes.value_counts().sort_index().items()}
    recent_all = frame[frame["datetime"].str[:4] >= str(S2_ERA_START_YEAR)] if len(frame) else frame
    return {
        "total": int(len(frame)),
        "sources": sources,
        "tags": {tag: int(sum(tag in tags for tags in frame["tags"])) for tag in TAGS},
        "tags_since_2016": {tag: int(sum(tag in tags for tags in recent_all["tags"]))
                            for tag in TAGS},
    }


def write_reports(frame: pd.DataFrame, path: Path | None = None) -> Path:
    """Write normalised reports as JSON lines (atomic replace); returns the path."""
    target = path or REPORTS_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    frame.loc[:, list(_COLUMNS)].to_json(tmp, orient="records", lines=True, force_ascii=False)
    tmp.replace(target)
    _CACHE.clear()
    return target


def build(force: bool = False) -> dict[str, Any]:
    """Download, normalise, de-duplicate and write every reachable source.

    Returns a summary: ``total``, ``sources`` (count, date_min, date_max,
    geocoded, since_2016 per source), ``tags`` and ``tags_since_2016``
    (count per tag), ``files`` (status per downloaded copy; a failed copy is
    reported there, never silently dropped), ``duplicates_removed``,
    ``not_ingested`` and ``path``. With ``force=False`` an existing build is
    returned without any network access. Raises ``ReportsUnavailable`` when
    no source at all could be read. A build made with older tag rules is
    redone from the cached downloads (no network unless a download is missing).
    """
    if not force and REPORTS_PATH.exists() and SUMMARY_PATH.exists():
        stored = dict(json.loads(SUMMARY_PATH.read_text()))
        if stored.get("rules_version") == RULES_VERSION:
            return stored
    frames: dict[str, pd.DataFrame] = {}
    files: dict[str, dict[str, Any]] = {}
    for name, spec in SOURCE_FILES.items():
        try:
            frame = _load_source(name, force)
            low, high = _date_range(frame)
            frames[name] = frame
            files[name] = {"status": "ok", "rows": int(len(frame)), "date_min": low,
                           "date_max": high, "urls": list(spec["parts"].values())}
        except Exception as exc:  # one dead source must not sink the others
            logger.warning("report source %s failed: %s", name, exc)
            files[name] = {"status": "failed", "reason": f"{type(exc).__name__}: {exc}"[:300],
                           "rows": 0, "urls": list(spec["parts"].values())}
    if not frames:
        raise ReportsUnavailable("no report source could be read: " + json.dumps(files)[:600])
    removed = 0
    if "nuforc_planetsig_2014" in frames and "nuforc_tidytuesday_2023" in frames:
        frames["nuforc_planetsig_2014"], removed = _dedupe_nuforc(
            frames["nuforc_tidytuesday_2023"], frames["nuforc_planetsig_2014"])
    merged = pd.concat([f.drop(columns=["_state"], errors="ignore") for f in frames.values()],
                       ignore_index=True)
    before = len(merged)
    merged = merged.drop_duplicates(subset="id").reset_index(drop=True)
    removed += before - len(merged)
    merged = merged.sort_values(["datetime", "id"], kind="stable").reset_index(drop=True)
    path = write_reports(merged)
    summary = summarise(merged)
    summary.update({
        "built_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "path": str(path), "files": files, "duplicates_removed": int(removed),
        "rules_version": RULES_VERSION,
        "not_ingested": dict(SOURCES_NOT_INGESTED),
    })
    SUMMARY_PATH.write_text(json.dumps(summary, indent=1, ensure_ascii=False))
    return summary


# --------------------------------------------------------------------------
# Load
# --------------------------------------------------------------------------

_CACHE: dict[str, tuple[tuple[int, int], pd.DataFrame, "_Index"]] = {}


@dataclass(frozen=True)
class _Index:
    """Geocoded, dated reports sorted by latitude, with dates as day numbers."""

    frame: pd.DataFrame
    lat: np.ndarray
    lon: np.ndarray
    day_start: np.ndarray
    day_end: np.ndarray
    source: np.ndarray
    #: False for cases the agency itself explained (MATCH_EXCLUDED_CLASSES).
    matchable: np.ndarray
    coverage: dict[str, tuple[int, int]]


def _interval_end(start: pd.Series, precision: pd.Series) -> pd.Series:
    """Last day of each report's date uncertainty interval."""
    end = start.copy()
    month = (precision == "month").to_numpy()
    year = (precision == "year").to_numpy()
    end[month] = start[month] + pd.offsets.MonthEnd(0)
    end[year] = start[year] + pd.offsets.YearEnd(0)
    return end


def _read_reports(path: Path) -> pd.DataFrame:
    with path.open(encoding="utf-8") as handle:
        records = [json.loads(line) for line in handle if line.strip()]
    frame = pd.DataFrame.from_records(records) if records else pd.DataFrame(
        columns=list(_COLUMNS))
    for column in _COLUMNS:
        if column not in frame.columns:
            frame[column] = None
    for column in ("lat", "lon", "location_precision_km", "duration_s"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    for column in ("id", "source", "datetime", "date_precision", "country", "place", "text"):
        frame[column] = frame[column].fillna("").astype(str)
    frame["tags"] = [list(t) if isinstance(t, (list, tuple)) else [] for t in frame["tags"]]
    frame["date"] = pd.to_datetime(frame["datetime"].str[:10], format="%Y-%m-%d",
                                   errors="coerce")
    frame["date_end"] = _interval_end(frame["date"], frame["date_precision"])
    return frame.loc[:, list(_COLUMNS) + ["date", "date_end"]]


def _build_index(frame: pd.DataFrame) -> _Index:
    usable = frame["lat"].notna() & frame["lon"].notna() & frame["date"].notna()
    part = frame[usable].sort_values("lat", kind="stable").reset_index(drop=True)
    matchable = ~part["official_class"].isin(MATCH_EXCLUDED_CLASSES).to_numpy(dtype=bool)
    day_start = part["date"].to_numpy(dtype="datetime64[D]").astype(np.int64)
    day_end = part["date_end"].to_numpy(dtype="datetime64[D]").astype(np.int64)
    source = part["source"].to_numpy(dtype=object)
    coverage = {str(name): (int(day_start[source == name].min()),
                            int(day_end[source == name].max()))
                for name in pd.unique(source)}
    return _Index(part, part["lat"].to_numpy(dtype=np.float64),
                  part["lon"].to_numpy(dtype=np.float64), day_start, day_end, source,
                  matchable, coverage)


def _loaded() -> tuple[pd.DataFrame, _Index]:
    """Reports and their match index, read once per file version."""
    path = REPORTS_PATH
    if not path.exists():
        try:
            build()
        except ReportsUnavailable:
            raise
        except Exception as exc:
            raise ReportsUnavailable(f"report build failed: {exc}") from exc
    stat = path.stat()
    stamp = (stat.st_mtime_ns, stat.st_size)
    cached = _CACHE.get(str(path))
    if cached is None or cached[0] != stamp:
        frame = _read_reports(path)
        _CACHE.clear()
        _CACHE[str(path)] = (stamp, frame, _build_index(frame))
        cached = _CACHE[str(path)]
    return cached[1], cached[2]


def load_reports() -> pd.DataFrame:
    """All normalised reports (a copy), building the file on first use.

    Columns: the record fields in the module docstring plus ``date`` and
    ``date_end`` (first and last day of the report's date uncertainty).
    Raises ``ReportsUnavailable`` if nothing was ever built and no source is
    reachable.
    """
    return _loaded()[0].copy()


def _specificity(frame: pd.DataFrame) -> pd.Series:
    """Rank value: weighted claims, +2 for GEIPAN class D, minus location precision / 5 km."""
    score = np.zeros(len(frame), dtype=np.float64)
    for tag, weight in TAG_WEIGHTS.items():
        score += weight * np.fromiter((tag in tags for tags in frame["tags"]), dtype=bool,
                                      count=len(frame))
    score += 2.0 * (frame["official_class"] == "D").to_numpy(dtype=bool)
    score -= frame["location_precision_km"].fillna(50.0).to_numpy() / 5.0
    return pd.Series(score, index=frame.index)


def landing_trace_reports(min_year: int = 2016,
                          tags: Sequence[str] = ("landing", "physical_trace", "crash_retrieval")
                          ) -> pd.DataFrame:
    """Reports from ``min_year`` on that CLAIM any of ``tags``, best location precision first.

    Ties are ordered by ``specificity`` (added column; see ``TAG_WEIGHTS``)
    and then newest first. Reports GEIPAN classed A or B stay in the result;
    filter on ``official_class`` if only unexplained cases are wanted.
    """
    frame = load_reports()
    wanted = set(tags)
    keep = (frame["date"].dt.year >= min_year).to_numpy() & np.fromiter(
        (bool(wanted.intersection(t)) for t in frame["tags"]), dtype=bool, count=len(frame))
    out = frame[keep].copy()
    out["specificity"] = _specificity(out)
    out["_precision"] = out["location_precision_km"].fillna(np.inf)
    out = out.sort_values(["_precision", "specificity", "date"], ascending=[True, False, False],
                          kind="stable")
    return out.drop(columns="_precision").reset_index(drop=True)


# --------------------------------------------------------------------------
# Seeded regions
# --------------------------------------------------------------------------

def _haversine_km(lat: float, lon: float, lats: np.ndarray, lons: np.ndarray) -> np.ndarray:
    phi1, phi2 = np.radians(lat), np.radians(lats)
    dphi = phi2 - phi1
    dlam = np.radians(lons - lon)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _plain_bbox(lat: float, lon: float, half_size_m: float) -> tuple[float, float, float, float]:
    west, south, east, north = io.point_bbox(lat, lon, half_size_m)
    return (float(west), float(south), float(east), float(north))


def _month_day(day: date) -> str:
    return "02-28" if (day.month, day.day) == (2, 29) else day.strftime("%m-%d")


def seeded_regions(n: int = 12, half_size_m: float = 4000.0) -> list[Region]:
    """Up to ``n`` search regions, one per selected witness report.

    Eligible reports: dated to the day, 2016 or later, at least 61 days old,
    geocoded, claiming a landing, physical trace or crash, not marked as a
    hoax, not explained in a NUFORC staff note, and not classed A/B by GEIPAN. They are picked greedily by
    ``specificity`` with a penalty of 1.5 per region already chosen in the
    same country and never within two box widths of an earlier pick. Returns
    fewer than ``n`` (possibly none) when too few reports qualify.
    """
    if n <= 0:
        return []
    pool = landing_trace_reports(min_year=S2_ERA_START_YEAR)
    today = pd.Timestamp(date.today())
    ok = (pool["date_precision"].isin(["minute", "day"]) & pool["lat"].notna()
          & pool["lon"].notna() & (pool["lat"].abs() <= 80.0)
          & (pool["date"] + pd.Timedelta(days=SEED_WINDOW_DAYS) <= today)
          & ~pool["official_class"].isin(MATCH_EXCLUDED_CLASSES)
          & ~pool["text"].str.contains(HOAX_PATTERN, case=False, regex=True)
          & ~pool["text"].str.contains(EDITOR_EXPLAINED_PATTERN, case=False, regex=True))
    pool = pool[ok].sort_values(["specificity", "location_precision_km", "date"],
                                ascending=[False, True, False], kind="stable")
    pool = pool.reset_index(drop=True)
    if pool.empty:
        return []
    score = pool["specificity"].to_numpy(dtype=np.float64).copy()
    lats, lons = pool["lat"].to_numpy(), pool["lon"].to_numpy()
    country = pool["country"].to_numpy(dtype=object)
    regions: list[Region] = []
    used_ids: set[str] = set()
    for _ in range(min(n, len(pool))):
        pick = int(np.argmax(score))
        if not np.isfinite(score[pick]):
            break
        row = pool.iloc[pick]
        near = _haversine_km(float(lats[pick]), float(lons[pick]), lats, lons)
        score[near <= 4.0 * half_size_m / 1000.0] = -np.inf
        score[(country == country[pick]) & np.isfinite(score)] -= 1.5
        when = row["date"].date()
        precision = float(row["location_precision_km"])
        slug = _slug(str(row["place"]))
        rid = f"S{len(regions) + 1:02d}-{slug}"
        while rid in used_ids:
            rid += "-B"
        used_ids.add(rid)
        covered = min(1.0, (2 * half_size_m / 1000.0) ** 2 / (np.pi * precision ** 2))
        regions.append(Region(
            id=rid,
            name=f"Seeded: {row['place']}, {row['country'] or '??'} "
                 f"({row['source']} report of {when.isoformat()})",
            bbox=_plain_bbox(float(row["lat"]), float(row["lon"]), half_size_m),
            kind="seeded",
            season=(_month_day(when), _month_day(when + timedelta(days=SEED_WINDOW_DAYS))),
            notes=(f"Box of {2 * half_size_m / 1000.0:.0f} km centred on the geocode of the "
                   f"place named in an unverified witness report, not on a surveyed site. The "
                   f"true site, if any, may lie anywhere within about {precision:.0f} km of the "
                   f"centre; this box covers roughly {covered:.0%} of that area, so a null "
                   f"result here does not test the report. Claimed (not established): "
                   f"{', '.join(row['tags'])}."),
            seed={
                "source": row["source"], "report_id": row["id"], "datetime": row["datetime"],
                "summary": str(row["text"])[:300],
                "location_precision_km": precision,
                "date_precision": row["date_precision"], "tags": list(row["tags"]),
                "official_class": row["official_class"] if isinstance(row["official_class"], str)
                else None,
                "place": row["place"], "country": row["country"],
                "lat": float(row["lat"]), "lon": float(row["lon"]),
            },
        ))
    return regions


# --------------------------------------------------------------------------
# Matching
# --------------------------------------------------------------------------

def _onset_window(candidate: Candidate) -> tuple[int, int] | None:
    """Onset window as day numbers, or None when either end is missing or unreadable."""
    if not candidate.absent_until or not candidate.present_from:
        return None
    try:
        first = np.datetime64(str(candidate.absent_until)[:10], "D").astype(np.int64)
        last = np.datetime64(str(candidate.present_from)[:10], "D").astype(np.int64)
    except ValueError:
        return None
    if first < -10 ** 6 or last < -10 ** 6:  # NaT
        return None
    return (int(min(first, last)), int(max(first, last)))


def _nearby(index: _Index, lat: float, lon: float, radius_km: float
            ) -> tuple[np.ndarray, np.ndarray]:
    """Index rows within ``radius_km`` and their distances (latitude band, then exact)."""
    if not (np.isfinite(lat) and np.isfinite(lon)) or radius_km <= 0 or index.lat.size == 0:
        return np.empty(0, dtype=np.int64), np.empty(0, dtype=np.float64)
    dlat = radius_km / _KM_PER_DEG
    lo = int(np.searchsorted(index.lat, lat - dlat, side="left"))
    hi = int(np.searchsorted(index.lat, lat + dlat, side="right"))
    rows = np.arange(lo, hi)
    if rows.size == 0:
        return rows, np.empty(0, dtype=np.float64)
    distance = _haversine_km(lat, lon, index.lat[lo:hi], index.lon[lo:hi])
    inside = distance <= radius_km
    return rows[inside], distance[inside]


def match_reports(candidate: Candidate, radius_km: float = 30.0, days: int = 7
                  ) -> list[dict[str, Any]]:
    """Reports near a candidate whose date lies inside its padded onset window.

    A report matches when its geocode is within ``radius_km`` of the candidate
    and its whole date uncertainty (one day for dated reports, the month or
    year for partial dates) lies within ``absent_until - days`` ..
    ``present_from + days``. GEIPAN class A/B cases never match. Returns
    ``[]`` when the candidate has no onset window, and also (with a logged
    warning) when no report data is available: use ``report_check`` to tell
    "nothing reported" from "could not look". Sorted nearest first. Each
    match: ``id``, ``source``, ``datetime``, ``date_precision``,
    ``distance_km``, ``tags``, ``text`` (first 300 characters),
    ``location_precision_km``, ``official_class``, ``place``, ``country``,
    ``claim_status`` (always "unverified witness report").
    """
    window = _onset_window(candidate)
    if window is None:
        return []
    try:
        index = _loaded()[1]
    except ReportsUnavailable as exc:
        logger.warning("witness reports unavailable, nothing matched: %s", exc)
        return []
    rows, distance = _nearby(index, float(candidate.lat), float(candidate.lon), radius_km)
    if rows.size == 0:
        return []
    timely = ((index.day_start[rows] >= window[0] - days)
              & (index.day_end[rows] <= window[1] + days) & index.matchable[rows])
    rows, distance = rows[timely], distance[timely]
    order = np.argsort(distance, kind="stable")
    matches: list[dict[str, Any]] = []
    for row_number, dist in zip(rows[order], distance[order]):
        row = index.frame.iloc[int(row_number)]
        official = row["official_class"]
        matches.append({
            "id": row["id"], "source": row["source"], "datetime": row["datetime"],
            "date_precision": row["date_precision"],
            "distance_km": round(float(dist), 2), "tags": list(row["tags"]),
            "text": str(row["text"])[:300],
            "location_precision_km": float(row["location_precision_km"]),
            "official_class": official if isinstance(official, str) else None,
            "place": row["place"], "country": row["country"],
            "claim_status": "unverified witness report",
        })
    return matches


def _iso_day(day: int) -> str:
    return str(np.datetime64(int(day), "D"))


def report_check(candidate: Candidate, radius_km: float = 30.0, days: int = 7) -> CheckResult:
    """``match_reports`` as a CheckResult that separates "nothing reported" from "could not look".

    ``not_run`` when the candidate has no onset window, the report data is
    unavailable, or no source covers the place and time (a source covers a
    place when it holds at least 5 reports of any date within 100 km, and a
    time when the padded window overlaps its date range). Otherwise
    ``does_not_explain`` (a witness report is never an explanation), with the
    matches and ``expected_by_chance`` in ``evidence``: the number of matches
    expected from the local reporting rate since 2016 alone. A match where
    that number is not well below 1 carries no evidential weight.
    """
    name, category, source = "witness_reports", "report", "NUFORC public copies; GEIPAN"
    window = _onset_window(candidate)
    if window is None:
        return CheckResult(name, category, "not_run", "candidate has no dated onset window", source)
    try:
        index = _loaded()[1]
    except ReportsUnavailable as exc:
        return CheckResult(name, category, "not_run", f"report data unavailable: {exc}"[:300],
                           source)
    lat, lon = float(candidate.lat), float(candidate.lon)
    low, high = window[0] - days, window[1] + days
    wide_rows, _ = _nearby(index, lat, lon, COVERAGE_RADIUS_KM)
    near_rows, _ = _nearby(index, lat, lon, radius_km)
    era_start = int(np.datetime64(f"{S2_ERA_START_YEAR}-01-01", "D").astype(np.int64))
    covering: dict[str, dict[str, Any]] = {}
    expected = 0.0
    for src, (first, last) in index.coverage.items():
        local = int(np.count_nonzero(index.source[wide_rows] == src))
        overlap = min(high, last) - max(low, first) + 1
        if local < COVERAGE_MIN_REPORTS or overlap <= 0:
            continue
        base_first = max(first, era_start)
        base_days = max(last - base_first + 1, 1)
        in_base = ((index.source[near_rows] == src) & index.matchable[near_rows]
                   & (index.day_start[near_rows] >= base_first))
        rate = float(np.count_nonzero(in_base)) / base_days
        expected += rate * overlap
        covering[src] = {"reports_within_100km": local, "date_min": _iso_day(first),
                         "date_max": _iso_day(last), "window_days_covered": int(overlap),
                         "window_days": int(high - low + 1)}
    if not covering:
        return CheckResult(
            name, category, "not_run",
            "no ingested report source covers this place and time (sources: "
            + "; ".join(f"{s} {_iso_day(a)}..{_iso_day(b)}" for s, (a, b) in
                        index.coverage.items()) + ")", source,
            {"window": [_iso_day(low), _iso_day(high)]})
    matches = match_reports(candidate, radius_km, days)
    detail = (f"{len(matches)} unverified report(s) within {radius_km:g} km inside "
              f"{_iso_day(low)}..{_iso_day(high)}; about {expected:.2f} expected by chance from "
              f"the local reporting rate; sources covering here: {', '.join(sorted(covering))}")
    return CheckResult(name, category, "does_not_explain", detail, source,
                       {"matches": matches, "expected_by_chance": round(expected, 3),
                        "coverage": covering, "window": [_iso_day(low), _iso_day(high)],
                        "radius_km": radius_km, "pad_days": days})
