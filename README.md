# Durunday Villa — ön tasarım dosyası

Konya / Meram / Durunday’da **1.001 m² parsel** üzerinde, **300 m² oturumlu, bodrumlu dubleks villa**
için hazırlanmış mimari ön tasarım (avan), mahal listesi, imalat tarifi ve marka seçimleri.

**Web sitesi:** https://emreceran.github.io/durunday-villa/

## İçerik

| Klasör / dosya | Açıklama |
|---|---|
| `docs/` | Yayınlanan web sitesi (GitHub Pages kaynağı) |
| `cizimler/` | 13 A3 antetli pafta (SVG): kapak, vaziyet 1/200, bodrum/zemin/1. kat planları, çatı, A–A ve B–B kesitleri, 4 görünüş, sistem kesiti 1/50, merdiven detayı 1/50, doğrama listesi |
| `render/` | 3B render görselleri (giriş, bahçe, kuş bakışı, akşam, salon iç mekan) |
| `kaynak/` | **Tasarım dosyaları** — tüm çizim ve tabloları üreten Python kaynakları |
| `Durunday Villa - Mahal Listesi.xlsx` | 6 sekme: künye, mahal programı, mahal listesi, imalat + markalar, yönetmelik, tasarım kontrolü |
| `Durunday Villa - Mahal Listesi.pdf` | Excel’in baskıya hazır çıktısı |
| `Durunday Villa - Cizimler.pdf` | 13 paftalık A3 yatay çizim seti |
| `cad/` | **DWG + DXF** çizim seti (mimara teslim): 1:1 cm model, pafta başına layout, ÇŞB CADD katman şeması — `cad/OKUBENI.md` |

## Tasarım dosyaları (`kaynak/`)

Her şey tek bir veri kaynağından üretilir; bir mahalin, kapının veya pencerenin ölçüsü değiştiğinde
çizim, kontrol, Excel, site ve 3B model birlikte güncellenir.

| Dosya | Görevi |
|---|---|
| `veri.py` | Parsel/imar, kotlar, aks-kolon ızgarası, mahaller, kapılar, pencereler, merdiven, dış elemanlar, mobilya (tek doğru kaynak) |
| `geometri.py` | Duvar parçaları, açıklıklar ve kapı kanatlarının geometrisi (çizim, kontrol ve 3B model ortak kullanır) |
| `kontrol.py` | Otomatik tasarım mantık kontrolü: erişim, mahremiyet, gün ışığı, kapı kanadı ve mobilya çakışması, kolon, merdiven, Hmax |
| `yonetmelik.py` | Planlı Alanlar İmar Yönetmeliği ve ilgili mevzuata göre uygunluk tablosu |
| `imalat.py` | Poz bazında teknik şartname, marka seçimleri ve mahal-poz ataması |
| `ciz.py` | Pafta çerçevesi + antet, kat planları (ölçü zincirleri, akslar, kotlar, mobilya, kapı/pencere kodları) |
| `paftalar.py` | Kapak, vaziyet, çatı, kesitler, görünüşler, sistem kesiti, merdiven detayı, doğrama listesi; tam seti yazar |
| `dograma.py`, `mobilya.py` | Kapı/pencere tip kodları; mobilya ölçüleri ve plan sembolleri |
| `excel_yap.py` · `pdf_yap.py` · `site_yap.py` | Excel, PDF (çizim seti + mahal listesi) ve `docs/` sitesi |
| `kayit.py` · `katmanlar.py` · `dxf_yap.py` | Çizim kaydı (katman + görünüş), ÇŞB katman şeması, DXF/DWG üretimi (ezdxf + ODA File Converter) |
| `render_3b.py` | Blender 4.2 betiği — 3B modeli `veri.py` geometrisinden kurar ve Cycles ile render alır |

```bash
cd kaynak
python3 veri.py        # geometri / merdiven özeti
python3 kontrol.py     # tasarım mantık kontrolü (hata varsa çıkış kodu 1)
python3 paftalar.py    # 13 paftayı üret (../cizimler)
python3 excel_yap.py   # Excel
python3 pdf_yap.py     # PDF'ler (Chrome + LibreOffice)
python3 site_yap.py    # site
python3 dxf_yap.py     # DXF + DWG seti (../cad) — ezdxf<1.2 ve ~/opt/oda (ODA File Converter) gerekir

# 3B render (Blender 4.2 gerekir; proje kökünden çalıştırın)
~/opt/blender-4.2.23-linux-x64/blender -b -P kaynak/render_3b.py -- \
    --kadraj giris --ornek 64 --en 1920 --cikti render/giris.jpg
# kadrajlar: giris · bahce · kus · aksam (ornek 96) · salon (iç mekan, ornek 128)
# hızlı ön izleme: --ornek 8 --en 800 ; çimsiz: CIMSIZ=1 ortam değişkeni
```

## Uyarı

Bu set **ön tasarım (avan)** niteliğindedir. Ruhsata esas mimari, statik, mekanik ve elektrik projeleri ile
zemin etüdü yetkili müellifler tarafından hazırlanıp ilgili idarece onaylanmalıdır. Parsel ve imar verileri
varsayımdır; Meram Belediyesi imar durumu belgesiyle teyit edilmelidir.
