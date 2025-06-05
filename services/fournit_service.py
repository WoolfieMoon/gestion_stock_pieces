from models.fournit import Fournit
from database.db import get_conn

class FournitService:
    def __init__(self):
        self.conn = get_conn()

    def ajouter(self, relation: Fournit):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Fournit (fournisseur_id, piece_id)
                VALUES (%s, %s)
            """, (relation.fournisseur_id, relation.piece_id))
            self.conn.commit()

    def supprimer(self, fournisseur_id: int, piece_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Fournit
                WHERE fournisseur_id = %s AND piece_id = %s
            """, (fournisseur_id, piece_id))
            self.conn.commit()
