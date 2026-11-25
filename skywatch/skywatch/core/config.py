"""Paths, network settings and GDAL environment for every SKYWATCH module.

Import this module before any rasterio read so remote reads are fast and
retry on transient proxy errors.
"""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"          # downloaded reference data (reports, catalogues)
CACHE = DATA / "cache"        # re-creatable caches (composites, API responses)
OUTPUT = ROOT / "output"      # results: candidates, dossiers, catalogue, proofs

#: Generic client name. Never put personal details in outbound requests.
USER_AGENT = "skywatch-research-pipeline/0.1"

EARTH_SEARCH = "https://earth-search.aws.element84.com/v1"
PLANETARY_COMPUTER = "https://planetarycomputer.microsoft.com/api/stac/v1"

#: Hosts this environment may reach. Anything else is refused by the proxy.
ALLOWED_HOSTS = (
    "earth-search.aws.element84.com",
    "sentinel-cogs.s3.us-west-2.amazonaws.com",
    "planetarycomputer.microsoft.com",
    "landsateuwest.blob.core.windows.net",
    "sentinel2l2a01.blob.core.windows.net",
    "sentinel1euwest.blob.core.windows.net",
    "astersa.blob.core.windows.net",
    "elevationeuwest.blob.core.windows.net",
    "modiseuwest.blob.core.windows.net",
    "api.openstreetmap.org",
    "esa-worldcover.s3.eu-central-1.amazonaws.com",
    "query.wikidata.org",
    "firms.modaps.eosdis.nasa.gov",
    "globalnightlight.s3.amazonaws.com",
    "services.arcgisonline.com",
    "wayback.maptiles.arcgis.com",
    "alice.btc.calendar.opentimestamps.org",
    "bob.btc.calendar.opentimestamps.org",
    "www.geipan.fr",
    "data.ntsb.gov",
    "raw.githubusercontent.com",
    # Allowed but unresponsive from this network when tested; best-effort only.
    "overpass-api.de",
    "overpass.kumi.systems",
    "overpass.private.coffee",
)

_GDAL_ENV = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "CPL_VSIL_CURL_ALLOWED_EXTENSIONS": ".tif,.tiff,.TIF,.TIFF,.hdf,.jp2",
    "GDAL_HTTP_MAX_RETRY": "5",
    "GDAL_HTTP_RETRY_DELAY": "2",
    "GDAL_HTTP_TIMEOUT": "60",
    "GDAL_HTTP_MERGE_CONSECUTIVE_RANGES": "YES",
    "VSI_CACHE": "TRUE",
    "VSI_CACHE_SIZE": "4000000",      # per open file: keep small, many files are open at once
    "GDAL_CACHEMAX": "192",
    "CPL_VSIL_CURL_USE_HEAD": "NO",
}


def setup_env() -> None:
    """Apply GDAL remote-read settings and create the data directories."""
    for key, value in _GDAL_ENV.items():
        os.environ.setdefault(key, value)
    for path in (DATA, CACHE, OUTPUT):
        path.mkdir(parents=True, exist_ok=True)


setup_env()
