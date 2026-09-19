# -*- coding: utf-8 -*-
"""Durunday Villa — 3B model ve render (Blender 4.2, Cycles CPU).
Geometri veri.py'den, pencere/kapı yerleşimi ciz.py'den okunur.

Kullanım:
  ~/opt/blender-4.2.23-linux-x64/blender -b -P kaynak/render_3b.py -- --kadraj giris --ornek 64
"""
import bpy, bmesh, sys, os, math
from mathutils import Vector

KOK = os.path.dirname(os.path.dirname(os.path.abspath(bpy.data.filepath or __file__)))
KAYNAK = os.path.join(KOK, "kaynak")
if KAYNAK not in sys.path:
    sys.path.insert(0, KAYNAK)

from veri import KATLAR, BINA, KAT_YUKSEKLIK, PARSEL          # noqa: E402
import ciz                                                     # noqa: E402

def arg(ad, vars):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(ad) + 1] if ad in a else vars

KADRAJ = arg("--kadraj", "giris")
ORNEK  = int(arg("--ornek", 64))
EN     = int(arg("--en", 1600))
ORAN   = float(arg("--oran", 0.5625))
CIKTI  = arg("--cikti", os.path.join(KOK, "render", KADRAJ + ".jpg"))

E, B = BINA["en"], BINA["boy"]
DD = 0.35                      # dış duvar
DIS, IC = DD / 2, DD / 2       # envelope: aks ± 0.175
KOT = {"Bodrum": -KAT_YUKSEKLIK["Bodrum"], "Zemin": 0.0, "1. Kat": KAT_YUKSEKLIK["Zemin"]}
UST = KOT["1. Kat"] + KAT_YUKSEKLIK["1. Kat"]     # saçak kotu (+6.30)
CATI_H, SACAK = 3.6, 0.6
DENIZLIK, PENCERE_H = 0.95, 1.85
KORKULUK = 1.10

def Y(yp):        # plan y'si (aşağı) -> 3B Y (kuzey +Y)
    return B - yp

# ---------------------------------------------------------------- yardımcı
def temizle():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def malzeme(ad, renk, purus=0.55, metal=0.0, gecir=0.0, ior=1.45, isik=None):
    m = bpy.data.materials.get(ad)
    if m:
        return m
    m = bpy.data.materials.new(ad)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*renk, 1)
    b.inputs["Roughness"].default_value = purus
    b.inputs["Metallic"].default_value = metal
    try:
        b.inputs["Transmission Weight"].default_value = gecir
        b.inputs["IOR"].default_value = ior
    except KeyError:
        pass
    if isik:
        b.inputs["Emission Color"].default_value = (*isik[0], 1)
        b.inputs["Emission Strength"].default_value = isik[1]
    return m

def kutu(x0, y0, z0, x1, y1, z1, ad="kutu", mat=None):
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(ad, me)
    bpy.context.collection.objects.link(o)
    o.scale = ((x1-x0), (y1-y0), (z1-z0))
    o.location = ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    o.select_set(False)
    if mat:
        o.data.materials.append(mat)
    return o

def mesh_yap(ad, verts, faces, mat=None):
    me = bpy.data.meshes.new(ad)
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new(ad, me)
    bpy.context.collection.objects.link(o)
    if mat:
        o.data.materials.append(mat)
    return o

def birlestir(nesneler, ad):
    if not nesneler:
        return None
    bpy.ops.object.select_all(action="DESELECT")
    for n in nesneler:
        n.select_set(True)
    bpy.context.view_layer.objects.active = nesneler[0]
    if len(nesneler) > 1:
        bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active
    o.name = ad
    bpy.ops.object.select_all(action="DESELECT")
    return o

def fark(hedef, kesici):
    if kesici is None:
        return hedef
    m = hedef.modifiers.new("bool", "BOOLEAN")
    m.operation = "DIFFERENCE"; m.object = kesici; m.solver = "EXACT"
    bpy.context.view_layer.objects.active = hedef
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(kesici, do_unlink=True)
    return hedef

# ---------------------------------------------------------------- model
def bina():
    tas   = malzeme("tas",   (0.46, 0.36, 0.24), 0.60)
    siva  = malzeme("siva",  (0.80, 0.79, 0.75), 0.68)
    kiremit = malzeme("kiremit", (0.155, 0.048, 0.032), 0.78)
    ic    = malzeme("ic",    (0.30, 0.29, 0.28), 0.85)
    parcalar = []

    for kat in ("Zemin", "1. Kat"):
        z0 = KOT[kat]; z1 = z0 + KAT_YUKSEKLIK[kat]
        mahaller = KATLAR[kat]
        acik = [r for r in mahaller if r[6] == "acik"]

        # --- iç kütle (içeriyi dolu tutar, açık hacimler boşluk olur)
        cekirdek = kutu(DIS, DIS, z0, E - DIS, B - DIS, z1, "cekirdek_" + kat, ic)
        kes = []
        for r in acik:
            x0 = r[2] + (DIS if r[2] <= 0.001 else 0.0)
            x1 = r[4] - (DIS if r[4] >= E - 0.001 else 0.0)
            yy0 = Y(r[5]) + (DIS if r[5] >= B - 0.001 else 0.0)
            yy1 = Y(r[3]) - (DIS if r[3] <= 0.001 else 0.0)
            kes.append(kutu(x0, yy0, z0 + 0.30, x1, yy1, z1 + 0.05, "kes", None))
        cekirdek = fark(cekirdek, birlestir(kes, "kesici_ic") if kes else None)
        parcalar.append(cekirdek)

        # --- dış duvar halkası
        dis = kutu(-DIS, -DIS, z0, E + DIS, B + DIS, z1, "duvar_" + kat, tas if kat == "Zemin" else siva)
        bosluk = [kutu(DIS, DIS, z0 - 0.05, E - DIS, B - DIS, z1 + 0.05, "ic_bosluk", None)]

        # açık hacimlerin cephesi: korkuluk üstü açılır
        for r in acik:
            for yon, sabit, a, b_ in _dis_kenarlar(r):
                bosluk.append(_kenar_kutusu(yon, sabit, a, b_, z0 + KORKULUK, z1 + 0.05))

        # pencereler
        for yon, sabit, a, b_, r in ciz.pencere_yerlestir(mahaller):
            if r[6] in ("teknik",) and "şaft" in r[1]:
                continue
            bosluk.append(_kenar_kutusu(yon, sabit, a, b_, z0 + DENIZLIK, z0 + DENIZLIK + PENCERE_H))

        # giriş kapısı (zemin, kuzey cephe, antre önü)
        if kat == "Zemin":
            for r in mahaller:
                if r[1].startswith("Antre"):
                    orta = (r[2] + r[4]) / 2
                    bosluk.append(_kenar_kutusu("y", 0.0, orta - 0.65, orta + 0.65, z0, z0 + 2.40))
        dis = fark(dis, birlestir(bosluk, "kesici_duvar"))
        parcalar.append(dis)

        # döşeme plakası (saçak gibi hafif taşkın, kat ayrım bandı)
        parcalar.append(kutu(-DIS - 0.06, -DIS - 0.06, z1 - 0.32, E + DIS + 0.06, B + DIS + 0.06,
                             z1, "doseme_" + kat, siva))

    # --- cam yüzeyler
    cam = malzeme("cam", (0.62, 0.72, 0.78), 0.03, gecir=0.95)
    dograma = malzeme("dograma", (0.10, 0.11, 0.12), 0.35, metal=0.6)
    camlar, cerceveler = [], []
    for kat in ("Zemin", "1. Kat"):
        z0 = KOT[kat]
        for yon, sabit, a, b_, r in ciz.pencere_yerlestir(KATLAR[kat]):
            if r[6] == "teknik" and "şaft" in r[1]:
                continue
            camlar.append(_kenar_kutusu(yon, sabit, a + 0.07, b_ - 0.07,
                                        z0 + DENIZLIK + 0.07, z0 + DENIZLIK + PENCERE_H - 0.07,
                                        kalin=0.04, mat=cam))
            cerceveler.append(_kenar_kutusu(yon, sabit, a, b_, z0 + DENIZLIK, z0 + DENIZLIK + PENCERE_H,
                                            kalin=0.10, mat=dograma))
    # açık hacimlerin cam korkulukları
    korkuluk_cam = malzeme("korkuluk_cam", (0.70, 0.80, 0.85), 0.05, gecir=0.85)
    for kat in ("Zemin", "1. Kat"):
        z0 = KOT[kat]
        for r in KATLAR[kat]:
            if r[6] != "acik":
                continue
            for yon, sabit, a, b_ in _dis_kenarlar(r):
                camlar.append(_kenar_kutusu(yon, sabit, a, b_, z0 + 0.35, z0 + KORKULUK,
                                            kalin=0.03, mat=korkuluk_cam))
    # giriş kapısı
    ahsap = malzeme("ahsap", (0.28, 0.16, 0.09), 0.45)
    for r in KATLAR["Zemin"]:
        if r[1].startswith("Antre"):
            orta = (r[2] + r[4]) / 2
            cerceveler.append(_kenar_kutusu("y", 0.0, orta - 0.60, orta + 0.60, 0.05, 2.35,
                                            kalin=0.12, mat=ahsap))
    parcalar += camlar + cerceveler

    # taban bandı
    parcalar.append(kutu(-DIS - 0.07, -DIS - 0.07, 0.0, E + DIS + 0.07, B + DIS + 0.07, 0.55,
                         "plint", malzeme("plint", (0.28, 0.25, 0.20), 0.65)))

    # --- çatı (kırma)
    t = SACAK
    x0, x1 = -DIS - t, E + DIS + t
    y0, y1 = -DIS - t, B + DIS + t
    orta_y = (y0 + y1) / 2
    yarim = (y1 - y0) / 2
    mx0, mx1 = x0 + yarim, x1 - yarim
    v = [(x0, y0, UST), (x1, y0, UST), (x1, y1, UST), (x0, y1, UST),
         (mx0, orta_y, UST + CATI_H), (mx1, orta_y, UST + CATI_H)]
    f = [(0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4)]
    parcalar.append(mesh_yap("cati", v, f, kiremit))
    # saçak alnı
    parcalar.append(kutu(x0, y0, UST - 0.22, x1, y1, UST, "sacak", malzeme("sacak", (0.66,0.64,0.60), 0.6)))
    return parcalar

def _dis_kenarlar(r):
    """Mahalin envelope'a değen kenarları: (yon, sabit, a, b) — 3B koordinatta."""
    k = []
    if r[3] <= 0.001:  k.append(("y", 0.0, r[2], r[4]))          # kuzey (plan üst)
    if r[5] >= B - 0.001: k.append(("y", B, r[2], r[4]))         # güney
    if r[2] <= 0.001:  k.append(("d", 0.0, r[3], r[5]))          # batı
    if r[4] >= E - 0.001: k.append(("d", E, r[3], r[5]))         # doğu
    return k

def _kenar_kutusu(yon, sabit, a, b_, z0, z1, kalin=None, mat=None):
    """yon 'y': duvar x boyunca, sabit = plan y ; 'd': duvar y boyunca, sabit = x."""
    k = (DD + 0.2) if kalin is None else kalin
    if yon == "y":
        yc = Y(sabit)
        return kutu(a, yc - k/2, z0, b_, yc + k/2, z1, "acik", mat)
    return kutu(sabit - k/2, Y(b_), z0, sabit + k/2, Y(a), z1, "acik", mat)

def cevre():
    cim  = malzeme("cim", (0.09, 0.19, 0.07), 0.95)
    tas_yol = malzeme("tas_yol", (0.30, 0.29, 0.27), 0.75)
    su   = malzeme("su", (0.02, 0.19, 0.26), 0.015, gecir=0.90)
    havuz_ici = malzeme("havuz_ici", (0.16, 0.42, 0.52), 0.5)
    beton = malzeme("beton", (0.34, 0.33, 0.32), 0.8)
    p = []
    rx0, rx1, ry0, ry1 = 1.8, 6.8, B + 0.2, B + 11.0
    zb = KOT["Bodrum"]

    # --- arazi (kalın kütle) ve kazılar
    arazi = kutu(-160, -160, -6.0, E + 160, B + 160, -0.02, "arazi", cim)
    kesiciler = []
    # garaj rampası kazısı (eğimli taban)
    v = [(rx0, ry0, zb - 0.35), (rx1, ry0, zb - 0.35), (rx1, ry1, -0.05), (rx0, ry1, -0.05),
         (rx0, ry0, 0.6), (rx1, ry0, 0.6), (rx1, ry1, 0.6), (rx0, ry1, 0.6)]
    f = [(0,1,2,3), (4,5,6,7), (0,1,5,4), (1,2,6,5), (2,3,7,6), (3,0,4,7)]
    kesiciler.append(mesh_yap("kazi_rampa", v, f))
    # havuz kazısı
    kesiciler.append(kutu(3.0, -9.7, -1.6, 12.0, -5.0, 0.4, "kazi_havuz"))
    arazi = fark(arazi, birlestir(kesiciler, "kazi"))
    p.append(arazi)

    # rampa döşemesi ve istinat duvarları
    p.append(mesh_yap("rampa", [(rx0, ry0, zb), (rx1, ry0, zb), (rx1, ry1, 0.0), (rx0, ry1, 0.0)],
                      [(0, 1, 2, 3)], beton))
    for xx, ic_yon in ((rx0, -0.18), (rx1, 0.18)):
        p.append(kutu(min(xx, xx + ic_yon), ry0, zb - 0.2, max(xx, xx + ic_yon), ry1, 0.15,
                      "istinat_%d" % int(xx * 10), beton))
    p.append(kutu(rx0, ry0 - 0.30, zb, rx1, ry0 - 0.05, zb + 2.45, "garaj_kapisi",
                  malzeme("garaj", (0.13, 0.14, 0.15), 0.4, metal=0.5)))

    # havuz
    p.append(kutu(3.05, -9.65, -1.55, 11.95, -5.05, -0.02, "havuz_kazan", havuz_ici))
    p.append(kutu(3.15, -9.55, -1.45, 11.85, -5.15, -0.12, "havuz_su", su))
    for hx0, hy0, hx1, hy1 in [(1.5, -11.3, 13.5, -9.65), (1.5, -5.05, 13.5, -3.5),
                               (1.5, -9.65, 3.05, -5.05), (11.95, -9.65, 13.5, -5.05)]:
        p.append(kutu(hx0, hy0, -0.03, hx1, hy1, 0.04, "havuz_kenari", tas_yol))

    # yollar, otopark, teras
    p.append(kutu(8.4, B + 0.2, -0.03, 13.3, B + 15.0, 0.03, "yurume_yolu", tas_yol))
    p.append(kutu(14.6, B + 1.0, -0.03, 20.0, B + 6.2, 0.03, "otopark", tas_yol))
    p.append(kutu(-1.2, -3.6, -0.03, E + 1.2, 0.0, 0.04, "teras", tas_yol))

    # giriş basamakları ve saçağı
    giris_x = None
    for r in KATLAR["Zemin"]:
        if r[1].startswith("Antre"):
            giris_x = (r[2] + r[4]) / 2
    if giris_x:
        tas_koyu = malzeme("tas_koyu", (0.34, 0.30, 0.24), 0.6)
        for i, dy in enumerate((0.0, 0.34, 0.68)):
            p.append(kutu(giris_x - 2.2, B + 0.05 + dy, -0.03, giris_x + 2.2, B + 0.42 + dy,
                          0.04 + 0.16 * (2 - i), "basamak_%d" % i, tas_yol))
        p.append(kutu(giris_x - 2.4, B + 0.1, 2.75, giris_x + 2.4, B + 2.3, 2.95, "giris_sacagi", tas_koyu))
        for sx in (giris_x - 2.1, giris_x + 2.1):
            p.append(kutu(sx - 0.09, B + 2.0, 0.0, sx + 0.09, B + 2.2, 2.75, "kolon_%d" % int(sx * 10),
                          malzeme("kolon", (0.12, 0.12, 0.13), 0.4, metal=0.5)))
    return p

def bitki():
    yaprak = malzeme("yaprak", (0.06, 0.16, 0.05), 0.9)
    yaprak2 = malzeme("yaprak2", (0.09, 0.20, 0.06), 0.9)
    govde = malzeme("govde", (0.13, 0.09, 0.05), 0.85)
    p = []
    agaclar = [(-6.5, 22.0, 3.4), (26.5, 20.0, 3.0), (-7.5, 4.0, 3.8), (27.0, 2.0, 3.2),
               (-6.0, -12.0, 3.6), (26.0, -13.5, 3.0), (16.0, -18.0, 3.4), (2.0, -18.5, 3.1),
               (-7.0, 30.0, 2.6), (27.0, 29.0, 2.8)]
    for i, (x, y, h) in enumerate(agaclar):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=h * 0.45, location=(x, y, h * 0.22))
        g = bpy.context.object; g.name = "govde_%d" % i; g.data.materials.append(govde); p.append(g)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=h * 0.42,
                                              location=(x, y, h * 0.75))
        t = bpy.context.object; t.name = "tac_%d" % i
        t.scale = (1.0, 1.0, 1.25)
        t.data.materials.append(yaprak if i % 2 else yaprak2); p.append(t)
    # çit / çalı sırası (parsel sınırı)
    for x0, y0, x1, y1 in [(-7.2, -20.0, -6.4, 32.0), (26.4, -20.0, 27.2, 32.0),
                           (-7.2, -20.8, 27.2, -20.0)]:
        p.append(kutu(x0, y0, -0.02, x1, y1, 1.15, "cit", yaprak))
    # havuz kenarı çalılar
    for x in (2.2, 12.8):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.75, location=(x, -10.6, 0.5))
        c = bpy.context.object; c.data.materials.append(yaprak2); p.append(c)
    return p

def isik_ve_kamera(kadraj):
    s = bpy.context.scene
    d = bpy.data.worlds.new("gokyuzu"); s.world = d
    d.use_nodes = True
    nt = d.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_WORLD":
            nt.nodes.remove(n)
    cik = nt.nodes["World Output"]
    gok = nt.nodes.new("ShaderNodeTexSky")
    gok.sky_type = "NISHITA"
    # kadraja göre güneş: yükseklik, azimut, lamba yönü
    GUNES = {
        "giris": (32, 318, Vector((0.50, -0.66, -0.56))),
        "bahce": (27, 168, Vector((-0.42, 0.78, -0.50))),
        "kus":   (34, 205, Vector((0.30, 0.72, -0.62))),
        "aksam": (5,  292, Vector((0.80, -0.30, -0.16))),
    }
    yuk, azm, yon = GUNES.get(kadraj, GUNES["giris"])
    gok.sun_elevation = math.radians(yuk)
    gok.sun_rotation = math.radians(azm)
    gok.sun_intensity = 0.22
    arka = nt.nodes.new("ShaderNodeBackground")
    arka.inputs["Strength"].default_value = 0.30 if kadraj != "aksam" else 0.10
    nt.links.new(gok.outputs[0], arka.inputs["Color"])
    nt.links.new(arka.outputs[0], cik.inputs["Surface"])

    gunes = bpy.data.lights.new("gunes", "SUN")
    gunes.energy = 4.5 if kadraj != "aksam" else 0.9
    gunes.angle = math.radians(1.5)
    go = bpy.data.objects.new("gunes", gunes)
    bpy.context.collection.objects.link(go)
    go.rotation_euler = yon.to_track_quat("-Z", "Y").to_euler()

    kadrajlar = {
        "giris":   ((-13.0, 40.0, 7.5),  (9.0, 12.0, 3.2), 35),
        "bahce":   ((33.0, -20.0, 7.0),  (9.0, 4.0, 3.6),  35),
        "kus":     ((-30.0, -34.0, 42.0),(10.0, 6.0, 0.5), 30),
        "aksam":   ((-10.0, 34.0, 5.5),  (9.0, 12.0, 3.0), 35),
    }
    loc, hedef, odak = kadrajlar.get(kadraj, kadrajlar["giris"])
    kam = bpy.data.cameras.new("kam"); kam.lens = odak
    ko = bpy.data.objects.new("kam", kam)
    bpy.context.collection.objects.link(ko)
    ko.location = Vector(loc)
    ko.rotation_euler = (Vector(hedef) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    s.camera = ko

    if kadraj == "aksam":      # pencerelerden sızan iç ışık
        for kat in ("Zemin", "1. Kat"):
            z0 = KOT[kat]
            l = bpy.data.lights.new("ic_%s" % kat, "AREA")
            l.energy = 900; l.size = 12; l.color = (1.0, 0.82, 0.60)
            o = bpy.data.objects.new("ic_%s" % kat, l)
            bpy.context.collection.objects.link(o)
            o.location = (E/2, B/2, z0 + 1.6)

def render():
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = ORNEK
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 6
    s.cycles.transmission_bounces = 6
    s.render.resolution_x = EN
    s.render.resolution_y = int(EN * ORAN)
    s.render.image_settings.file_format = "JPEG"
    s.render.image_settings.quality = 92
    s.render.filepath = CIKTI
    try:
        s.view_settings.view_transform = "AgX"
        s.view_settings.look = "AgX - Medium High Contrast"
        s.view_settings.exposure = -0.7 if KADRAJ != "aksam" else 0.2
    except Exception as e:
        print("renk yonetimi atlandi:", e)
    os.makedirs(os.path.dirname(CIKTI), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print("YAZILDI:", CIKTI)

if __name__ == "__main__":
    temizle()
    bina()
    cevre()
    bitki()
    isik_ve_kamera(KADRAJ)
    render()
