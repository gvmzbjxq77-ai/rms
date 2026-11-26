# Dossier: candidate SW-C03-OYUTOLGOI-OC0015

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.3452 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 43.01284 N, 106.84950 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 106.84878, 43.01228, 106.85022, 43.01339; centre 43.01284, 106.84950
- Area: 1,600 m2
- Search region: `C03-OYUTOLGOI`

## When
The feature is absent in imagery up to 2024-08-26 and present from 2025-08-01. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2025
- step_snr: 8.629
- d_brightness: -0.02658
- d_ndvi: -0.03225
- d_nbr: 0.105
- d_swir: -0.1629
- persistence_years: 2
- recovery_fraction: 0
- crowding: 0.002566
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-08-08", "2018-08-13", "2018-08-18"], "2019": ["2019-07-24", "2019-08-03", "2019-08-28"], "2020": ["2020-07-18", "2020-07-28", "2020-09-06"], "2021": ["2021-07-18", "2021-07-28", "2021-08-22"], "2022": ["2022-08-12", "2022-08-22", "2022-09-01"], "2023": ["2023-08-07", "2023-08-12",...
- scene_ids_before: ["S2A_48TXN_20240811_0_L2A", "S2A_48TXN_20240722_0_L2A", "S2B_48TXN_20240826_0_L2A"]
- scene_ids_after: ["S2A_48TXN_20250808_2_L2A", "S2B_48TXN_20250811_0_L2A", "S2B_48TXN_20250801_0_L2A"]
- res_m: 20
- weak: False
- regional_siblings: {"count": 5, "compared": 119, "year": 2025, "ids": ["SW-C03-OYUTOLGOI-OC0044", "SW-C03-OYUTOLGOI-OC0055", "SW-C03-OYUTOLGOI-OC0035", "SW-C03-OYUTOLGOI-OC0067", "SW-C03-OYUTOLGOI-OC0070"], "spread_km": 3.7, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 1,600
- shape.perimeter_m: 80
- shape.equivalent_diameter_m: 45.14
- shape.major_axis_m: 40
- shape.minor_axis_m: 40
- shape.elongation: 1
- shape.orientation_deg: 45
- shape.circularity: 1
- shape.solidity: 1
- shape.eccentricity: 0
- shape.rectangularity: 1
- shape.n_corners: 4
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 1

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.2886 / 0.2051; ndvi 0.005 / 0.0075; nbr 0.0158 / -0.0108
- after: brightness 0.1945 / 0.1989; ndvi 0.0024 / 0.013; nbr 0.0682 / 0.0096

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Jiuquan downrange drop zone, Alxa desert (drop_zone), 319 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). Footprint intersects mapped landuse=industrial (way 206629216, Оюутолгой); 2 explaining feature(s) within 123 m; nearest road or track 100 m. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
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
- The Esri picture in `hires.png` was taken on 2025-10-25 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
- `timeseries.png`: the detector recorded no time series (measurements['series'] is absent)

## Data provenance
- Sentinel-2 `before` composite, window 2023-08-27 to 2024-08-26: scenes S2A_48TXN_20230926_0_L2A, S2B_48TXN_20231021_0_L2A, S2A_48TXN_20240722_0_L2A, S2B_48TXN_20240826_0_L2A
- Sentinel-2 `after` composite, window 2025-08-01 to 2026-08-01: scenes S2B_48TXN_20250821_0_L2A, S2A_48TXN_20250917_1_L2A, S2A_48TXN_20251027_0_L2A, S2C_48TXN_20260622_0_L2A
- Sentinel-2 `context` composite, window 2025-08-01 to 2026-08-01: scenes S2B_48TXN_20250821_0_L2A, S2A_48TXN_20250917_1_L2A, S2A_48TXN_20251027_0_L2A, S2C_48TXN_20260622_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
