# SKYWATCH · Phase 1 GROUNDTRUTH

An open, falsifiable search of public satellite imagery for surface changes
that have no ordinary explanation. The pipeline finds abrupt changes, tries
to explain each one conventionally, and keeps only the residue, with the
evidence and with a record of every check that could not be run. It never
claims an origin.

## Stages

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -e . pytest access-parser

.venv/bin/python -m skywatch.sweep.run detect --kind control   # then --kind blind / seeded
.venv/bin/python -m skywatch.sweep.run sensors                  # thermal and night-light detectors
.venv/bin/python -m skywatch.sweep.run eliminate                # cheap checks, onset refinement, all checks, confirmation, tiers
.venv/bin/python -m skywatch.sweep.run recheck                  # re-apply the region-wide sibling census to finished regions
.venv/bin/python -m skywatch.sweep.followup                     # dossiers, timestamps, request drafts
.venv/bin/python -m skywatch.publish.adjudicate                 # review briefs for the panel
.venv/bin/python -m skywatch.publish.site                       # output/site/
.venv/bin/python -m pytest -q -m "not network"                  # unit tests
```

Each stage writes one file per region under `output/candidates/<stage>/` and
skips regions already done, so an interrupted sweep resumes.

## Layout

| Package | Purpose |
|---|---|
| `skywatch/core` | Catalogue search, a common UTM grid for every sensor, cloud-masked composites, the candidate / check / tier model |
| `skywatch/detect` | Sentinel-2 change detector (yearly steps, transients, dated event windows), shape analysis, Landsat optical and thermal, Sentinel-1 radar, terrain, night lights |
| `skywatch/eliminate` | Checks: OpenStreetMap, land cover, Wikidata, test and launch ranges, accident and meteorite records, fire history, natural processes (including the region-wide sibling census: the same change in the same year at five or more unrelated places is a regional process), sensor artefacts; the engine that runs them and assigns tiers |
| `skywatch/reports` | Witness-report ingestion and matching (reports are unverified claims) |
| `skywatch/dossier` | Per-candidate evidence folders with imagery |
| `skywatch/provenance`, `skywatch/foia` | OpenTimestamps proofs; public-records request drafts and ground-truth plans (drafts only, never sent) |
| `skywatch/sweep` | Regions (blind, control) and the staged runner |
| `skywatch/publish` | Catalogue export and the results page |

## Evidence tiers

- **T0** explained by at least one check.
- **T1** unexplained, seen in one sensor family.
- **T2** seen in two sensor families, but a mandatory check did not run, a check is inconclusive, or there is no dated onset.
- **T3** two sensors, a dated abrupt onset, every mandatory check ran and none explains it.
- **T4** T3 plus an independent witness report matched in time and place.

## Network

Only the hosts in `skywatch/core/config.py` (`ALLOWED_HOSTS`) are used. All
data is public and needs no account. Sources that need a login (night-time
and fine thermal data, radar interferometry, lightning archives) are recorded
as "not run", never substituted.
