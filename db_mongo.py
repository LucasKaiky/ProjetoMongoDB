from pymongo import MongoClient, ASCENDING
from typing import Optional, List, Dict

class MongoDB:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.col = self.db["locais"]
        self.col.create_index([("cidade", ASCENDING)])

    def add_local(self, nome_local: str, cidade: str, latitude: float, longitude: float, descricao: str) -> str:
        doc = {
            "nome_local": nome_local.strip(),
            "cidade": cidade.strip(),
            "coordenadas": {"latitude": float(latitude), "longitude": float(longitude)},
            "descricao": descricao.strip()
        }
        res = self.col.insert_one(doc)
        return str(res.inserted_id)

    def list_locais(self, cidade: Optional[str] = None) -> List[Dict]:
        q = {}
        if cidade:
            q["cidade"] = cidade.strip()
        cur = self.col.find(q, {"_id": False})
        return list(cur)

    def all_locais(self) -> List[Dict]:
        cur = self.col.find({}, {"_id": False})
        return list(cur)
