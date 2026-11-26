# Dossier: candidate SW-C02-OWEINAT-OC0012

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.3463 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 22.62725 N, 28.63471 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 28.63413, 22.62671, 28.63529, 22.62780; centre 22.62725, 28.63471
- Area: 1,600 m2
- Search region: `C02-OWEINAT`

## When
The feature is absent in imagery up to 2022-12-27 and present from 2023-02-05. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2023
- step_snr: 8.658
- d_brightness: -0.07316
- d_ndvi: -0.007301
- d_nbr: 0.02099
- d_swir: -0.1532
- persistence_years: 3
- recovery_fraction: 0
- crowding: 0.0007017
- n_valid_years: 8
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
- composite_dates: {"2018": ["2019-01-14", "2019-01-17", "2019-01-19"], "2019": ["2020-01-07", "2020-01-19", "2020-01-22"], "2020": ["2021-01-08", "2021-01-11", "2021-01-21"], "2021": ["2022-01-16", "2022-01-18", "2022-01-21"], "2022": ["2023-01-11", "2023-01-13", "2023-01-18"], "2023": ["2024-01-11", "2024-01-16",...
- scene_ids_before: ["S2A_35QPE_20230113_0_L2A", "S2A_35QPF_20230113_0_L2A", "S2B_35QPF_20230111_0_L2A", "S2B_35QPE_20230111_0_L2A", "S2B_35QPF_20230118_0_L2A", "S2B_35QPE_20230118_0_L2A"]
- scene_ids_after: ["S2B_35QPF_20240116_0_L2A", "S2B_35QPE_20240116_0_L2A", "S2A_35QPF_20240111_0_L2A", "S2A_35QPE_20240111_0_L2A", "S2A_35QPF_20240118_0_L2A", "S2A_35QPE_20240118_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 28 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_mode: contrast
- series_shift: -0.05291
- series_noise: 0.005496
- onset_window_days: 40
- onset_flips: 1
- landsat: {"status": "not_run", "reason": "footprint radius 23 m is below one Landsat pixel"}
- sar: {"status": "not_run", "reason": "footprint radius 23 m is under two radar pixels"}
- regional_siblings: {"count": 1, "compared": 119, "year": 2023, "ids": ["SW-C02-OWEINAT-OC0005"], "spread_km": 10.4, "min_cosine": 0.9, "magnitude_ratio": 2.0}
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
- before: brightness 0.2941 / 0.2067; ndvi 0.082 / 0.3747; nbr -0.0304 / 0.2427
- after: brightness 0.2868 / 0.2202; ndvi 0.0849 / 0.2926; nbr -0.0285 / 0.1749

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Palmachim launch and test site (launch_site), 1186 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (96%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 121 m of the footprint (63 tagged features in the extract; nearest road or track 112 m; nearest candidate cause landuse=farmland at 126 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (1 item(s) within 10.0 km; nearest: Sharq Al-Owainat (Q7490458, other) at 8.94 km) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2022-11-27 to 2023-03-07; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2023-02-05 (nearest record: Gebel Kamil (Found, 2009) at 270.6 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 112 m away; 42% of the land within 1.5 km is cropland Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 1.17 against background 0.41 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 174 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202204 to 202211) persistent light was absent (radiance 0.44, background 0.375 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (0 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 10 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 10 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 8 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.1% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2021-11-22 and 2023-02-20 within 85 m of the candidate (burned area: 16/16 monthly files read for 7 pixels; active fire: 113 eight-day files read (0 incomplete); 448/456 days covered, clear view on 446). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.021). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 1 of 119 other yearly candidates in this region changed the same way in 2023 (spectral direction within cosine 0.9, size within 2.0x), spread over 10.4 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.02) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2023-02-05 (nearest record: Gebel Kamil (Found, 2009) at 270.6 km)
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
- The Esri picture in `hires.png` was taken on 2025-06-01 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2021-12-27 to 2022-12-27: scenes S2A_35QPF_20211229_1_L2A, S2A_35QPF_20220131_0_L2A, S2A_35QPF_20220210_0_L2A, S2A_35QPF_20220220_0_L2A
- Sentinel-2 `after` composite, window 2023-02-05 to 2024-02-05: scenes S2B_35QPF_20230220_0_L2A, S2A_35QPF_20230225_0_L2A, S2A_35QPF_20230317_0_L2A, S2B_35QPF_20230401_0_L2A
- Sentinel-2 `context` composite, window 2023-02-05 to 2024-02-05: scenes S2B_35QPE_20230220_0_L2A, S2B_35QPF_20230220_0_L2A, S2A_35QPE_20230225_0_L2A, S2A_35QPF_20230225_0_L2A, S2A_35QPE_20230317_0_L2A, S2A_35QPF_20230317_0_L2A, S2B_35QPE_20230418_0_L2A, S2B_35QPF_20230418_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
