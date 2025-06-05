from models.mouvement import Mouvement
from database.db import get_conn

class MouvementService:
    def __init__(self):
        self.conn = get_conn()

    def ajouter(self, mouvement: Mouvement):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Mouvement (type, quantite, dateMouvement, piece_id, fournisseur_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (mouvement.type, mouvement.quantite, mouvement.dateMouvement, mouvement.piece_id, mouvement.fournisseur_id))
            mouvement.id = cursor.fetchone()[0]
            self.conn.commit()
        return mouvement

    def get_by_id(self, id: int) -> Mouvement:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Mouvement WHERE id = %s", (id,))
            row = cursor.fetchone()
            return Mouvement(*row) if row else None

    def get_all(self) -> list[Mouvement]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Mouvement")
            rows = cursor.fetchall()
            return [Mouvement(*row) for row in rows]

    def supprimer(self, id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM Mouvement WHERE id = %s", (id,))
            self.conn.commit()
