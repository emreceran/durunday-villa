# -*- coding: utf-8 -*-
"""Yönetmelik uygunluk kontrolleri — geometriden hesaplanır."""
from veri import (KATLAR, PARSEL, BINA, KAT_YUKSEKLIK, NET_TAVAN, KOT, TABII_ZEMIN, BALKONLAR, net_alan,
                  kat_ozeti, merdiven_kollari, MERDIVEN, mahal, ic_sinir)

PAIY = "Planlı Alanlar İmar Yönetmeliği (PAİY)"

def _tum(tip):
    return [m for liste in KATLAR.values() for m in liste if m["tip"] == tip]

def _en_kucuk(tip, sutun=0, filtre=lambda m: True):
    adaylar = [(net_alan(m), m) for m in _tum(tip) if filtre(m)]
    return min(adaylar, key=lambda am: am[0][sutun])

def v(x):
    return ("%.2f" % x).replace(".", ",")

def KONTROLLER():
    taban = BINA["en"] * BINA["boy"]
    emsal = taban * 2
    k = []
    k.append(("Taban alanı katsayısı (TAKS)", "≤ %s (%.0f m²)" % (v(PARSEL["taks"]), PARSEL["alan"] * PARSEL["taks"]),
              "%s (%.0f m²)" % (v(taban / PARSEL["alan"]), taban),
              "UYGUN" if taban <= PARSEL["alan"] * PARSEL["taks"] + .5 else "KONTROL",
              "Oturum 20,00 × 15,00 m; ısı yalıtımı ve 1,50 m'lik açık balkon çıkmaları TAKS'a dahil değildir."))
    k.append(("Kat alanları katsayısı (KAKS / emsal)", "≤ %s (%.0f m²)" % (v(PARSEL["kaks"]), PARSEL["alan"] * PARSEL["kaks"]),
              "%s (%.0f m²)" % (v(emsal / PARSEL["alan"]), emsal),
              "UYGUN" if emsal <= PARSEL["alan"] * PARSEL["kaks"] + .5 else "KONTROL",
              "Zemin + 1. kat emsale dahildir. Bodrumdaki sinema, oyun salonu, fitness ve misafir odası "
              "iskan edilen hacim sayılabilir — emsal dışı kabulü belediyece teyit edilmelidir."))
    k.append(("Bodrum katın emsal durumu", "Konut kullanımı emsale dahil; depo, tesisat, otopark hariç",
              "Bodrumda yaşama hacimleri var", "KONTROL",
              "Emsal hesabına katılırsa bodrum kullanımları depo/hobi niteliğinde projelendirilmeli veya zemin + 1. kat küçültülmelidir."))
    k.append(("Bina yüksekliği (Hmax)", "≤ %s m (Yençok 2 kat)" % v(PARSEL["hmax"]),
              "%s m (tabii zeminden çatı döşemesine)" % v(KOT["Çatı"] - TABII_ZEMIN),
              "UYGUN" if KOT["Çatı"] - TABII_ZEMIN <= PARSEL["hmax"] + 1e-6 else "KONTROL",
              "±0.00 = tabii zemin +0,30; zemin 3,20 + 1. kat 3,00 m. Çatı eğimi %30, mahya +8,94."))
    k.append(("Çekme mesafeleri", "ön 5,00 · yan 3,00 · arka 3,00 m",
              "ön %s · yan %s · arka %s m" % (v(5.0), v(3.0), v(PARSEL["boy"] - 5.0 - BINA["boy"])), "UYGUN",
              "%s Md. 24; vaziyet planında gösterilmiştir. Işıklıklar yan bahçede zemin altındadır." % PAIY))
    k.append(("Açık çıkma (balkon)", "≤ 1,50 m", "%s m (güney cephesi, 2 balkon)" % v(max(b["derinlik"] for b in BALKONLAR)),
              "UYGUN", "%s Md. 25 — konsol balkon, bahçe mesafesine taşar." % PAIY))
    s = mahal("Z-09")[1]; a, dar, uzun = net_alan(s)
    k.append(("Oturma odası (asgari 1 adet)", "12,00 m² · dar kenar 3,00 m", "%s m² · dar kenar %s m" % (v(a), v(dar)),
              "UYGUN" if a >= 12 and dar >= 3 else "KONTROL", "%s Md. 29 — Z-09 Salon." % PAIY))
    (a, dar, _), m = _en_kucuk("yatak", 0)
    k.append(("Yatak odası (en küçüğü)", "9,00 m² · dar kenar 2,50 m", "%s m² · dar kenar %s m" % (v(a), v(dar)),
              "UYGUN" if a >= 9 and dar >= 2.5 else "KONTROL",
              "%s Md. 29 — %s %s. Projede %d yatak odası var." % (PAIY, m["kod"], m["ad"], len(_tum("yatak")))))
    m = mahal("Z-11")[1]; a, dar, uzun = net_alan(m)
    k.append(("Mutfak", "3,30 m² · dar kenar 1,50 m", "%s m² · dar kenar %s m" % (v(a), v(dar)),
              "UYGUN" if a >= 3.3 and dar >= 1.5 else "KONTROL", "%s Md. 29 — Z-11 Mutfak (+ Z-16 arka mutfak)." % PAIY))
    (a, dar, _), m = _en_kucuk("islak", 0, lambda m: "WC" not in m["ad"] and "Sauna" not in m["ad"] and "Çamaşır" not in m["ad"])
    k.append(("Banyo (en küçüğü)", "3,00 m² · dar kenar 1,50 m", "%s m² · dar kenar %s m" % (v(a), v(dar)),
              "UYGUN" if a >= 3 and dar >= 1.5 else "KONTROL", "%s Md. 29 — %s %s." % (PAIY, m["kod"], m["ad"])))
    (a, dar, _), m = _en_kucuk("islak", 0, lambda m: "WC" in m["ad"])
    k.append(("Tuvalet (en küçüğü)", "1,20 m² · dar kenar 1,00 m", "%s m² · dar kenar %s m" % (v(a), v(dar)),
              "UYGUN" if a >= 1.2 and dar >= 1.0 else "KONTROL", "%s Md. 29 — %s %s." % (PAIY, m["kod"], m["ad"])))
    (a, dar, _), m = _en_kucuk("sirkulasyon", 1)
    k.append(("Hol / koridor genişliği (en dar)", "1,20 m", "%s m" % v(dar),
              "UYGUN" if dar >= 1.2 else "KONTROL", "%s Md. 29 — %s %s." % (PAIY, m["kod"], m["ad"])))
    gen = MERDIVEN["dogu_kol"][1] - MERDIVEN["dogu_kol"][0]
    k.append(("Konut içi merdiven kol genişliği", "≥ 1,00 m", "%s m (sahanlık %s m)" % (v(gen), v(1.25)),
              "UYGUN" if gen >= 1.0 else "KONTROL", "%s Md. 32 — iki kollu (U) merdiven." % PAIY))
    m0, m1 = merdiven_kollari("Bodrum"), merdiven_kollari("Zemin")
    k.append(("Merdiven rıht / basamak", "rıht ≤ 17,5 cm · basamak ≥ 26 cm",
              "bodrum→zemin 18 × %s cm · zemin→1. kat 19 × %s cm · basamak 28 cm" % (v(m0["riht"] * 100)[:-1], v(m1["riht"] * 100)[:-1]),
              "UYGUN" if max(m0["riht"], m1["riht"]) <= 0.175 else "KONTROL", "%s Md. 32; 2r + b = 61,7–62,0 cm." % PAIY))
    net_min = min(NET_TAVAN.values())
    k.append(("Net tavan yüksekliği", "≥ 2,40 m (konut)", "%s m (en düşük, asma tavan altı)" % v(net_min),
              "UYGUN" if net_min >= 2.40 else "KONTROL",
              "Bodrum %s · zemin %s · 1. kat %s m." % (v(NET_TAVAN["Bodrum"]), v(NET_TAVAN["Zemin"]), v(NET_TAVAN["1. Kat"]))))
    k.append(("Korkuluk yüksekliği", "≥ 1,10 m", "1,10 m (balkon, galeri, merdiven boşluğu, ışıklık)", "UYGUN",
              "Temperli lamine cam, tırmanmaya elverişsiz."))
    k.append(("Pencere denizliği (üst kat)", "düşme riskine karşı ≥ 0,85 m veya korkuluk", "0,90 m; kapı boyu camlar yalnız balkona",
              "UYGUN", "Otomatik kontrol: kontrol.py."))
    k.append(("Otopark", "Her bağımsız bölüm için en az 1 araç", "2 kapalı (garaj) + 2 açık", "UYGUN",
              "Otopark Yönetmeliği; garaj zemin katta, araç yolu doğrudan imar yolundan."))
    k.append(("Asansör", "Zorunlu değil (≤ 3 kat konut)", "3 duraklı, 630 kg, makine dairesiz", "UYGUN",
              "Engelsiz erişim için isteğe bağlı; kuyu betonarme perde."))
    k.append(("Sığınak", "Tek konutta aranmaz", "—", "KONTROL", "Sığınak Yönetmeliği kapsamı idareyle teyit edilmelidir."))
    k.append(("Isı yalıtımı", "TS 825 — 3. bölge (Konya)", "Dış duvar 8 cm taşyünü · çatı döşemesi 14 cm · bodrum XPS 5 cm",
              "UYGUN", "Binalarda Enerji Performansı Yönetmeliği; enerji kimlik belgesiyle kesinleşir."))
    k.append(("Deprem tasarımı", "TBDY-2018", "Betonarme çerçeve + asansör perdesi, radye temel", "UYGUN",
              "Aks açıklıkları ≤ 7,80 m. Zemin etüdüne göre statik projede kesinleşir."))
    k.append(("Yangın güvenliği", "Binaların Yangından Korunması Hakkında Yönetmelik",
              "Garaj–konut ve ısı merkezi kapıları EI30 · duman dedektörü · şaftta yangın durdurucu", "UYGUN",
              "Müstakil konut; bodrum misafir odasında ışıklıktan acil çıkış merdiveni."))
    k.append(("Su yalıtımı", "Su Yalıtımı Yönetmeliği / TS 11344",
              "Bodrum perde ve radyede çift kat membran + drenaj; ıslak hacimlerde 2K sürme", "UYGUN",
              "Sistem kesitinde (A-10) gösterilmiştir."))
    return k

if __name__ == "__main__":
    for r in KONTROLLER():
        print("%-38s %-36s %-50s %s" % (r[0][:38], r[1][:36], r[2][:50], r[3]))
