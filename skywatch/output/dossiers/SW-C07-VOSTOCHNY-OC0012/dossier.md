# Dossier: candidate SW-C07-VOSTOCHNY-OC0012

## What was detected
The detector `optical_change` flagged a mark resembling a landing trace (signature class `landing_trace`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.4436 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 51.87030 N, 128.33408 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): 128.33185, 51.86903, 128.33653, 51.87152; centre 51.87028, 128.33419
- Area: 27,200 m2
- Search region: `C07-VOSTOCHNY`

## When
The feature is absent in imagery up to 2023-08-06 and present from 2024-07-23. It appeared at some time between those two dates; the pipeline cannot say when within that window.

## Measurements
- Sensor families in which the feature is seen: optical_s2
- kind: step
- break_year: 2024
- step_snr: 11.09
- d_brightness: 0.1025
- d_ndvi: -0.59
- d_nbr: -0.5813
- d_swir: 0.1012
- persistence_years: 3
- recovery_fraction: 0
- crowding: 0.000614
- n_valid_years: 9
- years_used: [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
- composite_dates: {"2018": ["2018-07-30", "2018-08-02", "2018-08-04"], "2019": ["2019-08-02", "2019-08-07", "2019-08-12"], "2020": ["2020-07-14", "2020-07-29", "2020-08-13"], "2021": ["2021-07-17", "2021-08-13", "2021-08-16"], "2022": ["2022-08-16", "2022-08-21", "2022-09-02"], "2023": ["2023-07-14", "2023-07-17",...
- scene_ids_before: ["S2A_52UDC_20230806_0_L2A", "S2A_52UDC_20230717_0_L2A", "S2A_52UDC_20230714_0_L2A"]
- scene_ids_after: ["S2B_52UDC_20240723_0_L2A", "S2A_52UDC_20240820_0_L2A", "S2B_52UDC_20240726_0_L2A"]
- res_m: 20
- weak: False
- regional_siblings: {"count": 10, "compared": 79, "year": 2024, "ids": ["SW-C07-VOSTOCHNY-OC0065", "SW-C07-VOSTOCHNY-OC0021", "SW-C07-VOSTOCHNY-OC0033", "SW-C07-VOSTOCHNY-OC0050", "SW-C07-VOSTOCHNY-OC0067", "SW-C07-VOSTOCHNY-OC0074", "SW-C07-VOSTOCHNY-OC0073", "SW-C07-VOSTOCHNY-OC0071"], "spread_km": 9.2, "min_cosin...
- shape.area_m2: 27,200
- shape.perimeter_m: 635.3
- shape.equivalent_diameter_m: 186.1
- shape.major_axis_m: 217.4
- shape.minor_axis_m: 172.8
- shape.elongation: 1.258
- shape.orientation_deg: 153.6
- shape.circularity: 0.847
- shape.solidity: 0.85
- shape.eccentricity: 0.607
- shape.rectangularity: 0.6974
- shape.n_corners: 6
- shape.straight_edge_fraction: 0.7154
- shape.hole_fraction: 0
- shape.regularity: 0.6097

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- before: brightness 0.0539 / 0.05; ndvi 0.6247 / 0.639; nbr 0.3179 / 0.3365
- after: brightness 0.0946 / 0.0459; ndvi 0.4701 / 0.7326; nbr 0.2278 / 0.49

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). inside Vostochny Cosmodrome (launch_site, Russia): 1.1 km from the centre of an approximate 15 km circle (geometry confidence high); conventional military or space activity is the overwhelmingly likely cause Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
- **landcover** (natural): NOT RUN. skipped: already explained by military_or_rocket_range Source: engine.
- **osm_infrastructure** (infrastructure): NOT RUN. skipped: already explained by military_or_rocket_range Source: engine.
- **wikidata_nearby** (infrastructure): NOT RUN. skipped: already explained by military_or_rocket_range Source: engine.
- **aviation_accident** (event): NOT RUN. skipped: already explained by military_or_rocket_range Source: engine.
- **meteorite_record** (event): NOT RUN. skipped: already explained by military_or_rocket_range Source: engine.

## Checks that were NOT run
A check that did not run rules nothing out. These explanations remain open:
- **landcover** (mandatory): skipped: already explained by military_or_rocket_range
- **osm_infrastructure** (mandatory): skipped: already explained by military_or_rocket_range
- **wikidata_nearby** (mandatory): skipped: already explained by military_or_rocket_range
- **aviation_accident**: skipped: already explained by military_or_rocket_range
- **meteorite_record**: skipped: already explained by military_or_rocket_range
- **fire_history** (mandatory): never attempted: no result is recorded for this check
- **artefact_screen** (mandatory): never attempted: no result is recorded for this check
- **natural_process** (mandatory): never attempted: no result is recorded for this check

## Evidence tier
**T0**: explained by a conventional cause.

Reason: explained by: military_or_rocket_range (recorded on the candidate).

The tier ladder measures how much of the evidence is in place. Its top means "unexplained after every check", never "identified".

## Figures
- `before.png`: Sentinel-2 true colour, BEFORE onset
- `falsecolor_before.png`: Sentinel-2 false colour (SWIR1, NIR, red), BEFORE onset
- `after.png`: Sentinel-2 true colour, AFTER onset
- `falsecolor_after.png`: Sentinel-2 false colour (SWIR1, NIR, red), AFTER onset
- `difference.png`: After minus before: brightness and NDVI change
- `context.png`: Wider setting with the footprint marked
- `hires.png`: Esri World Imagery view (viewing only)
- `wayback_strip.png`: Esri Wayback versions; dates are publication dates, not acquisition dates
- The Esri picture in `hires.png` was taken on 2023-09-09 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
- `timeseries.png`: the detector recorded no time series (measurements['series'] is absent)

## Data provenance
- Sentinel-2 `before` composite, window 2022-08-06 to 2023-08-06: scenes S2A_52UDC_20221007_0_L2A, S2A_52UDC_20221027_0_L2A, S2A_52UDC_20230704_0_L2A, S2B_52UDC_20230712_0_L2A
- Sentinel-2 `after` composite, window 2024-07-23 to 2025-07-23: scenes S2A_52UDC_20240820_0_L2A, S2B_52UDC_20240911_0_L2A, S2A_52UDC_20241006_0_L2A, S2C_52UDC_20250626_0_L2A
- Sentinel-2 `context` composite, window 2024-07-23 to 2025-07-23: scenes S2A_52UDC_20240820_0_L2A, S2B_52UDC_20240911_0_L2A, S2A_52UDC_20241006_0_L2A, S2C_52UDC_20250626_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
