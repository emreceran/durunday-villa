# -*- coding: utf-8 -*-
"""Durunday Villa — kat planı / vaziyet / kesit SVG üreticisi. veri.py'den beslenir."""
import os, math
from veri import (KATLAR, BINA, PARSEL, DIS_DUVAR, IC_DUVAR, KAT_YUKSEKLIK,
                  NET_TAVAN, net_alan, kat_ozeti)

S = 100.0                    # 1 m = 100 birim  (1:100 ölçek)
M = 190                      # kenar boşluğu
KAPI = 0.90
GIRIS_KAPI = 1.10
GARAJ_KAPI = 5.00
SURME = 2.60
ACIK_GECIS = [("Z-01","Z-02"), ("Z-02","Z-06"), ("K-01","K-02"), ("B-02","B-05")]

RENK = {
 "yasam":      "#eaf2fb", "ikincil": "#eef4fb", "yatak": "#f2f6ec",
 "islak":      "#e6f3f4", "mutfak":  "#fdf3e4", "sirkulasyon": "#f4f2ee",
 "teknik":     "#f0f0f2", "acik":    "#edf6ec",
}
DUVAR = "#1f2937"
CIZGI = "#4b5563"

def x(v): return M + v * S
def y(v): return M + v * S

def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

# ----------------------------------------------------------------- yardımcılar
def komsuluk(mahaller):
    """Ortak duvar parçalarını bulur: (a, b, yon, p0, p1, sabit)"""
    ortak = []
    for i, a in enumerate(mahaller):
        for b in mahaller[i+1:]:
            ax0, ay0, ax1, ay1 = a[2], a[3], a[4], a[5]
            bx0, by0, bx1, by1 = b[2], b[3], b[4], b[5]
            if abs(ax1 - bx0) < 1e-6 or abs(bx1 - ax0) < 1e-6:      # düşey duvar
                sabit = ax1 if abs(ax1 - bx0) < 1e-6 else ax0
                p0, p1 = max(ay0, by0), min(ay1, by1)
                if p1 - p0 > 0.3:
                    ortak.append((a, b, "d", p0, p1, sabit))
            if abs(ay1 - by0) < 1e-6 or abs(by1 - ay0) < 1e-6:      # yatay duvar
                sabit = ay1 if abs(ay1 - by0) < 1e-6 else ay0
                p0, p1 = max(ax0, bx0), min(ax1, bx1)
                if p1 - p0 > 0.3:
                    ortak.append((a, b, "y", p0, p1, sabit))
    return ortak

def kapi_yerlestir(mahaller):
    """Her mahal için sirkülasyona (yoksa en büyük komşuya) 1 kapı."""
    ortaklar = komsuluk(mahaller)
    kapilar = []
    kullanildi = set()
    for r in mahaller:
        if "Asansör" in r[1] or "şaft" in r[1]:
            continue
        adaylar = []
        for a, b, yon, p0, p1, sabit in ortaklar:
            if a[0] == r[0]:
                diger = b
            elif b[0] == r[0]:
                diger = a
            else:
                continue
            if p1 - p0 < 1.10:
                continue
            if r[6] == "acik":
                oncelik = 3 if diger[6] == "acik" else 0
            else:
                oncelik = 0 if diger[6] == "sirkulasyon" else (1 if diger[6] != "acik" else 3)
            adaylar.append((oncelik, -(p1 - p0), yon, p0, p1, sabit, diger))
        if not adaylar:
            continue
        adaylar.sort()
        _, _, yon, p0, p1, sabit, diger = adaylar[0]
        gen = GIRIS_KAPI if (r[1].startswith("Antre")) else (SURME if r[6] == "acik" else KAPI)
        orta = (p0 + p1) / 2
        anahtar = (yon, round(sabit, 2), round(orta, 2))
        if anahtar in kullanildi:
            continue
        kullanildi.add(anahtar)
        kapilar.append((yon, sabit, orta - gen / 2, orta + gen / 2, r, diger))
    return kapilar

def gecis_yerlestir(mahaller):
    """Duvarında kapı kanadı olmayan geniş açıklıklar (salon-yemek gibi)."""
    kod = {r[0]: r for r in mahaller}
    cikti = []
    for a_kod, b_kod in ACIK_GECIS:
        if a_kod not in kod or b_kod not in kod:
            continue
        a, b = kod[a_kod], kod[b_kod]
        for aa, bb, yon, p0, p1, sabit in komsuluk([a, b]):
            gen = min(3.2, (p1 - p0) - 0.4)
            if gen < 1.2:
                continue
            orta = (p0 + p1) / 2
            cikti.append((yon, sabit, orta - gen/2, orta + gen/2))
    return cikti

def pencere_yerlestir(mahaller):
    p = []
    for r in mahaller:
        if r[6] in ("acik",) or "Asansör" in r[1] or "şaft" in r[1]:
            continue
        kenarlar = []
        if r[3] <= 1e-6:  kenarlar.append(("y", 0.0, r[2], r[4]))
        if r[5] >= BINA["boy"] - 1e-6: kenarlar.append(("y", BINA["boy"], r[2], r[4]))
        if r[2] <= 1e-6:  kenarlar.append(("d", 0.0, r[3], r[5]))
        if r[4] >= BINA["en"] - 1e-6:  kenarlar.append(("d", BINA["en"], r[3], r[5]))
        for yon, sabit, a, b in kenarlar:
            uz = b - a
            if uz < 1.8:
                continue
            gen = max(1.2, min(3.0, uz * 0.55))
            orta = (a + b) / 2
            p.append((yon, sabit, orta - gen / 2, orta + gen / 2, r))
    return p

# ----------------------------------------------------------------- çizim parçaları
def duvarlar_svg(mahaller):
    o = []
    t = DIS_DUVAR
    # dış duvar (çerçeve)
    o.append('<path d="M %.1f %.1f H %.1f V %.1f H %.1f Z M %.1f %.1f H %.1f V %.1f H %.1f Z" '
             'fill="%s" fill-rule="evenodd"/>' % (
        x(-t/2), y(-t/2), x(BINA["en"]+t/2), y(BINA["boy"]+t/2), x(-t/2),
        x(t/2), y(t/2), x(BINA["en"]-t/2), y(BINA["boy"]-t/2), x(t/2), DUVAR))
    # iç duvarlar
    for a, b, yon, p0, p1, sabit in komsuluk(mahaller):
        if yon == "d":
            o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (
                x(sabit - IC_DUVAR/2), y(p0), IC_DUVAR*S, (p1-p0)*S, DUVAR))
        else:
            o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (
                x(p0), y(sabit - IC_DUVAR/2), (p1-p0)*S, IC_DUVAR*S, DUVAR))
    return "\n".join(o)

def acikliklar_svg(kapilar, pencereler, garaj=None, giris=None):
    o = []
    def bosluk(yon, sabit, a, b, t):
        if yon == "d":
            return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ffffff"/>' % (
                x(sabit - t/2 - 0.02), y(a), (t + 0.04)*S, (b-a)*S)
        return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#ffffff"/>' % (
            x(a), y(sabit - t/2 - 0.02), (b-a)*S, (t + 0.04)*S)

    for yon, sabit, a, b in (garaj or []):
        o.append(bosluk(yon, sabit, a, b, IC_DUVAR))
    for yon, sabit, a, b, r, diger in kapilar:
        dis = (sabit <= 1e-6 or (yon == "d" and sabit >= BINA["en"]-1e-6)
               or (yon == "y" and sabit >= BINA["boy"]-1e-6))
        t = DIS_DUVAR if dis else IC_DUVAR
        o.append(bosluk(yon, sabit, a, b, t))
        g = b - a
        if g >= 3.0:                                       # seksiyonel garaj kapısı
            if yon == "y":
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="5"/>'
                         % (x(a), y(sabit), x(b), y(sabit), CIZGI))
                for i in range(1, 6):
                    xx = a + (b - a) * i / 6.0
                    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>'
                             % (x(xx), y(sabit-0.14), x(xx), y(sabit+0.14), CIZGI))
            else:
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="5"/>'
                         % (x(sabit), y(a), x(sabit), y(b), CIZGI))
            continue
        if r[6] == "acik" or diger[6] == "acik":          # sürme kapı
            if yon == "d":
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4"/>'
                         % (x(sabit-0.05), y(a), x(sabit-0.05), y(a+g*0.55), CIZGI))
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4"/>'
                         % (x(sabit+0.05), y(b-g*0.55), x(sabit+0.05), y(b), CIZGI))
            else:
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4"/>'
                         % (x(a), y(sabit-0.05), x(a+g*0.55), y(sabit-0.05), CIZGI))
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4"/>'
                         % (x(b-g*0.55), y(sabit+0.05), x(b), y(sabit+0.05), CIZGI))
            continue
        if yon == "d":
            o.append('<path d="M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                     'fill="none" stroke="%s" stroke-width="2"/>' % (
                x(sabit), y(a), x(sabit + g), y(a), g*S, g*S, x(sabit), y(a + g), CIZGI))
            o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4"/>' % (
                x(sabit), y(a), x(sabit + g), y(a), CIZGI))
        else:
            o.append('<path d="M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f" '
                     'fill="none" stroke="%s" stroke-width="2"/>' % (
                x(a), y(sabit), x(a), y(sabit + g), g*S, g*S, x(a + g), y(sabit), CIZGI))
            o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="4"/>' % (
                x(a), y(sabit), x(a), y(sabit + g), CIZGI))

    for yon, sabit, a, b, r in pencereler:
        t = DIS_DUVAR
        o.append(bosluk(yon, sabit, a, b, t))
        if yon == "y":
            for dy in (-t/2, -t/6, t/6, t/2):
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (
                    x(a), y(sabit+dy), x(b), y(sabit+dy), CIZGI))
        else:
            for dx in (-t/2, -t/6, t/6, t/2):
                o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (
                    x(sabit+dx), y(a), x(sabit+dx), y(b), CIZGI))
    return "\n".join(o)

def merdiven_svg(r, yon_yukari=True):
    """Mahal içine 11 basamaklı merdiven kolu + sahanlık."""
    x0, y0, x1, y1 = r[2]+0.1, r[3]+0.1, r[4]-0.1, r[5]-0.1
    o = []
    kol = 1.20
    n = 10
    h = (y1 - y0 - 1.2) / n
    for i in range(n):
        yy = y0 + 0.6 + i*h
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (
            x(x0+0.25), y(yy), x(x0+0.25+kol), y(yy), CIZGI))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="2"/>' % (
        x(x0+0.25), y(y0+0.6), kol*S, (n*h)*S, CIZGI))
    ox = x0 + 0.25 + kol/2
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="3" marker-end="url(#ok)"/>' % (
        x(ox), y(y1-0.5), x(ox), y(y0+0.5), "#b45309"))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">ÇIKIŞ</text>' % (
        x(ox+0.75), y(y0+1.2)))
    return "\n".join(o)

def asansor_svg(r):
    x0, y0, x1, y1 = r[2]+0.25, r[3]+0.25, r[4]-0.25, r[5]-0.25
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="%s" stroke-width="2"/>'
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>'
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2"/>' % (
        x(x0), y(y0), (x1-x0)*S, (y1-y0)*S, CIZGI,
        x(x0), y(y0), x(x1), y(y1), CIZGI, x(x1), y(y0), x(x0), y(y1), CIZGI))

def etiket_svg(r):
    a, dar, uzun = net_alan(r)
    cx = (r[2] + r[4]) / 2
    cy = (r[3] + r[5]) / 2
    if "erdiven" in r[1]:
        cy = r[5] - 0.75
    if "Asansör" in r[1]:
        cy = r[5] - 0.30
    genis = (r[4] - r[2]) * S
    o = ['<text x="%.1f" y="%.1f" class="kod" text-anchor="middle">%s</text>' % (x(cx), y(cy) - 14, esc(r[0]))]
    ad = esc(r[1])
    if len(ad) * 9 > genis and " " in ad:
        p = ad.rsplit(" ", 1)
        o.append('<text x="%.1f" y="%.1f" class="ad" text-anchor="middle">%s</text>' % (x(cx), y(cy) + 2, p[0]))
        o.append('<text x="%.1f" y="%.1f" class="ad" text-anchor="middle">%s</text>' % (x(cx), y(cy) + 17, p[1]))
        o.append('<text x="%.1f" y="%.1f" class="alan" text-anchor="middle">%.1f m²</text>' % (x(cx), y(cy) + 33, a))
    else:
        o.append('<text x="%.1f" y="%.1f" class="ad" text-anchor="middle">%s</text>' % (x(cx), y(cy) + 4, ad))
        o.append('<text x="%.1f" y="%.1f" class="alan" text-anchor="middle">%.1f m²</text>' % (x(cx), y(cy) + 20, a))
    return "\n".join(o)

def olcu_cizgisi(x0, y0, x1, y1, metin, ofset=0):
    """Basit ölçü çizgisi (yatay veya düşey)."""
    o = []
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5"/>' % (x0, y0, x1, y1, CIZGI))
    if abs(y1 - y0) < 1:
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5"/>' % (x0, y0-6, x0, y0+6, CIZGI))
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5"/>' % (x1, y1-6, x1, y1+6, CIZGI))
        o.append('<text x="%.1f" y="%.1f" class="olcu" text-anchor="middle">%s</text>' % ((x0+x1)/2, y0-8, metin))
    else:
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5"/>' % (x0-6, y0, x0+6, y0, CIZGI))
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5"/>' % (x1-6, y1, x1+6, y1, CIZGI))
        o.append('<text x="%.1f" y="%.1f" class="olcu" text-anchor="middle" transform="rotate(-90 %.1f %.1f)">%s</text>' % (
            x0-8, (y0+y1)/2, x0-8, (y0+y1)/2, metin))
    return "\n".join(o)

BASLIK_YUK = 150
def cerceve_svg(w, h, baslik, altbaslik, sag_bilgi):
    o = []
    o.append('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (w, h))
    o.append('<rect x="18" y="18" width="%d" height="%d" fill="none" stroke="%s" stroke-width="3"/>' % (w-36, h-36, DUVAR))
    ty = h - 18 - BASLIK_YUK
    o.append('<rect x="18" y="%d" width="%d" height="%d" fill="#f8fafc" stroke="%s" stroke-width="3"/>' % (ty, w-36, BASLIK_YUK, DUVAR))
    o.append('<text x="46" y="%d" class="baslik">%s</text>' % (ty + 52, esc(baslik)))
    o.append('<text x="46" y="%d" class="altb">%s</text>' % (ty + 88, esc(altbaslik)))
    o.append('<text x="46" y="%d" class="kucuk">%s</text>' % (ty + 120, esc(sag_bilgi)))
    o.append('<text x="%d" y="%d" class="altb" text-anchor="end">DURUNDAY VİLLA</text>' % (w-46, ty + 52))
    o.append('<text x="%d" y="%d" class="kucuk" text-anchor="end">Konya / Meram / Durunday — Bodrumlu dubleks villa</text>' % (w-46, ty + 84))
    o.append('<text x="%d" y="%d" class="kucuk" text-anchor="end">Ölçek 1:100 (A3) · Ön tasarım · 19.09.2026</text>' % (w-46, ty + 116))
    return "\n".join(o), ty

STIL = """
<style>
  text { font-family: "DejaVu Sans", Arial, Helvetica, sans-serif; fill:#111827; }
  .kod   { font-size: 15px; font-weight: 700; fill:#1d4ed8; letter-spacing:.5px; }
  .ad    { font-size: 15px; font-weight: 600; }
  .alan  { font-size: 13px; fill:#4b5563; }
  .olcu  { font-size: 14px; fill:#374151; }
  .kucuk { font-size: 15px; fill:#4b5563; }
  .baslik{ font-size: 34px; font-weight: 700; }
  .altb  { font-size: 19px; font-weight: 600; fill:#1f2937; }
  .lej   { font-size: 15px; fill:#374151; }
</style>
<defs>
  <marker id="ok" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">
    <path d="M0 0 L9 4.5 L0 9 z" fill="#b45309"/>
  </marker>
  <pattern id="cim" width="14" height="14" patternUnits="userSpaceOnUse">
    <rect width="14" height="14" fill="#eef7ec"/>
    <path d="M0 14 L7 6 M7 14 L14 6" stroke="#bcd9b6" stroke-width="1.4" fill="none"/>
  </pattern>
</defs>
"""

def kat_plani(kat):
    mahaller = KATLAR[kat]
    w = int(x(BINA["en"]) + M + 330)
    h = int(y(BINA["boy"]) + M + BASLIK_YUK)
    kapali, acik = kat_ozeti()[kat]
    cerceve, ty = cerceve_svg(w, h, "%s PLANI" % kat.upper(),
        "Net kapalı alan %.1f m²  ·  açık alan %.1f m²  ·  brüt kat alanı 300,0 m²" % (kapali, acik),
        "Kat yüksekliği %.2f m · net tavan yüksekliği %.2f m · duvarlar: dış 35 cm (19 tuğla + 8 XPS + kaplama), iç 15 cm" % (
            KAT_YUKSEKLIK[kat], NET_TAVAN[kat]))
    o = [cerceve]
    # mahal zeminleri
    for r in mahaller:
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s"/>' % (
            x(r[2]), y(r[3]), (r[4]-r[2])*S, (r[5]-r[3])*S, RENK.get(r[6], "#f5f5f5")))
        if r[6] == "acik":
            o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#cim)" opacity=".45"/>' % (
                x(r[2]), y(r[3]), (r[4]-r[2])*S, (r[5]-r[3])*S))
    o.append(duvarlar_svg(mahaller))
    kapilar = kapi_yerlestir(mahaller)
    pencereler = pencere_yerlestir(mahaller)
    # garaj kapısı (bodrum) ve giriş kapısı (zemin) kuzey cephede
    ekkapilar = []
    for r in mahaller:
        if r[1].startswith("Garaj"):
            orta = (r[2] + r[4]) / 2
            ekkapilar.append(("y", 0.0, orta - GARAJ_KAPI/2, orta + GARAJ_KAPI/2, r, r))
            pencereler = [p for p in pencereler if p[4][0] != r[0]]
    o.append(acikliklar_svg(kapilar + ekkapilar, pencereler, garaj=gecis_yerlestir(mahaller)))
    for r in mahaller:
        if "erdiven" in r[1]:
            o.append(merdiven_svg(r))
        if "Asansör" in r[1]:
            o.append(asansor_svg(r))
        o.append(etiket_svg(r))
    # ölçü çizgileri
    xs = sorted(set([r[2] for r in mahaller] + [r[4] for r in mahaller]))
    ys = sorted(set([r[3] for r in mahaller] + [r[5] for r in mahaller]))
    ust = y(0) - 60
    for a, b in zip(xs, xs[1:]):
        o.append(olcu_cizgisi(x(a), ust, x(b), ust, "%.2f" % (b - a)))
    o.append(olcu_cizgisi(x(0), ust - 52, x(BINA["en"]), ust - 52, "%.2f" % BINA["en"]))
    sol = x(0) - 62
    for a, b in zip(ys, ys[1:]):
        o.append(olcu_cizgisi(sol, y(a), sol, y(b), "%.2f" % (b - a)))
    o.append(olcu_cizgisi(sol - 54, y(0), sol - 54, y(BINA["boy"]), "%.2f" % BINA["boy"]))
    # kuzey oku + lejant
    nx, ny = x(BINA["en"]) + 92, y(0) + 40
    o.append('<circle cx="%.1f" cy="%.1f" r="34" fill="none" stroke="%s" stroke-width="2"/>' % (nx, ny, CIZGI))
    o.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>' % (nx, ny-30, nx-11, ny+16, nx+11, ny+16, DUVAR))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">K</text>' % (nx, ny + 52))
    ly = y(0) + 120
    for i, (etiket, anahtar) in enumerate([("Yaşam alanı","yasam"),("Yatak odası","yatak"),
            ("Islak hacim","islak"),("Mutfak","mutfak"),("Sirkülasyon","sirkulasyon"),
            ("Teknik / depo","teknik"),("Açık alan","acik")]):
        o.append('<rect x="%.1f" y="%.1f" width="26" height="18" fill="%s" stroke="%s" stroke-width="1"/>' % (
            nx - 34, ly + i*28, RENK[anahtar], CIZGI))
        o.append('<text x="%.1f" y="%.1f" class="lej">%s</text>' % (nx + 0, ly + 14 + i*28, etiket))
    # ölçek çubuğu
    sx, sy = x(0), ty - 46
    o.append('<text x="%.1f" y="%.1f" class="kucuk">0</text>' % (sx - 4, sy - 10))
    for i in range(5):
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="12" fill="%s"/>' % (
            sx + i*S, sy, S, DUVAR if i % 2 == 0 else "#ffffff"))
        o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="12" fill="none" stroke="%s" stroke-width="1"/>' % (
            sx + i*S, sy, S, DUVAR))
    o.append('<text x="%.1f" y="%.1f" class="kucuk">5 m</text>' % (sx + 5*S + 8, sy + 12))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s%s</svg>'
            % (w, h, w, h, STIL, "\n".join(o)))

# ----------------------------------------------------------------- vaziyet planı
def vaziyet_plani():
    P, B = PARSEL, BINA
    w = int(P["en"]*S + 2*M + 260)
    h = int(P["boy"]*S + 2*M + BASLIK_YUK)
    cerceve, ty = cerceve_svg(w, h, "VAZİYET PLANI",
        "Parsel %.0f m² · TAKS %.2f (%.0f m²) · KAKS %.2f (%.0f m²) · %s" % (
            P["alan"], P["taks"], P["alan"]*P["taks"], P["kaks"], P["alan"]*P["kaks"], P["nizam"]),
        "Çekme mesafeleri: ön %.1f m · yan %.1f m · arka %.1f m (imar durumu belgesiyle teyit edilecektir)" % (
            P["cekme_on"], P["cekme_yan"], P["cekme_arka"]))
    o = [cerceve]
    px, py = M, M
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="url(#cim)" stroke="%s" stroke-width="3"/>' % (
        px, py, P["en"]*S, P["boy"]*S, DUVAR))
    # çekme mesafeleri
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="none" stroke="#b45309" '
             'stroke-width="2" stroke-dasharray="12 8"/>' % (
        px + P["cekme_yan"]*S, py + P["cekme_on"]*S,
        (P["en"]-2*P["cekme_yan"])*S, (P["boy"]-P["cekme_on"]-P["cekme_arka"])*S))
    # bina
    bx = px + P["cekme_yan"]*S
    by = py + P["cekme_on"]*S
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#dbe7f6" stroke="%s" stroke-width="4"/>' % (
        bx, by, B["en"]*S, B["boy"]*S, DUVAR))
    o.append('<text x="%.1f" y="%.1f" class="altb" text-anchor="middle">VİLLA</text>' % (bx + B["en"]*S/2, by + B["boy"]*S/2 - 16))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">20,00 × 15,00 m = 300 m² oturum</text>' % (
        bx + B["en"]*S/2, by + B["boy"]*S/2 + 14))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">Bodrum + Zemin + 1. Kat + Çatı arası</text>' % (
        bx + B["en"]*S/2, by + B["boy"]*S/2 + 40))
    # yol, giriş, otopark, havuz
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#e5e7eb" stroke="%s" stroke-width="2"/>' % (
        px, py + P["boy"]*S, P["en"]*S, 70, CIZGI))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">İMAR YOLU</text>' % (px + P["en"]*S/2, py + P["boy"]*S + 45))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f1f5f9" stroke="%s" stroke-width="2"/>' % (
        bx + 2.0*S, py + P["boy"]*S - P["cekme_arka"]*S + 10, 6.0*S, 5.5*S, CIZGI))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">Açık otopark (2 araç) + rampa</text>' % (
        bx + 5.0*S, py + P["boy"]*S - P["cekme_arka"]*S + 10 + 2.9*S))
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="16" fill="#cfe9f5" stroke="%s" stroke-width="2"/>' % (
        bx + B["en"]*S - 8.0*S, py + 0.6*S, 8.0*S, 3.4*S, CIZGI))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">Havuz 8,00 × 3,40 (opsiyon)</text>' % (
        bx + B["en"]*S - 4.0*S, py + 2.5*S))
    # ölçüler
    o.append(olcu_cizgisi(px, py - 46, px + P["en"]*S, py - 46, "%.2f" % P["en"]))
    o.append(olcu_cizgisi(px - 46, py, px - 46, py + P["boy"]*S, "%.2f" % P["boy"]))
    o.append(olcu_cizgisi(px, by - 22, bx, by - 22, "%.2f" % P["cekme_yan"]))
    o.append(olcu_cizgisi(bx + B["en"]*S, by - 22, px + P["en"]*S, by - 22, "%.2f" % P["cekme_yan"]))
    o.append(olcu_cizgisi(bx - 22, py, bx - 22, by, "%.2f" % P["cekme_on"]))
    o.append(olcu_cizgisi(bx - 22, by + B["boy"]*S, bx - 22, py + P["boy"]*S, "%.2f" % P["cekme_arka"]))
    nx, ny = px + P["en"]*S + 120, py + 50
    o.append('<circle cx="%.1f" cy="%.1f" r="34" fill="none" stroke="%s" stroke-width="2"/>' % (nx, ny, CIZGI))
    o.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="%s"/>' % (nx, ny-30, nx-11, ny+16, nx+11, ny+16, DUVAR))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">K</text>' % (nx, ny + 52))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s%s</svg>'
            % (w, h, w, h, STIL, "\n".join(o)))

# ----------------------------------------------------------------- kesit
def kesit():
    kats = [("Bodrum", KAT_YUKSEKLIK["Bodrum"]), ("Zemin", KAT_YUKSEKLIK["Zemin"]), ("1. Kat", KAT_YUKSEKLIK["1. Kat"])]
    cati_h = 3.6
    toplam = sum(k[1] for k in kats) + cati_h
    w = int(BINA["en"]*S + 2*M + 200)
    h = int(toplam*S + 2*M + BASLIK_YUK + 60)
    cerceve, ty = cerceve_svg(w, h, "A–A KESİTİ",
        "Bodrum %.2f + Zemin %.2f + 1. Kat %.2f + kırma çatı — toplam yapı yüksekliği %.2f m" % (
            KAT_YUKSEKLIK["Bodrum"], KAT_YUKSEKLIK["Zemin"], KAT_YUKSEKLIK["1. Kat"], toplam),
        "Net tavan yüksekliği her katta ≥ 2,55 m (yönetmelik asgarisi 2,40 m) · döşeme kalınlığı 30 cm")
    o = [cerceve]
    zemin_y = M + (KAT_YUKSEKLIK["Zemin"] + KAT_YUKSEKLIK["1. Kat"] + cati_h)*S
    x0 = M
    genis = BINA["en"]*S
    # toprak
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#efe6da"/>' % (
        x0 - 80, zemin_y, genis + 160, (KAT_YUKSEKLIK["Bodrum"] + 0.9)*S))
    kot = zemin_y
    seviye = [("±0.00", zemin_y, "Zemin kat döşemesi")]
    for ad, yuk in [("1. Kat", KAT_YUKSEKLIK["Zemin"]), ("Çatı", KAT_YUKSEKLIK["1. Kat"])]:
        kot -= yuk*S
        seviye.append(("+%.2f" % ((zemin_y - kot)/S), kot, ad + " döşemesi"))
    bodrum_kot = zemin_y + KAT_YUKSEKLIK["Bodrum"]*S
    seviye.append(("-%.2f" % KAT_YUKSEKLIK["Bodrum"], bodrum_kot, "Bodrum döşemesi"))
    # kat hacimleri
    ust = zemin_y - (KAT_YUKSEKLIK["Zemin"] + KAT_YUKSEKLIK["1. Kat"])*S
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f7fafc" stroke="%s" stroke-width="3"/>' % (
        x0, ust, genis, (KAT_YUKSEKLIK["Zemin"] + KAT_YUKSEKLIK["1. Kat"] + KAT_YUKSEKLIK["Bodrum"])*S, DUVAR))
    for kotu, ad in [(zemin_y, "ZEMİN KAT"), (zemin_y - KAT_YUKSEKLIK["Zemin"]*S, "1. NORMAL KAT"), (bodrum_kot, "BODRUM KAT")]:
        yuk = KAT_YUKSEKLIK["Zemin"] if ad == "ZEMİN KAT" else (KAT_YUKSEKLIK["1. Kat"] if ad.startswith("1.") else KAT_YUKSEKLIK["Bodrum"])
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="10"/>' % (
            x0, kotu, x0 + genis, kotu, DUVAR))
        o.append('<text x="%.1f" y="%.1f" class="altb" text-anchor="middle">%s</text>' % (
            x0 + genis/2, kotu - yuk*S/2, ad))
        o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">kat yüksekliği %.2f m · net %.2f m</text>' % (
            x0 + genis/2, kotu - yuk*S/2 + 26, yuk, yuk - 0.35))
    # çatı
    tepe = ust - cati_h*S
    o.append('<path d="M %.1f %.1f L %.1f %.1f L %.1f %.1f Z" fill="#e7d9c9" stroke="%s" stroke-width="3"/>' % (
        x0 - 50, ust, x0 + genis/2, tepe, x0 + genis + 50, ust, DUVAR))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">Kırma çatı — eğim ≈ %d° · kilitli kiremit · 14 cm taşyünü yalıtım</text>' % (
        x0 + genis/2, tepe + 130, int(math.degrees(math.atan(cati_h / (BINA["en"]/2))))))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">Çatı arası depo (iç yükseklik ≥ 2,40 m)</text>' % (
        x0 + genis/2, tepe + 160))
    # kot işaretleri
    for etiket, yy, ad in seviye:
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5" stroke-dasharray="8 6"/>' % (
            x0 - 70, yy, x0 + genis + 150, yy, CIZGI))
        o.append('<text x="%.1f" y="%.1f" class="olcu">%s  %s</text>' % (x0 + genis + 12, yy - 8, etiket, ad))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s%s</svg>'
            % (w, h, w, h, STIL, "\n".join(o)))

# ----------------------------------------------------------------- çatı planı
def cati_plani():
    w = int(BINA["en"]*S + 2*M)
    h = int(BINA["boy"]*S + 2*M + BASLIK_YUK)
    cerceve, ty = cerceve_svg(w, h, "ÇATI PLANI",
        "Kırma çatı · 4 yöne eğimli · mahya ve dere çizgileri · alüminyum oluk ve iniş boruları",
        "Saçak taşması 60 cm · kilitli kiremit · çatı arası havalandırma menfezleri")
    o = [cerceve]
    t = 0.6
    o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#f3ece3" stroke="%s" stroke-width="3"/>' % (
        x(-t), y(-t), (BINA["en"]+2*t)*S, (BINA["boy"]+2*t)*S, DUVAR))
    E, Bo = BINA["en"]+2*t, BINA["boy"]+2*t
    yarim = Bo/2
    mah0, mah1 = -t + yarim, BINA["en"] + t - yarim
    for a, b in [((-t, -t), (mah0, yarim)), ((BINA["en"]+t, -t), (mah1, yarim)),
                 ((-t, BINA["boy"]+t), (mah0, yarim)), ((BINA["en"]+t, BINA["boy"]+t), (mah1, yarim))]:
        o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.5"/>' % (
            x(a[0]), y(a[1]), x(b[0]), y(b[1] - t), CIZGI))
    o.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="5"/>' % (
        x(mah0), y(yarim - t), x(mah1), y(yarim - t), DUVAR))
    o.append('<text x="%.1f" y="%.1f" class="altb" text-anchor="middle">MAHYA</text>' % (x(BINA["en"]/2), y(yarim - t) - 14))
    for i, (ax, ay) in enumerate([(1.2, 1.2), (BINA["en"]-1.2, 1.2), (1.2, BINA["boy"]-1.2), (BINA["en"]-1.2, BINA["boy"]-1.2)]):
        o.append('<circle cx="%.1f" cy="%.1f" r="12" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (x(ax), y(ay), CIZGI))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">○ iniş boruları (4 adet, Ø100)</text>' % (x(BINA["en"]/2), y(BINA["boy"]) + 60))
    for oxx in (BINA["en"]*0.3, BINA["en"]*0.7):
        o.append('<rect x="%.1f" y="%.1f" width="46" height="30" fill="#ffffff" stroke="%s" stroke-width="2"/>' % (
            x(oxx), y(yarim - t) - 60, CIZGI))
    o.append('<text x="%.1f" y="%.1f" class="kucuk" text-anchor="middle">□ baca / havalandırma</text>' % (x(BINA["en"]/2), y(BINA["boy"]) + 88))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s%s</svg>'
            % (w, h, w, h, STIL, "\n".join(o)))

CIZIMLER = [
    ("01-vaziyet-plani",  "Vaziyet Planı",   vaziyet_plani),
    ("02-bodrum-kat",     "Bodrum Kat Planı", lambda: kat_plani("Bodrum")),
    ("03-zemin-kat",      "Zemin Kat Planı",  lambda: kat_plani("Zemin")),
    ("04-birinci-kat",    "1. Normal Kat Planı", lambda: kat_plani("1. Kat")),
    ("05-cati-plani",     "Çatı Planı",      cati_plani),
    ("06-kesit-aa",       "A–A Kesiti",      kesit),
]

if __name__ == "__main__":
    hedef = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cizimler")
    os.makedirs(hedef, exist_ok=True)
    for dosya, ad, fn in CIZIMLER:
        svg = fn()
        with open(os.path.join(hedef, dosya + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        print("%-22s %-24s %6d bayt" % (dosya + ".svg", ad, len(svg)))
