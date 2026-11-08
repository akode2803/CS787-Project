# Blueprint PDF source

Rebuilds `../../CS787_Goal_Revision_Project_Blueprint.pdf` (23 pages) from Python sources.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install reportlab matplotlib pillow
python figs.py                      # diagrams -> fig/*.png
python build_pdf.py ../../CS787_Goal_Revision_Project_Blueprint.pdf   # builds in two passes (page count, then chrome)
```

- `content1.py` … `content4.py`: the sections; `refs.py`: bibliography; `pdfkit.py`: layout helpers; `figs.py`: figures; `power.py`: exact McNemar minimum-detectable-difference computation (also embedded in `content3.py`).
- Tested only with the versions installed on 2026-10-28 (Python 3.14, reportlab 5.1.0, matplotlib 3.11.2).
- Edit text in the `content*.py` files; every non-obvious claim carries an evidence tag ([V]/[R]/[O]/[H]/[U]).
