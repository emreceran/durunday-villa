# -*- coding: utf-8 -*-
"""Mobilya / donatı kütüphanesi: ölçüler (m) ve plan sembolleri (SVG).
Dönüş 0°: sembolün sırtı kuzeyde (y küçük), yüzü güneye bakar. Dönüş saat yönünde (ekran koordinatı)."""
import math

# yerleşim kontrolünde çakışmaya sayılmayan (zemin) öğeler
ZEMIN_OGESI = {"hali", "yoga", "bitki", "perde"}

def olcu(tip, p):
    """(en, derinlik) — dönüş 0° iken x ve y boyunca."""
    if tip == "yatak_cift":   return (p + 1.0, 2.10)
    if tip == "yatak_tek":    return (1.00, 2.00)
    if tip in ("gardirop",):  return (p, 0.62)
    if tip == "koltuk":       return (0.85, 0.85)
    if tip == "berjer":       return (0.80, 0.80)
    if tip == "kanepe":       return (p, 0.95)
    if tip in ("kanepe_l", "sehpa", "hali", "ada", "ada_dolap", "dus"): return p
    if tip == "tv_unite":     return (p, 0.45)
    if tip == "yemek_masasi": return (2.60, 2.20) if p >= 8 else (1.80, 2.00)
    if tip == "bufe":         return (p, 0.50)
    if tip == "tezgah":       return (p, 0.62)
    if tip == "buzdolabi":    return (0.92, 0.72)
    if tip == "bar_tabure":   return (p * 0.55, 0.45)
    if tip == "araba":        return (1.90, 4.70)
    if tip == "wc":           return (0.40, 0.65)
    if tip == "lavabo":       return (p, 0.50)
    if tip == "kuvet":        return (1.70, 0.80)
    if tip == "kuvet_serbest":return (1.70, 0.80)
    if tip == "masa":         return (p, 1.20)
    if tip == "masa_yuvarlak":return (p + 0.9, p + 0.9)
    if tip == "kitaplik":     return (p, 0.35)
    if tip == "vestiyer":     return (p, 0.60)
    if tip == "piyano":       return (1.55, 0.62)
    if tip == "komodin_tv":   return (p, 0.45)
    if tip == "sinema_koltuk":return (p * 0.95, 0.95)
    if tip == "perde":        return (p, 0.10)
    if tip == "bilardo":      return (2.70, 1.50)
    if tip == "bar":          return (p, 0.65)
    if tip == "raf":          return (p, 0.45)
    if tip == "pano":         return (p, 0.30)
    if tip == "kazan":        return (0.60, 0.50)
    if tip == "boyler":       return (0.70, 0.70)
    if tip == "depo_tank":    return (2.00, 1.40)
    if tip == "filtre":       return (1.60, 1.00)
    if tip == "bank":         return (p, 0.45)
    if tip == "sauna_bank":   return (p, 0.90)
    if tip == "kosu":         return (0.85, 2.00)
    if tip == "agirlik":      return (1.20, 1.20)
    if tip == "yoga":         return (1.00, 2.00)
    if tip == "sarap_raf":    return (p, 0.40)
    if tip == "camasir":      return (0.60, 0.60)
    if tip == "utu":          return (1.30, 0.40)
    if tip == "bitki":        return (0.50, 0.50)
    raise KeyError(tip)

def sinir_kutusu(o):
    """Mobilyanın plan sınır kutusu (x0,y0,x1,y1)."""
    tip, cx, cy, rot, p = o
    w, d = olcu(tip, p)
    a = math.radians(rot)
    ex = abs(w / 2 * math.cos(a)) + abs(d / 2 * math.sin(a))
    ey = abs(w / 2 * math.sin(a)) + abs(d / 2 * math.cos(a))
    return (cx - ex, cy - ey, cx + ex, cy + ey)
