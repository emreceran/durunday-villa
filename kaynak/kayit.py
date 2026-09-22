# -*- coding: utf-8 -*-
"""Çizim kaydı — DXF/DWG çıktısı için.

Cizim (SVG yazıcısı) her öğeyi çizerken, kayıt açıksa öğeyi o anki katman, görünüş ve
dönüşüm bilgisiyle buraya da yazar. Kayıt kapalıyken (varsayılan) hiçbir şey değişmez;
SVG/PDF çıktısı aynı kalır. `dxf_yap.py` kaydı açar, paftaları üretir ve kaydı DXF'e çevirir.

- katman: iç içe bağlam yığını; en içteki geçerli. Fonksiyonlar `katmanli(ad)` ile sarılır,
  büyük fonksiyonların içindeki bloklar `with katman(ad):` ile işaretlenir.
- görünüş: pafta üzerindeki bir çizimin (plan, kesit, görünüş…) kâğıt orijini ve ölçeği.
  Görünüş dışındaki öğeler (çerçeve, antet, başlıklar) kâğıt alanına gider.
- dönüşüm: SVG <g transform> karşılığı (mobilya sembolleri).
"""
import math
from contextlib import contextmanager
from functools import wraps

AKTIF = False
KAYIT = []
_katman, _gorunum, _tf = [], [], []
_bastir = [0]


def basla():
    global AKTIF
    AKTIF = True
    KAYIT.clear(); _katman.clear(); _gorunum.clear(); _tf.clear(); _bastir[0] = 0


def bitir():
    global AKTIF
    AKTIF = False
    return list(KAYIT)


def aktif_katman():
    return _katman[-1] if _katman else None


@contextmanager
def katman(ad):
    _katman.append(ad)
    try:
        yield
    finally:
        _katman.pop()


def katmanli(ad):
    """Fonksiyonu bir katman bağlamında çalıştıran sarmalayıcı."""
    def sar(f):
        @wraps(f)
        def ic(*a, **k):
            with katman(ad):
                return f(*a, **k)
        ic._katmanli = ad
        return ic
    return sar


@contextmanager
def gorunum(ad, ox, oy, s, tur="plan"):
    """tur: 'plan' (kâğıtta y aşağı = kuzey→güney) ya da 'dusey' (kesit/görünüş, y = kot)."""
    _gorunum.append(dict(ad=ad, ox=ox, oy=oy, s=s, tur=tur))
    try:
        yield
    finally:
        _gorunum.pop()


@contextmanager
def donusum(dx, dy, aci=0.0):
    _tf.append((dx, dy, aci))
    try:
        yield
    finally:
        _tf.pop()


@contextmanager
def bastir():
    """İçerideki öğeler kaydedilmez (ör. ölçü zincirinin çizgileri — yerine DIMENSION yazılır)."""
    _bastir[0] += 1
    try:
        yield
    finally:
        _bastir[0] -= 1


def _uygula(x, y):
    for dx, dy, aci in reversed(_tf):
        if aci:
            a = math.radians(aci)
            x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        x, y = x + dx, y + dy
    return x, y


def kaydet(tur, **v):
    if not AKTIF or _bastir[0]:
        return
    if _tf:
        for k in ("pts",):
            if k in v:
                v[k] = [_uygula(*p) for p in v[k]]
        if "xy" in v:
            v["xy"] = _uygula(*v["xy"])
        if "r" in v and tur == "daire":
            pass
        v["rot"] = v.get("rot", 0) + sum(t[2] for t in _tf)
    KAYIT.append(dict(tur=tur, katman=aktif_katman(), gor=_gorunum[-1] if _gorunum else None, **v))
