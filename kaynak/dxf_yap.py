# -*- coding: utf-8 -*-
"""Durunday Villa — DXF / DWG çizim seti (mimara teslim).

Paftalar SVG ile aynı kodla üretilir; kayıt modülü (kayit.py) her öğeyi katman ve görünüş
bilgisiyle yakalar. Model alanında her çizim 1:1 gerçek ölçüdedir (birim cm); her pafta A3
layout'ta antet + ölçekli viewport olarak durur. Katman şeması: katmanlar.py (ÇŞB CADD).

`python3 dxf_yap.py`            → ../cad/dxf/*.dxf + ../cad/dwg/*.dwg + ../cad/KATMAN-LISTESI.csv
`python3 dxf_yap.py 03-zemin-kat` → yalnız o pafta (DWG'siz, hızlı deneme)
"""
import os, sys, math, subprocess, inspect, csv
from collections import Counter

import ezdxf
from ezdxf.enums import TextEntityAlignment

import kayit
from kayit import katmanli
import ciz, paftalar
import katmanlar

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEDEF = os.path.join(KOK, "cad")
ODA = os.path.expanduser("~/opt/oda/AppRun")
PW, PH = ciz.PW, ciz.PH
BIRIM = 100.0                         # model birimi: cm (1 m = 100)

# ================================================================== çizim fonksiyonlarına katman bağlama
FONK = {
    ciz: {"aks_balonu": "AKS-BALON", "_kot_isareti": "KOT", "_korkuluk": "KORKULUK",
          "_plan_dis_elemanlar": "DIS-MEKAN", "_isiklik_plan": "ISIKLIK", "mahal_etiketi": "MAHAL-YAZI",
          "kapi_svg": "KAPI", "_kasa": "KAPI-KASA", "pencere_plan": "PENCERE", "merdiven_plan": "MERDIVEN",
          "asansor_plan": "ASANSOR", "kesit_isaretleri": "KESIT-HATTI", "plan_olculeri": "AKS",
          "ic_zincir": "OLCU-IC", "olcek_cubugu": "PAFTA-YAZI", "_kuzey_oku": "KUZEY",
          "_lejant_sembol": "LEJANT", "pafta": "ANTET"},
    paftalar: {"_zemin_toprak": "ZEMIN", "_kesit_dograma": "PENCERE", "_uzak_acikliklar": "GORUNEN",
               "_doseme": "DOSEME-KESIT", "_kiris": "BETONARME", "_kesit_dis": "DIS-MEKAN", "_cati_kesit": "CATI",
               "_merdiven_gorunus": "MERDIVEN-GOR", "_gor_pencere": "PENCERE", "_gor_kapi": "KAPI",
               "_gor_cikmalar": "CEPHE", "_agac": "PEYZAJ", "_insan": "INSAN", "dograma_icerik": "TABLO"},
}
VITRIFIYE = {"wc", "lavabo", "dus", "kuvet", "kuvet_serbest", "buzdolabi", "tezgah", "ada", "kazan", "boyler",
             "depo_tank", "filtre", "camasir", "ada_dolap"}
GORUNUMLER = {  # fonksiyon → (tür, x orijin argümanı, y orijin argümanı)
    (ciz, "plan_icerik"): ("plan", "ox", "oy"), (paftalar, "vaziyet_icerik"): ("plan", "ox", "oy"),
    (paftalar, "cati_icerik"): ("plan", "ox", "oy"), (paftalar, "kesit_icerik"): ("dusey", "ox", "oz"),
    (paftalar, "gorunus_icerik"): ("dusey", "ox", "oz"), (paftalar, "sistem_kesiti_icerik"): ("dusey", "ox", "oz"),
    (paftalar, "merdiven_icerik"): ("dusey", "ox", "oy"),
}


def _degistir(ad, yeni):
    for m in (ciz, paftalar):
        if hasattr(m, ad):
            setattr(m, ad, yeni)


def _gorunumlu(f, tur, ax, ay):
    sig = inspect.signature(f)
    def ic(*a, **k):
        b = sig.bind(*a, **k); b.apply_defaults()
        ad = f.__name__ + ":" + ":".join(str(v) for n, v in b.arguments.items() if n not in (ax, ay, "s"))
        with kayit.gorunum(ad, b.arguments[ax], b.arguments[ay], b.arguments.get("s", 1.0), tur):
            return f(*a, **k)
    ic._kancali = True
    return ic


_KANCALI = [False]


def kancala():
    if _KANCALI[0]:
        return
    _KANCALI[0] = True
    for mod, tablo in FONK.items():
        for ad, anahtar in tablo.items():
            _degistir(ad, katmanli(anahtar)(getattr(mod, ad)))
    # ölçü zinciri → gerçek DIMENSION
    oz0 = ciz.olcu_zinciri
    def olcu(c, noktalar, eksen, sabit, tx, yazi_ust=True, boy=1.8, uzatma=None):
        n = sorted(set(round(v, 4) for v in noktalar))
        if len(n) >= 2:
            k = "OLCU-IC" if kayit.aktif_katman() == "OLCU-IC" else "OLCU"
            with kayit.katman(k):
                kayit.kaydet("olcu", eksen=eksen, pts=[tx(v) for v in n], sabit=sabit, boy=boy, ust=yazi_ust,
                             uzatma=uzatma)
        with kayit.bastir():
            return oz0(c, noktalar, eksen, sabit, tx, yazi_ust, boy, uzatma)
    _degistir("olcu_zinciri", olcu)
    # doğrama etiketi: kapı / pencere
    ek0 = ciz._etiket_kutu
    def etiket(c, X, Y, kod, kapi=False):
        with kayit.katman("KAPI-POZ" if kapi else "PENCERE-POZ"):
            return ek0(c, X, Y, kod, kapi)
    _degistir("_etiket_kutu", etiket)
    # mobilya: tefriş / vitrifiye
    mb0 = ciz.mobilya_svg
    def mobilya(c, o, tx, ty, s):
        with kayit.katman("VITRIFIYE" if o[0] in VITRIFIYE else "MOBILYA"):
            return mb0(c, o, tx, ty, s)
    _degistir("mobilya_svg", mobilya)
    for (mod, ad), (tur, ax, ay) in GORUNUMLER.items():
        _degistir(ad, _gorunumlu(getattr(mod, ad), tur, ax, ay))


# ================================================================== DXF belgesi
ISO_TIP = {  # ISO 128 çizgi tipleri (kâğıt mm; LTSCALE ile kalınlığa göre küçültülür)
    "ACAD_ISO02W100": ("ISO kesik __ __ __", [15.0, 12.0, -3.0]),
    "ACAD_ISO03W100": ("ISO kesik boşluk __    __", [30.0, 12.0, -18.0]),
    "ACAD_ISO04W100": ("ISO uzun kesik nokta ____ . ____", [30.0, 24.0, -3.0, 0.0, -3.0]),
    "ACAD_ISO07W100": ("ISO nokta . . . .", [3.0, 0.0, -3.0]),
}


def yeni_belge():
    doc = ezdxf.new("R2018", setup=["styles"], units=ezdxf.units.CM)
    h = doc.header
    h["$INSUNITS"] = 5; h["$MEASUREMENT"] = 1; h["$LUNITS"] = 2
    h["$LTSCALE"] = 0.25; h["$PSLTSCALE"] = 1; h["$LWDISPLAY"] = 1
    h["$TEXTSTYLE"] = "YAZI"
    for ad, (acik, pat) in ISO_TIP.items():
        if ad not in doc.linetypes:
            doc.linetypes.add(ad, pattern=pat, description=acik)
    doc.styles.add("YAZI", font="arialn.ttf")
    doc.styles.add("YAZI-KALIN", font="arialnb.ttf")
    ds = doc.dimstyles.new("MIMARI")
    for k, v in dict(dimtxsty="YAZI", dimtxt=1.8 * 0.72, dimtsz=0.8, dimexe=1.2, dimexo=0.0, dimgap=0.5,
                     dimdec=0, dimtad=1, dimtih=0, dimtoh=0, dimtix=0, dimtofl=1, dimclrd=256, dimclre=256,
                     dimclrt=256, dimlunit=2, dimzin=8, dimrnd=0).items():
        ds.dxf.set(k, v)
    return doc


def katman_hazirla(doc, ad):
    if ad in doc.layers:
        return ad
    renk, tip, kal, acik, kay, yaz = katmanlar.ozellik(ad)
    ly = doc.layers.add(ad, color=renk, linetype=tip, lineweight=int(round(kal * 100)))
    ly.description = acik
    if not yaz:
        ly.dxf.plot = 0
    return ad


def dimstil(doc, s):
    ad = "MIMARI-1-%d" % round(1000 / s)
    if ad not in doc.dimstyles:
        ds = doc.dimstyles.duplicate_entry("MIMARI", ad)
        ds.dxf.dimscale = BIRIM / s
    return ad


# ================================================================== koordinat
class Esle:
    """Kâğıt (SVG mm, y aşağı) → model (cm, y yukarı)."""
    def __init__(self, gor, ofs=(0.0, 0.0)):
        self.g, self.ofs = gor, ofs
        self.k = BIRIM / gor["s"]
    def __call__(self, p):
        g = self.g
        return ((p[0] - g["ox"]) * self.k + self.ofs[0], -(p[1] - g["oy"]) * self.k + self.ofs[1])


def kagit(p):
    return (p[0], PH - p[1])
kagit.k = 1.0

DESEN_DXF = {  # SVG deseni → (DXF deseni, kâğıttaki ölçek (mm), açı)
    "p-duvar": ("ANSI31", 0.6, 0), "p-saft": ("ANSI31", 0.5, 0), "p-toprak": ("EARTH", 0.5, 0),
    "p-yalitim": ("INSUL", 0.05, 0), "p-beton": ("AR-CONC", 0.03, 0), "p-fayans": ("NET", 0.8, 0),
    "p-tas": ("NET", 1.6, 0), "p-dis-tas": ("NET", 1.6, 0), "p-izgara": ("NET", 0.3, 0),
    "p-kiremit": ("LINE", 0.8, 0), "p-kiremit-g": ("AR-B816", 0.012, 0), "p-sille": ("AR-B816", 0.035, 0),
    "p-ahsap": ("LINE", 0.4, 90), "p-su": ("AR-SAND", 0.05, 0),
}


def _koyu(renk):
    if not renk or renk == "none":
        return False
    if not renk.startswith("#"):
        return renk not in ("white",)
    h = renk.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255 < 0.35


def _noktalar(r):
    if r["tur"] == "yazi":                     # yazı kutusu (yaklaşık) — viewport sınırı için
        x, y = r["xy"]; w = len(r["t"]) * r["size"] * 0.5; h = r["size"]
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[r["anchor"]]
        if abs(r.get("rot", 0)) > 45:
            return [(x - h, y - w), (x + h * 0.2, y + w)]
        return [(x0, y - h), (x0 + w, y + h * 0.2)]
    if r["tur"] == "olcu":
        return [(p, r["sabit"]) for p in r["pts"]] if r["eksen"] == "x" else [(r["sabit"], p) for p in r["pts"]]
    if "pts" in r:
        return r["pts"]
    return [r["xy"]] if "xy" in r else []


# ================================================================== maske (SVG'de beyaz/opak dolgunun örttüğü öğeler)
MASKE_KAYNAK = {"ZEMIN", "ISIKLIK", "PENCERE", "BINA-IZ", "DIS-MEKAN"}
MASKE_HEDEF = {"ZEMIN", "YALITIM", "CIM", "CEPHE-TAS", "CEPHE-SIVA", "CEPHE-SUBASMAN", "CEPHE-SILME", "CEPHE-AHSAP",
               "BACA", None}
DOGRAMA = {"PENCERE", "KAPI", "GORUNEN"}


def _dik_kutu(q):
    if len(q) != 4:
        return None
    xs = sorted({round(p[0], 4) for p in q}); ys = sorted({round(p[1], 4) for p in q})
    if len(xs) != 2 or len(ys) != 2:
        return None
    return (xs[0], ys[0], xs[1], ys[1])


def _cikar(a, b):
    """a − b (eksene paralel dikdörtgenler) → dikdörtgen listesi."""
    ax0, ay0, ax1, ay1 = a; bx0, by0, bx1, by1 = b
    if bx0 >= ax1 or bx1 <= ax0 or by0 >= ay1 or by1 <= ay0:
        return [a]
    out = []
    if by0 > ay0: out.append((ax0, ay0, ax1, by0))
    if by1 < ay1: out.append((ax0, by1, ax1, ay1))
    y0, y1 = max(ay0, by0), min(ay1, by1)
    if bx0 > ax0: out.append((ax0, y0, bx0, y1))
    if bx1 < ax1: out.append((bx1, y0, ax1, y1))
    return [r for r in out if r[2] - r[0] > 1e-3 and r[3] - r[1] > 1e-3]


def _cizgi_kes(p, q, b):
    """Eksene paralel doğru parçasının b dikdörtgeni dışında kalan parçaları."""
    (x0, y0), (x1, y1) = p, q
    bx0, by0, bx1, by1 = b
    if abs(y0 - y1) < 1e-6 and by0 < y0 < by1:
        a, c = sorted((x0, x1)); parc = [(a, min(c, bx0)), (max(a, bx1), c)]
        return [((u, y0), (v, y0)) for u, v in parc if v - u > 1e-3]
    if abs(x0 - x1) < 1e-6 and bx0 < x0 < bx1:
        a, c = sorted((y0, y1)); parc = [(a, min(c, by0)), (max(a, by1), c)]
        return [((x0, u), (x0, v)) for u, v in parc if v - u > 1e-3]
    return [(p, q)]


def _kutu_pts(k):
    return [(k[0], k[1]), (k[2], k[1]), (k[2], k[3]), (k[0], k[3])]


def maskele(kayitlar):
    out = []
    for r in kayitlar:
        g = r["gor"]
        gorunus = g is not None and g["ad"].startswith("gorunus_icerik")
        maske = None
        if r["tur"] == "dolgu" and g is not None:
            beyaz = r["renk"] in ("#fff", "#ffffff", "white")
            if (beyaz and r["katman"] in MASKE_KAYNAK) or (gorunus and r["katman"] in DOGRAMA):
                maske = _dik_kutu(r["pts"])
        if maske:
            yeni = []
            for o in out:
                if o["gor"] is not g or o["katman"] not in MASKE_HEDEF or (o["katman"] is None and o["tur"] != "tarama"):
                    yeni.append(o); continue
                if o["tur"] in ("tarama", "dolgu"):
                    k = _dik_kutu(o["pts"])
                    if k is None:
                        yeni.append(o); continue
                    for p in _cikar(k, maske):
                        yeni.append(dict(o, pts=_kutu_pts(p)))
                elif o["tur"] == "cizgi" and len(o["pts"]) == 2:
                    for p, q in _cizgi_kes(o["pts"][0], o["pts"][1], maske):
                        yeni.append(dict(o, pts=[p, q]))
                else:
                    yeni.append(o)
            out = yeni
        # görünüşte doğrama dolguları kontur olarak kalır
        if gorunus and r["tur"] == "dolgu" and r["katman"] in DOGRAMA and r["renk"] not in ("#fff", "#ffffff"):
            r = dict(r, tur="cizgi", pts=r["pts"] + [r["pts"][0]], sw=0.13, dash=None)
        out.append(r)
    return out


# ================================================================== pafta → DXF
def ascii_ad(t):
    return t.translate(str.maketrans("ÇĞİÖŞÜçğıöşüÂâ–/", "CGIOSUcgiosuAa--"))


def pafta_yaz(doc, no, ad, kayitlar, ofs_y, sayim, tek):
    msp = doc.modelspace()
    lay_ad = ascii_ad("%s %s" % (no, ad))
    if tek:
        doc.layouts.rename("Layout1", lay_ad); lay = doc.layouts.get(lay_ad)
    else:
        lay = doc.layouts.new(lay_ad)
    lay.page_setup(size=(PW, PH), margins=(0, 0, 0, 0), units="mm", scale=(1, 1))
    # görünüşler: model alanında yan yana
    gorler = []
    for r in kayitlar:
        if r["gor"] is not None and all(r["gor"]["ad"] != g["ad"] for g in gorler):
            gorler.append(r["gor"])
    esle, kutu, x_ofs = {}, {}, 0.0
    for g in gorler:
        e0 = Esle(g)
        kp = [p for r in kayitlar if r["gor"] and r["gor"]["ad"] == g["ad"] for p in _noktalar(r)]
        mp = [e0(p) for p in kp]
        mx0 = min(p[0] for p in mp); mx1 = max(p[0] for p in mp)
        dx = 0.0 if not esle else x_ofs - mx0
        if g["tur"] == "plan" and g["ad"].startswith(("plan_icerik", "cati_icerik")):
            dy = ciz.H * BIRIM                         # bina güneybatı köşesi (0,0)
        else:
            dy = 0.0
        esle[g["ad"]] = Esle(g, (dx, dy + ofs_y))
        x_ofs = dx + mx1 + 2000.0
        kutu[g["ad"]] = (min(q[0] for q in kp), min(q[1] for q in kp), max(q[0] for q in kp), max(q[1] for q in kp))
    kayitlar = maskele(kayitlar)
    for r in kayitlar:
        g = r["gor"]
        if g is None:
            _oge(doc, lay, r, kagit, None, sayim)
        else:
            _oge(doc, msp, r, esle[g["ad"]], g, sayim)
    # viewport'lar (yazdırılmayan katmanda)
    vly = katman_hazirla(doc, katmanlar.ad("GOST-VPORT"))
    for gad, (x0, y0, x1, y1) in kutu.items():
        m = 3.0
        x0, y0 = max(x0 - m, 10.5), max(y0 - m, 10.5)
        x1, y1 = min(x1 + m, ciz.ANTET_X - 0.5), min(y1 + m, PH - 10.5)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        E = esle[gad]
        vp = lay.add_viewport(center=kagit((cx, cy)), size=(x1 - x0, y1 - y0), view_center_point=E((cx, cy)),
                              view_height=(y1 - y0) * E.k)
        vp.dxf.layer = vly


def _oge(doc, hedef, r, E, g, sayim):
    ly = katman_hazirla(doc, katmanlar.cozumle(r, g))
    tur, k = r["tur"], E.k
    at = {"layer": ly}
    if tur == "tarama":
        desen, olc, aci = DESEN_DXF.get(r["desen"], (None, 0, 0))
        if desen is None:
            return
        h = hedef.add_hatch(dxfattribs=at)
        h.set_pattern_fill(desen, scale=olc * k, angle=aci)
        h.paths.add_polyline_path([E(p) for p in r["pts"]], is_closed=True)
    elif tur == "dolgu":
        if not _koyu(r["renk"]):
            return
        h = hedef.add_hatch(dxfattribs=at)
        h.set_solid_fill(color=256)
        h.paths.add_polyline_path([E(p) for p in r["pts"]], is_closed=True)
    elif tur == "cizgi":
        if r.get("renk") in ("#fff", "#ffffff", "white"):
            return
        if r.get("dash") and doc.layers.get(ly).dxf.linetype == "Continuous" and "IZDUSUM" not in ly:
            at["linetype"] = "ACAD_ISO02W100"
        pts = [E(p) for p in r["pts"]]
        if len(pts) == 2:
            if math.dist(*pts) < 1e-6:
                return
            hedef.add_line(pts[0], pts[1], dxfattribs=at)
        else:
            kap = math.dist(pts[0], pts[-1]) < 1e-6
            hedef.add_lwpolyline(pts[:-1] if kap else pts, close=kap, dxfattribs=at)
    elif tur == "daire":
        cizgi = r.get("renk") not in (None, "none")
        dolu = _koyu(r.get("fill"))
        if not (cizgi or dolu):
            return
        c, rr = E(r["xy"]), r["r"] * k
        if cizgi:
            hedef.add_circle(c, rr, dxfattribs=at)
        if dolu:
            h = hedef.add_hatch(dxfattribs=at); h.set_solid_fill(color=256)
            h.paths.add_edge_path().add_arc(c, rr, 0, 360)
    elif tur == "yazi":
        t = r["t"].replace("−", "-").replace("±", "%%p")
        al = {"start": TextEntityAlignment.LEFT, "middle": TextEntityAlignment.CENTER,
              "end": TextEntityAlignment.RIGHT}[r["anchor"]]
        at["style"] = "YAZI-KALIN" if r["kalin"] else "YAZI"
        ent = hedef.add_text(t, height=r["size"] * 0.72 * k, rotation=-r.get("rot", 0), dxfattribs=at)
        ent.set_placement(E(r["xy"]), align=al)
    elif tur == "olcu":
        ds = dimstil(doc, g["s"])
        pts = r["pts"]
        for a, b in zip(pts, pts[1:]):
            if abs(b - a) / g["s"] < 0.05:
                continue
            if r["eksen"] == "x":
                ua = r["uzatma"] if r["uzatma"] is not None else r["sabit"]
                p1, p2, base, ang = E((a, ua)), E((b, ua)), E((a, r["sabit"])), 0
            else:
                ua = r["uzatma"] if r["uzatma"] is not None else r["sabit"]
                p1, p2, base, ang = E((ua, a)), E((ua, b)), E((r["sabit"], a)), 90
            d = hedef.add_linear_dim(base=base, p1=p1, p2=p2, angle=ang, dimstyle=ds, dxfattribs=at)
            d.render()
            sayim[ly] += 1
        return
    else:
        return
    sayim[ly] += 1


def katman_csv(katman_sayim):
    yol = os.path.join(HEDEF, "KATMAN-LISTESI.csv")
    with open(yol, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Katman", "Renk (ACI)", "Çizgi tipi", "Kalınlık 1/100 (mm)", "Yazdırılır", "İçerik", "Dayanak",
                    "Öğe sayısı (tüm set)"])
        for ad in sorted(katman_sayim):
            renk, tip, kal, acik, kay, yaz = katmanlar.ozellik(ad)
            w.writerow([ad, renk, tip, ("%.2f" % kal).replace(".", ","), "evet" if yaz else "hayır", acik, kay,
                        katman_sayim[ad]])
    return yol


def uret(sadece=None):
    kancala()
    os.makedirs(os.path.join(HEDEF, "dxf"), exist_ok=True)
    toplu = yeni_belge()
    ofs_y, toplam = 0.0, Counter()
    for dosya, ad, no, olcek, fn in paftalar.PAFTALAR:
        if sadece and dosya not in sadece:
            continue
        kayit.basla(); fn(); kayitlar = kayit.bitir()
        doc = yeni_belge(); sayim = Counter()
        pafta_yaz(doc, no, ad, kayitlar, 0.0, sayim, tek=True)
        yol = os.path.join(HEDEF, "dxf", "DV-%s-%s.dxf" % (no, dosya[3:]))
        doc.saveas(yol)
        pafta_yaz(toplu, no, ad, kayitlar, ofs_y, Counter(), tek=False)
        ofs_y -= 5000.0
        toplam.update(sayim)
        print("%-5s %-28s %6d öğe  %3d katman  %s" % (no, ad, sum(sayim.values()), len(sayim), os.path.basename(yol)))
    if not sadece:
        if "Layout1" in toplu.layouts:
            toplu.layouts.delete("Layout1")
        toplu.saveas(os.path.join(HEDEF, "dxf", "DV-TUM-PAFTALAR.dxf"))
        print("katman listesi:", katman_csv(toplam))
    return toplam


def dwg_cevir():
    if not os.path.exists(ODA):
        print("ODA File Converter yok — DWG atlandı (kurulum: README)"); return False
    kaynak, hedef = os.path.join(HEDEF, "dxf"), os.path.join(HEDEF, "dwg")
    os.makedirs(hedef, exist_ok=True)
    for f in os.listdir(hedef):
        os.remove(os.path.join(hedef, f))
    env = dict(os.environ); env.setdefault("DISPLAY", ":0")
    subprocess.run([ODA, kaynak, hedef, "ACAD2018", "DWG", "0", "1", "*.DXF"], env=env,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1800)
    n = len([f for f in os.listdir(hedef) if f.lower().endswith(".dwg")])
    print("DWG: %d dosya → %s" % (n, hedef))
    return n > 0


if __name__ == "__main__":
    sec = sys.argv[1:] or None
    uret(sec)
    if not sec:
        dwg_cevir()
