# Dossier: candidate SW-B14-USTYURT-OC0002

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2794 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 43.69800 N, 56.07123 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 56.07023, 43.69737, 56.07223, 43.69862; centre 43.69800, 56.07123
- Area: 3,200 m2
- Search region: `B14-USTYURT`

## When
The feature is absent in imagery up to 2025-03-14 and present from 2025-06-12. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: step
- break_year: 2025
- step_snr: 6.984
- d_brightness: 0.02407
- d_ndvi: 0.03855
- d_nbr: 0.0884
- d_swir: 0.008161
- persistence_years: 2
- recovery_fraction: 0
- crowding: 0.0005263
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-04", "2018-07-19", "2018-07-29"], "2019": ["2019-06-29", "2019-07-04", "2019-07-09"], "2020": ["2020-07-03", "2020-07-08", "2020-07-28"], "2021": ["2021-07-13", "2021-07-18", "2021-08-02"], "2022": ["2022-07-13", "2022-07-18", "2022-07-23"], "2023": ["2023-07-03", "2023-07-08",...
- scene_ids_before: ["S2A_40TDP_20240702_0_L2A", "S2A_40TDP_20240712_0_L2A", "S2B_40TDP_20240717_0_L2A"]
- scene_ids_after: ["S2A_40TDP_20250719_1_L2A", "S2B_40TDP_20250722_0_L2A", "S2C_40TDP_20250727_0_L2A"]
- res_m: 20
- weak: True
- series: time series with 30 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_mode: contrast
- series_shift: 0.0308
- series_noise: 0.003524
- onset_window_days: 90
- onset_flips: 1
- landsat: {"status": "ok", "before": [{"date": "2024-02-28", "scene_id": "LC08_L2SP_163030_20240228_02_T1", "brightness": -0.0036385059356689453, "ndvi": -0.0032942593097686768, "nbr": -0.0037880055606365204, "kelvin": -0.09893798828125}, {"date": "2024-05-10", "scene_id": "LC09_L2SP_163030_20240510_02_T1"...
- sar: {"status": "not_run", "reason": "footprint radius 32 m is under two radar pixels"}
- regional_siblings: {"count": 0, "compared": 14, "year": 2025, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 3,200
- shape.perimeter_m: 160
- shape.equivalent_diameter_m: 63.83
- shape.major_axis_m: 97.98
- shape.minor_axis_m: 40
- shape.elongation: 2.449
- shape.orientation_deg: 26.57
- shape.circularity: 1
- shape.solidity: 0.8
- shape.eccentricity: 0.9129
- shape.rectangularity: 0.6667
- shape.n_corners: 4
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 0.8

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.2828 / 0.2936; ndvi 0.0848 / 0.0769; nbr -0.0398 / -0.0425
- after: brightness 0.3292 / 0.3037; ndvi 0.0878 / 0.0806; nbr 0.0034 / -0.0407

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Baikonur Cosmodrome (launch_site), 584 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (81%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 3004 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (1 item(s) within 10.0 km; nearest: Tuzelboy Tog' (Q31538145, other) at 3.89 km) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2025-02-12 to 2025-07-12; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-06-12 (nearest record: Beyneu (Found, 2001) at 207.2 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): NOT RUN. The night-light archive ends 2025-06-30; the feature is first seen 2025-06-12, so no night-light data exists for the period after its appearance. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran and did not explain the feature. 10 natural-process tests ran clean Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (0 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 12 of 12 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 12 of 12 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.1% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2024-02-08 and 2025-06-27 within 106 m of the candidate, but the record is incomplete (burned area: 15/17 monthly files read for 7 pixels; no file for 2024-07, 2025-05; active fire: 129 eight-day files read (0 incomplete); 506/506 days covered, clear view on 456), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.024); NBR rose (+0.088); NDVI rose (+0.039). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 14 other yearly candidates in this region changed the same way in 2025 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.09) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-06-12 (nearest record: Beyneu (Found, 2001) at 207.2 km)
- **night_lights**: The night-light archive ends 2025-06-30; the feature is first seen 2025-06-12, so no night-light data exists for the period after its appearance.
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: fire_history (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2025-09-10 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2024-03-14 to 2025-03-14: scenes S2A_40TDP_20240702_0_L2A, S2A_40TDP_20240801_0_L2A, S2A_40TDP_20240831_0_L2A, S2B_40TDP_20241015_0_L2A
- Sentinel-2 `after` composite, window 2025-06-12 to 2026-06-12: scenes S2A_40TDP_20250629_1_L2A, S2A_40TDP_20250808_1_L2A, S2C_40TDP_20250826_0_L2A, S2B_40TDP_20250831_0_L2A
- Sentinel-2 `context` composite, window 2025-06-12 to 2026-06-12: scenes S2A_40TDP_20250629_1_L2A, S2A_40TDP_20250808_1_L2A, S2C_40TDP_20250826_0_L2A, S2B_40TDP_20250831_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
