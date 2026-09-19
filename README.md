# Durunday Villa — ön tasarım dosyası

Konya / Meram / Durunday’da **1.001 m² parsel** üzerinde, **300 m² oturumlu, bodrumlu dubleks villa**
için hazırlanmış mimari ön tasarım (avan), mahal listesi, imalat tarifi ve marka seçimleri.

**Web sitesi:** https://emreceran.github.io/durunday-villa/

## İçerik

| Klasör / dosya | Açıklama |
|---|---|
| `docs/` | Yayınlanan web sitesi (GitHub Pages kaynağı) |
| `cizimler/` | Vaziyet planı, bodrum/zemin/1. kat planları, çatı planı ve kesit (SVG, 1:100) |
| `render/` | 3B render görselleri (giriş, bahçe, kuş bakışı, akşam) |
| `kaynak/` | **Tasarım dosyaları** — tüm çizim ve tabloları üreten Python kaynakları |
| `Durunday Villa - Mahal Listesi.xlsx` | 5 sekmeli mahal listesi (künye, mahal programı, mahal listesi, imalat + markalar, yönetmelik) |
| `Durunday Villa - Mahal Listesi.pdf` | Excel’in baskıya hazır çıktısı |
| `Durunday Villa - Cizimler.pdf` | Altı çizimin A3 yatay seti |

## Tasarım dosyaları (`kaynak/`)

Her şey tek bir veri kaynağından üretilir; bir mahalin ölçüsü değiştiğinde çizim, Excel ve site birlikte güncellenir.

| Dosya | Görevi |
|---|---|
| `veri.py` | Parsel/imar verisi, kat geometrisi ve mahaller (tek doğru kaynak). Çalıştırıldığında kapsama testi yapar. |
| `imalat.py` | 68 poz için teknik şartname, marka seçimleri ve mahal-poz ataması |
| `yonetmelik.py` | Planlı Alanlar İmar Yönetmeliği ve ilgili mevzuata göre uygunluk kontrolleri (geometriden hesaplanır) |
| `ciz.py` | SVG kat planı, vaziyet planı, çatı planı ve kesit üreticisi |
| `excel_yap.py` | Mahal listesi Excel’ini üretir |
| `site_yap.py` | `docs/` altındaki statik siteyi üretir |
| `render_3b.py` | Blender 4.2 betiği — 3B modeli `veri.py` geometrisinden kurar ve Cycles ile render alır |

```bash
cd kaynak
python3 veri.py        # geometri kontrolü
python3 ciz.py         # çizimleri üret
python3 excel_yap.py   # Excel'i üret
python3 site_yap.py    # siteyi üret

# 3B render (Blender 4.2 gerekir)
~/opt/blender-4.2.23-linux-x64/blender -b -P render_3b.py -- \
    --kadraj giris --ornek 96 --en 1600 --cikti ../render/giris.jpg
# kadrajlar: giris · bahce · kus · aksam
```

## Uyarı

Bu set **ön tasarım (avan)** niteliğindedir. Ruhsata esas mimari, statik, mekanik ve elektrik projeleri ile
zemin etüdü yetkili müellifler tarafından hazırlanıp ilgili idarece onaylanmalıdır. Parsel ve imar verileri
varsayımdır; Meram Belediyesi imar durumu belgesiyle teyit edilmelidir.
