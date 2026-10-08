# ML for Space Plasma Physics (TMC course skeleton)

A University of Helsinki style TestMyCode (TMC) course skeleton: "Data
Science / Machine Learning applied to space plasma physics", Python-only,
numpy as the only third-party dependency (no pandas), 10 parts for a full
semester.

This is a **skeleton**, not real course content: only Part 1 has a working
exercise; Parts 2-10 are one-line README placeholders (see "Syllabus"
below).

## Toolchain used to verify this skeleton

- **[tmc-langs-cli](https://github.com/rage/tmc-langs-rust)** 0.39.6, the
  Rust CLI frontend from `rage/tmc-langs-rust` (the University of
  Helsinki's actively maintained TMC tooling; `testmycode/tmc-langs` is the
  older, now-inactive Java predecessor).
- Built from source with `cargo install --git https://github.com/rage/tmc-langs-rust --tag 0.39.6 tmc-langs-cli`
  (installed to `~/.cargo/bin/tmc-langs-cli`).
  **No prebuilt binaries exist**: every recent GitHub release
  (0.39.2-0.39.6) has an empty release-assets list, and the package is not
  published on crates.io (`cargo install tmc-langs-cli` alone fails to
  resolve). Building from source via `--git` is therefore the only
  currently-working install path on macOS; it requires `zstd` (`brew
  install zstd`, already present here) and the Rust toolchain (`cargo`,
  already present here).
- `mooc-cli` was investigated as an alternative but no such Python package
  or tool with that name was found under `rage`, `testmycode`, or on PyPI -
  do not treat it as installed or installable; if it exists it wasn't
  discoverable via GitHub/PyPI search at the time of writing.

## Directory layout

```
tmc-course/
├── README.md                  - this file
├── .tmcproject.yml             - course-wide TMC project defaults (merged into every exercise)
├── course_options.yml          - course-level config read by the TMC server on registration
├── metadata.yml                - course-wide deadline/visibility defaults (server-side)
├── requirements.txt             - numpy (+ pytest for authoring) for local dev/testing
├── part01_data_processing/      - the one real, verified example exercise
│   ├── .tmcproject.yml
│   ├── src/__main__.py          - student-facing stub
│   └── test/
│       ├── __init__.py          - required marker so the Python3 plugin recognizes this dir
│       └── test_exercise.py     - hidden tests, never shipped to students
└── part02/ .. part10/           - README.md stub only (topic placeholder)
```

## How the local build/test toolchain works

All commands below use the CLI verified above. Every `--exercise-path` /
`--output-path` argument must be an **absolute path** - a relative path
such as `.` fails with `No file name found in exercise path .`.

```bash
# Discover the exercise's tests and available points (no execution)
tmc-langs-cli scan-exercise \
  --exercise-path /abs/path/to/tmc-course/part01_data_processing \
  --output-path /tmp/scan.json

# Run the hidden tests against whatever is currently in src/
tmc-langs-cli run-tests \
  --exercise-path /abs/path/to/tmc-course/part01_data_processing \
  --output-path /tmp/results.json

# Produce what a student receives: solution code stripped out
tmc-langs-cli prepare-stub \
  --exercise-path /abs/path/to/tmc-course/part01_data_processing \
  --output-path /tmp/stub_out

# Produce the model solution: stub markers stripped out
tmc-langs-cli prepare-solution \
  --exercise-path /abs/path/to/tmc-course/part01_data_processing \
  --output-path /tmp/solution_out
```

Verified subcommand names come directly from
`crates/tmc-langs-cli/src/app.rs` in `rage/tmc-langs-rust`
(`Command` enum: `Checkstyle`, `Clean`, `CompressProject`, `ExtractProject`,
`FastAvailablePoints`, `FindExercises`,
`GetExercisePackagingConfiguration`, `PrepareSolution`, `PrepareStub`,
`PrepareSubmission`, `RunTests`, `ScanExercise`, plus server-communicating
subcommands under `tmc`/`mooc`/`settings`). Clap converts each PascalCase
variant to kebab-case, e.g. `RunTests` -> `run-tests`.

### A required, easy-to-miss detail: `test/__init__.py`

`tmc-langs-cli` auto-detects the language plugin per exercise by checking,
*in order*: no-tests markers, C#, Make, **Python3**, R, then Java. The
Python3 plugin's detector
(`crates/plugins/python3/src/plugin.rs::is_exercise_type_correct`) only
recognizes an exercise directory as Python if it directly contains one of:
`setup.py`, `requirements.txt`, `test/__init__.py`, or `tmc/__main__.py`.

Without one of those markers, detection falls through toward the Java
plugin, which - on a machine with no JVM installed, as here - crashes with
`Could not find the jvm dynamic library`. Fix: ship an (empty)
`test/__init__.py` in every Python exercise, as `part01_data_processing`
does.

## Student vs. hidden-test split

Confirmed from `Python3StudentFilePolicy::is_non_extra_student_file`
(`crates/plugins/python3/src/policy.rs`): **any** `.py` or `.ipynb` file
anywhere in the exercise is treated as a student file (editable, shipped to
students, overwritten on `prepare-stub`) **except** files under `test/`,
`tmc/`, `venv/`, or `.venv/`. In practice this repo uses the conventional
`src/` (student-facing) vs. `test/` (hidden, instructor-only) split, but
note the Python plugin does not strictly require a `src/` directory - it's
a convention, not an enforced rule.

Hidden tests are standard `unittest.TestCase` subclasses using the
[`tmc-python-tester`](https://github.com/testmycode/tmc-python-tester)
runner's `@points(...)` decorator to assign point IDs to individual test
methods (see `part01_data_processing/test/test_exercise.py`). Running
`python3 -m tmc` (what `tmc-langs-cli run-tests` shells out to) executes
these and writes `.tmc_test_results.json`.

## How numpy reaches the test run

`tmc-langs-cli run-tests` does **not** create a sandbox or virtualenv
itself when run locally: it shells out to whatever `python3` is first on
`PATH` (or the executable named by the `TMC_LANGS_PYTHON_EXEC` environment
variable) and runs `python3 -m tmc` in the exercise directory
(`crates/plugins/python3/src/plugin.rs::run_tmc_command`). That means:

- **Locally** (this repo, students working on their own machines): numpy
  must be installed into whatever Python `tmc-langs-cli` resolves to. This
  is why `requirements.txt` at the course root lists `numpy` - install it
  with `pip install -r requirements.txt` (a virtualenv is recommended, and
  is exactly how this skeleton was verified - see `## TODO` below for the
  exact venv commands used).
- **On the grading sandbox** (when a submission goes through
  `tmc.mooc.fi`): the actual submission is run in the sandbox image named
  by `.tmcproject.yml`'s `sandbox_image` field (confirmed field, default
  value not published; one documented example value is
  `eu.gcr.io/moocfi-public/tmc-sandbox-python:latest`). Whether that
  default image (or one you'd need to build/point to yourself) has numpy
  preinstalled **could not be confirmed from public documentation** - see
  `## TODO`.

`tmc-python-tester` (the `tmc` package imported by the hidden tests) is
**not published on PyPI** (`pip install tmc-python-tester` / PyPI API both
404) - install it with
`pip install git+https://github.com/testmycode/tmc-python-tester.git`, or
vendor a copy of its `tmc/` package into the course as some real mooc.fi
courses do (seen in course-derived student repos migrating away from a
vendored copy).

## Config files: what's real vs. what's server-side

- **`.tmcproject.yml`** (course root and per-exercise, note the leading
  dot) is parsed by `tmc-langs-cli` itself and merged
  root-then-exercise. Confirmed fields (from the `TmcProjectYml` struct,
  `crates/tmc-langs-framework/src/tmc_project_yml.rs`):
  `extra_student_files`, `extra_exercise_files`, `force_update`,
  `tests_timeout_ms`, `no-tests`, `fail_on_valgrind_error`,
  `minimum_python_version`, `sandbox_image`, `submission_size_limit_mb`.
- **`course_options.yml`** and **`metadata.yml`** are parsed by the
  **TMC server** (`tmc-server` / `tmc.mooc.fi`) when this repository is
  registered or refreshed as a course - `tmc-langs-cli` never reads them
  locally, and there is no reference to `course_options.yml` anywhere in
  the `rage/tmc-langs-rust` source. Confirmed fields, from the TMC webapp
  user manual
  ([testmycode-usermanual.github.io/usermanual/customcourse.html](https://testmycode-usermanual.github.io/usermanual/customcourse.html)):
  - `course_options.yml`: `hidden`, `hide_after`,
    `hidden_if_registered_after`, `locked_exercise_points_visible`,
    `formal_name`, `certificate_downloadable`, `certificate_unlock_spec`.
  - `metadata.yml`: `hidden`, `unlocked_after`, `deadline`,
    `publish_time`, `returnable`, `gdocs_sheet`, `solution_visible_after`,
    `runtime_options`, `valgrind_strategy`,
    `code_review_requests_enabled`, `run_tests_locally_action_enabled`.

## TODO / uncertain (flagged rather than guessed)

- **`hide_type: name`** - the task brief for this skeleton asked for a
  `hide_type` field with `hide_type: name` semantics. No such field
  appears anywhere in the TMC webapp user manual's `course_options.yml` /
  `metadata.yml` documentation, nor in the `rage/tmc-langs-rust` or
  `testmycode/tmc-server` sources searched. It is **not included** in
  `course_options.yml` to avoid fabricating schema. If this maps to a real
  (possibly newer or renamed) field, it needs to be confirmed against the
  live `tmc-server` codebase or by asking course staff who have registered
  a course before adding it.
- **"Points array per part"** - points are not declared as a config-file
  array anywhere. They come from `@points(...)` decorators on individual
  test methods (see `part01_data_processing/test/test_exercise.py`) and
  are computed automatically by `tmc-langs-cli fast-available-points` /
  `scan-exercise`. There is nothing to add to `course_options.yml` for
  this.
- **Deadlines** - not a `course_options.yml` field; they belong in
  `metadata.yml` (`deadline:` key), which this repo sets as a course-wide
  placeholder (`2027-01-01`) - replace before the course actually runs,
  and consider per-part `metadata.yml` files once real dates exist.
- **numpy in the actual mooc.fi grading sandbox** - could not be confirmed
  whether the default/published sandbox image ships numpy. Before
  registering this course for real, either (a) verify with mooc.fi/TMC
  staff, or (b) build and publish a custom sandbox image with numpy baked
  in and reference it via each exercise's `sandbox_image` field (or the
  course-root `.tmcproject.yml`).
- **`mooc-cli`** - could not confirm this tool exists under that name; not
  installed, not referenced further in this skeleton.
- **Exact `TMC_LANGS_PYTHON_EXEC` conventions on the real grading
  sandbox** - only confirmed for local runs; the sandbox likely fixes its
  own Python invocation but this wasn't independently verified.

## Verifying the toolchain locally (what was actually run)

```bash
# one-time local setup (numpy + pytest + the tmc-python-tester runner)
python3 -m venv .venv-tmc-test
.venv-tmc-test/bin/pip install numpy pytest
.venv-tmc-test/bin/pip install git+https://github.com/testmycode/tmc-python-tester.git

export TMC_LANGS_PYTHON_EXEC="$PWD/.venv-tmc-test/bin/python3"
tmc-langs-cli run-tests \
  --exercise-path "$PWD/tmc-course/part01_data_processing" \
  --output-path /tmp/results.json
```

This was run twice against `part01_data_processing`: once with the
unmodified stub (3 of 4 hidden tests correctly failed, confirming the
hidden tests actually check behavior) and once with the reference
`raw_series[~np.isnan(raw_series)]` solution filled in (all 4 tests
passed, `"status":"PASSED"`, correct points `1.1`/`1.1`/`1.2`/`1.2`
awarded) - confirming numpy is usable end-to-end through the real
`tmc-langs-cli` pipeline, not just in isolation.

## Next steps: registering the course on tmc.mooc.fi

1. Push this repository to a Git host reachable by the TMC server
   (GitHub, GitLab, etc.).
2. As course staff, register a new course on
   [tmc.mooc.fi](https://tmc.mooc.fi/) (or the relevant TMC server
   instance) pointing at this repository's URL and branch.
3. The server will run its own course refresh (roughly equivalent to what
   `tmc-langs-cli refresh-course` does locally) to read
   `course_options.yml` / `metadata.yml` and index every part's
   exercises.
4. Resolve the `## TODO` items above (`hide_type`, real deadlines, and the
   sandbox numpy question) before opening the course to students.
5. Flesh out Parts 2-10 with real exercises following the
   `part01_data_processing` pattern (`src/` + `test/__init__.py` +
   `test/test_*.py` + `.tmcproject.yml`).

## Syllabus (planned progression, Parts 2-10 are placeholders only)

1. **Data processing** - loading/reshaping/filtering plasma time series & particle data with numpy (implemented here).
2. **Feature engineering** - windowed, statistical, and spectral features from time series.
3. **Classification of plasma regimes** - supervised classification of solar wind / magnetosheath / foreshock.
4. **Dimensionality reduction on VDFs** - PCA and related linear algebra on velocity distribution functions.
5. **Clustering / unsupervised methods** - k-means and hierarchical clustering on unlabeled plasma data.
6. **Regression & forecasting** - predicting solar wind speed, density, and IMF components.
7. **Anomaly / event detection** - detecting shocks, substorms, and flux ropes.
8. **Neural network basics** - a small feed-forward network implemented from scratch in numpy.
9. **Physics-informed / domain-specific ML** - incorporating MHD/conservation constraints into models.
10. **Capstone project** - end-to-end pipeline on a self-selected space plasma ML problem.
