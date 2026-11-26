# Dossier: candidate SW-S01-PEYRUIS-OC0012

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2769 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 44.07124 N, 5.89463 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 5.89391, 44.07068, 5.89535, 44.07180; centre 44.07124, 5.89463
- Area: 1,600 m2
- Search region: `S01-PEYRUIS`

## When
The feature is absent in imagery up to 2021-03-30 and present from 2022-04-09. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2022
- step_snr: 6.922
- d_brightness: 0.04787
- d_ndvi: -0.2529
- d_nbr: -0.2317
- d_swir: 0.143
- persistence_years: 4
- recovery_fraction: 0.06572
- crowding: 0.0002631
- n_valid_years: 8
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2025, 2026]
- composite_dates: {"2018": ["2018-04-05", "2018-04-20", "2018-04-25"], "2019": ["2019-04-05", "2019-04-15", "2019-04-30"], "2020": ["2020-04-09", "2020-04-14", "2020-05-04"], "2021": ["2021-03-30"], "2022": ["2022-04-09", "2022-04-19", "2022-05-14"], "2023": ["2023-03-30", "2023-04-14", "2023-04-24"], "2025": ["20...
- scene_ids_before: ["S2A_31TGJ_20210330_2_L2A"]
- scene_ids_after: ["S2B_31TGJ_20220409_0_L2A", "S2B_31TGJ_20220419_0_L2A", "S2A_31TGJ_20220514_0_L2A"]
- res_m: 20
- regional_siblings: {"count": 2, "compared": 71, "year": 2022, "ids": ["SW-S01-PEYRUIS-OC0006", "SW-S01-PEYRUIS-OC0017"], "spread_km": 7.5, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- weak: False
- series: time series with 30 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: ndvi
- series_shift: -0.359
- series_noise: 0.1539
- onset_note: per-scene values do not separate before from after
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
- before: brightness 0.0376 / 0.059; ndvi 0.6779 / 0.5978; nbr 0.4117 / 0.3414
- after: brightness 0.0604 / 0.0505; ndvi 0.3826 / 0.5156; nbr 0.0515 / 0.2316

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Hammaguir launch and test site (launch_site), 1658 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly tree (100%); cropland 0%, built-up 0%, water/wetland 0%; onset is undated or straddles 2021, so the map may show either state. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 124 m of the footprint (1990 tagged features in the extract; nearest road or track 22 m; nearest building 292 m; nearest candidate cause landuse=farmland at 183 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (251 item(s) within 10.0 km; nearest: Mallefougasse-Augès (Q1018627, settlement) at 0.62 km; Église Saint-Jean-Baptiste de Mallefougasse (Q3581978, other) at 0.63 km; town hall of Mallefougasse-Augès (Q119316932, other) at 0.66 km) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2021-02-28 to 2022-05-09; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-04-09 (nearest record: Laborel (Fell, 1871) at 34.2 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 22 m away; a mapped building is 292 m away; 3% of the land within 1.5 km is cropland; 2.8% of the land within 1.5 km is built-up Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.53 against background 0.44 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 137 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202009 to 202102) persistent light was already present (radiance 2.655, background 0.49 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying); possible regional pattern: 2 of 71 other yearly candidates in this region changed the same way in 2022 (spectral direction within cosine 0.9, size within 2.0x), spread over 7.5 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (12 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:regional_pattern** (natural): ran but was INCONCLUSIVE. possible regional pattern: 2 of 71 other yearly candidates in this region changed the same way in 2022 (spectral direction within cosine 0.9, size within 2.0x), spread over 7.5 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. weak composites: 1 date(s) before, 3 after, 8 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 10 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran but was INCONCLUSIVE. weak composites: 1 date(s) before, 3 after, 8 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2020-02-24 and 2022-04-24 within 85 m of the candidate (burned area: 27/27 monthly files read for 6 pixels; active fire: 201 eight-day files read (0 incomplete); 791/791 days covered, clear view on 753). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.048). Recovery fraction 0.07: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): ran and did not explain the feature. 0 unverified report(s) within 30 km inside 2021-03-23..2022-04-16; about 0.10 expected by chance from the local reporting rate; sources covering here: geipan, nuforc Source: NUFORC public copies; GEIPAN.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.25) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-04-09 (nearest record: Laborel (Fell, 1871) at 34.2 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested

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
- The Esri picture in `hires.png` was taken on 2024-08-06 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2020-03-30 to 2021-03-30: scenes S2A_31TGJ_20200504_1_L2A, S2B_31TGJ_20200807_1_L2A, S2A_31TGJ_20201120_1_L2A, S2A_31TGJ_20210330_2_L2A
- Sentinel-2 `after` composite, window 2022-04-09 to 2023-04-09: scenes S2A_31TGJ_20221130_0_L2A, S2A_31TGJ_20230129_0_L2A, S2B_31TGJ_20230203_0_L2A, S2B_31TGJ_20230213_0_L2A
- Sentinel-2 `context` composite, window 2022-04-09 to 2023-04-09: scenes S2A_31TGJ_20221130_0_L2A, S2A_31TGJ_20230129_0_L2A, S2B_31TGJ_20230203_0_L2A, S2B_31TGJ_20230213_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
