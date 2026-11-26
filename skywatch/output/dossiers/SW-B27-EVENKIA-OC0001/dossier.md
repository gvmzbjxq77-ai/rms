# Dossier: candidate SW-B27-EVENKIA-OC0001

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2596 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 64.10254 N, 104.39588 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 104.39464, 64.10201, 104.39713, 64.10307; centre 64.10254, 104.39588
- Area: 1,600 m2
- Search region: `B27-EVENKIA`

## When
The feature is absent in imagery up to 2019-07-24 and present from 2020-08-02. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2020
- step_snr: 6.49
- d_brightness: -0.04639
- d_ndvi: 0.1458
- d_nbr: 0.3061
- d_swir: -0.172
- persistence_years: 7
- recovery_fraction: 0
- crowding: 4.386e-05
- n_valid_years: 7
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-06-25", "2018-07-12", "2018-07-19"], "2019": ["2019-07-20", "2019-07-24"], "2020": ["2020-08-02", "2020-08-05", "2020-08-12"], "2021": ["2021-07-14", "2021-07-16", "2021-07-28"], "2022": ["2022-06-21", "2022-06-23", "2022-07-29"], "2023": ["2023-06-29", "2023-07-23", "2023-08-02"]...
- scene_ids_before: ["S2A_48WVS_20190720_1_L2A", "S2A_48VVR_20190724_1_L2A", "S2A_48WVS_20190724_1_L2A"]
- scene_ids_after: ["S2B_48VVR_20200802_1_L2A", "S2B_48WVS_20200802_1_L2A", "S2B_48VVR_20200805_1_L2A", "S2B_48WVS_20200805_1_L2A", "S2B_48VVR_20200812_1_L2A"]
- res_m: 20
- weak: False
- series: time series with 28 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_shift: 0.3662
- series_noise: 0.6115
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "not_run", "reason": "footprint radius 23 m is below one Landsat pixel"}
- sar: {"status": "not_run", "reason": "footprint radius 23 m is under two radar pixels"}
- regional_siblings: {"count": 0, "compared": 119, "year": 2020, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
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
- before: brightness 0.0771 / 0.0741; ndvi 0.4393 / 0.5562; nbr 0.2319 / 0.405
- after: brightness 0.0362 / 0.0405; ndvi 0.4981 / 0.4953; nbr 0.2762 / 0.1734

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Vostochny drop zones, Yakutia (Aldan / Vilyuy) (drop_zone), 788 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly grass (51%); cropland 0%, built-up 0%, water/wetland 18%; the 2021 map postdates the onset, so it may show the change itself. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 2976 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2019-06-24 to 2020-09-01; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2020-08-02 (nearest record: Ssyromolotovo (Found, 1873) at 675.4 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 1.49 against background 1.06 nW/cm2/sr, lit in 1 of 9 monthly composites (202407 to 202506, 97 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (201901 to 201906) persistent light was absent (radiance 0.495, background 0.385 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. permafrost terrain with 16% water or wetland around the footprint: lake drainage, thaw slump or shoreline change is likely; 16% of the surroundings is water: channel migration, flood deposit or shoreline change Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (0 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran but was INCONCLUSIVE. permafrost terrain with 16% water or wetland around the footprint: lake drainage, thaw slump or shoreline change is likely Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran but was INCONCLUSIVE. 16% of the surroundings is water: channel migration, flood deposit or shoreline change Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. 5 of 11 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran but was INCONCLUSIVE. 5 of 11 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 2 and 3 separate dates; 7 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2018-06-19 and 2020-08-17 within 85 m of the candidate, but the record is incomplete (burned area: 27/27 monthly files read for 9 pixels; unmapped in 2019-03; active fire: 200 eight-day files read (0 incomplete); 791/791 days covered, clear view on 366), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.306); NDVI rose (+0.146). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 119 other yearly candidates in this region changed the same way in 2020 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.31) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2020-08-02 (nearest record: Ssyromolotovo (Found, 1873) at 675.4 km)
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
- The Esri picture in `hires.png` was taken on 2019-08-19 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2018-07-24 to 2019-07-24: scenes S2B_48WVS_20180902_1_L2A, S2A_48WVS_20190319_0_L2A, S2A_48WVS_20190704_1_L2A, S2A_48WVS_20190724_1_L2A
- Sentinel-2 `after` composite, window 2020-08-02 to 2021-08-02: scenes S2B_48WVS_20200924_1_L2A, S2B_48WVS_20210512_1_L2A, S2A_48WVS_20210524_1_L2A, S2A_48WVS_20210716_1_L2A
- Sentinel-2 `context` composite, window 2020-08-02 to 2021-08-02: scenes S2B_48WVS_20200924_1_L2A, S2B_48WVS_20210512_1_L2A, S2A_48WVS_20210524_1_L2A, S2A_48WVS_20210716_1_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
