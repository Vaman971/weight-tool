# Weight Function Calculator

## Overview

The Weight Function Calculator decomposes aircraft structures into
geometric primitives, computes mass and centre of gravity, and validates
the results against benchmark targets.

The repository now supports:

- shared generic component builders for areal, volumetric, and stored-mass primitives
- a categorized loader package under `src/loaders/`
- pluggable input formats: Excel, structured CSV bundles, JSON, and SQLite
- automatic export of structured sample inputs from the legacy Excel data
- Sphinx documentation with cross-platform build instructions

## Supported structures

| Structure | Components | Primitive families |
| --- | --- | --- |
| `cargo_floor` | Panels, C-section struts, cross beams | Areal quads, volumetric quads |
| `pax_floor` | Panels, I-section struts, rails, cross beams | Areal quads, volumetric quads |
| `pax_door` | Frames, intercostals, lintel, sill | Volumetric quads |
| `keel_beam` | Bottom/top/side panels, ribs, stringers, local attachments | Stored-mass hex, quad, bar, point |

## Installation

### Requirements

- Python >= 3.10
- Git

### Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows
.\.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### Install dependencies

```bash
# Runtime + developer tools
pip install -e ".[dev]"

# Runtime + developer tools + docs
pip install -e ".[dev,docs]"
```

Install git hooks if you are contributing:

```bash
pre-commit install
```

## Running the application

Once the virtual environment is active, the runtime commands are the
same on Windows, Linux, and macOS.

```bash
# Run one structure from the bundled Excel sample data
python -m src.main --structure cargo_floor --data-dir ./data

# Run one structure from a flat structure directory
python -m src.main --structure cargo_floor --data-dir /path/to/cargo_floor

# Run all structures from a parent data directory
python -m src.main --structure all --data-dir ./data

# Custom output directory
python -m src.main --structure pax_door --data-dir ./data --output-dir ./results
```

Generated outputs:

- `<structure>_reconciliation.csv`
- `<structure>_geometry.png`

## Structured inputs

The loader layer auto-detects the best available input by component stem.
That means the same structure can be run from:

- the original Excel workbooks
- structured CSV bundles
- structured JSON files
- structured SQLite files

The repository includes an exporter that converts the bundled Excel data
into structured samples derived from the current parsing logic.

```bash
# CSV bundle sample export
python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs --format csv

# JSON export
python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs_json --format json

# SQLite export
python -m src.loaders.export --structure cargo_floor --source-dir ./data --output-dir ./samples/structured_inputs_sqlite --format sqlite
```

Committed sample inputs are available at:

- `samples/structured_inputs/cargo_floor/`
- `samples/structured_inputs_json/cargo_floor/`
- `samples/structured_inputs_sqlite/cargo_floor/`

You can run the CLI directly against any of them:

```bash
python -m src.main --structure cargo_floor --data-dir ./samples/structured_inputs
python -m src.main --structure cargo_floor --data-dir ./samples/structured_inputs_json
python -m src.main --structure cargo_floor --data-dir ./samples/structured_inputs_sqlite
```

### CSV bundle layout

```text
samples/structured_inputs/cargo_floor/
|- CARGO_FLOOR_PANEL/
|  |- metadata.json
|  `- primitives.csv
|- C_SECTION_STRUCT/
|  |- metadata.json
|  `- primitives.csv
|- CARGO_BEAMS/
|  |- metadata.json
|  `- primitives.csv
|- INPUTS/
|  |- datums.csv
|  `- frame_coords.csv
`- VALIDATION/
   `- targets.csv
```

## Architecture

### Main flow

```text
inputs -> src/loaders -> COMPONENT_REGISTRY -> component builders -> WeightFunction -> validation
```

### Shared generic builders

| Generic | Module | Used by |
| --- | --- | --- |
| `GenericArealSurface` | `src/components/generic/areal_surface.py` | cargo floor panels, PAX floor panels |
| `GenericVolumetricBeam` | `src/components/generic/volumetric_beam.py` | cargo struts, cargo beams, PAX struts, PAX rails, PAX cross beams, PAX door components |
| `GenericStoredMassComponent` | `src/components/generic/stored_mass.py` | all keel beam components |

### Loader package

```text
src/loaders/
|- common.py
|- cargo_floor.py
|- pax_floor.py
|- pax_door.py
|- keel_beam.py
|- auxiliary.py
`- export.py
```

`src/data_loader.py` remains as a compatibility shim so existing imports
continue to work.

## Testing

```bash
pytest
pytest -v
pytest --cov=src
```

The suite includes:

- synthetic component tests
- real workbook loader integration tests
- structured input plug-in tests for CSV, JSON, and SQLite
- CLI pipeline tests using exported structured bundles

## Documentation

After the virtual environment is active, the canonical Sphinx commands
are cross-platform:

```bash
python -m sphinx -M clean docs/source docs/build
python -m sphinx -M html docs/source docs/build
python -m sphinx -M dirhtml docs/source docs/build
python -m sphinx -M linkcheck docs/source docs/build
```

Platform-specific shortcuts:

```bash
# Linux / macOS, from docs/
make html

# Windows, from docs/
.\make.bat html
```

If you are on a restricted network:

```powershell
$env:SPHINX_OFFLINE = "1"
python -m sphinx -M html docs/source docs/build
Remove-Item Env:SPHINX_OFFLINE
```

## License

Proprietary - Airbus Amber. All rights reserved.
