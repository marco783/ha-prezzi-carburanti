"""Self-check of the pure logic (MIMIT CSV aggregation, options -> targets): python tests/test_logic.py"""
import os
import sys
import types


class _Any:
    def __init__(self, *a, **k): pass
    def __class_getitem__(cls, item): return cls


for _m in ["aiohttp", "homeassistant.util", "homeassistant.util.dt", "homeassistant", "homeassistant.config_entries", "homeassistant.core", "homeassistant.helpers",
           "homeassistant.helpers.aiohttp_client", "homeassistant.helpers.update_coordinator"]:
    sys.modules[_m] = types.ModuleType(_m)
    sys.modules[_m].__getattr__ = lambda name: _Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from prezzi_carburanti import const  # noqa: E402
from prezzi_carburanti.mimit import compute  # noqa: E402

H = "idImpianto|Gestore|Bandiera|Tipo Impianto|Nome Impianto|Indirizzo|Comune|Provincia|Latitudine|Longitudine\n"
STATIONS = "Estrazione del 2026-09-28\n" + H + "\n".join([
    "1|X|Q8|Stradale|a|v|VERONA|VR|45|11",
    "2|X|Q8|Stradale|b|v|SOAVE|VR|45|11",
    "3|X|Q8|Autostradale|c|v|VERONA|VR|45|11",
    "4|X|Q8|Stradale|d|v|MILANO|MI|45|9",
    "5|X|Q8|Stradale|e|v|VERONA|VR|45|11",
])
P = "Estrazione del 2026-09-28\nidImpianto|descCarburante|prezzo|isSelf|dtComu\n" + "\n".join([
    "1|Gasolio|2.500|0|27/09/2026 10:00:00",   # served ignored: self exists
    "1|Gasolio|2.000|1|27/09/2026 10:00:00",
    "2|Gasolio|2.200|1|26/09/2026 10:00:00",
    "3|Gasolio|3.000|1|27/09/2026 10:00:00",   # motorway -> excluded
    "4|Gasolio|2.400|1|27/09/2026 10:00:00",
    "4|Blue Diesel|9.999|1|27/09/2026 10:00:00",  # special product -> ignored
    "5|Gasolio|1.000|1|10/09/2026 10:00:00",   # stale (>8 days)
    "5|GPL|0.800|0|27/09/2026 10:00:00",
])

T = [("national", None), ("provincia", "verona"), ("citta", "verona"), ("provincia", "milano")]
r = compute(P, STATIONS, T)
g = lambda k: r[k]["fuels"]["gasolio"]
assert g("provincia_verona") == {"avg": 2.1, "min": 2.0, "max": 2.2, "count": 2}, g("provincia_verona")
assert g("citta_verona") == {"avg": 2.0, "min": 2.0, "max": 2.0, "count": 1}
assert g("national")["count"] == 3 and g("provincia_milano")["avg"] == 2.4
assert r["provincia_verona"]["fuels"]["gpl"]["count"] == 1
assert r["provincia_verona"]["date"] == "2026-09-28"
assert r["provincia_verona"]["location"] == {"name": "Verona", "region": "Veneto"}

targets = const.targets_from_options({"national": True, "province": ["verona"], "citta": ["reggio-emilia"]})
assert [const.target_key(*t) for t in targets] == ["national", "provincia_verona", "citta_reggio-emilia"]
assert const.target_name("citta", "reggio-emilia") == "Città — Reggio Emilia"
print("OK")
