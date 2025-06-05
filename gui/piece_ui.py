# gui/piece_ui.py
import customtkinter as ctk
from tkinter import messagebox
from tkinter import StringVar
from services.piece_service import PieceService
from services.fournisseur_service import FournisseurService
from services.mouvement_service import MouvementService
from models.piece import Piece
from models.mouvement import Mouvement
from datetime import date
from gui.mouvement_ui import MouvementFrame
from database.db import get_conn

class PieceFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.service = PieceService()
        self.fournisseur_service = FournisseurService()
        self.mouvement_service = MouvementService()

        self.selected_id = None
        self.selected_row_frame = None
        self.rows = []

        # === Titre ===
        self.title = ctk.CTkLabel(self, text="Gestion des Pièces", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.pack(pady=10)

        # === Conteneur principal ===
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # === Table ===
        self.table = ctk.CTkScrollableFrame(self.main_frame, fg_color="#3a3a3a")
        self.table.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)
        for i in range(4):
            self.table.grid_columnconfigure(i, weight=1, uniform="column")
        self._create_header()

        # === Boutons ===
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=0, column=1, sticky="ns", padx=10)
        self.button_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.btn_ajouter = ctk.CTkButton(
            self.button_frame,
            text="Ajouter",
            width=150,
            height=40,
            corner_radius=8,
            command=self.ajouter
        )
        self.btn_ajouter.grid(row=1, column=0, pady=(2, 4))

        self.btn_modifier = ctk.CTkButton(
            self.button_frame,
            text="Modifier",
            width=150,
            height=40,
            corner_radius=8,
            command=self.modifier
        )
        self.btn_modifier.grid(row=2, column=0, pady=(2, 4))

        self.btn_supprimer = ctk.CTkButton(
            self.button_frame,
            text="Supprimer",
            width=150,
            height=40,
            corner_radius=8,
            command=self.supprimer
        )
        self.btn_supprimer.grid(row=3, column=0, pady=(2, 4))

        self.btn_recharger = ctk.CTkButton(
            self.button_frame,
            text="Recharger",
            width=150,
            height=40,
            corner_radius=8,
            command=self.charger_pieces
        )
        self.btn_recharger.grid(row=4, column=0, pady=(2, 4))

        self.btn_initialiser = ctk.CTkButton(
            self.button_frame,
            text="Initialiser",
            width=150,
            height=40,
            corner_radius=8,
            command=self.initialiser
        )
        self.btn_initialiser.grid(row=5, column=0, pady=(2, 4))

        # === Formulaire ===
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=20, pady=(0, 10))
        for i in range(4):
            self.form_frame.grid_columnconfigure(i, weight=1)

        self.entry_libelle = self._add_labeled_entry(self.form_frame, "Libellé", 0, 0)
        self.entry_stock = self._add_labeled_entry(self.form_frame, "Stock actuel (initial)", 1, 0)
        self.entry_prix = self._add_labeled_entry(self.form_frame, "Prix", 0, 2)
        self.entry_description = self._add_labeled_entry(self.form_frame, "Description", 1, 2)

        self.combo_var = StringVar()
        self.combo_fournisseur = ctk.CTkComboBox(self.form_frame, variable=self.combo_var, values=[])
        ctk.CTkLabel(self.form_frame, text="Fournisseur").grid(row=2, column=0, sticky="w", padx=5)
        self.combo_fournisseur.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.fournisseur_map = {}
        self._charger_fournisseurs()
        self.charger_pieces()

    def _charger_fournisseurs(self):
        fournisseurs = self.fournisseur_service.get_all()
        noms = [f.nom for f in fournisseurs]
        self.combo_fournisseur.configure(values=noms)
        self.fournisseur_map = {f.nom: f.id for f in fournisseurs}

    def _add_labeled_entry(self, frame, label, row, column):
        lbl = ctk.CTkLabel(frame, text=label)
        lbl.grid(row=row, column=column, sticky="w", padx=5)
        entry = ctk.CTkEntry(frame)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=5, pady=5)
        return entry

    def _create_header(self):
        header_frame = ctk.CTkFrame(self.table, fg_color="#3a3a3a")
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew")
        header_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="header")

        headers = ["ID", "Libellé", "Stock", "Prix"]
        for i, title in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=title,
                anchor="w",
                text_color="lightgray",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            label.grid(row=0, column=i, sticky="ew", padx=6, pady=6)

        separator = ctk.CTkFrame(self.table, height=2, fg_color="#5a5a5a")
        separator.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 4))

    def charger_pieces(self):
        for row_frame in self.rows:
            row_frame.destroy()
        self.rows.clear()

        conn = get_conn()
        with conn.cursor() as cursor:
            # Requête corrigée : utiliser stockActuel de Piece comme base + mouvements
            cursor.execute("""
                SELECT p.id,
                       p.libelle,
                       p.stockActuel + COALESCE(SUM(
                         CASE
                           WHEN LOWER(TRIM(m.type)) = 'entrée' THEN m.quantite
                           WHEN LOWER(TRIM(m.type)) = 'sortie' THEN -m.quantite
                           ELSE 0
                         END
                       ), 0) AS stock,
                       p.prix
                FROM Piece p
                LEFT JOIN Mouvement m ON m.piece_id = p.id
                GROUP BY p.id, p.libelle, p.stockActuel, p.prix
                ORDER BY p.id
            """)
            pieces = cursor.fetchall()

        for i, (pid, libelle, stock, prix) in enumerate(pieces):
            # Créer un objet Piece temporaire pour l'affichage
            piece = Piece(id=pid, libelle=libelle, stockActuel=stock, prix=prix, description="")
            self.afficher_ligne(piece, i)

    def afficher_ligne(self, piece: Piece, index: int):
        row_frame = ctk.CTkFrame(self.table, fg_color="#3a3a3a", cursor="hand2")
        row_frame.grid(row=index + 2, column=0, columnspan=4, sticky="ew", padx=0, pady=2)
        row_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="row")

        values = [
            str(piece.id),
            piece.libelle,
            str(piece.stockActuel),
            f"{piece.prix:.2f} €"
        ]
        for i, val in enumerate(values):
            label = ctk.CTkLabel(
                row_frame,
                text=val,
                anchor="w",
                text_color="white",
                font=ctk.CTkFont(size=14)
            )
            label.grid(row=0, column=i, sticky="ew", padx=6, pady=6)

        row_frame.bind("<Button-1>", lambda e, p=piece, rf=row_frame: self.selectionner(p, rf))
        for widget in row_frame.winfo_children():
            widget.bind("<Button-1>", lambda e, p=piece, rf=row_frame: self.selectionner(p, rf))

        self.rows.append(row_frame)

    def selectionner(self, piece: Piece, row_frame: ctk.CTkFrame):
        if self.selected_row_frame and self.selected_row_frame.winfo_exists():
            self.selected_row_frame.configure(fg_color="#3a3a3a")
        row_frame.configure(fg_color="#1f6aa5")
        self.selected_row_frame = row_frame

        self.selected_id = piece.id
        self.entry_libelle.delete(0, "end")
        self.entry_libelle.insert(0, piece.libelle)
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, str(piece.stockActuel))
        self.entry_prix.delete(0, "end")
        self.entry_prix.insert(0, str(piece.prix))
        self.entry_description.delete(0, "end")
        self.entry_description.insert(0, piece.description or "")

    def ajouter(self):
        try:
            piece = Piece(
                id=None,
                libelle=self.entry_libelle.get(),
                stockActuel=int(self.entry_stock.get()),
                prix=float(self.entry_prix.get()),
                description=self.entry_description.get()
            )
            piece = self.service.ajouter(piece)

            fournisseur_nom = self.combo_var.get()
            fournisseur_id = self.fournisseur_map.get(fournisseur_nom)

            if fournisseur_id:
                mouvement = Mouvement(
                    id=None,
                    type="entrée",
                    quantite=piece.stockActuel,
                    dateMouvement=date.today(),
                    piece_id=piece.id,
                    fournisseur_id=fournisseur_id
                )
                self.mouvement_service.ajouter(mouvement)

            self.charger_pieces()
            MouvementFrame.rafraichir()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def modifier(self):
        if self.selected_id is None:
            messagebox.showwarning("Attention", "Aucune pièce sélectionnée.")
            return
        try:
            piece = Piece(
                id=self.selected_id,
                libelle=self.entry_libelle.get(),
                stockActuel=int(self.entry_stock.get()),
                prix=float(self.entry_prix.get()),
                description=self.entry_description.get()
            )
            self.service.mettre_a_jour(piece)
            self.charger_pieces()
            MouvementFrame.rafraichir()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def supprimer(self):
        if self.selected_id is None:
            messagebox.showwarning("Attention", "Aucune pièce sélectionnée.")
            return
        try:
            self.service.supprimer(self.selected_id)
            self.selected_id = None
            self.selected_row_frame = None
            self.charger_pieces()
            MouvementFrame.rafraichir()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def initialiser(self):
        self.entry_libelle.delete(0, "end")
        self.entry_stock.delete(0, "end")
        self.entry_prix.delete(0, "end")
        self.entry_description.delete(0, "end")
        self.combo_fournisseur.set("")

        if self.selected_row_frame and self.selected_row_frame.winfo_exists():
            self.selected_row_frame.configure(fg_color="#3a3a3a")

        self.selected_row_frame = None
        self.selected_id = None
