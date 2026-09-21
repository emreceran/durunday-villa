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
"KP-01": ("Villa giriş kapısı", "Çelik iskelet, dış cephe uyumlu kompozit/ahşap kaplama, 110×240 cm, ısı-ses yalıtımlı, akıllı kilit.", "Kale Çelik Kapı Villa serisi veya Sur Kapı · kilit Yale Linus ya da Kale Kilit Akıllı"),
"KP-02": ("Lake iç kapı 90×210", "Amerikan panel gövde üzeri akrilik lake, gizli menteşe, manyetik dil, MDF lake kasa ve pervaz.", "Özel üretim lake kapı · menteşe/kilit Häfele veya Hoppe · lake AkzoNobel"),
"KP-03": ("Islak hacim kapısı", "Nem dayanımlı gövde, alt havalandırma, paslanmaz aksesuar, iç kilit.", "Özel üretim nem dayanımlı kapı · aksesuar Häfele"),
"KP-04": ("Sürgülü / gizli kasa kapı", "Duvar içine gömülü ray sistemli sürgülü kapı.", "Eclisse veya Häfele Slido gizli kasa sistemi"),
"KP-05": ("Yangın kapısı EI30", "Kazan dairesi ve teknik hacim girişi, kendiliğinden kapanır, duman sızdırmaz fitilli, sertifikalı.", "Hörmann H3-D veya Kale EI30 sertifikalı yangın kapısı"),
"KP-06": ("Otomatik seksiyonel garaj kapısı", "Yalıtımlı panel, motorlu, uzaktan kumanda + akıllı ev entegrasyonu, fotosel güvenlik.", "Hörmann LPU 42 + ProMatic motor (alternatif: Sarıcalar)"),
"KP-07": ("Cam kapı / cam bölme", "8–10 mm temperli cam, alüminyum çerçeve veya çerçevesiz menteşe; sauna ve duş bölmeleri.", "Şişecam temperli cam · aksesuar Häfele veya Sarayli"),
"KP-08": ("Depo / teknik kapı", "Boyalı çelik veya laminat kapı, kilitli.", "Standart çelik kapı · kilit Kale Kilit"),
"KP-09": ("Servis dış kapısı", "Isı yalıtımlı alüminyum kapı 90×210, antrasit, yarım buzlu cam, çok noktalı kilit.", "Schüco ADS 75 veya Asaş kapı serisi · kilit Kale / Roto"),
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
"MK-06": ("Kazan dairesi ekipmanı", "Hermetik yoğuşmalı kazan (baca şafttan çatıya) veya hava kaynaklı ısı pompası, 300 lt boyler, genleşme tankı, pompalar, gaz dedektörü + selenoid vana.", "Kazan Vaillant ecoTEC plus veya Buderus Logamax · boyler Vaillant uniSTOR · pompa Grundfos Alpha"),
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
 ("Dış duvar", "25 cm gazbeton (G2/04) + 8 cm taşyünü mantolama (λ ≤ 0,035) + zemin katta doğal taş, 1. katta ince silikon sıva. TS 825 3. bölge şartını sağlar.", "Gazbeton Akg / Türk Ytong · taşyünü İzocam veya Knauf Insulation · sistem Baumit ya da Weber therm"),
 ("Dış cephe kaplaması", "Zemin kat ve baca: 3 cm bej doğal taş (Sille taşı / traverten) mekanik ankrajlı; 1. kat: ince silikon sıva; kat silmesi beyaz GRC; antrasit alüminyum denizlik ve damlalık.", "Taş: Sille (Konya) veya Afyon/Burdur ocakları · ankraj Halfen · sıva Baumit SilikonTop"),
 ("Çatı", "Kırma çatı, ahşap karkas; 14 cm taşyünü, su yalıtım örtüsü, nefes alan membran, kilitli kiremit, alüminyum oluk.", "Kiremit Kılıçoğlu veya Toprak Seramik · taşyünü İzocam · membran Dörken Delta"),
 ("Teras / balkon su yalıtımı", "Çift kat poliüretan esaslı su yalıtımı + ısı yalıtımı + şap, don dayanımlı kaplama, çizgisel drenaj.", "Sika Sikalastic veya BASF MasterSeal · drenaj ACO"),
 ("Islak hacim su yalıtımı", "Duvarda 200 cm, döşemede tam alan çimento esaslı çift bileşenli yalıtım, köşelerde bandaj.", "Kalekim Su Yalıtım 2K veya Weber Tec 822 · bandaj Kalekim"),
 ("Asansör", "3 duraklı (bodrum-zemin-1. kat), 630 kg / 8 kişi, makine dairesiz; kuyu betonarme perde, su yalıtımlı.", "Schindler 3300 veya Kone MonoSpace 500"),
 ("Peyzaj / dış alanlar", "Otomatik damlama + rotorlu sulama, bahçe aydınlatması, doğal taş yürüme yolu, çim ve bitkilendirme, otomatik bahçe kapısı.", "Sulama Hunter / Rain Bird · kapı otomasyonu Nice veya Came"),
 ("Güvenlik", "Alarm, çevre ve iç mekan IP kamera, görüntülü diyafon, bahçe kapısı otomasyonu.", "Alarm Paradox · kamera Hikvision · diyafon Comelit"),
]

# ---- mahal-poz ataması: tipe göre varsayılan
# sütunlar: Döşeme, Süpürgelik, Duvar, Tavan, Kapı, Doğrama, Elektrik, Mekanik, Sıhhi tesisat
VARSAYILAN = {
 "yasam":       ("DK-03","SP-01","DV-01 + DV-04","TV-01","KP-02","DG-01","EL-04","MK-01 + MK-03","ST-01"),
 "ikincil":     ("DK-07","SP-01","DV-01","TV-01","KP-02","DG-07","EL-01","MK-01 + MK-04","ST-01"),
 "yatak":       ("DK-03","SP-01","DV-01 + DV-04","TV-01","KP-02","DG-01 + DG-05 + DG-06","EL-01","MK-01 + MK-03","ST-01"),
 "giyinme":     ("DK-03","SP-01","DV-01","TV-01","KP-02","DG-07","EL-01","MK-01 + MK-04","ST-01"),
 "islak":       ("DK-04","SP-05","DV-02","TV-03","KP-03","DG-01","EL-02","MK-02 + MK-04","ST-02"),
 "mutfak":      ("DK-01","SP-04","DV-02 + DV-01","TV-01","KP-04","DG-01","EL-03","MK-01 + MK-05","ST-05"),
 "sirkulasyon": ("DK-02","SP-02","DV-01","TV-01","—","DG-07","EL-04","MK-01","ST-01"),
 "teknik":      ("DK-08","SP-04","DV-01","TV-05","KP-08","DG-07","EL-05","MK-08","ST-01"),
 "garaj":       ("DK-06","SP-04","DV-06","TV-05","KP-06","DG-01","EL-08","MK-08","ST-07"),
 "merdiven":    ("DK-02","SP-02","DV-01","TV-02","—","—","EL-04","—","ST-01"),
 "asansor":     ("—","—","DV-06","TV-05","Asansör kat kapısı","DG-07","EL-05","—","ST-01"),
 "saft":        ("—","—","DV-06","—","Servis kapağı","DG-07","—","—","Düşey tesisat"),
 "bosluk":      ("—","—","DV-01","TV-01","—","DG-01","EL-04","—","ST-01"),
}

# mahal koduna özel değişiklikler: {kod: ({sütun_index: değer}, not)}
OZEL = {
 # ---------------- bodrum
 "B-01": ({2:"DV-07",3:"TV-06",4:"KP-02 (ses yalıtımlı)",6:"EL-07"}, "Penceresiz; duvar ve tavanda akustik dolgu, çift contalı kapı, 2 sıra 3'lü sinema koltuğu."),
 "B-02": ({5:"DG-03",7:"MK-01 + MK-03 + MK-04",8:"ST-05 (bar eviyesi)"}, "Bilardo + bar; batı ışıklığına bakan 340 cm pencere. Hole çift kanatlı kapı."),
 "B-03": ({5:"DG-03 + DG-06"}, "Misafir veya ev çalışanı için; batı ışıklığında dikme kaçış merdiveni (acil çıkış)."),
 "B-04": ({0:"DK-03",4:"KP-02"}, "Oda holü ve gömme dolap; oda ile banyoyu bodrum holünden ayırır."),
 "B-05": ({5:"DG-07"}, "Penceresiz; şafta bağlı mekanik havalandırma. Duş, lavabo, asma klozet."),
 "B-06": ({}, "Merdiven, asansör, depo ve odalara dağıtım holü; net genişlik 2,05 m."),
 "B-10": ({4:"KP-08"}, "Genel depo; duvar boyu raf, nem alma cihazı prizi."),
 "B-11": ({6:"EL-09"}, "Ana dağıtım panosu, zayıf akım kabini, akıllı ev ve NVR."),
 "B-12": ({0:"DK-01"}, "Teknik ve spa bölümüne servis koridoru; net genişlik 1,25 m."),
 "B-13": ({4:"KP-05",7:"MK-06",8:"ST-07"}, "EI30 kapı; hermetik kazan veya ısı pompası iç ünitesi, boyler, kollektörler; baca şafttan çatıya."),
 "B-14": ({2:"DV-06",8:"ST-07"}, "2 × 2,5 ton su deposu, hidrofor, titreşim takozu, taşma-boşaltma hattı."),
 "B-15": ({7:"MK-04"}, "Soğuk depo bölümü ayrı yalıtımlı, sabit havalandırma; iki yanda raf."),
 "B-16": ({8:"ST-07"}, "Havuz filtre, pompa, denge deposu ve dozaj ünitesi; havuza en kısa hat."),
 "B-17": ({4:"KP-03",5:"DG-07"}, "Soyunma dolapları, duş, bank; saunaya cam sürme kapı."),
 "B-18": ({0:"—",2:"DV-08",3:"DV-08",4:"KP-07",5:"DG-07",7:"MK-07 + MK-04"}, "Sedir kaplama, iki kademeli bank, elektrikli soba."),
 "B-19": ({0:"DK-07",5:"DG-03",7:"MK-01 + MK-03 + MK-04"}, "Doğu ışıklığına bakan pencere; kauçuk şok emici zemin, ayna duvar."),
 "B-20": ({}, "Hol deposu (bavul, mevsimlik eşya)."),
 "B-21": ({0:"DK-02",7:"MK-04 + ayrı klima (14–16 °C)"}, "Şarap rafları ve tadım masası; sabit ısı ve nem."),
 # ---------------- zemin
 "Z-01": ({0:"DK-02",4:"KP-01",5:"DG-01 (sabit yan cam)",6:"EL-09"}, "Galeri altında çift yükseklik giriş; gömme vestiyer dolabı, görüntülü diyafon, akıllı ev paneli."),
 "Z-02": ({0:"DK-02"}, "Girişten bahçeye görsel aks; merdiven, asansör, salon ve misafir süitine dağıtım."),
 "Z-06": ({}, "Misafir süiti — hol ve banyo ile; 1. kattaki yatak 2 süitiyle aynı aksta."),
 "Z-07": ({5:"DG-01 (buzlu)",8:"ST-02"}, "Duş, lavabo, asma klozet; kuzeyde yüksek pencere."),
 "Z-08": ({0:"DK-02"}, "Misafir süiti giriş holü, gömme dolap."),
 "Z-09": ({0:"DK-02",1:"SP-03",2:"DV-01 + DV-03 (şömine duvarı)",4:"KP-02 (çift kanat)",5:"DG-01 + DG-02"},
          "Şömine batı duvarında, baca dışta taş kütle; güneyde 540 cm kaldır-sür doğrama ile teras."),
 "Z-10": ({0:"DK-02",1:"SP-03",4:"—",5:"DG-02"}, "Salon ve mutfakla açık plan; 8 kişilik masa, büfe; güneyde 360 cm kaldır-sür."),
 "Z-11": ({5:"DG-01 + DG-02"}, "Ada tezgah (ocak + kahvaltı barı), doğu duvarında eviye tezgahı; pergolaya 540 cm kaldır-sür."),
 "Z-12": ({0:"DK-01"}, "Garaj, WC, kiler ve mutfağa servis koridoru; net 1,25 m."),
 "Z-13": ({7:"MK-08",5:"DG-01 (yüksek)"}, "2 araç; eve EI30 kapı ile bağlanır; elektrikli araç şarj hattı; seksiyonel kapı 480 × 240."),
 "Z-14": ({5:"DG-07",8:"ST-04"}, "Misafir WC; servis koridorundan girilir, salondan görünmez."),
 "Z-15": ({}, "Kiler: derin raflar, mutfağa yakın."),
 "Z-16": ({4:"KP-02 + KP-09 (dış servis kapısı)"}, "Arka mutfak ve servis girişi: bulaşık, hazırlık, market girişi doğu yan bahçeden."),
 # ---------------- 1. kat
 "K-01": ({0:"DK-02"}, "Galeriye bakan okuma köşesi; cam korkuluk h=110."),
 "K-06": ({}, "Süit: hol + banyo; kuzey ve batı pencereli köşe oda."),
 "K-07": ({5:"DG-01 (buzlu)"}, "Duş, lavabo, asma klozet (zemin kattaki misafir banyosunun üstünde)."),
 "K-08": ({0:"DK-03"}, "Yatak 2 holü, gömme dolap."),
 "K-09": ({2:"DV-03",5:"DG-01 (buzlu, geniş)",8:"ST-03"}, "Serbest küvet, çift lavabo, duş, asma klozet."),
 "K-10": ({}, "Süit girişi ve giyinme odası; ada dolap, tavana kadar gardırop."),
 "K-11": ({5:"DG-02 + DG-05"}, "Balkona 420 cm kaldır-sür; batıda pencere, oturma köşesi."),
 "K-12": ({}, "Güney pencereli; kendi banyosu var."),
 "K-13": ({5:"DG-07"}, "Duş, lavabo, asma klozet; şafta bitişik, mekanik havalandırma."),
 "K-14": ({0:"DK-02"}, "Yatak 3, çamaşır odası ve aile salonuna koridor; çatı arası kapağı burada."),
 "K-15": ({}, "Süit: giyinme odası üzerinden banyo; kuzey ve doğu pencereli."),
 "K-17": ({8:"ST-02 + küvet"}, "Küvet, lavabo, asma klozet; doğuda yüksek pencere."),
 "K-18": ({5:"DG-07",8:"ST-06"}, "Çamaşır + kurutma makinesi, ütü, tezgah; yer süzgeci ve taşma sensörü."),
 "K-19": ({8:"ST-04"}, "Aile salonuna hizmet eden WC."),
 "K-20": ({5:"DG-01 + DG-02"}, "Aile oturma / TV odası; balkona 540 cm kaldır-sür, doğuda pencere."),
}

SUTUNLAR = ["Döşeme", "Süpürgelik", "Duvar", "Tavan", "Kapı", "Doğrama / Pencere",
            "Elektrik", "Mekanik", "Sıhhi Tesisat"]

def mahal_satirlari():
    """[(kat, kod, ad, tip, net_alan, dar, uzun, [9 poz], not), ...]"""
    from veri import net_alan
    cikti = []
    for kat, mahaller in KATLAR.items():
        for m in mahaller:
            kod, ad, tip = m["kod"], m["ad"], m["tip"]
            degerler = list(VARSAYILAN[tip])
            ozel, aciklama = OZEL.get(kod, ({}, ""))
            for i, v in ozel.items():
                degerler[i] = v
            a, dar, uzun = net_alan(m)
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
