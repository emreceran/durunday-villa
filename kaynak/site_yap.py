# -*- coding: utf-8 -*-
"""Statik web sitesini üretir (GitHub Pages için)."""
import os, shutil, html, datetime
from veri import KATLAR, PARSEL, BINA, KAT_YUKSEKLIK, NET_TAVAN, net_alan, kat_ozeti
from imalat import POZ, GENEL, SUTUNLAR, mahal_satirlari
from yonetmelik import KONTROLLER
from ciz import CIZIMLER

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(KOK, "docs")
E = lambda t: html.escape(str(t))

SAYFALAR = [("index.html", "Proje"), ("cizimler.html", "Çizimler"),
            ("mahal-listesi.html", "Mahal Listesi"), ("imalat.html", "İmalat ve Markalar"),
            ("yonetmelik.html", "Yönetmelik Uygunluk"), ("dosyalar.html", "Dosyalar")]

def kabuk(aktif, baslik, govde, aciklama=""):
    nav = "\n".join(
        '<a href="%s"%s>%s</a>' % (d, ' class="aktif"' if d == aktif else "", E(a))
        for d, a in SAYFALAR)
    return """<!DOCTYPE html>
<html lang="tr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s — Durunday Villa</title>
<meta name="description" content="%s">
<link rel="stylesheet" href="varlik/stil.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏠</text></svg>">
</head><body>
<header class="ust">
  <div class="sarmal ust-ic">
    <a class="marka" href="index.html"><span class="nokta"></span> Durunday Villa</a>
    <nav>%s</nav>
    <button class="tema" onclick="temaDegistir()" title="Açık / koyu tema">◐</button>
  </div>
</header>
<main class="sarmal">
%s
</main>
<footer class="alt"><div class="sarmal">
  <p><strong>Durunday Villa</strong> — Konya / Meram / Durunday · 300 m² oturumlu bodrumlu dubleks villa</p>
  <p class="kucuk">Ön tasarım (avan) dokümanı · %s · Uygulama ve ruhsat için yetkili proje müellifi onayı gerekir.</p>
</div></footer>
<script>
function temaDegistir(){const k=document.documentElement;const y=k.getAttribute('data-tema')==='koyu'?'acik':'koyu';
 k.setAttribute('data-tema',y);try{localStorage.setItem('tema',y)}catch(e){}}
(function(){try{const t=localStorage.getItem('tema');if(t)document.documentElement.setAttribute('data-tema',t)}catch(e){}})();
function tabloAra(girdi, tabloId){const s=girdi.value.toLocaleLowerCase('tr');
 document.querySelectorAll('#'+tabloId+' tbody tr').forEach(function(tr){
   tr.style.display = tr.textContent.toLocaleLowerCase('tr').indexOf(s)>-1 ? '' : 'none';});}
function katFiltre(btn, kat, tabloId){
 document.querySelectorAll('#'+tabloId+'-sekme .cip').forEach(b=>b.classList.remove('secili'));
 btn.classList.add('secili');
 document.querySelectorAll('#'+tabloId+' tbody tr').forEach(function(tr){
   tr.style.display = (kat==='*'||tr.dataset.kat===kat) ? '' : 'none';});}
</script>
</body></html>""" % (E(baslik), E(aciklama or baslik), nav, govde,
                     datetime.date.today().strftime("%d.%m.%Y"))

STIL = """
:root{
  --ze:#ffffff; --ze2:#f6f8fb; --ze3:#eef2f7; --yz:#111827; --yz2:#4b5563;
  --vurgu:#1d4ed8; --vurgu2:#1f3864; --cerceve:#dde3ea; --iyi:#047857; --uyari:#b45309;
}
:root[data-tema="koyu"]{
  --ze:#0f141b; --ze2:#151c25; --ze3:#1c242f; --yz:#e8edf3; --yz2:#9aa7b5;
  --vurgu:#7aa2ff; --vurgu2:#cbd9ff; --cerceve:#26303c; --iyi:#34d399; --uyari:#fbbf24;
}
@media (prefers-color-scheme: dark){ :root:not([data-tema="acik"]){
  --ze:#0f141b; --ze2:#151c25; --ze3:#1c242f; --yz:#e8edf3; --yz2:#9aa7b5;
  --vurgu:#7aa2ff; --vurgu2:#cbd9ff; --cerceve:#26303c; --iyi:#34d399; --uyari:#fbbf24; }}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--ze);color:var(--yz);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
.sarmal{max-width:1180px;margin:0 auto;padding:0 16px}
.ust{position:sticky;top:0;z-index:20;background:var(--ze);border-bottom:1px solid var(--cerceve)}
.ust-ic{display:flex;align-items:center;gap:18px;min-height:60px;flex-wrap:wrap}
.marka{font-weight:700;text-decoration:none;color:var(--yz);white-space:nowrap;display:flex;align-items:center;gap:8px}
.nokta{width:10px;height:10px;border-radius:50%;background:var(--vurgu);display:inline-block}
.ust nav{display:flex;gap:4px;flex-wrap:wrap;margin-left:auto}
.ust nav a{color:var(--yz2);text-decoration:none;padding:7px 11px;border-radius:8px;font-size:14.5px;white-space:nowrap}
.ust nav a:hover{background:var(--ze3);color:var(--yz)}
.ust nav a.aktif{background:var(--vurgu);color:#fff}
.tema{background:none;border:1px solid var(--cerceve);color:var(--yz2);border-radius:8px;
  width:34px;height:34px;cursor:pointer;font-size:15px}
main{padding:28px 0 56px}
h1{font-size:30px;line-height:1.25;margin:10px 0 6px}
h2{font-size:21px;margin:34px 0 12px;padding-bottom:8px;border-bottom:1px solid var(--cerceve)}
h3{font-size:16px;margin:22px 0 8px;color:var(--vurgu2)}
p{margin:10px 0}
.giris{color:var(--yz2);font-size:17px;max-width:70ch}
.kucuk{font-size:13.5px;color:var(--yz2)}
.kartlar{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:18px 0}
.kart{background:var(--ze2);border:1px solid var(--cerceve);border-radius:12px;padding:16px}
.kart .sayi{font-size:26px;font-weight:700;color:var(--vurgu)}
.kart .etiket{font-size:13.5px;color:var(--yz2);margin-top:2px}
.kart a{color:var(--vurgu);text-decoration:none;font-weight:600}
.kart a:hover{text-decoration:underline}
table{width:100%;border-collapse:collapse;font-size:14px;background:var(--ze)}
th,td{border:1px solid var(--cerceve);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--ze3);font-size:13px}
thead th{position:sticky;top:60px;z-index:5}
tbody tr:nth-child(even){background:var(--ze2)}
td.kod,th.kod{white-space:nowrap;font-weight:700;color:var(--vurgu)}
td.sayi{text-align:right;white-space:nowrap}
.kaydir{overflow-x:auto;border:1px solid var(--cerceve);border-radius:12px}
.kaydir table{border:0}
.araclar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:14px 0}
input[type=search]{flex:1;min-width:220px;padding:9px 12px;border:1px solid var(--cerceve);
  border-radius:9px;background:var(--ze2);color:var(--yz);font-size:15px}
.cip{border:1px solid var(--cerceve);background:var(--ze2);color:var(--yz2);border-radius:999px;
  padding:6px 13px;font-size:13.5px;cursor:pointer}
.cip.secili{background:var(--vurgu);border-color:var(--vurgu);color:#fff}
.rozet{display:inline-block;padding:2px 9px;border-radius:999px;font-size:12.5px;font-weight:600}
.rozet.iyi{background:rgba(4,120,87,.12);color:var(--iyi)}
.rozet.uyari{background:rgba(180,83,9,.14);color:var(--uyari)}
figure{margin:0 0 26px}
figure img{width:100%;height:auto;display:block;background:#fff;border:1px solid var(--cerceve);border-radius:12px}
figcaption{font-size:14px;color:var(--yz2);margin-top:8px;display:flex;gap:10px;flex-wrap:wrap}
figcaption a{color:var(--vurgu)}
.uyari-kutu{background:rgba(180,83,9,.09);border-left:4px solid var(--uyari);
  padding:12px 16px;border-radius:0 10px 10px 0;margin:18px 0;font-size:14.5px}
.alt{border-top:1px solid var(--cerceve);padding:22px 0;color:var(--yz2);font-size:14px;background:var(--ze2)}
.liste{list-style:none;padding:0;margin:14px 0}
.liste li{border:1px solid var(--cerceve);border-radius:11px;padding:13px 15px;margin-bottom:9px;background:var(--ze2);
  display:flex;gap:14px;align-items:center;flex-wrap:wrap}
.liste .ad{font-weight:600}
.liste a{margin-left:auto;color:var(--vurgu);text-decoration:none;font-weight:600;white-space:nowrap}
.marka-hucre{color:var(--vurgu2);font-weight:500}
@media(max-width:700px){ h1{font-size:24px} thead th{position:static} .ust nav{margin-left:0;width:100%} }
"""

def index():
    ozet = kat_ozeti()
    kapali = sum(v[0] for v in ozet.values()); acik = sum(v[1] for v in ozet.values())
    mahal_sayisi = sum(len(v) for v in KATLAR.values())
    g = ['<h1>Durunday Villa — ön tasarım dosyası</h1>',
         '<p class="giris">Konya / Meram / Durunday’da 1.001 m² parsel üzerinde, 300 m² oturumlu, '
         'bodrumlu dubleks villa için hazırlanmış mimari ön tasarım, mahal listesi, imalat tarifi ve '
         'marka seçimlerinden oluşan doküman seti. Tüm çizimler ve tablolar tek bir veri kaynağından üretilmiştir.</p>']
    g.append('<div class="kartlar">')
    for sayi, etiket in [("300 m²", "Oturum (taban) alanı"), ("900 m²", "Brüt inşaat alanı"),
                         ("%.0f m²" % kapali, "Net kapalı kullanım"), ("%.0f m²" % acik, "Teras ve balkon"),
                         (str(mahal_sayisi), "Mahal"), ("7", "Yatak odası")]:
        g.append('<div class="kart"><div class="sayi">%s</div><div class="etiket">%s</div></div>' % (E(sayi), E(etiket)))
    g.append('</div>')
    g.append('<h2>Doküman seti</h2><div class="kartlar">')
    for dosya, ad, ack in [
        ("cizimler.html", "Çizimler", "Vaziyet planı, üç kat planı, çatı planı ve kesit — ölçülendirilmiş, 1:100."),
        ("mahal-listesi.html", "Mahal Listesi", "55 mahal için döşeme, duvar, tavan, kapı, doğrama, elektrik, mekanik ve tesisat tarifi."),
        ("imalat.html", "İmalat ve Markalar", "68 poz için teknik şartname ve üst segment marka/ürün seçimi."),
        ("yonetmelik.html", "Yönetmelik Uygunluk", "Planlı Alanlar İmar Yönetmeliği ve ilgili mevzuata göre kontrol tablosu."),
        ("dosyalar.html", "Dosyalar", "Excel mahal listesi, PDF çıktılar ve çizim kaynak dosyaları."),
    ]:
        g.append('<div class="kart"><h3 style="margin-top:0">%s</h3><p class="kucuk">%s</p>'
                 '<a href="%s">Aç →</a></div>' % (E(ad), E(ack), dosya))
    g.append('</div>')
    g.append('<h2>Künye</h2><div class="kaydir"><table><tbody>')
    for k, v in [
        ("Yeri", "Konya, Meram ilçesi, Durunday mahallesi"),
        ("Yapı türü", "Ayrık nizam, tek aileli müstakil villa (dubleks)"),
        ("Parsel", "%.0f m² · %.2f × %.2f m (varsayım — imar durumu ile teyit edilecek)" % (PARSEL["alan"], PARSEL["en"], PARSEL["boy"])),
        ("TAKS / KAKS", "%.2f / %.2f" % (PARSEL["taks"], PARSEL["kaks"])),
        ("Bina oturumu", "%.2f × %.2f m" % (BINA["en"], BINA["boy"])),
        ("Katlar", "Bodrum + Zemin + 1. Normal kat + çatı arası"),
        ("Kat yükseklikleri", " · ".join("%s %.2f m (net %.2f m)" % (a, KAT_YUKSEKLIK[a], NET_TAVAN[a]) for a in KAT_YUKSEKLIK)),
        ("Taşıyıcı sistem", "Betonarme perde + çerçeve, radye temel (TBDY-2018)"),
        ("Isıtma / soğutma", "Yoğuşmalı kazan + yerden ısıtma · VRF gizli tavan tipi"),
        ("Kalite segmenti", "Üst segment"),
    ]:
        g.append("<tr><th style='width:220px'>%s</th><td>%s</td></tr>" % (E(k), E(v)))
    g.append('</tbody></table></div>')
    g.append('<div class="uyari-kutu"><strong>Uyarı.</strong> Bu set ön tasarım (avan) niteliğindedir. '
             'Ruhsata esas mimari, statik, mekanik ve elektrik projeleri ile zemin etüdü, yetkili müellifler '
             'tarafından hazırlanıp ilgili idarece onaylanmalıdır. Parsel ve imar verileri varsayımdır.</div>')
    return kabuk("index.html", "Proje", "\n".join(g),
                 "Konya Meram Durunday'da 300 m² oturumlu bodrumlu dubleks villa — mimari ön tasarım ve mahal listesi.")

def cizimler_sayfa():
    g = ['<h1>Çizimler</h1>',
         '<p class="giris">Ölçek 1:100 · ölçülendirilmiş · duvar kalınlıkları dış 35 cm, iç 15 cm. '
         'Her çizim SVG’dir; büyütmek için üzerine tıklayabilirsiniz.</p>']
    for dosya, ad, _ in CIZIMLER:
        g.append('<figure id="%s"><a href="varlik/%s.svg" target="_blank" rel="noopener">'
                 '<img src="varlik/%s.svg" alt="%s" loading="lazy"></a>'
                 '<figcaption><strong>%s</strong>'
                 '<a href="varlik/%s.svg" target="_blank" rel="noopener">SVG olarak aç ↗</a></figcaption></figure>'
                 % (dosya, dosya, dosya, E(ad), E(ad), dosya))
    return kabuk("cizimler.html", "Çizimler", "\n".join(g),
                 "Vaziyet planı, bodrum/zemin/1. kat planları, çatı planı ve kesit.")

def mahal_sayfa():
    satirlar = mahal_satirlari()
    g = ['<h1>Mahal Listesi</h1>',
         '<p class="giris">Her mahal için imalat tarifi. Poz kodlarının teknik tanımı ve marka seçimi '
         '<a href="imalat.html">İmalat ve Markalar</a> sayfasındadır. Alanlar net (duvar içi) değerlerdir.</p>']
    g.append('<div class="araclar" id="mahal-sekme">')
    g.append('<button class="cip secili" onclick="katFiltre(this,\'*\',\'mahal\')">Tümü</button>')
    for kat in KATLAR:
        g.append('<button class="cip" onclick="katFiltre(this,\'%s\',\'mahal\')">%s</button>' % (E(kat), E(kat)))
    g.append('<input type="search" placeholder="Mahal, malzeme veya poz kodu ara…" oninput="tabloAra(this,\'mahal\')">')
    g.append('</div>')
    g.append('<div class="kaydir"><table id="mahal"><thead><tr>'
             '<th class="kod">No</th><th>Mahal</th><th>Kat</th><th>m²</th>'
             + "".join("<th>%s</th>" % E(s) for s in SUTUNLAR)
             + '<th>Açıklama</th></tr></thead><tbody>')
    for kat, kod, ad, tip, alan, dar, uzun, degerler, aciklama in satirlar:
        g.append('<tr data-kat="%s"><td class="kod">%s</td><td><strong>%s</strong></td><td>%s</td>'
                 '<td class="sayi">%.1f</td>%s<td class="kucuk">%s</td></tr>'
                 % (E(kat), E(kod), E(ad), E(kat), alan,
                    "".join("<td>%s</td>" % E(d) for d in degerler), E(aciklama)))
    g.append('</tbody></table></div>')
    return kabuk("mahal-listesi.html", "Mahal Listesi", "\n".join(g),
                 "55 mahal için döşeme, duvar, tavan, kapı, doğrama, elektrik, mekanik ve sıhhi tesisat tarifi.")

def imalat_sayfa():
    gruplar = [("Döşeme kaplaması", "DK"), ("Süpürgelik", "SP"), ("Duvar", "DV"), ("Tavan", "TV"),
               ("Kapı", "KP"), ("Doğrama / pencere", "DG"), ("Elektrik", "EL"),
               ("Mekanik", "MK"), ("Sıhhi tesisat", "ST")]
    g = ['<h1>İmalat Tanımları ve Marka Seçimleri</h1>',
         '<p class="giris">Üst segment için hazırlanmış şartname. Marka ve ürünler örnek niteliğindedir; '
         'teklif aşamasında eşdeğer ürünler önerilebilir.</p>',
         '<div class="araclar"><input type="search" placeholder="Poz kodu, malzeme veya marka ara…" '
         'oninput="tabloAra(this,\'poz\')"></div>',
         '<div class="kaydir"><table id="poz"><thead><tr><th class="kod">Kod</th><th>İmalat</th>'
         '<th>Teknik tanım / şartname</th><th>Marka / ürün seçimi</th></tr></thead><tbody>']
    for grup_ad, on in gruplar:
        g.append('<tr style="background:var(--ze3)"><td colspan="4"><strong>%s</strong></td></tr>' % E(grup_ad))
        for kod in sorted(k for k in POZ if k.startswith(on)):
            ad, tanim, marka = POZ[kod]
            g.append('<tr><td class="kod">%s</td><td><strong>%s</strong></td><td>%s</td>'
                     '<td class="marka-hucre">%s</td></tr>' % (E(kod), E(ad), E(tanim), E(marka)))
    g.append('</tbody></table></div>')
    g.append('<h2>Genel yapım imalatları</h2><div class="kaydir"><table><thead><tr>'
             '<th>İmalat</th><th>Teknik tanım</th><th>Marka / ürün seçimi</th></tr></thead><tbody>')
    for ad, tanim, marka in GENEL:
        g.append('<tr><td><strong>%s</strong></td><td>%s</td><td class="marka-hucre">%s</td></tr>'
                 % (E(ad), E(tanim), E(marka)))
    g.append('</tbody></table></div>')
    return kabuk("imalat.html", "İmalat ve Markalar", "\n".join(g),
                 "68 poz için teknik şartname ve üst segment marka seçimleri.")

def yonetmelik_sayfa():
    g = ['<h1>Yönetmelik Uygunluk Kontrolü</h1>',
         '<p class="giris">Projenin geometrisi, Planlı Alanlar İmar Yönetmeliği ve ilgili mevzuatın '
         'asgari değerleriyle otomatik olarak karşılaştırılmıştır. Değerler çizim verisinden hesaplanır.</p>',
         '<div class="kaydir"><table><thead><tr><th>Konu</th><th>Yönetmelik asgarisi</th>'
         '<th>Projede</th><th>Durum</th><th>Dayanak / açıklama</th></tr></thead><tbody>']
    for konu, asgari, projede, durum, dayanak in KONTROLLER():
        rozet = "iyi" if durum == "UYGUN" else "uyari"
        g.append('<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td>'
                 '<td><span class="rozet %s">%s</span></td><td class="kucuk">%s</td></tr>'
                 % (E(konu), E(asgari), E(projede), rozet, E(durum), E(dayanak)))
    g.append('</tbody></table></div>')
    g.append('<div class="uyari-kutu">Kontrol tablosu bilgilendirme amaçlıdır; yürürlükteki yönetmelik metni, '
             'Meram Belediyesi imar durumu ve plan notları esastır. Ruhsat başvurusu öncesinde yetkili '
             'proje müellifi tarafından teyit edilmelidir.</div>')
    return kabuk("yonetmelik.html", "Yönetmelik Uygunluk", "\n".join(g),
                 "Planlı Alanlar İmar Yönetmeliği'ne göre piyes ölçüleri, merdiven, yükseklik ve otopark kontrolü.")

def dosyalar_sayfa(dosyalar):
    g = ['<h1>Dosyalar</h1>',
         '<p class="giris">Tasarım ve doküman dosyalarının tamamı. Çizimler vektörel (SVG) olduğundan '
         'kalite kaybı olmadan büyütülebilir ve CAD ortamına aktarılabilir.</p>', '<ul class="liste">']
    for ad, yol, ack in dosyalar:
        g.append('<li><span><span class="ad">%s</span><br><span class="kucuk">%s</span></span>'
                 '<a href="%s" download>İndir ↓</a></li>' % (E(ad), E(ack), yol))
    g.append('</ul>')
    g.append('<h2>Kaynak dosyalar</h2><p class="giris">Tüm çizimler ve tablolar '
             '<code>kaynak/</code> klasöründeki Python dosyalarından üretilir: '
             '<code>veri.py</code> (geometri ve mahaller), <code>imalat.py</code> (şartname ve markalar), '
             '<code>yonetmelik.py</code> (uygunluk kuralları), <code>ciz.py</code> (çizimler), '
             '<code>excel_yap.py</code> ve <code>site_yap.py</code>. '
             'Bir mahalin ölçüsü değiştiğinde çizim, Excel ve site birlikte güncellenir.</p>')
    return kabuk("dosyalar.html", "Dosyalar", "\n".join(g), "Excel, PDF ve SVG çizim dosyaları.")

def uret():
    os.makedirs(os.path.join(SITE, "varlik"), exist_ok=True)
    os.makedirs(os.path.join(SITE, "dosyalar"), exist_ok=True)
    with open(os.path.join(SITE, "varlik", "stil.css"), "w", encoding="utf-8") as f:
        f.write(STIL)
    for dosya, ad, _ in CIZIMLER:
        shutil.copy(os.path.join(KOK, "cizimler", dosya + ".svg"),
                    os.path.join(SITE, "varlik", dosya + ".svg"))
    dosyalar = []
    xlsx = "Durunday Villa - Mahal Listesi.xlsx"
    if os.path.exists(os.path.join(KOK, xlsx)):
        shutil.copy(os.path.join(KOK, xlsx), os.path.join(SITE, "dosyalar", "durunday-villa-mahal-listesi.xlsx"))
        dosyalar.append(("Mahal listesi (Excel)", "dosyalar/durunday-villa-mahal-listesi.xlsx",
                         "5 sekme: künye ve genel tanımlar, mahal programı, mahal listesi, imalat tanımları + markalar, yönetmelik kontrolü"))
    for ad, yerel, ack in [("Mahal listesi (PDF)", "durunday-villa-mahal-listesi.pdf",
                            "Excel’in baskıya hazır PDF çıktısı"),
                           ("Çizim seti (PDF)", "durunday-villa-cizimler.pdf",
                            "Altı çizimin A3 yatay PDF seti")]:
        if os.path.exists(os.path.join(SITE, "dosyalar", yerel)):
            dosyalar.append((ad, "dosyalar/" + yerel, ack))
    for dosya, ad, _ in CIZIMLER:
        dosyalar.append((ad + " (SVG)", "varlik/%s.svg" % dosya, "Vektörel çizim, 1:100"))
    sayfalar = {"index.html": index(), "cizimler.html": cizimler_sayfa(),
                "mahal-listesi.html": mahal_sayfa(), "imalat.html": imalat_sayfa(),
                "yonetmelik.html": yonetmelik_sayfa(), "dosyalar.html": dosyalar_sayfa(dosyalar)}
    for ad, icerik in sayfalar.items():
        with open(os.path.join(SITE, ad), "w", encoding="utf-8") as f:
            f.write(icerik)
    return list(sayfalar)

if __name__ == "__main__":
    print("üretildi:", ", ".join(uret()))
