# Dossier: candidate SW-B13-MAPIMI-OC0005

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2664 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 26.81852 N, -103.62940 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -103.63009, 26.81770, -103.62870, 26.81934; centre 26.81852, -103.62940
- Area: 4,400 m2
- Search region: `B13-MAPIMI`

## When
The feature is absent in imagery up to 2021-04-25 and present from 2022-04-22. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: step
- break_year: 2022
- step_snr: 6.66
- d_brightness: 0.04518
- d_ndvi: -0.2154
- d_nbr: -0.2016
- d_swir: 0.07366
- persistence_years: 5
- recovery_fraction: 0
- crowding: 0.0005263
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-04-16", "2018-04-18", "2018-05-01"], "2019": ["2019-04-18", "2019-04-21", "2019-04-26"], "2020": ["2020-04-20", "2020-04-27", "2020-04-30"], "2021": ["2021-04-12", "2021-04-20", "2021-04-25"], "2022": ["2022-04-22", "2022-04-25", "2022-04-27"], "2023": ["2023-04-17", "2023-04-25",...
- scene_ids_before: ["S2A_13RFK_20210412_1_L2A", "S2B_13RFK_20210420_2_L2A", "S2A_13RFK_20210425_1_L2A"]
- scene_ids_after: ["S2B_13RFK_20220422_0_L2A", "S2B_13RFK_20220425_0_L2A", "S2A_13RFK_20220427_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 31 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: ndvi
- series_shift: -0.1395
- series_noise: 0.1101
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "ok", "before": [{"date": "2020-04-01", "scene_id": "LC08_L2SP_030041_20200401_02_T1", "brightness": -0.04601479321718216, "ndvi": 0.10151460766792297, "nbr": 0.06770288199186325, "kelvin": -1.09747314453125}, {"date": "2020-08-07", "scene_id": "LC08_L2SP_030041_20200807_02_T1", "brigh...
- sar: {"status": "not_run", "reason": "footprint radius 37 m is under two radar pixels"}
- regional_siblings: {"count": 2, "compared": 75, "year": 2022, "ids": ["SW-B13-MAPIMI-OC0001", "SW-B13-MAPIMI-OC0004"], "spread_km": 4.7, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 4,400
- shape.perimeter_m: 168.3
- shape.equivalent_diameter_m: 74.85
- shape.major_axis_m: 113.7
- shape.minor_axis_m: 46.9
- shape.elongation: 2.424
- shape.orientation_deg: 110.3
- shape.circularity: 1
- shape.solidity: 0.8462
- shape.eccentricity: 0.911
- shape.rectangularity: 0.7333
- shape.n_corners: 4
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 0.8462

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1212 / 0.1734; ndvi 0.3165 / 0.2004; nbr 0.1551 / 0.0839
- after: brightness 0.1284 / 0.1924; ndvi 0.2248 / 0.1355; nbr 0.016 / 0.0032

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is SpaceX Starbase, Boca Chica (launch_site), 648 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly shrub (81%); cropland 0%, built-up 0%, water/wetland 0%; onset is undated or straddles 2021, so the map may show either state. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 2928 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (7 item(s) within 10.0 km; nearest: Colonia Ganadera Constitución (Q49974211, settlement) at 1.14 km; Q55559277 (Q55559277, other) at 6.92 km; Q55553535 (Q55553535, other) at 6.95 km) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2021-03-26 to 2022-05-22; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-04-22 (nearest record: La Esmeralda (Found, 1999) at 33.8 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.45 against background 0.38 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 130 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202010 to 202103) persistent light was absent (radiance 0.38, background 0.315 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying); possible regional pattern: 2 of 75 other yearly candidates in this region changed the same way in 2022 (spectral direction within cosine 0.9, size within 2.0x), spread over 4.7 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (1 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 8 of 11 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 8 of 11 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.1% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2020-03-21 and 2022-05-07 within 114 m of the candidate (burned area: 27/27 monthly files read for 8 pixels; active fire: 195 eight-day files read (0 incomplete); 778/778 days covered, clear view on 767). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.045). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran but was INCONCLUSIVE. possible regional pattern: 2 of 75 other yearly candidates in this region changed the same way in 2022 (spectral direction within cosine 0.9, size within 2.0x), spread over 4.7 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.22) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-04-22 (nearest record: La Esmeralda (Found, 1999) at 33.8 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: natural:regional_pattern, natural:surface_water, natural_process (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2023-04-21 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2020-04-25 to 2021-04-25: scenes S2B_13RFK_20200525_3_L2A, S2B_13RFK_20201022_1_L2A, S2B_13RFK_20201108_1_L2A, S2A_13RFK_20201203_1_L2A
- Sentinel-2 `after` composite, window 2022-04-22 to 2023-04-22: scenes S2A_13RFK_20221103_0_L2A, S2A_13RFK_20221113_0_L2A, S2A_13RFK_20221203_0_L2A, S2B_13RFK_20221228_0_L2A
- Sentinel-2 `context` composite, window 2022-04-22 to 2023-04-22: scenes S2A_13RFK_20221103_0_L2A, S2A_13RFK_20221113_0_L2A, S2A_13RFK_20221203_0_L2A, S2B_13RFK_20221228_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
