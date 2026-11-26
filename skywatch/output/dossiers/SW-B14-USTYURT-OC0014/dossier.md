# Dossier: candidate SW-B14-USTYURT-OC0014

## What was detected
The detector `optical_change` flagged a structure or installation that the detector flagged (signature class `installation`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.4073 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 43.44544 N, 56.19788 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 56.19670, 43.44478, 56.19894, 43.44602; centre 43.44540, 56.19782
- Area: 4,800 m2
- Search region: `B14-USTYURT`

## When
The feature is absent in imagery up to 2025-11-24 and present from 2026-05-18. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: latest_year
- break_year: 2026
- step_snr: 10.18
- d_brightness: -0.02208
- d_ndvi: 0.1056
- d_nbr: 0.1576
- d_swir: -0.03871
- persistence_years: 1
- recovery_fraction: 0
- crowding: 0.002763
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-04", "2018-07-19", "2018-07-29"], "2019": ["2019-06-29", "2019-07-04", "2019-07-09"], "2020": ["2020-07-03", "2020-07-08", "2020-07-28"], "2021": ["2021-07-13", "2021-07-18", "2021-08-02"], "2022": ["2022-07-13", "2022-07-18", "2022-07-23"], "2023": ["2023-07-03", "2023-07-08",...
- scene_ids_before: ["S2A_40TDP_20250719_1_L2A", "S2B_40TDP_20250722_0_L2A", "S2C_40TDP_20250727_0_L2A"]
- scene_ids_after: ["S2C_40TDP_20260712_0_L2A", "S2B_40TDP_20260717_0_L2A", "S2A_40TDP_20260724_1_L2A"]
- res_m: 20
- weak: False
- series: time series with 31 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_mode: contrast
- series_shift: 0.05448
- series_noise: 0.006303
- onset_window_days: 175
- onset_flips: 3
- landsat: {"status": "ok", "before": [{"date": "2025-02-06", "scene_id": "LC09_L2SP_163030_20250206_02_T1", "brightness": -0.00805044174194336, "ndvi": 0.005058906972408295, "nbr": -0.01916399598121643, "kelvin": 0.04718017578125}, {"date": "2025-06-14", "scene_id": "LC09_L2SP_163030_20250614_02_T1", "brig...
- sar: {"status": "not_run", "reason": "footprint radius 39 m is under two radar pixels"}
- regional_siblings: {"count": 8, "compared": 14, "year": 2026, "ids": ["SW-B14-USTYURT-OC0011", "SW-B14-USTYURT-OC0007", "SW-B14-USTYURT-OC0006", "SW-B14-USTYURT-OC0013", "SW-B14-USTYURT-OC0009", "SW-B14-USTYURT-OC0005", "SW-B14-USTYURT-OC0008", "SW-B14-USTYURT-OC0015"], "spread_km": 37.4, "min_cosine": 0.9, "magnit...
- shape.area_m2: 4,800
- shape.perimeter_m: 204.1
- shape.equivalent_diameter_m: 78.18
- shape.major_axis_m: 115.5
- shape.minor_axis_m: 54.16
- shape.elongation: 2.132
- shape.orientation_deg: 168.7
- shape.circularity: 1
- shape.solidity: 0.9231
- shape.eccentricity: 0.8832
- shape.rectangularity: 0.8
- shape.n_corners: 4
- shape.straight_edge_fraction: 0.6538
- shape.hole_fraction: 0
- shape.regularity: 0.9231

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.2469 / 0.2769; ndvi 0.087 / 0.0766; nbr -0.0532 / -0.0385
- after: brightness 0.2349 / 0.2541; ndvi 0.1407 / 0.1014; nbr 0.0356 / -0.023

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Baikonur Cosmodrome (launch_site), 589 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (98%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 2946 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2025-10-25 to 2026-06-17; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2026-05-18 (nearest record: Beyneu (Found, 2001) at 237.0 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): NOT RUN. The night-light archive ends 2025-06-30; the feature is first seen 2026-05-18, so no night-light data exists for the period after its appearance. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. the scene-by-scene record is not a single transition; possible regional pattern: 8 of 14 other yearly candidates in this region changed the same way in 2026 (spectral direction within cosine 0.9, size within 2.0x), spread over 37.4 km; its regular outline kept it from being explained by that alone Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran but was INCONCLUSIVE. the scene-by-scene record is not a single transition Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (0 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 7 separate scenes show the short-lived change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 7 separate scenes show the short-lived change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.3% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2024-10-20 and 2026-06-02 within 114 m of the candidate, but the record is incomplete (burned area: 16/21 monthly files read for 6 pixels; no file for 2025-05, 2025-07, 2025-08, 2025-09, 2025-10; active fire: 115 eight-day files read (0 incomplete); 447/591 days covered, clear view on 365), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.158); NDVI rose (+0.106). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran but was INCONCLUSIVE. possible regional pattern: 8 of 14 other yearly candidates in this region changed the same way in 2026 (spectral direction within cosine 0.9, size within 2.0x), spread over 37.4 km; its regular outline kept it from being explained by that alone Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.16) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2026-05-18 (nearest record: Beyneu (Found, 2001) at 237.0 km)
- **night_lights**: The night-light archive ends 2025-06-30; the feature is first seen 2026-05-18, so no night-light data exists for the period after its appearance.
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: fire_history, natural:recurring_cycle, natural:regional_pattern, natural_process (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2025-05-30 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2024-11-24 to 2025-11-24: scenes S2B_40TDP_20250602_0_L2A, S2A_40TDP_20250629_1_L2A, S2A_40TDP_20250808_1_L2A, S2C_40TDP_20250826_0_L2A
- Sentinel-2 `after` composite, window 2026-05-18 to 2026-11-25: scenes S2B_40TDP_20260528_1_L2A, S2C_40TDP_20260801_0_L2A, S2B_40TDP_20260915_1_L2A, S2C_40TDP_20261020_0_L2A
- Sentinel-2 `context` composite, window 2026-05-18 to 2026-11-25: scenes S2B_40TDP_20260528_1_L2A, S2C_40TDP_20260801_0_L2A, S2B_40TDP_20260915_1_L2A, S2C_40TDP_20261020_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
