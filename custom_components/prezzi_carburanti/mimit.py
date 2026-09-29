"""Pure parsing/aggregation of the MIMIT open-data CSVs (no Home Assistant imports).

Rules (same as the official MIMIT "media regionale stradale"): motorway stations
excluded, only base products, one price per station and fuel (self preferred),
prices older than MAX_AGE_DAYS ignored.
"""
from __future__ import annotations

import csv
import io
import re
import unicodedata
from datetime import date, timedelta

from .const import SCOPE_CITTA, SCOPE_NATIONAL, SCOPE_PROVINCIA, target_key
from .provinces import PROVINCES

MAX_AGE_DAYS = 8
FUELS = {"benzina": "benzina", "gasolio": "gasolio", "gpl": "gpl", "metano": "metano"}
SOURCE = "MIMIT (impianti stradali, esclusi autostradali)"

_SIGLA_TO_SLUG = {s: slug for slug, p in PROVINCES.items() for s in p["sigle"]}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


def _rows(text: str):
    """Skip the 'Estrazione del ...' line; yield dict rows of the '|' CSV."""
    head, _, body = text.partition("\n")
    return head, csv.DictReader(io.StringIO(body), delimiter="|", quoting=csv.QUOTE_NONE)


def decode(raw: bytes) -> str:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def compute(prices_text: str, stations_text: str, targets: list[tuple[str, str | None]]) -> dict:
    """-> {target_key: {fuels: {fuel: {avg,min,max,count}}, date, source, location}}."""
    head, price_rows = _rows(prices_text)
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", head)
    if not m:
        raise ValueError("intestazione 'Estrazione del ...' non trovata in prezzo_alle_8.csv")
    extraction = date(*map(int, m.groups()))
    oldest = extraction - timedelta(days=MAX_AGE_DAYS)

    # station id -> (province slug | None, normalized comune); motorways dropped here
    stations = {}
    for r in _rows(stations_text)[1]:
        if "autostrad" in (r.get("Tipo Impianto") or "").lower():
            continue
        stations[r["idImpianto"]] = (_SIGLA_TO_SLUG.get((r.get("Provincia") or "").strip().upper()),
                                     _norm(r.get("Comune") or ""))

    # (station, fuel) -> (is_self, date, price): self preferred, then most recent
    best = {}
    for r in price_rows:
        fuel = FUELS.get((r.get("descCarburante") or "").strip().lower())
        sid = r.get("idImpianto")
        if not fuel or sid not in stations:
            continue
        try:
            price = float(r["prezzo"].replace(",", "."))
            d = r["dtComu"]
            day = date(int(d[6:10]), int(d[3:5]), int(d[:2]))
        except (ValueError, KeyError, TypeError, IndexError):
            continue
        if day < oldest or not 0.3 < price < 5:
            continue
        cand = (r.get("isSelf") == "1", day, price)
        if cand[:2] > best.get((sid, fuel), (False, date.min))[:2]:
            best[(sid, fuel)] = cand

    wanted = {target_key(*t): t for t in targets}
    acc: dict[str, dict[str, list[float]]] = {k: {} for k in wanted}
    for (sid, fuel), (_, _, price) in best.items():
        slug, comune = stations[sid]
        keys = [target_key(SCOPE_NATIONAL, None)]
        if slug:
            keys.append(target_key(SCOPE_PROVINCIA, slug))
            if comune == _norm(PROVINCES[slug]["name"]):
                keys.append(target_key(SCOPE_CITTA, slug))
        for k in keys:
            if k in acc:
                acc[k].setdefault(fuel, []).append(price)

    out = {}
    for k, (scope, slug) in wanted.items():
        fuels = {f: {"avg": round(sum(v) / len(v), 4), "min": min(v), "max": max(v), "count": len(v)}
                 for f, v in acc[k].items()}
        if not fuels:
            continue  # missing -> sensors of this location unavailable
        if scope == SCOPE_NATIONAL:
            loc = {"name": "Italia", "region": None}
        else:
            loc = {"name": PROVINCES[slug]["name"], "region": PROVINCES[slug]["region"]}
        out[k] = {"fuels": fuels, "date": extraction.isoformat(), "source": SOURCE, "location": loc}
    return out
