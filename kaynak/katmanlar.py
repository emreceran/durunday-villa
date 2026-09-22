# -*- coding: utf-8 -*-
"""DXF katman şeması — ÇŞB "CADD Bilgisayar Destekli Tasarım ve Çizim Düzenleme Usul ve Esasları"
(Yapı İşleri GM, 2016 / rev. 2020) mimari katmanları.

Ad formülü M-ÖĞE(4)-MALZEME; tarama aynı adın sonuna "-T"; görünüş/kesitte görünen (kesilmeyen)
elemanlar derinliğe göre "-1" (en yakın) … "-4". Renk (ACI), çizgi tipi ve 1/100 kalem kalınlığı
Tablo 3.8–3.9'dan. "kaynak" sütunu: ÇŞB = tablodan birebir; TÜRETİLMİŞ = listede olmayan eleman için
aynı formülle üretilmiş ad. Not: 1 Eylül 2028'de yürürlüğe girecek dijital proje yönetmeliğinde
mimari önek "MM-" olacak (ÖNEK değiştirilerek üretilebilir).
"""
ONEK = "M"

# ad: (ACI renk, çizgi tipi, kalınlık mm (1/100), açıklama, kaynak, yazdır)
K = {
 "TASI-BETONARME":  (5,   "Continuous", 0.35, "Betonarme kolon, perde, kiriş, döşeme, temel (kesilen)", "ÇŞB", 1),
 "DUVA-GAZBETON":   (64,  "Continuous", 0.20, "Gazbeton duvar (dış 25 cm, iç 13,5 cm)", "ÇŞB", 1),
 "ISYA-TASYUNU":    (251, "Continuous", 0.09, "Isı yalıtımı (taşyünü / XPS) ve su yalıtımı", "ÇŞB (ISYA)", 1),
 "SIVA":            (52,  "Continuous", 0.05, "Sıva (cephe: ince silikon sıva)", "ÇŞB", 1),
 "SAPP-CIMENTO":    (53,  "Continuous", 0.09, "Şap", "ÇŞB", 1),
 "ZMNK-SERAMIK":    (250, "Continuous", 0.05, "Zemin kaplama: porselen / seramik", "ÇŞB", 1),
 "ZMNK-DOGALTAS":   (121, "Continuous", 0.05, "Zemin kaplama: traverten / doğal taş", "ÇŞB", 1),
 "DUVK-DOGALTAS":   (139, "Continuous", 0.05, "Duvar/cephe kaplama: Sille taşı, subasman yontma taş", "ÇŞB", 1),
 "DUVK-AHSAP":      (126, "Continuous", 0.05, "Cephe ahşap kompozit kaplama", "TÜRETİLMİŞ", 1),
 "DUVK-PREKAST":    (127, "Continuous", 0.05, "Kat silmesi (prekast / GRC)", "TÜRETİLMİŞ", 1),
 "KPKN-AHSAP":      (93,  "Continuous", 0.09, "Kapı kanadı", "ÇŞB", 1),
 "KPKS-AHSAP":      (160, "Continuous", 0.09, "Kapı kasası", "ÇŞB", 1),
 "PNKS-ALUMINYUM":  (171, "Continuous", 0.09, "Pencere / doğrama kasası ve kanadı (alüminyum)", "ÇŞB", 1),
 "CAMM":            (9,   "Continuous", 0.05, "Cam", "ÇŞB", 1),
 "KORK-CAM":        (100, "Continuous", 0.09, "Cam korkuluk ve küpeşte", "ÇŞB", 1),
 "MERD-BETONARME":  (6,   "Continuous", 0.18, "Merdiven kolları, basamaklar, sahanlık", "ÇŞB", 1),
 "TEFR-MIMARI":     (29,  "Continuous", 0.09, "Mobilya / tefriş", "ÇŞB", 1),
 "TEFR-MEKANIK":    (238, "Continuous", 0.09, "Vitrifiye, mutfak ve mekanik ekipman, asansör", "ÇŞB", 1),
 "BACA-TUGLA":      (116, "Continuous", 0.09, "Baca ve şömine", "ÇŞB", 1),
 "CKAP-KIREMIT":    (66,  "Continuous", 0.09, "Çatı kaplama (kil kiremit), mahya, dere", "ÇŞB", 1),
 "CKAP-METAL":      (67,  "Continuous", 0.09, "Metal çatı: biyoklimatik pergola lamelleri", "ÇŞB", 1),
 "CKAP-YESILCATI":  (68,  "Continuous", 0.09, "Yeşil çatı (giriş saçağı)", "TÜRETİLMİŞ", 1),
 "CTAS-AHSAP":      (234, "Continuous", 0.20, "Çatı taşıyıcı (ahşap dikme, mahya kirişi)", "ÇŞB", 1),
 "OLUK-SAC":        (194, "Continuous", 0.09, "Oluk ve alın", "ÇŞB", 1),
 "YIBO-SAC":        (12,  "Continuous", 0.09, "Yağmur iniş borusu", "ÇŞB", 1),
 "KALD-TAS":        (45,  "Continuous", 0.09, "Dış zemin: teras, giriş sahanlığı, basamaklar", "ÇŞB", 1),
 "YOLL-ASFALT":     (54,  "Continuous", 0.09, "İmar yolu", "ÇŞB", 1),
 "YOLL-TAS":        (54,  "Continuous", 0.09, "Araç yolu, bahçe yolları (granit küp taş)", "ÇŞB", 1),
 "TRET-BETON":      (45,  "Continuous", 0.09, "Tretuvar", "ÇŞB", 1),
 "CVRE-GENEL":      (45,  "Continuous", 0.09, "Komşu parseller, çevre", "ÇŞB", 1),
 "CVRE-ZEMIN":      (45,  "Continuous", 0.18, "Doğal zemin / toprak (kesit ve görünüş)", "TÜRETİLMİŞ", 1),
 "BITK-AGAC":       (70,  "Continuous", 0.09, "Ağaçlar, selviler", "ÇŞB", 1),
 "BITK-CIM":        (70,  "Continuous", 0.09, "Çim alanlar", "ÇŞB", 1),
 "HAVU-BETONARME":  (4,   "Continuous", 0.18, "Havuz", "TÜRETİLMİŞ", 1),
 "ISIK-GALVANIZ":   (150, "Continuous", 0.09, "Bodrum ışıklıkları ve galvaniz ızgara", "TÜRETİLMİŞ", 1),
 "SAFT-TESISAT":    (8,   "Continuous", 0.09, "Tesisat şaftı", "TÜRETİLMİŞ", 1),
 "GOST-AKS":        (1,   "ACAD_ISO04W100", 0.09, "Aks çizgileri", "ÇŞB", 1),
 "GOST-AKSPOZ":     (1,   "Continuous", 0.09, "Aks balonları", "TÜRETİLMİŞ", 1),
 "GOST-DISOLCU":    (40,  "Continuous", 0.09, "Dış ölçüler (ölçü nesneleri)", "ÇŞB", 1),
 "GOST-ICOLCU":     (44,  "Continuous", 0.09, "İç ölçüler (ölçü nesneleri)", "ÇŞB", 1),
 "GOST-PLANKOT":    (46,  "Continuous", 0.09, "Plan kotları", "ÇŞB", 1),
 "GOST-KESITKOT":   (46,  "Continuous", 0.09, "Kesit ve görünüş kotları", "ÇŞB", 1),
 "GOST-TZKTK":      (7,   "Continuous", 0.09, "Tabii zemin ve tesviye kotları (vaziyet)", "ÇŞB", 1),
 "GOST-MAHALPOZ":   (7,   "Continuous", 0.09, "Mahal adı, numarası, alanı, kaplaması", "ÇŞB", 1),
 "GOST-KAPIPOZ":    (95,  "Continuous", 0.09, "Kapı poz etiketleri", "ÇŞB", 1),
 "GOST-PENCEREPOZ": (62,  "Continuous", 0.09, "Pencere poz etiketleri", "ÇŞB", 1),
 "GOST-MERDIVEPOZ": (145, "Continuous", 0.09, "Merdiven çıkış oku, basamak numaraları", "ÇŞB", 1),
 "GOST-ACYONU":     (248, "ACAD_ISO07W100", 0.09, "Kapı açılım yayı", "ÇŞB", 1),
 "GOST-IZDUSUM":    (80,  "ACAD_ISO07W100", 0.18, "Üstte kalan / görünmeyen izdüşüm (saçak, pergola, üst kol)", "ÇŞB", 1),
 "GOST-KESITHATTI": (240, "ACAD_ISO04W100", 0.18, "Kesit hattı ve okları", "ÇŞB", 1),
 "GOST-PARSELSINR": (21,  "ACAD_ISO03W100", 0.18, "Parsel sınırı / bahçe duvarı", "ÇŞB", 1),
 "GOST-YAPIYAKLAS": (35,  "ACAD_ISO02W100", 0.15, "Yapı yaklaşma sınırı (çekme mesafeleri)", "ÇŞB", 1),
 "GOST-BINAOTURUM": (7,   "Continuous", 0.30, "Vaziyette bina oturumu ve çatı izi", "TÜRETİLMİŞ", 1),
 "GOST-KUZEYOKU":   (1,   "Continuous", 0.09, "Kuzey oku", "ÇŞB", 1),
 "GOST-YAZI":       (2,   "Continuous", 0.09, "Genel yazılar, başlıklar, malzeme notları", "ÇŞB", 1),
 "GOST-TABLO":      (1,   "Continuous", 0.09, "Doğrama listesi, pafta listesi, alan tabloları", "ÇŞB", 1),
 "GOST-GENEL":      (81,  "Continuous", 0.09, "Diğer gösterimler (ölçek insanı vb.)", "ÇŞB", 1),
 "GOST-LEJANT":     (173, "Continuous", 0.09, "Lejant sembolleri", "ÇŞB", 1),
 "GOST-ANTET":      (176, "Continuous", 0.25, "Pafta çerçevesi ve antet (layout)", "ÇŞB", 1),
 "GOST-ANTETYAZI":  (177, "Continuous", 0.09, "Antet yazıları, notlar, pafta başlıkları (layout)", "ÇŞB", 1),
 "GOST-VPORT":      (8,   "Continuous", 0.09, "Viewport çerçeveleri — yazdırılmaz", "TÜRETİLMİŞ", 0),
}

# anlamsal anahtar (çizim kodundaki) → katman
ANAHTAR = {
 "DUVAR": "DUVA-GAZBETON", "PERDE": "TASI-BETONARME", "KOLON": "TASI-BETONARME", "BETONARME": "TASI-BETONARME",
 "DOSEME-KESIT": "TASI-BETONARME", "CEPHE": "TASI-BETONARME",
 "DUVAR-TARAMA": "DUVA-GAZBETON-T", "PERDE-TARAMA": "TASI-BETONARME-T", "KOLON-TARAMA": "TASI-BETONARME-T",
 "BETONARME-TARAMA": "TASI-BETONARME-T",
 "YALITIM": "ISYA-TASYUNU", "DOSEME-KAPLAMA": "ZMNK-SERAMIK",
 "KAPI": "KPKN-AHSAP", "KAPI-KASA": "KPKS-AHSAP", "KAPI-YAY": "GOST-ACYONU", "PENCERE": "PNKS-ALUMINYUM",
 "GORUNEN": "PNKS-ALUMINYUM-2", "KORKULUK": "KORK-CAM", "MERDIVEN": "MERD-BETONARME", "MERDIVEN-GOR": "MERD-BETONARME-2",
 "MOBILYA": "TEFR-MIMARI", "VITRIFIYE": "TEFR-MEKANIK", "ASANSOR": "TEFR-MEKANIK", "BACA": "BACA-TUGLA",
 "CATI": "CKAP-KIREMIT", "CATI-GOR": "CKAP-KIREMIT-2", "CATI-TASIYICI": "CTAS-AHSAP", "OLUK": "OLUK-SAC", "YIBO": "YIBO-SAC",
 "DIS-MEKAN": "KALD-TAS", "YOL": "YOLL-ASFALT", "YOL-BAHCE": "YOLL-TAS", "CEVRE": "CVRE-GENEL", "ZEMIN": "CVRE-ZEMIN",
 "AGAC": "BITK-AGAC", "PEYZAJ": "BITK-AGAC", "CIM": "BITK-CIM", "HAVUZ": "HAVU-BETONARME", "ISIKLIK": "ISIK-GALVANIZ",
 "SAFT": "SAFT-TESISAT", "CEPHE-TAS": "DUVK-DOGALTAS", "CEPHE-SUBASMAN": "DUVK-DOGALTAS", "CEPHE-AHSAP": "DUVK-AHSAP",
 "CEPHE-SILME": "DUVK-PREKAST", "CEPHE-SIVA": "SIVA",
 "AKS": "GOST-AKS", "AKS-BALON": "GOST-AKSPOZ", "OLCU": "GOST-DISOLCU", "OLCU-IC": "GOST-ICOLCU",
 "KOT": "GOST-PLANKOT", "KOT-DUSEY": "GOST-KESITKOT", "KOT-TZ": "GOST-TZKTK", "MAHAL-YAZI": "GOST-MAHALPOZ",
 "KAPI-POZ": "GOST-KAPIPOZ", "PENCERE-POZ": "GOST-PENCEREPOZ", "MERDIVEN-POZ": "GOST-MERDIVEPOZ",
 "USTTE": "GOST-IZDUSUM", "KESIT-HATTI": "GOST-KESITHATTI", "PARSEL": "GOST-PARSELSINR", "CEKME": "GOST-YAPIYAKLAS",
 "BINA-IZ": "GOST-BINAOTURUM", "KUZEY": "GOST-KUZEYOKU", "YAZI": "GOST-YAZI", "TABLO": "GOST-TABLO",
 "GENEL": "GOST-GENEL", "INSAN": "GOST-GENEL", "LEJANT": "GOST-LEJANT", "ANTET": "GOST-ANTET",
 "PAFTA-YAZI": "GOST-ANTETYAZI", "VIEWPORT": "GOST-VPORT",
}
# desen (SVG) → tarama katmanı (bağlamdan bağımsız, "güçlü" malzemeler) ve bağlamı tarama katmanı olmayanlar için yedek
DESEN_KATMAN = {
 "p-yalitim": "ISYA-TASYUNU", "p-toprak": "CVRE-ZEMIN", "p-beton": "TASI-BETONARME", "p-su": "HAVU-BETONARME",
 "p-saft": "SAFT-TESISAT", "p-izgara": "ISIK-GALVANIZ", "p-fayans": "ZMNK-SERAMIK", "p-tas": "ZMNK-DOGALTAS",
 "p-dis-tas": "KALD-TAS", "p-duvar": "DUVA-GAZBETON", "p-kiremit": "CKAP-KIREMIT", "p-kiremit-g": "CKAP-KIREMIT",
 "p-sille": "DUVK-DOGALTAS", "p-ahsap": "DUVK-AHSAP", "p-siva": "SIVA", "p-cim": "BITK-CIM",
}
GUCLU = {"p-yalitim", "p-toprak", "p-beton", "p-su", "p-saft", "p-izgara", "p-fayans", "p-tas"}
TARAMALI = {"TASI-BETONARME", "DUVA-GAZBETON", "ISYA-TASYUNU", "ZMNK-SERAMIK", "ZMNK-DOGALTAS", "DUVK-DOGALTAS",
            "DUVK-AHSAP", "KALD-TAS", "YOLL-TAS", "CVRE-ZEMIN", "HAVU-BETONARME", "ISIK-GALVANIZ", "SAFT-TESISAT",
            "CKAP-KIREMIT", "BACA-TUGLA", "MERD-BETONARME", "SIVA", "DUVK-PREKAST", "CKAP-YESILCATI"}


def ad(k):
    return "%s-%s" % (ONEK, k)


def ozellik(tam):
    """Tam katman adı (önek dahil) → (renk, tip, kalınlık, açıklama, kaynak, yazdır); türevleri çözer."""
    k = tam[len(ONEK) + 1:]
    tarama = k.endswith("-T")
    if tarama:
        k = k[:-2]
    derin = None
    if k[-2:] in ("-1", "-2", "-3", "-4"):
        derin = int(k[-1]); k = k[:-2]
    renk, tip, kal, acik, kay, yaz = K[k]
    if derin:
        kal = max(0.05, {1: kal, 2: 0.09, 3: 0.05, 4: 0.05}[derin]) if not tarama else kal
        acik += " — görünüşte görünen (derinlik %d)" % derin
    if tarama:
        renk = 250 if k == "TASI-BETONARME" else 8
        tip, kal = "Continuous", 0.05
        acik += " — tarama"
        kay = kay + " (-T kuralı)"
    return renk, tip, kal, acik, kay, yaz


_SAYI = ("ANTET", "PAFTA-YAZI", "KUZEY", "LEJANT", "VIEWPORT")
_ACIKLAMA = {"AKS", "AKS-BALON", "OLCU", "OLCU-IC", "KOT", "KOT-DUSEY", "KOT-TZ", "MAHAL-YAZI", "KAPI-POZ", "PENCERE-POZ",
             "MERDIVEN-POZ", "USTTE", "KESIT-HATTI", "PARSEL", "CEKME", "BINA-IZ", "YAZI", "TABLO", "GENEL", "INSAN"} | set(_SAYI)


def cozumle(r, g):
    """Kayıt → tam katman adı. g: görünüş (None = kâğıt alanı)."""
    key = r["katman"]
    tur = r["tur"]
    dusey = g is not None and g["tur"] == "dusey"
    gorunus = g is not None and g["ad"].startswith("gorunus_icerik")
    if g is None:
        if tur == "yazi" and key != "TABLO":
            return ad(ANAHTAR["PAFTA-YAZI"])
        if key in ("LEJANT", "KUZEY", "ANTET", "PAFTA-YAZI"):
            return ad(ANAHTAR[key])
        if key not in ("TABLO", "PENCERE", "KAPI", "KAPI-KASA", "KAPI-YAY"):
            key = "ANTET"
    if key is None:
        key = _tahmin(r, g)
    # yazılar: malzeme katmanında yazı olmaz
    if tur == "yazi" and key not in _ACIKLAMA and key not in ("TABLO",):
        key = {"MERDIVEN": "MERDIVEN-POZ", "MERDIVEN-GOR": "MERDIVEN-POZ", "DUVAR": "MAHAL-YAZI" if dusey else "YAZI",
               "KAPI": "KAPI-POZ"}.get(key, "YAZI")
    if key == "KOT" and dusey:
        key = "KOT-DUSEY"
    if key == "KAPI" and r.get("yol"):
        key = "KAPI-YAY"
    # kesikli çizgi: planda üstte kalan eleman
    if tur == "cizgi" and r.get("dash") and not dusey and key in ("DIS-MEKAN", "KAPI", "MERDIVEN", "GENEL", "CATI",
                                                                 "BINA-IZ", "DUVAR", "PENCERE", "YALITIM", "MOBILYA"):
        key = "USTTE"
    if tur == "cizgi" and r.get("renk") == "#7dd3fc":
        key = "KORKULUK"
    base = ANAHTAR.get(key, key if key in K else "GOST-GENEL")
    # tarama / dolgu
    if tur == "tarama" and key in _ACIKLAMA:
        pass
    elif tur == "tarama":
        d = r["desen"]
        taban = base[:-2] if base.endswith("-T") else base
        cekirdek = taban.rsplit("-", 1)[0] if taban[-2:] in ("-1", "-2") else taban
        if d in GUCLU or cekirdek not in TARAMALI:
            taban = DESEN_KATMAN.get(d, "GOST-GENEL")
            if gorunus and taban not in ("CVRE-ZEMIN",):
                taban += "-1"
        base = taban + "-T"
    elif tur == "dolgu":
        taban = base[:-2] if base.endswith("-T") else base
        cekirdek = taban.rsplit("-", 1)[0] if taban[-2:] in ("-1", "-2") else taban
        if key not in _ACIKLAMA and cekirdek in TARAMALI:
            base = taban + "-T"
    if gorunus and not base.startswith("GOST") and base[-2:] not in ("-1", "-2") and not base.endswith(("-1-T", "-2-T")) \
            and not base.startswith("CVRE-ZEMIN"):
        base = base[:-2] + "-1-T" if base.endswith("-T") else base + "-1"
    return ad(base)


def _tahmin(r, g):
    if r["tur"] == "yazi":
        return "YAZI"
    if r["tur"] == "tarama":
        return "GENEL"
    if g is not None and g["tur"] == "plan" and r["tur"] == "cizgi" and r.get("sw", 0) >= 0.45:
        return "DUVAR"
    if r["tur"] == "dolgu":
        return "BETONARME"
    return "GENEL"


def katman_listesi():
    """(ad, renk, tip, kalınlık, açıklama, kaynak, yazdır) — lejant tablosu için."""
    return [(ad(k),) + v for k, v in K.items()]
