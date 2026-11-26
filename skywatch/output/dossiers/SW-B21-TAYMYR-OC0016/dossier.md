# Dossier: candidate SW-B21-TAYMYR-OC0016

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.4277 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 74.61865 N, 98.53905 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 98.53590, 74.61801, 98.54202, 74.61925; centre 74.61863, 98.53896
- Area: 5,600 m2
- Search region: `B21-TAYMYR`

## When
The feature is absent in imagery up to 2023-08-03 and present from 2024-07-29. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: transient
- break_year: 2024
- step_snr: 10.69
- d_brightness: 0.2628
- d_ndvi: -0.4767
- d_nbr: -0.3862
- d_swir: 0.3224
- persistence_years: 1
- recovery_fraction: 1
- crowding: 0.0003947
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-08-09", "2018-08-25"], "2019": ["2019-07-17", "2019-07-18", "2019-08-12"], "2020": ["2020-08-14", "2020-08-15"], "2021": ["2021-08-02", "2021-08-05"], "2022": ["2022-07-11", "2022-08-13"], "2023": ["2023-07-28", "2023-08-03"], "2024": ["2024-07-29"], "2025": ["2025-08-06", "2025-0...
- scene_ids_before: ["S2B_47XMC_20230728_0_L2A", "S2A_47XMC_20230803_1_L2A"]
- scene_ids_after: ["S2B_47XMC_20240729_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 26 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_shift: -0.000403
- series_noise: 0.2158
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "ok", "before": [{"date": "2022-07-11", "scene_id": "LC09_L2SP_152007_20220711_02_T1", "brightness": 0.0007311403751373291, "ndvi": 0.007469445466995239, "nbr": -0.02590121328830719, "kelvin": null}, {"date": "2023-07-29", "scene_id": "LC08_L2SP_153007_20230729_02_T1", "brightness": 0....
- sar: {"status": "not_run", "reason": "no relative orbit covers both periods (0 scenes before, 0 after)"}
- regional_siblings: {"count": 0, "compared": 119, "year": 2024, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 5,600
- shape.perimeter_m: 228.3
- shape.equivalent_diameter_m: 84.44
- shape.major_axis_m: 109
- shape.minor_axis_m: 62.92
- shape.elongation: 1.732
- shape.orientation_deg: 172.8
- shape.circularity: 1
- shape.solidity: 1
- shape.eccentricity: 0.8165
- shape.rectangularity: 0.9333
- shape.n_corners: 4
- shape.straight_edge_fraction: 0.3368
- shape.hole_fraction: 0
- shape.regularity: 1

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.0565 / 0.0615; ndvi 0.5321 / 0.4403; nbr 0.2362 / 0.1066
- after: brightness 0.0629 / 0.0628; ndvi 0.5137 / 0.4373; nbr 0.2378 / 0.1263

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Novaya Zemlya test site, Sukhoy Nos (zone C) (test_range), 1249 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly moss (55%); cropland 0%, built-up 0%, water/wetland 1%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 181 m of the footprint (4 tagged features in the extract; no road or track within 3080 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2023-07-04 to 2024-08-28; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-07-29 (nearest record: Zhigansk (Found, 1966) at 1269.0 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 1.65 against background 1.29 nW/cm2/sr, lit in 1 of 7 monthly composites (202408 to 202506, 118 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. The months before the onset could not be measured. Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (6 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. permafrost region but no water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. only 1 of 4 scenes shows the short-lived change; a single-scene feature may be a residual cloud or shadow; weak composites: 2 date(s) before, 1 after, 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran but was INCONCLUSIVE. only 1 of 4 scenes shows the short-lived change; a single-scene feature may be a residual cloud or shadow Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran but was INCONCLUSIVE. weak composites: 2 date(s) before, 1 after, 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): NOT RUN. no MODIS fire product could be read (burned area: 0/27 monthly files read for 9 pixels; no file for 2022-06, 2022-07, 2022-08, 2022-09, 2022-10, 2022-11; active fire: 0 eight-day files read (0 incomplete); 0/777 days covered, clear view on 0). Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.263). Recovery fraction 1.00: fully recovered, which fits a grass fire but also a passing darkening Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 119 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.48) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-07-29 (nearest record: Zhigansk (Found, 1966) at 1269.0 km)
- **fire_history** (mandatory): no MODIS fire product could be read (burned area: 0/27 monthly files read for 9 pixels; no file for 2022-06, 2022-07, 2022-08, 2022-09, 2022-10, 2022-11; active fire: 0 eight-day files read (0 incomplete); 0/777 days covered, clear view on 0).
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
- The Esri picture in `hires.png` was taken on 2025-07-04 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2022-08-03 to 2023-08-03: scenes S2A_47XMC_20230726_1_L2A, S2B_47XMC_20230728_0_L2A, S2B_47XMC_20230729_0_L2A, S2A_47XMC_20230803_1_L2A
- Sentinel-2 `after` composite, window 2024-07-29 to 2025-07-29: scenes S2A_47XMC_20240813_0_L2A, S2B_47XMC_20240814_0_L2A, S2B_47XMC_20240815_0_L2A, S2C_47XMC_20250709_0_L2A
- Sentinel-2 `context` composite, window 2024-07-29 to 2025-07-29: scenes S2A_47XMC_20240813_0_L2A, S2B_47XMC_20240814_0_L2A, S2B_47XMC_20240815_0_L2A, S2C_47XMC_20250709_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
