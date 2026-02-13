# aeat-code2txt

Render AEAT fixed‑position reports (e.g. Models 303 and 390) from official XLSX layouts.

This library converts an AEAT XLSX layout into per‑sheet CSVs, parses the
layout definition, and renders fixed‑width text files using a single JSON
input (codes + non‑code fields).

## Layout source

The official layout XLSX files are stored here:

- `data/DR303e26v101.xlsx`
- `data/dr390e2025.xlsx`

Generated artifacts (303):

- `csv_x2c_303/` – per‑sheet CSVs (canonical)
- `aeat_code2txt/layouts/layouts_303.json` – bundled JSON layout (runtime input)
- `examples/fields_303.json` – full field catalog with metadata
- `examples/keys_303.json` – non‑code field keys (template)
- `examples/data_303.json` – merged input (codes + keys)
- `examples/output_303.txt` – sample render

Generated artifacts (390):

- `csv_x2c_390/` – per‑sheet CSVs
- `aeat_code2txt/layouts/layouts_390.json` – bundled JSON layout

## Quickstart

Regenerate everything from the XLSX:

```bash
scripts/regenerate_all.sh data/DR303e26v101.xlsx
```

If `data/dr390e2025.xlsx` exists, the script also generates the 390 artifacts.

- `csv_x2c_390/`
- `aeat_code2txt/layouts/layouts_390.json`

Render from a single JSON input:

```bash
PYTHONPATH=. python3 scripts/render_report.py \
  csv_x2c_303 \
  --data-json examples/data_303.json \
  --output examples/output_303.txt
```

Load bundled layout by model (recommended for runtime):

```python
from aeat_code2txt import load_layout

layout = load_layout("303")
```

Load model 390:

```python
layout = load_layout("390")
```

Strict mode (error on unknown keys):

```python
text = render_report(layout, data=data, strict=True)
```

## Single JSON input

You can supply a **single JSON** that mixes:

- numeric keys → AEAT codes (e.g. `"01": 1000.0`)
- non‑numeric keys → extra values (e.g. `"identificacion_1_nif": "B12345678"`)

See `examples/data_303.json`.

## Field keys (non‑code)

Fields without `[NN]` codes get an auto key derived from the description:

- lowercased
- accents stripped (e.g., `identificación` → `identificacion`)
- non‑alphanumeric → `_`

You can export the full key template:

```bash
PYTHONPATH=. python3 scripts/export_keys.py csv_x2c_303 --output examples/keys_303.json
```

## Full field catalog

To inspect every field (codes + non‑codes) with metadata:

```bash
PYTHONPATH=. python3 scripts/export_fields.py csv_x2c_303 --output examples/fields_303.json
```

Each entry includes:

- record name
- position/length/type
- code/key
- constant, decimals, formula (if any)
- description/validation/content

## Layout JSON (runtime)

Use the bundled JSON layouts at runtime instead of parsing CSVs:

```python
from aeat_code2txt import load_layout, render_report

layout = load_layout("303")
text = render_report(layout, data=data)
```

CSV parsing is only needed when the XLSX layout changes.

## Rendering API

```python
from decimal import Decimal
from aeat_code2txt import load_layout, render_report

layout = load_layout("303")
data = {"01": Decimal("1000.00"), "identificacion_1_nif": "B12345678"}

text = render_report(layout, data=data)
```

Hooks are supported:

- `pre_record_hooks(record, context)`
- `value_hooks(field, raw_value, context) -> str`
- `post_record_hooks(record, rendered_text, context) -> str`

## Reverse parsing (TXT → JSON)

```python
from aeat_code2txt import load_layout, parse_report, validate_report

layout = load_layout("303")
data = parse_report(text, layout)
issues = validate_report(text, layout)
```

`parse_report` returns a flat dict with both codes and keys.  
`validate_report` checks constants and formulas and returns a list of issues.

## Tests

```bash
python3 -m unittest discover -s tests
```

## Notes

- The CSV parsing is driven by the official XLSX.
- Formulas in the description are interpreted as simple `[NN]` sums/subtractions.
- Constants are extracted from `Contenido` when possible.
