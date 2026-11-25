# Dossier: candidate SW-B09-GIBSON-OC0006

## What was detected
The detector `optical_change` flagged a structure or installation that the detector flagged (signature class `installation`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.2547 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: -24.67805 N, 126.14364 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 126.14286, -24.67888, 126.14441, -24.67723; centre -24.67805, 126.14364
- Area: 5,600 m2
- Search region: `B09-GIBSON`

## When
The feature is absent in imagery up to 2024-10-05 and present from 2024-12-24. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_landsat, optical_s2
- kind: step
- break_year: 2025
- step_snr: 6.367
- d_brightness: 0.03732
- d_ndvi: -0.03234
- d_nbr: -0.0111
- d_swir: 0.1144
- persistence_years: 2
- recovery_fraction: 0
- crowding: 1.022e-11
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-27", "2018-07-29", "2018-08-03"], "2019": ["2019-07-27", "2019-08-01", "2019-08-03"], "2020": ["2020-07-26", "2020-07-28", "2020-07-31"], "2021": ["2021-07-26", "2021-08-02", "2021-08-05"], "2022": ["2022-07-26", "2022-07-31", "2022-08-05"], "2023": ["2023-07-26", "2023-07-28",...
- scene_ids_before: ["S2A_51JYN_20240730_0_L2A", "S2A_52JBT_20240730_0_L2A", "S2A_51JZN_20240730_0_L2A", "S2A_51KYP_20240730_0_L2A", "S2A_52KBU_20240730_0_L2A", "S2A_51KZP_20240730_0_L2A", "S2A_51JYN_20240727_0_L2A", "S2A_51JZN_20240727_0_L2A", "S2A_52JBT_20240727_0_L2A", "S2A_52KBU_20240727_0_L2A", "S2A_51KZP_20240...
- scene_ids_after: ["S2C_51JYN_20250801_0_L2A", "S2C_52JBT_20250801_0_L2A", "S2C_51JZN_20250801_0_L2A", "S2C_52KBU_20250801_0_L2A", "S2C_51KZP_20250801_0_L2A", "S2A_51JYN_20250727_1_L2A", "S2A_51JZN_20250727_1_L2A", "S2A_52JBT_20250727_1_L2A", "S2A_51KYP_20250727_0_L2A", "S2A_51KZP_20250727_1_L2A", "S2A_52KBU_20250...
- res_m: 20
- weak: False
- series: time series with 30 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: brightness
- series_mode: contrast
- series_shift: 0.0285
- series_noise: 0.008821
- onset_window_days: 80
- onset_flips: 1
- landsat: {"status": "ok", "before": [{"date": "2023-09-05", "scene_id": "LC09_L2SP_107077_20230905_02_T1", "brightness": -0.0007066652178764343, "ndvi": 0.0006300061941146851, "nbr": -0.02086443454027176, "kelvin": 0.381439208984375}, {"date": "2023-12-26", "scene_id": "LC09_L2SP_107077_20231226_02_T1", "...
- sar: {"status": "not_run", "reason": "no relative orbit covers both periods (0 scenes before, 23 after)"}
- regional_siblings: {"count": 0, "compared": 51, "year": 2025, "ids": [], "spread_km": 0.0, "min_cosine": 0.9, "magnitude_ratio": 2.0}
- shape.area_m2: 5,600
- shape.perimeter_m: 248.3
- shape.equivalent_diameter_m: 84.44
- shape.major_axis_m: 124
- shape.minor_axis_m: 59.88
- shape.elongation: 2.071
- shape.orientation_deg: 67.89
- shape.circularity: 1
- shape.solidity: 0.875
- shape.eccentricity: 0.8757
- shape.rectangularity: 0.7
- shape.n_corners: 4
- shape.straight_edge_fraction: 0.6504
- shape.hole_fraction: 0
- shape.regularity: 0.875

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.1075 / 0.1117; ndvi 0.1329 / 0.1359; nbr -0.1725 / -0.1583
- after: brightness 0.1131 / 0.1024; ndvi 0.1334 / 0.1687; nbr -0.1669 / -0.1321

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Emu Field nuclear test site (test_range), 751 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly shrub (52%); cropland 0%, built-up 0%, water/wetland 0%; the 2021 map predates the onset, so it shows the site before the change. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. OpenStreetMap has no tagged feature within 2987 m. OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (0 item(s) within 10.0 km; nearest: none) Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.0 km dated 2024-09-05 to 2025-01-23; no record in the window within the context radius. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-12-24 (nearest record: Warburton Range (Found, 1963) at 186.1 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran and did not explain the feature. remote: no mapped road within 300 m, no mapped building within 1 km, and no farmland or built-up land within 1.5 km (maps are incomplete in remote regions) Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 0.385 against background 0.29 nW/cm2/sr, lit in 0 of 6 monthly composites (202501 to 202506, 82 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202404 to 202409) persistent light was absent (radiance 0.36, background 0.255 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran but was INCONCLUSIVE. moisture-like spectral change (wetting or drying) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran and did not explain the feature. gentle ground (4 degrees) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran and did not explain the feature. 14 of 14 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran and did not explain the feature. 14 of 14 later scenes independently show the change Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 3 and 3 separate dates; 9 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 0.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran but was INCONCLUSIVE. no fire seen between 2023-09-01 and 2025-01-08 within 121 m of the candidate, but the record is incomplete (burned area: 16/17 monthly files read for 7 pixels; no file for 2023-09; active fire: 123 eight-day files read (0 incomplete); 488/496 days covered, clear view on 470), so a fire in the gap cannot be ruled out. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: surface brightened (+0.037). Recovery fraction 0.00: no recovery yet (burn scars can persist for years) Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **natural:regional_pattern** (natural): ran and did not explain the feature. 0 of 51 other yearly candidates in this region changed the same way in 2025 (spectral direction within cosine 0.9, size within 2.0x), spread over 0.0 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2024-12-24 (nearest record: Warburton Range (Found, 1963) at 186.1 km)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: fire_history, natural:surface_water, natural_process (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2025-08-02 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2023-10-06 to 2024-10-05: scenes S2A_51JZN_20231014_0_L2A, S2A_52JBT_20231014_0_L2A, S2B_51JZN_20231118_0_L2A, S2B_52JBT_20231118_0_L2A, S2A_51JZN_20231120_0_L2A, S2A_52JBT_20231120_0_L2A, S2B_51JZN_20231218_0_L2A, S2B_52JBT_20231218_0_L2A
- Sentinel-2 `after` composite, window 2024-12-24 to 2025-12-24: scenes S2A_51JZN_20241227_0_L2A, S2A_52JBT_20241227_0_L2A, S2A_51JZN_20250103_0_L2A, S2A_52JBT_20250103_0_L2A, S2A_51JZN_20250116_0_L2A, S2A_52JBT_20250116_0_L2A, S2C_51JZN_20250126_0_L2A, S2C_52JBT_20250126_0_L2A
- Sentinel-2 `context` composite, window 2024-12-24 to 2025-12-24: scenes S2A_51JZN_20241227_0_L2A, S2A_52JBT_20241227_0_L2A, S2A_51JZN_20250103_0_L2A, S2A_52JBT_20250103_0_L2A, S2A_51JZN_20250116_0_L2A, S2A_52JBT_20250116_0_L2A, S2C_51JZN_20250126_0_L2A, S2C_52JBT_20250126_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
