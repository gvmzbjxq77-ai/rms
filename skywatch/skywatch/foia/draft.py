"""Draft public-records requests and a ground-truth plan for a candidate.

Everything here produces text for a person to review, edit and send. Nothing
is sent. Requests ask, in neutral terms, for records about a dated surface
change at exact coordinates; they assert nothing about its cause.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from shapely.geometry import Point, shape
from shapely.prepared import prep

from ..core import config
from ..core.models import Candidate

COUNTRIES_FILE = config.DATA / "reference" / "ne_110m_admin_0_countries.geojson"

#: Access-to-information laws for the jurisdictions drafts are written for.
LAWS: dict[str, dict[str, str]] = {
    "US": {"law": "Freedom of Information Act, 5 U.S.C. § 552", "deadline": "20 working days"},
    "GB": {"law": "Freedom of Information Act 2000 and the Environmental Information Regulations 2004", "deadline": "20 working days"},
    "CA": {"law": "Access to Information Act (R.S.C. 1985, c. A-1)", "deadline": "30 days"},
    "AU": {"law": "Freedom of Information Act 1982 (Cth)", "deadline": "30 days"},
    "NZ": {"law": "Official Information Act 1982", "deadline": "20 working days"},
    "FR": {"law": "Code des relations entre le public et l'administration, Livre III (accès aux documents administratifs)", "deadline": "one month"},
    "DE": {"law": "Informationsfreiheitsgesetz (IFG) and Umweltinformationsgesetz (UIG)", "deadline": "one month"},
    "BR": {"law": "Lei de Acesso à Informação, Lei nº 12.527/2011", "deadline": "20 days"},
    "IN": {"law": "Right to Information Act, 2005", "deadline": "30 days"},
    "MX": {"law": "Ley General de Transparencia y Acceso a la Información Pública", "deadline": "20 working days"},
    "CL": {"law": "Ley N° 20.285 sobre Acceso a la Información Pública", "deadline": "20 working days"},
    "AR": {"law": "Ley 27.275 de Derecho de Acceso a la Información Pública", "deadline": "15 working days"},
    "ZA": {"law": "Promotion of Access to Information Act 2 of 2000", "deadline": "30 days"},
}
EU_NOTE = ("Records held by European Union institutions can also be requested under "
           "Regulation (EC) No 1049/2001.")
EU_MEMBERS = {"AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE",
              "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE"}


@lru_cache(maxsize=1)
def _countries() -> list[tuple[Any, str, str]]:
    features = json.loads(COUNTRIES_FILE.read_text())["features"]
    out = []
    for feature in features:
        props = feature["properties"]
        iso = props.get("ISO_A2_EH") or props.get("ISO_A2") or ""
        out.append((prep(shape(feature["geometry"])), iso if iso != "-99" else "", props.get("ADMIN", "")))
    return out


def country_of(lat: float, lon: float) -> dict[str, str]:
    """Offline country lookup from small-scale Natural Earth outlines.

    Returns ``{"iso": "", "name": "open ocean or unassigned"}`` when no
    country contains the point. Coastlines are coarse (1:110 million), so
    points within a few kilometres of a coast or border can be misassigned.
    """
    if not COUNTRIES_FILE.exists():
        return {"iso": "", "name": "unknown (country outlines not available)"}
    point = Point(lon, lat)
    for geometry, iso, name in _countries():
        if geometry.contains(point):
            return {"iso": iso, "name": name}
    return {"iso": "", "name": "open ocean or unassigned"}


def _window(candidate: Candidate) -> tuple[str, str]:
    if candidate.absent_until and candidate.present_from:
        return candidate.absent_until, candidate.present_from
    today = date.today()
    return (today - timedelta(days=365)).isoformat(), today.isoformat()


def _place(candidate: Candidate) -> str:
    return (f"latitude {candidate.lat:.5f}, longitude {candidate.lon:.5f} (WGS84), "
            f"and the area within 5 km of that point")


def _body(candidate: Candidate, agency: str, law: str, deadline: str, records: list[str],
          requester_name: str, requester_contact: str) -> str:
    start, end = _window(candidate)
    dated = bool(candidate.absent_until and candidate.present_from)
    when = (f"between {start} and {end}" if dated else
            f"during the past twelve months ({start} to {end}); the feature has no dated onset")
    lines = [
        f"**To:** {agency}",
        f"**Re:** Request for records under the {law}",
        "",
        "Dear Records Officer,",
        "",
        f"Under the {law}, I request copies of the records described below.",
        "",
        f"**Location:** {_place(candidate)}.",
        f"**Period:** {when}.",
        "",
        "**Background.** Public satellite imagery (Copernicus Sentinel-2) shows a change in the "
        f"ground surface of about {candidate.area_m2:,.0f} m² at this location in this period. "
        "I am trying to establish its ordinary cause and ask only for records that would help do so.",
        "",
        "**Records requested:**",
        *[f"{i}. {text}" for i, text in enumerate(records, start=1)],
        "",
        "**Format.** Electronic copies are preferred. If any part is withheld, please release "
        "the remainder and cite the exemption relied on for each redaction.",
        "",
        "**Fees.** This request is made for research in the public interest and not for "
        "commercial use. I ask that fees be waived or, failing that, to be told the estimated "
        "cost before any is incurred.",
        "",
        f"I look forward to your reply within the statutory period ({deadline}).",
        "",
        "Yours faithfully,",
        requester_name,
        requester_contact,
    ]
    return "\n".join(lines)


def draft_request(candidate: Candidate, requester_name: str = "[REQUESTER NAME]",
                  requester_contact: str = "[CONTACT]") -> list[dict[str, str]]:
    """Draft requests for the authorities most likely to hold explanatory records.

    Each draft is ``{agency, jurisdiction, law, subject, body_markdown}``.
    United States: the FAA, the land manager, the Department of the Air Force
    and AARO. Listed countries: the civil-aviation and land authorities under
    the national law. Elsewhere a single note says that no access law is
    listed for the jurisdiction; no law is invented.
    """
    country = country_of(candidate.lat, candidate.lon)
    iso, name = country["iso"], country["name"]
    start, end = _window(candidate)
    subject = f"Records about a surface change at {candidate.lat:.4f}, {candidate.lon:.4f} ({start} to {end})"
    aviation = [
        "Radar and air-traffic surveillance data, controller logs and recordings covering the location and period.",
        "Pilot reports, incident or accident notifications, and search-and-rescue records for the location and period.",
        "Notices to airmen, temporary flight restrictions and airspace reservations covering the location and period.",
    ]
    land = [
        "Permits, leases, rights-of-way, mining or exploration claims, and notices of operations covering the location.",
        "Records of earthworks, prescribed burns, fire incidents, clean-ups or emergency responses at the location in the period.",
        "Any survey, inspection or enforcement report that mentions ground disturbance at the location in the period.",
    ]
    drafts: list[dict[str, str]] = []

    def add(agency: str, law: str, deadline: str, records: list[str]) -> None:
        drafts.append({"agency": agency, "jurisdiction": name, "law": law, "subject": subject,
                       "body_markdown": _body(candidate, agency, law, deadline, records,
                                              requester_name, requester_contact)})

    if iso == "US":
        law, deadline = LAWS["US"]["law"], LAWS["US"]["deadline"]
        add("Federal Aviation Administration, FOIA Program Management Branch", law, deadline, aviation)
        add("The federal land manager for this location (Bureau of Land Management, U.S. Forest "
            "Service, National Park Service or Department of Defense: confirm which from the "
            "surface-management map before sending)", law, deadline, land)
        add("Department of the Air Force, FOIA Requester Service Center (including NORAD / "
            "USNORTHCOM air-surveillance records)", law, deadline,
            ["Air-surveillance track data and event logs covering the location and period.",
             "Records of military flight operations, training events or range activity at or over the location in the period."])
        add("All-domain Anomaly Resolution Office (via the Office of the Secretary of Defense FOIA office)",
            law, deadline,
            ["Any report, case file or sensor record that refers to the location in the period."])
        drafts[0]["body_markdown"] += (
            "\n\n_Note to requester: NOAA NEXRAD weather-radar archives are public and can be "
            "downloaded for the location and period without a request._")
    elif iso in LAWS:
        law, deadline = LAWS[iso]["law"], LAWS[iso]["deadline"]
        add(f"The national civil-aviation authority of {name}", law, deadline, aviation)
        add(f"The authority responsible for land, mining and environmental permits at this location in {name}",
            law, deadline, land)
        if iso in EU_MEMBERS:
            drafts[-1]["body_markdown"] += f"\n\n_Note to requester: {EU_NOTE}_"
    else:
        note = (f"No access-to-information law is listed here for {name}. Check whether one exists "
                "before writing; if none does, the civil-aviation authority and the land or mining "
                "ministry can still be asked informally for the records below.\n\n"
                + "\n".join(f"- {text}" for text in aviation + land))
        if iso in EU_MEMBERS:
            note += f"\n\n{EU_NOTE}"
        drafts.append({"agency": "(to be identified)", "jurisdiction": name, "law": "none listed",
                       "subject": subject, "body_markdown": note})
    return drafts


def _road_distance(candidate: Candidate) -> float | None:
    for check in candidate.checks:
        if check.check == "osm_infrastructure":
            value = check.evidence.get("nearest_road_m")
            return float(value) if isinstance(value, (int, float)) else None
    return None


def ground_truth_plan(candidate: Candidate) -> str:
    """A field plan that can falsify: what to record and what each cause would look like."""
    country = country_of(candidate.lat, candidate.lon)
    road = _road_distance(candidate)
    access = (f"The nearest mapped road or track is about {road / 1000:.1f} km from the footprint."
              if road is not None else
              "No road or track is mapped within the search radius; plan for cross-country travel "
              "and check recent imagery for unmapped tracks.")
    open_checks = [c for c in candidate.checks
                   if c.status in ("inconclusive", "not_run") and ":" not in c.check]
    lines = [
        f"# Ground-truth plan: {candidate.id}",
        "",
        f"**Site:** {candidate.lat:.5f}, {candidate.lon:.5f} ({country['name']}). "
        f"Footprint about {candidate.area_m2:,.0f} m². "
        f"Onset window: {candidate.absent_until or 'unknown'} to {candidate.present_from or 'unknown'}.",
        "",
        "## Before going",
        f"- **Access.** {access}",
        "- **Permission.** Establish who owns or manages the land and get written permission. "
        "Military ranges, mining concessions, protected areas and indigenous lands need their own consent. Do not enter without it.",
        "- **Safety.** Remote travel plan, two vehicles or a satellite messenger, water and fuel margins, "
        "local advice on unexploded ordnance, mine workings and wildlife.",
        "",
        "## What to record on site",
        "- GPS track of the approach and the outline of the feature.",
        "- Photographs with a scale bar from the four compass points and from the centre; a drone orthophoto if permitted.",
        "- Surface description: disturbed or compacted soil, burn residue, vehicle tracks, spoil, debris, structures, vegetation state.",
        "- Soil samples from inside the footprint and matched control samples from at least 50 m outside it, bagged and labelled.",
        "- Magnetometer and background-radiation readings inside the footprint and at the control points.",
        "- Chain of custody: who collected each sample, when, how it was sealed, and every transfer after that.",
        "",
        "## What each ordinary cause would look like",
        "- **Vehicle or construction activity:** wheel or track marks, graded surfaces, spoil heaps, litter, survey pegs.",
        "- **Mining or prospecting:** pits, trenches, drill collars, crushed rock, camp remains.",
        "- **Fire:** charcoal, ash, scorched stems, heat-spalled rock, with regrowth matching the onset date.",
        "- **Water:** sediment crusts, mud cracks, strandlines, salt, channels leading in or out.",
        "- **Wind:** fresh sand sheets, ripples, deflation surfaces with no disturbance beneath.",
        "- **Aircraft or debris impact:** a crater or gouge with ejecta, fragments, fuel staining; report any wreckage to the aviation authority and do not disturb it.",
        "",
        "## Checks still open for this candidate",
        *([f"- {c.check}: {c.status}. {c.detail[:200]}" for c in open_checks] or ["- none"]),
        "",
        "If the site shows one of the ordinary causes above, record it and close the candidate as explained. "
        "The plan succeeds whichever way the answer falls.",
    ]
    return "\n".join(lines)


def write_followups(candidate: Candidate, out_dir: Path) -> list[Path]:
    """Write ``foia_<n>.md`` drafts and ``ground_truth_plan.md`` into ``out_dir``."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for index, draft in enumerate(draft_request(candidate), start=1):
        path = out_dir / f"foia_{index}.md"
        path.write_text(f"<!-- DRAFT: review before sending. Nothing has been sent. -->\n"
                        f"# {draft['subject']}\n\n{draft['body_markdown']}\n")
        written.append(path)
    plan = out_dir / "ground_truth_plan.md"
    plan.write_text(ground_truth_plan(candidate) + "\n")
    written.append(plan)
    return written
