# Dossier: candidate SW-C09-SERIRTIBESTI-OC0003

## What was detected
The detector `optical_change` flagged a surface anomaly of unclassified kind (signature class `unknown`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2487 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 24.34198 N, 17.51581 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 17.51523, 24.34143, 17.51639, 24.34253; centre 24.34198, 17.51581
- Area: 1,600 m2
- Search region: `C09-SERIRTIBESTI`

## When
The feature is absent in imagery up to 2021-11-04 and present from 2022-10-20. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2022
- step_snr: 6.217
- d_brightness: -0.01955
- d_ndvi: 0.0004694
- d_nbr: 0.01663
- d_swir: -0.04822
- persistence_years: 5
- recovery_fraction: 0.2329
- crowding: 0.0004386
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-10-21", "2018-10-31", "2018-11-05"], "2019": ["2019-10-26", "2019-10-31", "2019-11-05"], "2020": ["2020-10-20", "2020-10-25", "2020-10-30"], "2021": ["2021-10-15", "2021-10-25", "2021-11-04"], "2022": ["2022-10-20", "2022-10-30", "2022-11-04"], "2023": ["2023-10-25", "2023-10-30",...
- scene_ids_before: ["S2A_33QYG_20211104_1_L2A", "S2A_33RYH_20211104_1_L2A", "S2A_33QYG_20211025_1_L2A", "S2A_33RYH_20211025_1_L2A", "S2A_33RYH_20211015_1_L2A", "S2A_33QYG_20211015_1_L2A"]
- scene_ids_after: ["S2A_33QYG_20221030_0_L2A", "S2A_33RYH_20221030_0_L2A", "S2B_33QYG_20221104_0_L2A", "S2B_33RYH_20221104_0_L2A", "S2A_33QYG_20221020_0_L2A", "S2A_33RYH_20221020_0_L2A"]
- res_m: 20
- weak: True
- series: time series with 30 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_shift: -0.02312
- series_noise: 0.01317
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "not_run", "reason": "footprint radius 23 m is below one Landsat pixel"}
- sar: {"status": "not_run", "reason": "footprint radius 23 m is under two radar pixels"}
- regional_siblings: {"count": 6, "compared": 119, "year": 2022, "ids": ["SW-C09-SERIRTIBESTI-OC0002", "SW-C09-SERIRTIBESTI-OC0106", "SW-C09-SERIRTIBESTI-OC0102", "SW-C09-SERIRTIBESTI-OC0109", "SW-C09-SERIRTIBESTI-OC0108", "SW-C09-SERIRTIBESTI-OC0112"], "spread_km": 43.6, "min_cosine": 0.9, "magnitude_ratio": 2.0}
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
- before: brightness 0.3302 / 0.3244; ndvi 0.0658 / 0.0668; nbr -0.0714 / -0.0772
- after: brightness 0.3121 / 0.3132; ndvi 0.0633 / 0.0681; nbr -0.057 / -0.0653

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is In Ekker nuclear test site (Taourirt Tan Afella) (test_range), 1254 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; onset is undated or straddles 2021, so the map may show either state. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 3019 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2021-10-05 to 2022-11-19; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-10-20 (nearest record: Sarir Tibesti 001 (Found, 1994) at 91.2 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.455 against background 0.38 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 164 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202104 to 202110) persistent light was absent (radiance 0.355, background 0.285 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): EXPLAINS the feature (a sufficient conventional cause was found). regional pattern: 6 of 119 other yearly candidates in this region changed the same way in 2022 (spectral direction within cosine 0.9, size within 2.0x), spread over 43.6 km; a change that recurs across a region is a regional process (rain, greening, blown sand, moisture or the sensor), not a local event Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (1 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 8 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 8 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2020-09-30 and 2022-11-04 within 85 m of the candidate (burned area: 27/27 monthly files read for 4 pixels; active fire: 192 eight-day files read (0 incomplete); 766/766 days covered, clear view on 760). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR change +0.017 is too small for a burn. Recovery fraction 0.23: gradual recovery, as vegetation regrowth after fire would give Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): EXPLAINS the feature (a sufficient conventional cause was found). regional pattern: 6 of 119 other yearly candidates in this region changed the same way in 2022 (spectral direction within cosine 0.9, size within 2.0x), spread over 43.6 km; a change that recurs across a region is a regional process (rain, greening, blown sand, moisture or the sensor), not a local event Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-10-20 (nearest record: Sarir Tibesti 001 (Found, 1994) at 91.2 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T0**: explained by a conventional cause.

Reason: explained by: natural:regional_pattern, natural_process (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2025-04-14 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2020-11-04 to 2021-11-04: scenes S2A_33QYG_20201129_1_L2A, S2A_33RYH_20201129_1_L2A, S2A_33QYG_20201209_1_L2A, S2A_33RYH_20201209_1_L2A, S2A_33QYG_20210508_1_L2A, S2A_33RYH_20210508_1_L2A, S2A_33QYG_20210826_1_L2A, S2A_33RYH_20210826_1_L2A
- Sentinel-2 `after` composite, window 2022-10-20 to 2023-10-20: scenes S2A_33QYG_20230118_0_L2A, S2A_33RYH_20230118_0_L2A, S2A_33QYG_20230309_0_L2A, S2A_33RYH_20230309_0_L2A, S2B_33QYG_20230821_1_L2A, S2B_33RYH_20230821_0_L2A, S2B_33QYG_20230920_0_L2A, S2B_33RYH_20230920_0_L2A
- Sentinel-2 `context` composite, window 2022-10-20 to 2023-10-20: scenes S2A_33QYG_20230118_0_L2A, S2A_33RYH_20230118_0_L2A, S2A_33QYG_20230309_0_L2A, S2A_33RYH_20230309_0_L2A, S2B_33QYG_20230821_1_L2A, S2B_33RYH_20230821_0_L2A, S2B_33QYG_20230920_0_L2A, S2B_33RYH_20230920_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
