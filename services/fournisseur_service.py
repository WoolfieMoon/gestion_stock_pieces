from models.fournisseur import Fournisseur
from database.db import get_conn

class FournisseurService:
    def __init__(self):
        self.conn = get_conn()

    def ajouter(self, fournisseur: Fournisseur):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Fournisseur (nom, tel, mail)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (fournisseur.nom, fournisseur.tel, fournisseur.mail))
            fournisseur.id = cursor.fetchone()[0]
            self.conn.commit()
        return fournisseur

    def get_by_id(self, id: int) -> Fournisseur:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Fournisseur WHERE id = %s", (id,))
            row = cursor.fetchone()
            return Fournisseur(*row) if row else None

    def get_all(self) -> list[Fournisseur]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Fournisseur")
            rows = cursor.fetchall()
            return [Fournisseur(*row) for row in rows]

    def mettre_a_jour(self, fournisseur: Fournisseur):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Fournisseur
                SET nom = %s, tel = %s, mail = %s
                WHERE id = %s
            """, (fournisseur.nom, fournisseur.tel, fournisseur.mail, fournisseur.id))
            self.conn.commit()

    def supprimer(self, id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM Fournisseur WHERE id = %s", (id,))
            self.conn.commit()
