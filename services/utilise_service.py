from models.utilise import Utilise
from database.db import get_conn

class UtiliseService:
    def __init__(self):
        self.conn = get_conn()

    def ajouter(self, relation: Utilise):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Utilise (appareil_id, piece_id, quantiteUtilisee)
                VALUES (%s, %s, %s)
            """, (relation.appareil_id, relation.piece_id, relation.quantiteUtilisee))
            self.conn.commit()

    def supprimer(self, appareil_id: int, piece_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM Utilise
                WHERE appareil_id = %s AND piece_id = %s
            """, (appareil_id, piece_id))
            self.conn.commit()
