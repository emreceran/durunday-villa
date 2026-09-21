# -*- coding: utf-8 -*-
"""PDF çıktıları: A3 çizim seti (Chrome headless) ve mahal listesi (LibreOffice)."""
import os, subprocess, tempfile, shutil
from paftalar import PAFTALAR

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def cizim_seti(hedef):
    parcalar = []
    for i, (d, *_) in enumerate(PAFTALAR):
        with open(os.path.join(KOK, "cizimler", d + ".svg"), encoding="utf-8") as f:
            svg = f.read()
        # her paftanın desen / işaretçi kimlikleri ayrı olsun
        svg = svg.replace('id="p-', 'id="s%d-p-' % i).replace("url(#p-", "url(#s%d-p-" % i)
        svg = svg.replace('id="ok', 'id="s%d-ok' % i).replace("url(#ok", "url(#s%d-ok" % i)
        parcalar.append('<div class="p">%s</div>' % svg)
    sayfalar = "".join(parcalar)
    html = ("<html><head><style>@page{size:420mm 297mm;margin:0}body{margin:0}"
            ".p{width:420mm;height:297mm;page-break-after:always;overflow:hidden}"
            ".p svg{width:420mm;height:297mm;display:block}</style></head><body>%s</body></html>" % sayfalar)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        yol = f.name
    subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    "--print-to-pdf=%s" % hedef, "file://" + yol], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(yol)

def mahal_listesi(xlsx, hedef):
    tmp = tempfile.mkdtemp()
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", tmp, xlsx], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    uret = os.path.join(tmp, os.path.splitext(os.path.basename(xlsx))[0] + ".pdf")
    shutil.move(uret, hedef)
    shutil.rmtree(tmp)

if __name__ == "__main__":
    c = os.path.join(KOK, "Durunday Villa - Cizimler.pdf")
    cizim_seti(c)
    m = os.path.join(KOK, "Durunday Villa - Mahal Listesi.pdf")
    if "--sadece-cizim" not in __import__("sys").argv:
        mahal_listesi(os.path.join(KOK, "Durunday Villa - Mahal Listesi.xlsx"), m)
    d = os.path.join(KOK, "docs", "dosyalar")
    os.makedirs(d, exist_ok=True)
    shutil.copy(c, os.path.join(d, "durunday-villa-cizimler.pdf"))
    shutil.copy(m, os.path.join(d, "durunday-villa-mahal-listesi.pdf"))
    for p in (c, m):
        print("%-40s %8d bayt" % (os.path.basename(p), os.path.getsize(p)))
