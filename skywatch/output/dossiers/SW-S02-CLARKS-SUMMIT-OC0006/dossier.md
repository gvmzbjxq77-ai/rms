# Dossier: candidate SW-S02-CLARKS-SUMMIT-OC0006

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2679 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 41.48103 N, -75.70765 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -75.70838, 41.48050, -75.70693, 41.48157; centre 41.48103, -75.70765
- Area: 1,600 m2
- Search region: `S02-CLARKS-SUMMIT`

## When
The feature is absent in imagery up to 2019-04-16 and present from 2020-03-01. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2020
- step_snr: 6.697
- d_brightness: -0.01309
- d_ndvi: -0.07843
- d_nbr: 0.06739
- d_swir: -0.1959
- persistence_years: 7
- recovery_fraction: 0
- crowding: 0.000307
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-03-17", "2018-04-21"], "2019": ["2019-03-17", "2019-04-16"], "2020": ["2020-03-01", "2020-03-21", "2020-03-26"], "2021": ["2021-03-11", "2021-03-21", "2021-04-05"], "2022": ["2022-03-16", "2022-03-21", "2022-04-05"], "2023": ["2023-03-21", "2023-03-26", "2023-04-10"], "2024": ["20...
- scene_ids_before: ["S2A_18TVL_20190317_0_L2A", "S2A_18TVL_20190416_1_L2A", "S2A_18TVM_20190416_1_L2A"]
- scene_ids_after: ["S2A_18TVL_20200301_1_L2A", "S2A_18TVL_20200321_0_L2A", "S2A_18TVM_20200321_1_L2A", "S2B_18TVM_20200326_0_L2A"]
- res_m: 20
- regional_siblings: {"count": 0, "compared": 84, "year": 2020, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- weak: False
- series: time series with 25 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: ndvi
- series_mode: absolute
- series_shift: -0.6819
- series_noise: 0.1575
- onset_note: series is not a single clean transition
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
- before: brightness 0.0756 / 0.0674; ndvi 0.5967 / 0.553; nbr 0.3268 / 0.3333
- after: brightness 0.1246 / 0.0526; ndvi 0.2819 / 0.6118; nbr 0.0856 / 0.4042

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Wallops Flight Facility (launch_site), 401 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly tree (64%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map postdates the onset, so it may show the change itself. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 121 m of the footprint (4945 tagged features in the extract; nearest road or track 0 m; nearest building 158 m; nearest candidate cause power=line at 153 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (324 item(s) within 10.0 km; nearest: Healthy Northeast Pennsylvania Initiative (Q30289873, other) at 0.41 km; Summit Lake Dam (Q49000821, dam_or_reservoir) at 0.81 km; Myers - Meyers Cemetery (Q117557412, other) at 0.81 km); nearest causal item beyond the limit: Summit Lake Dam (Q49000821, dam_or_reservoir) at 0.81 km Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2019-03-17 to 2020-03-31; nearest record in the window: NTSB GAA19CA361: Quicksilver Aircraft Northeast Sport, Ledgedale, PA (USA) at 32.9 km. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2020-03-01 (nearest record: Bald Eagle (Found, 1891) at 114.1 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 0 m away; a mapped building is 158 m away; 18.7% of the land within 1.5 km is built-up Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran but was INCONCLUSIVE. persistent artificial light at the site (human activity): Persistent artificial light IS present within 1500 m of the candidate: peak radiance 36.965 against background 1.573 nW/cm2/sr, lit in 12 of 12 monthly composites (202407 to 202506, 83 cloud-free nights). This indicates ongoing human activity or combustion at or near the site; it does not say what the feature is. Before the onset (201810 to 201903) persistent light was already present (radiance 32.185, background 1.525 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. the scene-by-scene record is not a single transition Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran but was INCONCLUSIVE. the scene-by-scene record is not a single transition Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (3 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 84 other yearly candidates in this region changed the same way in 2020 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 10 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 10 of 10 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 2 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2018-03-12 and 2020-03-16 within 85 m of the candidate (burned area: 25/25 monthly files read for 7 pixels; active fire: 188 eight-day files read (0 incomplete); 736/736 days covered, clear view on 579). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.067). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): ran and did not explain the feature. 5 unverified report(s) within 30 km inside 2019-04-09..2020-03-08; about 2.73 expected by chance from the local reporting rate; sources covering here: nuforc Source: NUFORC public copies; GEIPAN.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.08) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2020-03-01 (nearest record: Bald Eagle (Found, 1891) at 114.1 km)
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
- The Esri picture in `hires.png` was taken on 2025-06-24 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2018-04-16 to 2019-04-16: scenes S2A_18TVL_20180501_0_L2A, S2A_18TVM_20180501_0_L2A, S2A_18TVL_20180630_1_L2A, S2A_18TVM_20180630_1_L2A, S2A_18TVL_20180710_0_L2A, S2A_18TVM_20180710_0_L2A, S2A_18TVL_20190416_1_L2A, S2A_18TVM_20190416_1_L2A
- Sentinel-2 `after` composite, window 2020-03-01 to 2021-03-01: scenes S2A_18TVL_20200609_1_L2A, S2A_18TVM_20200609_1_L2A, S2B_18TVL_20200922_1_L2A, S2B_18TVM_20200922_1_L2A, S2A_18TVL_20201017_1_L2A, S2A_18TVM_20201017_1_L2A, S2A_18TVL_20201106_1_L2A, S2A_18TVM_20201106_1_L2A
- Sentinel-2 `context` composite, window 2020-03-01 to 2021-03-01: scenes S2A_18TVL_20200609_1_L2A, S2A_18TVM_20200609_1_L2A, S2B_18TVL_20200922_1_L2A, S2B_18TVM_20200922_1_L2A, S2A_18TVL_20201017_1_L2A, S2A_18TVM_20201017_1_L2A, S2A_18TVL_20201106_1_L2A, S2A_18TVM_20201106_1_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
