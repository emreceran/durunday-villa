# Durunday Villa — CAD teslim dosyaları (DXF + DWG)

Avan proje çizim setinin (13 pafta) AutoCAD dosyaları. PDF setiyle birebir aynı içerik, aynı geometriden üretildi.

## Klasörler
| Klasör | İçerik |
|---|---|
| `dwg/` | AutoCAD 2018 DWG — pafta başına bir dosya (`DV-A-00` … `DV-A-12`) + tümü tek dosyada `DV-TUM-PAFTALAR.dwg` (13 layout) |
| `dxf/` | Aynı dosyaların DXF (R2018) karşılığı |
| `KATMAN-LISTESI.csv` | Kullanılan 78 katman: renk, çizgi tipi, kalınlık, içerik, dayanak, öğe sayısı |

## Çizim düzeni
- **Model alanı 1:1 gerçek ölçü, birim cm** (`INSUNITS = cm`). Planlarda bina köşesi (0,0)–(2000,1500); kesit ve görünüşlerde y = kot × 100 (±0.00 = 0).
- **Her pafta bir layout'ta:** A3 yatay, çerçeve + antet kâğıt alanında, çizimler ölçekli viewport'larda (1/100, vaziyet 1/200, detaylar 1/50). Viewport çerçeveleri yazdırılmayan `M-GOST-VPORT` katmanında.
- **Ölçüler gerçek DIMENSION nesnesidir** (dış ölçüler `M-GOST-DISOLCU`, iç ölçüler `M-GOST-ICOLCU`); değerler cm.
- **Taramalar gerçek HATCH nesnesidir** ve ayrı `-T` katmanlarındadır. Örnek: `M-DUVA-GAZBETON-T`, `M-TASI-BETONARME-T`.
- `0` katmanında çizim yoktur.

## Katman şeması
Çevre ve Şehircilik Bakanlığı **CADD Bilgisayar Destekli Tasarım ve Çizim Düzenleme Usul ve Esasları** (Yapı İşleri GM, 2016 / rev. 2020) mimari katmanları kullanıldı.
- **Ad biçimi:** `M-ÖĞE-MALZEME`.
- **Renk (ACI), çizgi tipi ve 1/100 kalınlık:** Tablo 3.8 ve 3.9'dan alındı.
- **Görünüşte görünen elemanlar:** derinliğe göre `-1` ya da `-2` sonekli katmanda. Örnek: `M-DUVK-DOGALTAS-1` cephe taşı, `M-PNKS-ALUMINYUM-2` kesitte arkada görünen doğrama.

Başlıca katmanlar:

| Eleman | Katman |
|---|---|
| Kolon, perde, kiriş, döşeme, temel | `M-TASI-BETONARME` (+ `-T` dolu tarama) |
| Duvar (gazbeton) | `M-DUVA-GAZBETON` (+ `-T`) |
| Isı / su yalıtımı | `M-ISYA-TASYUNU` |
| Pencere / doğrama | `M-PNKS-ALUMINYUM` |
| Kapı kanadı · kasası · açılım yayı | `M-KPKN-AHSAP` · `M-KPKS-AHSAP` · `M-GOST-ACYONU` |
| Merdiven | `M-MERD-BETONARME` |
| Korkuluk | `M-KORK-CAM` |
| Mobilya · vitrifiye/mutfak | `M-TEFR-MIMARI` · `M-TEFR-MEKANIK` |
| Akslar · aks balonları | `M-GOST-AKS` · `M-GOST-AKSPOZ` |
| Mahal adları · kotlar | `M-GOST-MAHALPOZ` · `M-GOST-PLANKOT` / `M-GOST-KESITKOT` |
| Kapı / pencere pozları | `M-GOST-KAPIPOZ` · `M-GOST-PENCEREPOZ` |
| Kesit hattı · üstte kalan (saçak, pergola) | `M-GOST-KESITHATTI` · `M-GOST-IZDUSUM` |
| Parsel · çekme mesafeleri | `M-GOST-PARSELSINR` · `M-GOST-YAPIYAKLAS` |

- **Türetilmiş katmanlar:** listede karşılığı olmayan birkaç eleman aynı formülle adlandırıldı: şaft, ışıklık, havuz, toprak, cephe ahşap kaplaması, aks balonu. Bunlar CSV'de "TÜRETİLMİŞ" diye işaretli.
- **2028 değişikliği:** 1 Eylül 2028'de yürürlüğe girecek *Mimarlık ve Mühendislik Projelerinin Dijital Olarak Hazırlanması Hakkında Yönetmelik* mimari önekini `MM-` yapıyor. Gerekirse tek ayarla üretilebilir.

## Bilinen sınırlar (avan)
- Kapı, pencere ve mobilya sembolleri **blok değil**, ayrı çizgiler olarak duruyor. Uygulama projesinde bloklaştırılması önerilir.
- Yazı stili Arial Narrow (`arialn.ttf`). Yoksa AutoCAD benzer bir yazıtipiyle gösterir.
- Parsel ve imar verileri varsayımdır; Meram Belediyesi imar durumu ile teyit edilmelidir.
