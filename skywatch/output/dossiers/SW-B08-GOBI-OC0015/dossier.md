# Dossier: candidate SW-B08-GOBI-OC0015

## What was detected
The detector `optical_change` flagged a structure or installation that the detector flagged (signature class `installation`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2875 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 43.03225 N, 98.66048 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 98.65875, 43.03089, 98.66220, 43.03340; centre 43.03214, 98.66047
- Area: 11,600 m2
- Search region: `B08-GOBI`

## When
The feature is absent in imagery up to 2023-10-20 and present from 2025-07-21. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2025
- step_snr: 7.188
- d_brightness: 0.04791
- d_ndvi: 0.01069
- d_nbr: 0.03591
- d_swir: 0.08008
- persistence_years: 2
- recovery_fraction: 0.2835
- crowding: 0.0003509
- n_valid_years: 8
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-08-05", "2018-08-07", "2018-08-12"], "2019": ["2019-07-31", "2019-08-10", "2019-08-20"], "2020": ["2020-08-01", "2020-08-06", "2020-08-09"], "2021": ["2021-07-30", "2021-08-04", "2021-08-21"], "2022": ["2022-08-04", "2022-08-09", "2022-08-11"], "2023": ["2023-07-27", "2023-08-06",...
- scene_ids_before: ["S2B_47TMH_20240808_0_L2A", "S2A_47TMH_20240810_0_L2A", "S2B_47TMH_20240818_0_L2A"]
- scene_ids_after: ["S2C_47TMH_20250808_0_L2A", "S2C_47TMH_20250805_0_L2A", "S2B_47TMH_20250810_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 29 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_mode: contrast
- series_shift: 0.03197
- series_noise: 0.007639
- onset_window_days: 640
- onset_flips: 3
- landsat: {"status": "not_run", "reason": "too few clear Landsat scenes (4 before, 1 after)"}
- sar: {"status": "ok", "relative_orbit": 4, "orbit_state": "descending", "before": [{"date": "2023-03-04", "scene_id": "S1A_IW_GRDH_1SDV_20230304T233431_20230304T233500_047501_05B419", "contrast_db": 0.9352264404296875}, {"date": "2023-04-21", "scene_id": "S1A_IW_GRDH_1SDV_20230421T233432_20230421T2335...
- regional_siblings: {"count": 5, "compared": 119, "year": 2025, "ids": ["SW-B08-GOBI-OC0004", "SW-B08-GOBI-OC0018", "SW-B08-GOBI-OC0012", "SW-B08-GOBI-OC0010", "SW-B08-GOBI-OC0009"], "spread_km": 5.9, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 11,600
- shape.perimeter_m: 497.3
- shape.equivalent_diameter_m: 121.5
- shape.major_axis_m: 296.4
- shape.minor_axis_m: 66.4
- shape.elongation: 4.463
- shape.orientation_deg: 42.83
- shape.circularity: 0.5895
- shape.solidity: 0.6444
- shape.eccentricity: 0.9746
- shape.rectangularity: 0.8056
- shape.n_corners: 5
- shape.straight_edge_fraction: 0.6378
- shape.hole_fraction: 0
- shape.regularity: 0.3311

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1495 / 0.1133; ndvi 0.0583 / 0.0723; nbr -0.1776 / -0.1792
- after: brightness 0.1801 / 0.1249; ndvi 0.0682 / 0.0803; nbr -0.1485 / -0.1553

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Jiuquan Satellite Launch Center (launch_site), 232 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 2876 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.1 km dated 2023-09-20 to 2025-08-20; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-07-21 (nearest record: Noyan-Bogdo (Fell, 1933) at 309.9 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): NOT RUN. The night-light archive ends 2025-06-30; the feature is first seen 2025-07-21, so no night-light data exists for the period after its appearance. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. the scene-by-scene record is not a single transition; moisture-like spectral change (wetting or drying); an irregular brightness-only change on bare ground: moving sand, dust or a wetted surface is the likely cause; possible regional pattern: 5 of 119 other yearly candidates in this region changed the same way in 2025 (spectral direction within cosine 0.9, size within 2.0x), spread over 5.9 km; its regular outline kept it from being explained by that alone Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran but was INCONCLUSIVE. the scene-by-scene record is not a single transition Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (1 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran but was INCONCLUSIVE. an irregular brightness-only change on bare ground: moving sand, dust or a wetted surface is the likely cause Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 13 of 14 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 13 of 14 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 8 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2022-09-15 and 2025-08-05 within 198 m of the candidate, but the record is incomplete (burned area: 32/36 monthly files read for 8 pixels; no file for 2023-09, 2024-07, 2025-05, 2025-08; active fire: daily active-fire files not read for this period), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.048); NBR rose (+0.036). Recovery fraction 0.28: gradual recovery, as vegetation regrowth after fire would give Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran but was INCONCLUSIVE. possible regional pattern: 5 of 119 other yearly candidates in this region changed the same way in 2025 (spectral direction within cosine 0.9, size within 2.0x), spread over 5.9 km; its regular outline kept it from being explained by that alone Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.04) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-07-21 (nearest record: Noyan-Bogdo (Fell, 1933) at 309.9 km)
- **night_lights**: The night-light archive ends 2025-06-30; the feature is first seen 2025-07-21, so no night-light data exists for the period after its appearance.
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
- The Esri picture in `hires.png` was taken on 2025-08-21 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2022-10-20 to 2023-10-20: scenes S2B_47TMH_20221104_0_L2A, S2A_47TMH_20230806_0_L2A, S2A_47TMH_20231015_0_L2A, S2B_47TMH_20231020_0_L2A
- Sentinel-2 `after` composite, window 2025-07-21 to 2026-07-21: scenes S2A_47TMH_20250817_0_L2A, S2A_47TMH_20250906_0_L2A, S2B_47TMH_20250909_1_L2A, S2A_47TMH_20251026_0_L2A
- Sentinel-2 `context` composite, window 2025-07-21 to 2026-07-21: scenes S2A_47TMH_20250817_0_L2A, S2A_47TMH_20250906_0_L2A, S2B_47TMH_20250909_1_L2A, S2A_47TMH_20251026_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
