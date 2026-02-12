# AGENTS.md

## Project goals

- Parse official AEAT layout XLSX into structured layout definitions.
- Render fixed‑position TXT reports from a single JSON input.
- Keep regeneration deterministic and scriptable.

## Key paths

- XLSX source: `data/DR303e26v101.xlsx`
- Canonical CSV output: `csv_x2c/`
- Scripts: `scripts/`
- Examples: `examples/`
- Library: `aeat_code2txt/`

## Regeneration

Always use the regeneration script to update derived artifacts:

```bash
scripts/regenerate_all.sh data/DR303e26v101.xlsx
```

This rebuilds:

- `csv_x2c/`
- `examples/keys_303.json`
- `examples/fields_303.json`
- `examples/data_303.json`
- `examples/output_303.txt`

## Conventions

- Use ASCII in source files unless the file already uses UTF‑8 for descriptions.
- Keep parsing logic robust to accents and minor formatting changes.
- Avoid hard‑coding report layouts in code; prefer the XLSX/CSV input.
- Keep formulas simple ([NN] + [NN] - [NN]) and evaluate deterministically.

## Testing

```bash
python3 -m unittest discover -s tests
```
