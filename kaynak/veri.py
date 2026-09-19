# -*- coding: utf-8 -*-
"""Durunday Villa — tek doğru kaynak (single source of truth).
Kat planı geometrisi, mahal listesi, imalat tanımları ve marka seçimleri burada.
Tüm çizimler, Excel ve web sitesi bu dosyadan üretilir."""

# ---------------------------------------------------------------- parsel / imar
PARSEL = {
    "alan": 1001.0, "en": 26.0, "boy": 38.5,
    "taks": 0.30, "kaks": 0.60,
    "cekme_on": 5.0, "cekme_yan": 3.0, "cekme_arka": 3.0,
    "nizam": "Ayrık nizam, 2 kat (B+2+Ç)",
}
BINA = {"en": 20.0, "boy": 15.0}          # 20 × 15 = 300 m² oturum
DIS_DUVAR = 0.35
IC_DUVAR = 0.15
KAT_YUKSEKLIK = {"Bodrum": 2.90, "Zemin": 3.20, "1. Kat": 3.10}
NET_TAVAN = {"Bodrum": 2.55, "Zemin": 2.85, "1. Kat": 2.75}

# ---------------------------------------------------------------- mahaller
# (kod, ad, x0, y0, x1, y1, tip)
#   tip: yasam | yatak | islak | mutfak | sirkulasyon | teknik | acik
KATLAR = {
"Bodrum": [
 ("B-01","Garaj (3 araçlık)",              0.0, 0.0,  8.6,  6.0, "teknik"),
 ("B-02","Hobi ve oyun salonu",            0.0, 6.0,  8.6, 11.4, "yasam"),
 ("B-03","Ev sineması",                    0.0,11.4,  8.6, 15.0, "yasam"),
 ("B-04","Kazan dairesi / teknik hacim",   8.6, 0.0, 12.0,  3.8, "teknik"),
 ("B-05","Merdiven ve hol",                8.6, 3.8, 12.0,  9.4, "sirkulasyon"),
 ("B-06","Çamaşırhane ve ütü odası",       8.6, 9.4, 12.0, 11.4, "islak"),
 ("B-07","Depo",                           8.6,11.4, 12.0, 13.0, "teknik"),
 ("B-08","Kiler / soğuk oda",              8.6,13.0, 12.0, 15.0, "teknik"),
 ("B-09","Su deposu ve hidrofor",         12.0, 0.0, 14.6,  2.6, "teknik"),
 ("B-10","Elektrik panosu / depo",        12.0, 2.6, 14.6,  3.8, "teknik"),
 ("B-11","Asansör ve tesisat şaftı",      12.0, 3.8, 14.6,  6.0, "teknik"),
 ("B-12","WC + duş",                      12.0, 6.0, 14.6,  7.8, "islak"),
 ("B-13","Koridor",                       12.0, 7.8, 14.6,  9.4, "sirkulasyon"),
 ("B-14","Şarap mahzeni ve bar",          12.0, 9.4, 14.6, 15.0, "ikincil"),
 ("B-15","Spor salonu (fitness)",         14.6, 0.0, 20.0,  3.8, "yasam"),
 ("B-16","Sauna ve dinlenme",             14.6, 3.8, 17.6,  7.6, "islak"),
 ("B-17","Soyunma ve duş",                17.6, 3.8, 20.0,  7.6, "islak"),
 ("B-18","Hizmet / misafir odası",        14.6, 7.6, 17.6, 11.4, "yatak"),
 ("B-19","Hizmet banyosu",                17.6, 7.6, 20.0, 10.0, "islak"),
 ("B-20","Temizlik deposu",               17.6,10.0, 20.0, 11.4, "teknik"),
 ("B-21","Işıklık / İngiliz bahçesi",     14.6,11.4, 20.0, 15.0, "acik"),
],
"Zemin": [
 ("Z-01","Salon / oturma alanı",           0.0, 0.0,  8.6,  7.6, "yasam"),
 ("Z-02","Yemek alanı",                    0.0, 7.6,  8.6, 11.4, "yasam"),
 ("Z-03","Kapalı veranda",                 0.0,11.4,  8.6, 15.0, "yasam"),
 ("Z-04","Antre / giriş holü",             8.6, 0.0, 12.0,  3.8, "sirkulasyon"),
 ("Z-05","Merdiven, hol ve galeri",        8.6, 3.8, 12.0,  9.4, "sirkulasyon"),
 ("Z-06","Mutfak (ankastre)",              8.6, 9.4, 14.6, 13.0, "mutfak"),
 ("Z-07","Kiler / arka mutfak",            8.6,13.0, 14.6, 15.0, "mutfak"),
 ("Z-08","Misafir WC",                    12.0, 0.0, 14.6,  2.6, "islak"),
 ("Z-09","Vestiyer",                      12.0, 2.6, 14.6,  3.8, "teknik"),
 ("Z-10","Asansör ve tesisat şaftı",      12.0, 3.8, 14.6,  6.0, "teknik"),
 ("Z-11","Koridor",                       12.0, 6.0, 14.6,  9.4, "sirkulasyon"),
 ("Z-12","Misafir yatak odası (süit)",    14.6, 0.0, 20.0,  3.8, "yatak"),
 ("Z-13","Misafir banyosu",               14.6, 3.8, 17.6,  6.0, "islak"),
 ("Z-14","Misafir giyinme odası",         17.6, 3.8, 20.0,  6.0, "teknik"),
 ("Z-15","Çalışma odası / ofis",          14.6, 6.0, 20.0,  9.4, "yasam"),
 ("Z-16","Üstü örtülü teras (barbekü)",   14.6, 9.4, 20.0, 15.0, "acik"),
],
"1. Kat": [
 ("K-01","Ebeveyn yatak odası",            0.0, 0.0,  8.6,  3.8, "yatak"),
 ("K-02","Ebeveyn giyinme odası",          0.0, 3.8,  4.6,  7.6, "teknik"),
 ("K-03","Ebeveyn banyosu",                4.6, 3.8,  8.6,  7.6, "islak"),
 ("K-04","Aile oturma odası / TV",         0.0, 7.6,  5.2, 13.0, "yasam"),
 ("K-05","Çalışma odası / kütüphane",      5.2, 7.6,  8.6, 13.0, "yasam"),
 ("K-06","Ebeveyn balkonu",                0.0,13.0,  8.6, 15.0, "acik"),
 ("K-07","Üst hol, merdiven ve galeri",    8.6, 0.0, 12.0,  9.4, "sirkulasyon"),
 ("K-08","Çamaşır ve ütü nişi",            8.6, 9.4, 12.0, 11.4, "islak"),
 ("K-09","Yatak odası 4",                  8.6,11.4, 14.6, 15.0, "yatak"),
 ("K-10","Yatak odası 2",                 12.0, 0.0, 17.6,  3.8, "yatak"),
 ("K-11","Yatak odası 2 banyosu",         17.6, 0.0, 20.0,  3.8, "islak"),
 ("K-12","Asansör ve tesisat şaftı",      12.0, 3.8, 14.6,  6.0, "teknik"),
 ("K-13","Koridor",                       12.0, 6.0, 14.6,  7.6, "sirkulasyon"),
 ("K-14","Ortak banyo",                   12.0, 7.6, 14.6, 11.4, "islak"),
 ("K-15","Yatak odası 3",                 14.6, 3.8, 20.0,  7.6, "yatak"),
 ("K-16","Yatak odası 3 giyinme",         14.6, 7.6, 20.0,  9.4, "teknik"),
 ("K-17","Yatak odası 5",                 14.6, 9.4, 20.0, 13.0, "yatak"),
 ("K-18","Balkon 2",                      14.6,13.0, 20.0, 15.0, "acik"),
],
}

def net_alan(r):
    """Aks geometrisinden net (duvar içi) alanı hesaplar."""
    _, _, x0, y0, x1, y1, _ = r
    tsol  = DIS_DUVAR if x0 <= 0.001 else IC_DUVAR
    tsag  = DIS_DUVAR if x1 >= BINA["en"] - 0.001 else IC_DUVAR
    tust  = DIS_DUVAR if y0 <= 0.001 else IC_DUVAR
    talt  = DIS_DUVAR if y1 >= BINA["boy"] - 0.001 else IC_DUVAR
    en  = (x1 - x0) - tsol / 2 - tsag / 2
    boy = (y1 - y0) - tust / 2 - talt / 2
    return round(en * boy, 1), round(min(en, boy), 2), round(max(en, boy), 2)

def kat_ozeti():
    ozet = {}
    for kat, mahaller in KATLAR.items():
        kapali = sum(net_alan(r)[0] for r in mahaller if r[6] != "acik")
        acik   = sum(net_alan(r)[0] for r in mahaller if r[6] == "acik")
        ozet[kat] = (round(kapali, 1), round(acik, 1))
    return ozet

if __name__ == "__main__":
    # kapsama testi: mahaller 20×15 alanı boşluksuz ve çakışmasız doldurmalı
    import itertools
    for kat, mahaller in KATLAR.items():
        toplam = sum((r[4]-r[2])*(r[5]-r[3]) for r in mahaller)
        cakisma = []
        for a, b in itertools.combinations(mahaller, 2):
            if a[2] < b[4] and b[2] < a[4] and a[3] < b[5] and b[3] < a[5]:
                cakisma.append((a[0], b[0]))
        kapali, acik = kat_ozeti()[kat]
        print("%-8s aks toplam %6.1f m² (hedef 300.0) | çakışma: %s | net kapalı %6.1f + açık %5.1f"
              % (kat, toplam, cakisma or "yok", kapali, acik))
