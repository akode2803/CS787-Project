import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pdfkit import *
import refs
import content1, content2, content3, content4

OUT = sys.argv[1] if len(sys.argv) > 1 else "blueprint.pdf"


def build(out):
    doc = Doc(out, title="Goal Revision in Long-Running LLM Agents — Project Blueprint (CS787, draft v0.1)",
              author="CS787 Group 13 (prepared with Claude)", subject="Research design, source investigation and execution plan")
    toc = make_toc()
    story = []
    story += content1.title_page(toc)
    story += content1.sec1(); story += content1.sec2(); story += content1.sec3()
    story += content2.sec4(); story += content2.sec5(); story += content2.sec6()
    story += content3.sec7(); story += content3.sec8(); story += content3.sec9()
    story += content4.sec10(); story += content4.sec11(); story += content4.sec12()
    story += content4.sec13(); story += content4.sec14(); story += content4.appendix()
    final = []
    i = 0
    while i < len(story):
        fl = story[i]
        if isinstance(fl, H):
            nxt = story[i + 1] if i + 1 < len(story) else None
            if isinstance(nxt, KeepTogether):          # heading followed by a figure: keep them on one page
                final.append(CondPageBreak(20 * mm))
                final.append(KeepTogether([fl] + list(nxt._content))); i += 2; continue
            final.append(CondPageBreak((62 if fl.level == 1 else 48) * mm))
        elif isinstance(fl, Paragraph) and getattr(fl.style, 'name', '') == 'H3':
            final.append(CondPageBreak(30 * mm))
        final.append(fl); i += 1
    doc.multiBuild(final)
    return doc.page


import pdfkit
pdfkit.TOTAL[0] = 0
n = build(OUT)          # pass 1: learn the page count
pdfkit.TOTAL[0] = n
n2 = build(OUT)         # pass 2: draw "Page x of n"
assert n == n2, (n, n2)
print("built", OUT, "pages:", n)
