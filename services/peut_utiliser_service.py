from models.peut_utiliser import PeutUtiliser
from database.db import get_conn

class PeutUtiliserService:
    def __init__(self):
        self.conn = get_conn()

    def ajouter(self, relation: PeutUtiliser):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO PeutUtiliser (appareil_id, piece_id)
                VALUES (%s, %s)
            """, (relation.appareil_id, relation.piece_id))
            self.conn.commit()

    def supprimer(self, appareil_id: int, piece_id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM PeutUtiliser
                WHERE appareil_id = %s AND piece_id = %s
            """, (appareil_id, piece_id))
            self.conn.commit()
