# Dossier: candidate SW-C06-MU5735-EV0028

## What was detected
The detector `optical_event` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.291 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

## Where
- Position: 23.28160 N, 111.08760 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 111.08673, 23.28082, 111.08859, 23.28236; centre 23.28159, 111.08766
- Area: 12,600 m2
- Search region: `C06-MU5735`

## When
The feature is absent in imagery up to 2021-12-13 and present from 2022-04-07. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2, thermal_landsat
- kind: event_window
- event_date: 2022-03-21
- break_year: 2022
- step_snr: 7.274
- d_brightness: -0.03358
- d_ndvi: 0.6579
- d_nbr: 0.7103
- d_swir: -0.07141
- seasonal_baseline: True
- crowding: 0.009564
- composite_dates: {"before": ["2021-10-24", "2021-11-13", "2021-12-03", "2021-12-13"], "after": ["2022-04-07", "2022-04-12", "2022-07-26"]}
- scene_ids_before: ["S2A_49QDF_20211024_1_L2A", "S2A_49QEF_20211024_1_L2A", "S2A_49QDF_20211113_1_L2A", "S2A_49QEF_20211113_1_L2A", "S2A_49QDF_20211203_1_L2A", "S2A_49QEF_20211203_1_L2A", "S2A_49QDF_20211213_1_L2A", "S2A_49QEF_20211213_1_L2A"]
- scene_ids_after: ["S2B_49QDF_20220407_0_L2A", "S2B_49QEF_20220407_0_L2A", "S2A_49QEF_20220412_0_L2A", "S2B_49QDF_20220726_0_L2A", "S2B_49QEF_20220726_0_L2A"]
- res_m: 10
- weak: False
- series: time series with 29 dates (plotted in timeseries.png when usable; full values in dossier.json)
- series_feature: nbr
- series_shift: 0.3395
- series_noise: 0.235
- onset_note: per-scene values do not separate before from after
- landsat: {"status": "ok", "before": [{"date": "2020-11-30", "scene_id": "LC08_L2SP_124044_20201130_02_T1", "brightness": -0.0021694861352443695, "ndvi": 0.07950937747955322, "nbr": 0.12984275817871094, "kelvin": -1.496795654296875}, {"date": "2021-02-02", "scene_id": "LC08_L2SP_124044_20210202_02_T1", "br...
- sar: {"status": "ok", "relative_orbit": 84, "orbit_state": "ascending", "before": [{"date": "2021-04-25", "scene_id": "S1A_IW_GRDH_1SDV_20210425T104207_20210425T104232_037606_046F8B", "contrast_db": -0.7282485961914062}, {"date": "2021-06-24", "scene_id": "S1A_IW_GRDH_1SDV_20210624T104210_20210624T104...
- shape.area_m2: 12,600
- shape.perimeter_m: 449.7
- shape.equivalent_diameter_m: 126.7
- shape.major_axis_m: 163.9
- shape.minor_axis_m: 101.2
- shape.elongation: 1.619
- shape.orientation_deg: 33.4
- shape.circularity: 0.7829
- shape.solidity: 0.9065
- shape.eccentricity: 0.7866
- shape.rectangularity: 0.7636
- shape.n_corners: 10
- shape.straight_edge_fraction: 0.2967
- shape.hole_fraction: 0
- shape.regularity: 0.5557

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.0563 / 0.0499; ndvi 0.5967 / 0.6697; nbr 0.3829 / 0.4622
- after: brightness 0.0538 / 0.0571; ndvi 0.6672 / 0.6436; nbr 0.4881 / 0.4524

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): ran and did not explain the feature. outside every listed launch site, drop zone and range; nearest is Xichang downrange drop zone, south-west Hunan (drop_zone), 348 km beyond its approximate edge. The list is not exhaustive Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): ran and did not explain the feature. Footprint is mostly tree (77%); cropland 0%, built-up 0%, water/wetland 0%; onset is undated or straddles 2021, so the map may show either state. Source: ESA WorldCover 10 m 2021 v200 (c) ESA WorldCover project, CC BY 4.0.
- **osm_infrastructure** (infrastructure): ran and did not explain the feature. No mapped quarry, industry, military, aviation, power, building or similar feature within 190 m of the footprint (2221 tagged features in the extract; nearest road or track 368 m; nearest candidate cause landuse=residential at 514 m). OpenStreetMap coverage in remote regions is incomplete, so the absence of a mapped feature is weak evidence. Source: OpenStreetMap API 0.6 map call; data (c) OpenStreetMap contributors (ODbL).
- **wikidata_nearby** (infrastructure): ran and did not explain the feature. no causally plausible catalogued item within the explanation distance (6 item(s) within 10.0 km; nearest: Q28825022 (Q28825022, other) at 2.04 km; Langnan (Q10929234, settlement) at 2.04 km; 白石水库 (Q16690666, dam_or_reservoir) at 4.17 km); nearest causal item beyond the limit: 白石水库 (Q16690666, dam_or_reservoir) at 4.17 km Source: Wikidata SPARQL endpoint (query.wikidata.org).
- **aviation_accident** (event): ran and did not explain the feature. no recorded accident within 2.1 km dated 2021-11-13 to 2022-05-07; nearest record in the window: Wikidata Q111313251: China Eastern Airlines Flight 5735 at 5.3 km. Coverage is limited: Outside the United States the absence of a record is weak evidence: most general-aviation and all military crashes abroad are in neither catalogue. Source: NTSB aviation accident database (data.ntsb.gov/avdata) and Wikidata aviation-accident items.
- **meteorite_record** (event): NOT RUN. the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-04-07 (nearest record: Zhaoping (Found, 1983) at 106.3 km) Source: Meteoritical Society / NASA Meteorite Landings table (mirror on raw.githubusercontent.com).
- **human_context** (infrastructure): ran but was INCONCLUSIVE. ordinary human activity is present nearby: 7% of the land within 1.5 km is cropland; 2.2% of the land within 1.5 km is built-up Source: OpenStreetMap distances; ESA WorldCover 2021.
- **night_lights** (infrastructure): ran and did not explain the feature. No persistent light within 1500 m of the candidate: peak radiance 1.17 against background 0.575 nW/cm2/sr, lit in 2 of 12 monthly composites (202407 to 202506, 87 cloud-free nights). Unlit sites are not thereby unexplained; many installations carry no lights. Before the onset (202105 to 202111) persistent light was absent (radiance 0.92, background 0.465 nW/cm2/sr). Sensor footprint about 750 m, so a neighbour within roughly 1 km cannot be separated. Archive ends 2025-06-30. Source: World Bank Light Every Night archive, VIIRS DNB monthly cloud-free composites (globalnightlight.s3.amazonaws.com/composites).
- **natural_process** (natural): ran but was INCONCLUSIVE. slopes up to 33 degrees in the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:agriculture** (natural): ran and did not explain the feature. no cropland and not a pivot-sized disc Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:recurring_cycle** (natural): ran and did not explain the feature. the record shows one transition, not a cycle Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:surface_water** (natural): ran and did not explain the feature. no water mapped and no moisture signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:snow_ice** (natural): ran and did not explain the feature. no snow mapped and no snow signature Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:mass_movement** (natural): ran but was INCONCLUSIVE. slopes up to 33 degrees in the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:wind_blown_sand** (natural): ran and did not explain the feature. not an irregular brightness-only change on bare ground Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:permafrost_or_lake_drainage** (natural): ran and did not explain the feature. not a permafrost latitude or altitude Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:river_or_coast** (natural): ran and did not explain the feature. no significant water around the footprint Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:volcanic** (natural): ran and did not explain the feature. no catalogued volcano within 10 km Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **natural:regional_pattern** (natural): NOT RUN. no region-wide sibling census (not a yearly optical candidate, or census not computed) Source: Sentinel-2 change measurements, ESA WorldCover, Copernicus DEM.
- **artefact_screen** (artefact): ran but was INCONCLUSIVE. only 0 of 2 scenes shows the short-lived change; a single-scene feature may be a residual cloud or shadow Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:per_scene_support** (artefact): ran but was INCONCLUSIVE. only 0 of 2 scenes shows the short-lived change; a single-scene feature may be a residual cloud or shadow Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:observation_count** (artefact): ran and did not explain the feature. composites use 4 and 3 separate dates; 6 valid years Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:terrain_shadow** (artefact): ran and did not explain the feature. not a steep-slope darkening pattern Source: Sentinel-2 per-scene series and composite metadata.
- **artefact:widespread_change** (artefact): ran and did not explain the feature. isolated: only 1.0% of the surrounding 3 km changed in the same year Source: Sentinel-2 per-scene series and composite metadata.
- **fire_history** (event): ran and did not explain the feature. no burned area and no active fire between 2021-11-28 and 2022-04-22 within 128 m of the candidate (burned area: 6/6 monthly files read for 8 pixels; active fire: 37 eight-day files read (0 incomplete); 146/146 days covered, clear view on 137). MODIS misses fires smaller than roughly 25 hectares (and fires under persistent cloud), so a small fire is not excluded. Source: MODIS MCD64A1 burned area and MOD14A1/MYD14A1 active fire (Planetary Computer).
- **burn_spectral** (natural): ran and did not explain the feature. the before/after change does not look like a burn scar: NBR rose (+0.710); NDVI rose (+0.658). Source: candidate measurements.
- **lightning** (event): NOT RUN. no open global lightning archive can be reached without an account, so ignition by lightning was not tested Source: none.
- **witness_reports** (report): NOT RUN. no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03) Source: NUFORC public copies; GEIPAN.
- **artefact:index_range** (artefact): ran and did not explain the feature. index changes within range (largest 0.71) Source: Sentinel-2 per-scene series and composite metadata.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **meteorite_record**: the table's last recorded fall year is 2013; it cannot speak for an onset window ending 2022-04-07 (nearest record: Zhaoping (Found, 1983) at 106.3 km)
- **natural:regional_pattern**: no region-wide sibling census (not a yearly optical candidate, or census not computed)
- **lightning**: no open global lightning archive can be reached without an account, so ignition by lightning was not tested
- **witness_reports**: no ingested report source covers this place and time (sources: nuforc 1906-11-11..2023-05-18; geipan 1937-01-01..2026-09-03)

## Evidence tier
**T2**: confirmed in two independent sensors, but the evidence is incomplete.

Reason: confirmed in 2 sensors; inconclusive: artefact:per_scene_support, artefact_screen, human_context, natural:mass_movement, natural_process (recorded on the candidate).

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
- The Esri picture in `hires.png` was taken on 2025-06-23 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
None: every panel was produced.

## Data provenance
- Sentinel-2 `before` composite, window 2020-12-13 to 2021-12-13: scenes S2B_49QDF_20210102_1_L2A, S2B_49QEF_20210102_1_L2A, S2A_49QDF_20210206_1_L2A, S2A_49QEF_20210206_1_L2A, S2A_49QDF_20211203_1_L2A, S2A_49QEF_20211203_1_L2A, S2A_49QDF_20211213_1_L2A, S2A_49QEF_20211213_1_L2A
- Sentinel-2 `after` composite, window 2022-04-07 to 2023-04-07: scenes S2B_49QDF_20220407_0_L2A, S2B_49QEF_20220407_0_L2A, S2B_49QDF_20221014_0_L2A, S2B_49QEF_20221014_0_L2A, S2A_49QDF_20221228_0_L2A, S2A_49QEF_20221228_0_L2A, S2A_49QDF_20230107_0_L2A, S2A_49QEF_20230107_0_L2A
- Sentinel-2 `context` composite, window 2022-04-07 to 2023-04-07: scenes S2B_49QDF_20220407_0_L2A, S2B_49QEF_20220407_0_L2A, S2B_49QDF_20221014_0_L2A, S2B_49QEF_20221014_0_L2A, S2A_49QDF_20221228_0_L2A, S2A_49QEF_20221228_0_L2A, S2A_49QDF_20230107_0_L2A, S2A_49QEF_20230107_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
