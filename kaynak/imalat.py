# -*- coding: utf-8 -*-
"""İmalat tanımları (poz), marka seçimleri ve mahal-poz ataması."""
from veri import KATLAR

# kod: (ad, teknik tanım, marka / ürün seçimi)
POZ = {
# ---- döşeme
"DK-01": ("Porselen seramik 60×120", "Rektifiyeli 1. sınıf porselen 60×120 cm, 2 mm derz, C2TE sınıfı yapıştırıcı, silikonlu derz dolgusu; yerden ısıtmaya uygun.", "Seranit veya Kalebodur 60×120 rektifiye · yapıştırıcı Kalekim Ultrafleks · derz Kalekim Fuga Star"),
"DK-02": ("Doğal taş (traverten / mermer)", "60×60 veya 60×120 cm, 2 cm kalınlık, cilalı-mat; leke tutmaz emprenye uygulamalı.", "Temmer Marble veya Karmer traverten (Afyon/Burdur bej) · emprenye Akemi Nano Effect"),
"DK-03": ("Lamine meşe parke 14 mm", "Çok katmanlı lamine meşe, üst tabaka ≥3 mm, yağlı-mat yüzey, tam yapıştırmalı; yerden ısıtma uyumlu.", "Barlinek Pure veya Tarkett Heritage · yapıştırıcı Sika SikaBond-54 · su bazlı yağ Osmo"),
"DK-04": ("Anti-slip porselen (ıslak hacim)", "R10–R11 kaymaz porselen 60×60 cm, eğimli şap, gizli süzgeç, su yalıtımı üzerine.", "VitrA Nanoflex veya Seranit Riverstone R11 · süzgeç Geberit CleanLine veya ACO"),
"DK-05": ("Dış mekan doğal taş / porselen", "Don dayanımlı (≥20 çevrim), R11 kaymaz, 2 cm; drenajlı kot, açık derz.", "Seranit Outdoor 2 cm veya andezit (Ankara/Nevşehir) · kaide Fixing Plus"),
"DK-06": ("Epoksi kaplama", "3 mm çift bileşenli epoksi, anti-toz, araç yüküne dayanıklı, süzgece eğimli.", "Sika Sikafloor-264 veya BASF MasterTop 1200"),
"DK-07": ("LVT / kauçuk spor zemin", "4–5 mm click LVT, yüksek aşınma sınıfı; spor alanında 8 mm kauçuk şok emici alt katman.", "Tarkett iD Inspiration 55 · spor zemin Regupol Everroll"),
"DK-08": ("Şap üzeri seramik (depo)", "1. sınıf seramik 45×45 cm, düz derz; depo ve teknik hacimler.", "Kalebodur veya Ege Seramik"),
# ---- süpürgelik
"SP-01": ("MDF lake süpürgelik h=10 cm", "Ham MDF üzeri akrilik lake, gizli montaj, akrilik mastik bitiş.", "Starwood/Kastamonu MDF gövde · lake AkzoNobel veya Marshall Akrilik"),
"SP-02": ("Taş süpürgelik h=8 cm", "Döşeme kaplamasıyla aynı taştan kesme, cilalı kenar.", "Döşeme taşı ile aynı parti (Temmer / Karmer)"),
"SP-03": ("Gizli alüminyum süpürgelik h=6 cm", "Sıva içine gömülü alüminyum profil, duvarla aynı düzlemde, gizli LED opsiyonlu.", "Asaş veya Sistem Alüminyum gizli süpürgelik profili"),
"SP-04": ("Seramik süpürgelik h=8 cm", "Döşeme seramiğinden kesme süpürgelik.", "Döşeme seramiği ile aynı parti"),
"SP-05": ("Süpürgelik yok", "Duvar kaplaması zemine kadar indiği için süpürgelik uygulanmaz.", "—"),
# ---- duvar
"DV-01": ("Alçı sıva + saten + mat boya", "Makine sıvası + saten alçı + astar + silikon esaslı yıkanabilir mat iç cephe boyası (2 kat).", "Sıva/saten Knauf veya Dalsan · boya Filli Boya Momento Kadife ya da Marshall Maestro"),
"DV-02": ("Porselen duvar kaplaması", "60×120 rektifiyeli porselen, su yalıtımı üzerine, küf önleyici derz, köşede alüminyum profil.", "Seranit / VitrA 60×120 · derz Kalekim Fuga Star Antibakteriyel"),
"DV-03": ("Doğal taş / mermer duvar kaplaması", "Kitap açılımı (book-match) mermer veya traverten panel; ebeveyn banyo ve salon TV duvarı.", "Temmer Marble book-match · montaj Kalekim Marbleflex"),
"DV-04": ("Dekoratif aksan duvar", "Duvar kağıdı, ahşap lamel panel veya mikro beton efekt; oda başına bir aksan duvar.", "AGT lamel panel veya Vescom duvar kaplaması · mikro beton Baumit"),
"DV-05": ("Su itici alçı levha + boya", "Nem dayanımlı (yeşil) alçı levha bölme, taşyünü dolgu, su itici macun + boya.", "Knauf Aquapanel / Dalsan Nem Levhası · boya Marshall Banyo-Mutfak"),
"DV-06": ("Brüt beton üzeri plastik boya", "Düzeltilmiş beton / kaba sıva üzeri astar + plastik boya.", "DYO veya Marshall plastik boya"),
"DV-07": ("Akustik duvar paneli", "Kumaş kaplı akustik panel veya delikli ahşap panel + taşyünü dolgu.", "Vicoustic veya Knauf Cleaneo · dolgu İzocam Taşyünü"),
"DV-08": ("Sauna iç kaplaması", "Kanada sediri veya ısıl işlem görmüş ladin lambri, reçine akıtmayan, ısıya dayanıklı.", "Harvia sedir paneli veya Lunawood ThermoWood"),
# ---- tavan
"TV-01": ("Asma tavan + gizli LED nişi", "Alçı levha asma tavan, saten + mat boya, çevre gizli LED nişi, spot delikleri, denetim kapağı.", "Knauf / Dalsan levha · armatür Lamp83 veya Osram · şerit LED Arlight"),
"TV-02": ("Alçı sıva + tavan boyası", "Beton tavan üzeri alçı sıva + saten + tavan boyası (2 kat), sarkıt ankrajı.", "Filli Boya Tavan · Dalsan saten"),
"TV-03": ("Nem dayanımlı asma tavan", "Nem dayanımlı alçı levha veya alüminyum kaset; aspiratör, spot ve denetim kapağı entegre.", "Dalsan yeşil levha veya Hunter Douglas alüminyum kaset"),
"TV-04": ("Ahşap lamel tavan kaplaması", "Ahşap veya ahşap görünümlü alüminyum lamel; kapalı veranda, teras ve balkon altı.", "Lunawood ThermoWood veya AGT dış cephe lameli"),
"TV-05": ("Boyalı brüt beton tavan", "Tesisat görünür, astar + plastik boya; garaj, teknik hacim ve depo.", "DYO plastik boya"),
"TV-06": ("Akustik asma tavan", "Delikli alçı levha / akustik kaset + taşyünü dolgu; ev sineması.", "Knauf Cleaneo Akustik · dolgu İzocam"),
# ---- kapı
"KP-01": ("Villa giriş kapısı", "Çelik iskelet, dış cephe uyumlu kompozit/ahşap kaplama, 110×220 cm, ısı-ses yalıtımlı, akıllı kilit.", "Kale Çelik Kapı Villa serisi veya Sur Kapı · kilit Yale Linus ya da Kale Kilit Akıllı"),
"KP-02": ("Lake iç kapı 90×220", "Amerikan panel gövde üzeri akrilik lake, gizli menteşe, manyetik dil, MDF lake kasa ve pervaz.", "Özel üretim lake kapı · menteşe/kilit Häfele veya Hoppe · lake AkzoNobel"),
"KP-03": ("Islak hacim kapısı", "Nem dayanımlı gövde, alt havalandırma, paslanmaz aksesuar, iç kilit.", "Özel üretim nem dayanımlı kapı · aksesuar Häfele"),
"KP-04": ("Sürgülü / gizli kasa kapı", "Duvar içine gömülü ray sistemli sürgülü kapı.", "Eclisse veya Häfele Slido gizli kasa sistemi"),
"KP-05": ("Yangın kapısı EI30", "Kazan dairesi ve teknik hacim girişi, kendiliğinden kapanır, duman sızdırmaz fitilli, sertifikalı.", "Hörmann H3-D veya Kale EI30 sertifikalı yangın kapısı"),
"KP-06": ("Otomatik seksiyonel garaj kapısı", "Yalıtımlı panel, motorlu, uzaktan kumanda + akıllı ev entegrasyonu, fotosel güvenlik.", "Hörmann LPU 42 + ProMatic motor (alternatif: Sarıcalar)"),
"KP-07": ("Cam kapı / cam bölme", "8–10 mm temperli cam, alüminyum çerçeve veya çerçevesiz menteşe; sauna ve duş bölmeleri.", "Şişecam temperli cam · aksesuar Häfele veya Sarayli"),
"KP-08": ("Depo / teknik kapı", "Boyalı çelik veya laminat kapı, kilitli.", "Standart çelik kapı · kilit Kale Kilit"),
# ---- doğrama
"DG-01": ("Alüminyum pencere (ısı yalıtımlı)", "Poliamid bariyerli alüminyum profil, antrasit elektrostatik boya, 4+16Ar+4 Low-E ısıcam, çift açılım.", "Schüco AWS 75 veya Çuhadaroğlu / Asaş yalıtımlı seri · cam Şişecam Isıcam Konfor + argon"),
"DG-02": ("Lift & slide sürme cam sistem", "Sürme kanatlı, geniş açıklıklı, alçak eşikli; salon-teras ve veranda geçişi.", "Schüco ASS 70 HI veya Çuhadaroğlu sürme sistem"),
"DG-03": ("Bodrum ışıklık penceresi", "Işıklığa bakan pencere, dıştan galvaniz ızgara/korkuluk, drenajlı ışıklık.", "Asaş alüminyum · ızgara galvaniz çelik (özel üretim)"),
"DG-04": ("Çatı penceresi", "Isıcamlı çatı penceresi, sineklik ve karartma perdesi.", "Velux GGU veya Fakro"),
"DG-05": ("Motorlu panjur / güneş kırıcı", "Alüminyum motorlu panjur veya dış jaluzi; yatak odaları ve güneybatı cephesi.", "Somfy motor + Asaş panjur kutusu"),
"DG-06": ("Sineklik", "Plise veya sürme sineklik, doğrama rengiyle aynı.", "Asaş veya Öztek plise sineklik"),
"DG-07": ("Doğrama yok", "Penceresiz mahal; mekanik havalandırma ile çözülür.", "—"),
# ---- elektrik
"EL-01": ("Standart oda tesisatı", "6 priz, 2 TV+data, komütatör/vaviyen anahtar, sarkıt + spot devresi, perde motoru beslemesi, duman dedektörü.", "Anahtar-priz Viko by Panasonic Novella veya Legrand Valena · kablo Öznur / Prysmian"),
"EL-02": ("Islak hacim tesisatı", "IP44 priz, ayna aydınlatma + ayna ısıtıcı beslemesi, havlupan beslemesi, aspiratör senkronu, kaçak akım koruma.", "Legrand Plexo IP44 · kaçak akım rölesi Schneider veya ABB"),
"EL-03": ("Mutfak tesisatı", "Ankastre fırın, ocak, bulaşık makinesi, davlumbaz ve buzdolabı için ayrı sigortalı hatlar; tezgah üstü 6 priz, gömme priz kutusu, tezgah altı LED.", "Schneider Unica · gömme priz Evoline Port · LED Osram"),
"EL-04": ("Salon / yaşam alanı tesisatı", "Senaryolu dimmerli aydınlatma, gizli LED nişi, TV için gömme kanal, 10 priz, data ve ses altyapısı.", "KNX: Jung / Gira veya Schneider KNX · kablosuz alternatif: Somfy TaHoma"),
"EL-05": ("Teknik hacim tesisatı", "Ana pano / kat panosu, seyyar priz, acil aydınlatma, kazan ve hidrofor beslemesi, IP54 armatür.", "Pano Schneider Prisma veya ABB · armatür Lamp83 IP54"),
"EL-06": ("Dış mekan tesisatı", "IP65 armatür, bahçe ve cephe aydınlatması, kapaklı dış priz, kamera ve otomatik kapı beslemesi.", "Lamp83 / Fumagalli IP65 · kamera Hikvision veya Dahua"),
"EL-07": ("Sinema / hobi tesisatı", "Projeksiyon ve perde beslemesi, 7.1 hoparlör kablolaması, gömme kanal, ışık senaryosu, ses yalıtımlı buat.", "Kablolama Belden / Klotz · kumanda KNX (Jung)"),
"EL-08": ("Garaj tesisatı", "IP54 armatür, garaj kapısı motor beslemesi, elektrikli araç şarjı için 3 faz 11 kW hat, kapaklı priz.", "Şarj ünitesi Vestel EVC04 veya ABB Terra AC · pano Schneider"),
"EL-09": ("Akıllı ev ana altyapısı", "KNX ana hat, zayıf akım panosu, CAT6 yıldız topoloji, IP kamera NVR, görüntülü diyafon, alarm paneli.", "KNX Jung/Gira · switch Ubiquiti UniFi · diyafon Comelit veya Multitek · alarm Paradox"),
# ---- mekanik
"MK-01": ("Yerden ısıtma", "Kollektörlü serpantin, ısı yalıtım levhası + şap, mahal bazlı oda termostatı (akıllı ev entegre).", "Boru Uponor Comfort Pipe veya Rehau Rautitan · kollektör Danfoss · termostat Honeywell Evohome"),
"MK-02": ("Yerden ısıtma + havlupan", "MK-01'e ek olarak havlupan radyatör (karışımlı veya elektrikli).", "Havlupan Zehnder veya Demirdöküm · vana Danfoss"),
"MK-03": ("VRF / multi-split iç ünite", "Gizli tavan tipi veya duvar tipi iç ünite, drenaj hattı, kablolu kumanda.", "Daikin VRV 5 veya Mitsubishi Electric City Multi (alternatif: Toshiba)"),
"MK-04": ("Mekanik havalandırma", "Kanal tipi sessiz aspiratör, çatıya/cepheye atış, anahtar veya nem sensörüyle otomatik.", "Vortice veya Systemair kanal tipi fan"),
"MK-05": ("Davlumbaz ve mutfak havalandırması", "Ankastre davlumbaz + paslanmaz kanalla çatıya atış, geri akış klapesi.", "Falmec veya Siemens iQ700 ada tipi davlumbaz"),
"MK-06": ("Kazan dairesi ekipmanı", "Yoğuşmalı kazan, 300 lt boyler, genleşme tankı, sirkülasyon pompaları, gaz dedektörü + selenoid vana, taze hava menfezi.", "Kazan Vaillant ecoTEC plus veya Buderus Logamax · boyler Vaillant uniSTOR · pompa Grundfos Alpha"),
"MK-07": ("Sauna ünitesi", "Elektrikli sauna sobası (hacme göre kW), kumanda paneli, hava giriş-çıkış menfezleri, ısıya dayanıklı armatür.", "Harvia Cilindro + Xenio kumanda (alternatif: Tylö)"),
"MK-08": ("Isıtma yok / temperli", "Isıtma tesisatı yapılmaz; komşu hacimden temperlenir. Donmaya karşı tesisat izolasyonu.", "—"),
"MK-09": ("Isı geri kazanımlı havalandırma (opsiyon)", "Merkezi ısı geri kazanım cihazı, kanal dağıtımı, F7 filtre.", "Systemair SAVE veya Zehnder ComfoAir"),
# ---- sıhhi tesisat
"ST-01": ("Tesisat yok", "Su ve atık tesisatı bulunmaz.", "—"),
"ST-02": ("Banyo tam donanım", "Gömme rezervuarlı asma klozet, tezgah üstü lavabo, ankastre batarya, duş nişi + yağmurlama duş, gizli süzgeç, ara vanalar.", "VitrA Metropole veya Duravit ME · rezervuar Geberit Sigma · armatür Grohe Grohtherm / Hansgrohe"),
"ST-03": ("Ebeveyn banyo donanımı", "ST-02'ye ek: çift lavabo, ankastre termostatik batarya, serbest duran küvet, taharet/bide, havlupan bağlantısı.", "Duravit veya Villeroy&Boch küvet · armatür Hansgrohe Axor · duş Grohe Rainshower 360"),
"ST-04": ("WC donanımı", "Asma klozet + gömme rezervuar, lavabo, ankastre batarya, taharet musluğu.", "VitrA / Roca · Geberit gömme rezervuar · Grohe armatür"),
"ST-05": ("Mutfak donanımı", "Granit veya paslanmaz eviye, ankastre batarya, bulaşık makinesi bağlantısı, su arıtma altyapısı, yağ tutucu sifon.", "Eviye Franke veya Blanco · batarya Grohe Minta · arıtma BWT"),
"ST-06": ("Çamaşırhane donanımı", "Çamaşır ve kurutma makinesi bağlantısı, ön yıkama eviyesi, yer süzgeci, taşma koruma sensörü.", "Eviye Franke · süzgeç ACO · su kaçak sensörü Netatmo veya Grohe Sense"),
"ST-07": ("Teknik / garaj tesisatı", "Yer süzgeci, bahçe tipi çeşme, hortum bağlantısı.", "Süzgeç ACO · armatür Artema"),
"ST-08": ("Dış mekan tesisatı", "Bahçe çeşmesi, otomatik sulama vanası, teras süzgeci ve yağmur suyu drenajı.", "Sulama Hunter veya Rain Bird · süzgeç ACO Self"),
}

# ---- kaba yapı / genel imalatlar (mahale bağlı değil)
GENEL = [
 ("Taşıyıcı sistem", "Radye temel + betonarme perde/kolon-kiriş; TBDY-2018'e göre tasarım, C30/37 beton, B420C donatı.", "Hazır beton: Konya bölgesi TSE belgeli tesis · donatı İçdaş / Kardemir"),
 ("Bodrum su yalıtımı", "Bitümlü membran (çift kat) + drenaj levhası + çakıl dolgulu Ø150 drenaj borusu, temel altı 10 cm grobeton üzeri yalıtım.", "Membran Sika veya BTM · drenaj levhası Onduline / Izobu"),
 ("Dış duvar", "19 cm gaz beton veya tuğla + 8 cm XPS mantolama (λ ≤ 0,033) + kaplama. TS 825 3. bölge şartını sağlar.", "XPS Dow Styrofoam veya Austrotherm · sistem Baumit openSystem ya da Weber therm"),
 ("Dış cephe kaplaması", "Doğal taş (traverten/andezit) + ısı yalıtım sıvası, antrasit alüminyum denizlik ve damlalık profilleri.", "Taş: bölge ocakları (Afyon/Burdur/Nevşehir) · profil Asaş"),
 ("Çatı", "Kırma çatı, ahşap karkas; 14 cm taşyünü, su yalıtım örtüsü, nefes alan membran, kilitli kiremit, alüminyum oluk.", "Kiremit Kılıçoğlu veya Toprak Seramik · taşyünü İzocam · membran Dörken Delta"),
 ("Teras / balkon su yalıtımı", "Çift kat poliüretan esaslı su yalıtımı + ısı yalıtımı + şap, don dayanımlı kaplama, çizgisel drenaj.", "Sika Sikalastic veya BASF MasterSeal · drenaj ACO"),
 ("Islak hacim su yalıtımı", "Duvarda 200 cm, döşemede tam alan çimento esaslı çift bileşenli yalıtım, köşelerde bandaj.", "Kalekim Su Yalıtım 2K veya Weber Tec 822 · bandaj Kalekim"),
 ("Asansör", "4 duraklı (bodrum-zemin-1.kat-çatı arası), 4–6 kişilik, makine dairesiz, kuyu su yalıtımlı.", "Schindler 3300 veya Kone MonoSpace 500"),
 ("Peyzaj / dış alanlar", "Otomatik damlama + rotorlu sulama, bahçe aydınlatması, doğal taş yürüme yolu, çim ve bitkilendirme, otomatik bahçe kapısı.", "Sulama Hunter / Rain Bird · kapı otomasyonu Nice veya Came"),
 ("Güvenlik", "Alarm, çevre ve iç mekan IP kamera, görüntülü diyafon, bahçe kapısı otomasyonu.", "Alarm Paradox · kamera Hikvision · diyafon Comelit"),
]

# ---- mahal-poz ataması: tipe göre varsayılan
VARSAYILAN = {
 "yasam":       ("DK-03","SP-01","DV-01 + DV-04","TV-01","KP-02","DG-01","EL-04","MK-01 + MK-03","ST-01"),
 "ikincil":     ("DK-07","SP-01","DV-01 + DV-04","TV-01","KP-02","DG-03","EL-01","MK-01 + MK-03","ST-01"),
 "yatak":       ("DK-03","SP-01","DV-01 + DV-04","TV-01","KP-02","DG-01 + DG-05 + DG-06","EL-01","MK-01 + MK-03","ST-01"),
 "islak":       ("DK-04","SP-05","DV-02","TV-03","KP-03","DG-01","EL-02","MK-02 + MK-04","ST-02"),
 "mutfak":      ("DK-01","SP-04","DV-02 + DV-01","TV-01","KP-04","DG-01","EL-03","MK-01 + MK-05","ST-05"),
 "sirkulasyon": ("DK-02","SP-02","DV-01","TV-01","—","DG-01","EL-04","MK-01","ST-01"),
 "teknik":      ("DK-08","SP-04","DV-01","TV-05","KP-08","DG-07","EL-05","MK-08","ST-01"),
 "acik":        ("DK-05","SP-02","—","TV-04","—","DG-02","EL-06","—","ST-08"),
}

# mahal koduna özel değişiklikler: {kod: {sütun_index: değer}} + not
OZEL = {
 "B-01": ({0:"DK-06",2:"DV-06",3:"TV-05",4:"KP-06",5:"DG-03",6:"EL-08",8:"ST-07"},
          "Zemin süzgece eğimli; elektrikli araç şarjı için 3 faz 11 kW hat. Kapı 5,00 m seksiyonel."),
 "B-02": ({}, "Mini bar için su/atık altyapısı bırakılacak (opsiyon); hol ile geniş açık geçiş."),
 "B-03": ({0:"DK-07",2:"DV-07",3:"TV-06",4:"KP-02 (ses yalıtımlı)",5:"DG-07",6:"EL-07",7:"MK-01 + MK-04"},
          "Duvar ve tavanda akustik dolgu; kapı çift contalı ve eşik fitilli."),
 "B-04": ({2:"DV-06",4:"KP-05",5:"DG-03",7:"MK-06",8:"ST-07"},
          "Doğalgaz dedektörü + selenoid vana; taze hava menfezi yönetmelik ölçüsünde, yangın kapısı EI30."),
 "B-06": ({2:"DV-02 (h=150 cm)",5:"DG-03",7:"MK-04",8:"ST-06"},
          "Taşma koruma sensörü ve yer süzgeci zorunlu; tezgah altı makine yerleşimi."),
 "B-07": ({5:"DG-07"}, "Duvar boyu raf altyapısı."),
 "B-08": ({5:"DG-07",7:"MK-04"}, "Soğuk oda bölümü ayrı yalıtımlı, sabit havalandırmalı."),
 "B-09": ({2:"DV-06",5:"DG-07",8:"ST-07"}, "Paslanmaz veya polyester depo, taşma-boşaltma hattı, hidrofor titreşim takozu."),
 "B-10": ({2:"DV-06",5:"DG-07",6:"EL-09"}, "Ana dağıtım panosu ve zayıf akım panosu; akıllı ev ana kabini."),
 "B-11": ({0:"—",1:"—",2:"DV-06",3:"TV-05",4:"Asansör kabin kapısı",5:"DG-07"}, "4 duraklı makine dairesiz asansör; kuyu su yalıtımı ve süzgeci."),
 "B-12": ({5:"DG-07"}, "Spor ve sauna bölümüne hizmet eder."),
 "B-13": ({0:"DK-01",5:"DG-07"}, "Net genişlik 1,45 m (yönetmelik asgarisi 1,20 m)."),
 "B-14": ({0:"DK-02",5:"DG-07",7:"MK-04"}, "Sabit 14–16 °C için ayrı klima/nem kontrolü; ahşap şarap rafı."),
 "B-15": ({2:"DV-01 + ayna duvar",7:"MK-01 + MK-03 + MK-04",5:"DG-03"}, "8 mm kauçuk şok emici alt katman, tam boy ayna ve bale barı."),
 "B-16": ({2:"DV-02 + DV-08",4:"KP-07",5:"DG-07",7:"MK-07 + MK-04"}, "Sauna iç hacmi sedir kaplama; dinlenme alanı duştan ayrık."),
 "B-17": ({4:"KP-07",5:"DG-03"}, "Soyunma dolapları ve duş kabinleri."),
 "B-18": ({5:"DG-03"}, "Hizmet personeli veya uzun süreli misafir için; ensuite banyolu."),
 "B-19": ({5:"DG-03"}, "Duş kabinli."),
 "B-20": ({5:"DG-07"}, "Temizlik malzemesi ve süpürge dolabı, eviye bağlantısı."),
 "B-21": ({3:"—",5:"DG-03",8:"ST-08"}, "Işıklık tabanında drenaj, üstte galvaniz ızgara; bodruma doğal ışık ve havalandırma sağlar."),

 "Z-01": ({0:"DK-02",1:"SP-03",2:"DV-01 + DV-03 (TV duvarı)",4:"—",5:"DG-01 + DG-02"},
          "Galeri boşluğu; şömine için baca/tesisat opsiyonu. Yemek alanıyla açık geçiş."),
 "Z-02": ({0:"DK-02",1:"SP-03",4:"—"}, "Avize için tavanda taşıyıcı ankraj; mutfak ve salonla açık geçiş."),
 "Z-03": ({0:"DK-05",1:"SP-02",2:"DV-01 (dış cephe kaplaması)",3:"TV-04",4:"KP-07",5:"DG-02",6:"EL-06",7:"MK-08",8:"ST-08"},
          "Katlanır/sürme cam sistemle dört mevsim kullanım; tavanda ısıtıcı opsiyonu."),
 "Z-04": ({0:"DK-02",1:"SP-02",4:"KP-01",6:"EL-09"}, "Görüntülü diyafon, akıllı ev ana paneli, gömme paspas nişi."),
 "Z-05": ({0:"DK-02",1:"SP-02",4:"—"}, "Doğal taş basamak + rıht, 10 mm temperli cam korkuluk (h=110 cm), paslanmaz küpeşte."),
 "Z-06": ({}, "Ada tezgah; kuvars tezgah (Çimstone/Belenco), tezgah altı LED, çekmece içi priz."),
 "Z-07": ({3:"TV-03",4:"KP-02",7:"MK-04"}, "Arka mutfak: bulaşık ve hazırlık alanı, derin raflı kiler."),
 "Z-08": ({2:"DV-03",5:"DG-07",8:"ST-04"}, "Tezgah üstü çanak lavabo, ankastre batarya, dekoratif aydınlatma."),
 "Z-09": ({4:"KP-04",5:"DG-07",7:"MK-01"}, "Tavana kadar gardırop, havalandırma menfezi."),
 "Z-10": ({0:"—",1:"—",2:"DV-06",3:"TV-05",4:"Asansör kabin kapısı",5:"DG-07"}, "Asansör kuyusu ve tesisat şaftı; şaft yangın durdurucu ile katlarda kesilir."),
 "Z-11": ({0:"DK-02",5:"DG-07"}, "Misafir süitine ve ofise erişim; net genişlik 2,45 m."),
 "Z-12": ({}, "Giyinme nişi ve ensuite banyo ile süit kurgusu."),
 "Z-13": ({}, "Duş nişi gizli süzgeçli, cam duş kabini."),
 "Z-14": ({4:"KP-04",5:"DG-07",7:"MK-01 + MK-04"}, "Misafir süiti giyinme odası; sensörlü dolap içi aydınlatma."),
 "Z-15": ({0:"DK-03",6:"EL-01"}, "CAT6 data ve ayrı sigortalı priz hattı; kitaplık ankrajı."),
 "Z-16": ({}, "Yaz mutfağı ve barbekü; su-atık hattı, dış priz, üstü örtülü."),

 "K-01": ({}, "Giyinme ve banyo ile süit kurgusu; yatak başı çift yönlü anahtar."),
 "K-02": ({4:"KP-04",5:"DG-01",7:"MK-01 + MK-04"}, "Ada dolap, sensörlü dolap içi aydınlatma, tam boy ayna."),
 "K-03": ({2:"DV-03",8:"ST-03"}, "Çift lavabo, serbest duran küvet, yağmurlama duş, ayna ısıtıcı."),
 "K-04": ({4:"—"}, "TV ünitesi için gömme kanal; senaryolu aydınlatma. Balkona sürme kapı."),
 "K-05": ({4:"KP-04"}, "Kitaplık ankrajı, okuma aydınlatması, data hattı."),
 "K-06": ({}, "Ebeveyn ve aile oturma odasına açılan balkon; cam korkuluk, gizli drenaj."),
 "K-07": ({0:"DK-02",4:"—"}, "Galeri boşluğu çevresinde temperli cam korkuluk h=110 cm."),
 "K-08": ({2:"DV-05",4:"KP-04",5:"DG-07",7:"MK-04",8:"ST-06"}, "Üst kat çamaşır nişi; makine bağlantısı, yer süzgeci, taşma sensörü."),
 "K-09": ({}, "Gömme gardırop; ortak banyoya yakın."),
 "K-10": ({}, "Ensuite banyolu; gömme gardırop."),
 "K-11": ({}, "Duş kabinli, gizli süzgeçli."),
 "K-12": ({0:"—",1:"—",2:"DV-06",3:"TV-05",4:"Asansör kabin kapısı",5:"DG-07"}, "Asansör kuyusu ve tesisat şaftı."),
 "K-13": ({0:"DK-02",5:"DG-07"}, "Net genişlik 2,45 m; ortak banyo ve yatak odalarına erişim."),
 "K-14": ({}, "Küvet + duş; çocuk kullanımına uygun armatür yüksekliği."),
 "K-15": ({}, "Giyinme odası ile birlikte kullanılır."),
 "K-16": ({4:"KP-04",5:"DG-01",7:"MK-01 + MK-04"}, "Gömme dolap sistemi."),
 "K-17": ({}, "Gömme gardırop; çalışma masası için priz + data."),
 "K-18": ({}, "Yatak odası 5'e açılan balkon; korkuluk h=110 cm, tırmanmaya elverişsiz."),
}

SUTUNLAR = ["Döşeme", "Süpürgelik", "Duvar", "Tavan", "Kapı", "Doğrama / Pencere",
            "Elektrik", "Mekanik", "Sıhhi Tesisat"]

def mahal_satirlari():
    """[(kat, kod, ad, tip, net_alan, [9 poz], not), ...]"""
    from veri import net_alan
    cikti = []
    for kat, mahaller in KATLAR.items():
        for r in mahaller:
            kod, ad, tip = r[0], r[1], r[6]
            degerler = list(VARSAYILAN[tip])
            ozel, aciklama = OZEL.get(kod, ({}, ""))
            for i, v in ozel.items():
                degerler[i] = v
            a, dar, uzun = net_alan(r)
            cikti.append((kat, kod, ad, tip, a, dar, uzun, degerler, aciklama))
    return cikti

if __name__ == "__main__":
    s = mahal_satirlari()
    eksik = set()
    for row in s:
        for d in row[7]:
            for parca in d.replace("+", " ").split():
                p = parca.strip("()")
                if len(p) == 5 and p[2] == "-" and p not in POZ:
                    eksik.add(p)
    print("%d mahal, %d poz tanımı" % (len(s), len(POZ)))
    print("tanımsız poz kodu:", eksik or "yok")
