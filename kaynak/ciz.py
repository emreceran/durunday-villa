# -*- coding: utf-8 -*-
"""Durunday Villa — mimari çizim seti (A3 yatay SVG paftalar).

Her pafta veri.py'den üretilir. Ölçüler cm, kotlar m. `python3 ciz.py` → ../cizimler/*.svg"""
import os, math, html, base64, datetime, re
import kayit
from veri import (KATLAR, KATLAR_SIRA, KAPILAR, PENCERELER, MOBILYA, ACIK, MERDIVEN_KORKULUK, BINA,
                  BINA_KONUM, PARSEL, DIS_DUVAR, IC_DUVAR, YALITIM, KOT, TABII_ZEMIN, KAT_YUKSEKLIK,
                  NET_TAVAN, DOSEME, GARAJ_KOT, CATI, AKS_X, AKS_Y, KOLON, kolonlar, MERDIVEN,
                  merdiven_kollari, ASANSOR, BALKONLAR, GIRIS_SACAGI, PERGOLA, TERAS, ISIKLIKLAR,
                  BACA, HAVUZ, KAT_BOSLUGU_KAPAK, net_alan, ic_sinir, kat_ozeti)
from geometri import (oda_bul, mahal_sozluk, duvar_parcalari, duvar_dikdortgeni, kanat_geometrisi,
                      kapi_taraflari, duvar_kalinligi, ham_kenarlar)
from mobilya import olcu, sinir_kutusu

W, H = BINA["en"], BINA["boy"]
FONT = "'Arial Narrow','Liberation Sans Narrow','Roboto Condensed',Arial,Helvetica,sans-serif"
TARIH = "21.09.2026"
REVIZYON = [("R0", "19.09.2026", "İlk yayın"),
            ("R1", TARIH, "Plan kurgusu yeniden düzenlendi; kesit, görünüş, detay ve doğrama listesi eklendi")]
KALIN, ORTA, INCE, COK_INCE = 0.50, 0.30, 0.18, 0.13
GRI = "#6b7280"; ACIK_GRI = "#9ca3af"; MOB = "#7b8494"
CAM = "#dbeafe"

def esc(t):
    return html.escape(str(t), quote=True)

def f2(v):
    return ("%.2f" % v).replace("-0.00", "0.00")

def cm(v):
    return "%d" % round(v * 100)

def kot_yazi(v):
    if abs(v) < 0.005:
        return "±0.00"
    return ("+%.2f" % v) if v > 0 else ("−%.2f" % abs(v))

# ================================================================== SVG yardımcıları
# desen tanımları: tür, aralık(lar), çizgi rengi, kalınlık, zemin rengi
DESEN = {
 "p-fayans":  ("grid", (3.0, 3.0), "#c7ccd4", 0.10, None),
 "p-tas":     ("grid", (6.0, 6.0), "#d3d7de", 0.10, None),
 "p-dis-tas": ("grid", (6.0, 3.0), "#c9cdd3", 0.10, None),
 "p-izgara":  ("grid", (1.2, 1.2), "#6b7280", 0.10, None),
 "p-duvar":   ("diag", 1.5, "#3f444c", 0.22, None),
 "p-saft":    ("diag", 1.6, "#9ca3af", 0.12, None),
 "p-toprak":  ("diag", 3.0, "#a8957a", 0.15, None),
 "p-yalitim": ("diag2", 1.6, "#6b7280", 0.08, "#f4f1e8"),
 "p-kiremit": ("h", 2.5, "#9ca3af", 0.10, None),
 "p-kiremit-g": ("tugla", (3.0, 2.0), "#2f3338", 0.12, "#4b5058"),
 "p-sille":   ("tugla", (9.0, 1.5), "#b9ab8e", 0.12, "#efe6d4"),
 "p-ahsap":   ("v", 1.2, "#8a643f", 0.12, "#c89b6d"),
 "p-su":      ("h", 3.0, "#93c5fd", 0.15, None),
 "p-cim":     (None, None, None, None, "#f1f6ec"),
 "p-siva":    (None, None, None, None, "#fbfbf9"),
 "p-parke":   (None, None, None, None, None),
}

def desen_yolu(tur, par, x0, y0, x1, y1):
    """Dikdörtgen içinde desen çizgilerinin tek SVG path verisi."""
    d = []
    import math as _m
    if tur == "grid":
        sx, sy = par
        v = _m.ceil(x0 / sx) * sx
        while v < x1 - 1e-6:
            d.append("M%.2f %.2fV%.2f" % (v, y0, y1)); v += sx
        v = _m.ceil(y0 / sy) * sy
        while v < y1 - 1e-6:
            d.append("M%.2f %.2fH%.2f" % (x0, v, x1)); v += sy
    elif tur in ("h", "v"):
        st = par
        if tur == "h":
            v = _m.ceil(y0 / st) * st
            while v < y1 - 1e-6:
                d.append("M%.2f %.2fH%.2f" % (x0, v, x1)); v += st
        else:
            v = _m.ceil(x0 / st) * st
            while v < x1 - 1e-6:
                d.append("M%.2f %.2fV%.2f" % (v, y0, y1)); v += st
    elif tur == "tugla":
        sx, sy = par
        j = _m.ceil(y0 / sy)
        v = j * sy
        while v < y1 - 1e-6:
            d.append("M%.2f %.2fH%.2f" % (x0, v, x1))
            ust = min(v + sy, y1)
            off = (j % 2) * sx / 2
            u = _m.ceil((x0 - off) / sx) * sx + off
            while u < x1 - 1e-6:
                d.append("M%.2f %.2fV%.2f" % (u, v, ust)); u += sx
            v += sy; j += 1
    elif tur in ("diag", "diag2"):
        st = par * 1.41421356
        # x + y = k (sağ-üstten sol-alta inen çizgiler)
        k = _m.ceil((x0 + y0) / st) * st
        while k < x1 + y1:
            ax, ay = max(x0, k - y1), None
            ax = max(x0, k - y1); ay = k - ax
            bx = min(x1, k - y0); by = k - bx
            if bx > ax:
                d.append("M%.2f %.2fL%.2f %.2f" % (ax, ay, bx, by))
            k += st
    return "".join(d)

def _kaydet_sekil(q, fill, stroke, sw, dash, kapali, op=None, yol=False):
    """Bir şekli kayda yazar: desenli dolgu → tarama, düz dolgu → dolgu, kontur → çizgi."""
    if op is not None and float(op) < 0.5:
        fill = "none"
    if fill and fill != "none":
        if fill.startswith("url(#p-"):
            kayit.kaydet("tarama", pts=q, desen=fill[5:-1])
        else:
            kayit.kaydet("dolgu", pts=q, renk=fill)
    if stroke and stroke != "none" and sw and sw > 0:
        kayit.kaydet("cizgi", pts=q + ([q[0]] if kapali else []), sw=sw, dash=dash, renk=stroke, yol=yol)

_YOL = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")

def yol_noktalari(d, adim=12):
    """SVG path verisini alt yollara (nokta listesi, kapalı mı) çevirir; eğriler ve yaylar düzleştirilir."""
    tok = _YOL.findall(d)
    out, cur, x, y, sx, sy, i, cmd = [], [], 0.0, 0.0, 0.0, 0.0, 0, None
    def sayi():
        nonlocal i
        v = float(tok[i]); i += 1; return v
    while i < len(tok):
        if tok[i].isalpha():
            cmd = tok[i]; i += 1
            if cmd in "Zz":
                if cur:
                    out.append((cur, True)); cur = []
                x, y = sx, sy
                continue
        r = cmd.islower()
        C = cmd.upper()
        if C == "M":
            if cur:
                out.append((cur, False))
            nx, ny = sayi(), sayi()
            x, y = (x + nx, y + ny) if r else (nx, ny)
            sx, sy = x, y; cur = [(x, y)]
            cmd = "l" if r else "L"
        elif C == "L":
            nx, ny = sayi(), sayi(); x, y = (x + nx, y + ny) if r else (nx, ny); cur.append((x, y))
        elif C == "H":
            nx = sayi(); x = x + nx if r else nx; cur.append((x, y))
        elif C == "V":
            ny = sayi(); y = y + ny if r else ny; cur.append((x, y))
        elif C in "QC":
            n = 2 if C == "Q" else 3
            p = [sayi() for _ in range(2 * n)]
            if r:
                p = [v + (x if k % 2 == 0 else y) for k, v in enumerate(p)]
            ks = [(x, y)] + [(p[2 * k], p[2 * k + 1]) for k in range(n)]
            for j in range(1, adim + 1):
                t = j / adim
                pts = ks[:]
                while len(pts) > 1:
                    pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for a, b in zip(pts, pts[1:])]
                cur.append(pts[0])
            x, y = ks[-1]
        elif C == "A":
            rx, ry, rot, buyuk, yon, nx, ny = [sayi() for _ in range(7)]
            if r:
                nx, ny = x + nx, y + ny
            cur += _yay(x, y, rx, ry, rot, int(buyuk), int(yon), nx, ny, adim * 2)
            x, y = nx, ny
        else:
            i += 1
    if cur:
        out.append((cur, False))
    return [(q, k) for q, k in out if len(q) > 1]

def _yay(x1, y1, rx, ry, phi, fa, fs, x2, y2, n):
    """SVG eliptik yay → nokta listesi (W3C uç nokta → merkez dönüşümü)."""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    ph = math.radians(phi); c, s_ = math.cos(ph), math.sin(ph)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1p, y1p = c * dx + s_ * dy, -s_ * dx + c * dy
    rx, ry = abs(rx), abs(ry)
    lam = x1p ** 2 / rx ** 2 + y1p ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx ** 2 * ry ** 2 - rx ** 2 * y1p ** 2 - ry ** 2 * x1p ** 2
    den = rx ** 2 * y1p ** 2 + ry ** 2 * x1p ** 2
    k = math.sqrt(max(0, num / den)) * (-1 if fa == fs else 1)
    cxp, cyp = k * rx * y1p / ry, -k * ry * x1p / rx
    cx, cy = c * cxp - s_ * cyp + (x1 + x2) / 2, s_ * cxp + c * cyp + (y1 + y2) / 2
    def ang(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy); return a
    t1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dt = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not fs and dt > 0:
        dt -= 2 * math.pi
    elif fs and dt < 0:
        dt += 2 * math.pi
    out = []
    for j in range(1, n + 1):
        t = t1 + dt * j / n
        out.append((cx + rx * math.cos(t) * c - ry * math.sin(t) * s_, cy + rx * math.cos(t) * s_ + ry * math.sin(t) * c))
    return out

class Cizim:
    _sayac = [0]
    def __init__(self):
        self.p = []
    def add(self, s):
        self.p.append(s)
        if kayit.AKTIF and s.startswith("<line "):
            a = dict(re.findall(r'([\w-]+)="([^"]*)"', s))
            kayit.kaydet("cizgi", pts=[(float(a["x1"]), float(a["y1"])), (float(a["x2"]), float(a["y2"]))],
                         sw=float(a.get("stroke-width", INCE)), dash=a.get("stroke-dasharray"), renk=a.get("stroke"),
                         ok="marker-end" in a)
    def _desen(self, fill, x, y, w, h, op=None, clip=None):
        ad = fill[5:-1]
        tur, par, renk, kal, zemin = DESEN[ad]
        o = ' opacity="%s"' % op if op else ""
        cl = ' clip-path="url(#%s)"' % clip if clip else ""
        if zemin:
            if clip:
                self.p.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"%s%s/>' % (x, y, w, h, zemin, o, cl))
            else:
                self.p.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s"%s/>' % (x, y, w, h, zemin, o))
        if tur:
            dd = desen_yolu(tur, par, x, y, x + w, y + h)
            if dd:
                self.p.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.2f"%s%s/>' % (dd, renk, kal, o, cl))
    def line(self, x1, y1, x2, y2, w=INCE, c="#111", dash=None, cap="butt", op=None):
        if kayit.AKTIF:
            kayit.kaydet("cizgi", pts=[(x1, y1), (x2, y2)], sw=w, dash=dash, renk=c)
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        o = ' opacity="%s"' % op if op else ""
        self.p.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f"%s stroke-linecap="%s"%s/>'
                      % (x1, y1, x2, y2, c, w, d, cap, o))
    def rect(self, x, y, w, h, fill="none", stroke="none", sw=INCE, dash=None, rx=0, op=None, extra=""):
        if kayit.AKTIF:
            q = [(x, y), (x + max(w, 0), y), (x + max(w, 0), y + max(h, 0)), (x, y + max(h, 0))]
            _kaydet_sekil(q, fill, stroke, sw, dash, True, op)
        if fill.startswith("url(#p-") and fill[5:-1] in DESEN:
            self._desen(fill, x, y, max(w, 0), max(h, 0), op)
            fill = "none"
            if stroke == "none":
                return
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        o = ' opacity="%s"' % op if op else ""
        r = ' rx="%.2f"' % rx if rx else ""
        self.p.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"%s%s%s %s/>'
                      % (x, y, max(w, 0), max(h, 0), fill, stroke, sw, d, r, o, extra))
    def poly(self, pts, fill="none", stroke="#111", sw=INCE, kapali=True, dash=None, op=None, join="miter"):
        if kayit.AKTIF:
            _kaydet_sekil(list(pts), fill, stroke, sw, dash, kapali, op)
        if fill.startswith("url(#p-") and fill[5:-1] in DESEN:
            Cizim._sayac[0] += 1
            cid = "kl%d" % Cizim._sayac[0]
            self.p.append('<clipPath id="%s"><polygon points="%s"/></clipPath>' % (cid, " ".join("%.2f,%.2f" % q for q in pts)))
            xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
            self._desen(fill, min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys), op, clip=cid)
            fill = "none"
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        o = ' opacity="%s"' % op if op else ""
        tag = "polygon" if kapali else "polyline"
        self.p.append('<%s points="%s" fill="%s" stroke="%s" stroke-width="%.2f"%s%s stroke-linejoin="%s"/>'
                      % (tag, " ".join("%.2f,%.2f" % q for q in pts), fill, stroke, sw, d, o, join))
    def path(self, d, fill="none", stroke="#111", sw=INCE, dash=None, op=None):
        if kayit.AKTIF:
            for q, kap in yol_noktalari(d):
                _kaydet_sekil(q, fill if kap else "none", stroke, sw, dash, kap, op, yol=True)
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        o = ' opacity="%s"' % op if op else ""
        self.p.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%.2f"%s%s/>' % (d, fill, stroke, sw, da, o))
    def circle(self, x, y, r, fill="none", stroke="#111", sw=INCE, dash=None):
        if kayit.AKTIF:
            kayit.kaydet("daire", xy=(x, y), r=r, fill=fill, renk=stroke, sw=sw, dash=dash)
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.p.append('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"%s/>'
                      % (x, y, r, fill, stroke, sw, d))
    def text(self, x, y, t, size=2.2, anchor="start", weight=400, fill="#111", rot=0, italic=False, ls=0):
        if kayit.AKTIF:
            kayit.kaydet("yazi", xy=(x, y), t=str(t), size=size, anchor=anchor, kalin=weight >= 600, rot=rot, italik=italic)
        tr = ' transform="rotate(%.1f %.2f %.2f)"' % (rot, x, y) if rot else ""
        st = ' font-style="italic"' if italic else ""
        l = ' letter-spacing="%.2f"' % ls if ls else ""
        self.p.append('<text x="%.2f" y="%.2f" font-size="%.2f" text-anchor="%s" font-weight="%d" fill="%s"%s%s%s>%s</text>'
                      % (x, y, size, anchor, weight, fill, tr, st, l, esc(t)))
    def svg(self):
        return "\n".join(self.p)

DEFS = """<defs>
 <pattern id="p-fayans" patternUnits="userSpaceOnUse" width="3" height="3"><path d="M0 0H3M0 0V3" stroke="#c7ccd4" stroke-width="0.1"/></pattern>
 <pattern id="p-tas" patternUnits="userSpaceOnUse" width="6" height="6"><path d="M0 0H6M0 0V6" stroke="#d3d7de" stroke-width="0.1"/></pattern>
 <pattern id="p-parke" patternUnits="userSpaceOnUse" width="12" height="1.8"><path d="M0 0H12M0 0V1.8" stroke="#e6e1d6" stroke-width="0.08"/></pattern>
 <pattern id="p-dis-tas" patternUnits="userSpaceOnUse" width="6" height="3"><path d="M0 0H6M0 0V3" stroke="#c9cdd3" stroke-width="0.1"/></pattern>
 <pattern id="p-duvar" patternUnits="userSpaceOnUse" width="1.5" height="1.5" patternTransform="rotate(45)"><path d="M0 0V1.5" stroke="#3f444c" stroke-width="0.22"/></pattern>
 <pattern id="p-yalitim" patternUnits="userSpaceOnUse" width="2.0" height="2.0"><rect width="2" height="2" fill="#f4f1e8"/><path d="M0 2L1 0L2 2" fill="none" stroke="#6b7280" stroke-width="0.08"/></pattern>
 <pattern id="p-saft" patternUnits="userSpaceOnUse" width="1.6" height="1.6" patternTransform="rotate(45)"><path d="M0 0V1.6" stroke="#9ca3af" stroke-width="0.12"/></pattern>
 <pattern id="p-toprak" patternUnits="userSpaceOnUse" width="4" height="4" patternTransform="rotate(45)"><path d="M0 0V4M2 0V1.2" stroke="#8b7355" stroke-width="0.15"/></pattern>
 <pattern id="p-beton" patternUnits="userSpaceOnUse" width="2.4" height="2.4"><circle cx="0.6" cy="0.7" r="0.18" fill="#555"/><circle cx="1.7" cy="1.8" r="0.12" fill="#555"/><path d="M1.4 0.4l0.4 0.3l-0.5 0.1z" fill="#555"/></pattern>
 <pattern id="p-cim" patternUnits="userSpaceOnUse" width="4" height="4"><path d="M0.5 1.2l0.3-0.8l0.3 0.8M2.6 3.2l0.3-0.8l0.3 0.8" fill="none" stroke="#86a877" stroke-width="0.12"/></pattern>
 <pattern id="p-kiremit" patternUnits="userSpaceOnUse" width="2.5" height="2.5"><path d="M0 2.5H2.5" stroke="#9ca3af" stroke-width="0.1"/></pattern>
 <pattern id="p-izgara" patternUnits="userSpaceOnUse" width="1.2" height="1.2"><path d="M0 0H1.2M0 0V1.2" stroke="#6b7280" stroke-width="0.1"/></pattern>
 <pattern id="p-su" patternUnits="userSpaceOnUse" width="6" height="3"><path d="M0 1.5q1.5-0.8 3 0t3 0" fill="none" stroke="#93c5fd" stroke-width="0.15"/></pattern>
 <pattern id="p-sille" patternUnits="userSpaceOnUse" width="9" height="3.0"><rect width="9" height="3" fill="#efe6d4"/><path d="M0 3H9M0 0V1.5M4.5 1.5V3M0 1.5H9" stroke="#b9ab8e" stroke-width="0.12"/></pattern>
 <pattern id="p-siva" patternUnits="userSpaceOnUse" width="5" height="5"><rect width="5" height="5" fill="#fbfbf9"/></pattern>
 <pattern id="p-ahsap" patternUnits="userSpaceOnUse" width="1.2" height="5"><rect width="1.2" height="5" fill="#c89b6d"/><path d="M0 0V5" stroke="#8a643f" stroke-width="0.12"/></pattern>
 <pattern id="p-kiremit-g" patternUnits="userSpaceOnUse" width="3" height="2"><rect width="3" height="2" fill="#4b5058"/><path d="M0 2H3M1.5 0V2" stroke="#2f3338" stroke-width="0.12"/></pattern>
 <marker id="ok" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#111"/></marker>
 <marker id="ok-k" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#b45309"/></marker>
</defs>"""

# ================================================================== pafta (A3 yatay) + antet
PW, PH = 420.0, 297.0
ANTET_X = 318.0

def pafta(no, ad, olcek, icerik, notlar=None, lejant=None, kuzey=True):
    c = Cizim()
    c.add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%dmm" height="%dmm" font-family="%s">'
          % (PW, PH, PW, PH, FONT))
    c.add(DEFS)
    c.rect(0, 0, PW, PH, fill="#ffffff")
    c.rect(10, 10, PW - 20, PH - 20, stroke="#111", sw=0.7)
    c.add(icerik)
    # antet
    x0, x1 = ANTET_X, PW - 10
    c.rect(x0, 10, x1 - x0, PH - 20, fill="#ffffff", stroke="#111", sw=0.5)
    y = 10
    def ayrac(yy, w=0.3):
        c.line(x0, yy, x1, yy, w=w)
    c.text(x0 + 4, y + 9, "DURUNDAY VİLLA", 5.2, weight=700, ls=0.4)
    c.text(x0 + 4, y + 14.5, "Konya · Meram · Durunday", 2.6, fill=GRI)
    c.text(x0 + 4, y + 19, "Bodrumlu dubleks müstakil konut · 300 m² oturum", 2.3, fill=GRI)
    y += 23; ayrac(y)
    c.text(x0 + 4, y + 5.5, "MİMARİ ÖN PROJE (AVAN)", 2.8, weight=700, ls=0.3)
    c.text(x0 + 4, y + 9.8, "Ruhsat ve uygulamaya esas değildir", 2.1, fill=GRI, italic=True)
    y += 13; ayrac(y)
    # notlar / lejant
    yy = y + 5
    if lejant:
        c.text(x0 + 4, yy, "LEJANT", 2.2, weight=700, ls=0.3); yy += 3.2
        for tur, metin in lejant:
            _lejant_sembol(c, x0 + 4, yy - 2.2, tur)
            c.text(x0 + 15, yy, metin, 2.0)
            yy += 3.6
        yy += 1.5
    if notlar:
        c.text(x0 + 4, yy, "NOTLAR", 2.2, weight=700, ls=0.3); yy += 3.4
        for i, n in enumerate(notlar, 1):
            satirlar = _sar(n, 58)
            for j, s in enumerate(satirlar):
                c.text(x0 + 4, yy, ("%d. " % i if j == 0 else "    ") + s, 1.95, fill="#1f2937")
                yy += 2.7
            yy += 0.6
    # alt blok
    alt = PH - 10 - 92
    if kuzey:
        _kuzey_oku(c, x1 - 12, alt - 13, 6.5)
    ayrac(alt, 0.4)
    c.text(x0 + 4, alt + 5, "REVİZYONLAR", 2.0, weight=700, ls=0.3)
    ry = alt + 9
    for r, t, a in REVIZYON:
        c.text(x0 + 4, ry, r, 1.9, weight=700); c.text(x0 + 10, ry, t, 1.9)
        for k, s in enumerate(_sar(a, 44)):
            c.text(x0 + 27, ry + k * 2.5, s, 1.9)
        ry += 2.5 * len(_sar(a, 44)) + 1.2
    ayrac(alt + 26)
    c.text(x0 + 4, alt + 31, "İŞ SAHİBİ", 1.9, fill=GRI); c.text(x0 + 4, alt + 35.5, "—", 2.4)
    c.text(x0 + 48, alt + 31, "HAZIRLAYAN", 1.9, fill=GRI); c.text(x0 + 48, alt + 35.5, "E. Ceran", 2.4)
    c.line(x0 + 45, alt + 26, x0 + 45, alt + 40, w=0.2)
    ayrac(alt + 40)
    c.text(x0 + 4, alt + 45, "MÜELLİF MİMAR", 1.9, fill=GRI)
    c.text(x0 + 4, alt + 50, "(ruhsat aşamasında atanacak)", 2.0, fill=GRI, italic=True)
    c.text(x0 + 48, alt + 45, "İMZA", 1.9, fill=GRI)
    c.line(x0 + 45, alt + 40, x0 + 45, alt + 54, w=0.2)
    ayrac(alt + 54, 0.4)
    c.text(x0 + 4, alt + 60, "PAFTA ADI", 1.9, fill=GRI)
    for k, s in enumerate(_sar(ad, 26)):
        c.text(x0 + 4, alt + 67 + k * 6, s, 5.0, weight=700)
    ayrac(alt + 78)
    c.text(x0 + 4, alt + 82.5, "ÖLÇEK", 1.9, fill=GRI); c.text(x0 + 4, alt + 88.5, olcek, 3.6, weight=700)
    c.text(x0 + 32, alt + 82.5, "TARİH", 1.9, fill=GRI); c.text(x0 + 32, alt + 88.5, TARIH, 3.0)
    c.text(x0 + 62, alt + 82.5, "PAFTA NO", 1.9, fill=GRI); c.text(x0 + 62, alt + 89, no, 5.2, weight=700)
    c.line(x0 + 29, alt + 78, x0 + 29, PH - 10, w=0.2); c.line(x0 + 59, alt + 78, x0 + 59, PH - 10, w=0.2)
    c.add("</svg>")
    return c.svg()

def _sar(metin, n):
    kelimeler, satirlar, s = metin.split(), [], ""
    for k in kelimeler:
        if len(s) + len(k) + 1 > n and s:
            satirlar.append(s); s = k
        else:
            s = (s + " " + k).strip()
    if s:
        satirlar.append(s)
    return satirlar

def _kuzey_oku(c, x, y, r):
    c.circle(x, y, r, stroke="#111", sw=0.3)
    c.poly([(x, y - r - 1.5), (x + 2.2, y + 2.5), (x, y + 1.2), (x - 2.2, y + 2.5)], fill="#111", stroke="#111", sw=0.2)
    c.text(x, y - r - 2.8, "K", 3.0, "middle", 700)

def _lejant_sembol(c, x, y, tur):
    if tur == "betonarme":
        c.rect(x, y, 9, 2.6, fill="#111")
    elif tur == "duvar":
        c.rect(x, y, 9, 2.6, fill="url(#p-duvar)", stroke="#111", sw=0.25)
    elif tur == "yalitim":
        c.rect(x, y, 9, 2.6, fill="url(#p-yalitim)", stroke="#111", sw=0.2)
    elif tur == "korkuluk":
        c.line(x, y + 0.9, x + 9, y + 0.9, 0.18); c.line(x, y + 1.7, x + 9, y + 1.7, 0.18)
    elif tur == "fayans":
        c.rect(x, y, 9, 2.6, fill="url(#p-fayans)", stroke="#999", sw=0.15)
    elif tur == "tas":
        c.rect(x, y, 9, 2.6, fill="url(#p-tas)", stroke="#999", sw=0.15)
    elif tur == "saft":
        c.rect(x, y, 9, 2.6, fill="url(#p-saft)", stroke="#111", sw=0.2)
    elif tur == "toprak":
        c.rect(x, y, 9, 2.6, fill="url(#p-toprak)", stroke="none")
    elif tur == "sille":
        c.rect(x, y, 9, 2.6, fill="url(#p-sille)", stroke="#999", sw=0.15)
    elif tur == "siva":
        c.rect(x, y, 9, 2.6, fill="#fbfbf9", stroke="#999", sw=0.15)
    elif tur == "ahsap":
        c.rect(x, y, 9, 2.6, fill="url(#p-ahsap)", stroke="#999", sw=0.15)
    elif tur == "cam":
        c.rect(x, y, 9, 2.6, fill=CAM, stroke="#475569", sw=0.15)
    elif tur == "kiremit":
        c.rect(x, y, 9, 2.6, fill="url(#p-kiremit-g)", stroke="#111", sw=0.15)
    elif tur == "kot":
        _kot_isareti(c, x + 3, y + 2.3, "", 2.0)
    elif tur == "aks":
        c.circle(x + 4.5, y + 1.3, 1.6, stroke="#111", sw=0.2); c.text(x + 4.5, y + 2.0, "1", 1.8, "middle")

def _kot_isareti(c, x, y, yazi, boy=2.0, sol=False):
    c.poly([(x - 1.1, y - 1.9), (x + 1.1, y - 1.9), (x, y)], fill="#fff", stroke="#111", sw=0.2)
    c.poly([(x - 1.1, y - 1.9), (x, y - 1.9), (x, y)], fill="#111", stroke="none")
    if yazi:
        if sol:
            c.text(x - 1.8, y - 0.4, yazi, boy, "end", 700)
        else:
            c.text(x + 1.8, y - 0.4, yazi, boy, "start", 700)

# ================================================================== ölçü çizgisi
def olcu_zinciri(c, noktalar, eksen, sabit, tx, yazi_ust=True, boy=1.8, uzatma=None):
    """noktalar: dünya koordinatı (m) listesi; eksen 'x' → yatay zincir (y=sabit mm), 'y' → düşey (x=sabit mm)."""
    n = sorted(set(round(v, 4) for v in noktalar))
    if len(n) < 2:
        return
    if eksen == "x":
        c.line(tx(n[0]) - 1.5, sabit, tx(n[-1]) + 1.5, sabit, COK_INCE)
        for v in n:
            X = tx(v)
            c.line(X, sabit - 1.2, X, sabit + 1.2, COK_INCE)
            c.line(X - 0.8, sabit + 0.8, X + 0.8, sabit - 0.8, 0.3)
            if uzatma is not None:
                c.line(X, uzatma, X, sabit + (1.2 if uzatma > sabit else -1.2), 0.08, "#888")
        for a, b in zip(n, n[1:]):
            if b - a < 0.05:
                continue
            m = (tx(a) + tx(b)) / 2
            d = sabit - 0.8 if yazi_ust else sabit + 2.4
            sz = boy if abs(tx(b) - tx(a)) > 3.5 else boy * 0.8
            c.text(m, d, cm(b - a), sz, "middle")
    else:
        c.line(sabit, tx(n[0]) - 1.5, sabit, tx(n[-1]) + 1.5, COK_INCE)
        for v in n:
            Y = tx(v)
            c.line(sabit - 1.2, Y, sabit + 1.2, Y, COK_INCE)
            c.line(sabit - 0.8, Y + 0.8, sabit + 0.8, Y - 0.8, 0.3)
            if uzatma is not None:
                c.line(uzatma, Y, sabit + (1.2 if uzatma > sabit else -1.2), Y, 0.08, "#888")
        for a, b in zip(n, n[1:]):
            if b - a < 0.05:
                continue
            m = (tx(a) + tx(b)) / 2
            d = sabit - 0.8 if yazi_ust else sabit + 2.4
            sz = boy if abs(tx(b) - tx(a)) > 3.5 else boy * 0.8
            c.text(d, m, cm(b - a), sz, "middle", rot=-90)

def aks_balonu(c, x, y, ad, r=3.2):
    c.circle(x, y, r, fill="#fff", stroke="#111", sw=0.3)
    c.text(x, y + 1.2, ad, 3.2, "middle", 700)

# ================================================================== kat planı
TIP_DOSEME = {"islak": "p-fayans", "mutfak": "p-fayans", "sirkulasyon": "p-tas"}
DOSEME_ADI = {"islak": "porselen R10", "mutfak": "porselen 60×120", "sirkulasyon": "traverten",
              "yasam": "meşe parke", "yatak": "meşe parke", "giyinme": "meşe parke", "ikincil": "LVT",
              "teknik": "epoksi / seramik", "garaj": "epoksi"}
OZEL_DOSEME = {"Z-09": "traverten", "Z-10": "traverten", "B-19": "kauçuk spor zemin", "B-18": "sedir ızgara",
               "B-02": "meşe parke", "B-21": "doğal taş", "B-01": "halı / akustik"}
ETIKET_YERI = {  # mahal etiketi konumu (m) — mobilyadan kaçınmak için
 "B-01": (3.9, 4.45), "B-02": (5.6, 7.3), "B-03": (2.3, 12.9), "B-04": (6.4, 11.55), "B-05": (6.0, 13.2),
 "B-06": (8.9, 6.4), "B-10": (10.2, 2.0), "B-11": (13.3, 1.7), "B-12": (13.3, 6.2), "B-13": (15.7, 2.6),
 "B-14": (18.6, 1.3), "B-15": (17.0, 5.9), "B-16": (17.3, 9.35), "B-17": (13.7, 11.0), "B-18": (14.0, 13.2),
 "B-19": (17.6, 10.8), "B-20": (11.3, 11.3), "B-21": (9.5, 13.55),
 "Z-01": (11.3, 1.3), "Z-02": (8.9, 7.3), "Z-06": (2.6, 1.9), "Z-07": (6.55, 2.1), "Z-08": (6.45, 4.15),
 "Z-09": (4.0, 13.1), "Z-10": (10.2, 14.1), "Z-11": (16.4, 10.95), "Z-12": (13.3, 5.4), "Z-13": (17.25, 5.45),
 "Z-14": (15.3, 7.35), "Z-15": (15.3, 8.8), "Z-16": (18.3, 8.35),
 "K-01": (8.9, 7.3), "K-06": (2.6, 2.0), "K-07": (6.55, 2.1), "K-08": (6.45, 4.15), "K-09": (2.6, 9.15),
 "K-10": (5.95, 9.35), "K-11": (3.4, 14.0), "K-12": (9.25, 11.55), "K-13": (11.6, 11.7), "K-14": (13.3, 3.6),
 "K-15": (16.2, 2.3), "K-16": (15.3, 5.8), "K-17": (18.35, 5.85), "K-18": (15.7, 8.55), "K-19": (18.5, 8.55),
 "K-20": (15.2, 14.1),
}
KOT_YERI = {"Bodrum": [(9.3, 9.7, KOT["Bodrum"])],
            "Zemin": [(9.3, 9.7, 0.0), (15.0, 1.1, GARAJ_KOT), (4.0, 15.9, TERAS["kot"]), (-1.4, 16.6, TABII_ZEMIN)],
            "1. Kat": [(9.3, 9.7, KOT["1. Kat"])]}

def plan_icerik(kat, ox, oy, s=10.0, baslik=True, olculer=True, mobilya=True, kesitler=True):
    tx = lambda v: ox + v * s
    ty = lambda v: oy + v * s
    c = Cizim()
    soz = mahal_sozluk(kat)
    # ---------------- bina dışı elemanlar (altta)
    _plan_dis_elemanlar(c, kat, tx, ty, s)
    with kayit.katman("DOSEME-KAPLAMA"):
        # ---------------- döşeme dokusu
        for m in KATLAR[kat]:
            desen = TIP_DOSEME.get(m["tip"])
            if m["kod"] in ("Z-09", "Z-10"):
                desen = "p-tas"
            if m["tip"] == "garaj" or m["tip"] == "teknik":
                desen = None
            for r in m["r"]:
                nx0, ny0, nx1, ny1 = ic_sinir(r)
                if m["tip"] == "saft":
                    c.rect(tx(nx0), ty(ny0), (nx1 - nx0) * s, (ny1 - ny0) * s, fill="url(#p-saft)")
                elif desen:
                    c.rect(tx(nx0), ty(ny0), (nx1 - nx0) * s, (ny1 - ny0) * s, fill="url(#%s)" % desen)
        # çok parçalı mahallerde parçalar arası şerit
        for m in KATLAR[kat]:
            if len(m["r"]) > 1 and TIP_DOSEME.get(m["tip"]):
                for a in m["r"]:
                    for b in m["r"]:
                        if a is b:
                            continue
                        if abs(a[3] - b[1]) < 1e-6:
                            x0, x1 = max(a[0], b[0]), min(a[2], b[2])
                            x0 = x0 + (DIS_DUVAR if x0 < 1e-6 else IC_DUVAR / 2)
                            x1 = x1 - (DIS_DUVAR if x1 > W - 1e-6 else IC_DUVAR / 2)
                            c.rect(tx(x0), ty(a[3] - IC_DUVAR / 2), (x1 - x0) * s, IC_DUVAR * s,
                                   fill="url(#%s)" % TIP_DOSEME[m["tip"]])
    # ---------------- mobilya
    if mobilya:
        for o in MOBILYA.get(kat, []):
            mobilya_svg(c, o, tx, ty, s)
    # ---------------- merdiven, asansör
    merdiven_plan(c, kat, tx, ty, s)
    asansor_plan(c, kat, tx, ty, s)
    # ---------------- duvarlar
    parcalar = duvar_parcalari(kat)
    beton, duvar, kork = [], [], []
    for p in parcalar:
        r = duvar_dikdortgeni(p)
        tur = p[4]
        if tur == "korkuluk":
            kork.append(p); continue
        e, cc, a, b = p[0], p[1], p[2], p[3]
        orta = (a + b) / 2
        if e == "x":
            iki = (oda_bul(kat, cc - 0.2, orta), oda_bul(kat, cc + 0.2, orta))
        else:
            iki = (oda_bul(kat, orta, cc - 0.2), oda_bul(kat, orta, cc + 0.2))
        tipler = [soz[k]["tip"] if k in soz else "DIS" for k in iki]
        if (kat == "Bodrum" and tur == "dis") or "asansor" in tipler:
            beton.append(r)
        else:
            duvar.append(r)
    kolon_kutulari = [(x - KOLON / 2, y - KOLON / 2, x + KOLON / 2, y + KOLON / 2) for x, y in kolonlar()]
    def ciz_rect(r, fill, stroke, sw):
        c.rect(tx(r[0]), ty(r[1]), (r[2] - r[0]) * s, (r[3] - r[1]) * s, fill=fill, stroke=stroke, sw=sw)
    with kayit.katman("DUVAR"):
        for r in duvar:
            ciz_rect(r, "none", "#111", KALIN)
    with kayit.katman("PERDE"):
        for r in beton:
            ciz_rect(r, "none", "#111", KALIN)
    with kayit.katman("KOLON"):
        for r in kolon_kutulari:
            ciz_rect(r, "none", "#111", KALIN)
    with kayit.katman("DUVAR-TARAMA"):
        for r in duvar:
            ciz_rect(r, "#e5e7eb", "none", 0)
            ciz_rect(r, "url(#p-duvar)", "none", 0)
    with kayit.katman("PERDE-TARAMA"):
        for r in beton:
            ciz_rect(r, "#111", "none", 0)
    with kayit.katman("KOLON-TARAMA"):
        for r in kolon_kutulari:
            ciz_rect(r, "#111", "none", 0)
    with kayit.katman("YALITIM"):
        # dış duvar ısı yalıtımı bandı (bodrum hariç: perde dışında su yalıtımı + XPS)
        for p in parcalar:
            if p[4] != "dis":
                continue
            e, cc, a, b = p[0], p[1], p[2], p[3]
            t = YALITIM
            if e == "x":
                x0 = cc if cc < 1e-6 else cc - t
                c.rect(tx(x0), ty(a), t * s, (b - a) * s, fill="#f4f1e8")
                c.line(tx(x0 + (t if cc < 1e-6 else 0)), ty(a), tx(x0 + (t if cc < 1e-6 else 0)), ty(b), 0.15)
            else:
                y0 = cc if cc < 1e-6 else cc - t
                c.rect(tx(a), ty(y0), (b - a) * s, t * s, fill="#f4f1e8")
                c.line(tx(a), ty(y0 + (t if cc < 1e-6 else 0)), tx(b), ty(y0 + (t if cc < 1e-6 else 0)), 0.15)
    # korkuluklar
    for p in kork:
        _korkuluk(c, p[0], p[1], p[2], p[3], tx, ty)
    for e, cc, a, b in MERDIVEN_KORKULUK.get(kat, []):
        _korkuluk(c, e, cc, a, b, tx, ty)
    # ---------------- açıklıklar
    for k in KAPILAR[kat]:
        kapi_svg(c, kat, k, tx, ty, s)
    for p in PENCERELER[kat]:
        pencere_plan(c, kat, p, tx, ty, s)
    # doğrama kodları
    from dograma import pencere_kodu, kapi_kodu
    for p in PENCERELER[kat]:
        m = (p[1] + p[2]) / 2
        x, y = {"K": (m, -0.42), "G": (m, H + 0.42), "B": (-0.42, m), "D": (W + 0.42, m)}[p[0]]
        if kat == "Zemin" and p[0] == "G":
            y = H + 0.42
        _etiket_kutu(c, tx(x), ty(y), pencere_kodu(kat, p))
    for k in KAPILAR[kat]:
        if k[4] in ("gecis",):
            continue
        kod = kapi_kodu(kat, k)
        e, cc, a, b = k[0], k[1], k[2], k[3]
        sol, sag = kapi_taraflari(kat, k)
        hedef = k[5] if k[5] in (sol, sag) else (sag if sol == "DIS" else sol)
        if k[4] in ("garaj",):
            hedef = sag
        yon = -1 if hedef == sol else 1
        if k[4] in ("giris", "servis", "garaj"):
            yon = -yon
        m = (a + b) / 2
        d = 0.32 + (DIS_DUVAR / 2 if k[4] in ("giris", "servis", "garaj") else IC_DUVAR / 2)
        x, y = (cc + yon * d, m) if e == "x" else (m, cc + yon * d)
        _etiket_kutu(c, tx(x), ty(y), kod, kapi=True)
    with kayit.katman("BACA"):
        # ---------------- şömine
        if kat == "Zemin":
            a, b = BACA["a"], BACA["b"]
            c.rect(tx(DIS_DUVAR), ty(a + 0.05), 0.45 * s, (b - a - 0.1) * s, fill="#fff", stroke="#111", sw=0.3)
            c.rect(tx(DIS_DUVAR), ty(a + 0.25), 0.25 * s, (b - a - 0.5) * s, fill="#374151")
            c.rect(tx(DIS_DUVAR + 0.45), ty(a - 0.35), 0.40 * s, (b - a + 0.7) * s, fill="none", stroke="#111", sw=0.18)
            c.text(tx(DIS_DUVAR + 1.1), ty((a + b) / 2) + 0.8, "şömine", 1.6, fill=GRI)
        if kat in ("Zemin", "1. Kat"):
            a, b, d = BACA["a"], BACA["b"], BACA["derinlik"]
            c.rect(tx(-d), ty(a), d * s, (b - a) * s, fill="url(#p-duvar)", stroke="#111", sw=KALIN)
            c.rect(tx(-d + 0.15), ty(a + 0.2), 0.3 * s, (b - a - 0.4) * s, fill="#fff", stroke="#111", sw=0.15)
    with kayit.katman("USTTE"):
        # ---------------- çatı arası kapağı
        if kat == KAT_BOSLUGU_KAPAK[0]:
            _, kx, ky = KAT_BOSLUGU_KAPAK
            c.rect(tx(kx - 0.35), ty(ky - 0.6), 0.7 * s, 1.2 * s, fill="none", stroke="#111", sw=0.15, dash="0.8,0.5")
            c.line(tx(kx - 0.35), ty(ky - 0.6), tx(kx + 0.35), ty(ky + 0.6), 0.1, dash="0.8,0.5")
            c.text(tx(kx), ty(ky + 0.6) + 2.2, "çatı kapağı", 1.4, "middle", fill=GRI)
    # ---------------- etiketler
    for m in KATLAR[kat]:
        mahal_etiketi(c, kat, m, tx, ty)
    for x, y, v in KOT_YERI.get(kat, []):
        _kot_isareti(c, tx(x), ty(y), kot_yazi(v), 1.9)
    # ---------------- ölçüler, akslar, kesit işaretleri
    if olculer:
        plan_olculeri(c, kat, tx, ty, s)
    if kesitler:
        pr = _projeksiyon(kat)
        kesit_isaretleri(c, tx, ty, s, pr)
    return c.svg()

def _etiket_kutu(c, X, Y, kod, kapi=False):
    if not kod:
        return
    w = 1.35 * len(kod) * 0.62 + 1.0
    if kapi:
        c.rect(X - w / 2, Y - 1.05, w, 2.1, fill="#fff", stroke="#111", sw=0.13, rx=1.0)
    else:
        c.poly([(X - w / 2 - 0.6, Y), (X - w / 2, Y - 1.05), (X + w / 2, Y - 1.05), (X + w / 2 + 0.6, Y),
                (X + w / 2, Y + 1.05), (X - w / 2, Y + 1.05)], fill="#fff", stroke="#111", sw=0.13)
    c.text(X, Y + 0.5, kod, 1.35, "middle", 700)

def _korkuluk(c, e, cc, a, b, tx, ty):
    d = 0.035
    if e == "x":
        c.rect(tx(cc - d), ty(a), 2 * d * 10, (b - a) * 10, fill="#fff", stroke="#111", sw=0.18)
    else:
        c.rect(tx(a), ty(cc - d), (b - a) * 10, 2 * d * 10, fill="#fff", stroke="#111", sw=0.18)

def _plan_dis_elemanlar(c, kat, tx, ty, s):
    if kat == "Zemin":
        # teras ve pergola
        t = TERAS
        c.rect(tx(t["x0"]), ty(t["y0"]), (t["x1"] - t["x0"]) * s, (t["y1"] - t["y0"]) * s,
               fill="url(#p-dis-tas)", stroke="#111", sw=0.25)
        pg = PERGOLA
        c.rect(tx(pg["x0"] + 0.1), ty(pg["y0"] + 0.05), (pg["x1"] - pg["x0"] - 0.2) * s, (pg["y1"] - pg["y0"] - 0.1) * s,
               stroke="#111", sw=0.18, dash="1.2,0.7")
        for px in (pg["x0"] + 0.2, pg["x1"] - 0.2):
            c.rect(tx(px - 0.1), ty(pg["y1"] - 0.3), 2, 2, fill="#111")
        c.text(tx((pg["x0"] + pg["x1"]) / 2), ty(pg["y1"] - 0.5), "alüminyum biyoklimatik pergola (üstte)", 1.6, "middle", fill=GRI)
        c.rect(tx(pg["x1"] - 2.4), ty(pg["y1"] - 1.3), 1.9 * s, 0.7 * s, fill="#fff", stroke="#111", sw=0.2)
        c.text(tx(pg["x1"] - 1.45), ty(pg["y1"] - 0.85), "barbekü", 1.5, "middle")
        c.text(tx(4.0), ty(17.4), "TERAS", 2.2, "middle", 700)
        c.text(tx(4.0), ty(17.4) + 2.6, "dış mekan traverten, R11", 1.6, "middle", fill=GRI)
        # giriş sahanlığı, basamaklar, saçak
        g = GIRIS_SACAGI
        c.rect(tx(g["x0"]), ty(-g["derinlik"]), (g["x1"] - g["x0"]) * s, g["derinlik"] * s,
               fill="url(#p-dis-tas)", stroke="#111", sw=0.25)
        for i, dy in enumerate((0.0, 0.32)):
            c.line(tx(g["x0"] - 0.0), ty(-g["derinlik"] - dy), tx(g["x1"]), ty(-g["derinlik"] - dy), 0.2)
        c.line(tx(g["x0"]), ty(-g["derinlik"] - 0.64), tx(g["x1"]), ty(-g["derinlik"] - 0.64), 0.2)
        c.rect(tx(g["x0"] - 0.1), ty(-g["derinlik"] - 0.1), (g["x1"] - g["x0"] + 0.2) * s, (g["derinlik"] + 0.1) * s,
               stroke="#111", sw=0.18, dash="1.2,0.7")
        c.text(tx((g["x0"] + g["x1"]) / 2), ty(-g["derinlik"] - 0.9), "2 basamak · giriş saçağı (üstte)", 1.6, "middle", fill=GRI)
        # garaj önü
        c.rect(tx(14.0), ty(-1.6), 6.0 * s, 1.6 * s, fill="url(#p-dis-tas)", stroke="#111", sw=0.18)
        c.text(tx(17.0), ty(-0.7), "araç yolu (granit küp taş) −0.20", 1.6, "middle", fill=GRI)
        # ışıklıklar (ızgara)
        for i in ISIKLIKLAR:
            _isiklik_plan(c, i, tx, ty, s, ust=True)
        # servis yolu
        c.text(tx(20.9), ty(7.0), "servis girişi", 1.6, fill=GRI, rot=-90)
    elif kat == "Bodrum":
        for i in ISIKLIKLAR:
            _isiklik_plan(c, i, tx, ty, s, ust=False)
        # toprak çizgisi (bodrum perdesinin dışı)
        c.rect(tx(-0.25), ty(-0.25), (W + 0.5) * s, (H + 0.5) * s, stroke="#8b7355", sw=0.18, dash="1.5,0.8")
    elif kat == "1. Kat":
        for bk in BALKONLAR:
            c.rect(tx(bk["x0"]), ty(H), (bk["x1"] - bk["x0"]) * s, bk["derinlik"] * s,
                   fill="url(#p-dis-tas)", stroke="#111", sw=0.3)
            _korkuluk(c, "y", H + bk["derinlik"] - 0.06, bk["x0"] + 0.05, bk["x1"] - 0.05, tx, ty)
            _korkuluk(c, "x", bk["x0"] + 0.06, H + 0.05, H + bk["derinlik"] - 0.05, tx, ty)
            _korkuluk(c, "x", bk["x1"] - 0.06, H + 0.05, H + bk["derinlik"] - 0.05, tx, ty)
            c.text(tx((bk["x0"] + bk["x1"]) / 2), ty(H + 0.95), bk["ad"].upper(), 1.8, "middle", 700)
            c.text(tx((bk["x0"] + bk["x1"]) / 2), ty(H + 0.95) + 2.3, "cam korkuluk h=110 · +3.18", 1.5, "middle", fill=GRI)
        g = GIRIS_SACAGI
        c.rect(tx(g["x0"]), ty(-g["derinlik"]), (g["x1"] - g["x0"]) * s, g["derinlik"] * s,
               stroke="#111", sw=0.25, fill="#f3f4f6")
        c.text(tx((g["x0"] + g["x1"]) / 2), ty(-g["derinlik"] / 2) + 0.6, "giriş saçağı (yeşil çatı, +2.95)", 1.5, "middle", fill=GRI)

def _isiklik_plan(c, i, tx, ty, s, ust):
    d = i["derinlik"]
    if i["cephe"] == "B":
        x0, x1 = -d, 0.0
    else:
        x0, x1 = W, W + d
    y0, y1 = i["a"], i["b"]
    if ust:
        c.rect(tx(x0), ty(y0), (x1 - x0) * s, (y1 - y0) * s, fill="url(#p-izgara)", stroke="#111", sw=0.3)
        c.text(tx((x0 + x1) / 2), ty((y0 + y1) / 2), "ışıklık (galvaniz ızgara)", 1.4, "middle", fill=GRI, rot=-90)
    else:
        t = 0.25
        wx0, wx1 = (x0 - t, x0) if i["cephe"] == "B" else (x1, x1 + t)
        c.rect(tx(wx0), ty(y0 - t), t * s, (y1 - y0 + 2 * t) * s, fill="#111")
        c.rect(tx(x0 if i["cephe"] == "B" else x0), ty(y0 - t), d * s, t * s, fill="#111")
        c.rect(tx(x0 if i["cephe"] == "B" else x0), ty(y1), d * s, t * s, fill="#111")
        c.rect(tx(x0), ty(y0), (x1 - x0) * s, (y1 - y0) * s, fill="url(#p-dis-tas)")
        c.text(tx((x0 + x1) / 2), ty((y0 + y1) / 2), "ışıklık −3.16 · süzgeçli", 1.4, "middle", fill=GRI, rot=-90)
        # kaçış merdiveni (dikme basamak)
        if i["cephe"] == "B" and i["a"] > 10:
            for k in range(6):
                yy = y1 - 0.25 - k * 0.12
                c.line(tx(x0 + 0.1), ty(yy), tx(x0 + 0.5), ty(yy), 0.12)
            c.text(tx(x0 + 0.1), ty(y1 - 1.2), "kaçış", 1.3, fill=GRI, rot=-90)

def mahal_etiketi(c, kat, m, tx, ty):
    if m["tip"] in ("asansor", "saft"):
        if m["tip"] == "saft":
            r = m["r"][0]
            c.text(tx((r[0] + r[2]) / 2), ty((r[1] + r[3]) / 2), "ŞAFT", 1.4, "middle", 700, rot=-90)
        return
    if m["tip"] == "merdiven":
        return
    if m["tip"] == "bosluk":
        r = m["r"][0]
        c.line(tx(r[0] + 0.1), ty(r[1] + 0.45), tx(r[2] - 0.1), ty(r[3] - 0.1), 0.13)
        c.line(tx(r[0] + 0.1), ty(r[3] - 0.1), tx(r[2] - 0.1), ty(r[1] + 0.45), 0.13)
        c.text(tx((r[0] + r[2]) / 2), ty((r[1] + r[3]) / 2) + 3.2, "GALERİ BOŞLUĞU", 1.7, "middle", 700)
        return
    alan, dar, uzun = net_alan(m)
    if m["kod"] in ETIKET_YERI:
        x, y = ETIKET_YERI[m["kod"]]
    else:
        r = max(m["r"], key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
        x, y = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    X, Y = tx(x), ty(y)
    ad = m["ad"].upper()
    dar_mahal = min(q[2] - q[0] for q in m["r"]) < 1.6
    boy = 1.75 if dar_mahal else 2.05
    satirlar = _sar(ad, 13 if dar_mahal else 20)
    yy = Y - (len(satirlar) - 1) * boy * 0.55
    if m["tip"] == "sirkulasyon" and max(q[3] - q[1] for q in m["r"]) > 3 and min(q[2] - q[0] for q in m["r"]) < 1.6:
        # dar koridor: dikey yazı
        c.text(X, Y, "%s · %s m²" % (m["ad"].upper(), f2(alan).replace(".", ",")), 1.6, "middle", 700, rot=-90)
        return
    for i, sat in enumerate(satirlar):
        c.text(X, yy + i * boy * 1.05, sat, boy, "middle", 700)
    y2 = yy + len(satirlar) * boy * 1.05 + 0.2
    c.text(X, y2, "%s · %s m²" % (m["kod"], f2(alan).replace(".", ",")), 1.55, "middle", fill="#1f2937")
    dos = OZEL_DOSEME.get(m["kod"], DOSEME_ADI.get(m["tip"], ""))
    if dos:
        c.text(X, y2 + 2.1, dos, 1.4, "middle", fill=GRI, italic=True)

# ---------------------------------------------------------------- kapılar
def kapi_svg(c, kat, k, tx, ty, s):
    e, cc, a, b, tip, hedef, mentese = k
    t, f0, f1 = duvar_kalinligi(kat, e, cc, a, b)
    if tip in ("kapi", "yangin", "giris", "servis", "kapak"):
        (hx, hy), (ox, oy), (kx, ky), yon, w = kanat_geometrisi(kat, k)
        kal = 0.3 if tip != "kapak" else 0.18
        c.line(tx(hx), ty(hy), tx(ox), ty(oy), kal)
        r = w * s
        # yay: açık uçtan kapalı uca
        sweep = _yay_yonu(hx, hy, ox, oy, kx, ky)
        c.path("M%.2f %.2f A%.2f %.2f 0 0 %d %.2f %.2f" % (tx(ox), ty(oy), r, r, sweep, tx(kx), ty(ky)),
               stroke="#111", sw=COK_INCE)
        # kasa
        _kasa(c, e, f0, f1, a, b, tx, ty)
        if tip == "yangin":
            mx, my = (tx((hx + kx) / 2), ty((hy + ky) / 2))
            c.text(tx((hx + ox + kx) / 3) + (0 if e == "y" else 0), ty((hy + oy + ky) / 3) + 0.6, "EI30", 1.3, "middle", 700, fill="#b91c1c")
    elif tip == "cift":
        w2 = (b - a) / 2
        sol, sag = kapi_taraflari(kat, k)
        yon, yuz = (-1, f0) if hedef == sol else (1, f1)
        for (h, d) in ((a, a + w2), (b, b - w2)):
            if e == "x":
                c.line(tx(yuz), ty(h), tx(yuz + yon * w2), ty(h), 0.3)
                sw = _yay_yonu(yuz, h, yuz + yon * w2, h, yuz, d)
                c.path("M%.2f %.2f A%.2f %.2f 0 0 %d %.2f %.2f" % (tx(yuz + yon * w2), ty(h), w2 * s, w2 * s, sw, tx(yuz), ty(d)), sw=COK_INCE)
            else:
                c.line(tx(h), ty(yuz), tx(h), ty(yuz + yon * w2), 0.3)
                sw = _yay_yonu(h, yuz, h, yuz + yon * w2, d, yuz)
                c.path("M%.2f %.2f A%.2f %.2f 0 0 %d %.2f %.2f" % (tx(h), ty(yuz + yon * w2), w2 * s, w2 * s, sw, tx(d), ty(yuz)), sw=COK_INCE)
        _kasa(c, e, f0, f1, a, b, tx, ty)
    elif tip == "surme":
        m = (f0 + f1) / 2
        L = (b - a) / 2 + 0.05
        for i, (p0, off) in enumerate(((a, -0.025), (b - L, 0.025))):
            if e == "x":
                c.rect(tx(m + off - 0.02), ty(p0), 0.4, L * s, fill="#fff", stroke="#111", sw=0.2)
            else:
                c.rect(tx(p0), ty(m + off - 0.02), L * s, 0.4, fill="#fff", stroke="#111", sw=0.2)
        _kasa(c, e, f0, f1, a, b, tx, ty)
    elif tip == "gecis":
        for f in (f0, f1):
            if e == "x":
                c.line(tx(f), ty(a), tx(f), ty(b), 0.12, dash="0.9,0.6")
            else:
                c.line(tx(a), ty(f), tx(b), ty(f), 0.12, dash="0.9,0.6")
    elif tip == "garaj":
        m = f0 + 0.05
        c.line(tx(a), ty(f1 - 0.05), tx(b), ty(f1 - 0.05), 0.35)
        c.rect(tx(a + 0.05), ty(f1 + 0.05), (b - a - 0.1) * s, 2.6 * s, stroke="#111", sw=0.13, dash="1.0,0.7")
        c.text(tx((a + b) / 2), ty(f1 + 0.3), "seksiyonel kapı 480×240", 1.35, "middle", fill=GRI)
    elif tip == "asansor":
        m = (f0 + f1) / 2
        if e == "x":
            c.line(tx(f1 - 0.02), ty(a + 0.05), tx(f1 - 0.02), ty(b - 0.05), 0.35)
            c.line(tx(f1 - 0.06), ty(a + 0.05), tx(f1 - 0.06), ty((a + b) / 2 + 0.05), 0.2)
        else:
            c.line(tx(a + 0.05), ty(f1 - 0.02), tx(b - 0.05), ty(f1 - 0.02), 0.35)

def _kasa(c, e, f0, f1, a, b, tx, ty):
    for p in (a, b):
        if e == "x":
            c.line(tx(f0), ty(p), tx(f1), ty(p), 0.18)
        else:
            c.line(tx(p), ty(f0), tx(p), ty(f1), 0.18)

def _yay_yonu(hx, hy, ox, oy, kx, ky):
    """Açık uçtan kapalı uca, menteşe merkezli kısa yay için SVG sweep bayrağı."""
    v1 = (ox - hx, oy - hy); v2 = (kx - hx, ky - hy)
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    return 1 if cross > 0 else 0

# ---------------------------------------------------------------- pencere (plan)
def pencere_plan(c, kat, p, tx, ty, s):
    cephe, a, b, tip = p[0], p[1], p[2], p[3]
    t = DIS_DUVAR
    # derinlik: dıştan içe
    def seg(d0, d1, w=0.18, col="#111"):
        if cephe == "K":
            c.line(tx(a), ty(d0), tx(b), ty(d0), w, col); c.line(tx(a), ty(d1), tx(b), ty(d1), w, col)
        elif cephe == "G":
            c.line(tx(a), ty(H - d0), tx(b), ty(H - d0), w, col); c.line(tx(a), ty(H - d1), tx(b), ty(H - d1), w, col)
        elif cephe == "B":
            c.line(tx(d0), ty(a), tx(d0), ty(b), w, col); c.line(tx(d1), ty(a), tx(d1), ty(b), w, col)
        else:
            c.line(tx(W - d0), ty(a), tx(W - d0), ty(b), w, col); c.line(tx(W - d1), ty(a), tx(W - d1), ty(b), w, col)
    def kutu(d0, d1, p0, p1, fill="#fff", w=0.18):
        if cephe == "K":
            c.rect(tx(p0), ty(d0), (p1 - p0) * s, (d1 - d0) * s, fill=fill, stroke="#111", sw=w)
        elif cephe == "G":
            c.rect(tx(p0), ty(H - d1), (p1 - p0) * s, (d1 - d0) * s, fill=fill, stroke="#111", sw=w)
        elif cephe == "B":
            c.rect(tx(d0), ty(p0), (d1 - d0) * s, (p1 - p0) * s, fill=fill, stroke="#111", sw=w)
        else:
            c.rect(tx(W - d1), ty(p0), (d1 - d0) * s, (p1 - p0) * s, fill=fill, stroke="#111", sw=w)
    # boşluğu beyazla aç (yalıtım bandı üstünü örter)
    kutu(0.0, t, a, b, fill="#fff", w=0)
    if tip == "S":
        L = (b - a) / 2 + 0.04
        kutu(0.10, 0.155, a, a + L, fill=CAM, w=0.2)
        kutu(0.175, 0.23, b - L, b, fill=CAM, w=0.2)
        seg(0.0, t, 0.13)
    else:
        seg(0.0, t, 0.13)                               # dış ve iç yüz
        kutu(0.12, 0.20, a, b, fill=CAM, w=0.2)         # çerçeve + cam
        if tip in ("P", "Y", "I"):
            seg(-0.04, -0.04, 0.13)                     # dış denizlik
    # kasa çizgileri
    for q in (a, b):
        if cephe in ("K", "G"):
            y0, y1 = (0, t) if cephe == "K" else (H - t, H)
            c.line(tx(q), ty(y0), tx(q), ty(y1), 0.3)
        else:
            x0, x1 = (0, t) if cephe == "B" else (W - t, W)
            c.line(tx(x0), ty(q), tx(x1), ty(q), 0.3)

# ---------------------------------------------------------------- merdiven / asansör (plan)
def merdiven_plan(c, kat, tx, ty, s):
    kutu = MERDIVEN["kutu"]
    ic = ic_sinir(kutu)
    up = merdiven_kollari(kat)
    idx = KATLAR_SIRA.index(kat)
    down = merdiven_kollari(KATLAR_SIRA[idx - 1]) if idx > 0 else None
    b = MERDIVEN["basamak"]
    s0, s1 = MERDIVEN["sahanlik"]
    bx0, bx1 = MERDIVEN["bati_kol"]; dx0, dx1 = MERDIVEN["dogu_kol"]
    kesme_h = 1.20
    def basamaklar(x0, x1, y_ilk, n, yon, dash=None, maks=None):
        # y_ilk: ilk rıht çizgisi; yon +1 güneye, −1 kuzeye; n rıht → n çizgi (son çizgi sahanlık kenarı)
        cizgiler = []
        for i in range(n):
            yy = y_ilk + yon * i * b
            if maks is not None and i > maks:
                break
            cizgiler.append(yy)
            c.line(tx(x0), ty(yy), tx(x1), ty(yy), 0.15, dash=dash)
        return cizgiler
    # sahanlık
    if up or down:
        c.rect(tx(bx0), ty(s0), (dx1 - bx0) * s, (s1 - s0) * s, fill="url(#p-tas)", stroke="#111", sw=0.15,
               dash=None if (down or kat == "1. Kat") else "0.9,0.6")
    if up:
        k1, k2 = up["kollar"]
        n_kes = int(kesme_h / up["riht"])
        # batı kol: ilk rıht y = k1[2]
        y_ilk = k1[2]
        ciz = basamaklar(bx0, bx1, y_ilk, k1[4], +1, maks=n_kes)
        basamaklar(bx0, bx1, y_ilk + (n_kes + 1) * b, k1[4] - n_kes - 1, +1, dash="0.9,0.6")
        yk = y_ilk + n_kes * b + 0.14
        c.poly([(tx(bx0), ty(yk + 0.35)), (tx(bx0 + 0.45), ty(yk + 0.35)), (tx(bx0 + 0.6), ty(yk + 0.15)),
                (tx(bx0 + 0.72), ty(yk + 0.45)), (tx(bx1), ty(yk - 0.25))], kapali=False, sw=0.2)
        c.line(tx(bx0), ty(k1[2]), tx(bx0), ty(s0), 0.2); c.line(tx(bx1), ty(k1[2]), tx(bx1), ty(s0), 0.2)
        # çıkış oku
        xm = (bx0 + bx1) / 2
        c.circle(tx(xm), ty(k1[2] - 0.18), 0.5, fill="#111", stroke="none")
        c.line(tx(xm), ty(k1[2] - 0.18), tx(xm), ty(yk - 0.1), 0.25)
        c.poly([(tx(xm - 0.12), ty(yk - 0.35)), (tx(xm + 0.12), ty(yk - 0.35)), (tx(xm), ty(yk - 0.05))], fill="#111", stroke="none")
        c.text(tx(xm), ty(k1[2] - 0.45), "ÇIKIŞ", 1.45, "middle", 700)
        c.text(tx(xm) + 0.2, ty(yk + 0.9), "%d×%s/%s" % (k1[4] + k2[4], ("%.1f" % (up["riht"] * 100)).replace(".", ","), cm(b)),
               1.3, "middle", fill=GRI, rot=-90)
        if not down:
            # doğu kol yukarıda (kesik)
            basamaklar(dx0, dx1, k2[2], k2[4], -1, dash="0.9,0.6")
    if down:
        k1, k2 = down["kollar"]
        # alt kattan gelen doğu kol (tam görünür)
        basamaklar(dx0, dx1, k2[2], k2[4], -1)
        c.line(tx(dx0), ty(k2[3]), tx(dx0), ty(s0), 0.2); c.line(tx(dx1), ty(k2[3]), tx(dx1), ty(s0), 0.2)
        xm = (dx0 + dx1) / 2
        c.line(tx(xm), ty(k2[3] + 0.25), tx(xm), ty(s0 - 0.25), 0.25)
        c.poly([(tx(xm - 0.12), ty(s0 - 0.5)), (tx(xm + 0.12), ty(s0 - 0.5)), (tx(xm), ty(s0 - 0.2))], fill="#111", stroke="none")
        c.text(tx(xm), ty(k2[3] - 0.15), "İNİŞ", 1.45, "middle", 700)
        if not up:
            # en üst kat: batı kol da aşağıda, tam görünür
            basamaklar(bx0, bx1, k1[2], k1[4], +1)
            c.line(tx(bx0), ty(k1[2]), tx(bx0), ty(s0), 0.2); c.line(tx(bx1), ty(k1[2]), tx(bx1), ty(s0), 0.2)
    # merdiven gözü
    c.line(tx(bx1), ty(4.4), tx(bx1), ty(s0), 0.13)
    c.line(tx(dx0), ty(4.4), tx(dx0), ty(s0), 0.13)

def asansor_plan(c, kat, tx, ty, s):
    x0, y0, x1, y1 = ic_sinir(ASANSOR["kuyu"])
    # kabin 1,40 (derinlik, x) × 1,10 (y), kapı batıda
    kx0, kx1 = x0 + 0.12, x0 + 0.12 + 1.40
    ky0, ky1 = (y0 + y1) / 2 - 0.55, (y0 + y1) / 2 + 0.55
    c.rect(tx(kx0), ty(ky0), (kx1 - kx0) * s, (ky1 - ky0) * s, fill="#fff", stroke="#111", sw=0.2)
    c.line(tx(kx0), ty(ky0), tx(kx1), ty(ky1), 0.13); c.line(tx(kx0), ty(ky1), tx(kx1), ty(ky0), 0.13)
    c.rect(tx(x1 - 0.22), ty(y0 + 0.25), 0.15 * s, (y1 - y0 - 0.5) * s, fill="#d1d5db", stroke="#111", sw=0.13)
    c.text(tx((x0 + x1) / 2), ty(y1 - 0.12), "ASANSÖR 630 kg", 1.3, "middle", 700)

# ---------------------------------------------------------------- mobilya sembolleri
def mobilya_svg(c, o, tx, ty, s):
    tip, cx, cy, rot, p = o
    with kayit.donusum(tx(cx), ty(cy), rot):
        _mobilya_ciz(c, o, tx, ty, s)

def _mobilya_ciz(c, o, tx, ty, s):
    tip, cx, cy, rot, p = o
    w, d = olcu(tip, p)
    g = Cizim()
    # yerel koordinat: merkez (0,0), x ∈ [−w/2, w/2], y ∈ [−d/2, d/2]; sırt y = −d/2
    hw, hd = w / 2, d / 2
    st = dict(stroke=MOB, sw=0.13)
    def R(x0, y0, x1, y1, fill="#fff", rx=0, sw=0.13, dash=None):
        g.rect(x0 * s, y0 * s, (x1 - x0) * s, (y1 - y0) * s, fill=fill, stroke=MOB, sw=sw, rx=rx * s, dash=dash)
    def Lm(x0, y0, x1, y1, sw=0.1):
        g.line(x0 * s, y0 * s, x1 * s, y1 * s, sw, MOB)
    def C(x, y, r, fill="#fff"):
        g.circle(x * s, y * s, r * s, fill=fill, stroke=MOB, sw=0.12)
    if tip == "yatak_cift":
        bw = p
        R(-bw / 2, -hd, bw / 2, hd, rx=0.03)
        R(-bw / 2, -hd, bw / 2, -hd + 0.10, fill="#e5e7eb")
        for k in (-1, 1):
            R(k * bw / 4 - bw / 4 + 0.06 if k < 0 else 0.04, -hd + 0.18, (k * bw / 4 + bw / 4 - 0.04) if k < 0 else bw / 2 - 0.06, -hd + 0.55, rx=0.06)
        Lm(-bw / 2, -hd + 0.75, bw / 2, -hd + 0.75)
        Lm(-bw / 2, -hd + 0.75, -bw / 2 + 0.25, -hd + 0.95)
        for k in (-1, 1):
            R(k * (bw / 2 + 0.05) - (0.45 if k < 0 else 0), -hd, k * (bw / 2 + 0.05) + (0 if k < 0 else 0.45), -hd + 0.42)
            C(k * (bw / 2 + 0.275), -hd + 0.21, 0.1)
    elif tip in ("gardirop", "vestiyer"):
        R(-hw, -hd, hw, hd)
        n = max(1, int(round(w / 0.5)))
        for i in range(1, n):
            Lm(-hw + i * w / n, -hd, -hw + i * w / n, hd)
        Lm(-hw, -hd, hw, hd, 0.07)
    elif tip in ("koltuk", "berjer"):
        R(-hw, -hd, hw, hd, rx=0.08)
        R(-hw, -hd, hw, -hd + 0.2, fill="#f3f4f6", rx=0.06)
        R(-hw, -hd, -hw + 0.15, hd, fill="#f3f4f6", rx=0.05); R(hw - 0.15, -hd, hw, hd, fill="#f3f4f6", rx=0.05)
    elif tip == "kanepe":
        R(-hw, -hd, hw, hd, rx=0.08)
        R(-hw, -hd, hw, -hd + 0.22, fill="#f3f4f6", rx=0.05)
        n = max(2, int(w / 0.8))
        for i in range(1, n):
            Lm(-hw + 0.18 + i * (w - 0.36) / n, -hd + 0.22, -hw + 0.18 + i * (w - 0.36) / n, hd)
        R(-hw, -hd, -hw + 0.18, hd, fill="#f3f4f6", rx=0.05); R(hw - 0.18, -hd, hw, hd, fill="#f3f4f6", rx=0.05)
    elif tip == "kanepe_l":
        g.path("M%.2f %.2f H%.2f V%.2f H%.2f V%.2f H%.2f Z" % (
            -hw * s, -hd * s, hw * s, (-hd + 0.95) * s, (-hw + 0.95) * s, hd * s, -hw * s),
            fill="#fff", stroke=MOB, sw=0.13)
        R(-hw, -hd, hw, -hd + 0.22, fill="#f3f4f6"); R(-hw, -hd, -hw + 0.22, hd, fill="#f3f4f6")
        for i in range(1, 4):
            Lm(-hw + 0.95 + i * (w - 0.95) / 4, -hd + 0.22, -hw + 0.95 + i * (w - 0.95) / 4, -hd + 0.95)
    elif tip == "sehpa":
        R(-hw, -hd, hw, hd, fill="#f9fafb", rx=0.04)
    elif tip == "hali":
        R(-hw, -hd, hw, hd, fill="none", sw=0.1, dash=None)
        R(-hw + 0.08, -hd + 0.08, hw - 0.08, hd - 0.08, fill="none", sw=0.07)
    elif tip == "tv_unite" or tip == "komodin_tv" or tip == "bufe":
        R(-hw, -hd, hw, hd)
        if tip != "bufe":
            R(-hw * 0.7, -hd - 0.02, hw * 0.7, -hd + 0.06, fill="#374151")
    elif tip == "yemek_masasi":
        tw, td = (2.4, 1.0) if p >= 8 else (1.6, 0.9)
        R(-tw / 2, -td / 2, tw / 2, td / 2, rx=0.03)
        n = p // 2 - 1 if p >= 8 else 2
        for i in range(n):
            xx = -tw / 2 + (i + 0.5) * tw / n
            for k in (-1, 1):
                R(xx - 0.22, k * (td / 2 + 0.05) - (0.42 if k < 0 else 0), xx + 0.22, k * (td / 2 + 0.05) + (0 if k < 0 else 0.42), rx=0.05)
        for k in (-1, 1):
            R(k * (tw / 2 + 0.05) - (0.42 if k < 0 else 0), -0.22, k * (tw / 2 + 0.05) + (0 if k < 0 else 0.42), 0.22, rx=0.05)
    elif tip == "tezgah":
        R(-hw, -hd, hw, hd, fill="#fafafa")
        Lm(-hw, hd - 0.04, hw, hd - 0.04, 0.07)
        if w >= 3.0:
            R(-0.4, -hd + 0.1, 0.4, hd - 0.12, rx=0.04); C(0, -hd + 0.14, 0.03)            # eviye
            for i, xx in enumerate((-1.2, -0.8)):
                pass
            for dx, dy in ((0.95, -0.13), (1.3, -0.13), (0.95, 0.13), (1.3, 0.13)):   # ocak
                C(dx + 0.2, dy, 0.09)
    elif tip == "ada":
        R(-hw, -hd, hw, hd, fill="#fafafa", rx=0.02)
        R(-hw, -hd, hw, -hd + 0.62, fill="#fafafa")
        for dx in (-0.4, 0, 0.4):
            for dy in (-0.15,):
                C(dx - 0.6, -hd + 0.31 + dy + 0.15, 0.09)
        R(0.2, -hd + 0.1, 1.0, -hd + 0.52, rx=0.04)
    elif tip == "bar_tabure":
        n = p
        for i in range(n):
            C(-hw + 0.275 + i * 0.55, 0, 0.19)
    elif tip == "buzdolabi":
        R(-hw, -hd, hw, hd, fill="#f3f4f6"); Lm(0, -hd, 0, hd); Lm(-hw, -hd, hw, hd, 0.06)
    elif tip == "araba":
        R(-hw, -hd, hw, hd, fill="none", rx=0.35, sw=0.15)
        R(-hw + 0.12, -hd + 1.25, hw - 0.12, -hd + 1.9, fill="#f3f4f6", rx=0.1)
        R(-hw + 0.12, hd - 1.35, hw - 0.12, hd - 0.9, fill="#f3f4f6", rx=0.1)
        R(-hw + 0.15, -hd + 1.95, hw - 0.15, hd - 1.4, fill="none", rx=0.1)
    elif tip == "wc":
        R(-0.2, -hd, 0.2, -hd + 0.18, rx=0.03)
        g.path("M%.2f %.2f Q%.2f %.2f %.2f %.2f Q%.2f %.2f %.2f %.2f Z" % (
            -0.18 * s, (-hd + 0.18) * s, -0.2 * s, hd * s, 0, hd * s, 0.2 * s, hd * s, 0.18 * s, (-hd + 0.18) * s),
            fill="#fff", stroke=MOB, sw=0.13)
    elif tip == "lavabo":
        R(-hw, -hd, hw, hd, fill="#fafafa")
        n = 2 if w >= 1.4 else 1
        for i in range(n):
            xx = -hw + (i + 0.5) * w / n
            g.path("M%.2f %.2f a%.2f %.2f 0 1 0 0.01 0" % ((xx - 0.2) * s, 0.05 * s, 0.2 * s, 0.15 * s), fill="#fff", stroke=MOB, sw=0.12)
    elif tip == "dus":
        R(-hw, -hd, hw, hd, fill="#fff")
        Lm(-hw, -hd, hw, hd, 0.07); Lm(-hw, hd, hw, -hd, 0.07); C(0, 0, 0.05)
    elif tip in ("kuvet", "kuvet_serbest"):
        rx = 0.35 if tip == "kuvet_serbest" else 0.05
        R(-hw, -hd, hw, hd, rx=rx)
        R(-hw + 0.08, -hd + 0.08, hw - 0.08, hd - 0.08, rx=rx * 0.8)
        C(hw - 0.3, 0, 0.04)
    elif tip == "masa":
        R(-hw, -0.6, hw, 0.1)
        R(-0.24, 0.15, 0.24, 0.58, rx=0.07)
    elif tip == "masa_yuvarlak":
        C(0, 0, p / 2)
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            C(math.cos(a) * (p / 2 + 0.22), math.sin(a) * (p / 2 + 0.22), 0.2)
    elif tip == "kitaplik" or tip == "raf" or tip == "sarap_raf":
        R(-hw, -hd, hw, hd, fill="#fafafa")
        n = max(1, int(w / 0.8))
        for i in range(1, n):
            Lm(-hw + i * w / n, -hd, -hw + i * w / n, hd, 0.07)
        if tip == "sarap_raf":
            for i in range(int(w / 0.12)):
                C(-hw + 0.06 + i * 0.12, 0, 0.035, fill="#fff")
    elif tip == "piyano":
        R(-hw, -hd, hw, hd); R(-hw + 0.05, hd - 0.2, hw - 0.05, hd, fill="#f3f4f6")
        for i in range(1, 12):
            Lm(-hw + 0.05 + i * (w - 0.1) / 12, hd - 0.2, -hw + 0.05 + i * (w - 0.1) / 12, hd, 0.05)
    elif tip == "sinema_koltuk":
        for i in range(p):
            x0 = -hw + i * 0.95
            R(x0 + 0.03, -hd, x0 + 0.92, hd, rx=0.08)
            R(x0 + 0.03, -hd, x0 + 0.92, -hd + 0.22, fill="#f3f4f6", rx=0.06)
    elif tip == "perde":
        R(-hw, -hd, hw, hd, fill="#374151")
    elif tip == "bilardo":
        R(-hw, -hd, hw, hd, fill="#fff", rx=0.06)
        R(-hw + 0.1, -hd + 0.1, hw - 0.1, hd - 0.1, fill="#f3f4f6")
        for x in (-hw + 0.12, 0, hw - 0.12):
            for y in (-hd + 0.12, hd - 0.12):
                C(x, y, 0.05)
    elif tip == "bar":
        R(-hw, -hd, hw, hd, fill="#fafafa")
        for i in range(int(w / 0.6)):
            C(-hw + 0.3 + i * 0.6, hd + 0.25, 0.17)
    elif tip in ("pano",):
        R(-hw, -hd, hw, hd, fill="#e5e7eb")
    elif tip == "kazan":
        R(-hw, -hd, hw, hd, fill="#e5e7eb"); C(0, 0, 0.12)
    elif tip == "boyler":
        C(0, 0, 0.35, fill="#f3f4f6"); C(0, 0, 0.3)
    elif tip == "depo_tank":
        R(-hw, -hd, 0, hd, rx=0.1, fill="#f3f4f6"); R(0.05, -hd, hw, hd, rx=0.1, fill="#f3f4f6")
    elif tip == "filtre":
        C(-0.4, 0, 0.3, fill="#f3f4f6"); R(0.0, -0.3, 0.7, 0.3, fill="#e5e7eb")
    elif tip in ("bank", "sauna_bank"):
        R(-hw, -hd, hw, hd, fill="#f5efe6")
        for i in range(1, int(w / 0.12)):
            Lm(-hw + i * 0.12, -hd, -hw + i * 0.12, hd, 0.05)
        if tip == "sauna_bank":
            Lm(-hw, 0, hw, 0, 0.12)
    elif tip == "kosu":
        R(-hw, -hd, hw, hd, rx=0.08); R(-hw + 0.1, -hd + 0.3, hw - 0.1, hd - 0.1, fill="#f3f4f6")
    elif tip == "agirlik":
        R(-hw, -hd, hw, hd, rx=0.05); R(-0.1, -hd + 0.1, 0.1, hd - 0.1, fill="#e5e7eb")
    elif tip == "yoga":
        R(-0.3, -0.9, 0.3, 0.9, fill="none", rx=0.05, sw=0.08)
    elif tip == "camasir":
        R(-hw, -hd, hw, hd); C(0, 0.03, 0.21)
    elif tip == "utu":
        g.path("M%.2f %.2f H%.2f L%.2f %.2f L%.2f %.2f H%.2f Z" % (-hw * s, -hd * s, 0.3 * s, hw * s, 0, 0.3 * s, hd * s, -hw * s),
               fill="#fff", stroke=MOB, sw=0.12)
    elif tip == "ada_dolap":
        R(-hw, -hd, hw, hd, fill="#fafafa"); Lm(-hw, 0, hw, 0, 0.07)
    elif tip == "bitki":
        C(0, 0, 0.25, fill="#fff")
        for k in range(6):
            a = k * math.pi / 3
            Lm(0, 0, 0.22 * math.cos(a), 0.22 * math.sin(a), 0.07)
    c.add('<g transform="translate(%.2f %.2f) rotate(%.1f)">%s</g>' % (tx(cx), ty(cy), rot, g.svg()))

# ---------------------------------------------------------------- ölçüler, akslar
def _projeksiyon(kat):
    """Her cephedeki en büyük taşma (m) — ölçü zincirlerini dışarı itmek için."""
    pr = {"K": 0.3, "G": 0.3, "B": 0.3, "D": 0.3}
    if kat == "Zemin":
        pr["K"] = GIRIS_SACAGI["derinlik"] + 0.9
    if kat == "1. Kat":
        pr["G"] = max(b["derinlik"] for b in BALKONLAR) + 0.2
        pr["K"] = GIRIS_SACAGI["derinlik"] + 0.2
    if kat in ("Bodrum", "Zemin"):
        pr["B"] = max(pr["B"], 1.7); pr["D"] = max(pr["D"], 1.7)
    if kat in ("Zemin", "1. Kat"):
        pr["B"] = max(pr["B"], BACA["derinlik"] + 0.2)
    return pr

def plan_olculeri(c, kat, tx, ty, s):
    pr = _projeksiyon(kat)
    aks_x = [v for _, v in AKS_X]; aks_y = [v for _, v in AKS_Y]
    for cephe in ("K", "G", "B", "D"):
        acik = [p for p in PENCERELER[kat] if p[0] == cephe]
        dis_kapi = [k for k in KAPILAR[kat] if k[4] in ("giris", "garaj", "servis")
                    and ((cephe == "K" and k[0] == "y" and k[1] == 0) or (cephe == "G" and k[0] == "y" and k[1] == H)
                         or (cephe == "B" and k[0] == "x" and k[1] == 0) or (cephe == "D" and k[0] == "x" and k[1] == W))]
        uc = W if cephe in ("K", "G") else H
        nok = [0.0, uc] + [q for p in acik for q in (p[1], p[2])] + [q for k in dis_kapi for q in (k[2], k[3])]
        d0 = pr[cephe] * s + 4
        if cephe == "K":
            sab = [ty(0) - d0, ty(0) - d0 - 6, ty(0) - d0 - 12]
            olcu_zinciri(c, nok, "x", sab[0], tx, True, uzatma=ty(0) - 1)
            olcu_zinciri(c, aks_x, "x", sab[1], tx, True)
            olcu_zinciri(c, [0, W], "x", sab[2], tx, True)
            for ad, v in AKS_X:
                c.line(tx(v), sab[2] - 2, tx(v), ty(H) + pr["G"] * s + 18, 0.08, "#9ca3af", dash="3,1,0.5,1")
                aks_balonu(c, tx(v), sab[2] - 6, ad)
        elif cephe == "G":
            sab = [ty(H) + d0, ty(H) + d0 + 6, ty(H) + d0 + 12]
            olcu_zinciri(c, nok, "x", sab[0], tx, False)
            olcu_zinciri(c, aks_x, "x", sab[1], tx, False)
            olcu_zinciri(c, [0, W], "x", sab[2], tx, False)
            for ad, v in AKS_X:
                aks_balonu(c, tx(v), sab[2] + 6.5, ad)
        elif cephe == "B":
            sab = [tx(0) - d0, tx(0) - d0 - 6, tx(0) - d0 - 12]
            olcu_zinciri(c, nok, "y", sab[0], ty, True)
            olcu_zinciri(c, aks_y, "y", sab[1], ty, True)
            olcu_zinciri(c, [0, H], "y", sab[2], ty, True)
            for ad, v in AKS_Y:
                c.line(sab[2] - 2, ty(v), tx(W) + pr["D"] * s + 18, ty(v), 0.08, "#9ca3af", dash="3,1,0.5,1")
                aks_balonu(c, sab[2] - 6, ty(v), ad)
        else:
            sab = [tx(W) + d0, tx(W) + d0 + 6, tx(W) + d0 + 12]
            olcu_zinciri(c, nok, "y", sab[0], ty, False)
            olcu_zinciri(c, aks_y, "y", sab[1], ty, False)
            olcu_zinciri(c, [0, H], "y", sab[2], ty, False)
            for ad, v in AKS_Y:
                aks_balonu(c, sab[2] + 6.5, ty(v), ad)
    # iç ölçü zinciri: yatay (y = 6.0) ve düşey (x = 13.3 koridor hattı)
    ic_zincir(c, kat, "x", 12.3 if kat != "Bodrum" else 11.2, tx, ty)
    ic_zincir(c, kat, "y", 3.0 if kat != "Bodrum" else 6.6, tx, ty)

def ic_zincir(c, kat, eksen, sabit, tx, ty):
    """Bir doğru boyunca duvar yüzlerinden iç ölçü zinciri."""
    noktalar = []
    for s in ham_kenarlar(kat):
        if s[6] == "korkuluk":
            continue
        if eksen == "x" and s[0] == "x" and s[2] <= sabit <= s[3]:
            t = DIS_DUVAR if s[6] == "dis" else IC_DUVAR
            if s[1] < 1e-6:
                noktalar += [0.0, DIS_DUVAR]
            elif s[1] > W - 1e-6:
                noktalar += [W - DIS_DUVAR, W]
            else:
                noktalar += [s[1] - t / 2, s[1] + t / 2]
        if eksen == "y" and s[0] == "y" and s[2] <= sabit <= s[3]:
            if s[1] < 1e-6:
                noktalar += [0.0, DIS_DUVAR]
            elif s[1] > H - 1e-6:
                noktalar += [H - DIS_DUVAR, H]
            else:
                noktalar += [s[1] - IC_DUVAR / 2, s[1] + IC_DUVAR / 2]
    noktalar = sorted(set(round(v, 3) for v in noktalar))
    if eksen == "x":
        olcu_zinciri(c, noktalar, "x", ty(sabit), tx, True, boy=1.5)
    else:
        olcu_zinciri(c, noktalar, "y", tx(sabit), ty, True, boy=1.5)

KESITLER = {"A": ("x", 9.20), "B": ("y", 12.30)}

def kesit_isaretleri(c, tx, ty, s, pr):
    for ad, (e, v) in KESITLER.items():
        if e == "x":
            y0, y1 = ty(0) - pr["K"] * s - 4 - 12 - 17, ty(H) + pr["G"] * s + 4 + 12 + 18
            c.line(tx(v), y0, tx(v), y0 + 9, 0.6); c.line(tx(v), y1 - 9, tx(v), y1, 0.6)
            c.line(tx(v), y0 + 9, tx(v), y1 - 9, 0.1, dash="4,1.5,0.6,1.5")
            for yy in (y0, y1):
                c.poly([(tx(v), yy - 1.8), (tx(v) + 4.5, yy), (tx(v), yy + 1.8)], fill="#111", stroke="none")
                c.text(tx(v) - 1.8, yy + 1.2, ad, 3.6, "end", 700)
        else:
            x0, x1 = tx(0) - pr["B"] * s - 4 - 12 - 17, tx(W) + pr["D"] * s + 4 + 12 + 17
            c.line(x0, ty(v), x0 + 9, ty(v), 0.6); c.line(x1 - 9, ty(v), x1, ty(v), 0.6)
            c.line(x0 + 9, ty(v), x1 - 9, ty(v), 0.1, dash="4,1.5,0.6,1.5")
            for xx in (x0, x1):
                c.poly([(xx - 1.8, ty(v)), (xx, ty(v) - 4.5), (xx + 1.8, ty(v))], fill="#111", stroke="none")
                c.text(xx + 1.2, ty(v) + 4.2, ad, 3.6, "middle", 700)

PLAN_LEJANT = [("betonarme", "Betonarme kolon / perde"), ("duvar", "Duvar (gazbeton, 25 / 13,5 cm)"),
               ("yalitim", "Isı yalıtımı (taşyünü, 8 cm)"), ("korkuluk", "Cam korkuluk h=110 cm"),
               ("fayans", "Porselen / fayans kaplama"), ("tas", "Doğal taş (traverten)"),
               ("saft", "Tesisat şaftı"), ("kot", "Döşeme kotu (m)"), ("aks", "Aks balonu")]

def kat_plani_pafta(kat, no):
    ad = {"Bodrum": "BODRUM KAT PLANI", "Zemin": "ZEMİN KAT PLANI", "1. Kat": "1. KAT PLANI"}[kat]
    ox, oy = 62.0, 74.0
    icerik = plan_icerik(kat, ox, oy)
    c = Cizim()
    c.add(icerik)
    k, d = kat_ozeti()[kat]
    c.text(24, 279, "%s · Ö: 1/100" % ad, 3.8, weight=700, ls=0.3)
    c.text(24, 284, "Döşeme kotu %s · Net kullanım alanı %s m² · Brüt 300,00 m²"
           % (kot_yazi(KOT[kat]), f2(k).replace(".", ",")), 2.3, fill=GRI)
    olcek_cubugu(c, 230, 280, 10.0)
    notlar = PLAN_NOTLARI[kat]
    return pafta(no, ad, "1/100", c.svg(), notlar=notlar, lejant=PLAN_LEJANT)

def olcek_cubugu(c, x, y, s, n=5, adim=1.0):
    for i in range(n):
        c.rect(x + i * adim * s, y - 1.2, adim * s, 1.2, fill="#111" if i % 2 == 0 else "#fff", stroke="#111", sw=0.15)
        c.text(x + i * adim * s, y + 2.6, "%d" % (i * adim), 1.7, "middle")
    c.text(x + n * adim * s, y + 2.6, "%d m" % (n * adim), 1.7, "middle")

PLAN_NOTLARI = {
"Bodrum": [
 "Bodrum çevre duvarları 30 cm betonarme perdedir; dıştan 2 kat bitümlü membran + 5 cm XPS + drenaj levhası ve perde dibinde drenaj borusu uygulanır.",
 "Oyun salonu ve misafir odası gün ışığını batı ışıklıklarından, fitness salonu doğu ışıklığından alır. Işıklık tabanı −3.16, süzgeçli; üstü galvaniz ızgara + cam korkuluk.",
 "Misafir odası ışıklığında dikme kaçış merdiveni vardır (acil çıkış).",
 "Isı merkezi: yoğuşmalı hermetik kazan veya hava kaynaklı ısı pompası iç ünitesi; baca / hava kanalı tesisat şaftından çatıya çıkar. Kapı EI30.",
 "Sauna, soyunma ve penceresiz depolar mekanik havalandırmalıdır (şafta bağlı sessiz fan).",
],
"Zemin": [
 "Giriş kotu ±0.00 = tabii zemin +0.30. Garaj −0.17, teras −0.02; garajdan eve EI30, kendiliğinden kapanan kapı.",
 "Salon–yemek–mutfak açık plandır; güney cephesi kaldır-sür (lift & slide) doğrama ile teras ve pergolaya açılır.",
 "Misafir süiti (oda + banyo + hol) girişe yakın, aile bölümünden bağımsızdır; üst kattaki yatak 2 süitiyle aynı akstadır (ıslak hacimler üst üste).",
 "Servis girişi doğu yan bahçededir: araç yolu → servis kapısı → arka mutfak / kiler. Market alışverişi salondan geçmeden mutfağa ulaşır.",
 "Şömine bacası batı cephede dışa taşan taş kaplı kütledir; çatıdan 1,00 m yükselir.",
],
"1. Kat": [
 "Ebeveyn süiti: hol → giyinme odası → yatak odası ve banyo. Yatak odalarının tamamı hol/giyinme üzerinden girilir, her birinin kendi banyosu vardır.",
 "Balkonlar 1,50 m konsoldur (açık çıkma); ısı köprüsü kesici (Schöck Isokorb) ile döşemeye bağlanır.",
 "Giriş galerisi zemin kattan 1. kat tavanına kadar çift yüksekliktir; kuzey cephede tam boy sabit cam.",
 "Çatı arasına koridordaki katlanır merdivenli kapaktan çıkılır (yalıtımlı, 70×120).",
 "Pencere denizlikleri ≥ 90 cm; kapı boyu camlar yalnızca balkonlara açılır.",
],
}

# ================================================================== yazdır
def hepsi():
    import cizim_ek as ek
    return ek.CIZIMLER

if __name__ == "__main__":
    import sys
    hedef = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cizimler")
    os.makedirs(hedef, exist_ok=True)
    for kat, no, dosya in (("Bodrum", "A-02", "02-bodrum-kat"), ("Zemin", "A-03", "03-zemin-kat"),
                           ("1. Kat", "A-04", "04-birinci-kat")):
        svg = kat_plani_pafta(kat, no)
        with open(os.path.join(hedef, dosya + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        print(dosya, len(svg))
