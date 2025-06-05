import customtkinter as ctk
from tkinter import messagebox
from services.piece_service import PieceService
from services.mouvement_service import MouvementService
from services.fournisseur_service import FournisseurService
from models.mouvement import Mouvement
from database.db import get_conn
from datetime import datetime

class MouvementFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.piece_service = PieceService()
        self.mouvement_service = MouvementService()
        self.fournisseur_service = FournisseurService()

        self.pieces = self.piece_service.get_all()
        self.fournisseurs = self.fournisseur_service.get_all()
        self.map_piece = {f"{p.id} - {p.libelle}": p.id for p in self.pieces}
        self.map_fournisseur = {f.nom: f.id for f in self.fournisseurs}

        ctk.CTkLabel(self, text="Consultation des mouvements", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        # Formulaire d'ajout de mouvement
        self.form = ctk.CTkFrame(self)
        self.form.pack(padx=20, pady=(0, 10), fill="x")

        self.form.grid_columnconfigure(0, weight=1)
        self.form.grid_columnconfigure(1, weight=2)

        label_width = 180
        combo_width = 300

        ctk.CTkLabel(self.form, text="Sélectionner une pièce :", width=label_width, anchor="e").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_piece = ctk.CTkComboBox(self.form, values=list(self.map_piece.keys()), width=combo_width)
        self.combo_piece.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.form, text="Type de mouvement :", width=label_width, anchor="e").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_type = ctk.CTkComboBox(self.form, values=["entrée", "sortie"], width=combo_width)
        self.combo_type.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.form, text="Quantité :", width=label_width, anchor="e").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_quantite = ctk.CTkEntry(self.form, width=combo_width)
        self.entry_quantite.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(self.form, text="Fournisseur (pour entrée) :", width=label_width, anchor="e").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.combo_fournisseur = ctk.CTkComboBox(self.form, values=list(self.map_fournisseur.keys()), width=combo_width)
        self.combo_fournisseur.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.btn_valider = ctk.CTkButton(
            self,
            text="Enregistrer le mouvement",
            command=self.enregistrer_mouvement,
            width=250,
            height=40,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.btn_valider.pack(pady=20)

        # Tableau des mouvements
        self.frame_table = ctk.CTkFrame(self)
        self.frame_table.pack(fill="both", expand=True, padx=20, pady=10)
        self.frame_table.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        titres = ["ID", "Pièce", "Fournisseur", "Quantité", "Date", "Type"]
        for i, titre in enumerate(titres):
            ctk.CTkLabel(self.frame_table, text=titre, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=5, pady=5)

        self.afficher_mouvements()

    def enregistrer_mouvement(self):
        try:
            piece_id = self.map_piece.get(self.combo_piece.get())
            type_mv = self.combo_type.get()
            quantite = int(self.entry_quantite.get())
            fournisseur_id = self.map_fournisseur.get(self.combo_fournisseur.get()) if type_mv == "entrée" else None

            if not piece_id or not type_mv or quantite <= 0:
                raise ValueError("Veuillez remplir tous les champs correctement.")

            mouvement = Mouvement(
                id=None,
                type=type_mv,
                quantite=quantite,
                dateMouvement=datetime.today(),
                piece_id=piece_id,
                fournisseur_id=fournisseur_id
            )
            self.mouvement_service.ajouter(mouvement)
            self.afficher_mouvements()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def afficher_mouvements(self):
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT m.id, p.libelle, f.nom, m.quantite, m.dateMouvement, m.type
                FROM Mouvement m
                JOIN Piece p ON m.piece_id = p.id
                LEFT JOIN Fournisseur f ON m.fournisseur_id = f.id
                ORDER BY m.dateMouvement DESC
            """)
            mouvements = cursor.fetchall()

        for widget in self.frame_table.winfo_children()[6:]:
            widget.destroy()

        for i, (mid, lib_piece, nom_fournisseur, qte, date, type_m) in enumerate(mouvements, start=1):
            ctk.CTkLabel(self.frame_table, text=mid).grid(row=i, column=0, padx=5, pady=2)
            ctk.CTkLabel(self.frame_table, text=lib_piece).grid(row=i, column=1, padx=5, pady=2)
            ctk.CTkLabel(self.frame_table, text=nom_fournisseur or "-").grid(row=i, column=2, padx=5, pady=2)
            ctk.CTkLabel(self.frame_table, text=qte).grid(row=i, column=3, padx=5, pady=2)
            ctk.CTkLabel(self.frame_table, text=date.strftime("%d/%m/%Y")).grid(row=i, column=4, padx=5, pady=2)

            type_clean = type_m.strip().lower()
            if "entree" in type_clean:
                couleur = "#00dd00"
            elif "sortie" in type_clean:
                couleur = "#dd0000"
            else:
                couleur = "#888888"

            ctk.CTkLabel(
                self.frame_table,
                text=type_m.capitalize(),
                fg_color=couleur,
                text_color="white",
                corner_radius=6,
                font=ctk.CTkFont(weight="bold"),
                padx=8,
                pady=2
            ).grid(row=i, column=5, padx=5, pady=2)
