# Dossier: candidate SW-C01-BENBAN-OC0001

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.6 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 24.41899 N, 32.69609 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 32.69540, 24.41836, 32.69678, 24.41962; centre 24.41899, 32.69609
- Area: 3,600 m2
- Search region: `C01-BENBAN`

## When
The feature is absent in imagery up to 2019-07-20 and present from 2020-07-09. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2020
- step_snr: 15
- d_brightness: -0.09919
- d_ndvi: -0.001138
- d_nbr: -0.01708
- d_swir: -0.1414
- persistence_years: 7
- recovery_fraction: 0
- crowding: 0.003947
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-10", "2018-07-15", "2018-07-20"], "2019": ["2019-07-10", "2019-07-15", "2019-07-20"], "2020": ["2020-07-09", "2020-07-14", "2020-07-19"], "2021": ["2021-07-09", "2021-07-14", "2021-07-24"], "2022": ["2022-07-04", "2022-07-14", "2022-07-19"], "2023": ["2023-07-04", "2023-07-19",...
- scene_ids_before: ["S2A_36QVM_20190710_1_L2A", "S2A_36RVN_20190710_1_L2A", "S2B_36QVM_20190715_1_L2A", "S2B_36RVN_20190715_1_L2A", "S2A_36QVM_20190720_1_L2A", "S2A_36RVN_20190720_1_L2A"]
- scene_ids_after: ["S2A_36RVN_20200714_1_L2A", "S2A_36QVM_20200714_1_L2A", "S2B_36RVN_20200719_1_L2A", "S2B_36QVM_20200719_1_L2A", "S2B_36RVN_20200709_1_L2A", "S2B_36QVM_20200709_1_L2A"]
- res_m: 20
- series: time series with 31 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_shift: -0.004849
- series_noise: 0.03228
- onset_note: per-scene contrast does not separate before from after
- shape.area_m2: 3,600
- shape.perimeter_m: 160
- shape.equivalent_diameter_m: 67.7
- shape.major_axis_m: 65.32
- shape.minor_axis_m: 65.32
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
- before: brightness 0.2498 / 0.2597; ndvi 0.082 / 0.0827; nbr -0.0545 / -0.0564
- after: brightness 0.1884 / 0.1902; ndvi 0.0809 / 0.0802; nbr -0.0666 / -0.0738

## Conventional explanations tested
No check result is recorded for this candidate. Nothing has been ruled out.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **osm_infrastructure** (mandatory): never attempted: no result is recorded for this check
- **landcover** (mandatory): never attempted: no result is recorded for this check
- **wikidata_nearby** (mandatory): never attempted: no result is recorded for this check
- **fire_history** (mandatory): never attempted: no result is recorded for this check
- **artefact_screen** (mandatory): never attempted: no result is recorded for this check
- **natural_process** (mandatory): never attempted: no result is recorded for this check

## Evidence tier
**T1**: seen in one sensor only.

Reason: seen in one sensor only (optical_s2) (computed from the recorded evidence when the dossier was built).

The tier ladder measures how much of the evidence is in place. Its top means "unexplained after every check", never "identified".

## Figures
- `before.png`: Sentinel-2 true colour, BEFORE onset
- `falsecolor_before.png`: Sentinel-2 false colour (SWIR1, NIR, red), BEFORE onset
- `after.png`: Sentinel-2 true colour, AFTER onset
- `falsecolor_after.png`: Sentinel-2 false colour (SWIR1, NIR, red), AFTER onset
- `difference.png`: After minus before: brightness and NDVI change
- `context.png`: Wider setting with the footprint marked
- `timeseries.png`: Brightness, NDVI and NBR inside the footprint versus the ring
- `hires.png`: Esri World Imagery view (viewing only)
- `wayback_strip.png`: Esri Wayback versions; dates are publication dates, not acquisition dates
- The Esri picture in `hires.png` was taken on 2025-02-19 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2018-07-20 to 2019-07-20: scenes S2B_36QVM_20180829_1_L2A, S2B_36RVN_20180829_1_L2A, S2A_36QVM_20181003_1_L2A, S2A_36RVN_20181003_1_L2A, S2A_36QVM_20190401_1_L2A, S2A_36RVN_20190401_1_L2A, S2A_36QVM_20190501_1_L2A, S2A_36RVN_20190501_1_L2A
- Sentinel-2 `after` composite, window 2020-07-09 to 2021-07-09: scenes S2A_36QVM_20200902_1_L2A, S2A_36RVN_20200902_1_L2A, S2B_36QVM_20200927_1_L2A, S2B_36RVN_20200927_1_L2A, S2A_36QVM_20201022_1_L2A, S2A_36RVN_20201022_1_L2A, S2A_36QVM_20201111_1_L2A, S2A_36RVN_20201111_1_L2A
- Sentinel-2 `context` composite, window 2020-07-09 to 2021-07-09: scenes S2A_36QVM_20200902_1_L2A, S2A_36RVN_20200902_1_L2A, S2B_36QVM_20200927_1_L2A, S2B_36RVN_20200927_1_L2A, S2A_36QVM_20201022_1_L2A, S2A_36RVN_20201022_1_L2A, S2A_36QVM_20201111_1_L2A, S2A_36RVN_20201111_1_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
