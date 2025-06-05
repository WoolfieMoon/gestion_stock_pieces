# database/db.py

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

def init_db():
    conn = get_conn()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Appareil (
                id SERIAL PRIMARY KEY,
                libelle VARCHAR(255) NOT NULL UNIQUE
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Piece (
                id SERIAL PRIMARY KEY,
                libelle VARCHAR(255) NOT NULL UNIQUE,
                stockActuel INTEGER NOT NULL,
                prix NUMERIC(10, 2) NOT NULL,
                description TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Fournisseur (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(255) NOT NULL UNIQUE,
                tel VARCHAR(20),
                mail VARCHAR(255)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Mouvement (
                id SERIAL PRIMARY KEY,
                type VARCHAR(10) NOT NULL CHECK (type IN ('entree', 'sortie')),
                quantite INTEGER NOT NULL,
                dateMouvement DATE NOT NULL,
                piece_id INTEGER NOT NULL,
                fournisseur_id INTEGER,
                FOREIGN KEY (piece_id) REFERENCES Piece(id),
                FOREIGN KEY (fournisseur_id) REFERENCES Fournisseur(id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS PeutUtiliser (
                appareil_id INTEGER NOT NULL,
                piece_id INTEGER NOT NULL,
                PRIMARY KEY (appareil_id, piece_id),
                FOREIGN KEY (appareil_id) REFERENCES Appareil(id),
                FOREIGN KEY (piece_id) REFERENCES Piece(id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Utilise (
                appareil_id INTEGER NOT NULL,
                piece_id INTEGER NOT NULL,
                quantiteUtilisee INTEGER NOT NULL,
                PRIMARY KEY (appareil_id, piece_id),
                FOREIGN KEY (appareil_id) REFERENCES Appareil(id),
                FOREIGN KEY (piece_id) REFERENCES Piece(id)
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Fournit (
                fournisseur_id INTEGER NOT NULL,
                piece_id INTEGER NOT NULL,
                PRIMARY KEY (fournisseur_id, piece_id),
                FOREIGN KEY (fournisseur_id) REFERENCES Fournisseur(id),
                FOREIGN KEY (piece_id) REFERENCES Piece(id)
            );
        """)

        conn.commit()
        print("✅ Tables créées avec succès.")
    except Exception as e:
        print("❌ Erreur lors de la création des tables :", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def insert_data():
    conn = get_conn()
    cursor = conn.cursor()

    try:
        # Appareil
        cursor.execute("INSERT INTO Appareil (libelle) VALUES ('iPhone 12') ON CONFLICT DO NOTHING;")
        cursor.execute("INSERT INTO Appareil (libelle) VALUES ('Samsung Galaxy S22') ON CONFLICT DO NOTHING;")

        # Piece
        cursor.execute("""
            INSERT INTO Piece (libelle, stockActuel, prix, description)
            VALUES 
            ('Écran OLED', 50, 120.00, 'Écran OLED haute résolution')
            ON CONFLICT DO NOTHING;
        """)
        cursor.execute("""
            INSERT INTO Piece (libelle, stockActuel, prix, description)
            VALUES 
            ('Batterie 3000mAh', 100, 30.50, 'Batterie lithium pour smartphone')
            ON CONFLICT DO NOTHING;
        """)

        # Fournisseur
        cursor.execute("""
            INSERT INTO Fournisseur (nom, tel, mail)
            VALUES 
            ('TechParts Co.', '0123456789', 'contact@techparts.com')
            ON CONFLICT DO NOTHING;
        """)
        cursor.execute("""
            INSERT INTO Fournisseur (nom, tel, mail)
            VALUES 
            ('SmartSupply', '0987654321', 'info@smartsupply.com')
            ON CONFLICT DO NOTHING;
        """)

        # Manuellement lier les ID (optionnel si FK disponibles, sinon vous pouvez SELECT les ID dynamiquement)

        # Mouvement
        cursor.execute("""
            INSERT INTO Mouvement (type, quantite, dateMouvement, piece_id, fournisseur_id)
            VALUES ('entree', 20, '2025-05-01', 1, 1),
                   ('sortie', 5, '2025-05-03', 1, NULL),
                   ('entree', 50, '2025-05-04', 2, 2)
            ON CONFLICT DO NOTHING;
        """)

        # PeutUtiliser
        cursor.execute("""
            INSERT INTO PeutUtiliser (appareil_id, piece_id)
            VALUES (1, 1), (1, 2), (2, 2)
            ON CONFLICT DO NOTHING;
        """)

        # Utilise
        cursor.execute("""
            INSERT INTO Utilise (appareil_id, piece_id, quantiteUtilisee)
            VALUES (1, 1, 1), (1, 2, 1), (2, 2, 1)
            ON CONFLICT DO NOTHING;
        """)

        # Fournit
        cursor.execute("""
            INSERT INTO Fournit (fournisseur_id, piece_id)
            VALUES (1, 1), (2, 2)
            ON CONFLICT DO NOTHING;
        """)

        conn.commit()
        print("✅ Données insérées avec succès.")
    except Exception as e:
        print("❌ Erreur d'insertion :", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

