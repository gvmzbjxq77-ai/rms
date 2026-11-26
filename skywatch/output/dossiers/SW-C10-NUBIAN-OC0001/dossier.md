# Dossier: candidate SW-C10-NUBIAN-OC0001

## What was detected
The detector `optical_change` flagged a structure or installation that the detector flagged (signature class `installation`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.4195 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 20.61744 N, 28.60424 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 28.60363, 20.61659, 28.60496, 20.61840; centre 20.61750, 28.60429
- Area: 5,600 m2
- Search region: `C10-NUBIAN`

## When
The feature is absent in imagery up to 2023-11-02 and present from 2024-10-29. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: transient
- break_year: 2024
- step_snr: 10.49
- d_brightness: -0.03426
- d_ndvi: 0.0116
- d_nbr: 0.02447
- d_swir: -0.07879
- persistence_years: 1
- recovery_fraction: 1
- crowding: 0.00136
- n_valid_years: 8
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-10-29", "2018-10-31", "2018-11-03"], "2019": ["2019-10-26", "2019-10-31", "2019-11-03"], "2020": ["2020-10-28", "2020-10-30", "2020-11-02"], "2021": ["2021-10-28", "2021-10-30", "2021-11-02"], "2022": ["2022-10-25", "2022-10-28", "2022-10-30"], "2023": ["2023-10-28", "2023-10-30",...
- scene_ids_before: ["S2A_35QPC_20231030_0_L2A", "S2A_35QPC_20231102_0_L2A", "S2B_35QPC_20231028_0_L2A"]
- scene_ids_after: ["S2B_35QPC_20241101_0_L2A", "S2B_35QPC_20241029_0_L2A", "S2A_35QPC_20241103_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 29 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_shift: -0.01943
- series_noise: 0.02415
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "ok", "before": [{"date": "2022-09-28", "scene_id": "LC09_L2SP_177046_20220928_02_T1", "brightness": -0.0008401870727539062, "ndvi": 6.689876317977905e-05, "nbr": 0.00028128549456596375, "kelvin": -0.137237548828125}, {"date": "2023-02-11", "scene_id": "LC08_L2SP_177046_20230211_02_T1"...
- sar: {"status": "not_run", "reason": "no relative orbit covers both periods (0 scenes before, 58 after)"}
- regional_siblings: {"count": 5, "compared": 5, "year": 2024, "ids": ["SW-C10-NUBIAN-OC0002", "SW-C10-NUBIAN-OC0003", "SW-C10-NUBIAN-OC0006", "SW-C10-NUBIAN-OC0004", "SW-C10-NUBIAN-OC0005"], "spread_km": 24.4, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 5,600
- shape.perimeter_m: 244.1
- shape.equivalent_diameter_m: 84.44
- shape.major_axis_m: 140.3
- shape.minor_axis_m: 52.92
- shape.elongation: 2.652
- shape.orientation_deg: 98.08
- shape.circularity: 1
- shape.solidity: 0.875
- shape.eccentricity: 0.9262
- shape.rectangularity: 0.7778
- shape.n_corners: 4
- shape.straight_edge_fraction: 0.7278
- shape.hole_fraction: 0
- shape.regularity: 0.875

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.3346 / 0.3309; ndvi 0.0812 / 0.0821; nbr -0.0772 / -0.0761
- after: brightness 0.31 / 0.3261; ndvi 0.0797 / 0.0766; nbr -0.0693 / -0.0727

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Palmachim launch and test site (launch_site), 1387 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 2908 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2023-10-03 to 2024-11-28; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-10-29 (nearest record: Gebel Kamil (Found, 2009) at 303.7 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.445 against background 0.36 nW/cm2/sr, lit in 0 of 8 monthly composites (202411 to 202506, 121 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202305 to 202310) persistent light was absent (radiance 0.41, background 0.35 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): EXPLAINS the feature (a sufficient conventional cause was found). regional pattern: 5 of 5 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 24.4 km; a change that recurs across a region is a regional process (rain, greening, blown sand, moisture or the sensor), not a local event Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (0 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 4 separate scenes show the short-lived change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 4 separate scenes show the short-lived change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 8 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.1% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2022-09-28 and 2024-11-13 within 122 m of the candidate, but the record is incomplete (burned area: 25/27 monthly files read for 6 pixels; no file for 2023-09, 2024-07; active fire: 190 eight-day files read (0 incomplete); 754/778 days covered, clear view on 748), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.024). Recovery fraction 1.00: fully recovered, which fits a grass fire but also a passing darkening Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): EXPLAINS the feature (a sufficient conventional cause was found). regional pattern: 5 of 5 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 24.4 km; a change that recurs across a region is a regional process (rain, greening, blown sand, moisture or the sensor), not a local event Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-10-29 (nearest record: Gebel Kamil (Found, 2009) at 303.7 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T0**: explained by a conventional cause.

Reason: explained by: natural:regional_pattern, natural_process (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2023-09-12 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2022-11-02 to 2023-11-02: scenes S2B_35QPC_20221109_0_L2A, S2A_35QPC_20221114_0_L2A, S2B_35QPC_20221119_1_L2A, S2A_35QPC_20221124_0_L2A
- Sentinel-2 `after` composite, window 2024-10-29 to 2025-10-29: scenes S2A_35QPC_20241103_0_L2A, S2B_35QPC_20241108_0_L2A, S2B_35QPC_20241118_0_L2A, S2A_35QPC_20241123_0_L2A
- Sentinel-2 `context` composite, window 2024-10-29 to 2025-10-29: scenes S2A_35QPC_20241103_0_L2A, S2B_35QPC_20241108_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
