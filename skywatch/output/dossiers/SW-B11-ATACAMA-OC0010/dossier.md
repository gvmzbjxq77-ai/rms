# Dossier: candidate SW-B11-ATACAMA-OC0010

## What was detected
The detector `optical_change` flagged a structure or installation that the detector flagged (signature class `installation`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.3456 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: -25.36202 N, -69.98621 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -69.98712, -25.36310, -69.98535, -25.36093; centre -25.36202, -69.98623
- Area: 11,600 m2
- Search region: `B11-ATACAMA`

## When
The feature is absent in imagery up to 2023-04-18 and present from 2024-04-12. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: step
- break_year: 2024
- step_snr: 8.641
- d_brightness: 0.07743
- d_ndvi: -0.05014
- d_nbr: 0.0899
- d_swir: 0.003174
- persistence_years: 3
- recovery_fraction: 0.7383
- crowding: 0.0002631
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-04-04", "2018-04-09", "2018-04-19"], "2019": ["2019-04-02", "2019-04-09", "2019-04-14"], "2020": ["2020-04-13", "2020-04-18", "2020-04-23"], "2021": ["2021-04-13", "2021-04-18", "2021-04-21"], "2022": ["2022-04-13", "2022-04-16", "2022-04-21"], "2023": ["2023-04-08", "2023-04-16",...
- scene_ids_before: ["S2B_19JCM_20230416_0_L2A", "S2B_19JCN_20230416_0_L2A", "S2A_19JDN_20230408_0_L2A", "S2A_19JDM_20230408_0_L2A", "S2A_19JCM_20230408_0_L2A", "S2A_19JCN_20230408_0_L2A", "S2A_19JDM_20230418_0_L2A", "S2A_19JDN_20230418_0_L2A", "S2A_19JCN_20230418_0_L2A"]
- scene_ids_after: ["S2A_19JCM_20240412_0_L2A", "S2A_19JCN_20240412_0_L2A", "S2A_19JDM_20240412_0_L2A", "S2A_19JDN_20240412_0_L2A", "S2B_19JCM_20240417_0_L2A", "S2B_19JCN_20240417_0_L2A", "S2B_19JDM_20240417_0_L2A", "S2B_19JDN_20240417_0_L2A", "S2B_19JCM_20240420_0_L2A", "S2B_19JCN_20240420_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 32 dates (plotted in timeseries.png when usable; full values in dossier.json)
- onset_note: too few scenes on one side of the window
- landsat: {"status": "ok", "before": [{"date": "2022-04-12", "scene_id": "LC08_L2SP_001077_20220412_02_T1", "brightness": 0.0038323402404785156, "ndvi": 0.017098896205425262, "nbr": -0.010299086570739746, "kelvin": -0.17474365234375}, {"date": "2022-11-30", "scene_id": "LC09_L2SP_001077_20221130_02_T1", "b...
- sar: {"status": "ok", "relative_orbit": 156, "orbit_state": "descending", "before": [{"date": "2022-08-23", "scene_id": "S1A_IW_GRDH_1SDV_20220823T100230_20220823T100255_044678_05557B", "contrast_db": 0.8021697998046875}, {"date": "2022-10-22", "scene_id": "S1A_IW_GRDH_1SDV_20221022T100231_20221022T10...
- regional_siblings: {"count": 0, "compared": 119, "year": 2024, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 11,600
- shape.perimeter_m: 369.7
- shape.equivalent_diameter_m: 121.5
- shape.major_axis_m: 155.3
- shape.minor_axis_m: 95.47
- shape.elongation: 1.627
- shape.orientation_deg: 87.29
- shape.circularity: 1
- shape.solidity: 0.9062
- shape.eccentricity: 0.7888
- shape.rectangularity: 0.725
- shape.n_corners: 4
- shape.straight_edge_fraction: 0.8194
- shape.hole_fraction: 0
- shape.regularity: 0.9062

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1798 / 0.1699; ndvi 0.0728 / 0.0672; nbr -0.1005 / -0.1088
- after: brightness 0.237 / 0.1759; ndvi 0.0573 / 0.073; nbr -0.0284 / -0.0858

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Alcantara Launch Center (launch_site), 3742 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 241 m of the footprint (6 tagged features in the extract; nearest road or track 64 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (12 item(s) within 10.0 km; nearest: Aguada del Milagro (Q22367342, other) at 2.74 km; Margarita (Q23305419, mine_or_quarry) at 3.44 km; Cerro Agua Verde (Q23655603, other) at 4.11 km); nearest causal item beyond the limit: Margarita (Q23305419, mine_or_quarry) at 3.44 km Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.1 km dated 2023-03-19 to 2024-05-12; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-04-12 (nearest record: San Juan 025 (Found, 2008) at 8.8 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 64 m away Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.395 against background 0.325 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 174 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202210 to 202303) persistent light was absent (radiance 0.335, background 0.27 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran and did not explain the feature. 10 natural-process tests ran clean Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (3 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): NOT RUN. per-scene support could not be tested: too few clear scenes before the change to form a baseline Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): NOT RUN. too few clear scenes before the change to form a baseline Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2022-03-14 and 2024-04-27 within 150 m of the candidate, but the record is incomplete (burned area: 25/26 monthly files read for 6 pixels; no file for 2023-09; active fire: 187 eight-day files read (0 incomplete); 752/776 days covered, clear view on 749), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.077); NBR rose (+0.090). Recovery fraction 0.74: gradual recovery, as vegetation regrowth after fire would give Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 119 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.09) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-04-12 (nearest record: San Juan 025 (Found, 2008) at 8.8 km)
- **artefact_screen** (mandatory): per-scene support could not be tested: too few clear scenes before the change to form a baseline
- **artefact:per_scene_support**: too few clear scenes before the change to form a baseline
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; checks not run: artefact_screen; inconclusive: fire_history, human_context (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2025-03-05 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2022-04-18 to 2023-04-18: scenes S2A_19JCM_20220602_0_L2A, S2A_19JCN_20220602_0_L2A, S2A_19JDM_20220602_0_L2A, S2A_19JDN_20220602_0_L2A, S2B_19JCM_20230222_0_L2A, S2B_19JCN_20230222_0_L2A, S2B_19JDM_20230222_0_L2A, S2B_19JDN_20230222_0_L2A, S2B_19JCM_20230304_0_L2A, S2B_19JCN_20230304_0_L2A, S2B_19JDM_20230304_0_L2A, S2B_19JDN_20230304_0_L2A, S2A_19JCM_20230309_0_L2A, S2A_19JCN_20230309_0_L2A, S2A_19JDM_20230309_0_L2A, S2A_19JDN_20230309_0_L2A
- Sentinel-2 `after` composite, window 2024-04-12 to 2025-04-12: scenes S2B_19JCM_20240417_0_L2A, S2B_19JCN_20240417_0_L2A, S2B_19JDM_20240417_0_L2A, S2B_19JDN_20240417_0_L2A, S2B_19JCM_20250102_0_L2A, S2B_19JCN_20250102_0_L2A, S2B_19JDM_20250102_0_L2A, S2B_19JDN_20250102_1_L2A, S2A_19JCM_20250320_0_L2A, S2A_19JCN_20250320_0_L2A, S2A_19JDM_20250320_0_L2A, S2A_19JDN_20250320_0_L2A, S2C_19JCM_20250328_0_L2A, S2C_19JCN_20250328_0_L2A, S2C_19JDM_20250328_0_L2A, S2C_19JDN_20250328_0_L2A
- Sentinel-2 `context` composite, window 2024-04-12 to 2025-04-12: scenes S2B_19JCM_20240417_0_L2A, S2B_19JDM_20240417_0_L2A, S2B_19JCM_20250102_0_L2A, S2B_19JCN_20250102_0_L2A, S2B_19JDM_20250102_0_L2A, S2B_19JDN_20250102_1_L2A, S2A_19JCM_20250320_0_L2A, S2A_19JCN_20250320_0_L2A, S2A_19JDM_20250320_0_L2A, S2A_19JDN_20250320_0_L2A, S2C_19JCM_20250328_0_L2A, S2C_19JCN_20250328_0_L2A, S2C_19JDM_20250328_0_L2A, S2C_19JDN_20250328_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
