# Dossier: candidate SW-S03-RENFREW-OC0009

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.358 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 45.49620 N, -76.65105 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -76.65184, 45.49567, -76.65027, 45.49673; centre 45.49620, -76.65105
- Area: 1,600 m2
- Search region: `S03-RENFREW`

## When
The feature is absent in imagery up to 2025-09-19 and present from 2025-10-04. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2025
- step_snr: 8.949
- d_brightness: 0.08515
- d_ndvi: -0.4881
- d_nbr: -0.5237
- d_swir: 0.1512
- persistence_years: 2
- recovery_fraction: 0.1937
- crowding: 0.002061
- n_valid_years: 8
- years_used: [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2019": ["2019-10-11", "2019-10-26", "2019-11-30"], "2020": ["2020-10-30", "2020-11-04", "2020-11-14"], "2021": ["2021-11-04", "2021-11-24"], "2022": ["2022-11-09", "2022-12-09"], "2023": ["2023-11-04", "2023-11-24"], "2024": ["2024-10-19", "2024-11-13"], "2025": ["2025-10-09", "2025-10-16", "20...
- scene_ids_before: ["S2A_18TUR_20241019_0_L2A", "S2B_18TUR_20241113_0_L2A"]
- scene_ids_after: ["S2B_18TUR_20251009_0_L2A", "S2A_18TUR_20251016_0_L2A", "S2B_18TUR_20251029_1_L2A"]
- res_m: 20
- regional_siblings: {"count": 2, "compared": 68, "year": 2025, "ids": ["SW-S03-RENFREW-OC0030", "SW-S03-RENFREW-OC0001"], "spread_km": 2.6, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- weak: False
- series: time series with 31 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_mode: contrast
- series_shift: -0.3347
- series_noise: 0.0557
- onset_window_days: 15
- onset_flips: 1
- landsat: {"status": "not_run", "reason": "footprint radius 23 m is below one Landsat pixel"}
- sar: {"status": "not_run", "reason": "footprint radius 23 m is under two radar pixels"}
- shape.area_m2: 1,600
- shape.perimeter_m: 80
- shape.equivalent_diameter_m: 45.14
- shape.major_axis_m: 40
- shape.minor_axis_m: 40
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
- before: brightness 0.052 / 0.0447; ndvi 0.6074 / 0.675; nbr 0.3277 / 0.4026
- after: brightness 0.079 / 0.052; ndvi 0.4405 / 0.5855; nbr 0.141 / 0.279

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Wallops Flight Facility (launch_site), 853 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly tree (60%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 122 m of the footprint (5138 tagged features in the extract; nearest road or track 233 m; nearest building 1258 m; nearest candidate cause landuse=commercial at 1196 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (121 item(s) within 10.0 km; nearest: Horton (Q9293943, settlement) at 1.30 km; Little Halliday Creek (Q22556148, other) at 1.43 km; Horton (Q115261785, settlement) at 1.55 km); nearest causal item beyond the limit: Renfrew (Q61038846, research_station) at 4.22 km Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2025-08-20 to 2025-11-03; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-10-04 (nearest record: Blithfield (Found, 1910) at 27.2 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 233 m away; 30% of the land within 1.5 km is cropland; 2.2% of the land within 1.5 km is built-up Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): NOT RUN. The night-light archive ends 2025-06-30; the feature is first seen 2025-10-04, so no night-light data exists for the period after its appearance. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying); possible regional pattern: 2 of 68 other yearly candidates in this region changed the same way in 2025 (spectral direction within cosine 0.9, size within 2.0x), spread over 2.6 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (4 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:regional_pattern** (natural): ran but was INCONCLUSIVE. possible regional pattern: 2 of 68 other yearly candidates in this region changed the same way in 2025 (spectral direction within cosine 0.9, size within 2.0x), spread over 2.6 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 11 of 12 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 11 of 12 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 2 and 3 separate dates; 8 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.2% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2024-08-15 and 2025-10-19 within 85 m of the candidate, but the record is incomplete (burned area: 10/15 monthly files read for 5 pixels; no file for 2024-11, 2025-05, 2025-08, 2025-09, 2025-10; active fire: 79 eight-day files read (0 incomplete); 317/431 days covered, clear view on 206), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.085). Recovery fraction 0.19: gradual recovery, as vegetation regrowth after fire would give Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.52) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-10-04 (nearest record: Blithfield (Found, 1910) at 27.2 km)
- **night_lights**: The night-light archive ends 2025-06-30; the feature is first seen 2025-10-04, so no night-light data exists for the period after its appearance.
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
- The Esri picture in `hires.png` was taken on 2024-05-08 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2024-09-19 to 2025-09-19: scenes S2A_18TUR_20241019_0_L2A, S2B_18TUR_20241113_0_L2A, S2C_18TUR_20250815_0_L2A, S2B_18TUR_20250919_0_L2A
- Sentinel-2 `after` composite, window 2025-10-04 to 2026-10-04: scenes S2A_18TUR_20251016_0_L2A, S2B_18TUR_20260417_0_L2A, S2B_18TUR_20260517_0_L2A, S2B_18TUR_20260924_0_L2A
- Sentinel-2 `context` composite, window 2025-10-04 to 2026-10-04: scenes S2A_18TUR_20251016_0_L2A, S2B_18TUR_20260417_0_L2A, S2B_18TUR_20260517_0_L2A, S2B_18TUR_20260924_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
