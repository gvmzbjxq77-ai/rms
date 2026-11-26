# Dossier: candidate SW-C06-MU5735-EV0049

## What was detected
The detector `optical_event` flagged a surface anomaly of unclassified kind (signature class `unknown`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2843 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 23.32416 N, 111.11406 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 111.11249, 23.32299, 111.11571, 23.32525; centre 23.32412, 111.11410
- Area: 29,600 m2
- Search region: `C06-MU5735`

## When
The feature is absent in imagery up to 2021-12-13 and present from 2022-04-07. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: event_window
- event_date: 2022-03-21
- break_year: 2022
- step_snr: 7.108
- d_brightness: 0.05895
- d_ndvi: -0.7063
- d_nbr: -0.7627
- d_swir: 0.09235
- seasonal_baseline: True
- crowding: 0.01984
- composite_dates: {"before": ["2021-10-24", "2021-11-13", "2021-12-03", "2021-12-13"], "after": ["2022-04-07", "2022-04-12", "2022-07-26"]}
- scene_ids_before: ["S2A_49QDF_20211024_1_L2A", "S2A_49QEF_20211024_1_L2A", "S2A_49QDF_20211113_1_L2A", "S2A_49QEF_20211113_1_L2A", "S2A_49QDF_20211203_1_L2A", "S2A_49QEF_20211203_1_L2A", "S2A_49QDF_20211213_1_L2A", "S2A_49QEF_20211213_1_L2A"]
- scene_ids_after: ["S2B_49QDF_20220407_0_L2A", "S2B_49QEF_20220407_0_L2A", "S2A_49QEF_20220412_0_L2A", "S2B_49QDF_20220726_0_L2A", "S2B_49QEF_20220726_0_L2A"]
- res_m: 10
- weak: False
- shape.area_m2: 29,600
- shape.perimeter_m: 887.7
- shape.equivalent_diameter_m: 194.1
- shape.major_axis_m: 314.1
- shape.minor_axis_m: 134.1
- shape.elongation: 2.342
- shape.orientation_deg: 150.3
- shape.circularity: 0.472
- shape.solidity: 0.7914
- shape.eccentricity: 0.9042
- shape.rectangularity: 0.572
- shape.n_corners: 13
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 0.1763

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.0407 / 0.0426; ndvi 0.7888 / 0.7493; nbr 0.6152 / 0.5675
- after: brightness 0.0516 / 0.048; ndvi 0.6767 / 0.7101; nbr 0.4913 / 0.5556

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Xichang downrange drop zone, south-west Hunan (drop_zone), 344 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly tree (100%); cropland 0%, built-up 0%, water/wetland 0%; onset is undated or straddles 2021, so the map may show either state. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). Footprint intersects mapped historic=ruins (way 1042838116, MU5735坠毁地); 14 explaining feature(s) within 300 m; nearest road or track 6 m. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
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
- Sentinel-2 `before` composite, window 2020-12-13 to 2021-12-13: scenes S2B_49QEF_20210102_1_L2A, S2A_49QEF_20211113_1_L2A, S2A_49QEF_20211203_1_L2A, S2B_49QEF_20211208_1_L2A
- Sentinel-2 `after` composite, window 2022-04-07 to 2023-04-07: scenes S2B_49QEF_20221014_0_L2A, S2A_49QEF_20221228_0_L2A, S2A_49QEF_20230107_0_L2A, S2B_49QEF_20230221_0_L2A
- Sentinel-2 `context` composite, window 2022-04-07 to 2023-04-07: scenes S2B_49QDF_20220407_0_L2A, S2B_49QEF_20220407_0_L2A, S2B_49QDF_20221014_0_L2A, S2B_49QEF_20221014_0_L2A, S2A_49QDF_20221228_0_L2A, S2A_49QEF_20221228_0_L2A, S2A_49QDF_20230107_0_L2A, S2A_49QEF_20230107_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
