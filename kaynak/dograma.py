# -*- coding: utf-8 -*-
"""Pencere ve kapı tip kodları (doğrama listesi ile plan etiketleri ortak kullanır)."""
from veri import KATLAR_SIRA, KAPILAR, PENCERELER

def pencere_tipleri():
    """[(kod, tip, en, yükseklik, denizlik, [(kat, kayıt)...])]"""
    gruplar = {}
    for kat in KATLAR_SIRA:
        for p in PENCERELER[kat]:
            anahtar = (p[3], round(p[2] - p[1], 2), round(p[5] - p[4], 2))
            gruplar.setdefault(anahtar, []).append((kat, p))
    sira = {"S": 0, "P": 1, "F": 2, "Y": 3, "I": 4}
    out = []
    for i, (k, v) in enumerate(sorted(gruplar.items(), key=lambda kv: (sira[kv[0][0]], -kv[0][1]))):
        out.append(("%s%02d" % ("S" if k[0] == "S" else "P", i + 1), k[0], k[1], k[2], min(q[4] for _, q in v), v))
    return out

KAPI_YUKSEKLIK = {"kapi": 2.10, "yangin": 2.10, "giris": 2.40, "servis": 2.10, "cift": 2.40, "surme": 2.40,
                  "gecis": 2.40, "garaj": 2.40, "asansor": 2.10, "kapak": 0.60}
KAPI_AD = {"kapi": "Lake iç kapı (kanatlı)", "yangin": "Yangın kapısı EI30, kendiliğinden kapanır",
           "giris": "Villa giriş kapısı (çelik, ahşap kaplama)", "servis": "Servis dış kapısı (ısı yalıtımlı)",
           "cift": "Çift kanatlı cam panelli kapı", "surme": "Duvar içi sürme kapı",
           "garaj": "Seksiyonel garaj kapısı (motorlu)", "asansor": "Asansör kat kapısı (teleskopik)",
           "kapak": "Şaft servis kapağı", "gecis": "Kanatsız geçiş"}

def kapi_tipleri():
    gruplar = {}
    for kat in KATLAR_SIRA:
        for k in KAPILAR[kat]:
            if k[4] == "gecis":
                continue
            anahtar = (k[4], round(k[3] - k[2], 2))
            gruplar.setdefault(anahtar, []).append((kat, k))
    sira = ["giris", "servis", "garaj", "cift", "kapi", "yangin", "surme", "asansor", "kapak"]
    out = []
    for i, (k, v) in enumerate(sorted(gruplar.items(), key=lambda kv: (sira.index(kv[0][0]), -kv[0][1]))):
        out.append(("K%02d" % (i + 1), k[0], k[1], KAPI_YUKSEKLIK[k[0]], v))
    return out


def pencere_kodu(kat, p):
    for kod, tip, en, yuk, den, liste in pencere_tipleri():
        if (kat, p) in liste:
            return kod

def kapi_kodu(kat, k):
    for kod, tip, en, yuk, liste in kapi_tipleri():
        if (kat, k) in liste:
            return kod
