# Dossier: candidate SW-B19-PUNA-OC0010

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.3243 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: -25.14221 N, -67.73557 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -67.73630, -25.14282, -67.73490, -25.14156; centre -25.14219, -67.73560
- Area: 3,200 m2
- Search region: `B19-PUNA`

## When
The feature is absent in imagery up to 2023-05-15 and present from 2024-05-04. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: step
- break_year: 2024
- step_snr: 8.107
- d_brightness: 0.0479
- d_ndvi: -0.05591
- d_nbr: -0.158
- d_swir: 0.1331
- persistence_years: 3
- recovery_fraction: 0
- crowding: 8.772e-05
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-05-09", "2018-05-29", "2018-06-03"], "2019": ["2019-05-01", "2019-05-06", "2019-05-16"], "2020": ["2020-05-05", "2020-05-08", "2020-05-10"], "2021": ["2021-05-05", "2021-05-08", "2021-05-10"], "2022": ["2022-04-30", "2022-05-05", "2022-05-10"], "2023": ["2023-05-08", "2023-05-10",...
- scene_ids_before: ["S2A_19JFM_20230508_0_L2A", "S2A_19JFN_20230508_0_L2A", "S2B_19JFM_20230510_0_L2A", "S2B_19JFN_20230510_0_L2A", "S2A_19JFM_20230515_0_L2A", "S2A_19JFN_20230515_0_L2A"]
- scene_ids_after: ["S2B_19JFM_20240504_0_L2A", "S2B_19JFN_20240504_0_L2A", "S2A_19JFM_20240509_0_L2A", "S2A_19JFN_20240509_0_L2A", "S2A_19JFM_20240519_0_L2A", "S2A_19JFN_20240519_0_L2A"]
- res_m: 20
- weak: False
- series: time series with 29 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_shift: -0.07537
- series_noise: 0.1116
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "ok", "before": [{"date": "2022-04-13", "scene_id": "LC09_L2SP_233077_20220413_02_T1", "brightness": -0.02688077837228775, "ndvi": 0.17414213716983795, "nbr": 0.2687130570411682, "kelvin": -2.976470947265625}, {"date": "2022-08-27", "scene_id": "LC08_L2SP_233077_20220827_02_T1", "brigh...
- sar: {"status": "not_run", "reason": "footprint radius 32 m is under two radar pixels"}
- regional_siblings: {"count": 0, "compared": 119, "year": 2024, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 3,200
- shape.perimeter_m: 148.3
- shape.equivalent_diameter_m: 63.83
- shape.major_axis_m: 69.28
- shape.minor_axis_m: 54.77
- shape.elongation: 1.265
- shape.orientation_deg: 45
- shape.circularity: 1
- shape.solidity: 1
- shape.eccentricity: 0.6124
- shape.rectangularity: 0.8889
- shape.n_corners: 4
- shape.straight_edge_fraction: 0
- shape.hole_fraction: 0
- shape.regularity: 1

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1236 / 0.1532; ndvi 0.2951 / 0.0824; nbr 0.3794 / 0.0853
- after: brightness 0.1453 / 0.1588; ndvi 0.2849 / 0.0802; nbr 0.3347 / 0.0808

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Alcantara Launch Center (launch_site), 3554 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly grass (85%); cropland 0%, built-up 0%, water/wetland 2%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 141 m of the footprint (9 tagged features in the extract; nearest road or track 21 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (3 item(s) within 10.0 km; nearest: Cavi (Q140296294, settlement) at 1.11 km; Vega Aras (Q21845724, other) at 4.57 km; Proyecto Lindero (Q21573699, mine_or_quarry) at 4.91 km); nearest causal item beyond the limit: Proyecto Lindero (Q21573699, mine_or_quarry) at 4.91 km Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2023-04-15 to 2024-06-03; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-05-04 (nearest record: Aguas Calientes (Found, 1971) at 77.7 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: a mapped road or track is 21 m away Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.415 against background 0.35 nW/cm2/sr, lit in 0 of 12 monthly composites (202407 to 202506, 172 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202211 to 202304) persistent light was absent (radiance 0.405, background 0.335 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
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
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2022-04-10 and 2024-05-19 within 99 m of the candidate, but the record is incomplete (burned area: 25/26 monthly files read for 6 pixels; no file for 2023-09; active fire: 185 eight-day files read (0 incomplete); 739/771 days covered, clear view on 731), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.048). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 119 other yearly candidates in this region changed the same way in 2024 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.16) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-05-04 (nearest record: Aguas Calientes (Found, 1971) at 77.7 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: artefact:per_scene_support, artefact_screen, fire_history, human_context, natural:surface_water, natural_process (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2023-03-15 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2022-05-15 to 2023-05-15: scenes S2B_19JFN_20230420_0_L2A, S2A_19JFN_20230425_0_L2A, S2B_19JFN_20230510_0_L2A, S2A_19JFN_20230515_0_L2A
- Sentinel-2 `after` composite, window 2024-05-04 to 2025-05-04: scenes S2B_19JFN_20250310_0_L2A, S2A_19JFN_20250406_0_L2A, S2B_19JFN_20250409_0_L2A, S2B_19JFN_20250429_0_L2A
- Sentinel-2 `context` composite, window 2024-05-04 to 2025-05-04: scenes S2B_19JFN_20250310_0_L2A, S2A_19JFN_20250406_0_L2A, S2B_19JFN_20250409_0_L2A, S2B_19JFN_20250429_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
