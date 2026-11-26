# Dossier: candidate SW-B29-PATAGONIA-OC0002

## What was detected
The detector `optical_change` flagged a structure or installation that the detector flagged (signature class `installation`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 1 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: -47.57645 N, -70.33843 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -70.34033, -47.57779, -70.33641, -47.57522; centre -47.57650, -70.33837
- Area: 36,000 m2
- Search region: `B29-PATAGONIA`

## When
The feature is absent in imagery up to 2024-07-27 and present from 2025-08-29. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2024
- step_snr: 26.82
- d_brightness: 0.01981
- d_ndvi: -0.04694
- d_nbr: 0.8618
- d_swir: -0.2849
- persistence_years: 2
- recovery_fraction: 0.05897
- crowding: 0.007412
- n_valid_years: 8
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
- composite_dates: {"2018": ["2019-01-28", "2019-02-04", "2019-02-07"], "2019": ["2020-01-25", "2020-01-30", "2020-02-22"], "2020": ["2021-01-07", "2021-01-19", "2021-02-08"], "2021": ["2022-01-09", "2022-01-12", "2022-01-29"], "2022": ["2023-01-14", "2023-01-22", "2023-02-01"], "2023": ["2024-01-22", "2024-01-27",...
- scene_ids_before: ["S2B_19GCH_20240122_0_L2A", "S2B_19GDH_20240122_0_L2A", "S2A_19GCH_20240127_0_L2A", "S2A_19GDH_20240127_0_L2A", "S2B_19GCH_20240129_0_L2A", "S2B_19GDH_20240129_0_L2A"]
- scene_ids_after: ["S2B_19GCH_20250103_1_L2A", "S2B_19GDH_20250103_1_L2A", "S2B_19GCH_20250113_0_L2A", "S2B_19GDH_20250113_0_L2A", "S2C_19GCH_20250131_0_L2A", "S2C_19GDH_20250131_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 25 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_mode: contrast
- series_shift: 0.6609
- series_noise: 0.1691
- onset_window_days: 398
- onset_flips: 3
- landsat: {"status": "ok", "before": [{"date": "2023-08-01", "scene_id": "LC09_L2SP_230093_20230801_02_T1", "brightness": 0.06476961076259613, "ndvi": -0.05933792144060135, "nbr": 0.03557262569665909, "kelvin": -0.412689208984375}, {"date": "2023-11-05", "scene_id": "LC09_L2SP_230093_20231105_02_T1", "brig...
- sar: {"status": "ok", "relative_orbit": 164, "orbit_state": "ascending", "before": [{"date": "2023-12-04", "scene_id": "S1A_IW_GRDH_1SDV_20231204T234052_20231204T234117_051511_0637C5", "contrast_db": -0.10037612915039062}, {"date": "2024-01-21", "scene_id": "S1A_IW_GRDH_1SDV_20240121T234049_20240121T2...
- regional_siblings: {"count": 33, "compared": 119, "year": 2024, "ids": ["SW-B29-PATAGONIA-OC0103", "SW-B29-PATAGONIA-OC0107", "SW-B29-PATAGONIA-OC0116", "SW-B29-PATAGONIA-OC0084", "SW-B29-PATAGONIA-OC0089", "SW-B29-PATAGONIA-OC0070", "SW-B29-PATAGONIA-OC0081", "SW-B29-PATAGONIA-OC0088"], "spread_km": 26.6, "min_cos...
- shape.area_m2: 36,000
- shape.perimeter_m: 666.3
- shape.equivalent_diameter_m: 214.1
- shape.major_axis_m: 226
- shape.minor_axis_m: 204.8
- shape.elongation: 1.103
- shape.orientation_deg: 26.29
- shape.circularity: 1
- shape.solidity: 0.9574
- shape.eccentricity: 0.4228
- shape.rectangularity: 0.8182
- shape.n_corners: 7
- shape.straight_edge_fraction: 0.812
- shape.hole_fraction: 0
- shape.regularity: 0.9574

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1841 / 0.1281; ndvi 0.0803 / 0.1323; nbr -0.0768 / -0.1021
- after: brightness 0.1596 / 0.1132; ndvi 0.0882 / 0.1579; nbr 0.0773 / -0.0699

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Alcantara Launch Center (launch_site), 5608 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (91%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 295 m of the footprint (14 tagged features in the extract; nearest road or track 690 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (1 item(s) within 10.0 km; nearest: Q21832104 (Q21832104, other) at 5.86 km) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.1 km dated 2024-06-27 to 2025-09-28; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-08-29 (nearest record: Laguna Manantiales (Found, 1945) at 244.2 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): NOT RUN. The night-light archive ends 2025-06-30; the feature is first seen 2025-08-29, so no night-light data exists for the period after its appearance. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. the scene-by-scene record is not a single transition; possible regional pattern: 33 of 119 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 26.6 km; its regular outline kept it from being explained by that alone Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran but was INCONCLUSIVE. the scene-by-scene record is not a single transition Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (1 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 9 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 9 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 8 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.7% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2023-06-23 and 2025-09-13 within 205 m of the candidate, but the record is incomplete (burned area: 23/28 monthly files read for 10 pixels; no file for 2023-09, 2024-07, 2025-05, 2025-08, 2025-09; active fire: daily active-fire files not read for this period), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.862). Recovery fraction 0.06: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran but was INCONCLUSIVE. possible regional pattern: 33 of 119 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 26.6 km; its regular outline kept it from being explained by that alone Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.86) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-08-29 (nearest record: Laguna Manantiales (Found, 1945) at 244.2 km)
- **night_lights**: The night-light archive ends 2025-06-30; the feature is first seen 2025-08-29, so no night-light data exists for the period after its appearance.
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T1**: seen in one sensor only.

Reason: seen in one sensor only (optical_s2) (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2023-12-07 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2023-07-28 to 2024-07-27: scenes S2B_19GCH_20231203_0_L2A, S2B_19GDH_20231203_0_L2A, S2B_19GCH_20240129_0_L2A, S2B_19GDH_20240129_0_L2A, S2B_19GCH_20240411_0_L2A, S2B_19GDH_20240411_0_L2A, S2B_19GCH_20240421_0_L2A, S2B_19GDH_20240421_0_L2A
- Sentinel-2 `after` composite, window 2025-08-29 to 2026-08-29: scenes S2B_19GCH_20251129_0_L2A, S2B_19GDH_20251129_0_L2A, S2B_19GCH_20260329_0_L2A, S2B_19GDH_20260329_0_L2A, S2B_19GCH_20260521_0_L2A, S2B_19GDH_20260521_0_L2A, S2A_19GCH_20260707_1_L2A, S2A_19GDH_20260707_1_L2A
- Sentinel-2 `context` composite, window 2025-08-29 to 2026-08-29: scenes S2B_19GCH_20251129_0_L2A, S2B_19GDH_20251129_0_L2A, S2B_19GCH_20260329_0_L2A, S2B_19GDH_20260329_0_L2A, S2B_19GCH_20260521_0_L2A, S2B_19GDH_20260521_0_L2A, S2A_19GCH_20260707_1_L2A, S2A_19GDH_20260707_1_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
