"""Assemble the publishable results page from the catalogue and the dossiers.

Writes ``output/site/``: ``index.html`` (the page with summary data inlined),
``catalogue.json`` (every reviewed candidate), ``land.json`` (coastlines) and
small JPEG copies of the dossier images for the least explained candidates.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from PIL import Image

from ..core import config
from .export import SITE, build_catalogue

PAGE = Path(__file__).with_name("page.html")
DOSSIERS = config.OUTPUT / "dossiers"
#: Dossier images copied to the page, in display order, with their captions.
PANELS = (("before.png", "Before (Sentinel-2, 10 m)"), ("after.png", "After (Sentinel-2, 10 m)"),
          ("current.png", "Current view (Sentinel-2, 10 m)"),
          ("hires.png", "High-resolution view (Esri World Imagery; mosaic date unknown)"),
          ("timeseries.png", "Scene-by-scene record inside the footprint versus its surroundings"),
          ("context.png", "Wider context"))

LIMITS = [
    ("It is a sample, not the planet",
     "The blind regions cover a tiny fraction of Earth's land. Nothing here says what exists outside them."),
    ("Small things are invisible",
     "Detection runs at 20 m per pixel on yearly composites. Anything under about 40 m across, or that came and went between two clear images, is missed. A one-year change in the newest imagery has unknown persistence."),
    ("Thermal data cannot see a vehicle-sized object",
     "Landsat thermal pixels are 100 m and all scenes are daytime, so thermal anomalies mostly trace rock, sand and moisture. Night-time and finer thermal data need logins this run did not have."),
    ("No ground-deformation measurement",
     "Millimetre deformation needs radar interferometry products that require a data-provider account. That check was not run, so underground excavation cannot be ruled in or out."),
    ("Absence from a map is weak evidence",
     "OpenStreetMap and Wikidata are thin in remote regions. 'Nothing mapped here' often means nobody has mapped it yet. Lightning records and most countries' aircraft-accident records were not available."),
    ("Regional patterns are set aside by rule",
     "When five or more unrelated places in one region changed the same way in the same year, the change is attributed to a regional process (rain, greening, blown sand, moisture or the sensor) and explained as such. Five similar things built in one region in one year would be set aside by the same rule unless their outlines are regular."),
    ("A tier is not an identification",
     "The highest tier means every available check failed to explain a dated change seen by two sensors. The most likely causes are still unmapped tracks, mining, military activity, water and wind. Ground truth is the only way to know."),
]


def _jpeg(src: Path, dst: Path, width: int) -> bool:
    try:
        with Image.open(src) as im:
            im = im.convert("RGB")
            if im.width > width:
                im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.save(dst, "JPEG", quality=78, optimize=True)
        return True
    except Exception:
        return False


def _land(site: Path) -> None:
    source = config.DATA / "reference" / "ne_110m_land.geojson"
    rings: list[list[list[float]]] = []
    if source.exists():
        for feature in json.loads(source.read_text())["features"]:
            geom = feature["geometry"]
            polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
            for poly in polys:
                ring = [[round(x, 1), round(y, 1)] for x, y in poly[0] if -60 <= y <= 84]
                if len(ring) > 3:
                    rings.append(ring)
    (site / "land.json").write_text(json.dumps(rings, separators=(",", ":")))


def build_site(site: Path = SITE, image_candidates: int = 60, headline: str = "",
               subline: str = "") -> dict[str, Any]:
    """Build the page and its files; return a manifest of what to publish."""
    catalogue = build_catalogue(site)
    files: dict[str, str] = {}
    with_images = 0
    for record in catalogue["candidates"]:
        folder = DOSSIERS / record["id"]
        if not folder.exists() or with_images >= image_candidates:
            continue
        images = []
        for name, caption in PANELS:
            if (folder / name).exists():
                rel = f"img/{record['id']}/{name.replace('.png', '.jpg')}"
                if _jpeg(folder / name, site / rel, 760):
                    images.append({"src": rel, "caption": caption})
                    files[rel] = str(site / rel)
        if (folder / "thumb.png").exists():
            rel = f"img/{record['id']}/thumb.jpg"
            if _jpeg(folder / "thumb.png", site / rel, 320):
                record["thumb"] = rel
                files[rel] = str(site / rel)
        if images:
            record["images"] = images
            with_images += 1
    (site / "catalogue.json").write_text(json.dumps(catalogue["candidates"], default=str,
                                                     separators=(",", ":")))
    _land(site)
    files["catalogue.json"] = str(site / "catalogue.json")
    files["land.json"] = str(site / "land.json")
    pristine = [r for r in catalogue["regions"] if r["kind"] == "control" and r.get("expectation")
                and (r.get("expected") or "").lower().startswith(("a featureless", "remote rock", "one of the emptiest"))]
    error_rates = {
        "pristine_regions": len(pristine),
        "pristine_area_km2": sum(r["area_km2"] for r in pristine),
        "pristine_detections": sum(r["blobs_detected"] or 0 for r in pristine),
        "pristine_unexplained": sum(sum(v for t, v in r["tiers"].items() if t != "T0") for r in pristine),
        "controls_passed": sum(1 for r in catalogue["regions"] if r["kind"] == "control"
                               and (r.get("expectation") or {}).get("passed")),
        "controls_total": sum(1 for r in catalogue["regions"] if r["kind"] == "control"),
    }
    data = {
        "generated": date.today().isoformat(), "headline": headline, "subline": subline,
        "error_rates": error_rates,
        "coverage": catalogue["coverage"], "summary": catalogue["summary"],
        "regions": catalogue["regions"], "limits": LIMITS,
        "total_blobs": sum(r["blobs_detected"] or 0 for r in catalogue["regions"])
        + sum(r.get("event_candidates") or 0 for r in catalogue["regions"]),
        "top": catalogue["candidates"][:8],
    }
    html = PAGE.read_text().replace("/*__DATA__*/null", json.dumps(data, default=str).replace("</", "<\\/"))
    (site / "index.html").write_text(html)
    return {"page": str(site / "index.html"), "files": files, "candidates": len(catalogue["candidates"]),
            "with_images": with_images}


if __name__ == "__main__":
    print(json.dumps({k: v for k, v in build_site().items() if k != "files"}, indent=1))
