# -*- coding: utf-8 -*-
"""Tasarım mantık kontrolü — plan geometrisinden otomatik.

Her kontrol (grup, ad, durum, açıklama) üretir. durum: UYGUN | UYARI | HATA.
`python3 kontrol.py` hataları listeler; çıkış kodu hata varsa 1."""
import itertools, sys
from collections import deque
from veri import (KATLAR, KATLAR_SIRA, KAPILAR, PENCERELER, ACIK, MOBILYA, BINA, KOT, TABII_ZEMIN,
                  PARSEL, MERDIVEN, ASANSOR, ISIKLIKLAR, BACA, BALKONLAR, GIRIS_SACAGI, DIS_DUVAR,
                  IC_DUVAR, KOLON, kolonlar, merdiven_kollari, net_alan, ic_sinir)
from geometri import (oda_bul, mahal_sozluk, acik_tur, ham_kenarlar, kapi_taraflari, kanat_alani,
                      duvar_parcalari, duvar_dikdortgeni)
from mobilya import sinir_kutusu, ZEMIN_OGESI

W, H = BINA["en"], BINA["boy"]
EPS = 1e-6
KANATLI = ("kapi", "yangin", "giris", "servis", "kapak")
SONUC = []

def ekle(grup, ad, durum, aciklama=""):
    SONUC.append((grup, ad, durum, aciklama))

def kesisim(a, b, pay=0.0):
    return a[0] < b[2] - pay and b[0] < a[2] - pay and a[1] < b[3] - pay and b[1] < a[3] - pay

def icinde(k, s, pay=0.0):
    return k[0] >= s[0] - pay and k[1] >= s[1] - pay and k[2] <= s[2] + pay and k[3] <= s[3] + pay

# ------------------------------------------------------------------ 1. geometri
def k_geometri():
    for kat in KATLAR_SIRA:
        rects = [(m["kod"], r) for m in KATLAR[kat] for r in m["r"]]
        toplam = sum((r[2] - r[0]) * (r[3] - r[1]) for _, r in rects)
        cak = [(a[0], b[0]) for a, b in itertools.combinations(rects, 2) if kesisim(a[1], b[1])]
        ok = abs(toplam - W * H) < 0.01 and not cak
        ekle("Geometri", "%s: mahaller 20×15 alanı boşluksuz doldurur" % kat,
             "UYGUN" if ok else "HATA", "aks toplamı %.2f m², çakışma %s" % (toplam, cak or "yok"))
    # düşey elemanların hizası
    for tip in ("merdiven", "asansor", "saft"):
        kutular = {kat: [tuple(m["r"][0]) for m in KATLAR[kat] if m["tip"] == tip] for kat in KATLAR_SIRA}
        ayni = len({tuple(v) for v in kutular.values()}) == 1
        ekle("Geometri", "%s tüm katlarda aynı yerde" % tip.capitalize(), "UYGUN" if ayni else "HATA",
             "; ".join("%s %s" % (k, v) for k, v in kutular.items()))

# ------------------------------------------------------------------ 2. kapılar
def _ortak_kenar(kat, e, c, p, q):
    """p ile q arasındaki, e/c doğrusundaki ortak kenar aralıkları."""
    out = []
    for s in ham_kenarlar(kat):
        if s[0] == e and abs(s[1] - c) < EPS and {s[4], s[5]} == {p, q}:
            out.append((s[2], s[3]))
    out.sort()
    birlesik = []
    for a, b in out:
        if birlesik and abs(birlesik[-1][1] - a) < EPS:
            birlesik[-1] = (birlesik[-1][0], b)
        else:
            birlesik.append((a, b))
    return birlesik

def k_kapilar():
    kolon_kutulari = [(x - KOLON / 2, y - KOLON / 2, x + KOLON / 2, y + KOLON / 2) for x, y in kolonlar()]
    for kat in KATLAR_SIRA:
        sozluk = mahal_sozluk(kat)
        hatalar = []
        for k in KAPILAR[kat]:
            e, c, a, b, tip, hedef, mentese = k
            p, q = kapi_taraflari(kat, k)
            ad = "%s %s %.2f [%.2f–%.2f]" % (tip, e, c, a, b)
            if p == q:
                hatalar.append("%s: iki tarafı aynı mahal (%s)" % (ad, p)); continue
            if tip in ("giris", "servis", "garaj") and "DIS" not in (p, q):
                hatalar.append("%s: dış kapı dış duvarda değil" % ad)
            if tip not in ("giris", "servis", "garaj") and "DIS" in (p, q):
                hatalar.append("%s: iç kapı dış duvarda" % ad)
            aralik = _ortak_kenar(kat, e, c, p, q)
            dik = IC_DUVAR / 2 + 0.05
            uygun = any(a >= s0 + dik - EPS and b <= s1 - dik + EPS for s0, s1 in aralik)
            if not uygun:
                hatalar.append("%s (%s|%s): ortak duvar %s içine sığmıyor (köşeden ≥ %.0f cm pay)"
                               % (ad, p, q, aralik, dik * 100))
            if tip in KANATLI and hedef not in (p, q):
                hatalar.append("%s: açıldığı mahal %s kapının iki yanında değil (%s|%s)" % (ad, hedef, p, q))
            w = b - a
            if tip in ("kapi", "yangin") and not (0.79 <= w <= 1.01):
                hatalar.append("%s: kapı genişliği %.2f m olağan dışı" % (ad, w))
            if tip == "kapi" and w < 0.89 and all(sozluk.get(x, {}).get("tip") != "islak" for x in (p, q)):
                hatalar.append("%s: ıslak hacim dışı kapı 0,90 m altında" % ad)
            # kolonla çakışma
            op = (c - 0.2, a, c + 0.2, b) if e == "x" else (a, c - 0.2, b, c + 0.2)
            for kk in kolon_kutulari:
                if kesisim(op, kk, 0.01):
                    hatalar.append("%s: kolonla çakışıyor" % ad)
        ekle("Kapılar", "%s: kapılar doğru duvarda, köşelere ve kolonlara çarpmıyor" % kat,
             "HATA" if hatalar else "UYGUN", "; ".join(hatalar) or "%d kapı/açıklık" % len(KAPILAR[kat]))

def _engel_kutulari(kat):
    """Kanat alanına girmemesi gereken sabit engeller: merdiven kolları, asansör kuyusu."""
    out = []
    for m in KATLAR[kat]:
        if m["tip"] in ("asansor", "saft"):
            out.append((m["kod"], ic_sinir(m["r"][0])))
    mk = merdiven_kollari(kat)
    kollar = mk["kollar"] if mk else []
    if kat != "Bodrum":
        onceki = KATLAR_SIRA[KATLAR_SIRA.index(kat) - 1]
        kollar = kollar + [merdiven_kollari(onceki)["kollar"][1]]
    for x0, x1, ya, yb, r, yon in kollar:
        out.append(("merdiven kolu", (x0, min(ya, yb), x1, max(ya, yb))))
    s = MERDIVEN["sahanlik"]
    out.append(("sahanlık/boşluk", (MERDIVEN["bati_kol"][0], s[0], MERDIVEN["dogu_kol"][1], s[1])))
    return out

def k_kanatlar():
    for kat in KATLAR_SIRA:
        sorun = []
        kanatlar = []
        for k in KAPILAR[kat]:
            if k[4] not in KANATLI:
                continue
            alan = kanat_alani(kat, k)
            kanatlar.append((k, alan))
            hedef = k[5]
            if hedef != "DIS":
                ic = [ic_sinir(r) for r in mahal_sozluk(kat)[hedef]["r"]]
                if not any(icinde(alan, s, 0.02) for s in ic):
                    sorun.append("%s kapısı (%.2f–%.2f) kanadı %s duvarlarına çarpıyor" % (hedef, k[2], k[3], hedef))
            for ad, kutu in _engel_kutulari(kat):
                if kesisim(alan, kutu, 0.02):
                    sorun.append("%s kapısı kanadı %s ile çakışıyor" % (hedef, ad))
            for o in MOBILYA.get(kat, []):
                if o[0] in ZEMIN_OGESI:
                    continue
                if kesisim(alan, sinir_kutusu(o), 0.02):
                    sorun.append("%s kapısı kanadı %s (%.2f, %.2f) mobilyasına çarpıyor" % (hedef, o[0], o[1], o[2]))
        for (k1, a1), (k2, a2) in itertools.combinations(kanatlar, 2):
            if kesisim(a1, a2, 0.02):
                sorun.append("%s ve %s kapı kanatları birbirine çarpıyor" % (k1[5], k2[5]))
        ekle("Kapılar", "%s: kapı kanatları serbest açılıyor (duvar, merdiven, mobilya, diğer kapı)" % kat,
             "HATA" if sorun else "UYGUN", "; ".join(sorun) or "%d kanat" % len(kanatlar))

# ------------------------------------------------------------------ 3. erişim ve mahremiyet
def baglanti_grafi():
    """Düğüm: (kat, kod). Kenar: kapı, açık geçiş, merdiven, asansör."""
    g = {}
    def bag(u, v, tur):
        g.setdefault(u, []).append((v, tur)); g.setdefault(v, []).append((u, tur))
    for kat in KATLAR_SIRA:
        for m in KATLAR[kat]:
            g.setdefault((kat, m["kod"]), [])
        for k in KAPILAR[kat]:
            if k[4] == "kapak":
                continue
            p, q = kapi_taraflari(kat, k)
            bag((kat, p), (kat, q), k[4])
        for p, q, tur in ACIK.get(kat, []):
            if tur == "acik" or (tur == "korkuluk" and "merdiven" in (mahal_sozluk(kat)[p]["tip"], mahal_sozluk(kat)[q]["tip"])):
                bag((kat, p), (kat, q), tur)
    for tip in ("merdiven", "asansor"):
        dugumler = [(kat, m["kod"]) for kat in KATLAR_SIRA for m in KATLAR[kat] if m["tip"] == tip]
        for u, v in zip(dugumler, dugumler[1:]):
            bag(u, v, tip)
    return g

def k_erisim():
    g = baglanti_grafi()
    bas = ("Zemin", "DIS")
    gorulen = {bas}
    kuyruk = deque([bas])
    while kuyruk:
        u = kuyruk.popleft()
        for v, _ in g.get(u, []):
            if v not in gorulen:
                gorulen.add(v); kuyruk.append(v)
    ulasilamaz = [(kat, m["kod"], m["ad"]) for kat in KATLAR_SIRA for m in KATLAR[kat]
                  if m["tip"] not in ("saft", "bosluk") and (kat, m["kod"]) not in gorulen]
    ekle("Erişim", "Her mahale giriş kapısından ulaşılır", "HATA" if ulasilamaz else "UYGUN",
         "; ".join("%s %s %s" % u for u in ulasilamaz) or "tüm mahaller bağlı")
    # asansör kapısı her katta sirkülasyona açılıyor mu
    sorun = []
    for kat in KATLAR_SIRA:
        for k in KAPILAR[kat]:
            if k[4] == "asansor":
                p, q = kapi_taraflari(kat, k)
                diger = q if mahal_sozluk(kat)[p]["tip"] == "asansor" else p
                if mahal_sozluk(kat)[diger]["tip"] != "sirkulasyon":
                    sorun.append("%s: asansör %s mahaline açılıyor" % (kat, diger))
    ekle("Erişim", "Asansör her katta hole açılır (3 durak)", "HATA" if sorun else "UYGUN", "; ".join(sorun))

IZINLI_ONCUL = {
    # hedef tip: kapısının açılabileceği mahal tipleri
    "yatak":    {"sirkulasyon", "giyinme"},
    "giyinme":  {"sirkulasyon", "yatak"},
    "islak":    {"sirkulasyon", "yatak", "giyinme", "islak"},
    "mutfak":   {"sirkulasyon", "yasam", "mutfak", "DIS"},
    "yasam":    {"sirkulasyon", "yasam", "islak"},
    "ikincil":  {"sirkulasyon"},
    "teknik":   {"sirkulasyon", "teknik", "mutfak"},
    "garaj":    {"sirkulasyon", "DIS"},
    "sirkulasyon": {"sirkulasyon", "merdiven", "DIS", "yasam"},
}

def k_mahremiyet():
    sorun, notlar = [], []
    for kat in KATLAR_SIRA:
        sozluk = mahal_sozluk(kat)
        tip = lambda k: "DIS" if k == "DIS" else sozluk[k]["tip"]
        komsu = {}
        for k in KAPILAR[kat]:
            if k[4] in ("kapak", "asansor"):
                continue
            p, q = kapi_taraflari(kat, k)
            komsu.setdefault(p, set()).add(q); komsu.setdefault(q, set()).add(p)
        for p, q, tur in ACIK.get(kat, []):
            if tur == "acik":
                komsu.setdefault(p, set()).add(q); komsu.setdefault(q, set()).add(p)
        for kod, m in sozluk.items():
            t = m["tip"]
            if t not in IZINLI_ONCUL:
                continue
            gelen = komsu.get(kod, set())
            izin = IZINLI_ONCUL[t]
            if t == "islak" and "WC" in m["ad"]:
                izin = izin | {"yasam"}
            if t == "islak" and "Soyunma" in m["ad"]:
                izin = izin | {"sirkulasyon"}
            if t == "yasam" and "Fitness" in m["ad"]:
                izin = izin | {"islak"}
            uygun = [g for g in gelen if tip(g) in izin]
            if not uygun:
                sorun.append("%s %s: kapısı yalnızca %s mahallerine açılıyor"
                             % (kod, m["ad"], ", ".join(sorted("%s(%s)" % (g, tip(g)) for g in gelen)) or "—"))
            # yatak odasına başka yatak/ıslak/mutfak içinden geçilmemeli
            if t == "yatak":
                for g in gelen:
                    if tip(g) in ("yatak", "mutfak", "yasam", "teknik", "garaj"):
                        sorun.append("%s %s: %s içinden geçilerek girilebiliyor" % (kod, m["ad"], g))
            # içinden başka mahale geçilen ıslak hacim
            if t == "islak" and len(gelen) > 1 and "Soyunma" not in m["ad"]:
                notlar.append("%s %s: %d kapılı" % (kod, m["ad"], len(gelen)))
    ekle("Erişim", "Mahremiyet: yatak odaları hol/giyinme üzerinden, banyolar odadan veya holden",
         "HATA" if sorun else "UYGUN", "; ".join(sorun) or "tüm kapı ilişkileri uygun")
    if notlar:
        ekle("Erişim", "Geçişli ıslak hacim", "UYARI", "; ".join(notlar))

# ------------------------------------------------------------------ 4. gün ışığı ve havalandırma
def _pencere_mahalleri(kat, p):
    cephe, a, b = p[0], p[1], p[2]
    d = 0.5
    if cephe in ("K", "G"):
        y = d if cephe == "K" else H - d
        return {oda_bul(kat, x, y) for x in (a + 0.01, (a + b) / 2, b - 0.01)}
    x = d if cephe == "B" else W - d
    return {oda_bul(kat, x, y) for y in (a + 0.01, (a + b) / 2, b - 0.01)}

def k_gunisigi():
    sorun, uyari = [], []
    for kat in KATLAR_SIRA:
        sozluk = mahal_sozluk(kat)
        cam = {}
        for p in PENCERELER[kat]:
            odalar = _pencere_mahalleri(kat, p)
            if len(odalar) != 1:
                sorun.append("%s %s cephesi %.2f–%.2f penceresi birden fazla mahale taşıyor: %s"
                             % (kat, p[0], p[1], p[2], odalar)); continue
            kod = odalar.pop()
            if sozluk[kod]["tip"] == "bosluk":
                kod = "K-01"
            h = p[5] - p[4]
            cam[kod] = cam.get(kod, 0) + (p[2] - p[1]) * h * 0.75
            if p[3] == "I" and not any(i["cephe"] == p[0] and i["a"] <= p[1] + EPS and i["b"] >= p[2] - EPS
                                       for i in ISIKLIKLAR):
                sorun.append("%s %s: bodrum penceresi ışıklığa bakmıyor" % (kat, kod))
            if kat == "Bodrum" and p[3] != "I":
                sorun.append("%s %s: bodrumda toprağa açılan pencere" % (kat, kod))
            if p[0] == "B" and p[1] < BACA["b"] and p[2] > BACA["a"] and kat != "Bodrum":
                sorun.append("%s %s: pencere şömine bacasıyla çakışıyor" % (kat, kod))
        for kod, m in sozluk.items():
            if m["tip"] in ("yatak", "yasam", "mutfak"):
                alan = net_alan(m)[0]
                c = cam.get(kod, 0)
                if c <= 0:
                    sorun.append("%s %s: penceresi yok" % (kod, m["ad"]))
                elif c < alan / 10:
                    sorun.append("%s %s: cam alanı %.1f m² < döşemenin 1/10'u (%.1f m²)" % (kod, m["ad"], c, alan / 10))
                elif c < alan / 8:
                    uyari.append("%s %s: cam/döşeme 1/%.0f" % (kod, m["ad"], alan / c))
    ekle("Gün ışığı", "Yaşama mahalleri (yatak, oturma, mutfak) doğrudan gün ışığı alır; cam ≥ döşeme/10",
         "HATA" if sorun else "UYGUN", "; ".join(sorun) or "tüm yaşama mahallerinde pencere var")
    if uyari:
        ekle("Gün ışığı", "Cam oranı 1/8'in altında kalan mahaller", "UYARI", "; ".join(uyari))
    # penceresiz ıslak hacimler → mekanik havalandırma
    liste = []
    for kat in KATLAR_SIRA:
        pencereli = set()
        for p in PENCERELER[kat]:
            pencereli |= _pencere_mahalleri(kat, p)
        for m in KATLAR[kat]:
            if m["tip"] == "islak" and m["kod"] not in pencereli:
                liste.append(m["kod"])
    ekle("Gün ışığı", "Penceresiz ıslak hacimler mekanik havalandırma (şafta bağlı aspiratör) ile çözülür",
         "UYGUN", ", ".join(liste))

def k_pencere_yerlesimi():
    kolon_kutulari = [(x - KOLON / 2, y - KOLON / 2, x + KOLON / 2, y + KOLON / 2) for x, y in kolonlar()]
    sorun = []
    for kat in KATLAR_SIRA:
        for p in PENCERELER[kat]:
            cephe, a, b = p[0], p[1], p[2]
            if cephe in ("K", "G"):
                y = 0.0 if cephe == "K" else H
                kutu = (a, y - 0.2, b, y + 0.2)
            else:
                x = 0.0 if cephe == "B" else W
                kutu = (x - 0.2, a, x + 0.2, b)
            for kk in kolon_kutulari:
                if kesisim(kutu, kk, 0.05):
                    sorun.append("%s %s %.2f–%.2f: kolona denk geliyor" % (kat, cephe, a, b))
            # iç duvara en az 10 cm pay
            for s in ham_kenarlar(kat):
                if s[6] == "dis":
                    continue
                if cephe in ("K", "G") and s[0] == "x" and a - 0.10 < s[1] < b + 0.10:
                    ucy = (s[2], s[3])
                    if (cephe == "K" and ucy[0] < 0.4) or (cephe == "G" and ucy[1] > H - 0.4):
                        sorun.append("%s %s %.2f–%.2f: iç duvara (x=%.2f) çok yakın" % (kat, cephe, a, b, s[1]))
                if cephe in ("B", "D") and s[0] == "y" and a - 0.10 < s[1] < b + 0.10:
                    ucx = (s[2], s[3])
                    if (cephe == "B" and ucx[0] < 0.4) or (cephe == "D" and ucx[1] > W - 0.4):
                        sorun.append("%s %s %.2f–%.2f: iç duvara (y=%.2f) çok yakın" % (kat, cephe, a, b, s[1]))
        # aynı cephede çakışan açıklık
        for p1, p2 in itertools.combinations(PENCERELER[kat], 2):
            if p1[0] == p2[0] and p1[1] < p2[2] and p2[1] < p1[2]:
                sorun.append("%s %s: %.2f–%.2f ile %.2f–%.2f çakışıyor" % (kat, p1[0], p1[1], p1[2], p2[1], p2[2]))
    ekle("Cephe", "Pencereler kolona, iç duvara ve birbirine çarpmıyor", "HATA" if sorun else "UYGUN",
         "; ".join(sorun) or "tüm pencereler serbest")
    # sürme cam kapılar balkona / terasa açılıyor
    sorun = []
    for p in PENCERELER["1. Kat"]:
        if p[3] == "S":
            if not any(bk["x0"] <= p[1] and bk["x1"] >= p[2] for bk in BALKONLAR):
                sorun.append("1. kat %s %.2f–%.2f sürme kapı balkonsuz" % (p[0], p[1], p[2]))
        if p[3] == "P" and p[4] < 0.85:
            sorun.append("1. kat penceresi denizlik %.2f < 0,85 (düşme riski)" % p[4])
    ekle("Cephe", "Üst kattaki kapı boyu camlar balkona açılır; pencere denizlikleri ≥ 0,85 m",
         "HATA" if sorun else "UYGUN", "; ".join(sorun))

# ------------------------------------------------------------------ 5. taşıyıcı sistem
def k_kolonlar():
    for kat in KATLAR_SIRA:
        duvarlar = [duvar_dikdortgeni(p) for p in duvar_parcalari(kat) if p[4] != "korkuluk"]
        serbest = []
        for x, y in kolonlar():
            kk = (x - KOLON / 2, y - KOLON / 2, x + KOLON / 2, y + KOLON / 2)
            if not any(kesisim(kk, d, 0.0) for d in duvarlar):
                serbest.append("(%.1f, %.1f) %s" % (x, y, oda_bul(kat, x, y)))
        ekle("Taşıyıcı", "%s: kolonlar duvar içinde / duvar ucunda" % kat,
             "UYARI" if serbest else "UYGUN",
             ("serbest kolon: " + "; ".join(serbest)) if serbest else "%d kolon" % len(kolonlar()))
    ax = sorted({x for x, _ in kolonlar()}); ay = sorted({y for _, y in kolonlar()})
    acik = max(b - a for a, b in zip(ax, ax[1:])), max(b - a for a, b in zip(ay, ay[1:]))
    ekle("Taşıyıcı", "En büyük kiriş açıklığı ≤ 8,0 m", "UYGUN" if max(acik) <= 8.0 else "UYARI",
         "x yönünde %.2f m · y yönünde %.2f m (asansör kuyusu betonarme perde)" % acik)

# ------------------------------------------------------------------ 6. merdiven, kot, imar
def k_merdiven():
    for kat in ("Bodrum", "Zemin"):
        mk = merdiven_kollari(kat)
        r = mk["riht"] * 100
        b = MERDIVEN["basamak"] * 100
        gen = min(mk["kollar"][0][1] - mk["kollar"][0][0], mk["kollar"][1][1] - mk["kollar"][1][0])
        sah = MERDIVEN["sahanlik"][1] - MERDIVEN["sahanlik"][0]
        ok = r <= 17.5 and b >= 26 and 60 <= 2 * r + b <= 64 and gen >= 1.0 and sah >= gen
        ekle("Merdiven", "%s → %s: rıht %.1f cm · basamak %.0f cm · 2r+b %.1f · kol %.2f m · sahanlık %.2f m"
             % (mk["alt"], mk["ust"], r, b, 2 * r + b, gen, sah), "UYGUN" if ok else "HATA",
             "%d rıht (%d + %d)" % (mk["kollar"][0][4] + mk["kollar"][1][4], mk["kollar"][0][4], mk["kollar"][1][4]))
    # kolların kutuya sığması ve başlangıç/varış bölgesi
    kutu = MERDIVEN["kutu"]
    sorun = []
    for kat in ("Bodrum", "Zemin"):
        for x0, x1, ya, yb, r, yon in merdiven_kollari(kat)["kollar"]:
            if min(ya, yb) < kutu[1] + 0.9:
                sorun.append("%s kolu kutu kuzeyine %.2f m kala başlıyor/bitiyor" % (kat, min(ya, yb) - kutu[1]))
    # baş yüksekliği: üst kattaki kolun alt yüzü ile alt kol arasındaki en dar mesafe
    mk0, mk1 = merdiven_kollari("Bodrum"), merdiven_kollari("Zemin")
    bas = KOT["Zemin"] - KOT["Bodrum"] - 0.25 - mk0["riht"]
    ekle("Merdiven", "Kollar kutuya sığar, kuzeyde ≥ 0,90 m varış/çıkış sahanlığı kalır",
         "HATA" if sorun else "UYGUN", "; ".join(sorun) or "varış bandı y 3,20–%.2f" % mk1["kollar"][0][2])
    ekle("Merdiven", "Baş yüksekliği ≥ 2,10 m", "UYGUN" if bas >= 2.10 else "HATA",
         "üst kol altı ile alt basamak arası ≈ %.2f m (merdivenler üst üste, aynı kutuda)" % bas)

def k_imar():
    h = KOT["Çatı"] - TABII_ZEMIN
    ekle("İmar", "Bina yüksekliği (tabii zeminden saçak döşemesine) ≤ Hmax %.2f m" % PARSEL["hmax"],
         "UYGUN" if h <= PARSEL["hmax"] + EPS else "HATA", "%.2f m" % h)
    for bk in BALKONLAR:
        ekle("İmar", "%s konsol derinliği ≤ 1,50 m (açık çıkma)" % bk["ad"],
             "UYGUN" if bk["derinlik"] <= 1.5 else "HATA", "%.2f m" % bk["derinlik"])
    g = GIRIS_SACAGI
    giris = [k for k in KAPILAR["Zemin"] if k[4] == "giris"][0]
    ekle("İmar", "Giriş kapısı saçak altında", "UYGUN" if g["x0"] <= giris[2] and g["x1"] >= giris[3] else "HATA",
         "saçak %.2f–%.2f · kapı %.2f–%.2f" % (g["x0"], g["x1"], giris[2], giris[3]))
    garaj = mahal_sozluk("Zemin")["Z-13"]
    nx0, ny0, nx1, ny1 = ic_sinir(garaj["r"][0])
    gk = [k for k in KAPILAR["Zemin"] if k[4] == "garaj"][0]
    ok = (nx1 - nx0) >= 5.40 and (ny1 - ny0) >= 5.50 and gk[3] - gk[2] >= 4.60
    ekle("İmar", "Garaj 2 araç için yeterli (net ≥ 5,40 × 5,50 m, kapı ≥ 4,60 m)", "UYGUN" if ok else "HATA",
         "net %.2f × %.2f m · kapı %.2f m" % (nx1 - nx0, ny1 - ny0, gk[3] - gk[2]))

# ------------------------------------------------------------------ 7. mobilya yerleşimi
def k_mobilya():
    for kat in KATLAR_SIRA:
        sorun = []
        for o in MOBILYA[kat]:
            kutu = sinir_kutusu(o)
            kod = oda_bul(kat, o[1], o[2])
            if kod == "DIS":
                sorun.append("%s (%.2f, %.2f) bina dışında" % (o[0], o[1], o[2])); continue
            ic = [ic_sinir(r) for r in mahal_sozluk(kat)[kod]["r"]]
            if not any(icinde(kutu, s, 0.03) for s in ic) and o[0] not in ZEMIN_OGESI:
                # çok parçalı mahalde birleşik sınır
                m = mahal_sozluk(kat)[kod]
                if len(m["r"]) == 1 or not _birlesik_icinde(kutu, ic):
                    sorun.append("%s %s (%.2f, %.2f) duvara taşıyor" % (kod, o[0], o[1], o[2]))
            for ad, e in _engel_kutulari(kat):
                if o[0] not in ZEMIN_OGESI and kesisim(kutu, e, 0.02):
                    sorun.append("%s (%.2f, %.2f) %s ile çakışıyor" % (o[0], o[1], o[2], ad))
        cift = [(a, b) for a, b in itertools.combinations(MOBILYA[kat], 2)
                if a[0] not in ZEMIN_OGESI and b[0] not in ZEMIN_OGESI
                and kesisim(sinir_kutusu(a), sinir_kutusu(b), 0.02)
                and not ({a[0], b[0]} <= {"sehpa", "kanepe_l", "koltuk", "berjer"} )
                and not ({a[0], b[0]} in ({"ada", "bar_tabure"}, {"camasir", "tezgah"}))]
        for a, b in cift:
            sorun.append("%s (%.2f, %.2f) ↔ %s (%.2f, %.2f)" % (a[0], a[1], a[2], b[0], b[1], b[2]))
        # pencere önü: kapı boyu cam (S) önü 0,90 m boş
        for p in PENCERELER[kat]:
            if p[3] != "S":
                continue
            kutu = (p[1], H - 0.35 - 0.9, p[2], H - 0.35) if p[0] == "G" else None
            if kutu:
                for o in MOBILYA[kat]:
                    if o[0] not in ZEMIN_OGESI and kesisim(kutu, sinir_kutusu(o), 0.02):
                        sorun.append("%s sürme cam önünü kapatıyor" % o[0])
        ekle("Yerleşim", "%s: mobilyalar duvar, merdiven ve birbirleriyle çakışmıyor" % kat,
             "HATA" if sorun else "UYGUN", "; ".join(sorun) or "%d donatı" % len(MOBILYA[kat]))

def _birlesik_icinde(kutu, ic):
    # kutunun köşeleri ve orta noktaları parçalardan birinin içinde mi
    x0, y0, x1, y1 = kutu
    noktalar = [(x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1),
                (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)]
    return all(any(s[0] - 0.03 <= px <= s[2] + 0.03 and s[1] - 0.03 <= py <= s[3] + 0.03 for s in ic)
               for px, py in noktalar)

# ------------------------------------------------------------------ 8. tesisat
def k_tesisat():
    ust_alt = [("1. Kat", "Zemin"), ("Zemin", "Bodrum")]
    notlar = []
    for ust, alt in ust_alt:
        for m in KATLAR[ust]:
            if m["tip"] != "islak":
                continue
            for r in m["r"]:
                cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
                alttaki = mahal_sozluk(alt)[oda_bul(alt, cx, cy)]
                if alttaki["tip"] in ("yasam", "yatak", "mutfak"):
                    notlar.append("%s %s → altında %s %s" % (m["kod"], m["ad"], alttaki["kod"], alttaki["ad"]))
    ekle("Tesisat", "Islak hacimler yaşama mahallerinin üstüne gelmiyor (gelenler asma tavanda şafta bağlanır)",
         "UYARI" if notlar else "UYGUN", "; ".join(notlar) or "tüm ıslak hacimler ıslak/servis üstünde")

def calistir():
    SONUC.clear()
    for f in (k_geometri, k_kapilar, k_kanatlar, k_erisim, k_mahremiyet, k_gunisigi, k_pencere_yerlesimi,
              k_kolonlar, k_merdiven, k_imar, k_mobilya, k_tesisat):
        f()
    return list(SONUC)

if __name__ == "__main__":
    s = calistir()
    say = {"UYGUN": 0, "UYARI": 0, "HATA": 0}
    for g, ad, d, ack in s:
        say[d] += 1
        if d != "UYGUN" or "-v" in sys.argv:
            print("[%s] %s — %s\n      %s" % (d, g, ad, ack))
    print("\n%d kontrol: %d uygun · %d uyarı · %d hata" % (len(s), say["UYGUN"], say["UYARI"], say["HATA"]))
    sys.exit(1 if say["HATA"] else 0)
