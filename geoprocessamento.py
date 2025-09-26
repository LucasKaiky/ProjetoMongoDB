from typing import List, Dict, Tuple
from geopy.distance import geodesic

def distancia_km(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return float(geodesic(a, b).km)

def locais_no_raio(locais: List[Dict], origem_lat: float, origem_lon: float, raio_km: float) -> List[Dict]:
    origem = (float(origem_lat), float(origem_lon))
    out = []
    for l in locais:
        lat = l.get("coordenadas", {}).get("latitude")
        lon = l.get("coordenadas", {}).get("longitude")
        if lat is None or lon is None:
            continue
        d = distancia_km(origem, (float(lat), float(lon)))
        if d <= float(raio_km):
            x = dict(l)
            x["distancia_km"] = round(d, 3)
            out.append(x)
    out.sort(key=lambda x: x["distancia_km"])
    return out
