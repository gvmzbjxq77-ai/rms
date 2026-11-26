# Dossier: candidate SW-B28-AMAZON-OC0002

## What was detected
The detector `optical_change` flagged a surface anomaly of unclassified kind (signature class `unknown`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.335 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: -5.45487 N, -66.04838 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -66.04892, -5.45541, -66.04784, -5.45432; centre -5.45487, -66.04838
- Area: 1,600 m2
- Search region: `B28-AMAZON`

## When
The feature is absent in imagery up to 2024-08-18 and present from 2025-07-19. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2025
- step_snr: 8.375
- d_brightness: 0.007026
- d_ndvi: 0.00787
- d_nbr: -0.03935
- d_swir: 0.05119
- persistence_years: 2
- recovery_fraction: 0.2301
- crowding: 0.0003509
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-21", "2018-07-26", "2018-08-25"], "2019": ["2019-07-31", "2019-08-10", "2019-08-15"], "2020": ["2020-07-30", "2020-08-04", "2020-08-09"], "2021": ["2021-07-20", "2021-08-09", "2021-08-24"], "2022": ["2022-07-20", "2022-07-30", "2022-08-24"], "2023": ["2023-07-30", "2023-08-09",...
- scene_ids_before: ["S2B_19MHP_20240729_0_L2A", "S2B_19MHQ_20240729_0_L2A", "S2B_19MHP_20240808_0_L2A", "S2B_19MHQ_20240808_0_L2A", "S2B_19MHP_20240818_0_L2A", "S2B_19MHQ_20240818_0_L2A"]
- scene_ids_after: ["S2C_19MHP_20250719_0_L2A", "S2C_19MHQ_20250719_0_L2A", "S2A_19MHP_20250731_1_L2A", "S2A_19MHQ_20250731_1_L2A", "S2B_19MHP_20250813_0_L2A", "S2B_19MHQ_20250813_0_L2A"]
- res_m: 20
- weak: True
- series: time series with 27 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_shift: -0.04271
- series_noise: 0.08682
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "not_run", "reason": "footprint radius 23 m is below one Landsat pixel"}
- sar: {"status": "not_run", "reason": "footprint radius 23 m is under two radar pixels"}
- regional_siblings: {"count": 0, "compared": 119, "year": 2025, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
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
- before: brightness 0.0284 / 0.0284; ndvi 0.8477 / 0.846; nbr 0.6801 / 0.67
- after: brightness 0.0303 / 0.0277; ndvi 0.8325 / 0.8456; nbr 0.6301 / 0.6601

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Guiana Space Centre, Kourou (launch_site), 1882 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly tree (100%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 120 m of the footprint (8 tagged features in the extract; no road or track within 3060 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2024-07-19 to 2025-08-18; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-07-19 (nearest record: Muenatauray (Found, 1960) at 1271.1 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): NOT RUN. The night-light archive ends 2025-06-30; the feature is first seen 2025-07-19, so no night-light data exists for the period after its appearance. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran and did not explain the feature. 10 natural-process tests ran clean Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (6 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. 5 of 11 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran but was INCONCLUSIVE. 5 of 11 later scenes show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2023-07-15 and 2025-08-03 within 85 m of the candidate, but the record is incomplete (burned area: 21/26 monthly files read for 4 pixels; no file for 2023-09, 2024-07, 2024-11, 2025-05, 2025-08; active fire: 175 eight-day files read (0 incomplete); 698/751 days covered, clear view on 605), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR change -0.039 is too small for a burn. Recovery fraction 0.23: gradual recovery, as vegetation regrowth after fire would give Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 119 other yearly candidates in this region changed the same way in 2025 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.04) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2025-07-19 (nearest record: Muenatauray (Found, 1960) at 1271.1 km)
- **night_lights**: The night-light archive ends 2025-06-30; the feature is first seen 2025-07-19, so no night-light data exists for the period after its appearance.
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
- The Esri picture in `hires.png` was taken on 2025-11-05 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2023-08-19 to 2024-08-18: scenes S2A_19MHP_20230908_0_L2A, S2A_19MHQ_20230908_0_L2A, S2A_19MHP_20240724_0_L2A, S2A_19MHQ_20240724_0_L2A, S2B_19MHP_20240729_0_L2A, S2B_19MHQ_20240729_0_L2A, S2B_19MHP_20240818_0_L2A, S2B_19MHQ_20240818_0_L2A
- Sentinel-2 `after` composite, window 2025-07-19 to 2026-07-19: scenes S2C_19MHP_20250719_0_L2A, S2C_19MHQ_20250719_0_L2A, S2A_19MHP_20250731_1_L2A, S2A_19MHQ_20250731_1_L2A, S2C_19MHP_20250828_0_L2A, S2C_19MHQ_20250828_0_L2A, S2B_19MHP_20260321_0_L2A, S2B_19MHQ_20260321_0_L2A
- Sentinel-2 `context` composite, window 2025-07-19 to 2026-07-19: scenes S2C_19MHP_20250719_0_L2A, S2C_19MHQ_20250719_0_L2A, S2A_19MHP_20250731_1_L2A, S2A_19MHQ_20250731_1_L2A, S2C_19MHP_20250828_0_L2A, S2C_19MHQ_20250828_0_L2A, S2B_19MHP_20260321_0_L2A, S2B_19MHQ_20260321_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
