# Dossier: candidate SW-C01-BENBAN-OC0002

## What was detected
The detector `optical_change` flagged a structure or installation that the detector flagged (signature class `installation`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.4798 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 24.44244 N, 32.74102 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 32.74013, 24.44157, 32.74191, 24.44337; centre 24.44247, 32.74102
- Area: 11,200 m2
- Search region: `C01-BENBAN`

## When
The feature is absent in imagery up to 2021-07-24 and present from 2022-07-04. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2022
- step_snr: 12
- d_brightness: 0.04447
- d_ndvi: -0.06795
- d_nbr: 0.05335
- d_swir: -0.1513
- persistence_years: 5
- recovery_fraction: 0.01694
- crowding: 0.000921
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-10", "2018-07-15", "2018-07-20"], "2019": ["2019-07-10", "2019-07-15", "2019-07-20"], "2020": ["2020-07-09", "2020-07-14", "2020-07-19"], "2021": ["2021-07-09", "2021-07-14", "2021-07-24"], "2022": ["2022-07-04", "2022-07-14", "2022-07-19"], "2023": ["2023-07-04", "2023-07-19",...
- scene_ids_before: ["S2A_36QVM_20210709_1_L2A", "S2A_36RVN_20210709_1_L2A", "S2B_36QVM_20210714_1_L2A", "S2B_36RVN_20210714_1_L2A", "S2B_36QVM_20210724_1_L2A", "S2B_36RVN_20210724_1_L2A"]
- scene_ids_after: ["S2A_36QVM_20220714_0_L2A", "S2A_36RVN_20220714_0_L2A", "S2B_36RVN_20220719_0_L2A", "S2B_36QVM_20220719_0_L2A", "S2A_36RVN_20220704_0_L2A", "S2A_36QVM_20220704_0_L2A"]
- res_m: 20
- weak: False
- shape.area_m2: 11,200
- shape.perimeter_m: 336.6
- shape.equivalent_diameter_m: 119.4
- shape.major_axis_m: 130.1
- shape.minor_axis_m: 109
- shape.elongation: 1.194
- shape.orientation_deg: 90
- shape.circularity: 1
- shape.solidity: 1
- shape.eccentricity: 0.5462
- shape.rectangularity: 0.9333
- shape.n_corners: 5
- shape.straight_edge_fraction: 0.6877
- shape.hole_fraction: 0
- shape.regularity: 1

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.294 / 0.265; ndvi 0.0846 / 0.0857; nbr -0.0583 / -0.0748
- after: brightness 0.3069 / 0.2689; ndvi 0.0607 / 0.0765; nbr -0.0713 / -0.0985

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Palmachim launch and test site (launch_site), 845 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (99%); cropland 0%, built-up 1%, water/wetland 0%; onset is undated or straddles 2021, so the map may show either state. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). Footprint intersects mapped power=plant (way 694477324, محطة بنبان للطاقة الشمسية); 11 explaining feature(s) within 200 m; nearest road or track 0 m. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
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
- The Esri picture in `hires.png` was taken on 2025-02-19 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
- `timeseries.png`: the detector recorded no time series (measurements['series'] is absent)

## Data provenance
- Sentinel-2 `before` composite, window 2020-07-24 to 2021-07-24: scenes S2B_36RVN_20200828_1_L2A, S2A_36RVN_20201022_1_L2A, S2A_36RVN_20210520_2_L2A, S2A_36RVN_20210609_1_L2A
- Sentinel-2 `after` composite, window 2022-07-04 to 2023-07-04: scenes S2B_36RVN_20220808_0_L2A, S2B_36RVN_20220907_0_L2A, S2B_36RVN_20230425_0_L2A, S2A_36RVN_20230520_0_L2A
- Sentinel-2 `context` composite, window 2022-07-04 to 2023-07-04: scenes S2B_36RVN_20220808_0_L2A, S2B_36QVM_20220907_0_L2A, S2B_36RVN_20220907_0_L2A, S2A_36QVM_20221002_0_L2A, S2A_36RVN_20221002_0_L2A, S2B_36QVM_20221027_0_L2A, S2B_36RVN_20221027_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
