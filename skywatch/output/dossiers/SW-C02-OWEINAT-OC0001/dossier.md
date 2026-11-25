# Dossier: candidate SW-C02-OWEINAT-OC0001

## What was detected
The detector `optical_change` flagged a structure or installation that the detector flagged (signature class `installation`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.905 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 22.54705 N, 28.72389 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 28.72053, 22.54374, 28.72725, 22.55031; centre 22.54703, 28.72389
- Area: 310,800 m2
- Search region: `C02-OWEINAT`

## When
The feature is absent in imagery up to 2023-01-18 and present from 2024-01-11. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2023
- step_snr: 22.62
- d_brightness: -0.3073
- d_ndvi: 0.7919
- d_nbr: 0.7226
- d_swir: -0.4702
- persistence_years: 3
- recovery_fraction: 0.09269
- crowding: 4.386e-05
- n_valid_years: 8
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
- composite_dates: {"2018": ["2019-01-14", "2019-01-17", "2019-01-19"], "2019": ["2020-01-07", "2020-01-19", "2020-01-22"], "2020": ["2021-01-08", "2021-01-11", "2021-01-21"], "2021": ["2022-01-16", "2022-01-18", "2022-01-21"], "2022": ["2023-01-11", "2023-01-13", "2023-01-18"], "2023": ["2024-01-11", "2024-01-16",...
- scene_ids_before: ["S2A_35QPE_20230113_0_L2A", "S2A_35QPF_20230113_0_L2A", "S2B_35QPF_20230111_0_L2A", "S2B_35QPE_20230111_0_L2A", "S2B_35QPF_20230118_0_L2A", "S2B_35QPE_20230118_0_L2A"]
- scene_ids_after: ["S2B_35QPF_20240116_0_L2A", "S2B_35QPE_20240116_0_L2A", "S2A_35QPF_20240111_0_L2A", "S2A_35QPE_20240111_0_L2A", "S2A_35QPF_20240118_0_L2A", "S2A_35QPE_20240118_0_L2A"]
- res_m: 20
- weak: False
- shape.area_m2: 310,800
- shape.perimeter_m: 2,030
- shape.equivalent_diameter_m: 629.1
- shape.major_axis_m: 632.4
- shape.minor_axis_m: 625.7
- shape.elongation: 1.011
- shape.orientation_deg: 56.8
- shape.circularity: 0.9478
- shape.solidity: 0.9725
- shape.eccentricity: 0.1459
- shape.rectangularity: 0.7848
- shape.n_corners: 8
- shape.straight_edge_fraction: 0.8035
- shape.hole_fraction: 0
- shape.regularity: 0.8736

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.3313 / 0.2748; ndvi 0.0932 / 0.2308; nbr -0.0333 / 0.0985
- after: brightness 0.1575 / 0.2789; ndvi 0.5598 / 0.2443; nbr 0.4037 / 0.1053

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Palmachim launch and test site (launch_site), 1189 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (98%); cropland 2%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). Footprint intersects mapped aeroway=aerodrome (way 776494607, مطار شرق العوينات الدولى); 3 explaining feature(s) within 300 m; nearest road or track 0 m. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
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
- The Esri picture in `hires.png` was taken on 2025-02-14 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
- `timeseries.png`: the detector recorded no time series (measurements['series'] is absent)

## Data provenance
- Sentinel-2 `before` composite, window 2022-01-18 to 2023-01-18: scenes S2A_35QPE_20220131_0_L2A, S2A_35QPF_20220131_0_L2A, S2B_35QPE_20220202_0_L2A, S2B_35QPF_20220202_0_L2A, S2A_35QPE_20220210_0_L2A, S2A_35QPF_20220210_0_L2A, S2A_35QPE_20220220_0_L2A, S2A_35QPF_20220220_0_L2A
- Sentinel-2 `after` composite, window 2024-01-11 to 2025-01-10: scenes S2A_35QPE_20240131_0_L2A, S2A_35QPF_20240131_0_L2A, S2A_35QPE_20240210_0_L2A, S2A_35QPF_20240210_0_L2A, S2B_35QPE_20240212_0_L2A, S2B_35QPF_20240212_0_L2A, S2B_35QPE_20240323_0_L2A, S2B_35QPF_20240323_0_L2A
- Sentinel-2 `context` composite, window 2024-01-11 to 2025-01-10: scenes S2A_35QPE_20240131_0_L2A, S2A_35QPF_20240131_0_L2A, S2A_35QPE_20240210_0_L2A, S2A_35QPF_20240210_0_L2A, S2B_35QPE_20240212_0_L2A, S2B_35QPF_20240212_0_L2A, S2B_35QPE_20240323_0_L2A, S2B_35QPF_20240323_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
