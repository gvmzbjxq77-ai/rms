# Dossier: candidate SW-C01-BENBAN-OC0009

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.392 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 24.49646 N, 32.74936 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 32.74871, 24.49577, 32.75009, 24.49721; centre 24.49649, 32.74940
- Area: 4,000 m2
- Search region: `C01-BENBAN`

## When
The feature is absent in imagery up to 2024-10-16 and present from 2024-11-25. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: step
- break_year: 2025
- step_snr: 9.801
- d_brightness: -0.08008
- d_ndvi: 0.03835
- d_nbr: -0.01834
- d_swir: -0.02654
- persistence_years: 2
- recovery_fraction: 0.02502
- crowding: 0.001842
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-10", "2018-07-15", "2018-07-20"], "2019": ["2019-07-10", "2019-07-15", "2019-07-20"], "2020": ["2020-07-09", "2020-07-14", "2020-07-19"], "2021": ["2021-07-09", "2021-07-14", "2021-07-24"], "2022": ["2022-07-04", "2022-07-14", "2022-07-19"], "2023": ["2023-07-04", "2023-07-19",...
- scene_ids_before: ["S2B_36RVN_20240718_0_L2A", "S2B_36QVM_20240718_0_L2A", "S2A_36RVN_20240713_0_L2A", "S2A_36QVM_20240713_0_L2A", "S2B_36RVN_20240728_0_L2A", "S2B_36QVM_20240728_0_L2A"]
- scene_ids_after: ["S2C_36RVN_20250718_0_L2A", "S2C_36QVM_20250718_0_L2A", "S2B_36QVM_20250723_0_L2A", "S2B_36RVN_20250723_0_L2A", "S2A_36RVN_20250710_0_L2A", "S2A_36QVM_20250710_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 32 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_mode: contrast
- series_shift: -0.05983
- series_noise: 0.01035
- onset_window_days: 40
- onset_flips: 1
- landsat: {"status": "ok", "before": [{"date": "2023-09-17", "scene_id": "LC09_L2SP_175043_20230917_02_T1", "brightness": 0.00835070013999939, "ndvi": -0.003898926079273224, "nbr": -0.0007207579910755157, "kelvin": -0.164581298828125}, {"date": "2024-01-31", "scene_id": "LC08_L2SP_175043_20240131_02_T1", "...
- sar: {"status": "not_run", "reason": "footprint radius 36 m is under two radar pixels"}
- regional_siblings: {"count": 0, "compared": 119, "year": 2025, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 4,000
- shape.perimeter_m: 164.1
- shape.equivalent_diameter_m: 71.36
- shape.major_axis_m: 90.83
- shape.minor_axis_m: 55.48
- shape.elongation: 1.637
- shape.orientation_deg: 108.2
- shape.circularity: 1
- shape.solidity: 0.9091
- shape.eccentricity: 0.7917
- shape.rectangularity: 0.8333
- shape.n_corners: 4
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 0.9091

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.2837 / 0.268; ndvi 0.0823 / 0.0911; nbr -0.0733 / -0.0768
- after: brightness 0.2527 / 0.259; ndvi 0.1053 / 0.1013; nbr -0.0588 / -0.0512

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Palmachim launch and test site (launch_site), 839 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 160 m of the footprint (1804 tagged features in the extract; nearest road or track 142 m; nearest candidate cause railway=construction at 1348 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (2 item(s) within 10.0 km; nearest: Benban Solar Park (Q48989519, power_or_industry) at 4.62 km; أبريم (Q100259207, settlement) at 9.79 km); nearest causal item beyond the limit: Benban Solar Park (Q48989519, power_or_industry) at 4.62 km Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2024-09-16 to 2024-12-25; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-11-25 (nearest record: Aswan (Found, 1955) at 58.2 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 142 m away; 0.7% of the land within 1.5 km is built-up Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.9 against background 0.69 nW/cm2/sr, lit in 0 of 7 monthly composites (202412 to 202506, 105 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202404 to 202409) persistent light was absent (radiance 0.62, background 0.6 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran and did not explain the feature. 10 natural-process tests ran clean Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
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
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.2% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2023-09-12 and 2024-12-10 within 106 m of the candidate, but the record is incomplete (burned area: 14/16 monthly files read for 6 pixels; no file for 2023-09, 2024-07; active fire: 116 eight-day files read (0 incomplete); 448/456 days covered, clear view on 448), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NDVI rose (+0.038). Recovery fraction 0.03: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 119 other yearly candidates in this region changed the same way in 2025 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.04) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-11-25 (nearest record: Aswan (Found, 1955) at 58.2 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: fire_history, human_context (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2025-05-07 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2023-10-17 to 2024-10-16: scenes S2B_36RVN_20240519_1_L2A, S2A_36RVN_20240713_0_L2A, S2B_36RVN_20240728_0_L2A, S2B_36RVN_20240906_0_L2A
- Sentinel-2 `after` composite, window 2024-11-25 to 2025-11-25: scenes S2C_36RVN_20241130_1_L2A, S2A_36RVN_20250511_0_L2A, S2C_36RVN_20250906_0_L2A, S2A_36RVN_20250928_0_L2A
- Sentinel-2 `context` composite, window 2024-11-25 to 2025-11-25: scenes S2C_36RVN_20241130_1_L2A, S2A_36RVN_20250511_0_L2A, S2C_36RVN_20250906_0_L2A, S2A_36RVN_20250928_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
