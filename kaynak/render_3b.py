# -*- coding: utf-8 -*-
"""Durunday Villa — 3B model ve fotogerçekçi render (Blender 4.2, Cycles CPU).

Bina, cephe açıklıkları, iç duvarlar, merdiven, mobilya, balkon, saçak, pergola, ışıklık,
baca ve havuz doğrudan veri.py / geometri.py'den kurulur (çizimlerle aynı kaynak).

  ~/opt/blender-4.2.23-linux-x64/blender -b -P kaynak/render_3b.py -- \\
      --kadraj giris --ornek 64 --en 1920 --cikti render/giris.jpg
  kadrajlar: giris · bahce · kus · aksam · salon
"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector, Matrix

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, "kaynak")
if KAYNAK not in sys.path:
    sys.path.insert(0, KAYNAK)

from veri import (KATLAR, BINA, KOT, TABII_ZEMIN, PENCERELER, KAPILAR, BALKONLAR, GIRIS_SACAGI,  # noqa
                  PERGOLA, TERAS, ISIKLIKLAR, BACA, HAVUZ, MOBILYA, MERDIVEN, DIS_DUVAR, GARAJ_KOT,
                  merdiven_kollari, ic_sinir, CATI)
from geometri import duvar_parcalari, duvar_dikdortgeni, aciklik_listesi, mahal_sozluk, oda_bul  # noqa
from mobilya import olcu  # noqa

def arg(ad, var):
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return a[a.index(ad) + 1] if ad in a else var

KADRAJ = arg("--kadraj", "giris")
ORNEK = int(arg("--ornek", 64))
EN = int(arg("--en", 1920))
ORAN = float(arg("--oran", 0.5625))
CIKTI = arg("--cikti", os.path.join(KOK, "render", KADRAJ + ".jpg"))
AKSAM = KADRAJ == "aksam"
IC = KADRAJ == "salon"

W, H = BINA["en"], BINA["boy"]
YAL = 0.08                      # ısı yalıtımı + kaplama (dış yüz bina çizgisinin 8 cm dışında)
ZG = TABII_ZEMIN                # tabii zemin −0.30
SILME = (2.98, 3.18)            # kat silmesi
SOFFIT = 6.40                   # saçak altı
SACAK = CATI["sacak"]
EGIM = CATI["egim"]
FASCIA_UST = 6.62
RIDGE = FASCIA_UST + EGIM * ((H + 2 * SACAK) / 2)
random.seed(7)

def BY(y):                      # plan y (kuzey→güney) → Blender Y (güney→kuzey)
    return H - y

# ============================================================ malzemeler
def _yeni(ad):
    m = bpy.data.materials.new(ad)
    m.use_nodes = True
    nt = m.node_tree
    return m, nt, nt.nodes["Principled BSDF"]

def _set(b, **k):
    ad = {"renk": "Base Color", "purus": "Roughness", "metal": "Metallic", "gecir": "Transmission Weight",
          "ior": "IOR", "isik_renk": "Emission Color", "isik": "Emission Strength", "alfa": "Alpha",
          "ss": "Subsurface Weight", "kaplama": "Coat Weight", "parlak": "Specular IOR Level"}
    for a, v in k.items():
        s = b.inputs[ad[a]]
        s.default_value = (*v, 1) if isinstance(v, tuple) and len(v) == 3 else v

def duz(ad, renk, purus=0.5, **k):
    if ad in bpy.data.materials:
        return bpy.data.materials[ad]
    m, nt, b = _yeni(ad)
    _set(b, renk=renk, purus=purus, **k)
    return m

def _node(nt, tip, **k):
    n = nt.nodes.new(tip)
    for a, v in k.items():
        n.inputs[a].default_value = v
    return n

def _dunya_duvar(nt):
    """Duvar yüzeyleri için (x+y, z) haritalaması."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    ay = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Object"], ay.inputs[0])
    top = nt.nodes.new("ShaderNodeMath"); top.operation = "ADD"
    nt.links.new(ay.outputs[0], top.inputs[0]); nt.links.new(ay.outputs[1], top.inputs[1])
    bir = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(top.outputs[0], bir.inputs[0]); nt.links.new(ay.outputs[2], bir.inputs[1])
    nt.links.new(ay.outputs[1], bir.inputs[2])
    return bir.outputs[0]

def _dunya_zemin(nt):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    return tc.outputs["Object"]

def plak(ad, r1, r2, derz, en, boy, derz_w, purus, kabart=0.3, duvar=True, uv=False, gozenek=0.0,
         testere=0.0):
    """Derzli plak/tuğla/kiremit dokusu."""
    if ad in bpy.data.materials:
        return bpy.data.materials[ad]
    m, nt, b = _yeni(ad)
    if uv:
        v = nt.nodes.new("ShaderNodeTexCoord").outputs["UV"]
    else:
        v = _dunya_duvar(nt) if duvar else _dunya_zemin(nt)
    t = nt.nodes.new("ShaderNodeTexBrick")
    t.offset = 0.5; t.offset_frequency = 2
    t.inputs["Color1"].default_value = (*r1, 1)
    t.inputs["Color2"].default_value = (*r2, 1)
    t.inputs["Mortar"].default_value = (*derz, 1)
    t.inputs["Scale"].default_value = 1.0
    t.inputs["Mortar Size"].default_value = derz_w
    t.inputs["Mortar Smooth"].default_value = 0.15
    t.inputs["Brick Width"].default_value = en
    t.inputs["Row Height"].default_value = boy
    nt.links.new(v, t.inputs["Vector"])
    n = _node(nt, "ShaderNodeTexNoise", Scale=3.0, Detail=8.0, Roughness=0.6)
    nt.links.new(v, n.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "OVERLAY"
    mix.inputs["Factor"].default_value = 0.22
    nt.links.new(t.outputs["Color"], mix.inputs["A"]); nt.links.new(n.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    yuk = t.outputs["Fac"]
    if gozenek:
        g = _node(nt, "ShaderNodeTexNoise", Scale=60.0, Detail=4.0)
        nt.links.new(v, g.inputs["Vector"])
        r = nt.nodes.new("ShaderNodeValToRGB")
        r.color_ramp.elements[0].position = 0.62; r.color_ramp.elements[1].position = 0.70
        r.color_ramp.elements[0].color = (1, 1, 1, 1); r.color_ramp.elements[1].color = (0, 0, 0, 1)
        nt.links.new(g.outputs["Fac"], r.inputs["Fac"])
        c = nt.nodes.new("ShaderNodeMath"); c.operation = "MULTIPLY"
        nt.links.new(yuk, c.inputs[0]); nt.links.new(r.outputs["Color"], c.inputs[1])
        yuk = c.outputs[0]
    if testere:
        # kiremit bindirmesi: her sırada testere dişi yükseklik
        ay = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(v, ay.inputs[0])
        bol = nt.nodes.new("ShaderNodeMath"); bol.operation = "DIVIDE"; bol.inputs[1].default_value = boy
        nt.links.new(ay.outputs[1], bol.inputs[0])
        fr = nt.nodes.new("ShaderNodeMath"); fr.operation = "FRACT"; nt.links.new(bol.outputs[0], fr.inputs[0])
        ters = nt.nodes.new("ShaderNodeMath"); ters.operation = "SUBTRACT"; ters.inputs[0].default_value = 1.0
        nt.links.new(fr.outputs[0], ters.inputs[1])
        c = nt.nodes.new("ShaderNodeMath"); c.operation = "MULTIPLY"
        nt.links.new(yuk, c.inputs[0]); nt.links.new(ters.outputs[0], c.inputs[1])
        yuk = c.outputs[0]
    bump = _node(nt, "ShaderNodeBump", Strength=kabart, Distance=0.02)
    nt.links.new(yuk, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    _set(b, purus=purus)
    return m

def gurultu(ad, r1, r2, olcek, purus, kabart=0.1, detay=8.0, duvar=False, metal=0.0):
    if ad in bpy.data.materials:
        return bpy.data.materials[ad]
    m, nt, b = _yeni(ad)
    v = _dunya_duvar(nt) if duvar else _dunya_zemin(nt)
    n = _node(nt, "ShaderNodeTexNoise", Scale=olcek, Detail=detay, Roughness=0.6)
    nt.links.new(v, n.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = (*r1, 1); r.color_ramp.elements[1].color = (*r2, 1)
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    bump = _node(nt, "ShaderNodeBump", Strength=kabart, Distance=0.01)
    nt.links.new(n.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    _set(b, purus=purus, metal=metal)
    return m

def ahsap(ad, r1, r2, lamel=0.14, dikey=True, purus=0.45):
    if ad in bpy.data.materials:
        return bpy.data.materials[ad]
    m, nt, b = _yeni(ad)
    v = _dunya_duvar(nt)
    if not dikey:
        v = _dunya_zemin(nt)
    # lamel derzi
    t = nt.nodes.new("ShaderNodeTexBrick")
    t.inputs["Color1"].default_value = (*r1, 1); t.inputs["Color2"].default_value = (*r2, 1)
    t.inputs["Mortar"].default_value = (0.03, 0.02, 0.012, 1)
    t.inputs["Scale"].default_value = 1.0
    t.inputs["Mortar Size"].default_value = 0.006
    t.inputs["Brick Width"].default_value = lamel if dikey else 2.4
    t.inputs["Row Height"].default_value = 3.0 if dikey else lamel
    t.offset = 0.0
    nt.links.new(v, t.inputs["Vector"])
    # damar
    map_ = nt.nodes.new("ShaderNodeMapping")
    map_.inputs["Scale"].default_value = (18.0, 1.2, 1.0) if dikey else (1.2, 18.0, 1.0)
    nt.links.new(v, map_.inputs[0])
    wv = _node(nt, "ShaderNodeTexWave", Scale=2.0, Distortion=6.0, Detail=4.0)
    nt.links.new(map_.outputs[0], wv.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs["Factor"].default_value = 0.35
    nt.links.new(t.outputs["Color"], mix.inputs["A"]); nt.links.new(wv.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    bump = _node(nt, "ShaderNodeBump", Strength=0.25, Distance=0.01)
    nt.links.new(t.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    _set(b, purus=purus)
    return m

def _golge_gecirgen(nt, b, oran=0.9):
    """Gölge ışınlarında cam/su şeffaf: güneş iç mekana ve havuz tabanına ulaşsın."""
    lp = nt.nodes.new("ShaderNodeLightPath")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mx.inputs[0])
    nt.links.new(b.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    tr.inputs["Color"].default_value = (oran, oran, oran, 1)
    nt.links.new(mx.outputs[0], nt.nodes["Material Output"].inputs["Surface"])

def cam(ad, renk=(0.92, 0.96, 0.96), purus=0.0):
    if ad in bpy.data.materials:
        return bpy.data.materials[ad]
    m, nt, b = _yeni(ad)
    _set(b, renk=renk, purus=purus, gecir=1.0, ior=1.50)
    _golge_gecirgen(nt, b)
    return m

def yaprak_mat(ad, r1, r2, trans=0.35):
    if ad in bpy.data.materials:
        return bpy.data.materials[ad]
    m, nt, b = _yeni(ad)
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = (*r1, 1); r.color_ramp.elements[1].color = (*r2, 1)
    nt.links.new(oi.outputs["Random"], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], b.inputs["Base Color"])
    _set(b, purus=0.55)
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent")
    nt.links.new(r.outputs["Color"], tr.inputs["Color"])
    mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = trans
    out = nt.nodes["Material Output"]
    nt.links.new(b.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs["Surface"])
    return m

def cim_mat(ad="m_cim"):
    if ad in bpy.data.materials:
        return bpy.data.materials[ad]
    m, nt, b = _yeni(ad)
    v = _dunya_zemin(nt)
    n = _node(nt, "ShaderNodeTexNoise", Scale=0.35, Detail=6.0)
    nt.links.new(v, n.inputs["Vector"])
    n2 = _node(nt, "ShaderNodeTexNoise", Scale=40.0, Detail=10.0, Roughness=0.7)
    nt.links.new(v, n2.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].color = (0.045, 0.105, 0.022, 1)
    r.color_ramp.elements[1].color = (0.105, 0.19, 0.045, 1)
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"])
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "OVERLAY"
    mix.inputs["Factor"].default_value = 0.5
    nt.links.new(r.outputs["Color"], mix.inputs["A"]); nt.links.new(n2.outputs["Color"], mix.inputs["B"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    bump = _node(nt, "ShaderNodeBump", Strength=0.6, Distance=0.02)
    nt.links.new(n2.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    _set(b, purus=0.9)
    return m

def su_mat():
    m, nt, b = _yeni("m_su")
    _set(b, renk=(0.75, 0.93, 0.95), purus=0.02, gecir=1.0, ior=1.333)
    v = _dunya_zemin(nt)
    n = _node(nt, "ShaderNodeTexNoise", Scale=1.6, Detail=4.0, Roughness=0.5)
    nt.links.new(v, n.inputs["Vector"])
    bump = _node(nt, "ShaderNodeBump", Strength=0.10, Distance=0.05)
    nt.links.new(n.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    _golge_gecirgen(nt, b, 0.85)
    vol = nt.nodes.new("ShaderNodeVolumeAbsorption")
    vol.inputs["Color"].default_value = (0.35, 0.80, 0.85, 1); vol.inputs["Density"].default_value = 0.45
    nt.links.new(vol.outputs[0], nt.nodes["Material Output"].inputs["Volume"])
    return m

def MAL():
    return dict(
        tas=plak("m_tas", (0.78, 0.70, 0.56), (0.71, 0.62, 0.48), (0.60, 0.54, 0.44), 0.78, 0.30, 0.004,
                 0.62, kabart=0.35, gozenek=1.0),
        siva=gurultu("m_siva", (0.84, 0.83, 0.80), (0.90, 0.89, 0.86), 9, 0.75, 0.04, 4, duvar=True),
        beton=gurultu("m_beton", (0.70, 0.69, 0.66), (0.76, 0.75, 0.72), 14, 0.7, 0.03, duvar=True),
        beton_k=gurultu("m_beton_k", (0.38, 0.37, 0.35), (0.46, 0.45, 0.43), 14, 0.85, 0.06),
        ahsap=ahsap("m_ahsap", (0.36, 0.19, 0.085), (0.30, 0.155, 0.068)),
        ahsap_yatay=ahsap("m_ahsap_y", (0.36, 0.19, 0.085), (0.30, 0.155, 0.068), dikey=False),
        kiremit=plak("m_kiremit", (0.060, 0.062, 0.066), (0.085, 0.086, 0.09), (0.02, 0.02, 0.02),
                     0.30, 0.34, 0.006, 0.38, kabart=0.8, uv=True, testere=1.0),
        dograma=duz("m_dograma", (0.045, 0.048, 0.052), 0.35, metal=0.55),
        paslanmaz=duz("m_paslanmaz", (0.62, 0.62, 0.63), 0.22, metal=1.0),
        cam=cam("m_cam"),
        cam_buzlu=cam("m_cam_buzlu", (0.95, 0.97, 0.97), 0.25),
        kor_cam=cam("m_kor_cam", (0.88, 0.95, 0.95)),
        teras=plak("m_teras", (0.74, 0.69, 0.60), (0.70, 0.65, 0.56), (0.55, 0.52, 0.47), 0.60, 0.60, 0.003,
                   0.7, kabart=0.15, duvar=False),
        yol=plak("m_yol", (0.60, 0.58, 0.54), (0.55, 0.53, 0.49), (0.40, 0.38, 0.35), 0.60, 0.40, 0.006,
                 0.75, kabart=0.2, duvar=False),
        kup=plak("m_kup", (0.34, 0.34, 0.35), (0.42, 0.42, 0.43), (0.22, 0.22, 0.22), 0.10, 0.10, 0.008,
                 0.8, kabart=0.4, duvar=False),
        asfalt=gurultu("m_asfalt", (0.05, 0.05, 0.055), (0.09, 0.09, 0.095), 60, 0.85, 0.2),
        bordur=gurultu("m_bordur", (0.55, 0.55, 0.53), (0.62, 0.62, 0.6), 20, 0.7, 0.05),
        kaldirim=plak("m_kaldirim", (0.52, 0.50, 0.47), (0.46, 0.44, 0.41), (0.3, 0.3, 0.3), 0.30, 0.30, 0.01,
                      0.8, kabart=0.2, duvar=False),
        toprak=gurultu("m_toprak", (0.10, 0.07, 0.045), (0.16, 0.115, 0.075), 12, 0.95, 0.3),
        cakil=gurultu("m_cakil", (0.45, 0.43, 0.40), (0.62, 0.60, 0.56), 90, 0.9, 0.5),
        cim=cim_mat(),
        havuz_ic=plak("m_havuz_ic", (0.55, 0.80, 0.84), (0.50, 0.76, 0.80), (0.8, 0.85, 0.86), 0.05, 0.05,
                      0.08, 0.25, kabart=0.05, duvar=True),
        su=su_mat(),
        kabuk=gurultu("m_kabuk", (0.12, 0.10, 0.08), (0.24, 0.21, 0.17), 30, 0.9, 0.8),
        yaprak_zeytin=yaprak_mat("m_y_zeytin", (0.16, 0.20, 0.10), (0.30, 0.34, 0.20), 0.25),
        yaprak_cinar=yaprak_mat("m_y_cinar", (0.07, 0.17, 0.03), (0.20, 0.32, 0.06)),
        yaprak_selvi=yaprak_mat("m_y_selvi", (0.025, 0.07, 0.02), (0.06, 0.12, 0.035), 0.2),
        yaprak_simsir=yaprak_mat("m_y_simsir", (0.05, 0.14, 0.025), (0.12, 0.24, 0.05), 0.2),
        lavanta=yaprak_mat("m_lavanta", (0.22, 0.17, 0.42), (0.36, 0.28, 0.58), 0.2),
        cim_yaprak=yaprak_mat("m_cim_y", (0.05, 0.12, 0.02), (0.14, 0.24, 0.05), 0.4),
        ic_duvar=duz("m_ic_duvar", (0.74, 0.72, 0.68), 0.85),
        ic_tavan=duz("m_ic_tavan", (0.86, 0.85, 0.83), 0.9),
        parke=ahsap("m_parke", (0.42, 0.28, 0.16), (0.36, 0.24, 0.13), lamel=0.19, dikey=False, purus=0.35),
        traverten=plak("m_traverten", (0.70, 0.64, 0.55), (0.66, 0.60, 0.51), (0.55, 0.51, 0.45), 1.20, 0.60,
                       0.0015, 0.22, kabart=0.05, duvar=False, gozenek=1.0),
        kumas=gurultu("m_kumas", (0.46, 0.45, 0.43), (0.52, 0.51, 0.49), 180, 0.95, 0.15),
        kumas_k=gurultu("m_kumas_k", (0.22, 0.26, 0.28), (0.27, 0.31, 0.33), 180, 0.95, 0.15),
        kumas_b=gurultu("m_kumas_b", (0.70, 0.52, 0.34), (0.76, 0.58, 0.40), 180, 0.95, 0.15),
        hali=gurultu("m_hali", (0.26, 0.25, 0.23), (0.32, 0.30, 0.28), 150, 1.0, 0.3),
        mobilya_ahsap=ahsap("m_mob_ahsap", (0.40, 0.25, 0.13), (0.34, 0.21, 0.11), lamel=3.0, dikey=False,
                            purus=0.3),
        lake=duz("m_lake", (0.72, 0.69, 0.64), 0.35),
        lake_k=duz("m_lake_k", (0.15, 0.15, 0.16), 0.4),
        tezgah=gurultu("m_tezgah", (0.86, 0.85, 0.83), (0.92, 0.91, 0.90), 25, 0.15, 0.01),
        siyah=duz("m_siyah", (0.02, 0.02, 0.02), 0.5),
        perde=duz("m_perde", (0.92, 0.90, 0.86), 0.9, gecir=0.0, ss=0.0),
        tul=_tul(),
        lamba=duz("m_lamba", (1.0, 0.8, 0.55), 0.4, isik_renk=(1.0, 0.72, 0.42), isik=(12.0 if AKSAM else 2.0)),
        led=duz("m_led", (1.0, 0.85, 0.65), 0.4, isik_renk=(1.0, 0.78, 0.5), isik=(18.0 if AKSAM else 0.0)),
        havuz_isik=duz("m_havuz_isik", (0.6, 0.9, 1.0), 0.3, isik_renk=(0.5, 0.9, 1.0),
                       isik=(40.0 if AKSAM else 0.0)),
        komsu_cam=duz("m_komsu_cam", (0.16, 0.18, 0.2), 0.15, metal=0.3),
        araba=duz("m_araba", (0.18, 0.2, 0.22), 0.15, metal=0.8, kaplama=1.0),
    )

def _tul():
    m, nt, b = _yeni("m_tul")
    _set(b, renk=(0.95, 0.94, 0.91), purus=0.9)
    tr = nt.nodes.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (0.95, 0.93, 0.88, 1)
    sa = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx1 = nt.nodes.new("ShaderNodeMixShader"); mx1.inputs[0].default_value = 0.5
    nt.links.new(b.outputs[0], mx1.inputs[1]); nt.links.new(tr.outputs[0], mx1.inputs[2])
    mx2 = nt.nodes.new("ShaderNodeMixShader"); mx2.inputs[0].default_value = 0.55
    nt.links.new(mx1.outputs[0], mx2.inputs[1]); nt.links.new(sa.outputs[0], mx2.inputs[2])
    nt.links.new(mx2.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    return m

# ============================================================ geometri yığını
class Yigin:
    """Malzeme başına tek mesh — binlerce kutuyu hızlı kurar."""
    def __init__(self, ad):
        self.ad = ad
        self.d = {}

    def _al(self, mat):
        return self.d.setdefault(mat.name, (mat, [], []))

    def kutu(self, mat, X0, Y0, Z0, X1, Y1, Z1):
        if X1 - X0 < 1e-5 or Y1 - Y0 < 1e-5 or Z1 - Z0 < 1e-5:
            return
        _, v, f = self._al(mat)
        i = len(v)
        v += [(X0, Y0, Z0), (X1, Y0, Z0), (X1, Y1, Z0), (X0, Y1, Z0),
              (X0, Y0, Z1), (X1, Y0, Z1), (X1, Y1, Z1), (X0, Y1, Z1)]
        f += [(i, i + 3, i + 2, i + 1), (i + 4, i + 5, i + 6, i + 7), (i, i + 1, i + 5, i + 4),
              (i + 1, i + 2, i + 6, i + 5), (i + 2, i + 3, i + 7, i + 6), (i + 3, i, i + 4, i + 7)]

    def pkutu(self, mat, x0, y0, x1, y1, z0, z1):
        """Plan koordinatında kutu."""
        self.kutu(mat, min(x0, x1), BY(max(y0, y1)), z0, max(x0, x1), BY(min(y0, y1)), z1)

    def poly(self, mat, verts, faces):
        _, v, f = self._al(mat)
        i = len(v)
        v += verts
        f += [tuple(i + k for k in fc) for fc in faces]

    def boru(self, mat, p0, p1, r0, r1, n=7):
        p0, p1 = Vector(p0), Vector(p1)
        ek = p1 - p0
        if ek.length < 1e-4:
            return
        z = ek.normalized()
        x = z.orthogonal().normalized(); y = z.cross(x)
        vs, fs = [], []
        for k, (p, r) in enumerate(((p0, r0), (p1, r1))):
            for j in range(n):
                a = 2 * math.pi * j / n
                vs.append(tuple(p + (x * math.cos(a) + y * math.sin(a)) * r))
        for j in range(n):
            fs.append((j, (j + 1) % n, n + (j + 1) % n, n + j))
        fs.append(tuple(range(n))[::-1]); fs.append(tuple(range(n, 2 * n)))
        self.poly(mat, vs, fs)

    def olustur(self, bevel=0.0, duzgun=False):
        out = []
        for ad, (mat, v, f) in self.d.items():
            me = bpy.data.meshes.new(self.ad + "_" + ad)
            me.from_pydata(v, [], f); me.update()
            o = bpy.data.objects.new(self.ad + "_" + ad, me)
            bpy.context.collection.objects.link(o)
            o.data.materials.append(mat)
            if duzgun:
                for p in me.polygons:
                    p.use_smooth = True
            if bevel:
                b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 2
                b.limit_method = "ANGLE"
            out.append(o)
        self.d = {}
        return out

# ============================================================ cephe sistemi
def cephe_uvd(cephe, u0, u1, d0, d1):
    """Cephe yerel koordinatı (u boyunca, d dış yüzden içe) → plan dikdörtgeni."""
    if cephe == "K":
        return (u0, -YAL + d0, u1, -YAL + d1)
    if cephe == "G":
        return (u0, H + YAL - d1, u1, H + YAL - d0)
    if cephe == "B":
        return (-YAL + d0, u0, -YAL + d1, u1)
    return (W + YAL - d1, u0, W + YAL - d0, u1)

def ckutu(Y, mat, cephe, u0, u1, d0, d1, z0, z1):
    x0, y0, x1, y1 = cephe_uvd(cephe, u0, u1, d0, d1)
    Y.pkutu(mat, x0, y0, x1, y1, z0, z1)

def cephe_acikliklari(kat):
    """{cephe: [(a, b, z0, z1, tip, kayit)]}"""
    out = {"K": [], "G": [], "B": [], "D": []}
    k0 = KOT[kat]
    for p in PENCERELER.get(kat, []):
        out[p[0]].append((p[1], p[2], k0 + p[4], k0 + p[5], p[3], p))
    for k in KAPILAR.get(kat, []):
        if k[4] == "giris":
            out["K"].append((k[2], k[3], 0.0, 2.40, "giris", k))
        elif k[4] == "garaj":
            out["K"].append((k[2], k[3], GARAJ_KOT, 2.35, "garaj", k))
        elif k[4] == "servis":
            out["D" if k[1] > 1 else "B"].append((k[2], k[3], 0.0, 2.20, "servis", k))
    return out

def duvar_panosu(Y, mat, cephe, u0, u1, z0, z1, acik, d0=0.0, d1=DIS_DUVAR + YAL, malzeme_fn=None):
    """Açıklıklar etrafında duvar parçaları (boolean yok)."""
    acik = sorted([a for a in acik if a[1] > u0 and a[0] < u1 and a[3] > z0 and a[2] < z1])
    u = u0
    for a in acik:
        oa, ob, oz0, oz1 = max(a[0], u0), min(a[1], u1), max(a[2], z0), min(a[3], z1)
        if oa > u:
            _parca(Y, mat, cephe, u, oa, d0, d1, z0, z1, malzeme_fn)
        if oz0 > z0:
            _parca(Y, mat, cephe, oa, ob, d0, d1, z0, oz0, malzeme_fn)
        if oz1 < z1:
            _parca(Y, mat, cephe, oa, ob, d0, d1, oz1, z1, malzeme_fn)
        u = max(u, ob)
    if u < u1:
        _parca(Y, mat, cephe, u, u1, d0, d1, z0, z1, malzeme_fn)

def _parca(Y, mat, cephe, u0, u1, d0, d1, z0, z1, fn):
    if fn:
        for m2, a, b, c, d in fn(cephe, u0, u1, z0, z1):
            ckutu(Y, m2, cephe, a, b, d0, d1, c, d)
    else:
        ckutu(Y, mat, cephe, u0, u1, d0, d1, z0, z1)

def pencere(Y, M, cephe, a, b, z0, z1, tip, perde=False):
    fr = 0.055                   # kasa genişliği
    dd0, dd1 = 0.10, 0.17        # doğrama derinliği (dış yüzden)
    D = M["dograma"]
    ckutu(Y, D, cephe, a, b, dd0, dd1, z0, z0 + fr)
    ckutu(Y, D, cephe, a, b, dd0, dd1, z1 - fr, z1)
    ckutu(Y, D, cephe, a, a + fr, dd0, dd1, z0, z1)
    ckutu(Y, D, cephe, b - fr, b, dd0, dd1, z0, z1)
    w = b - a
    if tip == "S":
        n = max(2, round(w / 1.8))
    elif tip in ("P", "I"):
        n = 2 if w > 1.3 else 1
    elif tip == "F":
        n = max(1, round(w / 1.2))
    else:
        n = 1
    for i in range(1, n):
        u = a + w * i / n
        ckutu(Y, D, cephe, u - 0.035, u + 0.035, dd0 - (0.02 if tip == "S" and i % 2 else 0), dd1, z0, z1)
    # vasistas kaydı (yüksek pencere/sabit camda)
    if tip == "F" and z1 - z0 > 2.6:
        ckutu(Y, D, cephe, a, b, dd0, dd1, z1 - 0.62, z1 - 0.56)
    mat = M["cam_buzlu"] if tip == "Y" else M["cam"]
    ckutu(Y, mat, cephe, a + fr, b - fr, 0.13, 0.142, z0 + fr, z1 - fr)
    # denizlik
    if tip in ("P", "Y", "I") and z0 > 0.2 + (KOT["Bodrum"] if tip == "I" else 0) - 5:
        ckutu(Y, M["beton"], cephe, a - 0.03, b + 0.03, -0.04, 0.12, z0 - 0.035, z0)
    # iç denizlik / perde
    if perde:
        if tip in ("P", "Y"):
            ckutu(Y, M["tul"], cephe, a - 0.15, b + 0.15, 0.48, 0.49, z0 - 0.02 if tip != "P" else z0 - 0.9 + 0.02,
                  z1 + 0.25)
        elif tip == "S":
            k = min(0.8, w * 0.18)
            ckutu(Y, M["perde"], cephe, a - 0.25, a - 0.25 + k, 0.45, 0.52, z0 + 0.01, z1 + 0.25)
            ckutu(Y, M["perde"], cephe, b + 0.25 - k, b + 0.25, 0.45, 0.52, z0 + 0.01, z1 + 0.25)
            if z0 > 1.0:
                ckutu(Y, M["tul"], cephe, a - 0.2, a + w * 0.45, 0.53, 0.54, z0 + 0.01, z1 + 0.25)

def giris_kapisi(Y, M, a, b):
    D = M["dograma"]
    ckutu(Y, D, "K", a, b, 0.10, 0.18, 2.34, 2.40)
    ckutu(Y, D, "K", a, a + 0.06, 0.10, 0.18, 0.0, 2.40)
    ckutu(Y, D, "K", b - 0.06, b, 0.10, 0.18, 0.0, 2.40)
    ckutu(Y, M["ahsap"], "K", a + 0.06, b - 0.06, 0.12, 0.17, 0.0, 2.34)
    # dikey tutamak
    ckutu(Y, M["paslanmaz"], "K", b - 0.26, b - 0.22, 0.02, 0.06, 0.55, 1.95)
    ckutu(Y, M["paslanmaz"], "K", b - 0.26, b - 0.22, 0.06, 0.12, 0.62, 0.66)
    ckutu(Y, M["paslanmaz"], "K", b - 0.26, b - 0.22, 0.06, 0.12, 1.84, 1.88)

def garaj_kapisi(Y, M, a, b, z0, z1):
    ckutu(Y, M["dograma"], "K", a, b, 0.10, 0.16, z0, z1)
    n = 5
    for i in range(n):
        zz = z0 + (z1 - z0) * i / n
        ckutu(Y, M["ahsap_yatay"], "K", a + 0.02, b - 0.02, 0.08, 0.10, zz + 0.012, zz + (z1 - z0) / n - 0.012)

def servis_kapisi(Y, M, cephe, a, b, z0, z1):
    ckutu(Y, M["dograma"], cephe, a, b, 0.10, 0.17, z0, z1)
    ckutu(Y, M["cam_buzlu"], cephe, a + 0.15, b - 0.15, 0.08, 0.10, z0 + 1.0, z1 - 0.2)
    ckutu(Y, M["paslanmaz"], cephe, b - 0.2, b - 0.1, 0.04, 0.08, 1.0, 1.05)

# ---------- cephe malzeme bölgeleri
def zemin_kaplama(cephe, u0, u1, z0, z1):
    """Zemin kat: taş; giriş cephesinde antre bölümü ahşap lambri."""
    out = []
    if cephe == "K":
        a, b = 7.80, 12.60
        segs = [(u0, min(u1, a), "tas"), (max(u0, a), min(u1, b), "ahsap"), (max(u0, b), u1, "tas")]
        for s0, s1, m in segs:
            if s1 > s0:
                out.append((MM[m], s0, s1, z0, z1))
        return out
    return [(MM["tas"], u0, u1, z0, z1)]

MM = {}

def cepheler(Y, M):
    uz = {"K": W, "G": W, "B": H, "D": H}
    for cephe in ("K", "G", "B", "D"):
        u0, u1 = (-YAL, W + YAL) if cephe in ("K", "G") else (DIS_DUVAR, H - DIS_DUVAR)
        # bodrum (toprak altı + ışıklık)
        ac = cephe_acikliklari("Bodrum")[cephe]
        duvar_panosu(Y, M["beton"], cephe, u0, u1, KOT["Bodrum"] - 0.30, ZG, ac)
        # zemin kat: taş, antre ahşap
        ac = cephe_acikliklari("Zemin")[cephe]
        duvar_panosu(Y, M["tas"], cephe, u0, u1, ZG, SILME[0], ac, malzeme_fn=zemin_kaplama)
        # silme
        duvar_panosu(Y, M["beton"], cephe, u0 - (0.04 if cephe in ("K", "G") else 0),
                     u1 + (0.04 if cephe in ("K", "G") else 0), SILME[0], SILME[1], [], d0=-0.04)
        # 1. kat sıva
        ac = cephe_acikliklari("1. Kat")[cephe]
        duvar_panosu(Y, M["siva"], cephe, u0, u1, SILME[1], SOFFIT, ac)
        for kat in ("Bodrum", "Zemin", "1. Kat"):
            for a, b, z0, z1, tip, kay in cephe_acikliklari(kat)[cephe]:
                if tip == "giris":
                    giris_kapisi(Y, M, a, b)
                elif tip == "garaj":
                    garaj_kapisi(Y, M, a, b, z0, z1)
                elif tip == "servis":
                    servis_kapisi(Y, M, cephe, a, b, z0, z1)
                else:
                    pencere(Y, M, cephe, a, b, z0, z1, tip, perde=(kat != "Bodrum"))
        # yağmur inişleri (köşelerde)
    g = SACAK + 0.07
    for x, y, gx, gy in ((-YAL - 0.07, -YAL - 0.07, -g, -g), (W + YAL + 0.07, -YAL - 0.07, W + g, -g),
                         (-YAL - 0.07, H + YAL + 0.07, -g, H + g), (W + YAL + 0.07, H + YAL + 0.07, W + g, H + g),
                         (6.9, H + YAL + 0.07, 6.9, H + g), (13.1, H + YAL + 0.07, 13.1, H + g)):
        Y.boru(M["dograma"], (x, BY(y), ZG), (x, BY(y), 5.95), 0.05, 0.05, 8)
        Y.boru(M["dograma"], (x, BY(y), 5.95), (gx, BY(gy), 6.50), 0.05, 0.05, 8)

# ============================================================ çatı
def cati(M):
    x0, x1 = -SACAK, W + SACAK
    y0, y1 = -SACAK, H + SACAK
    X0, X1, Y0, Y1 = x0, x1, BY(y1), BY(y0)
    ze, zr = FASCIA_UST, RIDGE
    yr = (Y0 + Y1) / 2
    hl = (Y1 - Y0) / 2
    rx0, rx1 = X0 + hl, X1 - hl
    kal = 0.06
    yuzler = [  # (köşeler, uv fonksiyonu)
        [(X0, Y0, ze), (X1, Y0, ze), (rx1, yr, zr), (rx0, yr, zr)],     # güney
        [(X1, Y1, ze), (X0, Y1, ze), (rx0, yr, zr), (rx1, yr, zr)],     # kuzey
        [(X1, Y0, ze), (X1, Y1, ze), (rx1, yr, zr)],                     # doğu
        [(X0, Y1, ze), (X0, Y0, ze), (rx0, yr, zr)],                     # batı
    ]
    me = bpy.data.meshes.new("cati")
    bm = bmesh.new()
    uvl = bm.loops.layers.uv.new("UVMap")
    for i, yz in enumerate(yuzler):
        vs = [bm.verts.new(v) for v in yz]
        f = bm.faces.new(vs)
        for lp in f.loops:
            X, Yy, Z = lp.vert.co
            egim_uz = (Z - ze) / EGIM * math.sqrt(1 + EGIM ** 2)
            u = X if i < 2 else Yy
            lp[uvl].uv = (u, egim_uz)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("cati", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(M["kiremit"])
    s = o.modifiers.new("kal", "SOLIDIFY"); s.thickness = kal; s.offset = -1
    # mahya ve kırma kapları
    Yg = Yigin("cati_ek")
    for a, b in [((rx0, yr, zr), (rx1, yr, zr)), ((X0, Y0, ze), (rx0, yr, zr)), ((X1, Y0, ze), (rx1, yr, zr)),
                 ((X0, Y1, ze), (rx0, yr, zr)), ((X1, Y1, ze), (rx1, yr, zr))]:
        Yg.boru(M["kiremit"], (a[0], a[1], a[2] + 0.03), (b[0], b[1], b[2] + 0.03), 0.10, 0.10, 8)
    # alın tahtası, saçak altı, oluk
    t = 0.035
    for (ax0, ay0, ax1, ay1) in [(X0, Y0 - t, X1, Y0), (X0, Y1, X1, Y1 + t), (X0 - t, Y0, X0, Y1), (X1, Y0, X1 + t, Y1)]:
        Yg.kutu(M["dograma"], ax0, ay0, SOFFIT, ax1, ay1, ze)
    Yg.kutu(M["ahsap_yatay"], X0, Y0, SOFFIT - 0.02, X1, Y1, SOFFIT)
    g = 0.13
    for (ax0, ay0, ax1, ay1) in [(X0 - g, Y0 - g - t, X1 + g, Y0 - t), (X0 - g, Y1 + t, X1 + g, Y1 + t + g),
                                  (X0 - g - t, Y0, X0 - t, Y1), (X1 + t, Y0, X1 + t + g, Y1)]:
        Yg.kutu(M["dograma"], ax0, ay0, ze - 0.14, ax1, ay1, ze - 0.02)
    # baca
    bx0, bx1 = -YAL - BACA["derinlik"], -YAL
    Yg.pkutu(M["tas"], bx0, BACA["a"], bx1 + 0.02, BACA["b"], ZG, 8.25)
    Yg.pkutu(M["beton"], bx0 - 0.06, BACA["a"] - 0.06, bx1 + 0.08, BACA["b"] + 0.06, 8.25, 8.33)
    Yg.pkutu(M["beton_k"], bx0 + 0.15, BACA["a"] + 0.25, bx1 - 0.13, BACA["b"] - 0.25, 8.33, 8.55)
    Yg.pkutu(M["beton"], bx0 + 0.05, BACA["a"] + 0.15, bx1 - 0.03, BACA["b"] - 0.15, 8.55, 8.60)
    Yg.olustur()

# ============================================================ döşemeler, iç mekan
def dosemeler(Y, M):
    # zemin kat döşemesi (bodrum tavanı)
    Y.pkutu(M["traverten"], DIS_DUVAR, DIS_DUVAR, W - DIS_DUVAR, H - DIS_DUVAR, -0.02, 0.0)
    Y.pkutu(M["ic_tavan"], 0, 0, W, H, -0.30, -0.02)
    Y.pkutu(M["beton_k"], 0, 0, W, H, KOT["Bodrum"] - 0.3, KOT["Bodrum"])
    # 1. kat döşemesi: galeri ve merdiven boşluğu hariç
    bosluk = [(7.8, 0.0, 10.0, 3.2), MERDIVEN["kutu"]]
    z0, z1 = KOT["1. Kat"] - 0.30, KOT["1. Kat"]
    _delikli_doseme(Y, M["ic_tavan"], M["parke"], bosluk, z0, z1)
    # çatı döşemesi
    Y.pkutu(M["ic_tavan"], 0, 0, W, H, KOT["Çatı"] - 0.30, KOT["Çatı"])
    # bodrum-zemin arası merdiven boşluğu da açık (zemin döşemesinde)

def _delikli_doseme(Y, alt, ust, bosluk, z0, z1):
    xs = sorted({0.0, W} | {b[0] for b in bosluk} | {b[2] for b in bosluk})
    ys = sorted({0.0, H} | {b[1] for b in bosluk} | {b[3] for b in bosluk})
    for xa, xb in zip(xs, xs[1:]):
        for ya, yb in zip(ys, ys[1:]):
            cx, cy = (xa + xb) / 2, (ya + yb) / 2
            if any(b[0] < cx < b[2] and b[1] < cy < b[3] for b in bosluk):
                continue
            Y.pkutu(alt, xa, ya, xb, yb, z0, z1 - 0.02)
            Y.pkutu(ust, max(xa, DIS_DUVAR), max(ya, DIS_DUVAR), min(xb, W - DIS_DUVAR), min(yb, H - DIS_DUVAR),
                    z1 - 0.02, z1)

TAVAN = {"Bodrum": KOT["Bodrum"] + 2.76, "Zemin": KOT["Zemin"] + 2.90, "1. Kat": KOT["1. Kat"] + 2.70}

def ic_duvarlar(Y, M):
    for kat in ("Zemin", "1. Kat"):
        z0, zt = KOT[kat], TAVAN[kat]
        for p in duvar_parcalari(kat):
            if p[4] == "dis":
                continue
            x0, y0, x1, y1 = duvar_dikdortgeni(p)
            if p[4] == "korkuluk":
                Y.pkutu(M["kor_cam"], x0 + 0.02, y0, x1 - 0.02, y1, z0, z0 + 1.10) if p[0] == "x" else \
                    Y.pkutu(M["kor_cam"], x0, y0 + 0.02, x1, y1 - 0.02, z0, z0 + 1.10)
                continue
            Y.pkutu(M["ic_duvar"], x0, y0, x1, y1, z0, zt)
        # kapı üstü lentolar
        for e, c, a, b, tur, kay in aciklik_listesi(kat):
            if tur != "kapi":
                continue
            tip = kay[4]
            if tip in ("giris", "garaj", "servis"):
                continue
            ust = {"gecis": 2.60, "asansor": 2.10, "kapak": 2.0}.get(tip, 2.20)
            t = 0.075
            if e == "x":
                Y.pkutu(M["ic_duvar"], c - t, a, c + t, b, z0 + ust, zt)
            else:
                Y.pkutu(M["ic_duvar"], a, c - t, b, c + t, z0 + ust, zt)
            if tip in ("kapi", "yangin", "kapak", "surme", "cift", "asansor"):
                m = M["lake"] if tip != "asansor" else M["paslanmaz"]
                if e == "x":
                    Y.pkutu(m, c - 0.02, a + 0.01, c + 0.02, b - 0.01, z0, z0 + ust)
                else:
                    Y.pkutu(m, a + 0.01, c - 0.02, b - 0.01, c + 0.02, z0, z0 + ust)

def merdiven(Y, M):
    for kat in ("Bodrum", "Zemin"):
        mk = merdiven_kollari(kat)
        z = KOT[mk["alt"]]
        r = mk["riht"]
        b = MERDIVEN["basamak"]
        s0, s1 = MERDIVEN["sahanlik"]
        x0k, x1k, ya, yb, n, yon = mk["kollar"][0]
        for i in range(n - 1):
            yy = ya + i * b
            zz = z + (i + 1) * r
            Y.pkutu(M["traverten"], x0k, yy, x1k, yy + b + 0.03, zz - 0.05, zz)
            Y.pkutu(M["ic_tavan"], x0k, yy, x1k, yy + b, zz - 0.25, zz - 0.05)
        zs = z + n * r
        Y.pkutu(M["traverten"], MERDIVEN["bati_kol"][0], s0, MERDIVEN["dogu_kol"][1], s1, zs - 0.05, zs)
        Y.pkutu(M["ic_tavan"], MERDIVEN["bati_kol"][0], s0, MERDIVEN["dogu_kol"][1], s1, zs - 0.25, zs - 0.05)
        x0k, x1k, ya, yb, n2, yon = mk["kollar"][1]
        for i in range(n2 - 1):
            yy = ya - (i + 1) * b
            zz = zs + (i + 1) * r
            Y.pkutu(M["traverten"], x0k, yy - 0.03, x1k, yy + b, zz - 0.05, zz)
            Y.pkutu(M["ic_tavan"], x0k, yy, x1k, yy + b, zz - 0.25, zz - 0.05)
        # cam korkuluk (göz boşluğu)
        Y.pkutu(M["kor_cam"], 11.28, s0 - 2.6, 11.32, s0, z + 0.9, zs + 1.1)

# ---------- mobilya
YUKSEK = {"yatak_cift": 0.55, "yatak_tek": 0.5, "gardirop": 2.35, "koltuk": 0.8, "berjer": 0.8, "kanepe": 0.8,
          "kanepe_l": 0.8, "sehpa": 0.4, "tv_unite": 0.5, "yemek_masasi": 0.76, "bufe": 0.85, "tezgah": 0.92,
          "ada": 0.92, "buzdolabi": 2.2, "bar_tabure": 0.75, "wc": 0.4, "lavabo": 0.85, "dus": 2.0,
          "kuvet": 0.58, "kuvet_serbest": 0.6, "masa": 0.76, "masa_yuvarlak": 0.76, "kitaplik": 2.2,
          "vestiyer": 2.3, "piyano": 1.25, "komodin_tv": 0.6, "ada_dolap": 0.9, "camasir": 0.85, "utu": 0.9}

def mobilya_blok(Y, M, kat):
    z0 = KOT[kat]
    for tip, cx, cy, rot, p in MOBILYA.get(kat, []):
        if tip not in YUKSEK or tip in ("hali", "bitki"):
            continue
        if kat == "Zemin" and oda_bul("Zemin", cx, cy) in ("Z-09", "Z-10", "Z-11") and tip in DETAYLI:
            continue
        w, d = olcu(tip, p)
        if rot % 180 == 90:
            w, d = d, w
        h = YUKSEK[tip]
        m = {"gardirop": M["lake"], "vestiyer": M["lake"], "buzdolabi": M["lake"], "tezgah": M["lake_k"],
             "kitaplik": M["mobilya_ahsap"], "dus": M["kor_cam"], "masa": M["mobilya_ahsap"],
             "yemek_masasi": M["mobilya_ahsap"], "piyano": M["siyah"]}.get(tip, M["kumas"])
        if tip == "yatak_cift":
            Y.pkutu(M["kumas"], cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2, z0, z0 + 0.3)
            Y.pkutu(M["perde"], cx - w / 2 + 0.05, cy - d / 2 + 0.05, cx + w / 2 - 0.05, cy + d / 2 - 0.05,
                    z0 + 0.3, z0 + h)
            continue
        Y.pkutu(m, cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2, z0, z0 + h)

DETAYLI = {"kanepe_l", "berjer", "sehpa", "piyano", "yemek_masasi", "bufe", "tezgah", "ada", "buzdolabi",
           "bar_tabure", "hali", "tv_unite"}

def yuvarlak_kutu(M, mat, x0, y0, x1, y1, z0, z1, r=0.03, ad="mob"):
    """Kenarları yuvarlatılmış kutu (plan koordinatı)."""
    me = bpy.data.meshes.new(ad)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(ad, me)
    bpy.context.collection.objects.link(o)
    o.scale = (abs(x1 - x0), abs(y1 - y0), z1 - z0)
    o.location = ((x0 + x1) / 2, BY((y0 + y1) / 2), (z0 + z1) / 2)
    o.data.materials.append(mat)
    b = o.modifiers.new("bev", "BEVEL"); b.width = r; b.segments = 3; b.affect = "EDGES"
    # ölçek uygulanmadığı için bevel ölçekle bozulmasın
    o.data.transform(Matrix.Diagonal((o.scale[0], o.scale[1], o.scale[2], 1)))
    o.scale = (1, 1, 1)
    return o

def salon_detay(M):
    """Zemin kat salon – yemek – mutfak: sunum kalitesinde mobilya."""
    z = 0.0
    Y = Yigin("salon")
    # --- L koltuk (sırtı doğuda, şömineye bakar): x 3.3–5.9, y 8.4–11.8
    x0, y0, x1, y1 = 3.3, 8.4, 5.9, 11.8
    yuvarlak_kutu(M, M["kumas"], x1 - 0.95, y0, x1, y1, z + 0.10, z + 0.42, 0.04)          # oturma tabanı (uzun)
    yuvarlak_kutu(M, M["kumas"], x0, y0, x1 - 0.95, y0 + 0.95, z + 0.10, z + 0.42, 0.04)   # kısa kol (kuzey)
    yuvarlak_kutu(M, M["kumas"], x1 - 0.22, y0, x1, y1, z + 0.42, z + 0.80, 0.06)          # sırt
    yuvarlak_kutu(M, M["kumas"], x0, y0, x1 - 0.22, y0 + 0.22, z + 0.42, z + 0.80, 0.06)   # kısa kol sırtı
    yuvarlak_kutu(M, M["kumas"], x1 - 0.95, y1 - 0.22, x1 - 0.22, y1, z + 0.42, z + 0.62, 0.06)  # kolçak
    for i in range(3):
        a = y0 + 0.95 + i * 0.95
        yuvarlak_kutu(M, M["kumas"], x1 - 0.93, a + 0.02, x1 - 0.24, a + 0.93, z + 0.42, z + 0.56, 0.07)
        yuvarlak_kutu(M, M["kumas_k"] if i == 1 else M["kumas_b"], x1 - 0.40, a + 0.25, x1 - 0.22, a + 0.70,
                      z + 0.52, z + 0.90, 0.06)
    for x, y in ((x1 - 0.9, y1 - 0.05), (x1 - 0.05, y1 - 0.05), (x1 - 0.05, y0 + 0.05), (x0 + 0.05, y0 + 0.05),
                 (x0 + 0.05, y0 + 0.9)):
        Y.pkutu(M["dograma"], x - 0.03, y - 0.03, x + 0.03, y + 0.03, z, z + 0.10)
    # sehpa (traverten blok) ve halı
    yuvarlak_kutu(M, M["traverten"], 1.8, 9.5, 2.8, 10.7, z, z + 0.36, 0.02)
    Y.pkutu(M["hali"], 0.9, 8.1, 5.0, 12.1, z, z + 0.012)
    # berjerler
    for cy, rot in ((8.2, 0), (12.0, 180)):
        yuvarlak_kutu(M, M["kumas_b"], 1.2, cy - 0.38, 2.0, cy + 0.38, z + 0.22, z + 0.44, 0.05)
        s = -1 if rot == 0 else 1
        yuvarlak_kutu(M, M["kumas_b"], 1.2, cy - s * 0.38 - 0.10, 2.0, cy - s * 0.38 + 0.10, z + 0.44, z + 0.78,
                      0.05) if False else None
        yb = cy - 0.38 if rot == 0 else cy + 0.20
        yuvarlak_kutu(M, M["kumas_b"], 1.2, yb, 2.0, yb + 0.18, z + 0.44, z + 0.80, 0.05)
        for x in (1.26, 1.94):
            for y in (cy - 0.32, cy + 0.32):
                Y.pkutu(M["mobilya_ahsap"], x - 0.02, y - 0.02, x + 0.02, y + 0.02, z, z + 0.22)
    # şömine: iç yüzde taş kaplı kütle + ocak
    Y.pkutu(M["traverten"], 0.35, 9.1, 0.62, 11.1, z, TAVAN["Zemin"])
    Y.pkutu(M["siyah"], 0.36, 9.6, 0.63, 10.6, z + 0.35, z + 0.95)
    Y.pkutu(M["lamba"], 0.40, 9.7, 0.50, 10.5, z + 0.36, z + 0.42)
    Y.pkutu(M["traverten"], 0.35, 8.9, 0.95, 11.3, z, z + 0.30)
    # piyano
    yuvarlak_kutu(M, M["siyah"], 1.23, 5.30, 2.77, 5.90, z, z + 1.25, 0.02)
    # --- yemek masası (x 9.1–11.3, y 11.0–13.6) ve 8 sandalye
    yuvarlak_kutu(M, M["mobilya_ahsap"], 9.65, 11.15, 10.75, 13.45, z + 0.72, z + 0.76, 0.01)
    for x, y in ((9.75, 11.3), (10.65, 11.3), (9.75, 13.3), (10.65, 13.3)):
        Y.pkutu(M["mobilya_ahsap"], x - 0.03, y - 0.03, x + 0.03, y + 0.03, z, z + 0.72)
    for i in range(3):
        cy = 11.55 + i * 0.75
        for sx, yon in ((9.35, -1), (11.05, 1)):
            yuvarlak_kutu(M, M["kumas"], sx - 0.23, cy - 0.23, sx + 0.23, cy + 0.23, z + 0.44, z + 0.50, 0.03)
            bx = sx + yon * 0.20
            yuvarlak_kutu(M, M["kumas"], bx - 0.03, cy - 0.22, bx + 0.03, cy + 0.22, z + 0.50, z + 0.88, 0.02)
            for dx in (-0.18, 0.18):
                for dy in (-0.18, 0.18):
                    Y.pkutu(M["dograma"], sx + dx - 0.012, cy + dy - 0.012, sx + dx + 0.012, cy + dy + 0.012,
                            z, z + 0.44)
    for cy, yon in ((11.0, -1), (13.6, 1)):
        yuvarlak_kutu(M, M["kumas"], 9.97, cy - 0.23, 10.43, cy + 0.23, z + 0.44, z + 0.50, 0.03)
    # büfe
    yuvarlak_kutu(M, M["mobilya_ahsap"], 10.15, 10.28, 12.35, 10.76, z + 0.12, z + 0.85, 0.01)
    # sarkıt aydınlatma (lineer)
    Y.pkutu(M["dograma"], 9.9, 11.4, 10.5, 13.2, 2.12, 2.16)
    Y.pkutu(M["lamba"], 9.95, 11.45, 10.45, 13.15, 2.105, 2.12)
    for yy in (11.6, 13.0):
        Y.pkutu(M["dograma"], 10.19, yy - 0.004, 10.21, yy + 0.004, 2.16, TAVAN["Zemin"])
    # --- mutfak
    # doğu tezgahı (pencere altında) x 19.03–19.65, y 10.1–14.5
    yuvarlak_kutu(M, M["lake"], 19.05, 10.1, 19.65, 14.5, z + 0.10, z + 0.88, 0.005)
    yuvarlak_kutu(M, M["tezgah"], 19.00, 10.1, 19.65, 14.5, z + 0.88, z + 0.92, 0.005)
    Y.pkutu(M["siyah"], 19.1, 11.9, 19.55, 12.6, z + 0.921, z + 0.925)       # eviye
    Y.pkutu(M["paslanmaz"], 19.52, 12.2, 19.56, 12.26, z + 0.92, z + 1.22)
    # kuzey dolap duvarı: buzdolabı + fırın kolonu + tezgah + üst dolap
    yuvarlak_kutu(M, M["lake"], 14.04, 9.88, 14.96, 10.60, z, z + 2.35, 0.005)
    yuvarlak_kutu(M, M["lake"], 15.0, 9.88, 16.8, 10.49, z + 0.10, z + 0.88, 0.005)
    yuvarlak_kutu(M, M["tezgah"], 15.0, 9.88, 16.8, 10.52, z + 0.88, z + 0.92, 0.005)
    yuvarlak_kutu(M, M["lake"], 15.0, 9.88, 16.8, 10.24, z + 1.50, z + 2.35, 0.005)
    Y.pkutu(M["led"], 15.02, 10.10, 16.78, 10.20, z + 1.49, z + 1.50)
    # ada: x 14.9–17.9, y 11.75–12.85 (şelale uçlu)
    yuvarlak_kutu(M, M["mobilya_ahsap"], 15.0, 11.85, 17.8, 12.75, z + 0.08, z + 0.88, 0.005)
    yuvarlak_kutu(M, M["tezgah"], 14.9, 11.75, 17.9, 12.85, z + 0.88, z + 0.92, 0.005)
    yuvarlak_kutu(M, M["tezgah"], 14.9, 11.75, 14.94, 12.85, z, z + 0.88, 0.003)
    yuvarlak_kutu(M, M["tezgah"], 17.86, 11.75, 17.9, 12.85, z, z + 0.88, 0.003)
    Y.pkutu(M["siyah"], 15.8, 11.9, 16.6, 12.4, z + 0.921, z + 0.925)          # ocak
    # bar tabureleri
    for x in (15.85, 16.4, 16.95):
        yuvarlak_kutu(M, M["kumas_b"], x - 0.2, 13.1, x + 0.2, 13.5, z + 0.70, z + 0.76, 0.03)
        Y.pkutu(M["dograma"], x - 0.015, 13.285, x + 0.015, 13.315, z, z + 0.70)
        Y.pkutu(M["dograma"], x - 0.18, 13.12, x + 0.18, 13.14, z + 0.3, z + 0.32)
    # ada üstü sarkıtlar
    for x in (15.6, 16.4, 17.2):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(x, BY(12.3), 1.85), segments=24, ring_count=12)
        o = bpy.context.object; o.data.materials.append(M["lamba"]); bpy.ops.object.shade_smooth()
        Y.pkutu(M["dograma"], x - 0.004, 12.296, x + 0.004, 12.304, 1.97, TAVAN["Zemin"])
    # doğu duvarında ceviz lamel panel (kapı ile açıklık arası)
    y = 7.62
    while y < 10.70:
        Y.pkutu(M["mobilya_ahsap"], 7.66, y, 7.725, y + 0.045, z, TAVAN["Zemin"])
        y += 0.075
    Y.pkutu(M["siyah"], 7.70, 7.60, 7.72, 10.72, z, TAVAN["Zemin"])
    # gömme spotlar
    for (xa, xb, ya, yb) in ((0.9, 7.3, 5.8, 14.2), (8.4, 12.1, 10.8, 14.2), (13.2, 19.2, 10.4, 14.2)):
        nx, ny = max(2, int((xb - xa) / 1.4)), max(2, int((yb - ya) / 1.4))
        for i in range(nx):
            for j in range(ny):
                cx = xa + (xb - xa) * (i + 0.5) / nx
                cy = ya + (yb - ya) * (j + 0.5) / ny
                Y.pkutu(M["lamba"], cx - 0.04, cy - 0.04, cx + 0.04, cy + 0.04, TAVAN["Zemin"] - 0.005,
                        TAVAN["Zemin"])
    # tavan: gizli LED nişi çevresi (salon)
    Y.pkutu(M["led"], 0.40, 5.33, 7.65, 5.37, TAVAN["Zemin"] - 0.03, TAVAN["Zemin"] - 0.01)
    Y.olustur()

# ============================================================ dış elemanlar
def dis_elemanlar(Y, M):
    # --- giriş: sahanlık, basamaklar, saçak
    g = GIRIS_SACAGI
    Y.pkutu(M["teras"], g["x0"], -g["derinlik"], g["x1"], -YAL, ZG, -0.02)
    Y.pkutu(M["teras"], g["x0"] + 0.4, -g["derinlik"] - 0.32, g["x1"] - 0.4, -g["derinlik"], ZG, -0.16)
    Y.pkutu(M["beton"], g["x0"], -g["derinlik"], g["x1"], -YAL, 2.75, 2.97)
    Y.pkutu(M["ahsap_yatay"], g["x0"] + 0.02, -g["derinlik"] + 0.02, g["x1"] - 0.02, -YAL, 2.73, 2.75)
    for x in (8.3, 10.0, 11.7):
        Y.pkutu(M["lamba"], x - 0.06, -1.0, x + 0.06, -0.88, 2.725, 2.73)
    # antre sağındaki sabit camın önüne ahşap dikey lamel yok; ev numarası
    Y.pkutu(M["paslanmaz"], 12.05, -YAL - 0.03, 12.35, -YAL, 1.55, 1.75)
    # --- balkonlar
    for bk in BALKONLAR:
        x0, x1, d = bk["x0"], bk["x1"], bk["derinlik"]
        Y.pkutu(M["beton"], x0, H + YAL, x1, H + d, SILME[0], SILME[1])
        Y.pkutu(M["teras"], x0 + 0.02, H + YAL, x1 - 0.02, H + d - 0.02, SILME[1], SILME[1] + 0.02)
        Y.pkutu(M["ahsap_yatay"], x0 + 0.02, H + YAL, x1 - 0.02, H + d - 0.02, SILME[0] - 0.01, SILME[0])
        zk0, zk1 = SILME[1] + 0.02, SILME[1] + 1.12
        for (a0, b0, a1, b1) in [(x0 + 0.03, H + d - 0.06, x1 - 0.03, H + d - 0.045),
                                  (x0 + 0.03, H + YAL, x0 + 0.045, H + d - 0.06),
                                  (x1 - 0.045, H + YAL, x1 - 0.03, H + d - 0.06)]:
            Y.pkutu(M["kor_cam"], a0, b0, a1, b1, zk0, zk1)
        Y.pkutu(M["dograma"], x0 + 0.02, H + d - 0.07, x1 - 0.02, H + d - 0.035, SILME[1], zk0 + 0.06)
        # balkon mobilyası
        cx = (x0 + x1) / 2
        yuvarlak_kutu(M, M["mobilya_ahsap"], cx - 0.3, H + 0.55, cx + 0.3, H + 1.15, zk0 + 0.45, zk0 + 0.48)
        Y.pkutu(M["dograma"], cx - 0.02, H + 0.83, cx + 0.02, H + 0.87, zk0, zk0 + 0.45)
        for sx in (cx - 0.9, cx + 0.9):
            yuvarlak_kutu(M, M["kumas_b"], sx - 0.3, H + 0.5, sx + 0.3, H + 1.1, zk0 + 0.25, zk0 + 0.42, 0.04)
            yuvarlak_kutu(M, M["kumas_b"], sx - 0.3, H + 0.45, sx + 0.3, H + 0.6, zk0 + 0.42, zk0 + 0.78, 0.04)
    # --- teras
    t = TERAS
    Y.pkutu(M["teras"], t["x0"], H + YAL, t["x1"], t["y1"], ZG - 0.1, t["kot"])
    Y.pkutu(M["teras"], 7.8, t["y1"], 12.6, t["y1"] + 0.35, ZG - 0.1, -0.16)
    # --- pergola (alüminyum, lamel)
    p = PERGOLA
    for x in (p["x0"] + 0.08, p["x1"] - 0.08):
        Y.pkutu(M["dograma"], x - 0.07, p["y1"] - 0.15, x + 0.07, p["y1"] - 0.01, -0.02, 2.95)
    Y.pkutu(M["dograma"], p["x0"], p["y1"] - 0.16, p["x1"], p["y1"], 2.70, 2.95)
    Y.pkutu(M["dograma"], p["x0"], H + 1.5, p["x0"] + 0.15, p["y1"], 2.70, 2.95)
    Y.pkutu(M["dograma"], p["x1"] - 0.15, H + 1.5, p["x1"], p["y1"], 2.70, 2.95)
    x = p["x0"] + 0.25
    while x < p["x1"] - 0.2:
        Y.pkutu(M["dograma"], x - 0.09, H + 1.5, x + 0.09, p["y1"] - 0.16, 2.84, 2.87)
        x += 0.24
    if AKSAM:
        Y.pkutu(M["led"], p["x0"] + 0.15, p["y1"] - 0.2, p["x1"] - 0.15, p["y1"] - 0.16, 2.70, 2.72)
    # pergola altı yemek takımı
    cx, cy = 16.3, 17.2
    yuvarlak_kutu(M, M["mobilya_ahsap"], cx - 1.1, cy - 0.5, cx + 1.1, cy + 0.5, 0.70, 0.74, 0.01)
    for dx in (-0.95, 0.95):
        Y.pkutu(M["dograma"], cx + dx - 0.03, cy - 0.4, cx + dx + 0.03, cy + 0.4, -0.02, 0.70)
    for i in range(3):
        sx = cx - 0.75 + i * 0.75
        for sy, yon in ((cy - 0.85, -1), (cy + 0.85, 1)):
            yuvarlak_kutu(M, M["kumas"], sx - 0.24, sy - 0.24, sx + 0.24, sy + 0.24, 0.40, 0.47, 0.04)
            yuvarlak_kutu(M, M["kumas"], sx - 0.24, sy + yon * 0.2 - 0.04, sx + 0.24, sy + yon * 0.2 + 0.04, 0.47,
                          0.85, 0.03)
            Y.pkutu(M["dograma"], sx - 0.2, sy - 0.2, sx + 0.2, sy + 0.2, -0.02, 0.40)
    # terasta oturma grubu (salon önü)
    yuvarlak_kutu(M, M["kumas"], 1.6, 16.3, 4.6, 17.2, 0.10, 0.40, 0.05)
    yuvarlak_kutu(M, M["kumas"], 1.6, 17.0, 4.6, 17.25, 0.40, 0.75, 0.05)
    yuvarlak_kutu(M, M["mobilya_ahsap"], 2.4, 15.5, 3.8, 16.1, -0.02, 0.35, 0.02)
    for bx in (1.0, 5.2):
        yuvarlak_kutu(M, M["kumas"], bx - 0.4, 15.6, bx + 0.4, 16.4, 0.10, 0.40, 0.05)
    # --- ışıklıklar
    for i in ISIKLIKLAR:
        d = i["derinlik"]
        if i["cephe"] == "B":
            px0, px1 = -YAL - d, -YAL
        else:
            px0, px1 = W + YAL, W + YAL + d
        a, b = i["a"], i["b"]
        zb = KOT["Bodrum"] - 0.10
        Y.pkutu(M["cakil"], px0, a, px1, b, zb - 0.1, zb)
        # istinat duvarları
        dis = px0 if i["cephe"] == "B" else px1
        Y.pkutu(M["beton"], min(dis, dis + (-0.2 if i["cephe"] == "B" else 0.2)), a - 0.2,
                max(dis, dis + (-0.2 if i["cephe"] == "B" else 0.2)), b + 0.2, zb - 0.1, ZG + 0.12)
        Y.pkutu(M["beton"], px0, a - 0.2, px1, a, zb - 0.1, ZG + 0.12)
        Y.pkutu(M["beton"], px0, b, px1, b + 0.2, zb - 0.1, ZG + 0.12)
        # cam korkuluk + ızgara yok (korkuluklu açık ışıklık)
        cx0 = dis - 0.1 if i["cephe"] == "B" else dis + 0.1
        Y.pkutu(M["kor_cam"], cx0 - 0.01, a - 0.1, cx0 + 0.01, b + 0.1, ZG + 0.12, ZG + 1.1)
        Y.pkutu(M["kor_cam"], min(cx0, -YAL if i["cephe"] == "B" else W + YAL), a - 0.11,
                max(cx0, -YAL if i["cephe"] == "B" else W + YAL), a - 0.09, ZG + 0.12, ZG + 1.1)
        Y.pkutu(M["kor_cam"], min(cx0, -YAL if i["cephe"] == "B" else W + YAL), b + 0.09,
                max(cx0, -YAL if i["cephe"] == "B" else W + YAL), b + 0.11, ZG + 0.12, ZG + 1.1)

# ============================================================ arazi, peyzaj
PX0, PX1 = -3.0, 23.0          # parsel (bina koordinatında)
PY0, PY1 = -5.0, 33.5
SERT = []                      # (x0,y0,x1,y1) sert zemin — çim ekilmez

def arazi(M):
    Y = Yigin("arazi")
    # çevre (komşu parseller, yol) — bina çevresi için büyük düzlem
    Y.pkutu(M["cim"], -120, PY1, 140, 160, ZG - 0.5, ZG - 0.01)
    Y.pkutu(M["cim"], -120, PY0, PX0, PY1, ZG - 0.5, ZG - 0.01)
    Y.pkutu(M["cim"], PX1, PY0, 140, PY1, ZG - 0.5, ZG - 0.01)
    # kaldırım + yol + karşı kaldırım
    Y.pkutu(M["kaldirim"], -120, PY0 - 2.5, 140, PY0, ZG - 0.5, ZG - 0.03)
    Y.pkutu(M["bordur"], -120, PY0 - 2.65, 140, PY0 - 2.5, ZG - 0.5, ZG - 0.03)
    Y.pkutu(M["asfalt"], -120, PY0 - 11.5, 140, PY0 - 2.65, ZG - 0.5, ZG - 0.18)
    Y.pkutu(M["bordur"], -120, PY0 - 11.65, 140, PY0 - 11.5, ZG - 0.5, ZG - 0.03)
    Y.pkutu(M["kaldirim"], -120, PY0 - 14.0, 140, PY0 - 11.65, ZG - 0.5, ZG - 0.03)
    Y.pkutu(M["cim"], -120, -160, 140, PY0 - 14.0, ZG - 0.5, ZG - 0.02)
    # yol çizgisi
    for i in range(-40, 50):
        x = i * 3.0
        Y.pkutu(M["tezgah"], x, PY0 - 7.15, x + 1.5, PY0 - 7.0, ZG - 0.18, ZG - 0.175)
    # --- sert zeminler (plan)
    ser = [
        (M["teras"], 7.9, -5.0, 9.7, -2.12, ZG - 0.1, ZG + 0.02),            # yaya yolu
        (M["kup"], 14.3, -5.0, 19.7, -YAL, ZG - 0.1, ZG + 0.02),             # araba yolu
        (M["yol"], 20.2, -YAL, 22.6, 16.5, ZG - 0.1, ZG + 0.015) if False else None,
        (M["yol"], 21.55, -YAL, 22.75, 18.8, ZG - 0.1, ZG + 0.015),           # doğu servis yolu
        (M["yol"], 20.0 + YAL, 6.2, 21.55, 7.8, ZG - 0.1, ZG + 0.015),        # servis kapısı önü
        (M["yol"], -2.75, -YAL, -1.65, 18.8, ZG - 0.1, ZG + 0.015),           # batı bahçe yolu
        (M["teras"], 3.5, 21.0, 18.5, HAVUZ["y0"] - 0.35, ZG - 0.1, ZG + 0.01),   # havuz güvertesi
        (M["teras"], 3.5, HAVUZ["y1"] + 0.35, 18.5, 29.0, ZG - 0.1, ZG + 0.01),
        (M["teras"], 3.5, HAVUZ["y0"] - 0.35, HAVUZ["x0"] - 0.35, HAVUZ["y1"] + 0.35, ZG - 0.1, ZG + 0.01),
        (M["teras"], HAVUZ["x1"] + 0.35, HAVUZ["y0"] - 0.35, 18.5, HAVUZ["y1"] + 0.35, ZG - 0.1, ZG + 0.01),
        (M["yol"], 9.3, 19.35, 11.1, 21.0, ZG - 0.1, ZG + 0.01),              # teras → havuz
    ]
    for s in ser:
        if s is None:
            continue
        m, x0, y0, x1, y1, z0, z1 = s
        Y.pkutu(m, x0, y0, x1, y1, z0, z1)
        SERT.append((x0, y0, x1, y1))
    SERT.append((-0.5, -1.0, 20.5, 19.4))                # bina + teras
    for i in ISIKLIKLAR:
        d = i["derinlik"]
        x0 = -YAL - d - 0.3 if i["cephe"] == "B" else W
        SERT.append((x0, i["a"] - 0.3, x0 + d + 0.4, i["b"] + 0.3))
    SERT.append((-0.8, 9.5, 0.1, 10.7))                  # baca
    SERT.append((PX0, PY0, PX1, PY0 + 0.45))              # ön bahçe duvarı altı
    SERT.append((PX0, PY0, PX0 + 0.3, PY1)); SERT.append((PX1 - 0.3, PY0, PX1, PY1)); SERT.append((PX0, PY1 - 0.3, PX1, PY1))
    # --- havuz
    h = HAVUZ
    Y.pkutu(M["havuz_ic"], h["x0"], h["y0"], h["x1"], h["y1"], -1.75, -1.60)
    for (a0, b0, a1, b1) in [(h["x0"] - 0.2, h["y0"] - 0.2, h["x1"] + 0.2, h["y0"]),
                              (h["x0"] - 0.2, h["y1"], h["x1"] + 0.2, h["y1"] + 0.2),
                              (h["x0"] - 0.2, h["y0"], h["x0"], h["y1"]), (h["x1"], h["y0"], h["x1"] + 0.2, h["y1"])]:
        Y.pkutu(M["havuz_ic"], a0, b0, a1, b1, -1.75, ZG + 0.005)
    Y.pkutu(M["su"], h["x0"], h["y0"], h["x1"], h["y1"], -1.60, ZG - 0.10)
    # havuz kenar taşı (bordür)
    for (a0, b0, a1, b1) in [(h["x0"] - 0.35, h["y0"] - 0.35, h["x1"] + 0.35, h["y0"]),
                              (h["x0"] - 0.35, h["y1"], h["x1"] + 0.35, h["y1"] + 0.35),
                              (h["x0"] - 0.35, h["y0"], h["x0"], h["y1"]), (h["x1"], h["y0"], h["x1"] + 0.35, h["y1"])]:
        Y.pkutu(M["beton"], a0, b0, a1, b1, ZG, ZG + 0.05)
    if AKSAM:
        for x in (8.0, 11.0, 14.0):
            Y.pkutu(M["havuz_isik"], x - 0.15, h["y0"] + 0.001, x + 0.15, h["y0"] + 0.02, -1.0, -0.8)
    # havuz güvertesi deliği: güverte taşı havuzu kaplamasın
    Y.olustur()
    # güverte havuz üstünde kalmasın: güverteyi dört parça yap
    for o in list(bpy.data.objects):
        pass
    # --- çim yüzeyi (sert zeminler hariç ızgara)
    cim_yuzeyi(M)

def _sert_mi(x, y):
    for x0, y0, x1, y1 in SERT:
        if x0 <= x <= x1 and y0 <= y <= y1:
            return True
    h = HAVUZ
    return h["x0"] - 0.4 <= x <= h["x1"] + 0.4 and h["y0"] - 0.4 <= y <= h["y1"] + 0.4

def cim_yuzeyi(M):
    bm = bmesh.new()
    s = 0.25
    nx, ny = int((PX1 - PX0) / s), int((PY1 - PY0) / s)
    vs = {}
    def v(i, j):
        if (i, j) not in vs:
            vs[(i, j)] = bm.verts.new((PX0 + i * s, BY(PY0 + j * s), ZG))
        return vs[(i, j)]
    for i in range(nx):
        for j in range(ny):
            cx, cy = PX0 + (i + 0.5) * s, PY0 + (j + 0.5) * s
            if _sert_mi(cx, cy):
                continue
            bm.faces.new((v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)))
    me = bpy.data.meshes.new("cim"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new("cim", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(M["cim"])
    return o

def havuz_guverte_duzelt():
    """Havuz güvertesi kutusu havuzun üstünü kapatmasın diye güverteyi dört parçaya böler."""
    pass

# ============================================================ geometry nodes: saçma (çim, yaprak)
def sacma_gn(ad, sablon, yogunluk, secim=None, derinlik=0.0, olcek=(0.7, 1.3), dik=False, tohum=0):
    ng = bpy.data.node_groups.new(ad, "GeometryNodeTree")
    ng.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    dp = N.new("GeometryNodeDistributePointsOnFaces"); dp.distribute_method = "RANDOM"
    dp.inputs["Density"].default_value = yogunluk
    dp.inputs["Seed"].default_value = tohum
    L.new(gi.outputs[0], dp.inputs["Mesh"])
    if secim is not None:
        # kameraya uzaklık seçimi
        pos = N.new("GeometryNodeInputPosition")
        vm = N.new("ShaderNodeVectorMath"); vm.operation = "DISTANCE"
        vm.inputs[1].default_value = secim[0]
        L.new(pos.outputs[0], vm.inputs[0])
        cmp = N.new("FunctionNodeCompare"); cmp.data_type = "FLOAT"; cmp.operation = "LESS_THAN"
        cmp.inputs[1].default_value = secim[1]
        L.new(vm.outputs["Value"], cmp.inputs[0])
        L.new(cmp.outputs[0], dp.inputs["Selection"])
    noktalar = dp.outputs["Points"]
    if derinlik:
        rnd = N.new("FunctionNodeRandomValue"); rnd.data_type = "FLOAT"
        rnd.inputs[2].default_value = 0.0; rnd.inputs[3].default_value = derinlik
        rnd.inputs[8].default_value = tohum + 3
        sc = N.new("ShaderNodeVectorMath"); sc.operation = "SCALE"
        L.new(dp.outputs["Normal"], sc.inputs[0]); L.new(rnd.outputs[1], sc.inputs[3])
        neg = N.new("ShaderNodeVectorMath"); neg.operation = "SCALE"; neg.inputs[3].default_value = -1.0
        L.new(sc.outputs[0], neg.inputs[0])
        sp = N.new("GeometryNodeSetPosition")
        L.new(noktalar, sp.inputs["Geometry"]); L.new(neg.outputs[0], sp.inputs["Offset"])
        noktalar = sp.outputs[0]
    oi = N.new("GeometryNodeObjectInfo"); oi.inputs[0].default_value = sablon
    ip = N.new("GeometryNodeInstanceOnPoints")
    L.new(noktalar, ip.inputs["Points"]); L.new(oi.outputs["Geometry"], ip.inputs["Instance"])
    rr = N.new("FunctionNodeRandomValue"); rr.data_type = "FLOAT_VECTOR"
    rr.inputs[0].default_value = (0, 0, 0) if dik else (-3.14, -3.14, -3.14)
    rr.inputs[1].default_value = (0.25, 0.25, 6.28) if dik else (3.14, 3.14, 3.14)
    rr.inputs[8].default_value = tohum + 1
    L.new(rr.outputs[0], ip.inputs["Rotation"])
    rs = N.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"
    rs.inputs[2].default_value = olcek[0]; rs.inputs[3].default_value = olcek[1]
    rs.inputs[8].default_value = tohum + 2
    L.new(rs.outputs[1], ip.inputs["Scale"])
    L.new(ip.outputs["Instances"], go.inputs[0])
    return ng

def sablon_nesne(ad, verts, faces, mat):
    me = bpy.data.meshes.new(ad)
    me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(ad, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat)
    o.location = (0, 0, -50)
    o.hide_render = True; o.hide_viewport = True
    return o

def yaprak_sablonu(ad, uz, en, mat):
    v = [(0, -uz / 2, 0), (en / 2, 0, 0.01), (0, uz / 2, 0), (-en / 2, 0, 0.01)]
    return sablon_nesne(ad, v, [(0, 1, 2, 3)], mat)

def cim_sablonu(mat):
    random.seed(3)
    v, f = [], []
    for k in range(9):
        a = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, 0.025)
        x, y = r * math.cos(a), r * math.sin(a)
        h = random.uniform(0.05, 0.11)
        w = 0.004
        dx, dy = math.cos(a + 1.57) * w, math.sin(a + 1.57) * w
        egx, egy = math.cos(a) * h * 0.35, math.sin(a) * h * 0.35
        i = len(v)
        v += [(x - dx, y - dy, 0), (x + dx, y + dy, 0), (x + egx * 0.4 + dx * 0.6, y + egy * 0.4 + dy * 0.6, h * 0.55),
              (x + egx * 0.4 - dx * 0.6, y + egy * 0.4 - dy * 0.6, h * 0.55), (x + egx, y + egy, h)]
        f += [(i, i + 1, i + 2, i + 3), (i + 3, i + 2, i + 4)]
    return sablon_nesne("sablon_cim", v, f, mat)

def cim_ekle(M, cim_obj, merkez, yaricap, yog):
    s = cim_sablonu(M["cim_yaprak"])
    ng = sacma_gn("gn_cim", s, yog, secim=(merkez, yaricap), olcek=(0.7, 1.4), dik=True, tohum=5)
    cim2 = cim_obj.copy(); cim2.data = cim_obj.data
    bpy.context.collection.objects.link(cim2)
    cim2.name = "cim_sac"
    mod = cim2.modifiers.new("gn", "NODES"); mod.node_group = ng

# ---------- bitkiler
def agac(Y, M, x, y, h, tur, tohum):
    rnd = random.Random(tohum)
    X, YY = x, BY(y)
    z0 = ZG
    kum = []                                    # yaprak küme merkezleri (x,y,z,r)
    if tur == "selvi":
        Y.boru(M["kabuk"], (X, YY, z0), (X, YY, z0 + h * 0.3), 0.10, 0.07)
        kum.append(("elips", X, YY, z0 + h * 0.55, 0.65 * h / 8, h * 0.48))
    else:
        r0 = h * (0.030 if tur == "zeytin" else 0.018)
        govde_h = h * (0.32 if tur == "zeytin" else 0.42)
        lean = (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3))
        p_tepe = Vector((X + lean[0], YY + lean[1], z0 + govde_h))
        Y.boru(M["kabuk"], (X, YY, z0), p_tepe, r0 * 1.2, r0 * 0.8)
        n_dal = 6 if tur == "zeytin" else 7
        for i in range(n_dal):
            a = 2 * math.pi * i / n_dal + rnd.uniform(-0.3, 0.3)
            egim = rnd.uniform(0.5, 1.0) if tur == "zeytin" else rnd.uniform(0.35, 0.8)
            uz = h * rnd.uniform(0.28, 0.40)
            d = Vector((math.cos(a) * math.sin(egim), math.sin(a) * math.sin(egim), math.cos(egim)))
            p0 = p_tepe + Vector((0, 0, rnd.uniform(-0.1, 0.4) * h * 0.2))
            p1 = p0 + d * uz
            Y.boru(M["kabuk"], p0, p1, r0 * 0.55, r0 * 0.25)
            for j in range(3):
                a2 = a + rnd.uniform(-0.9, 0.9)
                e2 = egim + rnd.uniform(-0.4, 0.2)
                d2 = Vector((math.cos(a2) * math.sin(e2), math.sin(a2) * math.sin(e2), math.cos(e2)))
                q0 = p0 + d * uz * rnd.uniform(0.45, 0.9)
                q1 = q0 + d2 * uz * rnd.uniform(0.35, 0.6)
                Y.boru(M["kabuk"], q0, q1, r0 * 0.25, r0 * 0.08, 5)
                kum.append(("kure", q1.x, q1.y, q1.z, h * rnd.uniform(0.10, 0.15), 0))
            kum.append(("kure", p1.x, p1.y, p1.z, h * rnd.uniform(0.13, 0.19), 0))
        kum.append(("kure", p_tepe.x, p_tepe.y, p_tepe.z + h * 0.35, h * 0.2, 0))
    return kum

def kumeleri_yap(M, kumeler, tur, sablon, yog, derinlik, dik=False):
    bm = bmesh.new()
    for k in kumeler:
        tipk, x, y, z, r, hz = k
        if tipk == "kure":
            m = Matrix.Translation((x, y, z)) @ Matrix.Diagonal((r, r, r * 0.8, 1))
            bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0, matrix=m)
        else:
            m = Matrix.Translation((x, y, z)) @ Matrix.Diagonal((r, r, hz, 1))
            bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=10, radius=1.0, matrix=m)
    me = bpy.data.meshes.new("kume_" + tur); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("kume_" + tur, me)
    bpy.context.collection.objects.link(o)
    ng = sacma_gn("gn_" + tur, sablon, yog, derinlik=derinlik, olcek=(0.7, 1.3), tohum=len(tur) * 7, dik=dik)
    mod = o.modifiers.new("gn", "NODES"); mod.node_group = ng
    # çekirdek (boşlukları koyulaştırır)
    return o

def bitkiler(M, Y):
    agaclar = {"zeytin": [], "cinar": [], "selvi": []}
    # arka bahçe
    liste = [
        ("cinar", -0.8, 30.5, 9.5), ("cinar", 20.5, 31.0, 9.0),
        ("zeytin", 2.2, 24.5, 4.8), ("zeytin", 19.0, 24.0, 4.5),
        ("zeytin", 1.5, -2.8, 4.2),                                          # ön bahçe
    ]
    for i in range(6):
        liste.append(("selvi", -2.2, 18.5 + i * 2.4, rnd_h(i)))
        liste.append(("selvi", 22.2, 20.5 + i * 2.2, rnd_h(i + 3)))
    # sokak ağaçları (kaldırım)
    for i, x in enumerate((-16.0, 28.0, 38.0) if KADRAJ == "kus" else (38.0,)):
        liste.append(("cinar", x, PY0 - 1.3, 7.5 + (i % 2)))
    # komşu bahçe ağaçları
    for i, (x, y) in enumerate(((-8.5, 15), (-9, 37), (28.5, 16), (29, 38), (14, 39), (-20, 16), (40, 16))):
        liste.append(("cinar", x, y, 7 + i % 3))
    kadraj_kamera = KADRAJLAR[KADRAJ][0] if KADRAJ in KADRAJLAR else None
    for tur, x, y, h in liste:
        if kadraj_kamera and math.hypot(x - kadraj_kamera[0], BY(y) - kadraj_kamera[1]) < 3.5:
            continue
        if KADRAJ != "kus" and _gorus_engeli(x, BY(y)):
            continue
        agaclar[tur] += agac(Y, M, x, y, h, tur, int(x * 13 + y * 7))
    sab = {"zeytin": yaprak_sablonu("sablon_zeytin", 0.12, 0.035, M["yaprak_zeytin"]),
           "cinar": yaprak_sablonu("sablon_cinar", 0.16, 0.13, M["yaprak_cinar"]),
           "selvi": yaprak_sablonu("sablon_selvi", 0.10, 0.05, M["yaprak_selvi"])}
    yog = {"zeytin": 240, "cinar": 90, "selvi": 480}
    der = {"zeytin": 0.35, "cinar": 0.5, "selvi": 0.35}
    for tur, kum in agaclar.items():
        if kum:
            kumeleri_yap(M, kum, tur, sab[tur], yog[tur], der[tur])
    # şimşir top/bordür + lavanta
    cal = []
    for x in (6.2, 7.3, 13.0):
        cal.append(("kure", x, BY(-0.6), ZG + 0.35, 0.38, 0))
    for x in (3.6, 4.6, 16.5, 17.5, 18.5):
        cal.append(("kure", x, BY(20.1), ZG + 0.3, 0.33, 0))
    for yy in (-4.3,):
        for x in [-2.4 + k * 0.9 for k in range(11)]:
            cal.append(("kure", x, BY(yy), ZG + 0.3, 0.34, 0))
    sim = yaprak_sablonu("sablon_simsir", 0.05, 0.03, M["yaprak_simsir"])
    kumeleri_yap(M, cal, "simsir", sim, 1400, 0.12)
    # lavanta tarhı: yaya yolu kenarı ve teras önü
    lav = []
    for x in [0.3 + k * 0.55 for k in range(13)]:
        lav.append(("kure", x, BY(-1.2), ZG + 0.22, 0.28, 0))
    for x in [12.8 + k * 0.55 for k in range(3)]:
        pass
    for yy in [19.6 + k * 0.55 for k in range(3)]:
        pass
    lvs = sablon_nesne("sablon_lav", [(0, -0.005, 0), (0, 0.005, 0), (0, 0.004, 0.12), (0, -0.004, 0.12)],
                       [(0, 1, 2, 3)], M["lavanta"])
    kumeleri_yap(M, lav, "lavanta", lvs, 900, 0.05, dik=True)

def _gorus_engeli(X, Yb, pay=2.2):
    """Kamera–hedef doğrultusunda, kameraya yakın yarıda duran ağacı ele."""
    loc, hedef = KADRAJLAR[KADRAJ][0], KADRAJLAR[KADRAJ][1]
    ax, ay, bx, by = loc[0], loc[1], hedef[0], hedef[1]
    dx, dy = bx - ax, by - ay
    uz2 = dx * dx + dy * dy
    t = ((X - ax) * dx + (Yb - ay) * dy) / uz2
    if t < 0 or t > 0.75:
        return False
    d = abs((X - ax) * dy - (Yb - ay) * dx) / math.sqrt(uz2)
    return d < pay

def rnd_h(i):
    return 6.5 + (i * 37 % 10) / 5.0

def bahce_duvari(Y, M):
    # ön: taş kaide + antrasit dikey lamel çit; kapı açıklıkları
    yy = PY0
    parcalar = [(PX0, 7.8), (9.8, 14.1), (19.9, PX1)]
    for a, b in parcalar:
        Y.pkutu(M["tas"], a, yy, b, yy + 0.30, ZG - 0.1, ZG + 0.60)
        Y.pkutu(M["beton"], a - 0.02, yy - 0.02, b + 0.02, yy + 0.32, ZG + 0.60, ZG + 0.66)
        x = a + 0.05
        while x < b - 0.05:
            Y.pkutu(M["dograma"], x, yy + 0.12, x + 0.04, yy + 0.18, ZG + 0.66, ZG + 1.75)
            x += 0.11
        Y.pkutu(M["dograma"], a, yy + 0.11, b, yy + 0.19, ZG + 1.75, ZG + 1.80)
        for p in (a, b):
            Y.pkutu(M["tas"], p - 0.22 if p == b else p, yy - 0.05, p if p == b else p + 0.22, yy + 0.35,
                    ZG - 0.1, ZG + 1.90)
    # yaya kapısı (kapalı) ve araç kapısı (açık, sürgü duvar arkasında)
    x = 7.85
    while x < 9.75:
        Y.pkutu(M["dograma"], x, yy + 0.13, x + 0.04, yy + 0.17, ZG + 0.05, ZG + 1.80)
        x += 0.11
    Y.pkutu(M["dograma"], 7.82, yy + 0.12, 9.78, yy + 0.18, ZG + 0.02, ZG + 0.08)
    Y.pkutu(M["dograma"], 7.82, yy + 0.12, 9.78, yy + 0.18, ZG + 1.74, ZG + 1.80)
    Y.pkutu(M["lamba"], 9.95, yy - 0.02, 10.1, yy, ZG + 1.4, ZG + 1.6)
    # yan ve arka: sıvalı bahçe duvarı 1.80
    for (a0, b0, a1, b1) in [(PX0 - 0.25, PY0, PX0, PY1), (PX1, PY0, PX1 + 0.25, PY1), (PX0 - 0.25, PY1, PX1 + 0.25, PY1 + 0.25)]:
        Y.pkutu(M["siva"], a0, b0, a1, b1, ZG - 0.1, ZG + 1.80)
        Y.pkutu(M["beton"], a0 - 0.03, b0, a1 + 0.03, b1 + 0.0, ZG + 1.80, ZG + 1.86)

def bahce_isiklari(Y, M):
    noktalar = [(7.6, -3.9), (7.6, -2.6), (10.0, -3.9), (10.0, -2.6), (9.0, 20.0), (11.4, 20.0),
                (3.4, 20.9), (18.7, 20.9), (3.4, 29.2), (18.7, 29.2), (21.4, 3.0), (21.4, 17.5), (-1.5, 3.0),
                (-1.5, 17.5)]
    for x, y in noktalar:
        Y.pkutu(M["dograma"], x - 0.06, y - 0.06, x + 0.06, y + 0.06, ZG, ZG + 0.55)
        Y.pkutu(M["lamba"] if AKSAM else M["beton"], x - 0.055, y - 0.055, x + 0.055, y + 0.055, ZG + 0.42,
                ZG + 0.52)
    return noktalar

def sezlonglar(M):
    for cy in (23.2, 24.4, 25.6):
        x0, x1 = 16.5, 18.3
        yuvarlak_kutu(M, M["mobilya_ahsap"], x0, cy - 0.33, x1, cy + 0.33, ZG + 0.01, ZG + 0.28, 0.02)
        yuvarlak_kutu(M, M["perde"], x0 + 0.02, cy - 0.31, x1 - 0.5, cy + 0.31, ZG + 0.28, ZG + 0.36, 0.04)
        yuvarlak_kutu(M, M["perde"], x1 - 0.52, cy - 0.31, x1 - 0.02, cy + 0.31, ZG + 0.28, ZG + 0.62, 0.06)
    # şemsiye
    Y = Yigin("semsiye")
    Y.pkutu(M["dograma"], 17.37, 21.9, 17.43, 21.96, ZG, ZG + 2.3)
    Y.olustur()
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=1.5, radius2=0.05, depth=0.45, location=(17.4, BY(21.93), ZG + 2.35))
    o = bpy.context.object; o.data.materials.append(M["perde"])

def komsu_evler(Y, M):
    evler = [(-26, -2, 14, 12), (-28, 20, 13, 13), (32, -3, 15, 12), (33, 21, 14, 12), (-6, 42, 16, 12),
             (18, 43, 15, 12), (-14, -36, 16, 12), (14, -37, 15, 12)]
    for x, y, w, d in evler:
        Y.pkutu(M["siva"], x, y, x + w, y + d, ZG, ZG + 6.2)
        for z in (1.0, 4.1):
            for k in range(int(w / 3)):
                xx = x + 1.0 + k * 3.0
                Y.pkutu(M["komsu_cam"], xx, y - 0.02, xx + 1.4, y + 0.05, ZG + z, ZG + z + 1.5)
                Y.pkutu(M["komsu_cam"], xx, y + d - 0.05, xx + 1.4, y + d + 0.02, ZG + z, ZG + z + 1.5)
        # basit kırma çatı
        X0, X1, Y0, Y1 = x - 0.5, x + w + 0.5, BY(y + d + 0.5), BY(y - 0.5)
        ze = ZG + 6.3; zr = ze + (Y1 - Y0) / 2 * 0.3
        yr = (Y0 + Y1) / 2; hl = (Y1 - Y0) / 2
        v = [(X0, Y0, ze), (X1, Y0, ze), (X1, Y1, ze), (X0, Y1, ze), (X0 + hl, yr, zr), (X1 - hl, yr, zr)]
        Y.poly(M["kiremit"] if False else M["beton_k"], v, [(0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4)])

# ============================================================ ışık, kamera
# (kamera, hedef, lens, güneş yükseklik°, güneş azimut° [Blender: 0 = +Y kuzeyden saat yönü], hdri dönüş°)
KADRAJLAR = {
    "giris": ((-5.0, BY(-18.0), 2.6), (9.0, BY(5.0), 3.6), 26, 24, 292, 200),
    "bahce": ((19.6, BY(32.9), 1.60), (8.0, BY(10.0), 3.4), 22, 36, 215, 20),
    "kus":   ((-17.0, BY(47.0), 27.0), (10.0, BY(13.0), 0.0), 36, 42, 220, 20),
    "aksam": ((3.5, BY(33.0), 1.45), (11.0, BY(10.0), 3.3), 22, -3, 250, 20),
    "salon": ((0.75, BY(13.45), 1.35), (19.0, BY(11.9), 1.20), 17, 38, 215, 20),
}

def dunya(yuk, azm, hdri_don):
    s = bpy.context.scene
    d = bpy.data.worlds.new("dunya"); s.world = d; d.use_nodes = True
    nt = d.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_WORLD":
            nt.nodes.remove(n)
    cik = nt.nodes["World Output"]
    if AKSAM:
        gok = nt.nodes.new("ShaderNodeTexSky"); gok.sky_type = "NISHITA"
        gok.sun_elevation = math.radians(1.5); gok.sun_rotation = math.radians(azm)
        gok.sun_intensity = 0.15; gok.air_density = 1.4; gok.dust_density = 2.5
        bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 0.25
        nt.links.new(gok.outputs[0], bg.inputs["Color"])
        nt.links.new(bg.outputs[0], cik.inputs["Surface"])
        return
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(hdri_don))
    nt.links.new(tc.outputs["Generated"], mp.inputs[0])
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(os.path.expanduser("~/opt/hdri/symmetrical_garden_02.hdr"))
    nt.links.new(mp.outputs[0], env.inputs["Vector"])
    # HDRI güneşini kırp (gölgeler ayrı güneş lambasından)
    kr = nt.nodes.new("ShaderNodeMix"); kr.data_type = "RGBA"; kr.blend_type = "DARKEN"
    kr.inputs["Factor"].default_value = 1.0; kr.inputs["B"].default_value = (2.2, 2.2, 2.2, 1)
    nt.links.new(env.outputs["Color"], kr.inputs["A"])
    bg = nt.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 0.75
    nt.links.new(kr.outputs["Result"], bg.inputs["Color"])
    nt.links.new(bg.outputs[0], cik.inputs["Surface"])

def isiklar(yuk, azm):
    gun = bpy.data.lights.new("gunes", "SUN")
    if AKSAM:
        gun.energy = 0.0
    else:
        gun.energy = 3.4 if not IC else 3.0
        gun.color = (1.0, 0.95, 0.87)
    gun.angle = math.radians(1.2)
    o = bpy.data.objects.new("gunes", gun)
    bpy.context.collection.objects.link(o)
    el, az = math.radians(yuk), math.radians(azm)
    yon = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))  # güneşe doğru
    o.rotation_euler = (-yon).to_track_quat("-Z", "Y").to_euler()
    if AKSAM or IC:
        ic_isiklar()

def ic_isiklar():
    for kat in ("Zemin", "1. Kat"):
        for m in KATLAR[kat]:
            if m["tip"] not in ("yasam", "yatak", "mutfak", "sirkulasyon", "islak", "giyinme"):
                continue
            for r in m["r"]:
                x0, y0, x1, y1 = ic_sinir(r)
                a = (x1 - x0) * (y1 - y0)
                l = bpy.data.lights.new("ic", "AREA"); l.shape = "RECTANGLE"
                l.size, l.size_y = (x1 - x0) * 0.6, (y1 - y0) * 0.6
                l.energy = a * (11 if AKSAM else 6) * (0.5 if m["tip"] in ("islak", "giyinme") else 1.0)
                l.color = (1.0, 0.76, 0.50)
                o = bpy.data.objects.new("ic", l)
                bpy.context.collection.objects.link(o)
                o.location = ((x0 + x1) / 2, BY((y0 + y1) / 2), TAVAN[kat] - 0.05)
    if AKSAM:
        # dış: saçak altı, bahçe, havuz
        for x in (8.3, 10.0, 11.7):
            nokta((x, BY(-0.95), 2.6), 25, (1.0, 0.75, 0.45))
        for x, y in bahce_isik_noktalari:
            nokta((x, BY(y), ZG + 0.40), 6, (1.0, 0.75, 0.45))
        h = HAVUZ
        for x in (8.0, 11.0, 14.0):
            nokta((x, BY(h["y0"] + 0.4), -0.9), 90, (0.5, 0.85, 1.0))
        # ağaç altı spotları
        for x, y in ((2.2, 24.5), (19.0, 24.0), (1.5, -2.8)):
            s = bpy.data.lights.new("spot", "SPOT"); s.energy = 180; s.spot_size = math.radians(60)
            s.color = (1.0, 0.8, 0.55)
            o = bpy.data.objects.new("spot", s); bpy.context.collection.objects.link(o)
            o.location = (x + 0.6, BY(y) + 0.6, ZG + 0.2)
            o.rotation_euler = (math.radians(-15), math.radians(15), 0)
        # cephe aplikleri (garaj yanı, servis)
        for x in (14.3, 19.7):
            nokta((x, BY(-0.3), 2.3), 18, (1.0, 0.75, 0.45))

bahce_isik_noktalari = []

def nokta(loc, e, renk):
    l = bpy.data.lights.new("n", "POINT"); l.energy = e; l.color = renk; l.shadow_soft_size = 0.05
    o = bpy.data.objects.new("n", l); bpy.context.collection.objects.link(o)
    o.location = loc

def kamera(loc, hedef, lens):
    kam = bpy.data.cameras.new("kam"); kam.lens = lens; kam.sensor_width = 36
    ko = bpy.data.objects.new("kam", kam); bpy.context.collection.objects.link(ko)
    ko.location = Vector(loc)
    dx, dy = hedef[0] - loc[0], hedef[1] - loc[1]
    yatay = math.hypot(dx, dy)
    if KADRAJ == "kus":
        ko.rotation_euler = (Vector(hedef) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    else:
        ko.rotation_euler = (math.radians(90), 0.0, math.atan2(dy, dx) - math.radians(90))
        kam.shift_y = ((hedef[2] - loc[2]) / yatay) * (lens / 36.0)
    kam.clip_start = 0.05; kam.clip_end = 600
    bpy.context.scene.camera = ko

def render():
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = ORNEK
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.02
    s.cycles.use_denoising = True
    s.cycles.denoiser = "OPENIMAGEDENOISE"
    s.cycles.max_bounces = 6
    s.cycles.diffuse_bounces = 3
    s.cycles.glossy_bounces = 3
    s.cycles.transmission_bounces = 6
    s.cycles.transparent_max_bounces = 8
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.cycles.blur_glossy = 1.0
    s.cycles.sample_clamp_indirect = 8.0
    s.render.threads_mode = "FIXED"; s.render.threads = 4
    s.render.resolution_x = EN
    s.render.resolution_y = int(EN * ORAN)
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "JPEG"
    s.render.image_settings.quality = 93
    s.render.filepath = CIKTI
    s.view_settings.view_transform = "AgX"
    s.view_settings.look = "AgX - Medium High Contrast" if not AKSAM else "AgX - Base Contrast"
    s.view_settings.exposure = {"aksam": 0.9, "salon": -0.7}.get(KADRAJ, -0.15)
    os.makedirs(os.path.dirname(CIKTI), exist_ok=True)
    bpy.ops.render.render(write_still=True)
    print("YAZILDI:", CIKTI)

def kur():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M = MAL()
    MM.update({"tas": M["tas"], "ahsap": M["ahsap"]})
    Y = Yigin("bina")
    cepheler(Y, M)
    dosemeler(Y, M)
    ic_duvarlar(Y, M)
    merdiven(Y, M)
    mobilya_blok(Y, M, "Zemin")
    mobilya_blok(Y, M, "1. Kat")
    dis_elemanlar(Y, M)
    Y.olustur()
    cati(M)
    salon_detay(M)
    arazi(M)
    Y2 = Yigin("peyzaj")
    bahce_duvari(Y2, M)
    bahce_isik_noktalari.extend(bahce_isiklari(Y2, M))
    komsu_evler(Y2, M)
    bitkiler(M, Y2)
    Y2.olustur()
    sezlonglar(M)
    loc, hedef, lens, yuk, azm, hd = KADRAJLAR[KADRAJ]
    cim = bpy.data.objects.get("cim")
    if cim and KADRAJ not in ("kus",) and os.environ.get("CIMSIZ") != "1":
        yar = {"giris": 22, "bahce": 30, "aksam": 26, "salon": 22}[KADRAJ]
        cim_ekle(M, cim, Vector((loc[0], loc[1], ZG)), yar, float(os.environ.get("CIM_YOG", 700)))
    dunya(yuk, azm, hd)
    isiklar(yuk, azm)
    kamera(loc, hedef, lens)

if __name__ == "__main__":
    kur()
    if os.environ.get("KAYDET"):
        bpy.ops.wm.save_as_mainfile(filepath=os.environ["KAYDET"])
    render()
