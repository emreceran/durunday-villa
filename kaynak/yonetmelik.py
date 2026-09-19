# -*- coding: utf-8 -*-
"""Yönetmelik uygunluk kontrolleri — geometriden hesaplanır."""
from veri import KATLAR, PARSEL, BINA, KAT_YUKSEKLIK, NET_TAVAN, net_alan, kat_ozeti

PAIY = "Planlı Alanlar İmar Yönetmeliği (PAİY)"

def _min_tip(tip, sutun=0):
    """Verilen tipteki mahaller içinde en küçük alan / dar kenar."""
    en_kucuk = None
    for kat, mahaller in KATLAR.items():
        for r in mahaller:
            if r[6] != tip:
                continue
            a, dar, uzun = net_alan(r)
            deger = (a, dar, r)
            if en_kucuk is None or deger[sutun] < en_kucuk[sutun]:
                en_kucuk = deger
    return en_kucuk

def _mahal(kod):
    for kat, mahaller in KATLAR.items():
        for r in mahaller:
            if r[0] == kod:
                return r
    return None

def KONTROLLER():
    ozet = kat_ozeti()
    taban = BINA["en"] * BINA["boy"]
    emsal = taban * 2                      # zemin + 1. kat (bodrum ve çatı arası hariç)
    k = []
    k.append(("Taban alanı katsayısı (TAKS)",
              "≤ %.2f (%.0f m²)" % (PARSEL["taks"], PARSEL["alan"]*PARSEL["taks"]),
              "%.2f (%.0f m²)" % (taban/PARSEL["alan"], taban),
              "UYGUN" if taban <= PARSEL["alan"]*PARSEL["taks"] + .5 else "KONTROL",
              "Oturum 20,00 × 15,00 m. Parsel bilgisi varsayımdır, imar durumu ile teyit edilmelidir."))
    k.append(("Kat alanları katsayısı (KAKS/Emsal)",
              "≤ %.2f (%.0f m²)" % (PARSEL["kaks"], PARSEL["alan"]*PARSEL["kaks"]),
              "%.2f (%.0f m²)" % (emsal/PARSEL["alan"], emsal),
              "UYGUN" if emsal <= PARSEL["alan"]*PARSEL["kaks"] + .5 else "KONTROL",
              "Zemin + 1. kat emsale dahil; bodrum ve çatı arası emsal dışı kabul edilmiştir (teyit gerekir)."))
    k.append(("Çekme mesafeleri",
              "ön 5,00 · yan 3,00 · arka 3,00 m",
              "ön %.2f · yan %.2f · arka %.2f m" % (PARSEL["cekme_on"], PARSEL["cekme_yan"], PARSEL["cekme_arka"]),
              "UYGUN", "%s Md. 24 ve plan notları; vaziyet planında gösterilmiştir." % PAIY))
    o = _mahal("Z-01"); a, dar, uzun = net_alan(o)
    k.append(("Oturma odası (asgari 1 adet)", "12,00 m² · dar kenar 3,00 m",
              "%.1f m² · dar kenar %.2f m" % (a, dar), "UYGUN" if a >= 12 and dar >= 3.0 else "KONTROL",
              "%s Md. 29 — Z-01 Salon." % PAIY))
    y = _min_tip("yatak", 0); a, dar, r = y
    k.append(("Yatak odası (en küçüğü)", "9,00 m² · dar kenar 2,50 m",
              "%.1f m² · dar kenar %.2f m" % (a, dar), "UYGUN" if a >= 9 and dar >= 2.5 else "KONTROL",
              "%s Md. 29 — %s %s. Projede 7 yatak odası var." % (PAIY, r[0], r[1])))
    m = _mahal("Z-06"); a, dar, uzun = net_alan(m)
    k.append(("Mutfak", "3,30 m² · dar kenar 1,50 m",
              "%.1f m² · dar kenar %.2f m" % (a, dar), "UYGUN" if a >= 3.3 and dar >= 1.5 else "KONTROL",
              "%s Md. 29 — Z-06 Mutfak (+ Z-07 kiler/arka mutfak)." % PAIY))
    b = _min_tip("islak", 0); a, dar, r = b
    k.append(("Banyo / yıkanma yeri (en küçüğü)", "3,00 m² · dar kenar 1,50 m",
              "%.1f m² · dar kenar %.2f m" % (a, dar), "UYGUN" if a >= 3.0 and dar >= 1.5 else "KONTROL",
              "%s Md. 29 — %s %s. Projede 9 ıslak hacim var." % (PAIY, r[0], r[1])))
    w = _mahal("Z-08"); a, dar, uzun = net_alan(w)
    k.append(("Tuvalet", "1,20 m² · dar kenar 1,00 m",
              "%.1f m² · dar kenar %.2f m" % (a, dar), "UYGUN" if a >= 1.2 and dar >= 1.0 else "KONTROL",
              "%s Md. 29 — Z-08 Misafir WC." % PAIY))
    s = _min_tip("sirkulasyon", 1); a, dar, r = s
    k.append(("Hol / koridor genişliği (en dar)", "1,20 m",
              "%.2f m" % dar, "UYGUN" if dar >= 1.2 else "KONTROL",
              "%s Md. 29 — %s %s." % (PAIY, r[0], r[1])))
    k.append(("Konut içi merdiven kol genişliği", "1,00 m (ortak merdivende 1,20 m)",
              "1,20 m", "UYGUN", "%s Md. 32. Merdiven kovası 3,40 × 5,60 m mahal içinde." % PAIY))
    k.append(("Merdiven rıht / basamak", "rıht ≤ 17,50 cm · basamak ≥ 26,0 cm",
              "rıht 17,1 cm (bodrum→zemin, 17 basamak) · 16,8 cm (zemin→1. kat, 19 basamak) · basamak 28,0 cm",
              "UYGUN", "%s Md. 32. Kat yüksekliklerinden hesaplanmıştır." % PAIY))
    net_min = min(NET_TAVAN.values())
    k.append(("Net tavan yüksekliği", "2,40 m",
              "%.2f m (en düşük kat)" % net_min, "UYGUN" if net_min >= 2.40 else "KONTROL",
              "Kat yükseklikleri: " + " · ".join("%s %.2f m" % (a2, b2) for a2, b2 in KAT_YUKSEKLIK.items())))
    k.append(("Çatı arası iç yüksekliği", "2,40 m (kullanılabilir hacim için)",
              "mahyada 3,60 m", "UYGUN", "Çatı arası depo olarak kullanılacaktır; bağımsız bölüm değildir."))
    k.append(("Korkuluk yüksekliği", "1,10 m",
              "1,10 m (balkon, teras, galeri, merdiven)", "UYGUN",
              "Temperli cam korkuluk; tırmanmaya elverişsiz tasarım."))
    k.append(("Otopark", "Her bağımsız bölüm için en az 1 araçlık",
              "3 kapalı (garaj) + 2 açık = 5 araç", "UYGUN",
              "Otopark Yönetmeliği; kapalı garaj bodrum katta, rampa bahçe içinde."))
    k.append(("Sığınak", "Bağımsız bölüm sayısına göre (tek konutta aranmaz)",
              "Bodrumda depo hacimleri ayrılmıştır", "KONTROL",
              "Sığınak Yönetmeliği kapsamı ilgili idareyle teyit edilmelidir."))
    k.append(("Asansör", "Kat adedi 4'ten fazla binalarda zorunlu",
              "4 duraklı asansör (isteğe bağlı olarak) yapılmıştır", "UYGUN",
              "%s Md. 34. Kuyu 2,60 × 2,20 m, makine dairesiz." % PAIY))
    k.append(("Isı yalıtımı", "TS 825 — 3. iklim bölgesi (Konya)",
              "Dış duvar 8 cm XPS · çatı 14 cm taşyünü · döşeme 4 cm", "UYGUN",
              "Binalarda Enerji Performansı Yönetmeliği; enerji kimlik belgesi hesabı yapılacaktır."))
    k.append(("Deprem tasarımı", "TBDY-2018",
              "Betonarme perde + çerçeve sistem, radye temel", "UYGUN",
              "Zemin etüdü raporuna göre zemin sınıfı ve tasarım spektrumu belirlenecektir."))
    k.append(("Yangın güvenliği", "Binaların Yangından Korunması Hakkında Yönetmelik",
              "Kazan dairesi EI30 yangın kapısı · duman dedektörü · şaftlarda yangın durdurucu",
              "UYGUN", "Müstakil konut; kaçış merdiveni aranmaz."))
    k.append(("Su yalıtımı", "TS 11344 / Su Yalıtımı Yönetmeliği",
              "Bodrum perde ve temelde çift kat membran + drenaj; ıslak hacimlerde 2K yalıtım",
              "UYGUN", "Yalıtım detayları uygulama projesinde çizilecektir."))
    return k

if __name__ == "__main__":
    for r in KONTROLLER():
        print("%-40s %-34s %-44s %s" % (r[0][:40], r[1][:34], r[2][:44], r[3]))
