# Dossier: candidate SW-B19-PUNA-OC0012

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.3088 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: -25.10724 N, -67.64098 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -67.64165, -25.10785, -67.64025, -25.10660; centre -25.10722, -67.64095
- Area: 3,200 m2
- Search region: `B19-PUNA`

## When
The feature is absent in imagery up to 2022-05-05 and present from 2022-06-07. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: step
- break_year: 2023
- step_snr: 7.719
- d_brightness: 0.04869
- d_ndvi: -0.003596
- d_nbr: 0.02853
- d_swir: 0.05764
- persistence_years: 4
- recovery_fraction: 0.3289
- crowding: 0.0002193
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-05-09", "2018-05-29", "2018-06-03"], "2019": ["2019-05-01", "2019-05-06", "2019-05-16"], "2020": ["2020-05-05", "2020-05-08", "2020-05-10"], "2021": ["2021-05-05", "2021-05-08", "2021-05-10"], "2022": ["2022-04-30", "2022-05-05", "2022-05-10"], "2023": ["2023-05-08", "2023-05-10",...
- scene_ids_before: ["S2A_19JFM_20220430_0_L2A", "S2A_19JFN_20220430_0_L2A", "S2B_19JFM_20220505_0_L2A", "S2B_19JFN_20220505_0_L2A", "S2A_19JFM_20220510_0_L2A", "S2A_19JFN_20220510_0_L2A"]
- scene_ids_after: ["S2A_19JFM_20230508_0_L2A", "S2A_19JFN_20230508_0_L2A", "S2B_19JFM_20230510_0_L2A", "S2B_19JFN_20230510_0_L2A", "S2A_19JFM_20230515_0_L2A", "S2A_19JFN_20230515_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 32 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_mode: contrast
- series_shift: 0.04848
- series_noise: 0.01079
- onset_window_days: 33
- onset_flips: 1
- landsat: {"status": "ok", "before": [{"date": "2021-04-11", "scene_id": "LC08_L2SP_232077_20210411_02_T1", "brightness": -0.0037395358085632324, "ndvi": -0.0016901344060897827, "nbr": -0.0007763542234897614, "kelvin": -0.364959716796875}, {"date": "2021-09-02", "scene_id": "LC08_L2SP_232078_20210902_02_T1...
- sar: {"status": "not_run", "reason": "footprint radius 32 m is under two radar pixels"}
- regional_siblings: {"count": 1, "compared": 119, "year": 2023, "ids": ["SW-B19-PUNA-OC0071"], "spread_km": 14.6, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 3,200
- shape.perimeter_m: 148.3
- shape.equivalent_diameter_m: 63.83
- shape.major_axis_m: 69.28
- shape.minor_axis_m: 54.77
- shape.elongation: 1.265
- shape.orientation_deg: 135
- shape.circularity: 1
- shape.solidity: 1
- shape.eccentricity: 0.6124
- shape.rectangularity: 0.8889
- shape.n_corners: 4
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 1

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1345 / 0.177; ndvi 0.0439 / 0.0802; nbr 0.0258 / 0.0977
- after: brightness 0.1479 / 0.1673; ndvi 0.0416 / 0.0681; nbr 0.036 / 0.0915

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Alcantara Launch Center (launch_site), 3544 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 141 m of the footprint (19 tagged features in the extract; nearest road or track 0 m; nearest candidate cause landuse=industrial at 2049 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (2 item(s) within 10.0 km; nearest: Vega Chachi (Q21844540, other) at 2.58 km; Vega Aras (Q21845724, other) at 6.03 km) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2022-04-05 to 2022-07-07; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-06-07 (nearest record: Aguas Calientes (Found, 1971) at 87.9 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 0 m away Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.44 against background 0.345 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 168 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202111 to 202204) persistent light was absent (radiance 0.435, background 0.335 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
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
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2021-03-31 and 2022-06-22 within 99 m of the candidate (burned area: 16/16 monthly files read for 5 pixels; active fire: 113 eight-day files read (0 incomplete); 449/449 days covered, clear view on 446). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.049); NBR rose (+0.029). Recovery fraction 0.33: gradual recovery, as vegetation regrowth after fire would give Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 1 of 119 other yearly candidates in this region changed the same way in 2023 (spectral direction within cosine 0.9, size within 2.0x), spread over 14.6 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.03) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-06-07 (nearest record: Aguas Calientes (Found, 1971) at 87.9 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: human_context, natural:surface_water, natural_process (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2023-07-21 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2021-05-05 to 2022-05-05: scenes S2A_19JFN_20210505_1_L2A, S2B_19JFN_20210510_1_L2A, S2B_19JFN_20220204_0_L2A, S2B_19JFN_20220306_0_L2A
- Sentinel-2 `after` composite, window 2022-06-07 to 2023-06-07: scenes S2B_19JFN_20230510_0_L2A, S2A_19JFN_20230525_0_L2A, S2B_19JFN_20230530_0_L2A, S2A_19JFN_20230604_0_L2A
- Sentinel-2 `context` composite, window 2022-06-07 to 2023-06-07: scenes S2B_19JFN_20230510_0_L2A, S2A_19JFN_20230525_0_L2A, S2B_19JFN_20230530_0_L2A, S2A_19JFN_20230604_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
