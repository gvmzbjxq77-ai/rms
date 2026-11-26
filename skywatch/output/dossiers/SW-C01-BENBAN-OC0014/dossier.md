# Dossier: candidate SW-C01-BENBAN-OC0014

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.3491 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 24.41179 N, 32.76052 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 32.75973, 24.41125, 32.76131, 24.41233; centre 24.41179, 32.76052
- Area: 3,200 m2
- Search region: `C01-BENBAN`

## When
The feature is absent in imagery up to 2023-10-02 and present from 2023-11-11. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: step
- break_year: 2024
- step_snr: 8.727
- d_brightness: -0.06052
- d_ndvi: 0.05338
- d_nbr: 0.04989
- d_swir: -0.08687
- persistence_years: 3
- recovery_fraction: 0
- crowding: 0.003421
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-10", "2018-07-15", "2018-07-20"], "2019": ["2019-07-10", "2019-07-15", "2019-07-20"], "2020": ["2020-07-09", "2020-07-14", "2020-07-19"], "2021": ["2021-07-09", "2021-07-14", "2021-07-24"], "2022": ["2022-07-04", "2022-07-14", "2022-07-19"], "2023": ["2023-07-04", "2023-07-19",...
- scene_ids_before: ["S2A_36RVN_20230719_0_L2A", "S2A_36QVM_20230719_0_L2A", "S2B_36RVN_20230724_0_L2A", "S2B_36QVM_20230724_0_L2A", "S2B_36RVN_20230704_0_L2A", "S2B_36QVM_20230704_0_L2A"]
- scene_ids_after: ["S2B_36RVN_20240718_0_L2A", "S2B_36QVM_20240718_0_L2A", "S2A_36RVN_20240713_0_L2A", "S2A_36QVM_20240713_0_L2A", "S2B_36RVN_20240728_0_L2A", "S2B_36QVM_20240728_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 30 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_mode: contrast
- series_shift: -0.05295
- series_noise: 0.00909
- onset_window_days: 40
- onset_flips: 1
- landsat: {"status": "ok", "before": [{"date": "2022-08-30", "scene_id": "LC08_L2SP_174043_20220830_02_T1", "brightness": -0.0005384385585784912, "ndvi": 0.002219080924987793, "nbr": 0.010214097797870636, "kelvin": 0.199371337890625}, {"date": "2023-01-21", "scene_id": "LC08_L2SP_174043_20230121_02_T1", "b...
- sar: {"status": "not_run", "reason": "footprint radius 32 m is under two radar pixels"}
- regional_siblings: {"count": 3, "compared": 119, "year": 2024, "ids": ["SW-C01-BENBAN-OC0054", "SW-C01-BENBAN-OC0056", "SW-C01-BENBAN-OC0070"], "spread_km": 10.8, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 3,200
- shape.perimeter_m: 160
- shape.equivalent_diameter_m: 63.83
- shape.major_axis_m: 89.44
- shape.minor_axis_m: 40
- shape.elongation: 2.236
- shape.orientation_deg: 0
- shape.circularity: 1
- shape.solidity: 1
- shape.eccentricity: 0.8944
- shape.rectangularity: 1
- shape.n_corners: 4
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 1

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.268 / 0.2656; ndvi 0.0884 / 0.0838; nbr -0.065 / -0.0705
- after: brightness 0.2267 / 0.2618; ndvi 0.1059 / 0.0826; nbr -0.066 / -0.0679

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Palmachim launch and test site (launch_site), 848 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 160 m of the footprint (2552 tagged features in the extract; nearest road or track 196 m; nearest candidate cause railway=construction at 487 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (1 item(s) within 10.0 km; nearest: Benban Solar Park (Q48989519, power_or_industry) at 5.38 km) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2023-09-02 to 2023-12-11; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2023-11-11 (nearest record: Aswan (Found, 1955) at 49.3 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 196 m away; 3.2% of the land within 1.5 km is built-up Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran but was INCONCLUSIVE. persistent artificial light at the site (human activity): Persistent artificial light IS present within 1500 m of the candidate: peak radiance 24.92 against background 0.595 nW/cm2/sr, lit in 12 of 12 monthly composites (202407 to 202506, 174 cloud-free nights). This indicates ongoing human activity or combustion at or near the site; it does not say what the feature is. Before the onset (202304 to 202309) persistent light was already present (radiance 34.985, background 0.65 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying); possible regional pattern: 3 of 119 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 10.8 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (1 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 12 of 12 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 12 of 12 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.3% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2022-08-28 and 2023-11-26 within 100 m of the candidate, but the record is incomplete (burned area: 15/16 monthly files read for 6 pixels; no file for 2023-09; active fire: 110 eight-day files read (0 incomplete); 432/456 days covered, clear view on 430), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.050); NDVI rose (+0.053). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran but was INCONCLUSIVE. possible regional pattern: 3 of 119 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 10.8 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.05) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2023-11-11 (nearest record: Aswan (Found, 1955) at 49.3 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: fire_history, human_context, natural:regional_pattern, natural:surface_water, natural_process, night_lights (recorded on the candidate).

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
- Sentinel-2 `before` composite, window 2022-10-02 to 2023-10-02: scenes S2A_36QVM_20221002_0_L2A, S2A_36RVN_20221002_0_L2A, S2B_36QVM_20221027_0_L2A, S2B_36RVN_20221027_0_L2A, S2B_36QVM_20221106_0_L2A, S2B_36RVN_20221106_0_L2A, S2B_36RVN_20231002_0_L2A
- Sentinel-2 `after` composite, window 2023-11-11 to 2024-11-10: scenes S2A_36QVM_20240414_0_L2A, S2A_36RVN_20240414_0_L2A, S2B_36QVM_20241016_0_L2A, S2B_36RVN_20241016_0_L2A, S2C_36QVM_20241031_1_L2A, S2A_36RVN_20241031_0_L2A, S2B_36QVM_20241105_0_L2A, S2B_36RVN_20241105_0_L2A
- Sentinel-2 `context` composite, window 2023-11-11 to 2024-11-10: scenes S2A_36QVM_20240414_0_L2A, S2A_36RVN_20240414_0_L2A, S2B_36QVM_20241016_0_L2A, S2B_36RVN_20241016_0_L2A, S2C_36QVM_20241031_1_L2A, S2A_36RVN_20241031_0_L2A, S2B_36QVM_20241105_0_L2A, S2B_36RVN_20241105_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
