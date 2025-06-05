from dataclasses import dataclass
from datetime import date

@dataclass
class Mouvement:
    id: int
    type: str                  # 'entree' ou 'sortie'
    quantite: int
    dateMouvement: date
    piece_id: int
    fournisseur_id: int = None
