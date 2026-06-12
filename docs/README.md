# Documentation index

Documentation for the Berton (2023) cirrus parcel reference implementation.

- `MODEL_EXTRACTION.md` — extraction record and implementation status for the Berton (2023) model.
- `berton2023-model-code.md` — practical guide to `src/cloud_rom/berton2023.py` for humans and coding agents.
- `notebooks.md` — inventory and purpose of notebooks in `notebooks/`.
- `berton-2023-pdftotext.txt` — PDF text extraction using `pdftotext -layout`.
- `berton-2023-raw.txt` — PDF text extraction using `pdftotext -raw`.

Validation commands:

```bash
uv run pytest -q
uv run pyright
```
