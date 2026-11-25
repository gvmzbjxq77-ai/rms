# Dossier: candidate SW-C08-ERTAALE-TH0001

## What was detected
The detector `landsat_thermal` flagged a persistent thermal anomaly (signature class `thermal`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.7098 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 13.60397 N, 40.66314 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 40.66002, 13.60140, 40.66580, 13.60632; centre 13.60386, 40.66291
- Area: 89,100 m2
- Search region: `C08-ERTAALE`

## When
No dated onset: the pipeline has no pair of dates bracketing the appearance (absent_until = None, present_from = None). Only a current view is shown.

## Measurements
- Sensor families in which the feature is seen: thermal_landsat
- median_anomaly_K: 7.793
- median_z: 8.517
- hit_fraction: 0.7692
- n_scenes: 14
- sign: 1
- dates: ["2019-01-16", "2020-01-19", "2021-03-26", "2021-12-23", "2022-06-17", "2023-01-03", "2023-06-28", "2023-12-29", "2024-06-30", "2025-01-16", "2025-06-17", "2025-12-26", "2026-06-12", "2026-11-03"]
- years: ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
- res_m: 90
- elevation_detrended: True
- surface_detrended: True

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- current: brightness 0.1448 / 0.1055; ndvi -0.0095 / 0.0073; nbr 0.019 / -0.0237

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Palmachim launch and test site (launch_site), 2117 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (98%); cropland 0%, built-up 0%, water/wetland 2%; onset is undated or straddles 2021, so the map may show either state. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). Footprint intersects mapped natural=volcano (node 319176124, Erta Ale); 4 explaining feature(s) within 300 m; nearest road or track 714 m. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): NOT RUN. skipped: already explained by osm_infrastructure Source: engine.
- **aviation_accident** (event): NOT RUN. skipped: already explained by osm_infrastructure Source: engine.
- **meteorite_record** (event): NOT RUN. skipped: already explained by osm_infrastructure Source: engine.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **wikidata_nearby** (mandatory): skipped: already explained by osm_infrastructure
- **aviation_accident**: skipped: already explained by osm_infrastructure
- **meteorite_record**: skipped: already explained by osm_infrastructure
- **fire_history** (mandatory): never attempted: no result is recorded for this check
- **artefact_screen** (mandatory): never attempted: no result is recorded for this check
- **natural_process** (mandatory): never attempted: no result is recorded for this check

## Evidence tier
**T0**: explained by a conventional cause.

Reason: explained by: osm_infrastructure (recorded on the candidate).

The tier ladder measures how much of the evidence is in place. Its top means "unexplained after every check", never "identified".

## Figures
- `current.png`: Sentinel-2 true colour, CURRENT (no dated onset)
- `falsecolor_current.png`: Sentinel-2 false colour (SWIR1, NIR, red), CURRENT (no dated onset)
- `context.png`: Wider setting with the footprint marked
- `hires.png`: Esri World Imagery view (viewing only)
- `wayback_strip.png`: Esri Wayback versions; dates are publication dates, not acquisition dates
- The Esri picture in `hires.png` was taken on 2025-04-01 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
- `difference.png`: no dated onset window, so there is no before/after pair
- `timeseries.png`: the detector recorded no time series (measurements['series'] is absent)

## Data provenance
- Sentinel-2 `current` composite, window 2025-11-25 to 2026-11-25: scenes S2A_37PFR_20251125_0_L2A, S2C_37PFR_20251203_0_L2A, S2A_37PFR_20251225_0_L2A, S2C_37PFR_20260112_0_L2A
- Sentinel-2 `context` composite, window 2025-11-25 to 2026-11-25: scenes S2A_37PFQ_20251125_0_L2A, S2A_37PFR_20251125_0_L2A, S2C_37PFQ_20251203_0_L2A, S2C_37PFR_20251203_0_L2A, S2C_37PFQ_20260112_0_L2A, S2C_37PFR_20260112_0_L2A, S2C_37PFQ_20260211_0_L2A, S2C_37PFR_20260211_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
