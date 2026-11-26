# Dossier: candidate SW-B13-MAPIMI-OC0011

## What was detected
The detector `optical_change` flagged a surface anomaly of unclassified kind (signature class `unknown`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.6959 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 26.76456 N, -103.78699 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -103.78942, 26.76261, -103.78484, 26.76645; centre 26.76453, -103.78713
- Area: 74,400 m2
- Search region: `B13-MAPIMI`

## When
The feature is absent in imagery up to 2019-04-26 and present from 2020-04-20. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: transient
- break_year: 2020
- step_snr: 17.4
- d_brightness: -0.02052
- d_ndvi: -0.2184
- d_nbr: 0.4765
- d_swir: -0.2247
- persistence_years: 1
- recovery_fraction: 1
- crowding: 0
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-04-16", "2018-04-18", "2018-05-01"], "2019": ["2019-04-18", "2019-04-21", "2019-04-26"], "2020": ["2020-04-20", "2020-04-27", "2020-04-30"], "2021": ["2021-04-12", "2021-04-20", "2021-04-25"], "2022": ["2022-04-22", "2022-04-25", "2022-04-27"], "2023": ["2023-04-17", "2023-04-25",...
- scene_ids_before: ["S2B_13RFK_20190418_1_L2A", "S2B_13RFK_20190421_1_L2A", "S2A_13RFK_20190426_1_L2A"]
- scene_ids_after: ["S2A_13RFK_20200420_1_L2A", "S2A_13RFK_20200427_1_L2A", "S2A_13RFK_20200430_1_L2A"]
- res_m: 20
- weak: False
- series: time series with 25 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_shift: 0.06653
- series_noise: 0.2321
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "ok", "before": [{"date": "2018-07-17", "scene_id": "LC08_L2SP_030042_20180717_02_T1", "brightness": -0.028064638376235962, "ndvi": 0.03840912878513336, "nbr": 0.05272259563207626, "kelvin": -0.85528564453125}, {"date": "2018-11-22", "scene_id": "LC08_L2SP_030041_20181122_02_T1", "brig...
- sar: {"status": "ok", "relative_orbit": 12, "orbit_state": "descending", "before": [{"date": "2018-09-03", "scene_id": "S1A_IW_GRDH_1SDV_20180903T124835_20180903T124900_023534_02900F", "contrast_db": 2.665721893310547}, {"date": "2018-11-02", "scene_id": "S1A_IW_GRDH_1SDV_20181102T124835_20181102T1249...
- regional_siblings: {"count": 0, "compared": 75, "year": 2020, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 74,400
- shape.perimeter_m: 1,126
- shape.equivalent_diameter_m: 307.8
- shape.major_axis_m: 407.8
- shape.minor_axis_m: 241.1
- shape.elongation: 1.692
- shape.orientation_deg: 141.3
- shape.circularity: 0.7378
- shape.solidity: 0.8857
- shape.eccentricity: 0.8066
- shape.rectangularity: 0.7126
- shape.n_corners: 10
- shape.straight_edge_fraction: 0.4875
- shape.hole_fraction: 0
- shape.regularity: 0.4822

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1405 / 0.1888; ndvi 0.2018 / 0.1148; nbr 0.0711 / 0.0116
- after: brightness 0.1144 / 0.1839; ndvi 0.2512 / 0.1296; nbr 0.1751 / 0.0261

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is SpaceX Starbase, Boca Chica (launch_site), 663 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly shrub (64%); cropland 2%, built-up 0%, water/wetland 0%; the 2021 map postdates the onset, so it may show the change itself. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 300 m of the footprint (38 tagged features in the extract; nearest road or track 0 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (5 item(s) within 10.0 km; nearest: Loma Prieta (Q49980579, settlement) at 4.45 km; Mesa Espinazo del Diablo (Q27784776, other) at 5.04 km; Mapimí (Q22680926, protected_area) at 8.34 km) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.2 km dated 2019-03-27 to 2020-05-20; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2020-04-20 (nearest record: Escalón (Found, 1979) at 33.6 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 0 m away Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.43 against background 0.385 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 127 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (201810 to 201903) persistent light was absent (radiance 0.29, background 0.215 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
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
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. only 1 of 3 scenes shows the short-lived change; a single-scene feature may be a residual cloud or shadow Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran but was INCONCLUSIVE. only 1 of 3 scenes shows the short-lived change; a single-scene feature may be a residual cloud or shadow Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2018-03-22 and 2020-05-05 within 312 m of the candidate (burned area: 27/27 monthly files read for 10 pixels; active fire: 196 eight-day files read (0 incomplete); 776/776 days covered, clear view on 738). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.476). Recovery fraction 1.00: fully recovered, which fits a grass fire but also a passing darkening Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 75 other yearly candidates in this region changed the same way in 2020 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.48) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2020-04-20 (nearest record: Escalón (Found, 1979) at 33.6 km)
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
- The Esri picture in `hires.png` was taken on 2023-06-07 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2018-04-26 to 2019-04-26: scenes S2A_13RFK_20190324_1_L2A, S2B_13RFK_20190329_1_L2A, S2A_13RFK_20190413_1_L2A, S2A_13RFK_20190426_1_L2A
- Sentinel-2 `after` composite, window 2020-04-20 to 2021-04-20: scenes S2B_13RFK_20200525_3_L2A, S2B_13RFK_20201022_1_L2A, S2B_13RFK_20201108_1_L2A, S2A_13RFK_20201203_1_L2A
- Sentinel-2 `context` composite, window 2020-04-20 to 2021-04-20: scenes S2B_13RFK_20200525_3_L2A, S2B_13RFK_20201022_1_L2A, S2B_13RFK_20201108_1_L2A, S2A_13RFK_20201203_1_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
