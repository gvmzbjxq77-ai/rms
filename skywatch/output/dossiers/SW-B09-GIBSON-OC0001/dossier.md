# Dossier: candidate SW-B09-GIBSON-OC0001

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2684 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: -24.53938 N, 126.18319 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 126.18251, -24.53993, 126.18387, -24.53882; centre -24.53938, 126.18319
- Area: 2,400 m2
- Search region: `B09-GIBSON`

## When
The feature is absent in imagery up to 2023-03-05 and present from 2023-04-29. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2023
- step_snr: 6.711
- d_brightness: 0.02763
- d_ndvi: -0.02371
- d_nbr: -0.03225
- d_swir: 0.0988
- persistence_years: 4
- recovery_fraction: 0
- crowding: 0.0004386
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-27", "2018-07-29", "2018-08-03"], "2019": ["2019-07-27", "2019-08-01", "2019-08-03"], "2020": ["2020-07-26", "2020-07-28", "2020-07-31"], "2021": ["2021-07-26", "2021-08-02", "2021-08-05"], "2022": ["2022-07-26", "2022-07-31", "2022-08-05"], "2023": ["2023-07-26", "2023-07-28",...
- scene_ids_before: ["S2A_51JYN_20220731_0_L2A", "S2A_52KBU_20220731_0_L2A", "S2A_51KZP_20220731_0_L2A", "S2A_51JZN_20220731_0_L2A", "S2A_52JBT_20220731_0_L2A", "S2A_51KYP_20220731_0_L2A", "S2B_51JZN_20220726_0_L2A", "S2B_52JBT_20220726_0_L2A", "S2B_51KYP_20220726_0_L2A", "S2B_52KBU_20220726_0_L2A", "S2B_51KZP_20220...
- scene_ids_after: ["S2A_51JYN_20230726_0_L2A", "S2A_51JZN_20230726_0_L2A", "S2A_51KYP_20230726_0_L2A", "S2A_51KZP_20230726_0_L2A", "S2A_52JBT_20230726_0_L2A", "S2A_52KBU_20230726_0_L2A", "S2B_51JYN_20230728_0_L2A", "S2B_51JZN_20230728_0_L2A", "S2B_51KZP_20230728_0_L2A", "S2B_52JBT_20230728_0_L2A", "S2B_52KBU_20230...
- res_m: 20
- weak: False
- series: time series with 30 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_mode: contrast
- series_shift: 0.01158
- series_noise: 0.002568
- onset_window_days: 55
- onset_flips: 1
- landsat: {"status": "not_run", "reason": "footprint radius 28 m is below one Landsat pixel"}
- sar: {"status": "not_run", "reason": "footprint radius 28 m is under two radar pixels"}
- regional_siblings: {"count": 0, "compared": 51, "year": 2023, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 2,400
- shape.perimeter_m: 120
- shape.equivalent_diameter_m: 55.28
- shape.major_axis_m: 65.32
- shape.minor_axis_m: 40
- shape.elongation: 1.633
- shape.orientation_deg: 0
- shape.circularity: 1
- shape.solidity: 1
- shape.eccentricity: 0.7906
- shape.rectangularity: 1
- shape.n_corners: 4
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 1

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1161 / 0.1178; ndvi 0.1451 / 0.1461; nbr -0.1231 / -0.1144
- after: brightness 0.1189 / 0.098; ndvi 0.148 / 0.1967; nbr -0.1329 / -0.0798

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Emu Field nuclear test site (test_range), 757 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly shrub (54%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 137 m of the footprint (1 tagged features in the extract; no road or track within 3162 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2023-02-03 to 2023-05-29; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2023-04-29 (nearest record: Veevers (Found, 1984) at 193.4 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.38 against background 0.29 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 159 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202209 to 202302) persistent light was absent (radiance 0.375, background 0.28 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran and did not explain the feature. 10 natural-process tests ran clean Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (2 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. 3 of 13 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran but was INCONCLUSIVE. 3 of 13 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2022-01-29 and 2023-05-14 within 92 m of the candidate (burned area: 17/17 monthly files read for 7 pixels; active fire: 113 eight-day files read (0 incomplete); 455/471 days covered, clear view on 428). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.028). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 51 other yearly candidates in this region changed the same way in 2023 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.03) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2023-04-29 (nearest record: Veevers (Found, 1984) at 193.4 km)
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
- The Esri picture in `hires.png` was taken on 2025-08-19 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2022-03-05 to 2023-03-05: scenes S2A_51JZN_20220310_0_L2A, S2A_52JBT_20220310_0_L2A, S2B_51JZN_20220315_0_L2A, S2B_52JBT_20220315_0_L2A, S2B_51JZN_20220318_0_L2A, S2B_52JBT_20220318_0_L2A, S2B_51JZN_20220407_0_L2A, S2B_52JBT_20220407_0_L2A
- Sentinel-2 `after` composite, window 2023-04-29 to 2024-04-28: scenes S2A_51JZN_20230507_0_L2A, S2A_52JBT_20230507_0_L2A, S2B_51JZN_20230509_0_L2A, S2B_52JBT_20230509_0_L2A, S2B_51JZN_20230512_0_L2A, S2B_52JBT_20230512_0_L2A, S2A_51JZN_20230517_0_L2A, S2A_52JBT_20230517_0_L2A
- Sentinel-2 `context` composite, window 2023-04-29 to 2024-04-28: scenes S2A_51JZN_20230507_0_L2A, S2A_52JBT_20230507_0_L2A, S2B_51JZN_20230509_0_L2A, S2B_52JBT_20230509_0_L2A, S2B_51JZN_20230512_0_L2A, S2B_52JBT_20230512_0_L2A, S2A_51JZN_20230517_0_L2A, S2A_52JBT_20230517_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
