"""Layout helpers for the blueprint PDF (reportlab / platypus)."""
import os
import matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether, Image, ListFlowable, ListItem, CondPageBreak, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfgen import canvas as rl_canvas

# ---------------------------------------------------------------- fonts
FONT_DIR = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
for name, fn in (("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DV-I", "DejaVuSans-Oblique.ttf"),
                 ("DV-BI", "DejaVuSans-BoldOblique.ttf"), ("DVM", "DejaVuSansMono.ttf"), ("DVM-B", "DejaVuSansMono-Bold.ttf")):
    pdfmetrics.registerFont(TTFont(name, os.path.join(FONT_DIR, fn)))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")
pdfmetrics.registerFontFamily("DVM", normal="DVM", bold="DVM-B", italic="DVM", boldItalic="DVM-B")

# ---------------------------------------------------------------- tokens
INK = colors.HexColor("#0b0b0b"); INK2 = colors.HexColor("#52514e"); MUTED = colors.HexColor("#898781")
GRID = colors.HexColor("#d9d8d0"); BLUE = colors.HexColor("#2a78d6"); BLUE_D = colors.HexColor("#184f95")
BLUE_L = colors.HexColor("#eaf2fc"); ORANGE = colors.HexColor("#eb6834"); ORANGE_L = colors.HexColor("#fdf0ea")
GREY_L = colors.HexColor("#f4f3ef"); ZEBRA = colors.HexColor("#f8f8f5"); AQUA_L = colors.HexColor("#e8f6f0")
RED_L = colors.HexColor("#fbeaea"); YEL_L = colors.HexColor("#fdf4dc")
LINK = "#1c5cab"

PAGE_W, PAGE_H = A4
MARGIN_X = 17 * mm
TEXT_W = PAGE_W - 2 * MARGIN_X

# evidence tags (inline)
TAG_V = '<font color="#006300"><b>[V]</b></font>'   # verified in a primary source during this session
TAG_R = '<font color="#1c5cab"><b>[R]</b></font>'   # reported by the authors of a cited source, not independently re-run
TAG_O = '<font color="#6250d6"><b>[O]</b></font>'   # observed/computed by us in a small check
TAG_H = '<font color="#a14a00"><b>[H]</b></font>'   # hypothesis, design proposal or planning assumption
TAG_U = '<font color="#b02a2a"><b>[U]</b></font>'   # unverified / unknown / open

# ---------------------------------------------------------------- styles
def S(name, **kw):
    base = dict(fontName="DV", fontSize=8.6, leading=11.9, textColor=INK, alignment=TA_LEFT, spaceAfter=0, spaceBefore=0)
    base.update(kw)
    return ParagraphStyle(name, **base)

ST = {
    "Body": S("Body", spaceAfter=4.2),
    "BodyTight": S("BodyTight", spaceAfter=2),
    "Small": S("Small", fontSize=7.4, leading=9.8, textColor=INK2, spaceAfter=3),
    "Caption": S("Caption", fontSize=7.3, leading=9.6, textColor=INK2, spaceBefore=2, spaceAfter=7),
    "H1": S("H1", fontName="DV-B", fontSize=14.2, leading=17.5, textColor=INK, spaceBefore=8, spaceAfter=7),
    "H2": S("H2", fontName="DV-B", fontSize=10.3, leading=13.4, textColor=BLUE_D, spaceBefore=8, spaceAfter=3.5),
    "H3": S("H3", fontName="DV-B", fontSize=8.8, leading=11.6, textColor=INK, spaceBefore=5, spaceAfter=2),
    "H3nk": S("H3nk", fontName="DV-B", fontSize=8.8, leading=11.6, textColor=INK, spaceBefore=5, spaceAfter=2),
    "Cell": S("Cell", fontSize=7.35, leading=9.5),
    "CellB": S("CellB", fontName="DV-B", fontSize=7.35, leading=9.5),
    "CellH": S("CellH", fontName="DV-B", fontSize=7.35, leading=9.5, textColor=INK),
    "Mono": S("Mono", fontName="DVM", fontSize=6.9, leading=8.9, textColor=INK, spaceAfter=4),
    "Title": S("Title", fontName="DV-B", fontSize=23, leading=27, textColor=INK, spaceAfter=3),
    "Subtitle": S("Subtitle", fontSize=10.5, leading=14.2, textColor=INK2, spaceAfter=8),
    "TOC1": S("TOC1", fontName="DV-B", fontSize=8.8, leading=13.2, leftIndent=0, spaceBefore=1.5),
    "TOC2": S("TOC2", fontSize=7.6, leading=10, leftIndent=14, textColor=INK2),
    "Bib": S("Bib", fontSize=7.5, leading=10, leftIndent=18, firstLineIndent=-18, spaceAfter=2.6),
}


def P(text, style="Body"):
    return Paragraph(text, ST[style] if isinstance(style, str) else style)


class H(Paragraph):
    """Heading paragraph that registers itself for the TOC / PDF outline."""
    def __init__(self, text, level):
        super().__init__(text, ST["H1" if level == 1 else "H2"])
        self.level = level


def H1(t): return H(t, 1)
def H2(t): return H(t, 2)
def H3(t): return Paragraph(t, ST["H3"])


def bullets(items, style="Body", indent=11, gap=1.6):
    flow = [ListItem(Paragraph(t, ST[style]), leftIndent=indent, bulletColor=INK2) for t in items]
    return ListFlowable(flow, bulletType="bullet", start="•", leftIndent=indent, bulletFontSize=7, bulletOffsetY=-0.3,
                        spaceAfter=gap + 2)


def numbered(items, style="Body", indent=13):
    flow = [ListItem(Paragraph(t, ST[style]), leftIndent=indent) for t in items]
    return ListFlowable(flow, bulletType="1", leftIndent=indent, bulletFontName="DV", bulletFontSize=7.6, spaceAfter=4)


def tbl(rows, widths, header=True, zebra=True, style_cell="Cell", repeat=1, extra=None, keep=False, align_top=True):
    """rows: list of lists of str/Flowable. widths: relative weights, scaled to TEXT_W."""
    tot = float(sum(widths)); cw = [TEXT_W * w / tot for w in widths]
    data = []
    for i, r in enumerate(rows):
        row = []
        for c in r:
            if isinstance(c, str):
                row.append(Paragraph(c, ST["CellH"] if (header and i == 0) else ST[style_cell]))
            else:
                row.append(c)
        data.append(row)
    t = Table(data, colWidths=cw, repeatRows=repeat if header else 0, splitByRow=1)
    cmds = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.2),
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, GRID), ("LINEABOVE", (0, 0), (-1, 0), 0.8, MUTED)]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), GREY_L), ("LINEBELOW", (0, 0), (-1, 0), 0.8, MUTED)]
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if (i % 2) == 0:
                cmds.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    if extra: cmds += extra
    t.setStyle(TableStyle(cmds))
    t.spaceAfter = 6
    return KeepTogether([t]) if keep else t


def callout(title, body_paras, kind="blue"):
    bg, bar = {"blue": (BLUE_L, BLUE), "orange": (ORANGE_L, ORANGE), "green": (AQUA_L, colors.HexColor("#1baf7a")),
               "red": (RED_L, colors.HexColor("#e34948")), "grey": (GREY_L, MUTED)}[kind]
    inner = [Paragraph(f"<b>{title}</b>", ST["BodyTight"])] if title else []
    inner += [Paragraph(b, ST["Cell"] if False else S("co", fontSize=8.1, leading=11, spaceAfter=2)) for b in body_paras]
    t = Table([[inner]], colWidths=[TEXT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), bg), ("LINEBEFORE", (0, 0), (0, -1), 2.6, bar),
                           ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    t.spaceAfter = 7
    return t


def figure(path, caption, width=TEXT_W):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w, h = im.size
    img = Image(path, width=width, height=width * h / w)
    return KeepTogether([img, Paragraph(caption, ST["Caption"])])


def mono(text):
    import html as _h
    t = _h.escape(text, quote=False)
    return Paragraph(t.replace("\n", "<br/>").replace(" ", "&nbsp;"), ST["Mono"])


def codebox(text):
    t = Table([[mono(text)]], colWidths=[TEXT_W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GREY_L), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    t.spaceAfter = 6
    return KeepTogether([t])


# ---------------------------------------------------------------- citations
REFS = []   # (key, html)
_IDX = {}

def register_refs(items):
    for k, html in items:
        _IDX[k] = len(REFS) + 1
        REFS.append((k, html))

def c(*keys):
    parts = [f'<a href="#ref_{k}" color="{LINK}">{_IDX[k]}</a>' for k in keys]
    return "[" + ", ".join(parts) + "]"

def link(url, text=None):
    return f'<a href="{url}" color="{LINK}">{text or url}</a>'


# ---------------------------------------------------------------- doc template
class NumberedCanvas(rl_canvas.Canvas):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw); self._saved = []
    def showPage(self):
        self._saved.append(dict(self.__dict__)); self._startPage()
    def save(self):
        n = len(self._saved)
        for st in self._saved:
            self.__dict__.update(st); self._draw_chrome(n); super().showPage()
        super().save()
    def _draw_chrome(self, n):
        pg = self._pageNumber
        if pg == 1:
            return
        self.setFont("DV", 6.9); self.setFillColor(MUTED)
        self.drawString(MARGIN_X, PAGE_H - 11.5 * mm, "CS787 · Goal Revision in Long-Running LLM Agents · Project Blueprint (draft v0.1, 28 Oct 2026)")
        self.setStrokeColor(GRID); self.setLineWidth(0.5); self.line(MARGIN_X, PAGE_H - 13 * mm, PAGE_W - MARGIN_X, PAGE_H - 13 * mm)
        self.drawRightString(PAGE_W - MARGIN_X, 9.5 * mm, f"Page {pg} of {n}")
        self.drawString(MARGIN_X, 9.5 * mm, "Evidence tags: [V] verified  [R] reported  [O] observed by us  [H] hypothesis/plan  [U] unverified")


TOTAL = [0]


def draw_chrome(canv, doc):
    pg = doc.page
    if pg == 1:
        return
    canv.saveState()
    canv.setFont("DV", 6.9); canv.setFillColor(MUTED)
    canv.drawString(MARGIN_X, PAGE_H - 11.5 * mm, "CS787 · Goal Revision in Long-Running LLM Agents · Project Blueprint (draft v0.1, 28 Oct 2026)")
    canv.setStrokeColor(GRID); canv.setLineWidth(0.5); canv.line(MARGIN_X, PAGE_H - 13 * mm, PAGE_W - MARGIN_X, PAGE_H - 13 * mm)
    canv.drawRightString(PAGE_W - MARGIN_X, 9.5 * mm, f"Page {pg} of {TOTAL[0] or '?'}")
    canv.drawString(MARGIN_X, 9.5 * mm, "Evidence tags: [V] verified  [R] reported  [O] observed by us  [H] hypothesis/plan  [U] unverified")
    canv.restoreState()


class Doc(BaseDocTemplate):
    def __init__(self, fn, **kw):
        super().__init__(fn, pagesize=A4, leftMargin=MARGIN_X, rightMargin=MARGIN_X, topMargin=18 * mm, bottomMargin=16 * mm,
                         title=kw.get("title", ""), author=kw.get("author", ""), subject=kw.get("subject", ""))
        fr = Frame(MARGIN_X, 16 * mm, TEXT_W, PAGE_H - 34 * mm, id="f", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="main", frames=[fr], onPage=draw_chrome)])
        self._hcount = 0

    def beforeDocument(self):
        self._hcount = 0

    def afterFlowable(self, fl):
        if isinstance(fl, H):
            self._hcount += 1
            key = f"h{self._hcount}"
            text = fl.getPlainText()
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, fl.level - 1, 0)
            if fl.level == 1:
                self.notify("TOCEntry", (0, text, self.page, key))


def make_toc():
    toc = TableOfContents()
    toc.levelStyles = [ST["TOC1"]]
    toc.tableStyle = TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                 ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)])
    toc.dotsMinLevel = 0
    return toc
