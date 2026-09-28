"""Self-check of the pure logic (API normalization, options -> targets).

Stubs Home Assistant so it runs with plain Python: python tests/test_logic.py
Payloads are trimmed copies of real mappacarburanti.it responses.
"""
import os
import sys
import types


class _Any:
    def __init__(self, *a, **k): pass
    def __class_getitem__(cls, item): return cls


for _m in ["homeassistant", "homeassistant.config_entries", "homeassistant.core", "homeassistant.helpers",
           "homeassistant.helpers.aiohttp_client", "homeassistant.helpers.update_coordinator"]:
    sys.modules[_m] = types.ModuleType(_m)
    sys.modules[_m].__getattr__ = lambda name: _Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "custom_components"))

from prezzi_carburanti import const  # noqa: E402
from prezzi_carburanti.coordinator import _normalize  # noqa: E402

NATIONAL = {"date": "2026-09-20", "source": "MIMIT", "fuels": {
    "gasolio": {"avg": 2.3356, "min": 1.544, "max": 2.899, "count": 21158}}}
CITY = {"date": "2026-09-20", "source": "MIMIT", "city": {"name": "Verona", "region": "Veneto"},
        "fuels": {"gasolio": {"stats": {"avg": 2.1, "min": 1.6, "max": 2.3, "count": 80}}}}

n = _normalize("national", NATIONAL)
assert n["fuels"]["gasolio"] == {"avg": 2.3356, "min": 1.544, "max": 2.899, "count": 21158}
assert n["location"]["name"] == "Italia"
c = _normalize("citta", CITY)
assert c["fuels"]["gasolio"]["avg"] == 2.1 and c["location"] == {"name": "Verona", "region": "Veneto"}

targets = const.targets_from_options({"national": True, "province": ["verona"], "citta": ["reggio-emilia"]})
assert [const.target_key(*t) for t in targets] == ["national", "provincia_verona", "citta_reggio-emilia"]
assert const.target_name("citta", "reggio-emilia") == "Città — Reggio Emilia"
print("OK")
