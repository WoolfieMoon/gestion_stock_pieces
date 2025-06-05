# services/piece_service.py

from models.piece import Piece
from database.db import get_conn


class PieceService:
    def __init__(self):
        self.conn = get_conn()

    def ajouter(self, piece: Piece):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO Piece (libelle, stockActuel, prix, description)
                           VALUES (%s, %s, %s, %s) RETURNING id
                           """, (piece.libelle, piece.stockActuel, piece.prix, piece.description))
            piece.id = cursor.fetchone()[0]
            self.conn.commit()
        return piece

    def get_by_id(self, id: int) -> Piece:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Piece WHERE id = %s", (id,))
            row = cursor.fetchone()
            if row:
                return Piece(*row)
            return None

    def get_all(self) -> list[Piece]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Piece")
            rows = cursor.fetchall()
            return [Piece(*row) for row in rows]

    def mettre_a_jour(self, piece: Piece):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                           UPDATE Piece
                           SET libelle     = %s,
                               stockActuel = %s,
                               prix        = %s,
                               description = %s
                           WHERE id = %s
                           """, (piece.libelle, piece.stockActuel, piece.prix, piece.description, piece.id))
            self.conn.commit()

    def supprimer(self, id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM Piece WHERE id = %s", (id,))
            self.conn.commit()
