# -*- coding: utf-8 -*-
"""Durunday Villa — tek doğru kaynak (single source of truth).

Koordinatlar metre; x batı→doğu (0…20), y kuzey→güney (0…15). Kuzey cephe (y=0) imar yoluna bakar.
Mahal dikdörtgenleri aks ölçüsüdür: dış cephede dış yüz, iç duvarlarda duvar ekseni.
Dış duvar (35 cm) bina çizgisinin İÇİNDE kalır; ısı yalıtımı (8 cm) TAKS'a dahil değildir.

Buradan üretilir: kat planları, kesitler, görünüşler, vaziyet ve çatı planı (ciz.py),
mantık/yönetmelik kontrolü (kontrol.py, yonetmelik.py), Excel, web sitesi ve 3B model (render_3b.py).
"""

# ---------------------------------------------------------------- parsel / imar (VARSAYIM)
PARSEL = {
    "alan": 1001.0, "en": 26.0, "boy": 38.5,
    "taks": 0.30, "kaks": 0.60, "hmax": 6.50,
    "cekme_on": 5.0, "cekme_yan": 3.0, "cekme_arka": 3.0,
    "nizam": "Ayrık nizam, 2 kat (Yençok = 2, Hmax = 6,50 m)",
}
BINA = {"en": 20.0, "boy": 15.0}           # 20 × 15 = 300 m² oturum
BINA_KONUM = (3.0, 5.0)                    # parselde bina köşesi (batı yan bahçe 3,00 · ön bahçe 5,00)
DIS_DUVAR = 0.35
IC_DUVAR = 0.15
YALITIM = 0.08

# ---------------------------------------------------------------- kotlar
# ±0.00 = zemin kat bitmiş döşeme; tabii zemin (bahçe) −0.30
TABII_ZEMIN = -0.30
KOT = {"Bodrum": -3.06, "Zemin": 0.00, "1. Kat": 3.20, "Çatı": 6.20}
KAT_YUKSEKLIK = {"Bodrum": 3.06, "Zemin": 3.20, "1. Kat": 3.00}
DOSEME = 0.30                              # plak 20 cm + şap/kaplama 10 cm
NET_TAVAN = {"Bodrum": 2.66, "Zemin": 2.80, "1. Kat": 2.60}   # asma tavan altı
GARAJ_KOT = -0.17
CATI = {"egim": 0.30, "sacak": 0.80, "tip": "Kırma çatı, antrasit kil kiremit"}
KATLAR_SIRA = ["Bodrum", "Zemin", "1. Kat"]

# ---------------------------------------------------------------- taşıyıcı sistem
# Betonarme çerçeve + asansör perdesi. Kolonlar aks kesişimlerinde (40 × 40).
AKS_X = [("1", 0.0), ("2", 7.8), ("3", 12.6), ("4", 20.0)]
AKS_Y = [("A", 0.0), ("B", 5.2), ("C", 10.0), ("D", 15.0)]
KOLON = 0.40

def kolonlar():
    """Kolon merkezleri: aks kesişimleri. Dış akslarda kolon dış yüzü bina çizgisine oturur."""
    out = []
    for _, x in AKS_X:
        for _, y in AKS_Y:
            cx = min(max(x, KOLON / 2), BINA["en"] - KOLON / 2)
            cy = min(max(y, KOLON / 2), BINA["boy"] - KOLON / 2)
            out.append((cx, cy))
    return out

# ---------------------------------------------------------------- merdiven (U, iki kollu)
# Kutu x 10.00–12.60, y 3.20–8.00. Batı kol güneye çıkar, sahanlıkta döner, doğu kol kuzeye çıkar.
MERDIVEN = {
    "kutu": (10.0, 3.2, 12.6, 8.0),
    "bati_kol": (10.05, 11.25),            # x aralığı (net 1,20 m)
    "dogu_kol": (11.35, 12.525),           # x aralığı (net 1,175 m)
    "sahanlik": (6.675, 7.925),            # y aralığı (1,25 m)
    "basamak": 0.28,
    # kat: (alt kat, üst kat, rıht sayısı batı kol, rıht sayısı doğu kol)
    "kollar": {"Bodrum": ("Bodrum", "Zemin", 9, 9), "Zemin": ("Zemin", "1. Kat", 10, 9)},
}

def merdiven_kollari(kat):
    """Bu kattan yukarı çıkan kolların (x0,x1,y_bas,y_son,riht,yon) listesi."""
    if kat not in MERDIVEN["kollar"]:
        return None
    alt, ust, r1, r2 = MERDIVEN["kollar"][kat]
    h = KOT[ust] - KOT[alt]
    riht = h / (r1 + r2)
    s0 = MERDIVEN["sahanlik"][0]
    b = MERDIVEN["basamak"]
    k1 = (MERDIVEN["bati_kol"][0], MERDIVEN["bati_kol"][1], s0 - (r1 - 1) * b, s0, r1, +1)
    k2 = (MERDIVEN["dogu_kol"][0], MERDIVEN["dogu_kol"][1], s0, s0 - (r2 - 1) * b, r2, -1)
    return {"alt": alt, "ust": ust, "h": h, "riht": riht, "kollar": [k1, k2]}

ASANSOR = {"kuyu": (10.0, 8.0, 12.0, 10.2), "kabin": "630 kg · 8 kişi · 1,10 × 1,40 m", "durak": 3}

# ---------------------------------------------------------------- mahaller
# kod, ad, tip, [dikdörtgenler]
#   tip: yasam | yatak | islak | mutfak | sirkulasyon | giyinme | teknik | garaj | ikincil
#        merdiven | asansor | saft | bosluk
def M(kod, ad, tip, *rects):
    return {"kod": kod, "ad": ad, "tip": tip, "r": list(rects)}

KATLAR = {
"Bodrum": [
 M("B-01", "Ev sineması",                 "ikincil",     (0.0, 0.0, 7.8, 5.2)),
 M("B-02", "Oyun ve bar salonu",          "yasam",       (0.0, 5.2, 7.8, 10.0)),
 M("B-03", "Misafir / hizmetli odası",    "yatak",       (0.0, 10.0, 5.0, 15.0)),
 M("B-04", "Oda holü ve dolap",           "sirkulasyon", (5.0, 10.0, 7.8, 12.6)),
 M("B-05", "Oda banyosu",                 "islak",       (5.0, 12.6, 7.8, 15.0)),
 M("B-06", "Bodrum holü",                 "sirkulasyon", (7.8, 3.2, 10.0, 12.6)),
 M("B-07", "Merdiven",                    "merdiven",    (10.0, 3.2, 12.6, 8.0)),
 M("B-08", "Asansör",                     "asansor",     (10.0, 8.0, 12.0, 10.2)),
 M("B-09", "Tesisat şaftı",               "saft",        (12.0, 8.0, 12.6, 10.2)),
 M("B-10", "Genel depo",                  "teknik",      (7.8, 0.0, 12.6, 3.2)),
 M("B-11", "Elektrik ve zayıf akım odası","teknik",      (12.6, 0.0, 14.0, 3.2)),
 M("B-12", "Koridor",                     "sirkulasyon", (12.6, 3.2, 14.0, 9.8)),
 M("B-13", "Isı merkezi (kazan / ısı pompası)", "teknik", (14.0, 0.0, 17.4, 4.6)),
 M("B-14", "Su deposu ve hidrofor",       "teknik",      (17.4, 0.0, 20.0, 4.6)),
 M("B-15", "Kiler ve soğuk depo",         "teknik",      (14.0, 4.6, 20.0, 7.2)),
 M("B-16", "Havuz makine dairesi",        "teknik",      (14.0, 7.2, 20.0, 9.8)),
 M("B-17", "Soyunma ve duş",              "islak",       (12.6, 9.8, 15.4, 12.4)),
 M("B-18", "Sauna",                       "islak",       (12.6, 12.4, 15.4, 15.0)),
 M("B-19", "Fitness salonu",              "yasam",       (15.4, 9.8, 20.0, 15.0)),
 M("B-20", "Depo",                        "teknik",      (10.0, 10.2, 12.6, 12.6)),
 M("B-21", "Şarap mahzeni",               "ikincil",     (7.8, 12.6, 12.6, 15.0)),
],
"Zemin": [
 M("Z-01", "Antre / giriş holü",          "sirkulasyon", (7.8, 0.0, 14.0, 3.2)),
 M("Z-02", "Hol",                         "sirkulasyon", (7.8, 3.2, 10.0, 10.2)),
 M("Z-03", "Merdiven",                    "merdiven",    (10.0, 3.2, 12.6, 8.0)),
 M("Z-04", "Asansör",                     "asansor",     (10.0, 8.0, 12.0, 10.2)),
 M("Z-05", "Tesisat şaftı",               "saft",        (12.0, 8.0, 12.6, 10.2)),
 M("Z-06", "Misafir yatak odası",         "yatak",       (0.0, 0.0, 5.8, 5.2)),
 M("Z-07", "Misafir banyosu",             "islak",       (5.8, 0.0, 7.8, 3.2)),
 M("Z-08", "Misafir süit holü",           "sirkulasyon", (5.8, 3.2, 7.8, 5.2)),
 M("Z-09", "Salon (şömineli)",            "yasam",       (0.0, 5.2, 7.8, 15.0)),
 M("Z-10", "Yemek alanı",                 "yasam",       (7.8, 10.2, 12.6, 15.0)),
 M("Z-11", "Mutfak (adalı)",              "mutfak",      (12.6, 9.8, 20.0, 15.0)),
 M("Z-12", "Servis koridoru",             "sirkulasyon", (12.6, 3.2, 14.0, 9.8)),
 M("Z-13", "Garaj (2 araç)",              "garaj",       (14.0, 0.0, 20.0, 6.0)),
 M("Z-14", "Misafir WC",                  "islak",       (14.0, 6.0, 16.6, 7.8)),
 M("Z-15", "Kiler",                       "teknik",      (14.0, 7.8, 16.6, 9.8)),
 M("Z-16", "Arka mutfak / servis girişi", "mutfak",      (16.6, 6.0, 20.0, 9.8)),
],
"1. Kat": [
 M("K-01", "Üst hol ve okuma köşesi",     "sirkulasyon", (7.8, 3.2, 10.0, 10.2), (10.0, 0.0, 12.6, 3.2)),
 M("K-02", "Galeri boşluğu",              "bosluk",      (7.8, 0.0, 10.0, 3.2)),
 M("K-03", "Merdiven",                    "merdiven",    (10.0, 3.2, 12.6, 8.0)),
 M("K-04", "Asansör",                     "asansor",     (10.0, 8.0, 12.0, 10.2)),
 M("K-05", "Tesisat şaftı",               "saft",        (12.0, 8.0, 12.6, 10.2)),
 M("K-06", "Yatak odası 2",               "yatak",       (0.0, 0.0, 5.8, 5.2)),
 M("K-07", "Yatak odası 2 banyosu",       "islak",       (5.8, 0.0, 7.8, 3.2)),
 M("K-08", "Yatak odası 2 holü",          "sirkulasyon", (5.8, 3.2, 7.8, 5.2)),
 M("K-09", "Ebeveyn banyosu",             "islak",       (0.0, 5.2, 4.2, 10.0)),
 M("K-10", "Ebeveyn giyinme odası",       "giyinme",     (4.2, 5.2, 7.8, 10.0)),
 M("K-11", "Ebeveyn yatak odası",         "yatak",       (0.0, 10.0, 7.8, 15.0)),
 M("K-12", "Yatak odası 4",               "yatak",       (7.8, 10.2, 10.6, 15.0), (10.6, 12.8, 12.6, 15.0)),
 M("K-13", "Yatak odası 4 banyosu",       "islak",       (10.6, 10.2, 12.6, 12.8)),
 M("K-14", "Koridor",                     "sirkulasyon", (12.6, 0.0, 14.0, 9.8)),
 M("K-15", "Yatak odası 3",               "yatak",       (14.0, 0.0, 20.0, 4.6)),
 M("K-16", "Yatak odası 3 giyinme",       "giyinme",     (14.0, 4.6, 16.6, 7.2)),
 M("K-17", "Yatak odası 3 banyosu",       "islak",       (16.6, 4.6, 20.0, 7.2)),
 M("K-18", "Çamaşır ve ütü odası",        "islak",       (14.0, 7.2, 17.4, 9.8)),
 M("K-19", "Aile WC",                     "islak",       (17.4, 7.2, 20.0, 9.8)),
 M("K-20", "Aile oturma odası",           "yasam",       (12.6, 9.8, 20.0, 15.0)),
],
}

# duvarsız birleşen mahal çiftleri (açık plan / korkuluklu boşluk)
#   "acik": duvar yok · "korkuluk": duvar yerine 110 cm cam korkuluk
ACIK = {
"Bodrum": [("B-06", "B-07", "acik")],
"Zemin":  [("Z-01", "Z-02", "acik"), ("Z-01", "Z-03", "acik"), ("Z-01", "Z-12", "acik"),
           ("Z-02", "Z-03", "acik"), ("Z-02", "Z-10", "acik")],
"1. Kat": [("K-01", "K-02", "korkuluk"), ("K-01", "K-03", "acik"), ("K-01", "K-14", "acik")],
}
# merdiven boşluğu korkulukları (eksen, sabit, a, b) — merdivenin açık kenarları ve üst kat boşluğu
MERDIVEN_KORKULUK = {
"Bodrum": [("x", 10.0, 4.435, 7.925)],
"Zemin":  [("x", 10.0, 4.155, 7.925), ("x", 11.30, 4.435, 6.675)],
"1. Kat": [("x", 10.0, 4.435, 7.925), ("y", 4.435, 10.0, 11.30), ("x", 11.30, 4.435, 6.675)],
}

# ---------------------------------------------------------------- kapılar
# (eksen, sabit, a, b, tip, açıldığı mahal, menteşe ucu)
#   eksen "x": duvar x=sabit düşey çizgi, açıklık y∈[a,b];  "y": duvar y=sabit, açıklık x∈[a,b]
#   tip: kapi | cift | surme | gecis (kanatsız) | giris | garaj | yangin | servis | asansor | kapak
#   menteşe ucu: "a" veya "b" (açıklığın hangi ucunda menteşe)
#   açıldığı mahal "DIS" = dışarı
KAPILAR = {
"Bodrum": [
 ("x", 7.8, 3.55, 4.45, "kapi",  "B-01", "a"),      # sinema
 ("x", 7.8, 5.80, 7.40, "cift",  "B-02", "a"),      # oyun salonu
 ("x", 7.8, 10.65, 11.55, "kapi", "B-04", "b"),     # misafir odası holü
 ("x", 5.0, 10.75, 11.65, "kapi", "B-03", "a"),     # misafir odası
 ("y", 12.6, 5.50, 6.30, "kapi", "B-05", "b"),      # banyo
 ("y", 3.2, 8.40, 9.30, "kapi",  "B-10", "b"),      # genel depo
 ("x", 12.6, 3.35, 4.35, "gecis", None, None),      # merdiven ↔ koridor
 ("y", 3.2, 12.85, 13.75, "kapi", "B-11", "a"),     # pano odası
 ("x", 14.0, 3.55, 4.45, "yangin", "B-13", "b"),    # ısı merkezi (EI30)
 ("x", 17.4, 1.20, 2.10, "kapi", "B-14", "a"),      # su deposu
 ("x", 14.0, 5.40, 6.30, "kapi", "B-15", "a"),      # kiler
 ("x", 14.0, 8.00, 8.90, "kapi", "B-16", "a"),      # havuz makine
 ("y", 9.8, 12.85, 13.75, "kapi", "B-17", "b"),     # soyunma
 ("y", 12.4, 13.40, 14.20, "surme", None, None),    # sauna (cam)
 ("x", 15.4, 10.40, 11.30, "kapi", "B-19", "a"),    # fitness
 ("x", 10.0, 10.95, 11.85, "kapi", "B-20", "a"),    # depo
 ("y", 12.6, 8.40, 9.30, "kapi", "B-21", "a"),      # şarap mahzeni
 ("x", 10.0, 8.55, 9.55, "asansor", None, None),
 ("x", 12.6, 8.40, 9.00, "kapak", "B-12", "a"),     # şaft servis kapağı
],
"Zemin": [
 ("y", 0.0, 8.55, 9.65, "giris", "Z-01", "a"),      # villa giriş kapısı
 ("x", 7.8, 3.55, 4.45, "kapi",  "Z-08", "a"),      # misafir süit holü
 ("x", 5.8, 3.90, 4.80, "kapi",  "Z-06", "b"),      # misafir yatak
 ("y", 3.2, 6.00, 6.80, "kapi",  "Z-07", "a"),      # misafir banyo
 ("x", 7.8, 5.80, 7.40, "cift",  "Z-09", "a"),      # salon
 ("x", 7.8, 10.80, 14.20, "gecis", None, None),     # salon ↔ yemek
 ("x", 12.6, 10.40, 14.60, "gecis", None, None),    # yemek ↔ mutfak
 ("x", 10.0, 8.55, 9.55, "asansor", None, None),
 ("x", 12.6, 8.40, 9.00, "kapak", "Z-12", "a"),
 ("x", 14.0, 3.55, 4.45, "yangin", "Z-13", "b"),    # garaj (EI30, garaj tarafına açılır)
 ("y", 0.0, 14.60, 19.40, "garaj", None, None),     # seksiyonel garaj kapısı
 ("x", 14.0, 6.45, 7.25, "kapi",  "Z-14", "a"),     # misafir WC
 ("x", 14.0, 8.25, 9.15, "kapi",  "Z-15", "b"),     # kiler
 ("y", 9.8, 12.85, 13.75, "surme", None, None),     # koridor → mutfak
 ("y", 9.8, 17.40, 18.30, "kapi", "Z-16", "b"),     # arka mutfak
 ("x", 20.0, 6.55, 7.45, "servis", "Z-16", "a"),    # servis girişi (doğu yan bahçe)
],
"1. Kat": [
 ("x", 7.8, 3.55, 4.45, "kapi",  "K-08", "a"),
 ("x", 5.8, 3.90, 4.80, "kapi",  "K-06", "b"),
 ("y", 3.2, 6.00, 6.80, "kapi",  "K-07", "a"),
 ("x", 7.8, 5.70, 6.60, "kapi",  "K-10", "a"),      # ebeveyn süiti girişi (giyinme)
 ("x", 4.2, 8.60, 9.40, "kapi",  "K-09", "b"),      # ebeveyn banyosu
 ("y", 10.0, 4.60, 5.50, "kapi", "K-11", "a"),      # ebeveyn yatak
 ("y", 10.2, 8.95, 9.85, "kapi", "K-12", "b"),      # yatak 4
 ("x", 10.6, 11.60, 12.40, "kapi", "K-13", "b"),    # yatak 4 banyo
 ("x", 12.6, 3.35, 4.35, "gecis", None, None),      # merdiven ↔ koridor
 ("x", 10.0, 8.55, 9.55, "asansor", None, None),
 ("x", 12.6, 8.40, 9.00, "kapak", "K-14", "a"),
 ("x", 14.0, 1.20, 2.10, "kapi",  "K-15", "a"),     # yatak 3
 ("y", 4.6, 14.55, 15.45, "kapi", "K-16", "a"),     # yatak 3 giyinme
 ("x", 16.6, 5.00, 5.80, "kapi", "K-17", "a"),     # yatak 3 banyo (giyinmeden)
 ("x", 14.0, 8.00, 8.90, "kapi",  "K-18", "a"),     # çamaşır
 ("y", 9.8, 12.85, 13.75, "kapi", "K-20", "a"),     # aile oturma
 ("y", 9.8, 18.50, 19.30, "kapi", "K-19", "b"),     # aile WC
],
}

# ---------------------------------------------------------------- pencereler ve cephe kapıları
# (cephe, a, b, tip, denizlik, lento)   cephe: K(y=0) G(y=15) B(x=0) D(x=20); a,b cephe boyunca
#   tip: P pencere · S sürme cam kapı (lift & slide) · F sabit cam · Y yüksek (banyo, buzlu) · I ışıklık penceresi
PENCERELER = {
"Bodrum": [
 ("B", 5.90, 9.30, "I", 0.90, 2.30),     # oyun salonu → batı ışıklığı
 ("B", 11.00, 14.40, "I", 0.90, 2.30),   # misafir odası → batı ışıklığı
 ("D", 10.80, 14.20, "I", 0.90, 2.30),   # fitness → doğu ışıklığı
],
"Zemin": [
 ("K", 1.60, 4.20, "P", 1.00, 2.40),     # misafir yatak
 ("K", 6.30, 7.30, "Y", 1.60, 2.40),     # misafir banyo
 ("K", 10.20, 12.00, "F", 0.00, 2.40),   # antre yan camı
 ("B", 1.20, 3.80, "P", 1.00, 2.40),     # misafir yatak
 ("B", 6.00, 8.60, "P", 0.45, 2.40),     # salon
 ("B", 11.50, 14.10, "P", 0.45, 2.40),   # salon
 ("G", 1.20, 6.60, "S", 0.00, 2.60),     # salon → teras
 ("G", 8.40, 12.00, "S", 0.00, 2.60),    # yemek → teras
 ("G", 13.40, 18.80, "S", 0.00, 2.60),   # mutfak → pergola
 ("D", 10.80, 14.00, "P", 1.00, 2.40),   # mutfak tezgah üstü
 ("D", 7.80, 9.60, "P", 1.00, 2.40),     # arka mutfak
 ("D", 2.40, 3.40, "Y", 1.60, 2.40),     # garaj
],
"1. Kat": [
 ("K", 1.60, 4.20, "P", 0.90, 2.30),     # yatak 2
 ("K", 6.30, 7.30, "Y", 1.50, 2.30),     # yatak 2 banyo
 ("K", 8.30, 9.70, "F", 0.00, 2.30),     # galeri camı (girişin üstü)
 ("K", 10.20, 12.00, "P", 0.90, 2.30),   # okuma köşesi
 ("K", 15.40, 18.60, "P", 0.90, 2.30),   # yatak 3
 ("B", 1.20, 3.80, "P", 0.90, 2.30),     # yatak 2
 ("B", 6.20, 8.60, "Y", 1.20, 2.30),     # ebeveyn banyosu (buzlu, geniş)
 ("B", 11.30, 13.90, "P", 0.90, 2.30),   # ebeveyn yatak
 ("G", 1.80, 6.00, "S", 0.00, 2.30),     # ebeveyn → balkon
 ("G", 8.60, 11.80, "P", 0.90, 2.30),    # yatak 4
 ("G", 13.40, 18.80, "S", 0.00, 2.30),   # aile oturma → balkon
 ("D", 1.00, 3.60, "P", 0.90, 2.30),     # yatak 3
 ("D", 5.70, 6.70, "Y", 1.50, 2.30),     # yatak 3 banyo
 ("D", 8.00, 9.00, "Y", 1.50, 2.30),     # aile WC
 ("D", 10.80, 14.00, "P", 0.90, 2.30),   # aile oturma
],
}

# ---------------------------------------------------------------- dış elemanlar
BALKONLAR = [   # 1. kat, güney cephe, konsol (açık çıkma ≤ 1,50 m)
    {"ad": "Ebeveyn balkonu", "x0": 0.60, "x1": 7.20, "derinlik": 1.50},
    {"ad": "Aile balkonu",    "x0": 13.20, "x1": 19.40, "derinlik": 1.50},
]
GIRIS_SACAGI = {"x0": 7.90, "x1": 12.40, "derinlik": 1.80}          # kuzey cephe, zemin
PERGOLA = {"x0": 12.60, "x1": 20.00, "y0": 15.0, "y1": 19.0}          # mutfak önü, alüminyum
TERAS = {"x0": 0.0, "x1": 20.0, "y0": 15.0, "y1": 19.0, "kot": -0.02}  # zemin kat güney terası
ISIKLIKLAR = [  # bodrum ışıklıkları (İngiliz bahçesi) — bina dışında, yan bahçede
    {"cephe": "B", "a": 5.60, "b": 9.60, "derinlik": 1.40},
    {"cephe": "B", "a": 10.60, "b": 14.60, "derinlik": 1.40},
    {"cephe": "D", "a": 10.40, "b": 14.60, "derinlik": 1.40},
]
BACA = {"cephe": "B", "a": 9.60, "b": 10.60, "derinlik": 0.60}       # salon şöminesi, dışa taşan taş kaplı baca
HAVUZ = {"x0": 6.0, "x1": 16.0, "y0": 23.0, "y1": 27.0}              # bina koordinatında (güney bahçe)
KAT_BOSLUGU_KAPAK = ("1. Kat", 13.30, 6.40)                           # çatı arası katlanır merdiven kapağı

# ---------------------------------------------------------------- mobilya (plan sembolleri)
# (tip, cx, cy, dönüş°, parametre)   dönüş 0: sembolün "sırtı" kuzeyde (y küçük tarafta)
MOBILYA = {
"Bodrum": [
 ("perde", 3.9, 0.55, 0, 3.6), ("sinema_koltuk", 3.9, 2.6, 180, 3), ("sinema_koltuk", 3.9, 3.9, 180, 3),
 ("bar", 2.1, 5.6, 0, 3.0), ("bilardo", 3.2, 7.9, 0, None), ("kanepe", 6.2, 9.45, 180, 2.2),
 ("yatak_cift", 2.3, 11.13, 0, 1.6), ("gardirop", 4.615, 13.2, 90, 1.8), ("masa", 1.2, 14.05, 180, 1.2),
 ("gardirop", 5.9, 10.385, 0, 1.6),
 ("wc", 7.2, 14.325, 180, None), ("lavabo", 5.9, 14.4, 180, 0.9), ("dus", 7.15, 13.35, 0, (1.0, 1.0)),
 ("raf", 10.2, 0.575, 0, 4.2), ("pano", 13.3, 0.5, 0, 1.2),
 ("kazan", 15.0, 0.6, 0, None), ("boyler", 16.3, 0.7, 0, None), ("depo_tank", 18.9, 3.3, 90, None),
 ("raf", 17.35, 4.9, 0, 4.4), ("raf", 17.35, 6.9, 180, 4.4),
 ("filtre", 17.0, 8.5, 0, None),
 ("gardirop", 14.55, 10.185, 0, 1.4), ("bank", 12.9, 11.55, 270, 1.4), ("dus", 14.8, 11.8, 0, (1.0, 1.0)),
 ("sauna_bank", 14.0, 14.2, 180, 2.4),
 ("kosu", 16.5, 12.4, 0, None), ("kosu", 17.7, 12.4, 0, None), ("agirlik", 19.0, 11.0, 0, None),
 ("yoga", 18.8, 13.8, 0, None),
 ("raf", 11.3, 12.3, 180, 2.3),
 ("sarap_raf", 10.2, 14.45, 180, 4.5), ("masa_yuvarlak", 11.2, 13.45, 0, 0.6),
],
"Zemin": [
 ("yatak_cift", 2.4, 4.075, 180, 1.8), ("gardirop", 5.415, 1.8, 90, 2.4), ("koltuk", 1.0, 1.0, 45, None),
 ("lavabo", 6.125, 1.0, 270, 0.8), ("wc", 7.4, 1.9, 90, None), ("dus", 7.14, 0.85, 0, (1.17, 1.0)),
 ("gardirop", 6.8, 4.815, 180, 1.8),
 ("vestiyer", 8.175, 1.6, 270, 2.2),
 ("piyano", 2.0, 5.585, 0, None),
 ("kanepe_l", 4.6, 10.1, 90, (3.4, 2.6)), ("berjer", 1.6, 8.2, 0, None), ("berjer", 1.6, 12.0, 180, None),
 ("sehpa", 2.3, 10.1, 90, (1.2, 0.7)), ("hali", 2.9, 10.1, 90, (4.0, 3.4)),
 ("yemek_masasi", 10.2, 12.3, 90, 8), ("bufe", 11.25, 10.525, 0, 2.2),
 ("tezgah", 19.34, 12.3, 90, 4.4), ("ada", 16.4, 12.3, 0, (3.0, 1.1)), ("bar_tabure", 16.4, 13.3, 0, 3),
 ("buzdolabi", 14.5, 10.235, 0, None), ("tezgah", 15.9, 10.185, 0, 1.8),
 ("araba", 16.0, 3.0, 0, None), ("araba", 18.5, 3.0, 0, None),
 ("wc", 16.2, 6.9, 90, None), ("lavabo", 15.3, 6.325, 0, 0.8),
 ("raf", 15.75, 8.1, 0, 1.4), ("raf", 15.75, 9.5, 180, 1.4),
 ("tezgah", 16.985, 7.9, 270, 3.3), ("raf", 18.3, 6.3, 0, 1.6),
 ("bitki", 8.4, 9.6, 0, None), ("bitki", 13.5, 0.7, 0, None),
],
"1. Kat": [
 ("yatak_cift", 2.4, 4.075, 180, 1.8), ("gardirop", 5.415, 1.8, 90, 2.4), ("masa", 3.0, 0.95, 0, 1.2),
 ("lavabo", 6.125, 1.0, 270, 0.8), ("wc", 7.4, 1.9, 90, None), ("dus", 7.14, 0.85, 0, (1.17, 1.0)),
 ("gardirop", 6.8, 4.815, 180, 1.8),
 ("kuvet_serbest", 1.3, 7.4, 90, None), ("lavabo", 3.875, 6.4, 90, 1.8), ("dus", 1.05, 9.375, 0, (1.4, 1.1)),
 ("wc", 2.4, 5.6, 0, None),
 ("gardirop", 4.585, 6.9, 270, 3.0), ("gardirop", 5.85, 5.585, 0, 1.9), ("gardirop", 7.415, 8.1, 90, 2.8),
 ("ada_dolap", 5.95, 7.8, 0, (1.0, 1.4)),
 ("yatak_cift", 6.675, 12.35, 90, 1.8), ("koltuk", 1.0, 11.2, 0, None), ("koltuk", 1.0, 13.2, 180, None),
 ("sehpa", 1.0, 12.2, 0, (0.5, 0.5)),
 ("yatak_cift", 8.925, 13.45, 270, 1.4), ("gardirop", 8.185, 11.25, 270, 1.8), ("masa", 11.6, 14.05, 180, 1.2),
 ("wc", 12.2, 12.3, 90, None), ("lavabo", 11.1, 10.525, 0, 0.7), ("dus", 12.025, 10.875, 0, (1.0, 1.2)),
 ("berjer", 10.75, 1.6, 180, None), ("berjer", 11.85, 1.6, 180, None), ("sehpa", 11.3, 0.8, 0, (0.5, 0.5)),
 ("yatak_cift", 17.4, 3.475, 180, 1.8), ("masa", 15.6, 0.95, 0, 1.2), ("berjer", 19.1, 0.9, 225, None),
 ("gardirop", 15.3, 6.815, 180, 2.3),
 ("kuvet", 18.2, 6.725, 0, None), ("wc", 19.325, 6.0, 90, None), ("lavabo", 18.3, 4.925, 0, 1.2),
 ("tezgah", 16.2, 9.415, 180, 2.2), ("camasir", 15.6, 9.425, 180, None), ("camasir", 16.25, 9.425, 180, None),
 ("utu", 15.7, 7.95, 0, None),
 ("wc", 19.325, 8.0, 90, None), ("lavabo", 18.0, 7.525, 0, 0.8),
 ("tv_unite", 16.6, 10.1, 0, 2.4), ("kanepe_l", 16.6, 12.4, 180, (3.6, 2.4)), ("sehpa", 16.6, 11.3, 0, (1.2, 0.6)),
 ("hali", 16.6, 12.0, 0, (3.8, 3.0)), ("masa", 13.6, 13.0, 0, 1.4), ("bitki", 19.3, 14.3, 0, None),
],
}

# ---------------------------------------------------------------- yardımcılar
def mahal(kod):
    for kat, liste in KATLAR.items():
        for m in liste:
            if m["kod"] == kod:
                return kat, m
    return None, None

def _duvar_yari(kenar_deger, sinir):
    return DIS_DUVAR if abs(kenar_deger - sinir) < 1e-6 else IC_DUVAR / 2

def ic_sinir(r):
    """Dikdörtgenin duvar içi (net) sınırları."""
    x0, y0, x1, y1 = r
    nx0 = x0 + (DIS_DUVAR if x0 <= 1e-6 else IC_DUVAR / 2)
    nx1 = x1 - (DIS_DUVAR if x1 >= BINA["en"] - 1e-6 else IC_DUVAR / 2)
    ny0 = y0 + (DIS_DUVAR if y0 <= 1e-6 else IC_DUVAR / 2)
    ny1 = y1 - (DIS_DUVAR if y1 >= BINA["boy"] - 1e-6 else IC_DUVAR / 2)
    return nx0, ny0, nx1, ny1

def net_alan(m):
    """(net alan, dar kenar, uzun kenar) — çok parçalı mahalde dar/uzun en büyük parçadan."""
    toplam, en_buyuk = 0.0, None
    for r in m["r"]:
        nx0, ny0, nx1, ny1 = ic_sinir(r)
        a = (nx1 - nx0) * (ny1 - ny0)
        toplam += a
        if en_buyuk is None or a > en_buyuk[0]:
            en_buyuk = (a, min(nx1 - nx0, ny1 - ny0), max(nx1 - nx0, ny1 - ny0))
    # çok parçalı mahalde parçalar arası duvar yok: ortak kenar payını geri ekle
    if len(m["r"]) > 1:
        for i in range(len(m["r"])):
            for j in range(i + 1, len(m["r"])):
                toplam += _ortak_pay(m["r"][i], m["r"][j])
    return round(toplam, 1), round(en_buyuk[1], 2), round(en_buyuk[2], 2)

def _ortak_pay(a, b):
    """İki parçanın ortak kenarındaki (duvar olmayan) yarım duvar şeritleri."""
    t = IC_DUVAR / 2
    if abs(a[2] - b[0]) < 1e-6 or abs(b[2] - a[0]) < 1e-6:
        l = min(a[3], b[3]) - max(a[1], b[1])
        return max(l, 0) * 2 * t
    if abs(a[3] - b[1]) < 1e-6 or abs(b[3] - a[1]) < 1e-6:
        l = min(a[2], b[2]) - max(a[0], b[0])
        return max(l, 0) * 2 * t
    return 0.0

KAPALI_DISI = ("bosluk", "merdiven", "asansor", "saft")

def kat_ozeti():
    """{kat: (net kullanım alanı, boşluk/dikey sirkülasyon alanı)}"""
    ozet = {}
    for kat, liste in KATLAR.items():
        kapali = sum(net_alan(m)[0] for m in liste if m["tip"] not in KAPALI_DISI)
        diger = sum(net_alan(m)[0] for m in liste if m["tip"] in KAPALI_DISI)
        ozet[kat] = (round(kapali, 1), round(diger, 1))
    return ozet

if __name__ == "__main__":
    import itertools
    for kat, liste in KATLAR.items():
        rects = [(m["kod"], r) for m in liste for r in m["r"]]
        toplam = sum((r[2] - r[0]) * (r[3] - r[1]) for _, r in rects)
        cakisma = [(a[0], b[0]) for a, b in itertools.combinations(rects, 2)
                   if a[1][0] < b[1][2] - 1e-6 and b[1][0] < a[1][2] - 1e-6
                   and a[1][1] < b[1][3] - 1e-6 and b[1][1] < a[1][3] - 1e-6]
        k, d = kat_ozeti()[kat]
        print("%-7s aks toplamı %6.1f m² (hedef 300) | çakışma: %s | net kullanım %6.1f m² + dikey/boşluk %4.1f m²"
              % (kat, toplam, cakisma or "yok", k, d))
    for kat in ("Bodrum", "Zemin"):
        mk = merdiven_kollari(kat)
        print("merdiven %s→%s: h=%.2f · %d rıht · rıht %.2f cm · 2r+b = %.1f cm"
              % (mk["alt"], mk["ust"], mk["h"], mk["kollar"][0][4] + mk["kollar"][1][4],
                 mk["riht"] * 100, 2 * mk["riht"] * 100 + 28))
