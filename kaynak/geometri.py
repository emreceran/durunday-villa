# -*- coding: utf-8 -*-
"""veri.py geometrisinden türetilen yapı elemanları: duvar parçaları, açıklıklar, kapı kanatları.
Çizim (ciz.py), kontrol (kontrol.py) ve 3B model (render_3b.py) aynı fonksiyonları kullanır."""
from veri import (KATLAR, ACIK, KAPILAR, PENCERELER, BINA, DIS_DUVAR, IC_DUVAR, ic_sinir)

EPS = 1e-6
W, H = BINA["en"], BINA["boy"]

def oda_bul(kat, x, y):
    """Noktadaki mahal kodu; bina dışı 'DIS'."""
    if x < -EPS or x > W + EPS or y < -EPS or y > H + EPS:
        return "DIS"
    for m in KATLAR[kat]:
        for r in m["r"]:
            if r[0] - EPS <= x <= r[2] + EPS and r[1] - EPS <= y <= r[3] + EPS:
                return m["kod"]
    return "DIS"

def mahal_sozluk(kat):
    return {m["kod"]: m for m in KATLAR[kat]}

def acik_tur(kat, a, b):
    for p, q, tur in ACIK.get(kat, []):
        if {p, q} == {a, b}:
            return tur
    return None

def _koordinatlar(kat):
    xs, ys = {0.0, W}, {0.0, H}
    for m in KATLAR[kat]:
        for r in m["r"]:
            xs.update([r[0], r[2]]); ys.update([r[1], r[3]])
    return sorted(xs), sorted(ys)

def ham_kenarlar(kat):
    """Temel kenar parçaları: (eksen, sabit, a, b, sol/üst mahal, sağ/alt mahal, tür)
    tür: dis | ic | korkuluk ; aynı mahal veya 'acik' birleşimi dahil edilmez."""
    xs, ys = _koordinatlar(kat)
    out = []
    d = 1e-3
    for c in xs:
        for a, b in zip(ys, ys[1:]):
            ym = (a + b) / 2
            p, q = oda_bul(kat, c - d, ym), oda_bul(kat, c + d, ym)
            if p == q:
                continue
            tur = _tur(kat, p, q)
            if tur:
                out.append(("x", c, a, b, p, q, tur))
    for c in ys:
        for a, b in zip(xs, xs[1:]):
            xm = (a + b) / 2
            p, q = oda_bul(kat, xm, c - d), oda_bul(kat, xm, c + d)
            if p == q:
                continue
            tur = _tur(kat, p, q)
            if tur:
                out.append(("y", c, a, b, p, q, tur))
    return out

def _tur(kat, p, q):
    if "DIS" in (p, q):
        return "dis"
    t = acik_tur(kat, p, q)
    if t == "acik":
        return None
    if t == "korkuluk":
        return "korkuluk"
    return "ic"

def _birlestir(parcalar):
    """Aynı eksen/sabit/tür ardışık parçaları birleştirir."""
    parcalar = sorted(parcalar, key=lambda s: (s[0], s[1], s[6], s[2]))
    out = []
    for s in parcalar:
        if out and out[-1][0] == s[0] and abs(out[-1][1] - s[1]) < EPS and out[-1][6] == s[6] \
                and abs(out[-1][3] - s[2]) < EPS:
            o = out[-1]
            out[-1] = (o[0], o[1], o[2], s[3], o[4], o[5], o[6])
        else:
            out.append(s)
    return out

def aciklik_listesi(kat):
    """Duvarı kesen tüm açıklıklar: (eksen, sabit, a, b, tür, kayıt)"""
    out = []
    for k in KAPILAR.get(kat, []):
        out.append((k[0], k[1], k[2], k[3], "kapi", k))
    for p in PENCERELER.get(kat, []):
        cephe, a, b = p[0], p[1], p[2]
        eksen, sabit = {"K": ("y", 0.0), "G": ("y", H), "B": ("x", 0.0), "D": ("x", W)}[cephe]
        out.append((eksen, sabit, a, b, "pencere", p))
    return out

def duvar_parcalari(kat):
    """Çizilecek duvar parçaları (açıklıklar düşülmüş): (eksen, sabit, a, b, tür, uc_a_acik, uc_b_acik)"""
    kenarlar = _birlestir(ham_kenarlar(kat))
    acikliklar = aciklik_listesi(kat)
    out = []
    for e, c, a, b, p, q, tur in kenarlar:
        kesitler = sorted([(o[2], o[3]) for o in acikliklar
                           if o[0] == e and abs(o[1] - c) < EPS and o[2] < b - EPS and o[3] > a + EPS])
        bas, bas_acik = a, False
        for oa, ob in kesitler:
            if oa > bas + EPS:
                out.append((e, c, bas, oa, tur, bas_acik, True))
            bas, bas_acik = ob, True
        if b > bas + EPS:
            out.append((e, c, bas, b, tur, bas_acik, False))
    return out

def duvar_dikdortgeni(parca):
    """Duvar parçasının plan dikdörtgeni (x0, y0, x1, y1)."""
    e, c, a, b, tur, acik_a, acik_b = parca
    if tur == "dis":
        t0, t1 = (0, DIS_DUVAR) if c < EPS else (-DIS_DUVAR, 0)
    elif tur == "korkuluk":
        t0, t1 = -0.03, 0.03
    else:
        t0, t1 = -IC_DUVAR / 2, IC_DUVAR / 2
    ua = 0 if acik_a or tur == "dis" else IC_DUVAR / 2
    ub = 0 if acik_b or tur == "dis" else IC_DUVAR / 2
    if tur == "korkuluk":
        ua = ub = 0
    if e == "x":
        return (c + t0, a - ua, c + t1, b + ub)
    return (a - ua, c + t0, b + ub, c + t1)

def duvar_kalinligi(kat, e, c, a, b):
    """Bir açıklığın bulunduğu duvarın kalınlığı ve iki yüzünün sabit koordinatı."""
    if (e == "x" and (c < EPS or c > W - EPS)) or (e == "y" and (c < EPS or c > H - EPS)):
        if c < EPS:
            return DIS_DUVAR, 0.0, DIS_DUVAR
        return DIS_DUVAR, c - DIS_DUVAR, c
    return IC_DUVAR, c - IC_DUVAR / 2, c + IC_DUVAR / 2

def kapi_taraflari(kat, kapi):
    """Kapının iki yanındaki mahaller (sol/üst, sağ/alt)."""
    e, c, a, b = kapi[0], kapi[1], kapi[2], kapi[3]
    m = (a + b) / 2
    d = 0.2
    if e == "x":
        return oda_bul(kat, c - d, m), oda_bul(kat, c + d, m)
    return oda_bul(kat, m, c - d), oda_bul(kat, m, c + d)

def kanat_geometrisi(kat, kapi):
    """Kanatlı kapı için: (menteşe noktası, açık kanat ucu, kapalı kanat ucu, yön işareti, kanat boyu)
    Kanat, 'açıldığı mahal' tarafındaki duvar yüzünden başlar."""
    e, c, a, b, tip, hedef, mentese = kapi
    t, f0, f1 = duvar_kalinligi(kat, e, c, a, b)
    sol, sag = kapi_taraflari(kat, kapi)
    if hedef == sol:
        yon, yuz = -1, f0
    else:
        yon, yuz = +1, f1
    w = b - a
    if e == "x":
        hy = a if mentese == "a" else b
        diger = b if mentese == "a" else a
        return (yuz, hy), (yuz + yon * w, hy), (yuz, diger), yon, w
    hx = a if mentese == "a" else b
    diger = b if mentese == "a" else a
    return (hx, yuz), (hx, yuz + yon * w), (diger, yuz), yon, w

def kanat_alani(kat, kapi):
    """Kanadın süpürdüğü kare (x0,y0,x1,y1)."""
    (hx, hy), (ox, oy), (kx, ky), yon, w = kanat_geometrisi(kat, kapi)
    xs = [hx, ox, kx]; ys = [hy, oy, ky]
    return (min(xs), min(ys), max(xs), max(ys))

def mahal_ic_sinirlari(kat, kod):
    return [ic_sinir(r) for r in mahal_sozluk(kat)[kod]["r"]]
