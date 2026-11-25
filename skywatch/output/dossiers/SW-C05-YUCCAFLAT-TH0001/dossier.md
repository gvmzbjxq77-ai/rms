# Dossier: candidate SW-C05-YUCCAFLAT-TH0001

## What was detected
The detector `landsat_thermal` flagged a persistent thermal anomaly (signature class `thermal`). The class describes what the mark looks like in the imagery; it is not a statement about what made it.

Detector score: 0.5504 on a 0 to 1 scale. This is the detector's own measure of how strong the signal is, not a probability of anything.

Notes: stopped after the cheap checks

## Where
- Position: 37.16788 N, -116.16072 E (WGS84; negative values mean south or west)
- Footprint (west, south, east, north): -116.16420, 37.16365, -116.15617, 37.17101; centre 37.16733, -116.16019
- Area: 226,800 m2
- Search region: `C05-YUCCAFLAT`

## When
No dated onset: the pipeline has no pair of dates bracketing the appearance (absent_until = None, present_from = None). Only a current view is shown.

## Measurements
- Sensor families in which the feature is seen: thermal_landsat
- median_anomaly_K: -5.897
- median_z: -6.604
- hit_fraction: 0.9231
- n_scenes: 14
- sign: -1
- dates: ["2019-06-08", "2020-05-25", "2021-02-21", "2022-02-08", "2022-07-02", "2023-01-02", "2023-07-05", "2023-12-04", "2024-06-21", "2024-12-06", "2025-07-10", "2025-12-17", "2026-06-19", "2026-11-10"]
- years: ["2019", "2020", "2021", "2022", "2023", "2024", "2025", "2026"]
- res_m: 90
- elevation_detrended: True
- surface_detrended: True

Mean values in the dossier's own Sentinel-2 composites (inside the footprint / rest of the detail panel):
- current: brightness 0.0884 / 0.1056; ndvi 0.2211 / 0.2045; nbr 0.0422 / 0.0383

## Conventional explanations tested
- **military_or_rocket_range** (infrastructure): EXPLAINS the feature (a sufficient conventional cause was found). inside Nevada National Security Site (test_range, United States): 21.2 km from the centre of an approximate 28 km circle (geometry confidence high); conventional military or space activity is the overwhelmingly likely cause Source: SKYWATCH curated list data/reference/ranges.json (approximate geometries).
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
- `current.png`: Sentinel-2 true colour, CURRENT (no dated onset)
- `falsecolor_current.png`: Sentinel-2 false colour (SWIR1, NIR, red), CURRENT (no dated onset)
- `context.png`: Wider setting with the footprint marked
- `hires.png`: Esri World Imagery view (viewing only)
- `wayback_strip.png`: Esri Wayback versions; dates are publication dates, not acquisition dates
- The Esri picture in `hires.png` was taken on 2020-12-05 according to Esri's metadata for the centre point. Compare that date with the onset window before reading anything into it.
- The dates in `wayback_strip.png` are the dates on which Esri published each version of its mosaic. They are NOT the dates on which the pictures were taken; a picture can be months or years older than its publication.
- Shown for viewing only: not used for detection and not counted as an independent sensor.

## Panels that could not be produced
- `difference.png`: no dated onset window, so there is no before/after pair
- `timeseries.png`: the detector recorded no time series (measurements['series'] is absent)

## Data provenance
- Sentinel-2 `current` composite, window 2025-11-25 to 2026-11-25: scenes S2C_11SNB_20251128_0_L2A, S2B_11SNB_20260112_0_L2A, S2C_11SNB_20260904_0_L2A, S2B_11SNB_20261108_0_L2A
- Sentinel-2 `context` composite, window 2025-11-25 to 2026-11-25: scenes S2C_11SNB_20251128_0_L2A, S2B_11SNB_20260112_0_L2A, S2C_11SNB_20260904_0_L2A, S2B_11SNB_20261108_0_L2A
- Scene URLs, grids, Esri tile sources and file checksums are in `dossier.json`.

## Closing statement
This dossier records, at most, an unexplained observation: a surface feature that the checks listed above did not account for. It makes no claim about what caused the feature or where it came from. An unexplained observation is not evidence of any particular origin: checks that were not run, gaps in the data and errors in this pipeline all remain possible explanations.
