# -*- coding: utf-8 -*-
"""Durunday Villa — çizim setinin geri kalanı: kapak, vaziyet, çatı, kesitler, görünüşler,
sistem kesiti, merdiven detayı, doğrama listesi. Hepsi veri.py'den üretilir.

`python3 paftalar.py` → ../cizimler/*.svg (tam set)"""
import os, math, base64
from veri import (KATLAR, KATLAR_SIRA, KAPILAR, PENCERELER, BINA, BINA_KONUM, PARSEL, DIS_DUVAR, IC_DUVAR,
                  YALITIM, KOT, TABII_ZEMIN, KAT_YUKSEKLIK, NET_TAVAN, DOSEME, GARAJ_KOT, CATI, AKS_X, AKS_Y,
                  KOLON, MERDIVEN, merdiven_kollari, BALKONLAR, GIRIS_SACAGI, PERGOLA, TERAS, ISIKLIKLAR, BACA,
                  HAVUZ, net_alan, kat_ozeti)
from geometri import oda_bul, mahal_sozluk, ham_kenarlar
import ciz
from ciz import (Cizim, pafta, olcu_zinciri, aks_balonu, kot_yazi, _kot_isareti, f2, cm, esc, _sar,
                 KALIN, ORTA, INCE, COK_INCE, GRI, CAM, KESITLER, olcek_cubugu, _kuzey_oku)

W, H = BINA["en"], BINA["boy"]
KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAC = CATI["sacak"]
EGIM = CATI["egim"]
Z_SACAK = 6.45                     # saçak ucu (alın tahtası üstü)
Z_ALIN_ALT = 6.10                  # saçak altı lambri
Z_MAHYA = Z_SACAK + EGIM * (H / 2 + SAC)
MAHYA_X = (-SAC + (H / 2 + SAC), W + SAC - (H / 2 + SAC))
Z_BACA = 8.40
Z_BALKON = KOT["1. Kat"] - 0.02
Z_SACAK_GIRIS = (2.75, 2.95)
Z_PERGOLA = 2.85

def cati_z(x, y):
    return Z_SACAK + EGIM * min(x + SAC, W + SAC - x, y + SAC, H + SAC - y)

from dograma import pencere_tipleri, kapi_tipleri, KAPI_YUKSEKLIK, KAPI_AD

# ================================================================== yardımcı: kesit ve görünüş dönüşümü
class Tuval:
    def __init__(self, ox, oz, s=10.0, ters=False, genislik=0.0):
        self.ox, self.oz, self.s, self.ters, self.gen = ox, oz, s, ters, genislik
    def X(self, u):
        return self.ox + (self.gen - u if self.ters else u) * self.s
    def Z(self, z):
        return self.oz - z * self.s

def _zemin_toprak(c, T, u0, u1, z_ust, z_alt):
    c.rect(T.X(min(u0, u1)) if not T.ters else T.X(max(u0, u1)), T.Z(z_ust), abs(u1 - u0) * T.s, (z_ust - z_alt) * T.s,
           fill="url(#p-toprak)")

def _dik(c, T, u0, u1, z0, z1, **kw):
    xa, xb = sorted((T.X(u0), T.X(u1)))
    c.rect(xa, T.Z(z1), xb - xa, (z1 - z0) * T.s, **kw)

# ================================================================== KESİT
def kesit_icerik(ad, ox, oz, s=10.0):
    e, cut = KESITLER[ad]
    c = Cizim()
    T = Tuval(ox, oz, s)
    L = H if e == "x" else W                     # kesit boyunca bina genişliği
    # ------------- zemin (toprak) ve dış düzenleme
    sol_uc, sag_uc = (-3.2, L + 5.0) if e == "x" else (-2.6, L + 2.6)
    z_alt = -4.3
    c.rect(T.X(sol_uc), T.Z(TABII_ZEMIN), (sag_uc - sol_uc) * s, (TABII_ZEMIN - z_alt) * s, fill="url(#p-toprak)")
    c.rect(T.X(-0.02), T.Z(0.0), (L + 0.04) * s, (0.0 - z_alt) * s, fill="#fff")    # bina içi toprak yok
    # ışıklıklar (B–B)
    if e == "y":
        for i in ISIKLIKLAR:
            if i["a"] < cut < i["b"]:
                d = i["derinlik"]
                u0, u1 = (-d, 0) if i["cephe"] == "B" else (L, L + d)
                c.rect(T.X(u0), T.Z(TABII_ZEMIN + 0.05), d * s, (TABII_ZEMIN + 0.05 + 3.36) * s, fill="#fff")
                duvar_u = u0 - 0.25 if i["cephe"] == "B" else u1
                _dik(c, T, duvar_u, duvar_u + 0.25, -3.36, TABII_ZEMIN + 0.10, fill="#111")
                _dik(c, T, u0, u1, -3.36, -3.16, fill="#6b7280")
                gx = (u0, u1)
                c.line(T.X(gx[0]), T.Z(TABII_ZEMIN + 0.05), T.X(gx[1]), T.Z(TABII_ZEMIN + 0.05), 0.5, "#374151", dash="0.6,0.4")
                ku = duvar_u + 0.12
                c.line(T.X(ku), T.Z(TABII_ZEMIN + 0.10), T.X(ku), T.Z(TABII_ZEMIN + 1.20), 0.9, "#7dd3fc")
                c.text(T.X((u0 + u1) / 2), T.Z(-2.0), "ışıklık", 1.6, "middle", fill=GRI, rot=-90)
    # zemin çizgisi
    c.line(T.X(sol_uc), T.Z(TABII_ZEMIN), T.X(0), T.Z(TABII_ZEMIN), 0.6)
    c.line(T.X(L), T.Z(TABII_ZEMIN), T.X(sag_uc), T.Z(TABII_ZEMIN), 0.6)
    # ------------- temel (radye) + grobeton
    _dik(c, T, -0.5, L + 0.5, -3.16 - 0.60, -3.16, fill="#111")
    _dik(c, T, -0.6, L + 0.6, -3.86 - 0.02, -3.76, fill="url(#p-beton)", stroke="#111", sw=0.15)
    # ------------- katlar
    for kat in KATLAR_SIRA:
        z0 = KOT[kat]
        ust = {"Bodrum": "Zemin", "Zemin": "1. Kat", "1. Kat": "Çatı"}[kat]
        z1 = KOT[ust]
        tavan = z1 - DOSEME if ust != "Çatı" else KOT["Çatı"] - 0.20
        soz = mahal_sozluk(kat)
        # mahal bantları
        bantlar = _bantlar(kat, e, cut, L)
        for u0, u1, kod in bantlar:
            m = soz[kod]
            if m["tip"] in ("saft",):
                continue
            # uzaktaki duvardaki kapılar / pencereler (görünen)
            _uzak_acikliklar(c, T, kat, kod, e, cut, u0, u1, z0)
            if m["tip"] != "bosluk" and u1 - u0 > 1.0:
                ad_s = _sar(m["ad"].upper(), max(8, int((u1 - u0) * 3.2)))
                for i, sat in enumerate(ad_s[:2]):
                    c.text(T.X((u0 + u1) / 2), T.Z(z0 + 1.05) + i * 2.3, sat, 1.7, "middle", 700, fill="#374151")
        # kesilen duvarlar
        for sgm in ham_kenarlar(kat):
            if sgm[0] == e or not (sgm[2] < cut < sgm[3]):
                continue
            u = sgm[1]
            tur = sgm[6]
            if tur == "korkuluk":
                c.line(T.X(u), T.Z(z0), T.X(u), T.Z(z0 + 1.10), 0.9, "#7dd3fc")
                c.line(T.X(u) - 0.3, T.Z(z0 + 1.10), T.X(u) + 0.3, T.Z(z0 + 1.10), 0.4)
                continue
            if tur == "dis":
                ua, ub = (0, DIS_DUVAR) if u < 1e-6 else (L - DIS_DUVAR, L)
            else:
                ua, ub = u - IC_DUVAR / 2, u + IC_DUVAR / 2
            acik = _kesitteki_aciklik(kat, e, cut, u)
            beton = kat == "Bodrum" and tur == "dis"
            parcalar = [(z0, tavan)]
            if acik:
                a0, a1, tip = acik
                parcalar = [(z0, z0 + a0), (z0 + a1, tavan)] if a0 > 0 else [(z0 + a1, tavan)]
                _kesit_dograma(c, T, ua, ub, z0 + a0, z0 + a1, tip, tur == "dis")
            for p0, p1 in parcalar:
                if p1 - p0 < 0.01:
                    continue
                if beton:
                    _dik(c, T, ua, ub, p0, p1, fill="#111")
                else:
                    _dik(c, T, ua, ub, p0, p1, fill="url(#p-duvar)", stroke="#111", sw=KALIN)
                    if tur == "dis" and kat != "Bodrum":
                        yu = (ua, ua + YALITIM) if u < 1e-6 else (ub - YALITIM, ub)
                        _dik(c, T, yu[0], yu[1], p0, p1, fill="url(#p-yalitim)", stroke="#111", sw=0.15)
            if beton:
                yu = (-0.10, 0) if u < 1e-6 else (L, L + 0.10)
                _dik(c, T, yu[0], yu[1], -3.16, TABII_ZEMIN, fill="url(#p-yalitim)", stroke="#111", sw=0.15)
        # döşeme (bu katın tavanı)
        _doseme(c, T, ust, e, cut, L)
    # zemin kat döşemesi (bodrum tavanı çizildi); bodrum taban döşemesi (radye üstü)
    _dik(c, T, DIS_DUVAR, L - DIS_DUVAR, KOT["Bodrum"] - 0.10, KOT["Bodrum"], fill="#d1d5db", stroke="#111", sw=0.15)
    # ------------- merdiven görünüşü (A–A)
    if e == "x":
        _merdiven_gorunus(c, T, cut)
    # ------------- dış elemanlar
    _kesit_dis(c, T, e, cut, L)
    # ------------- çatı
    _cati_kesit(c, T, e, cut, L)
    # ------------- kotlar ve ölçüler
    sag = sag_uc + 0.6
    for v, ad2 in ((Z_MAHYA, "mahya"), (KOT["Çatı"], "çatı döşemesi"), (KOT["1. Kat"], "1. kat"), (0.0, "zemin kat"),
                   (TABII_ZEMIN, "tabii zemin"), (KOT["Bodrum"], "bodrum"), (-3.76, "temel altı")):
        c.line(T.X(sag_uc), T.Z(v), T.X(sag) + 1, T.Z(v), 0.1, "#6b7280", dash="1,0.6")
        _kot_isareti(c, T.X(sag) + 3, T.Z(v), kot_yazi(v), 1.9)
        c.text(T.X(sag) + 13, T.Z(v) - 0.4, ad2, 1.6, fill=GRI)
    zler = [KOT["Bodrum"], 0.0, KOT["1. Kat"], KOT["Çatı"], Z_MAHYA]
    olcu_zinciri(c, zler, "y", T.X(sol_uc) - 6, lambda z: T.Z(z), True)
    olcu_zinciri(c, [TABII_ZEMIN, KOT["Çatı"]], "y", T.X(sol_uc) - 12, lambda z: T.Z(z), True)
    c.text(T.X(sol_uc) - 14.5, T.Z(3.0), "Hmax = 6,50 m (tabii zeminden çatı döşemesine)", 1.6, "middle", fill="#b45309", rot=-90)
    # yön etiketi
    sol_ad, sag_ad = ("KUZEY (yol)", "GÜNEY (bahçe)") if e == "x" else ("BATI", "DOĞU")
    c.text(T.X(sol_uc), T.Z(z_alt) + 5, sol_ad, 1.8, fill=GRI)
    c.text(T.X(sag_uc), T.Z(z_alt) + 5, sag_ad, 1.8, "end", fill=GRI)
    return c.svg()

def _bantlar(kat, e, cut, L):
    """Kesit doğrusu boyunca (u0, u1, mahal) bantları."""
    kesim = sorted({0.0, L} | {q for m in KATLAR[kat] for r in m["r"]
                                 for q in ((r[1], r[3]) if e == "x" else (r[0], r[2]))})
    out = []
    for a, b in zip(kesim, kesim[1:]):
        m = (a + b) / 2
        kod = oda_bul(kat, cut, m) if e == "x" else oda_bul(kat, m, cut)
        if out and out[-1][2] == kod:
            out[-1] = (out[-1][0], b, kod)
        else:
            out.append((a, b, kod))
    return out

def _kesitteki_aciklik(kat, e, cut, u):
    """Kesilen duvarda kesit noktasında açıklık varsa (alt, üst, tip)."""
    for k in KAPILAR[kat]:
        if k[0] != e and abs(k[1] - u) < 1e-6 and k[2] < cut < k[3]:
            return (0.0, KAPI_YUKSEKLIK[k[4]], k[4])
    for p in PENCERELER[kat]:
        if e == "x" and p[0] in ("K", "G") and abs((0.0 if p[0] == "K" else H) - u) < 1e-6 and p[1] < cut < p[2]:
            return (p[4], p[5], "P" + p[3])
        if e == "y" and p[0] in ("B", "D") and abs((0.0 if p[0] == "B" else W) - u) < 1e-6 and p[1] < cut < p[2]:
            return (p[4], p[5], "P" + p[3])
    return None

def _kesit_dograma(c, T, ua, ub, za, zb, tip, dis):
    if tip.startswith("P"):
        m0 = ua + (0.10 if ua < 1 else 0.15)
        _dik(c, T, m0, m0 + 0.08, za, zb, fill=CAM, stroke="#111", sw=0.25)
        c.line(T.X(ua) - 0.4, T.Z(za), T.X(ub) + 0.4, T.Z(za), 0.3)      # denizlik
        _dik(c, T, ua, ub, zb, zb + 0.02, fill="#111")
    elif tip in ("gecis",):
        pass
    else:
        c.line(T.X((ua + ub) / 2), T.Z(za), T.X((ua + ub) / 2), T.Z(zb), 0.25)

def _uzak_acikliklar(c, T, kat, kod, e, cut, u0, u1, z0):
    """Bakış yönündeki ilk duvarın kapı/pencerelerini ince çizgiyle göster."""
    m = mahal_sozluk(kat)[kod]
    for r in m["r"]:
        if e == "x":
            if not (r[0] <= cut <= r[2]):
                continue
            uzak, ek = r[2], "x"
            ra, rb = max(r[1], u0), min(r[3], u1)
        else:
            if not (r[1] <= cut <= r[3]):
                continue
            uzak, ek = r[1], "y"
            ra, rb = max(r[0], u0), min(r[2], u1)
        for k in KAPILAR[kat]:
            if k[0] == ek and abs(k[1] - uzak) < 1e-6 and k[2] < rb and k[3] > ra and k[4] not in ("kapak",):
                h = KAPI_YUKSEKLIK[k[4]]
                _dik(c, T, max(k[2], ra), min(k[3], rb), z0, z0 + h, fill="none", stroke="#6b7280", sw=0.15)
                if k[4] in ("kapi", "yangin", "servis"):
                    c.line(T.X(max(k[2], ra) + 0.08), T.Z(z0 + 1.05), T.X(max(k[2], ra) + 0.2), T.Z(z0 + 1.05), 0.2, "#6b7280")
        cephe = {("x", W): "D", ("y", 0.0): "K"}.get((ek, uzak))
        if cephe:
            for p in PENCERELER[kat]:
                if p[0] == cephe and p[1] < rb and p[2] > ra:
                    _dik(c, T, max(p[1], ra), min(p[2], rb), z0 + p[4], z0 + p[5], fill="#eef6ff", stroke="#6b7280", sw=0.15)

def _doseme(c, T, ust, e, cut, L):
    """ust katın döşemesi (alttaki katın tavanı)."""
    z = KOT[ust]
    if ust == "Çatı":
        _dik(c, T, 0, L, z - 0.20, z, fill="#111")
        _dik(c, T, DIS_DUVAR, L - DIS_DUVAR, z, z + 0.14, fill="url(#p-yalitim)", stroke="#111", sw=0.15)
        _kiris(c, T, e, cut, z - 0.20, L)
        return
    bosluk = []
    kat = ust
    for u0, u1, kod in _bantlar(kat, e, cut, L):
        tip = mahal_sozluk(kat)[kod]["tip"]
        if tip == "bosluk":
            bosluk.append((u0, u1))
        if tip == "merdiven":
            x0, y0, x1, y1 = MERDIVEN["kutu"]
            if e == "x":
                bosluk.append((4.435, 7.925))
            else:
                bosluk.append((x0 + 0.05, x1 - 0.075))
    parcalar = [(0.0, L)]
    for b0, b1 in bosluk:
        yeni = []
        for p0, p1 in parcalar:
            if b1 <= p0 or b0 >= p1:
                yeni.append((p0, p1)); continue
            if b0 > p0: yeni.append((p0, b0))
            if b1 < p1: yeni.append((b1, p1))
        parcalar = yeni
    for p0, p1 in parcalar:
        _dik(c, T, p0, p1, z - DOSEME, z - 0.10, fill="#111")
        _dik(c, T, p0 + (DIS_DUVAR if p0 < 1e-6 else 0), p1 - (DIS_DUVAR if p1 > L - 1e-6 else 0), z - 0.10, z,
             fill="#e5e7eb", stroke="#111", sw=0.12)
    _kiris(c, T, e, cut, z - DOSEME, L)

def _kiris(c, T, e, cut, z_alt, L):
    akslar = [v for _, v in (AKS_Y if e == "x" else AKS_X)]
    for v in akslar:
        u0 = min(max(v - 0.15, 0.0), L - 0.35)
        if v < 1e-6:
            u0 = 0.0
        _dik(c, T, u0, u0 + 0.30, z_alt - 0.30, z_alt, fill="#111")

def _kesit_dis(c, T, e, cut, L):
    # teras (güney) ve giriş (kuzey) — A–A ; teras kenarları — B–B
    if e == "x":
        g = GIRIS_SACAGI
        if g["x0"] <= cut <= g["x1"]:
            _dik(c, T, -g["derinlik"], 0, -0.12, -0.02, fill="#d6d3d1", stroke="#111", sw=0.2)
            for i in range(2):
                _dik(c, T, -g["derinlik"] - 0.32 * (i + 1), -g["derinlik"] - 0.32 * i, TABII_ZEMIN, -0.02 - 0.14 * (i + 1) + 0.14,
                     fill="#d6d3d1", stroke="#111", sw=0.2)
            _dik(c, T, -g["derinlik"], 0, Z_SACAK_GIRIS[0], Z_SACAK_GIRIS[1], fill="#111")
            _dik(c, T, -g["derinlik"], 0, Z_SACAK_GIRIS[1], Z_SACAK_GIRIS[1] + 0.10, fill="#7c9a5b", stroke="#111", sw=0.15)
            c.text(T.X(-g["derinlik"] / 2), T.Z(Z_SACAK_GIRIS[1] + 0.25), "giriş saçağı", 1.5, "middle", fill=GRI)
        t = TERAS
        if t["x0"] <= cut <= t["x1"]:
            _dik(c, T, L, t["y1"], TABII_ZEMIN - 0.25, -0.02, fill="url(#p-beton)", stroke="#111", sw=0.2)
            _dik(c, T, L, t["y1"], -0.06, -0.02, fill="#d6d3d1", stroke="#111", sw=0.15)
            c.text(T.X((L + t["y1"]) / 2), T.Z(0.25), "TERAS −0.02", 1.7, "middle", 700, fill="#374151")
        pg = PERGOLA
        if pg["x0"] <= cut <= pg["x1"]:
            _dik(c, T, L, pg["y1"], Z_PERGOLA - 0.2, Z_PERGOLA, fill="#4b5563")
            _dik(c, T, pg["y1"] - 0.15, pg["y1"], -0.02, Z_PERGOLA - 0.2, fill="#4b5563")
        for bk in BALKONLAR:
            if bk["x0"] <= cut <= bk["x1"]:
                _dik(c, T, L, L + bk["derinlik"], Z_BALKON - 0.18, Z_BALKON, fill="#111")
                c.line(T.X(L + bk["derinlik"] - 0.05), T.Z(Z_BALKON), T.X(L + bk["derinlik"] - 0.05), T.Z(Z_BALKON + 1.1), 0.9, "#7dd3fc")
    else:
        # baca (batı)
        a, b = BACA["a"], BACA["b"]
        if a <= cut <= b:
            _dik(c, T, -BACA["derinlik"], 0, 0, Z_BACA, fill="url(#p-duvar)", stroke="#111", sw=KALIN)
        else:
            _dik(c, T, -BACA["derinlik"], 0, TABII_ZEMIN, Z_BACA, fill="none", stroke="#6b7280", sw=0.15)

def _cati_kesit(c, T, e, cut, L):
    n = 80
    us = [-SAC + i * (L + 2 * SAC) / n for i in range(n + 1)]
    zf = (lambda u: cati_z(cut, u)) if e == "x" else (lambda u: cati_z(u, cut))
    ust = [(T.X(u), T.Z(zf(u))) for u in us]
    alt = [(T.X(u), T.Z(zf(u) - 0.26)) for u in reversed(us)]
    # uzaktaki çatı silueti (görünen)
    if e == "y":
        sil = [(-SAC, Z_SACAK), (MAHYA_X[0], Z_MAHYA), (MAHYA_X[1], Z_MAHYA), (L + SAC, Z_SACAK)]
        c.poly([(T.X(u), T.Z(z)) for u, z in sil], fill="url(#p-kiremit)", stroke="#6b7280", sw=0.2, kapali=True)
    c.poly(ust + alt, fill="#c8a57a", stroke="#111", sw=0.4)
    c.poly(ust, stroke="#111", sw=0.6, kapali=False)
    # alın tahtası ve saçak altı
    for u in (-SAC, L + SAC):
        uu = u if u < 0 else u - 0.04
        _dik(c, T, uu, uu + 0.04, Z_ALIN_ALT, Z_SACAK, fill="#374151")
        c.circle(T.X(u - 0.08 if u < 0 else u + 0.08), T.Z(Z_SACAK - 0.12), 0.9, fill="#fff", stroke="#111", sw=0.25)
    for u0, u1 in ((-SAC, 0.0), (L, L + SAC)):
        _dik(c, T, u0, u1, Z_ALIN_ALT - 0.02, Z_ALIN_ALT, fill="#c89b6d", stroke="#111", sw=0.12)
    # dikmeler ve mahya kirişi
    orta = L / 2
    for u in (orta - 3.0, orta, orta + 3.0):
        z_ust = zf(u) - 0.26
        if z_ust > KOT["Çatı"] + 0.3:
            _dik(c, T, u - 0.06, u + 0.06, KOT["Çatı"] + 0.14, z_ust, fill="#e7d3b4", stroke="#111", sw=0.15)
    c.text(T.X(orta), T.Z(KOT["Çatı"] + 0.75), "ÇATI ARASI (kullanılmaz, havalandırmalı)", 1.6, "middle", fill=GRI)
    # etiket
    c.text(T.X(orta + 2.4), T.Z(zf(orta + 2.4)) - 2.0, "antrasit kil kiremit · %%%d" % round(EGIM * 100), 1.6, "start", fill="#111")

def _merdiven_gorunus(c, T, cut):
    b = MERDIVEN["basamak"]
    for kat in ("Bodrum", "Zemin"):
        mk = merdiven_kollari(kat)
        z0 = KOT[kat]
        k1, k2 = mk["kollar"]
        r = mk["riht"]
        # batı kol (ön planda)
        pts = [(k1[2], z0)]
        for i in range(k1[4]):
            y = k1[2] + i * b
            pts += [(y, z0 + (i + 1) * r), (min(y + b, k1[3]), z0 + (i + 1) * r)]
        zs = z0 + k1[4] * r
        pts += [(MERDIVEN["sahanlik"][1], zs)]
        c.poly([(T.X(u), T.Z(z)) for u, z in pts], stroke="#374151", sw=0.25, kapali=False)
        c.line(T.X(k1[2]), T.Z(z0 - 0.18), T.X(k1[3]), T.Z(zs - 0.18), 0.2, "#374151")
        _dik(c, T, MERDIVEN["sahanlik"][0], MERDIVEN["sahanlik"][1], zs - 0.18, zs, fill="none", stroke="#374151", sw=0.2)
        # doğu kol (arkada, üst kısmı görünür)
        pts2 = [(k2[2], zs)]
        for i in range(k2[4]):
            y = k2[2] - i * b
            pts2 += [(y, zs + (i + 1) * r), (max(y - b, k2[3]), zs + (i + 1) * r)]
        c.poly([(T.X(u), T.Z(z)) for u, z in pts2], stroke="#9ca3af", sw=0.18, kapali=False)
        # korkuluk (cam, küpeşte)
        c.line(T.X(k1[2]), T.Z(z0 + 1.0), T.X(k1[3]), T.Z(zs + 1.0), 0.3, "#0ea5e9")

# ================================================================== GÖRÜNÜŞ
CEPHE_BILGI = {  # ad, bakış, genişlik, ters
    "K": ("KUZEY GÖRÜNÜŞÜ (GİRİŞ CEPHESİ)", W, True),
    "G": ("GÜNEY GÖRÜNÜŞÜ (BAHÇE CEPHESİ)", W, False),
    "D": ("DOĞU GÖRÜNÜŞÜ", H, True),
    "B": ("BATI GÖRÜNÜŞÜ", H, False),
}

def gorunus_icerik(cephe, ox, oz, s=10.0):
    ad, L, ters = CEPHE_BILGI[cephe]
    c = Cizim()
    T = Tuval(ox, oz, s, ters, L)
    sol, sag = -2.2, L + 2.2
    # arka plan ağaçları
    for u, r, h in ((-1.4, 1.9, 6.3), (L + 1.4, 2.1, 7.0)):
        _agac(c, T, u, r, h)
    # ------------- kütle: zemin kat taş, 1. kat sıva
    _dik(c, T, 0, L, TABII_ZEMIN, 0.0, fill="#d9cdb4", stroke="#111", sw=0.3)            # subasman
    _dik(c, T, 0, L, 0.0, KOT["1. Kat"] - 0.30, fill="url(#p-sille)", stroke="#111", sw=0.35)
    _dik(c, T, 0, L, KOT["1. Kat"] - 0.30, KOT["1. Kat"], fill="#e5e7eb", stroke="#111", sw=0.35)   # kat silmesi
    _dik(c, T, 0, L, KOT["1. Kat"], Z_ALIN_ALT, fill="#fbfbf9", stroke="#111", sw=0.35)
    # saçak gölgesi
    _dik(c, T, 0, L, Z_ALIN_ALT - 0.45, Z_ALIN_ALT, fill="#000", op="0.08")
    # ------------- açıklıklar
    for kat in ("Zemin", "1. Kat"):
        z0 = KOT[kat]
        for p in PENCERELER[kat]:
            if p[0] == cephe:
                _gor_pencere(c, T, p, z0)
        for k in KAPILAR[kat]:
            if k[4] in ("giris", "garaj", "servis") and _kapi_cephesi(k) == cephe:
                _gor_kapi(c, T, k, z0)
    # ------------- baca
    a, b = BACA["a"], BACA["b"]
    if cephe == "B":
        _dik(c, T, a, b, TABII_ZEMIN, Z_BACA, fill="url(#p-sille)", stroke="#111", sw=0.35)
        _dik(c, T, a - 0.08, b + 0.08, Z_BACA, Z_BACA + 0.12, fill="#374151")
    elif cephe in ("K", "G"):
        _dik(c, T, -BACA["derinlik"], 0, TABII_ZEMIN, Z_BACA, fill="url(#p-sille)", stroke="#111", sw=0.35)
        _dik(c, T, -BACA["derinlik"] - 0.08, 0.08, Z_BACA, Z_BACA + 0.12, fill="#374151")
    # ------------- çatı
    if cephe in ("K", "G"):
        poly = [(-SAC, Z_SACAK), (MAHYA_X[0], Z_MAHYA), (MAHYA_X[1], Z_MAHYA), (L + SAC, Z_SACAK)]
    else:
        poly = [(-SAC, Z_SACAK), (L / 2, Z_MAHYA), (L + SAC, Z_SACAK)]
    c.poly([(T.X(u), T.Z(z)) for u, z in poly], fill="url(#p-kiremit-g)", stroke="#111", sw=0.4)
    _dik(c, T, -SAC, L + SAC, Z_ALIN_ALT, Z_SACAK, fill="#374151", stroke="#111", sw=0.3)          # alın + oluk
    _dik(c, T, -SAC, L + SAC, Z_SACAK - 0.05, Z_SACAK + 0.05, fill="#1f2937")
    if cephe == "K" or cephe == "G":
        # baca çatının önünde
        pass
    if cephe == "D":
        # batıdaki baca çatının arkasından yükselir
        siluet = Z_SACAK + EGIM * min(a + SAC, H + SAC - b, H / 2 + SAC)
        _dik(c, T, a, b, siluet, Z_BACA, fill="url(#p-sille)", stroke="#111", sw=0.3)
        _dik(c, T, a - 0.08, b + 0.08, Z_BACA, Z_BACA + 0.12, fill="#374151")
    # yağmur inişleri
    for u in (0.12, L - 0.12):
        _dik(c, T, u - 0.05, u + 0.05, TABII_ZEMIN, Z_ALIN_ALT, fill="#374151")
    # ------------- çıkmalar
    _gor_cikmalar(c, T, cephe, L)
    # ------------- zemin
    c.rect(T.X(sol) if not ters else T.X(sag), T.Z(TABII_ZEMIN), (sag - sol) * s, 3.0, fill="url(#p-toprak)")
    c.line(T.X(sol), T.Z(TABII_ZEMIN), T.X(sag), T.Z(TABII_ZEMIN), 0.7)
    # insan (ölçek)
    _insan(c, T, L * 0.62 if cephe in ("K", "G") else L * 0.35, TABII_ZEMIN if cephe != "G" else -0.02)
    # ------------- kotlar
    kx = max(T.X(sol), T.X(sag)) + 2
    for v in (Z_MAHYA, Z_SACAK, KOT["Çatı"], KOT["1. Kat"], 0.0, TABII_ZEMIN):
        c.line(max(T.X(0), T.X(L)) + 1, T.Z(v), kx, T.Z(v), 0.1, "#9ca3af", dash="1,0.6")
        _kot_isareti(c, kx + 2, T.Z(v), kot_yazi(v), 1.8)
    # malzeme notları
    notlar = [(Z_MAHYA - 0.9, "antrasit kil kiremit, %30 eğim"),
              (5.0, "1. kat: beyaz ince silikon sıva (8 cm taşyünü mantolama)"),
              (3.05, "kat silmesi: beyaz prekast / GRC"),
              (1.4, "zemin kat: doğal taş kaplama (Sille taşı, bej)"),
              (-0.15, "subasman: yontma taş")]
    lx = min(T.X(sol), T.X(sag)) - 2
    for z, t in notlar:
        c.line(lx, T.Z(z), min(T.X(0), T.X(L)) + 4, T.Z(z), 0.1, "#6b7280")
        c.circle(min(T.X(0), T.X(L)) + 4, T.Z(z), 0.35, fill="#111", stroke="none")
        c.text(lx - 1, T.Z(z) + 0.6, t, 1.7, "end", fill="#1f2937")
    # yön ekleri
    kenar = {"K": ("DOĞU", "BATI"), "G": ("BATI", "DOĞU"), "D": ("GÜNEY", "KUZEY"), "B": ("KUZEY", "GÜNEY")}[cephe]
    c.text(T.X(0) if not ters else T.X(L), T.Z(TABII_ZEMIN) + 5.5, kenar[0], 1.6, "start", fill=GRI)
    c.text(T.X(L) if not ters else T.X(0), T.Z(TABII_ZEMIN) + 5.5, kenar[1], 1.6, "end", fill=GRI)
    c.text(min(T.X(sol), T.X(sag)), T.Z(Z_MAHYA) - 4, ad + " · Ö: 1/100", 3.0, weight=700, ls=0.2)
    return c.svg()

def _kapi_cephesi(k):
    if k[0] == "y":
        return "K" if k[1] < 1e-6 else ("G" if k[1] > H - 1e-6 else None)
    return "B" if k[1] < 1e-6 else ("D" if k[1] > W - 1e-6 else None)

def _gor_pencere(c, T, p, z0):
    a, b, tip, d, l = p[1], p[2], p[3], p[4], p[5]
    if tip == "I":
        return
    za, zb = z0 + d, z0 + l
    _dik(c, T, a - 0.03, b + 0.03, za - 0.05, zb + 0.03, fill="#1f2937")          # kasa (antrasit)
    _dik(c, T, a + 0.03, b - 0.03, za + 0.02, zb - 0.04, fill="#cfe1f2")
    # yansıma
    xa, xb = sorted((T.X(a), T.X(b)))
    w = xb - xa
    for f in (0.15, 0.55):
        c.line(xa + w * f, T.Z(zb - 0.15), xa + w * f + min(w * 0.25, 4), T.Z(za + 0.3), 0.25, "#ffffff", op="0.8")
    # kayıtlar / kanatlar
    L = b - a
    n = 1
    if tip == "S":
        n = 3 if L > 4.5 else 2
    elif tip == "P" and L > 1.6:
        n = 2 if L < 3.0 else 3
    elif tip == "F" and L > 1.6:
        n = 2
    for i in range(1, n):
        u = a + i * L / n
        _dik(c, T, u - 0.03, u + 0.03, za, zb, fill="#1f2937")
    if tip == "F" and zb - za > 2.0:
        _dik(c, T, a, b, za + 2.10, za + 2.15, fill="#1f2937")
    # denizlik (taş)
    if tip in ("P", "Y"):
        _dik(c, T, a - 0.05, b + 0.05, za - 0.08, za - 0.03, fill="#e7e5e4", stroke="#111", sw=0.15)
    # güneş kırıcı / panjur kutusu (yatak odaları ve güney-batı)
    if tip in ("P", "S") and z0 > 1:
        _dik(c, T, a - 0.03, b + 0.03, zb + 0.03, zb + 0.20, fill="#374151")

def _gor_kapi(c, T, k, z0):
    a, b, tip = k[2], k[3], k[4]
    h = KAPI_YUKSEKLIK[tip]
    if tip == "giris":
        _dik(c, T, a - 0.05, b + 0.05, z0, z0 + h + 0.05, fill="#1f2937")
        _dik(c, T, a + 0.02, b - 0.02, z0, z0 + h, fill="url(#p-ahsap)")
        _dik(c, T, a + 0.85, a + 0.88, z0 + 0.6, z0 + 1.7, fill="#d1d5db")
    elif tip == "garaj":
        _dik(c, T, a - 0.05, b + 0.05, z0 - 0.17, z0 + h + 0.05, fill="#1f2937")
        _dik(c, T, a, b, GARAJ_KOT, z0 + h, fill="#6b7280")
        n = 5
        for i in range(1, n):
            z = GARAJ_KOT + i * (h - GARAJ_KOT) / n
            c.line(T.X(a), T.Z(z), T.X(b), T.Z(z), 0.2, "#374151")
    else:
        _dik(c, T, a - 0.04, b + 0.04, z0, z0 + h + 0.04, fill="#1f2937")
        _dik(c, T, a + 0.03, b - 0.03, z0, z0 + h - 0.02, fill="#4b5563")

def _gor_cikmalar(c, T, cephe, L):
    g = GIRIS_SACAGI
    if cephe == "K":
        _dik(c, T, g["x0"], g["x1"], Z_SACAK_GIRIS[0], Z_SACAK_GIRIS[1], fill="#f3f4f6", stroke="#111", sw=0.35)
        _dik(c, T, g["x0"], g["x1"], Z_SACAK_GIRIS[0] - 0.02, Z_SACAK_GIRIS[0], fill="#c89b6d")
        for i in range(2):
            _dik(c, T, g["x0"] - 0.2, g["x1"] + 0.2, TABII_ZEMIN + 0.14 * i, TABII_ZEMIN + 0.14 * (i + 1),
                 fill="#e7e5e4", stroke="#111", sw=0.2)
        # ahşap kaplama giriş nişi çerçevesi
        _dik(c, T, g["x0"] + 0.05, g["x0"] + 0.45, 0.0, Z_SACAK_GIRIS[0], fill="url(#p-ahsap)", stroke="#111", sw=0.2)
        # araç yolu
        c.text(T.X(17.0), T.Z(TABII_ZEMIN) + 2.8, "garaj · araç yolu −0.20", 1.6, "middle", fill=GRI)
    if cephe == "G":
        for bk in BALKONLAR:
            _dik(c, T, bk["x0"], bk["x1"], Z_BALKON - 0.20, Z_BALKON, fill="#f3f4f6", stroke="#111", sw=0.35)
            _dik(c, T, bk["x0"] + 0.03, bk["x1"] - 0.03, Z_BALKON, Z_BALKON + 1.10, fill="#dbeafe", stroke="#475569", sw=0.2, op="0.75")
            _dik(c, T, bk["x0"], bk["x1"], Z_BALKON - 0.45, Z_BALKON - 0.20, fill="#000", op="0.07")
        pg = PERGOLA
        _dik(c, T, pg["x0"], pg["x1"], Z_PERGOLA - 0.22, Z_PERGOLA, fill="#4b5563", stroke="#111", sw=0.3)
        for px in (pg["x0"] + 0.15, pg["x1"] - 0.30):
            _dik(c, T, px, px + 0.15, -0.02, Z_PERGOLA - 0.22, fill="#4b5563")
        for i in range(24):
            u = pg["x0"] + 0.3 + i * (pg["x1"] - pg["x0"] - 0.6) / 23
            c.line(T.X(u), T.Z(Z_PERGOLA - 0.2), T.X(u), T.Z(Z_PERGOLA), 0.15, "#9ca3af")
        _dik(c, T, TERAS["x0"] - 0.4, TERAS["x1"] + 0.4, TABII_ZEMIN, -0.02, fill="#e7e5e4", stroke="#111", sw=0.2)
    if cephe in ("D", "B"):
        # profilden görülen çıkmalar: kuzeyde giriş saçağı yalnız doğu/batıdan bakınca görünür
        yon = 1
        _dik(c, T, -g["derinlik"], 0, Z_SACAK_GIRIS[0], Z_SACAK_GIRIS[1], fill="#f3f4f6", stroke="#111", sw=0.3)
        for bk in BALKONLAR[:1]:
            _dik(c, T, L, L + bk["derinlik"], Z_BALKON - 0.20, Z_BALKON, fill="#f3f4f6", stroke="#111", sw=0.35)
            _dik(c, T, L, L + bk["derinlik"], Z_BALKON, Z_BALKON + 1.10, fill="#dbeafe", stroke="#475569", sw=0.2, op="0.75")
        pg = PERGOLA
        if cephe in ("D", "B"):
            _dik(c, T, L, pg["y1"], Z_PERGOLA - 0.22, Z_PERGOLA, fill="#4b5563", stroke="#111", sw=0.3)
            _dik(c, T, pg["y1"] - 0.3, pg["y1"] - 0.15, -0.02, Z_PERGOLA - 0.22, fill="#4b5563")
        _dik(c, T, L, TERAS["y1"], TABII_ZEMIN, -0.02, fill="#e7e5e4", stroke="#111", sw=0.2)
        for i in ISIKLIKLAR:
            if i["cephe"] == cephe:
                _dik(c, T, i["a"], i["b"], TABII_ZEMIN + 0.05, TABII_ZEMIN + 1.15, fill="#dbeafe", stroke="#475569", sw=0.2, op="0.7")
                c.text(T.X((i["a"] + i["b"]) / 2), T.Z(TABII_ZEMIN) + 2.6, "ışıklık korkuluğu", 1.4, "middle", fill=GRI)

def _agac(c, T, u, r, h):
    x = T.X(u)
    c.line(x, T.Z(TABII_ZEMIN), x, T.Z(h - r), 0.5, "#9ca3af")
    c.circle(x, T.Z(h - r * 0.8), r * T.s, fill="#f3f4f6", stroke="#d1d5db", sw=0.25)

def _insan(c, T, u, z):
    x, y = T.X(u), T.Z(z)
    s = T.s
    c.circle(x, y - 1.62 * s, 0.11 * s, fill="#9ca3af", stroke="none")
    c.path("M%.2f %.2f l%.2f %.2f l%.2f %.2f l%.2f %.2f l%.2f %.2f z" % (
        x - 0.2 * s, y - 1.45 * s, 0.4 * s, 0, 0.05 * s, 0.75 * s, -0.12 * s, 0.7 * s, -0.26 * s, 0),
        fill="#9ca3af", stroke="none")

# ================================================================== VAZİYET (1/200)
def vaziyet_icerik(ox, oy, s=5.0):
    c = Cizim()
    bx, by = BINA_KONUM
    X = lambda x: ox + x * s
    Y = lambda y: oy + y * s
    PE, PB = PARSEL["en"], PARSEL["boy"]
    # yol
    c.rect(X(-6), Y(-9), (PE + 12) * s, 7 * s, fill="#e5e7eb")
    c.rect(X(-6), Y(-2), (PE + 12) * s, 2 * s, fill="#f3f4f6", stroke="#9ca3af", sw=0.15)
    c.line(X(-6), Y(-5.5), X(PE + 6), Y(-5.5), 0.3, "#fff", dash="3,2")
    c.text(X(PE / 2), Y(-6.2), "İMAR YOLU (10,00 m)", 2.4, "middle", 700, fill="#4b5563")
    c.text(X(PE / 2), Y(-0.7), "tretuvar", 1.6, "middle", fill=GRI)
    # komşular
    for x0, x1, ad in ((-6, 0, "KOMŞU PARSEL"), (PE, PE + 6, "KOMŞU PARSEL")):
        c.rect(X(x0), Y(0), (x1 - x0) * s, PB * s, fill="#fafafa")
        c.text(X((x0 + x1) / 2), Y(PB / 2), ad, 1.8, "middle", fill=GRI, rot=-90)
    # bahçe (çim)
    c.rect(X(0), Y(0), PE * s, PB * s, fill="url(#p-cim)")
    # bahçe duvarı
    c.rect(X(0), Y(0), PE * s, PB * s, stroke="#111", sw=0.9)
    c.line(X(0), Y(0), X(PE), Y(0), 0.1, "#fff")
    # çekme mesafeleri
    c.rect(X(PARSEL["cekme_yan"]), Y(PARSEL["cekme_on"]), (PE - 2 * PARSEL["cekme_yan"]) * s,
           (PB - PARSEL["cekme_on"] - PARSEL["cekme_arka"]) * s, stroke="#b45309", sw=0.25, dash="2,1")
    c.text(X(PE - 3.3), Y(PB - 3.4), "yapı yaklaşma sınırı", 1.5, "end", fill="#b45309")
    # araç yolu ve kapılar
    c.rect(X(bx + 14.0), Y(0), 6.0 * s, (by) * s, fill="url(#p-dis-tas)", stroke="#111", sw=0.2)
    c.rect(X(bx + 7.9), Y(0), 4.5 * s, (by - GIRIS_SACAGI["derinlik"]) * s, fill="none")
    c.rect(X(bx + 8.55 - 0.3), Y(0), 1.7 * s, (by - GIRIS_SACAGI["derinlik"] - 0.64) * s, fill="url(#p-dis-tas)", stroke="#111", sw=0.2)
    c.line(X(bx + 14.0), Y(0), X(bx + 20.0), Y(0), 1.2, "#374151")
    c.text(X(bx + 17.0), Y(-2.6), "sürme bahçe kapısı 6,00 m", 1.5, "middle", fill="#374151")
    c.line(X(bx + 8.25), Y(0), X(bx + 9.95), Y(0), 1.2, "#374151")
    c.text(X(bx + 9.1), Y(-2.6), "yaya kapısı", 1.5, "middle", fill="#374151")
    c.text(X(bx + 17.0), Y(2.6), "ARAÇ YOLU", 1.7, "middle", 700)
    # servis yolu (doğu)
    c.rect(X(bx + W + 0.2), Y(by - 0.5), 1.2 * s, 8.3 * s, fill="url(#p-dis-tas)", stroke="#111", sw=0.15)
    # teras, pergola
    t = TERAS
    c.rect(X(bx + t["x0"]), Y(by + t["y0"]), (t["x1"] - t["x0"]) * s, (t["y1"] - t["y0"]) * s, fill="url(#p-dis-tas)", stroke="#111", sw=0.25)
    pg = PERGOLA
    c.rect(X(bx + pg["x0"]), Y(by + pg["y0"]), (pg["x1"] - pg["x0"]) * s, (pg["y1"] - pg["y0"]) * s,
           stroke="#111", sw=0.2, dash="1.2,0.7")
    # havuz
    hv = HAVUZ
    c.rect(X(bx + hv["x0"] - 1.2), Y(by + hv["y0"] - 1.2), (hv["x1"] - hv["x0"] + 2.4) * s, (hv["y1"] - hv["y0"] + 2.4) * s,
           fill="url(#p-dis-tas)", stroke="#111", sw=0.2)
    c.rect(X(bx + hv["x0"]), Y(by + hv["y0"]), (hv["x1"] - hv["x0"]) * s, (hv["y1"] - hv["y0"]) * s, fill="#dbeafe", stroke="#111", sw=0.35)
    c.rect(X(bx + hv["x0"]), Y(by + hv["y0"]), (hv["x1"] - hv["x0"]) * s, (hv["y1"] - hv["y0"]) * s, fill="url(#p-su)")
    c.text(X(bx + (hv["x0"] + hv["x1"]) / 2), Y(by + (hv["y0"] + hv["y1"]) / 2) + 0.8, "HAVUZ 10,00 × 4,00 m · h=1,40",
           1.8, "middle", 700, fill="#1e3a8a")
    # teras–havuz yolu
    c.rect(X(bx + 10.4), Y(by + t["y1"]), 1.2 * s, (hv["y0"] - 1.2 - t["y1"]) * s, fill="url(#p-dis-tas)", stroke="#111", sw=0.15)
    # ışıklıklar
    for i in ISIKLIKLAR:
        x0 = bx - i["derinlik"] if i["cephe"] == "B" else bx + W
        c.rect(X(x0), Y(by + i["a"]), i["derinlik"] * s, (i["b"] - i["a"]) * s, fill="url(#p-izgara)", stroke="#111", sw=0.25)
    # bina (çatı planı taslağı)
    c.rect(X(bx - SAC), Y(by - SAC), (W + 2 * SAC) * s, (H + 2 * SAC) * s, fill="#fff", stroke="#111", sw=0.2, dash="1.5,0.8")
    c.rect(X(bx), Y(by), W * s, H * s, fill="#e5e7eb", stroke="#111", sw=0.8)
    c.rect(X(bx), Y(by), W * s, H * s, fill="url(#p-duvar)", op="0.25")
    for (xa, ya), (xb_, yb_) in (((-SAC, -SAC), (MAHYA_X[0], H / 2)), ((W + SAC, -SAC), (MAHYA_X[1], H / 2)),
                                  ((-SAC, H + SAC), (MAHYA_X[0], H / 2)), ((W + SAC, H + SAC), (MAHYA_X[1], H / 2))):
        c.line(X(bx + xa), Y(by + ya), X(bx + xb_), Y(by + yb_), 0.15, "#6b7280")
    c.line(X(bx + MAHYA_X[0]), Y(by + H / 2), X(bx + MAHYA_X[1]), Y(by + H / 2), 0.3, "#374151")
    c.rect(X(bx - BACA["derinlik"]), Y(by + BACA["a"]), BACA["derinlik"] * s, (BACA["b"] - BACA["a"]) * s, fill="#9ca3af", stroke="#111", sw=0.2)
    c.text(X(bx + W / 2), Y(by + 4.6), "VİLLA", 3.2, "middle", 700)
    c.text(X(bx + W / 2), Y(by + 4.6) + 4.0, "Bodrum + Zemin + 1. Kat · kırma çatı", 1.8, "middle")
    c.text(X(bx + W / 2), Y(by + 4.6) + 7.0, "±0.00 = tabii zemin +0.30 · Hmax 6,50 m", 1.8, "middle")
    c.text(X(bx + W / 2), Y(by + 4.6) + 10.0, "oturum 20,00 × 15,00 = 300,00 m²", 1.8, "middle")
    # giriş oku
    c.line(X(bx + 9.1), Y(-1.2), X(bx + 9.1), Y(by - 0.3), 0.35, "#b45309")
    c.poly([(X(bx + 9.1) - 1, Y(by - 1.2)), (X(bx + 9.1) + 1, Y(by - 1.2)), (X(bx + 9.1), Y(by - 0.3))], fill="#b45309", stroke="none")
    # ağaçlar
    agaclar = [(1.6, 2.6, 1.4), (6.0, 2.6, 1.5), (4.6, 34.4, 2.6), (21.4, 34.6, 2.6), (3.6, 29.0, 1.6), (22.4, 29.0, 1.6)]
    for x, y, r in agaclar:
        c.circle(X(x), Y(y), r * s, fill="#eef5ea", stroke="#6b8f5b", sw=0.25)
        c.circle(X(x), Y(y), 0.25 * s, fill="#6b8f5b", stroke="none")
    for i in range(8):                    # selvi dizileri (yan sınırlar)
        for x in (0.7, PE - 0.7):
            y = 20.5 + i * 1.6
            if y > 27.2:
                continue
            c.circle(X(x), Y(y), 0.55 * s, fill="#dfeadb", stroke="#6b8f5b", sw=0.2)
    for x0, x1, y in ((0.5, 10.4, 0.6), ):
        c.rect(X(x0), Y(y), (x1 - x0) * s, 0.6 * s, fill="#dfeadb", stroke="#6b8f5b", sw=0.2, rx=1)
    # şezlonglar
    for i in range(3):
        x = bx + hv["x0"] + 1.5 + i * 1.3
        c.rect(X(x), Y(by + hv["y1"] + 0.2), 0.7 * s, 1.9 * s, fill="#fff", stroke="#6b7280", sw=0.15, rx=0.3)
    # kotlar
    for x, y, v in ((bx + 9.1, by - 2.4, TABII_ZEMIN), (bx + 17, 1.0, -0.20), (bx + 9.1, by + 2.0, 0.0),
                    (bx + 4, by + H + 2.0, TERAS["kot"]), (bx + 3, by + H + 6.0, TABII_ZEMIN), (2.0, -3.0, -0.45)):
        _kot_isareti(c, X(x), Y(y), kot_yazi(v), 1.8)
    # ölçüler
    olcu_zinciri(c, [0, bx, bx + W, PE], "x", Y(PB) + 8, X, False)
    olcu_zinciri(c, [0, PE], "x", Y(PB) + 14, X, False)
    olcu_zinciri(c, [0, by, by + H, PB], "y", X(0) - 36, Y, True)
    olcu_zinciri(c, [0, PB], "y", X(0) - 42, Y, True)
    c.text(X(1.4), Y(by / 2) + 0.7, "ön bahçe 5,00", 1.5, fill="#b45309")
    c.text(X(1.4), Y(by + H + 1.4), "yan 3,00", 1.5, fill="#b45309")
    c.text(X(bx + W / 2), Y(PB - 1.4), "arka bahçe %s" % f2(PB - by - H).replace(".", ","), 1.5, "middle", fill="#b45309")
    return c.svg()

# ================================================================== ÇATI PLANI (1/100)
def cati_icerik(ox, oy, s=10.0):
    c = Cizim()
    tx = lambda x: ox + x * s
    ty = lambda y: oy + y * s
    # alttaki elemanlar (kesik)
    for bk in BALKONLAR:
        c.rect(tx(bk["x0"]), ty(H), (bk["x1"] - bk["x0"]) * s, bk["derinlik"] * s, stroke="#6b7280", sw=0.2, dash="1,0.6")
    pg = PERGOLA
    c.rect(tx(pg["x0"]), ty(pg["y0"]), (pg["x1"] - pg["x0"]) * s, (pg["y1"] - pg["y0"]) * s, fill="#fff", stroke="#111", sw=0.3)
    for i in range(28):
        yy = pg["y0"] + 0.2 + i * (pg["y1"] - pg["y0"] - 0.4) / 27
        c.line(tx(pg["x0"] + 0.1), ty(yy), tx(pg["x1"] - 0.1), ty(yy), 0.12, "#6b7280")
    c.text(tx((pg["x0"] + pg["x1"]) / 2), ty(pg["y1"] - 0.6), "biyoklimatik pergola (döner alüminyum lameller) +2.85", 1.6, "middle", fill="#111")
    t = TERAS
    c.rect(tx(t["x0"]), ty(t["y0"]), (pg["x0"] - t["x0"]) * s, (t["y1"] - t["y0"]) * s, fill="url(#p-dis-tas)", stroke="#111", sw=0.2)
    g = GIRIS_SACAGI
    c.rect(tx(g["x0"]), ty(-g["derinlik"]), (g["x1"] - g["x0"]) * s, g["derinlik"] * s, fill="#e8efe0", stroke="#111", sw=0.3)
    c.text(tx((g["x0"] + g["x1"]) / 2), ty(-g["derinlik"] / 2) + 0.7, "giriş saçağı: yeşil çatı %2 → süzgeç", 1.5, "middle")
    # çatı
    x0, y0, x1, y1 = -SAC, -SAC, W + SAC, H + SAC
    yuzler = [
        ([(x0, y0), (x1, y0), (MAHYA_X[1], H / 2), (MAHYA_X[0], H / 2)], (0, -1)),
        ([(x0, y1), (x1, y1), (MAHYA_X[1], H / 2), (MAHYA_X[0], H / 2)], (0, 1)),
        ([(x0, y0), (x0, y1), (MAHYA_X[0], H / 2)], (-1, 0)),
        ([(x1, y0), (x1, y1), (MAHYA_X[1], H / 2)], (1, 0)),
    ]
    for pts, yon in yuzler:
        c.poly([(tx(x), ty(y)) for x, y in pts], fill="#f3f4f6", stroke="#111", sw=0.5)
    # kiremit sıraları (saçağa paralel)
    for i in range(1, 30):
        d = i * 0.28
        if d > H / 2 + SAC - 0.1:
            break
        # kuzey/güney yüzleri
        for yy, sgn in ((y0 + d, 1), (y1 - d, -1)):
            xa, xb = x0 + d, x1 - d
            if xb > xa:
                c.line(tx(xa), ty(yy), tx(xb), ty(yy), 0.06, "#9ca3af")
        for xx, sgn in ((x0 + d, 1), (x1 - d, -1)):
            ya, yb = y0 + d, y1 - d
            if yb > ya:
                c.line(tx(xx), ty(ya), tx(xx), ty(yb), 0.06, "#9ca3af")
    # mahya ve kalkan
    c.line(tx(MAHYA_X[0]), ty(H / 2), tx(MAHYA_X[1]), ty(H / 2), 0.6)
    for (xa, ya) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        c.line(tx(xa), ty(ya), tx(MAHYA_X[0] if xa < W / 2 else MAHYA_X[1]), ty(H / 2), 0.4)
    # oluk
    c.rect(tx(x0), ty(y0), (x1 - x0) * s, (y1 - y0) * s, stroke="#111", sw=0.25)
    c.rect(tx(x0 + 0.15), ty(y0 + 0.15), (x1 - x0 - 0.3) * s, (y1 - y0 - 0.3) * s, stroke="#111", sw=0.12)
    # yağmur inişleri
    for x, y in ((x0 + 0.3, y0 + 0.3), (x1 - 0.3, y0 + 0.3), (x0 + 0.3, y1 - 0.3), (x1 - 0.3, y1 - 0.3),
                 (W / 2, y1 - 0.3), (6.0, y0 + 0.3)):
        c.circle(tx(x), ty(y), 0.9, fill="#fff", stroke="#111", sw=0.3)
        c.circle(tx(x), ty(y), 0.35, fill="#111", stroke="none")
    # eğim okları
    for (xa, ya), (xb_, yb_) in (((10.0, 5.0), (10.0, 1.2)), ((10.0, 10.0), (10.0, 13.8)),
                                  ((3.0, 7.5), (0.2, 7.5)), ((17.0, 7.5), (19.8, 7.5))):
        c.line(tx(xa), ty(ya), tx(xb_), ty(yb_), 0.3)
        ang = math.atan2(ty(yb_) - ty(ya), tx(xb_) - tx(xa))
        ux, uy = math.cos(ang), math.sin(ang)
        c.poly([(tx(xb_), ty(yb_)), (tx(xb_) - 2.2 * ux + 0.8 * uy, ty(yb_) - 2.2 * uy - 0.8 * ux),
                (tx(xb_) - 2.2 * ux - 0.8 * uy, ty(yb_) - 2.2 * uy + 0.8 * ux)], fill="#111", stroke="none")
        c.text((tx(xa) + tx(xb_)) / 2 + (2.2 if xa == xb_ else 0), (ty(ya) + ty(yb_)) / 2 - (0 if xa == xb_ else 1.2),
               "%30", 1.9, "start" if xa == xb_ else "middle", 700)
    # baca
    a, b = BACA["a"], BACA["b"]
    c.rect(tx(-BACA["derinlik"]), ty(a), BACA["derinlik"] * s, (b - a) * s, fill="url(#p-duvar)", stroke="#111", sw=0.5)
    c.rect(tx(-BACA["derinlik"] + 0.15), ty(a + 0.2), 0.3 * s, (b - a - 0.4) * s, fill="#fff", stroke="#111", sw=0.2)
    c.text(tx(-0.3), ty(b + 0.6), "baca +8.40", 1.6, "middle")
    # havalandırma
    for x in (5.0, 15.0):
        c.rect(tx(x - 0.2), ty(H / 2 - 1.9), 0.4 * s, 0.25 * s, fill="#fff", stroke="#111", sw=0.2)
    c.text(tx(15.0), ty(H / 2 - 2.2), "çatı arası havalandırma kiremidi", 1.4, "middle", fill=GRI)
    # bina çizgisi
    c.rect(tx(0), ty(0), W * s, H * s, stroke="#111", sw=0.25, dash="2,1")
    # kotlar
    _kot_isareti(c, tx(10.0), ty(H / 2 - 0.3), "mahya " + kot_yazi(Z_MAHYA), 1.8)
    _kot_isareti(c, tx(3.0), ty(-0.2), "saçak " + kot_yazi(Z_SACAK), 1.8)
    # ölçüler
    olcu_zinciri(c, [x0, 0, MAHYA_X[0], MAHYA_X[1], W, x1], "x", ty(y0) - 22, tx, True, uzatma=ty(y0) - 1)
    olcu_zinciri(c, [x0, x1], "x", ty(y0) - 28, tx, True)
    olcu_zinciri(c, [y0, 0, H / 2, H, y1], "y", tx(x0) - 8, ty, True)
    olcu_zinciri(c, [y0, y1], "y", tx(x0) - 14, ty, True)
    for ad, v in AKS_X:
        aks_balonu(c, tx(v), ty(y0) - 36, ad)
        c.line(tx(v), ty(y0) - 32.8, tx(v), ty(y0) - 1, 0.08, "#9ca3af", dash="3,1,0.5,1")
    return c.svg()

# ================================================================== SİSTEM KESİTİ (1/50)
KATMAN = [
 # (z, açıklama) — sağdaki not listesi, yukarıdan aşağı
 ("Çatı", ["Antrasit kil kiremit (kilitli)", "Çıta 3/5 + karşı çıta 3/5 (havalandırma boşluğu)",
           "Nefes alan su yalıtım örtüsü (difüzyona açık)", "OSB/3 18 mm", "Ahşap mertek 5/15 @ 50 cm, aşık, dikme",
           "Alüminyum oluk + saçak altı ahşap kompozit lambri"]),
 ("Çatı döşemesi", ["Taşyünü şilte 14 cm (TS 825, 3. bölge)", "Buhar dengeleyici", "Betonarme döşeme 20 cm",
                    "Asma tavan (alçı levha) — net h 2,60"]),
 ("Dış duvar", ["İnce silikon sıva + file (1. kat) / doğal taş 3 cm (zemin)", "Taşyünü levha 8 cm (mantolama)",
                "Gazbeton / bims blok 25 cm", "Alçı sıva + boya"]),
 ("Balkon", ["Porselen R11 2 cm, eğimli şap", "Sürme su yalıtımı, damlalık", "Betonarme konsol 18 cm + Isokorb ısı köprüsü kesici",
             "Çerçevesiz temperli lamine cam korkuluk h=110"]),
 ("Ara kat döşemesi", ["Lamine meşe parke 14 mm / traverten", "Şap 6 cm + yerden ısıtma borusu", "EPS/XPS 3 cm + kenar bandı",
                       "Betonarme döşeme 20 cm + kiriş", "Asma tavan (gizli perde nişi)"]),
 ("Zemin kat döşemesi", ["Traverten 2 cm", "Şap 6 cm + yerden ısıtma", "XPS 3 cm", "Betonarme döşeme 20 cm"]),
 ("Teras", ["Dış mekan traverten R11, 3 cm", "Harç + drenaj", "Sıkıştırılmış stabilize + grobeton", "Eşikte lineer süzgeç"]),
 ("Bodrum perdesi", ["Betonarme perde 30 cm (su geçirimsiz beton)", "2 kat bitümlü membran (−3,86'dan +0,30'a)",
                     "XPS 5 cm + drenaj levhası", "Perde dibinde delikli drenaj borusu + filtre çakıl"]),
 ("Radye temel", ["Parke / şap + yerden ısıtma", "XPS 5 cm", "Radye 60 cm (C30/37)", "2 kat membran + koruma betonu",
                  "Grobeton 10 cm"]),
]

def sistem_kesiti_icerik(ox, oz, s=20.0):
    """Güney cephesi, x = 4.0 (salon / ebeveyn yatak / misafir odası) — 1/50."""
    c = Cizim()
    T = Tuval(ox, oz, s)
    # u: y koordinatı (m), kesit y=12.0 ... 17.0 arası
    u0, u1 = 12.0, 17.2
    def U(y):
        return ox + (y - u0) * s
    Z = T.Z
    # toprak
    c.rect(U(H), Z(TABII_ZEMIN), (u1 - H) * s, (TABII_ZEMIN + 3.95) * s, fill="url(#p-toprak)")
    c.rect(U(u0), Z(-3.86), (u1 - u0) * s, 0.9, fill="none")
    # radye + grobeton
    c.rect(U(u0), Z(-3.16), (H + 0.5 - u0) * s, 0.60 * s, fill="#111")
    c.rect(U(u0), Z(-3.76), (H + 0.6 - u0) * s, 0.10 * s, fill="url(#p-beton)", stroke="#111", sw=0.15)
    c.rect(U(u0), Z(-3.06), (H - DIS_DUVAR - u0) * s, 0.10 * s, fill="#e5e7eb", stroke="#111", sw=0.12)   # şap
    c.rect(U(u0), Z(-3.11), (H - DIS_DUVAR - u0) * s, 0.05 * s, fill="url(#p-yalitim)", stroke="#111", sw=0.1)
    # perde + yalıtım
    c.rect(U(H - 0.35), Z(0.0), 0.30 * s, 3.16 * s, fill="#111")
    c.rect(U(H - 0.05), Z(0.0 + 0.3), 0.05 * s, 3.46 * s, fill="url(#p-yalitim)", stroke="#111", sw=0.12)
    c.rect(U(H), Z(0.0 + 0.3), 0.02 * s, 3.46 * s, fill="#1f2937")
    c.circle(U(H + 0.25), Z(-3.0), 0.08 * s, fill="#fff", stroke="#111", sw=0.3)
    c.rect(U(H + 0.02), Z(-2.6), 0.6 * s, 0.7 * s, fill="#fff", stroke="#9ca3af", sw=0.1)
    c.circle(U(H + 0.4), Z(-3.0), 0.2 * s, fill="none", stroke="#6b7280", sw=0.15, dash="0.5,0.5")
    # bodrum iç
    c.text(U(13.4), Z(-1.4), "MİSAFİR ODASI (bodrum)", 2.4, "middle", 700, fill="#374151")
    # zemin kat döşemesi
    for z in (0.0, KOT["1. Kat"]):
        c.rect(U(u0), Z(z - 0.10), (H - u0) * s, 0.20 * s, fill="#111")
        c.rect(U(u0), Z(z), (H - DIS_DUVAR - u0) * s, 0.10 * s, fill="#e5e7eb", stroke="#111", sw=0.12)
        c.rect(U(H - 0.30), Z(z - 0.30), 0.30 * s, 0.30 * s, fill="#111")         # kiriş
        for i in range(8):
            c.circle(U(u0 + 0.3 + i * 0.35), Z(z - 0.05), 0.4, fill="#fff", stroke="#b91c1c", sw=0.15)
    # çatı döşemesi
    z = KOT["Çatı"]
    c.rect(U(u0), Z(z), (H - u0) * s, 0.20 * s, fill="#111")
    c.rect(U(u0), Z(z + 0.14), (H - DIS_DUVAR - u0) * s, 0.14 * s, fill="url(#p-yalitim)", stroke="#111", sw=0.12)
    c.rect(U(H - 0.30), Z(z - 0.20), 0.30 * s, 0.30 * s, fill="#111")
    # zemin kat: sürme doğrama (0–2.60), üstünde kiriş + taş kaplama
    c.rect(U(H - 0.25), Z(2.60), 0.12 * s, 2.60 * s, fill=CAM, stroke="#111", sw=0.3)
    c.rect(U(H - 0.35), Z(KOT["1. Kat"] - 0.30), 0.35 * s, (KOT["1. Kat"] - 0.30 - 2.60) * s, fill="url(#p-duvar)", stroke="#111", sw=0.3)
    c.rect(U(H - 0.03), Z(KOT["1. Kat"]), 0.03 * s, (KOT["1. Kat"] - 2.60) * s, fill="#d9cdb4", stroke="#111", sw=0.1)
    c.rect(U(H - 0.30), Z(0.02), 0.34 * s, 0.04 * s, fill="#111")     # eşik
    c.text(U(13.4), Z(1.3), "SALON", 2.4, "middle", 700, fill="#374151")
    # 1. kat: sürme (0–2.30) + balkon
    zz = KOT["1. Kat"]
    c.rect(U(H - 0.25), Z(zz + 2.30), 0.12 * s, 2.30 * s, fill=CAM, stroke="#111", sw=0.3)
    c.rect(U(H - 0.35), Z(KOT["Çatı"] - 0.20), 0.35 * s, (KOT["Çatı"] - 0.20 - zz - 2.30) * s, fill="url(#p-duvar)", stroke="#111", sw=0.3)
    c.rect(U(H - 0.08), Z(KOT["Çatı"] - 0.20), 0.08 * s, (KOT["Çatı"] - 0.20 - zz - 2.30) * s, fill="url(#p-yalitim)", stroke="#111", sw=0.1)
    c.rect(U(H - 0.20), Z(KOT["Çatı"] - 0.20 - (KOT["Çatı"] - 0.20 - zz - 2.30) + 0.2), 0.17 * s, 0.18 * s, fill="#374151")   # panjur kutusu
    c.text(U(13.4), Z(zz + 1.3), "EBEVEYN YATAK ODASI", 2.4, "middle", 700, fill="#374151")
    bk = BALKONLAR[0]
    c.rect(U(H), Z(Z_BALKON), bk["derinlik"] * s, 0.18 * s, fill="#111")
    c.rect(U(H - 0.02), Z(Z_BALKON - 0.02), 0.10 * s, 0.22 * s, fill="#f59e0b")          # ısı köprüsü kesici
    c.rect(U(H), Z(Z_BALKON + 0.03), bk["derinlik"] * s, 0.03 * s, fill="#d6d3d1", stroke="#111", sw=0.1)
    c.rect(U(H + bk["derinlik"] - 0.08), Z(Z_BALKON + 1.10), 0.03 * s, 1.20 * s, fill="#7dd3fc", stroke="#111", sw=0.12)
    c.rect(U(H + bk["derinlik"] - 0.14), Z(Z_BALKON + 0.08), 0.14 * s, 0.26 * s, fill="#6b7280")
    # teras
    c.rect(U(H), Z(-0.02), (u1 - H) * s, 0.06 * s, fill="#d6d3d1", stroke="#111", sw=0.15)
    c.rect(U(H), Z(-0.08), (u1 - H) * s, (TABII_ZEMIN + 0.08 + 0.25) * s, fill="url(#p-beton)", stroke="#111", sw=0.1)
    c.rect(U(H + 0.05), Z(-0.02), 0.12 * s, 0.10 * s, fill="#fff", stroke="#111", sw=0.2)      # lineer süzgeç
    # çatı: saçak
    zr = lambda y: cati_z(4.0, y)
    pts_u = [(U(y), Z(zr(y))) for y in (u0, H + SAC)]
    pts_a = [(U(y), Z(zr(y) - 0.26)) for y in (H + SAC, u0)]
    c.poly(pts_u + pts_a, fill="#c8a57a", stroke="#111", sw=0.4)
    for i in range(6):
        y = u0 + i * 0.6
        c.line(U(y), Z(zr(y)), U(y + 0.3), Z(zr(y + 0.3)), 0.8, "#374151")
    c.rect(U(H + SAC - 0.04), Z(Z_SACAK), 0.04 * s, (Z_SACAK - Z_ALIN_ALT) * s, fill="#374151")
    c.circle(U(H + SAC + 0.07), Z(Z_SACAK - 0.1), 0.08 * s, fill="#fff", stroke="#111", sw=0.3)
    c.rect(U(H), Z(Z_ALIN_ALT), SAC * s, 0.02 * s, fill="#c89b6d", stroke="#111", sw=0.12)
    c.rect(U(H - 0.35), Z(zr(H - 0.35) - 0.26), 0.35 * s, (zr(H - 0.35) - 0.26 - KOT["Çatı"]) * s, fill="#e7d3b4", stroke="#111", sw=0.2)
    c.text(U(13.2), Z(6.75), "ÇATI ARASI", 2.2, "middle", 700, fill="#374151")
    # kotlar
    for v in (Z_SACAK, KOT["Çatı"], KOT["1. Kat"], 0.0, TABII_ZEMIN, KOT["Bodrum"], -3.76):
        c.line(U(u0) - 3, Z(v), U(u0), Z(v), 0.1, "#6b7280")
        _kot_isareti(c, U(u0) - 4, Z(v), kot_yazi(v), 2.0, sol=True)
    # katman notları
    nx = U(u1) + 14
    ny = Z(Z_SACAK) - 4
    hedef_z = {"Çatı": zr(15.4) - 0.1, "Çatı döşemesi": KOT["Çatı"] - 0.1, "Dış duvar": 4.6, "Balkon": Z_BALKON - 0.05,
               "Ara kat döşemesi": KOT["1. Kat"] - 0.05, "Zemin kat döşemesi": -0.05, "Teras": -0.05,
               "Bodrum perdesi": -1.8, "Radye temel": -3.4}
    hedef_u = {"Çatı": 15.4, "Çatı döşemesi": 14.2, "Dış duvar": H - 0.15, "Balkon": H + 0.7, "Ara kat döşemesi": 14.0,
               "Zemin kat döşemesi": 13.8, "Teras": 16.2, "Bodrum perdesi": H - 0.2, "Radye temel": 13.6}
    for ad, satirlar in KATMAN:
        c.text(nx, ny, ad.upper(), 2.1, weight=700)
        c.line(nx - 1, ny - 0.7, U(hedef_u[ad]), Z(hedef_z[ad]), 0.13, "#6b7280")
        c.circle(U(hedef_u[ad]), Z(hedef_z[ad]), 0.45, fill="#b45309", stroke="none")
        ny += 2.9
        for sat in satirlar:
            c.text(nx + 1.5, ny, "· " + sat, 1.75, fill="#1f2937")
            ny += 2.35
        ny += 1.6
    return c.svg()

# ================================================================== MERDİVEN DETAYI (1/50)
def merdiven_icerik(ox, oy, s=20.0):
    c = Cizim()
    mk = merdiven_kollari("Zemin")
    k1, k2 = mk["kollar"]
    r, b = mk["riht"], MERDIVEN["basamak"]
    kx0, ky0, kx1, ky1 = MERDIVEN["kutu"]
    # ---------- kesit (batı kol boyunca, doğuya bakış) — y yatay
    oz = oy + 118
    U = lambda y: ox + (y - 2.6) * s
    Z = lambda z: oz - z * s
    # döşemeler
    for z, (a, bb) in ((0.0, (2.6, 4.155)), (KOT["1. Kat"], (2.6, 4.435))):
        c.rect(U(a), Z(z), (bb - a) * s, 0.30 * s, fill="#111")
    c.rect(U(7.925), Z(KOT["1. Kat"]), 0.6 * s, 0.30 * s, fill="#111")
    c.rect(U(7.925), Z(0.0), 0.6 * s, 0.30 * s, fill="#111")
    c.rect(U(7.925), Z(KOT["1. Kat"] - 0.30), 0.15 * s, (KOT["1. Kat"] - 0.30) * s, fill="url(#p-duvar)", stroke="#111", sw=0.4)
    # batı kol (kesilen)
    pts = [(k1[2], 0.0)]
    for i in range(k1[4]):
        y = k1[2] + i * b
        pts += [(y, (i + 1) * r), (min(y + b, k1[3]), (i + 1) * r)]
    zs = k1[4] * r
    pts += [(7.925, zs), (7.925, zs - 0.18), (MERDIVEN["sahanlik"][0] + 0.1, zs - 0.18), (k1[2] + 0.1, -0.1), (k1[2], -0.1)]
    c.poly([(U(y), Z(z)) for y, z in pts], fill="#9ca3af", stroke="#111", sw=0.5)
    # doğu kol (görünen)
    pts2 = [(k2[2], zs)]
    for i in range(k2[4]):
        y = k2[2] - i * b
        pts2 += [(y, zs + (i + 1) * r), (max(y - b, k2[3]), zs + (i + 1) * r)]
    c.poly([(U(y), Z(z)) for y, z in pts2], stroke="#374151", sw=0.3, kapali=False)
    c.line(U(k2[2]), Z(zs - 0.18), U(k2[3]), Z(KOT["1. Kat"] - 0.18), 0.25, "#374151")
    # kaplama: traverten basamak
    for i in range(k1[4]):
        y = k1[2] + i * b
        c.rect(U(y - 0.03), Z((i + 1) * r + 0.0), (b + 0.03) * s, 0.03 * s, fill="#e7e5e4", stroke="#111", sw=0.1)
    # korkuluk (cam + küpeşte)
    c.line(U(k1[2]), Z(0.95), U(k1[3]), Z(zs + 0.95), 0.6, "#0ea5e9")
    c.line(U(k1[2]), Z(0.05), U(k1[3]), Z(zs + 0.05), 0.3, "#0ea5e9", dash="1,0.6")
    c.line(U(k1[2]) - 4, Z(0.95), U(k1[2]), Z(0.95), 0.6, "#0ea5e9")
    # ölçüler
    olcu_zinciri(c, [k1[2] + i * b for i in range(k1[4])] + [MERDIVEN["sahanlik"][1]], "x", Z(-0.6), U, False, boy=1.6)
    olcu_zinciri(c, [0.0, zs, KOT["1. Kat"]], "y", U(2.6) - 8, Z, True)
    for v in (0.0, zs, KOT["1. Kat"]):
        _kot_isareti(c, U(8.6) + 2, Z(v), kot_yazi(v), 2.0)
    c.text(U(5.6), Z(-1.25), "KESİT M–M (batı kol) · Ö: 1/50", 2.8, "middle", 700)
    c.text(U(3.0), Z(2.6), "baş yüksekliği ≥ 2,20", 1.8, fill="#b45309")
    # ---------- plan (zemin kat) — 1/50
    px, py = ox + 150, oy + 8
    X = lambda x: px + (x - kx0) * s
    Y = lambda y: py + (y - ky0 + 0.4) * s
    c.rect(X(kx0), Y(ky0), (kx1 - kx0) * s, (ky1 - ky0) * s, fill="#fafafa", stroke="#111", sw=0.2)
    c.rect(X(kx1 - 0.075), Y(ky0), 0.15 * s, (ky1 - ky0) * s, fill="url(#p-duvar)", stroke="#111", sw=0.4)
    c.rect(X(kx0), Y(ky1 - 0.075), (kx1 - kx0) * s, 0.15 * s, fill="#111")
    bx0, bx1 = MERDIVEN["bati_kol"]; dx0, dx1 = MERDIVEN["dogu_kol"]
    for i in range(k1[4]):
        y = k1[2] + i * b
        c.line(X(bx0), Y(y), X(bx1), Y(y), 0.25)
    for i in range(k2[4] + 1):
        y = k2[2] - i * b
        c.line(X(dx0), Y(y), X(dx1), Y(y), 0.25, dash="1,0.6")
    for x in (bx0, bx1, dx0, dx1):
        c.line(X(x), Y(4.155 if x < 11.3 else 4.435), X(x), Y(MERDIVEN["sahanlik"][0]), 0.3)
    c.rect(X(bx0), Y(MERDIVEN["sahanlik"][0]), (dx1 - bx0) * s, (MERDIVEN["sahanlik"][1] - MERDIVEN["sahanlik"][0]) * s,
           fill="url(#p-tas)", stroke="#111", sw=0.3)
    c.line(X(kx0 + 0.02), Y(k1[2]), X(kx0 + 0.02), Y(ky1), 0.8, "#0ea5e9")
    xm = (bx0 + bx1) / 2
    c.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#111" stroke-width="0.3" marker-end="url(#ok)"/>'
          % (X(xm), Y(k1[2] - 0.15), X(xm), Y(7.2)))
    c.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#111" stroke-width="0.3" marker-end="url(#ok)"/>'
          % (X((dx0 + dx1) / 2), Y(7.2), X((dx0 + dx1) / 2), Y(k2[3] - 0.1)))
    for i in range(k1[4]):
        c.text(X(bx0) + 1.2, Y(k1[2] + i * b + b / 2) + 0.7, str(i + 1), 1.6)
    for i in range(k2[4]):
        c.text(X(dx1) - 1.2, Y(k2[2] - i * b - b / 2) + 0.7, str(k1[4] + i + 1), 1.6, "end")
    olcu_zinciri(c, [kx0, bx0, bx1, dx0, dx1, kx1], "x", Y(ky0) - 5, X, True, boy=1.6)
    olcu_zinciri(c, [ky0, k1[2], MERDIVEN["sahanlik"][0], MERDIVEN["sahanlik"][1], ky1], "y", X(kx1) + 8, Y, False, boy=1.6)
    c.text(X((kx0 + kx1) / 2), Y(ky1) + 9, "PLAN (zemin kat) · Ö: 1/50", 2.8, "middle", 700)
    # ---------- hesap tablosu
    tx0, ty0 = ox, oy + 150
    c.text(tx0, ty0, "MERDİVEN HESABI (PAİY Md. 32 — konut içi merdiven)", 2.6, weight=700)
    satirlar = [("Kat", "Yükseklik", "Rıht", "Basamak", "2r + b", "Kol / sahanlık"),]
    for kat in ("Bodrum", "Zemin"):
        m = merdiven_kollari(kat)
        satirlar.append(("%s → %s" % (m["alt"], m["ust"]), "%s m" % f2(m["h"]).replace(".", ","),
                         "%d × %s cm" % (m["kollar"][0][4] + m["kollar"][1][4], ("%.1f" % (m["riht"] * 100)).replace(".", ",")),
                         "28 cm", ("%.1f" % (2 * m["riht"] * 100 + 28)).replace(".", ","), "1,20 / 1,25 m"))
    satirlar.append(("Sınır değer", "—", "≤ 17,5 cm", "≥ 26 cm", "60–64", "≥ 1,00 m"))
    kol = [0, 34, 56, 82, 102, 120]
    for i, sat in enumerate(satirlar):
        y = ty0 + 6 + i * 5
        if i == 0 or i == len(satirlar) - 1:
            c.rect(tx0 - 1, y - 3.6, 150, 5, fill="#f3f4f6")
        for k, v in enumerate(sat):
            c.text(tx0 + kol[k], y, v, 2.0, weight=700 if i == 0 else 400)
    notlar = ["Basamak ve sahanlık: 3 cm traverten, 2 cm rıht; basamak burnunda kaymaz kanal.",
              "Korkuluk: 10+10 mm temperli lamine cam, zemine gömme alüminyum U profil, h = 100 cm (basamak burnundan), paslanmaz küpeşte Ø42.",
              "Duvar tarafında Ø40 paslanmaz küpeşte h = 90 cm; LED basamak aydınlatması (her 3 basamakta bir).",
              "Kol altı: betonarme plak 18 cm, alttan alçı sıva + boya; sahanlık asansör perdesine oturur."]
    y = ty0 + 6 + len(satirlar) * 5 + 4
    for n in notlar:
        for j, sat in enumerate(_sar(n, 110)):
            c.text(tx0, y, ("· " if j == 0 else "  ") + sat, 1.9, fill="#1f2937"); y += 2.8
    return c.svg()

# ================================================================== DOĞRAMA LİSTESİ
def dograma_icerik(ox, oy):
    c = Cizim()
    s = 5.0                         # 1/200 çizim, kutu içinde
    pt = pencere_tipleri()
    kt = kapi_tipleri()
    c.text(ox, oy, "PENCERE VE CAM KAPILAR (alüminyum, ısı yalıtımlı, antrasit RAL 7016, 4+16Ar+4 Low-E ısıcam)", 2.6, weight=700)
    x, y = ox, oy + 5
    kutu_w, kutu_h = 58, 44
    for i, (kod, tip, en, yuk, den, liste) in enumerate(pt):
        cx = ox + (i % 5) * (kutu_w + 1.5)
        cy = oy + 4 + (i // 5) * (kutu_h + 1.5)
        c.rect(cx, cy, kutu_w, kutu_h, stroke="#111", sw=0.25)
        c.rect(cx, cy, kutu_w, 5, fill="#f3f4f6", stroke="#111", sw=0.25)
        c.text(cx + 2, cy + 3.7, kod, 2.6, weight=700)
        c.text(cx + kutu_w - 2, cy + 3.7, "%d adet" % len(liste), 2.1, "end", 700)
        # çizim
        sk = min(5.0, 34.0 / max(en, 0.1), 26.0 / max(yuk + den, 0.1))
        gx = cx + (kutu_w - en * sk) / 2
        taban = cy + 34
        c.line(cx + 4, taban, cx + kutu_w - 4, taban, 0.15, "#9ca3af", dash="0.8,0.5")
        c.rect(gx, taban - (den + yuk) * sk, en * sk, yuk * sk, fill=CAM, stroke="#111", sw=0.4)
        n = 1
        if tip == "S":
            n = 3 if en > 4.5 else 2
        elif tip in ("P", "F") and en > 1.6:
            n = 2 if en < 3.0 else 3
        for k in range(1, n):
            xx = gx + k * en * sk / n
            c.line(xx, taban - (den + yuk) * sk, xx, taban - den * sk, 0.3)
        if tip == "S":
            for k in range(n):
                xa = gx + (k + 0.25) * en * sk / n
                c.add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#111" stroke-width="0.2" marker-end="url(#ok)"/>'
                      % (xa, taban - (den + yuk / 2) * sk, xa + en * sk / n * 0.5, taban - (den + yuk / 2) * sk))
        elif tip in ("P", "Y"):
            # açılım üçgeni (vasistas + çarpma)
            c.poly([(gx, taban - (den + yuk) * sk), (gx + en * sk / n, taban - (den + yuk / 2) * sk), (gx, taban - den * sk)],
                   stroke="#6b7280", sw=0.12, kapali=False, dash="0.8,0.5")
        adlar = {"S": "Kaldır-sür cam kapı", "P": "Pencere (çift açılım)", "F": "Sabit cam", "Y": "Yüksek pencere (buzlu)",
                 "I": "Işıklık penceresi"}
        c.text(cx + 2, cy + 38.3, "%s · %s × %s" % (adlar[tip], cm(en), cm(yuk)), 1.85, weight=700)
        yerler = ", ".join(sorted({"%s %s" % ({"Bodrum": "B", "Zemin": "Z", "1. Kat": "1K"}[k], p[0]) for k, p in liste}))
        denizler = "/".join(sorted({cm(q[4]) for _, q in liste}))
        c.text(cx + 2, cy + 41.5, "denizlik %s · %s" % (denizler, yerler), 1.6, fill=GRI)
    # kapılar tablosu
    y0 = oy + 4 + ((len(pt) + 4) // 5) * (kutu_h + 1.5) + 6
    c.text(ox, y0, "KAPILAR", 2.6, weight=700)
    kolon = [0, 14, 70, 96, 116, 136]
    basliklar = ["Kod", "Tür", "Genişlik × yükseklik", "Adet", "Katlar", "Açıklama"]
    c.rect(ox - 1, y0 + 2, 300, 5, fill="#f3f4f6")
    for k, b in enumerate(basliklar):
        c.text(ox + kolon[k], y0 + 5.6, b, 2.0, weight=700)
    aciklama = {"kapi": "Amerikan panel gövde, akrilik lake, gizli menteşe, manyetik kilit",
                "yangin": "EI30 sertifikalı çelik, kapı kapatıcı, duman contası",
                "giris": "Çelik iskelet, ahşap kompozit kaplama, akıllı kilit, üst eşik fitili",
                "servis": "Isı yalıtımlı alüminyum, antrasit, yarım cam",
                "cift": "Alüminyum çerçeve, temperli buzlu cam panel",
                "surme": "Gizli kasalı sürme (Eclisse) / sauna: temperli cam",
                "garaj": "Yalıtımlı panel 42 mm, motorlu, fotosel",
                "asansor": "Asansör firması tedariki, paslanmaz",
                "kapak": "Menteşeli servis kapağı, kilitli"}
    for i, (kod, tip, en, yuk, liste) in enumerate(kt):
        yy = y0 + 10.5 + i * 4.2
        katlar = ", ".join(sorted({k for k, _ in liste}, key=KATLAR_SIRA.index))
        for k, v in enumerate([kod, KAPI_AD[tip], "%s × %s" % (cm(en), cm(yuk)), str(len(liste)), katlar, aciklama[tip]]):
            c.text(ox + kolon[k], yy, v, 1.9, weight=700 if k == 0 else 400)
        c.line(ox - 1, yy + 1.4, ox + 299, yy + 1.4, 0.08, "#d1d5db")
    return c.svg()

# ================================================================== KAPAK
def kapak_icerik():
    c = Cizim()
    # render
    for ad in ("bahce", "giris", "kus"):
        yol = os.path.join(KOK, "render", ad + ".jpg")
        if os.path.exists(yol):
            with open(yol, "rb") as f:
                veri = base64.b64encode(f.read()).decode()
            c.add('<image x="20" y="20" width="290" height="163" preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,%s"/>' % veri)
            c.rect(20, 20, 290, 163, stroke="#111", sw=0.3)
            break
    c.text(20, 196, "DURUNDAY VİLLA", 9.0, weight=700, ls=0.8)
    c.text(20, 204, "Konya · Meram · Durunday — bodrumlu dubleks müstakil konut", 3.2, fill="#374151")
    c.text(20, 210, "Mimari ön proje (avan) çizim seti · Revizyon R1 · %s" % ciz.TARIH, 2.6, fill=GRI)
    # pafta listesi
    c.text(20, 222, "PAFTA LİSTESİ", 2.6, weight=700, ls=0.3)
    liste = [(no, ad, olc) for dosya, ad, no, olc, _ in PAFTALAR]
    for i, (no, ad, olc) in enumerate(liste):
        kx = 20 + (i // 7) * 100
        ky = 228 + (i % 7) * 5.2
        c.text(kx, ky, no, 2.2, weight=700)
        c.text(kx + 12, ky, ad, 2.2)
        c.text(kx + 92, ky, olc, 2.0, "end", fill=GRI)
    # alan tablosu (sağ üst, antet yanında değil — resmin altında sağda)
    ax, ay = 222, 196
    c.text(ax, ay, "ALAN ÖZETİ", 2.6, weight=700, ls=0.3)
    oz = kat_ozeti()
    satirlar = [("Kat", "Brüt", "Net")]
    top_b = top_n = 0
    for kat in KATLAR_SIRA:
        satirlar.append((kat, "300,00", f2(oz[kat][0]).replace(".", ",")))
        top_b += 300; top_n += oz[kat][0]
    satirlar.append(("Toplam", "%s" % f2(top_b).replace(".", ","), f2(top_n).replace(".", ",")))
    for i, (a, b_, n) in enumerate(satirlar):
        y = ay + 6 + i * 4.4
        w = 700 if i in (0, len(satirlar) - 1) else 400
        c.text(ax, y, a, 2.1, weight=w); c.text(ax + 48, y, b_, 2.1, "end", weight=w); c.text(ax + 72, y, n, 2.1, "end", weight=w)
    y = ay + 6 + len(satirlar) * 4.4 + 2
    for t in ("Parsel 1.001 m² · TAKS 0,30 · KAKS 0,60", "Emsal alanı 600 m² (zemin + 1. kat)",
              "Teras 80 m² · balkon 19 m² · pergola 30 m²", "Otopark: 2 kapalı + 2 açık"):
        c.text(ax, y, t, 1.9, fill="#1f2937"); y += 3.2
    return c.svg()

# ================================================================== pafta tanımları
def _pafta_kesit(ad):
    e = KESITLER[ad][0]
    if e == "x":
        ic = kesit_icerik(ad, 70, 172)
    else:
        ic = kesit_icerik(ad, 55, 172)
    c = Cizim(); c.add(ic)
    c.text(24, 279, "%s–%s KESİTİ · Ö: 1/100" % (ad, ad), 3.8, weight=700, ls=0.3)
    c.text(24, 284, ("Kesit x = %s m, doğuya bakış (hol, galeri, yemek alanı)" if e == "x"
                     else "Kesit y = %s m, kuzeye bakış (salon–yemek–mutfak; ışıklıklar)") % f2(KESITLER[ad][1]).replace(".", ","),
           2.3, fill=GRI)
    return c.svg()

def _pafta_gorunus(c1, c2):
    c = Cizim()
    if c1 in ("K", "G"):
        c.add(gorunus_icerik(c1, 84, 124))
        c.add(gorunus_icerik(c2, 84, 254))
    else:
        c.add(gorunus_icerik(c1, 108, 124))
        c.add(gorunus_icerik(c2, 108, 254))
    return c.svg()

KESIT_LEJANT = [("betonarme", "Betonarme (kesilen)"), ("duvar", "Duvar (kesilen)"), ("yalitim", "Isı / su yalıtımı"),
                ("toprak", "Doğal zemin"), ("cam", "Cam / doğrama"), ("kot", "Kot (m)")]
GOR_LEJANT = [("sille", "Doğal taş kaplama (Sille taşı)"), ("siva", "İnce silikon sıva (mantolama)"),
              ("ahsap", "Ahşap kompozit kaplama"), ("kiremit", "Antrasit kil kiremit"), ("cam", "Isıcam, antrasit doğrama")]

PAFTALAR = [
 # dosya, ad, no, ölçek, üretici
 ("00-kapak", "KAPAK VE PAFTA LİSTESİ", "A-00", "—", lambda: pafta("A-00", "KAPAK VE PAFTA LİSTESİ", "—", kapak_icerik(),
      notlar=["Bu set ön tasarım (avan) niteliğindedir; ruhsata esas mimari, statik, mekanik ve elektrik projeleri yetkili müelliflerce hazırlanacaktır.",
              "Parsel, imar ve kot bilgileri varsayımdır; Meram Belediyesi imar durumu ve hâlihazır harita ile teyit edilmelidir.",
              "Ölçüler cm, kotlar m'dir. ±0.00 = zemin kat bitmiş döşemesi = tabii zemin +0.30.",
              "Tüm paftalar tek veri kaynağından (veri.py) üretilir; plan, kesit, görünüş ve tablolar birbiriyle tutarlıdır."], kuzey=False)),
 ("01-vaziyet-plani", "VAZİYET PLANI", "A-01", "1/200", lambda: pafta("A-01", "VAZİYET PLANI", "1/200",
      _sar_icerik(vaziyet_icerik(96, 62), "VAZİYET PLANI · Ö: 1/200", "Parsel 26,00 × 38,50 = 1.001 m² · ön bahçe 5,00 · yan bahçeler 3,00 · arka bahçe 18,50"),
      notlar=["Araç girişi doğuda, garaja doğrudan (rampa yok); önünde 2 araçlık açık park yeri.",
              "Yaya girişi ayrı kapıdan, giriş saçağına yürüyüş yolu ile.",
              "Servis yolu doğu yan bahçeden arka mutfak kapısına ulaşır.",
              "Bahçe duvarı: yol cephesinde 50 cm taş + 100 cm antrasit metal çit; yan ve arka sınırlarda 180 cm.",
              "Havuz arka bahçede; makine dairesi bodrumda (B-16).",
              "Selvi dizileri yan komşulara görsel perde oluşturur."],
      lejant=[("cam", "Havuz"), ("tas", "Sert zemin / taş döşeme"), ("aks", "Ağaç (mevcut/dikilecek)")])),
 ("02-bodrum-kat", "BODRUM KAT PLANI", "A-02", "1/100", lambda: ciz.kat_plani_pafta("Bodrum", "A-02")),
 ("03-zemin-kat", "ZEMİN KAT PLANI", "A-03", "1/100", lambda: ciz.kat_plani_pafta("Zemin", "A-03")),
 ("04-birinci-kat", "1. KAT PLANI", "A-04", "1/100", lambda: ciz.kat_plani_pafta("1. Kat", "A-04")),
 ("05-cati-plani", "ÇATI PLANI", "A-05", "1/100", lambda: pafta("A-05", "ÇATI PLANI", "1/100",
      _sar_icerik(cati_icerik(72, 84), "ÇATI PLANI · Ö: 1/100", "Kırma çatı %%30 · saçak 80 cm · mahya %s" % kot_yazi(Z_MAHYA)),
      notlar=["Çatı konstrüksiyonu ahşaptır; betonarme çatı döşemesi üzerinde 14 cm taşyünü ısı yalıtımı vardır.",
              "Oluk ve yağmur inişleri antrasit alüminyum; inişler bahçe drenajına ve yağmur suyu deposuna bağlanır.",
              "Çatı arası havalandırılır (saçak altı menfez + mahya havalandırması).",
              "Giriş saçağı ekstansif yeşil çatıdır; pergola biyoklimatik (açılır lamelli) alüminyumdur."],
      lejant=[("kiremit", "Kil kiremit"), ("duvar", "Baca (taş kaplı)")])),
 ("06-kesit-aa", "A–A KESİTİ", "A-06", "1/100", lambda: pafta("A-06", "A–A KESİTİ", "1/100", _pafta_kesit("A"),
      notlar=["Kesit giriş kapısı, galeri, hol ve yemek alanından geçer; merdiven kesitin arkasında görünüştedir.",
              "Galeri: giriş holü zemin kattan çatı döşemesine kadar çift yüksekliktir (6,20 m).",
              "Kat yükseklikleri: bodrum 3,06 · zemin 3,20 · 1. kat 3,00 m; döşeme 30 cm (20 plak + 10 şap/kaplama).",
              "Radye temel 60 cm; zemin etüdüne göre statik projede kesinleşecektir."], lejant=KESIT_LEJANT)),
 ("07-kesit-bb", "B–B KESİTİ", "A-07", "1/100", lambda: pafta("A-07", "B–B KESİTİ", "1/100", _pafta_kesit("B"),
      notlar=["Kesit salon–yemek–mutfak açık planından geçer; bodrumda batı ve doğu ışıklıkları görülür.",
              "Işıklık tabanı −3.16, süzgeçli; üstü galvaniz ızgara ve cam korkuluk.",
              "Şömine bacası batı cephede, çatıdan yükselir (+8.40)."], lejant=KESIT_LEJANT)),
 ("08-gorunus-kg", "KUZEY VE GÜNEY GÖRÜNÜŞLERİ", "A-08", "1/100", lambda: pafta("A-08", "KUZEY VE GÜNEY GÖRÜNÜŞLERİ", "1/100",
      _pafta_gorunus("K", "G"), notlar=["Doğramalar antrasit (RAL 7016) ısı yalıtımlı alüminyum.",
                                         "Yatak odalarında motorlu dış jaluzi kutusu cephe içine gömülüdür.",
                                         "Güney cephesi: konsol balkonlar ve teras pergolası yazın güneş kontrolü sağlar."],
      lejant=GOR_LEJANT)),
 ("09-gorunus-db", "DOĞU VE BATI GÖRÜNÜŞLERİ", "A-09", "1/100", lambda: pafta("A-09", "DOĞU VE BATI GÖRÜNÜŞLERİ", "1/100",
      _pafta_gorunus("D", "B"), notlar=["Batı cephesinde şömine bacası taş kaplı dikey kütle olarak okunur.",
                                         "Işıklık korkulukları çerçevesiz cam, h = 110 cm."], lejant=GOR_LEJANT)),
 ("10-sistem-kesiti", "SİSTEM KESİTİ", "A-10", "1/50", lambda: pafta("A-10", "SİSTEM KESİTİ", "1/50",
      _sar_icerik(sistem_kesiti_icerik(46, 190), "SİSTEM KESİTİ S–S · Ö: 1/50", "Güney cephesi, x = 4,00 m: bodrum misafir odası · salon · ebeveyn yatak odası ve balkon"),
      notlar=["Isı yalıtımı TS 825'e göre 3. bölge (Konya) değerleriyle; enerji kimlik belgesi hesabında kesinleşir.",
              "Bodrum su yalıtımı radye altından perde üstüne kesintisiz; köşelerde pah ve takviye bandı.",
              "Balkon döşemesi ısı köprüsü kesici elemanla (Isokorb) ana döşemeye bağlanır.",
              "Doğrama montajı: iç tarafta buhar kesici, dış tarafta difüzyona açık bant (RAL montaj)."],
      lejant=KESIT_LEJANT)),
 ("11-merdiven", "MERDİVEN DETAYI", "A-11", "1/50", lambda: pafta("A-11", "MERDİVEN DETAYI", "1/50",
      _sar_icerik(merdiven_icerik(34, 30), "MERDİVEN DETAYI · Ö: 1/50", "İki kollu (U) merdiven, betonarme, traverten kaplama, cam korkuluk"),
      notlar=["Merdiven kutusu tüm katlarda aynı yerdedir (x 10,00–12,60 · y 3,20–8,00).",
              "Bodrum→zemin 18 rıht (9+9), zemin→1. kat 19 rıht (10+9); basamak 28 cm."])),
 ("12-dograma", "DOĞRAMA LİSTESİ", "A-12", "—", lambda: pafta("A-12", "DOĞRAMA LİSTESİ", "—",
      dograma_icerik(22, 22), notlar=["Ölçüler kaba inşaat boşluğudur (cm); imalat öncesi yerinde alınacaktır.",
                                        "Tüm dış doğramalar Uw ≤ 1,4 W/m²K; yatak odalarında sineklik ve motorlu jaluzi.",
                                        "Kapı kodları plan paftalarındaki kapı yerleriyle eşleşir."])),
]

def _sar_icerik(icerik, baslik, alt):
    c = Cizim(); c.add(icerik)
    c.text(24, 279, baslik, 3.8, weight=700, ls=0.3)
    c.text(24, 284, alt, 2.3, fill=GRI)
    return c.svg()

CIZIMLER = [(d, ad, fn) for d, ad, no, olc, fn in PAFTALAR]

if __name__ == "__main__":
    hedef = os.path.join(KOK, "cizimler")
    os.makedirs(hedef, exist_ok=True)
    for f in os.listdir(hedef):
        if f.endswith(".svg"):
            os.remove(os.path.join(hedef, f))
    for dosya, ad, no, olc, fn in PAFTALAR:
        svg = fn()
        with open(os.path.join(hedef, dosya + ".svg"), "w", encoding="utf-8") as f:
            f.write(svg)
        print("%-20s %-4s %-28s %7d bayt" % (dosya, no, ad, len(svg)))
