# Dossier: candidate SW-B04-TANEZROUFT-OC0001

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2477 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 22.71478 N, 1.45953 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 1.45887, 22.71417, 1.46025, 22.71542; centre 22.71480, 1.45956
- Area: 3,200 m2
- Search region: `B04-TANEZROUFT`

## When
The feature is absent in imagery up to 2019-11-01 and present from 2020-10-26. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2020
- step_snr: 6.191
- d_brightness: 0.04746
- d_ndvi: -0.04171
- d_nbr: -0.01802
- d_swir: 0.09216
- persistence_years: 7
- recovery_fraction: 0
- crowding: 0.0004386
- n_valid_years: 8
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-10-27", "2018-11-01", "2018-11-03"], "2019": ["2019-10-27", "2019-10-29", "2019-11-01"], "2020": ["2020-10-26", "2020-10-28", "2020-11-05"], "2021": ["2021-10-26", "2021-11-02"], "2022": ["2022-10-26", "2022-10-28", "2022-11-02"], "2023": ["2023-10-28", "2023-10-31", "2023-11-02"]...
- scene_ids_before: ["S2B_31QCF_20191101_1_L2A", "S2B_31QCF_20191029_1_L2A", "S2A_31QCF_20191027_1_L2A"]
- scene_ids_after: ["S2A_31QCF_20201028_1_L2A", "S2B_31QCF_20201026_1_L2A", "S2B_31QCF_20201105_1_L2A"]
- res_m: 20
- weak: False
- series: time series with 31 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_shift: 0.03562
- series_noise: 0.02661
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "ok", "before": [{"date": "2018-10-09", "scene_id": "LC08_L2SP_195044_20181009_02_T1", "brightness": 0.002328813076019287, "ndvi": 0.008852720260620117, "nbr": 0.015512891113758087, "kelvin": -0.296783447265625}, {"date": "2019-02-07", "scene_id": "LC08_L2SP_194044_20190207_02_T1", "br...
- sar: {"status": "not_run", "reason": "footprint radius 32 m is under two radar pixels"}
- regional_siblings: {"count": 0, "compared": 0, "year": 2020, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
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
- before: brightness 0.2947 / 0.2937; ndvi 0.0964 / 0.0914; nbr -0.0838 / -0.11
- after: brightness 0.305 / 0.2848; ndvi 0.0888 / 0.0909; nbr -0.0818 / -0.1042

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is In Ekker nuclear test site (Taourirt Tan Afella) (test_range), 386 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly bare (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map postdates the onset, so it may show the change itself. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 2932 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2019-10-02 to 2020-11-25; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2020-10-26 (nearest record: Ilafegh 015 (Found, 1989) at 111.1 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.5 against background 0.385 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 137 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (201905 to 201910) persistent light was absent (radiance 0.275, background 0.235 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
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
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. 5 of 11 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran but was INCONCLUSIVE. 5 of 11 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 8 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2018-09-27 and 2020-11-10 within 99 m of the candidate (burned area: 27/27 monthly files read for 6 pixels; active fire: 198 eight-day files read (0 incomplete); 776/776 days covered, clear view on 763). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.047). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 0 other yearly candidates in this region changed the same way in 2020 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.04) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2020-10-26 (nearest record: Ilafegh 015 (Found, 1989) at 111.1 km)
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
- The Esri picture in `hires.png` was taken on 2025-01-30 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2018-11-01 to 2019-11-01: scenes S2B_31QCF_20181103_1_L2A, S2B_31QCF_20190512_3_L2A, S2A_31QCF_20190517_1_L2A, S2B_31QCF_20190621_1_L2A
- Sentinel-2 `after` composite, window 2020-10-26 to 2021-10-26: scenes S2A_31QCF_20201028_1_L2A, S2A_31QCF_20201117_1_L2A, S2A_31QCF_20201207_1_L2A, S2B_31QCF_20201212_1_L2A
- Sentinel-2 `context` composite, window 2020-10-26 to 2021-10-26: scenes S2A_31QCF_20201028_1_L2A, S2A_31QCF_20201117_1_L2A, S2A_31QCF_20201207_1_L2A, S2B_31QCF_20201212_1_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
