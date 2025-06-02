from dataclasses import dataclass

@dataclass
class Piece:
    id: int
    libelle: str
    stockActuel: int
    prix: float
    description: str
