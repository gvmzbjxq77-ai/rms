# Dossier: candidate SW-C04-DOMEFIRE-OC0009

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2556 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 35.30410 N, -115.56551 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -115.56701, 35.30326, -115.56374, 35.30492; centre 35.30409, -115.56538
- Area: 11,600 m2
- Search region: `C04-DOMEFIRE`

## When
The feature is absent in imagery up to 2020-10-07 and present from 2021-09-22. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2021
- step_snr: 6.391
- d_brightness: 0.05534
- d_ndvi: -0.04452
- d_nbr: 0.007078
- d_swir: 0.1128
- persistence_years: 6
- recovery_fraction: 0
- crowding: 0.002719
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-09-13", "2018-10-08", "2018-10-18"], "2019": ["2019-09-28", "2019-10-03", "2019-10-08"], "2020": ["2020-09-27", "2020-10-02", "2020-10-07"], "2021": ["2021-09-22", "2021-09-27", "2021-10-02"], "2022": ["2022-10-07", "2022-10-12", "2022-10-17"], "2023": ["2023-09-17", "2023-10-12",...
- scene_ids_before: ["S2A_11SPU_20201002_1_L2A", "S2A_11SPV_20201002_1_L2A", "S2B_11SPU_20200927_1_L2A", "S2B_11SPV_20200927_1_L2A", "S2B_11SPU_20201007_1_L2A", "S2B_11SPV_20201007_1_L2A"]
- scene_ids_after: ["S2B_11SPU_20210922_1_L2A", "S2B_11SPV_20210922_1_L2A", "S2A_11SPU_20210927_1_L2A", "S2A_11SPV_20210927_1_L2A", "S2B_11SPU_20211002_1_L2A", "S2B_11SPV_20211002_1_L2A"]
- res_m: 20
- weak: False
- regional_siblings: {"count": 13, "compared": 86, "year": 2021, "ids": ["SW-C04-DOMEFIRE-OC0006", "SW-C04-DOMEFIRE-OC0049", "SW-C04-DOMEFIRE-OC0048", "SW-C04-DOMEFIRE-OC0053", "SW-C04-DOMEFIRE-OC0054", "SW-C04-DOMEFIRE-OC0055", "SW-C04-DOMEFIRE-OC0050", "SW-C04-DOMEFIRE-OC0052"], "spread_km": 6.6, "min_cosine": 0.9,...
- shape.area_m2: 11,600
- shape.perimeter_m: 433.1
- shape.equivalent_diameter_m: 121.5
- shape.major_axis_m: 222.9
- shape.minor_axis_m: 84.9
- shape.elongation: 2.625
- shape.orientation_deg: 2.271
- shape.circularity: 0.777
- shape.solidity: 0.7073
- shape.eccentricity: 0.9246
- shape.rectangularity: 0.5273
- shape.n_corners: 6
- shape.straight_edge_fraction: 0.8012
- shape.hole_fraction: 0
- shape.regularity: 0.427

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1293 / 0.1379; ndvi 0.1595 / 0.1532; nbr -0.1757 / -0.1363
- after: brightness 0.1688 / 0.167; ndvi 0.1189 / 0.139; nbr -0.1595 / -0.0899

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Fort Irwin National Training Center (test_range), 74 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly grass (40%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map postdates the onset, so it may show the change itself. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). Footprint is 197 m from mapped historic=mine (node 369165380, Teutonia Mine); 2 explaining feature(s) within 297 m; nearest road or track 790 m. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
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
- `before.png`: Sentinel-2 true colour, BEFORE onset
- `falsecolor_before.png`: Sentinel-2 false colour (SWIR1, NIR, red), BEFORE onset
- `after.png`: Sentinel-2 true colour, AFTER onset
- `falsecolor_after.png`: Sentinel-2 false colour (SWIR1, NIR, red), AFTER onset
- `difference.png`: After minus before: brightness and NDVI change
- `context.png`: Wider setting with the footprint marked
- `hires.png`: Esri World Imagery view (viewing only)
- `wayback_strip.png`: Esri Wayback versions; dates are publication dates, not acquisition dates
- The Esri picture in `hires.png` was taken on 2024-02-28 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
- `timeseries.png`: the detector recorded no time series (measurements['series'] is absent)

## Data provenance
- Sentinel-2 `before` composite, window 2019-10-08 to 2020-10-07: scenes S2A_11SPV_20200415_1_L2A, S2B_11SPV_20200609_1_L2A, S2A_11SPV_20200902_1_L2A, S2B_11SPV_20201007_1_L2A
- Sentinel-2 `after` composite, window 2021-09-22 to 2022-09-22: scenes S2B_11SPV_20210922_1_L2A, S2B_11SPV_20211002_1_L2A, S2A_11SPV_20211027_1_L2A, S2B_11SPV_20220907_0_L2A
- Sentinel-2 `context` composite, window 2021-09-22 to 2022-09-22: scenes S2B_11SPV_20210922_1_L2A, S2B_11SPV_20211002_1_L2A, S2A_11SPV_20211027_1_L2A, S2B_11SPV_20220907_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
