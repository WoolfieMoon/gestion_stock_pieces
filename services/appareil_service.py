from models.appareil import Appareil
from database.db import get_conn

class AppareilService:
    def __init__(self):
        self.conn = get_conn()

    def ajouter(self, appareil: Appareil):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Appareil (libelle)
                VALUES (%s)
                RETURNING id
            """, (appareil.libelle,))
            appareil.id = cursor.fetchone()[0]
            self.conn.commit()
        return appareil

    def get_by_id(self, id: int) -> Appareil:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Appareil WHERE id = %s", (id,))
            row = cursor.fetchone()
            return Appareil(*row) if row else None

    def get_all(self) -> list[Appareil]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM Appareil")
            rows = cursor.fetchall()
            return [Appareil(*row) for row in rows]

    def mettre_a_jour(self, appareil: Appareil):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE Appareil SET libelle = %s WHERE id = %s
            """, (appareil.libelle, appareil.id))
            self.conn.commit()

    def supprimer(self, id: int):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM Appareil WHERE id = %s", (id,))
            self.conn.commit()
