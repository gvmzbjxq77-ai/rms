# Dossier: candidate SW-C06-MU5735-OC0004

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.4423 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 23.32247 N, 111.08705 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 111.08647, 23.32192, 111.08764, 23.32301; centre 23.32247, 111.08705
- Area: 1,600 m2
- Search region: `C06-MU5735`

## When
The feature is absent in imagery up to 2023-11-28 and present from 2024-11-07. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2024
- step_snr: 11.06
- d_brightness: 0.07433
- d_ndvi: -0.522
- d_nbr: -0.4782
- d_swir: 0.119
- persistence_years: 3
- recovery_fraction: 0.2183
- crowding: 0.002588
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-10-05", "2018-10-30", "2018-11-29"], "2019": ["2019-11-04", "2019-11-09", "2019-11-14"], "2020": ["2020-11-08", "2020-11-13", "2020-12-08"], "2021": ["2021-10-24", "2021-11-13", "2021-12-03"], "2022": ["2022-10-14", "2022-10-24", "2022-11-13"], "2023": ["2023-11-18", "2023-11-23",...
- scene_ids_before: ["S2B_49QDF_20231118_0_L2A", "S2B_49QEF_20231118_0_L2A", "S2B_49QDF_20231128_0_L2A", "S2B_49QEF_20231128_0_L2A", "S2A_49QEF_20231123_0_L2A"]
- scene_ids_after: ["S2A_49QDF_20241107_0_L2A", "S2A_49QEF_20241107_0_L2A", "S2B_49QDF_20241112_0_L2A", "S2B_49QEF_20241112_0_L2A", "S2B_49QEF_20241202_0_L2A", "S2B_49QDF_20241202_0_L2A"]
- res_m: 20
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
- before: brightness 0.0421 / 0.0484; ndvi 0.6977 / 0.6744; nbr 0.5142 / 0.4973
- after: brightness 0.0735 / 0.0654; ndvi 0.4832 / 0.6038; nbr 0.3134 / 0.4639

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Xichang downrange drop zone, south-west Hunan (drop_zone), 344 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly tree (96%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). Footprint is 8 m from mapped landuse=farmland (way 1042216506); 2 explaining feature(s) within 120 m; nearest road or track 4 m. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
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
- The Esri picture in `hires.png` was taken on 2022-04-03 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
- `timeseries.png`: the detector recorded no time series (measurements['series'] is absent)

## Data provenance
- Sentinel-2 `before` composite, window 2022-11-28 to 2023-11-28: scenes S2A_49QDF_20221228_0_L2A, S2A_49QEF_20221228_0_L2A, S2A_49QDF_20230107_0_L2A, S2A_49QEF_20230107_0_L2A, S2B_49QDF_20231118_0_L2A, S2B_49QEF_20231118_0_L2A, S2B_49QDF_20231128_0_L2A, S2B_49QEF_20231128_0_L2A
- Sentinel-2 `after` composite, window 2024-11-07 to 2025-11-07: scenes S2B_49QDF_20250101_0_L2A, S2B_49QEF_20250101_0_L2A, S2A_49QDF_20250116_0_L2A, S2A_49QEF_20250116_0_L2A, S2B_49QDF_20250121_0_L2A, S2B_49QEF_20250121_0_L2A, S2B_49QDF_20250322_0_L2A, S2B_49QEF_20250322_0_L2A
- Sentinel-2 `context` composite, window 2024-11-07 to 2025-11-07: scenes S2B_49QDF_20250101_0_L2A, S2B_49QEF_20250101_0_L2A, S2A_49QDF_20250116_0_L2A, S2A_49QEF_20250116_0_L2A, S2B_49QDF_20250121_0_L2A, S2B_49QEF_20250121_0_L2A, S2B_49QDF_20250322_0_L2A, S2B_49QEF_20250322_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
