# Reproduction scopes and commands

## Standalone frozen-input reproduction

Extract the revised ZIP into a new folder. Do not put SUBMISSION_PACKAGE next to it. With Python 3.12 and the declared requirements installed, run:

```
python run_all.py
```

This regenerates the main policy/mutation results, all exact certificates, both timing protocols, the direct source-program experiment, ablation, audits and Markdown manuscript. It uses only bundled inputs and code. The historical 255-configuration CSV is under inputs/historical and is hash-bound in inputs/manifest.json. The version evaluation uses bundled actual version-worker outputs. Default reproduction does not retrain models or install multiple SciPy versions. It has no dependency on original manuscript files.

The revised package's clean-extraction report records the candidate ZIP hash and scientific source hashes that were exercised. Final document/report additions can change the distribution hash without changing those tested programs; the report explicitly compares their hashes. This is local clean reproduction, not independent-human replication.

## Optional fresh library execution

Create two separate Python 3.12 environments, one with numpy==2.3.5 and scipy==1.15.3, the other with numpy==2.3.5 and scipy==1.18.1. The newer environment also needs the main requirements for evaluation. Supply their executables explicitly:

```
python run_version_pair.py --old-python PATH_TO_OLD_PYTHON --new-python PATH_TO_NEW_PYTHON
```

The worker version-asserts the imported binary and writes fresh source hashes, runtime metadata and scores. The eleven interpolation input arrays are bundled; no adjacent original project is required. Results are differences between dependency versions on inherited calibration inputs, not confirmed upstream bugs.

## Optional model refitting

`python run_all.py --retrain` additionally requires the inherited source datasets from the adjacent SUBMISSION_PACKAGE. This optional training path is intentionally distinguished from default standalone reproduction. Its source hashes and exact split indices are recorded; it is not silently part of the frozen-input claim.

## Manuscript authoring

The DOCX/PDF supplied with the archive are rendered reading copies. Regenerating scientific results changes timings; it does not automatically refresh a binary Word/PDF file. `build_manuscript.py` updates the Markdown narrative from active records. `render_manuscript.py` requires the separate authoring requirements and creates DOCX and figures; PDF export was performed with native Microsoft Word and inspected with Poppler. Rendering dependencies are not required by the scientific runner.

## Timing interpretation

Raw records, source snapshots and runtime reports are separate for traced end-to-end certificate timings, untraced matched-method timings and within-invocation phase ablation. Do not pool them. Reproduction will change timing values. Boolean memberships, exact rational intervals, logical counts and independent-verification outcomes are the deterministically checked results.
