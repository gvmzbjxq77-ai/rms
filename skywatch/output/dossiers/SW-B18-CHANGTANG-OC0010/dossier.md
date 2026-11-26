# Dossier: candidate SW-B18-CHANGTANG-OC0010

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.3409 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 35.06507 N, 85.97413 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 85.97346, 35.06453, 85.97479, 35.06560; centre 35.06507, 85.97413
- Area: 1,600 m2
- Search region: `B18-CHANGTANG`

## When
The feature is absent in imagery up to 2020-09-22 and present from 2021-09-17. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2021
- step_snr: 8.523
- d_brightness: -0.02362
- d_ndvi: -0.3563
- d_nbr: -0.07575
- d_swir: -0.08584
- persistence_years: 6
- recovery_fraction: 0.2579
- crowding: 4.386e-05
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-08-29", "2018-09-28", "2018-10-03"], "2019": ["2019-09-08", "2019-09-13", "2019-09-23"], "2020": ["2020-09-12", "2020-09-17", "2020-09-22"], "2021": ["2021-09-17", "2021-09-22", "2021-09-27"], "2022": ["2022-09-02", "2022-09-07", "2022-10-07"], "2023": ["2023-09-12", "2023-09-27",...
- scene_ids_before: ["S2A_45SUU_20200912_1_L2A", "S2A_45SUV_20200912_1_L2A", "S2A_45SVU_20200912_1_L2A", "S2A_45SVV_20200912_0_L2A", "S2B_45SUU_20200917_1_L2A", "S2B_45SUV_20200917_1_L2A", "S2B_45SVU_20200917_1_L2A", "S2B_45SVV_20200917_1_L2A", "S2A_45SUU_20200922_1_L2A", "S2A_45SUV_20200922_1_L2A", "S2A_45SVU_20200...
- scene_ids_after: ["S2A_45SUU_20210917_2_L2A", "S2A_45SVU_20210917_1_L2A", "S2B_45SUV_20210922_1_L2A", "S2B_45SVV_20210922_1_L2A", "S2A_45SUU_20210927_1_L2A", "S2A_45SUV_20210927_1_L2A", "S2A_45SVU_20210927_1_L2A", "S2A_45SVV_20210927_1_L2A"]
- res_m: 20
- weak: False
- series: time series with 29 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: ndvi
- series_shift: -0.05302
- series_noise: 0.0337
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "not_run", "reason": "footprint radius 23 m is below one Landsat pixel"}
- sar: {"status": "not_run", "reason": "footprint radius 23 m is under two radar pixels"}
- regional_siblings: {"count": 3, "compared": 119, "year": 2021, "ids": ["SW-B18-CHANGTANG-OC0024", "SW-B18-CHANGTANG-OC0036", "SW-B18-CHANGTANG-OC0029"], "spread_km": 21.3, "min_cosine": 0.9, "magnitude_ratio": 2.0}
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
- before: brightness 0.219 / 0.2239; ndvi 0.0553 / 0.0677; nbr 0.0209 / -0.0108
- after: brightness 0.1882 / 0.2108; ndvi 0.0119 / 0.0702; nbr -0.0051 / -0.0546

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Lop Nur test site, atmospheric test area (test_range), 680 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (96%); cropland 0%, built-up 0%, water/wetland 4%; the 2021 map postdates the onset, so it may show the change itself. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 121 m of the footprint (2 tagged features in the extract; no road or track within 3028 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2020-08-23 to 2021-10-17; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2021-09-17 (nearest record: Alaer 001 (Found, 2007) at 718.0 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.565 against background 0.445 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 108 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202003 to 202008) persistent light was absent (radiance 0.395, background 0.315 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. possible regional pattern: 3 of 119 other yearly candidates in this region changed the same way in 2021 (spectral direction within cosine 0.9, size within 2.0x), spread over 21.3 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (1 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. permafrost region but no water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. 3 of 11 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran but was INCONCLUSIVE. 3 of 11 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2019-08-19 and 2021-10-02 within 85 m of the candidate (burned area: 27/27 monthly files read for 8 pixels; active fire: 198 eight-day files read (0 incomplete); 776/776 days covered, clear view on 588). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR dropped only -0.076. Recovery fraction 0.26: gradual recovery, as vegetation regrowth after fire would give Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran but was INCONCLUSIVE. possible regional pattern: 3 of 119 other yearly candidates in this region changed the same way in 2021 (spectral direction within cosine 0.9, size within 2.0x), spread over 21.3 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.36) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2021-09-17 (nearest record: Alaer 001 (Found, 2007) at 718.0 km)
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
- The Esri picture in `hires.png` was taken on 2025-09-16 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2019-09-23 to 2020-09-22: scenes S2B_45SUU_20191013_1_L2A, S2B_45SVU_20191013_1_L2A, S2A_45SUU_20191207_1_L2A, S2A_45SVU_20191207_1_L2A, S2A_45SUU_20191227_1_L2A, S2A_45SVU_20191227_1_L2A, S2A_45SUU_20200724_1_L2A, S2A_45SVU_20200724_1_L2A
- Sentinel-2 `after` composite, window 2021-09-17 to 2022-09-17: scenes S2A_45SUU_20210927_1_L2A, S2A_45SVU_20210927_1_L2A, S2A_45SUU_20211007_1_L2A, S2A_45SVU_20211007_1_L2A, S2A_45SUU_20211017_1_L2A, S2A_45SVU_20211017_1_L2A, S2A_45SUU_20220724_1_L2A, S2A_45SVU_20220724_1_L2A
- Sentinel-2 `context` composite, window 2021-09-17 to 2022-09-17: scenes S2A_45SUU_20210927_1_L2A, S2A_45SVU_20210927_1_L2A, S2A_45SUU_20211007_1_L2A, S2A_45SVU_20211007_1_L2A, S2A_45SUU_20211017_1_L2A, S2A_45SVU_20211017_1_L2A, S2A_45SUU_20220724_1_L2A, S2A_45SVU_20220724_1_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
