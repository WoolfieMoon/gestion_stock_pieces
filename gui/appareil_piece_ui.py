# gui/appareil_piece_ui.py

import customtkinter as ctk
from tkinter import messagebox
from services.appareil_service import AppareilService
from services.piece_service import PieceService
from services.peut_utiliser_service import PeutUtiliserService
from models.peut_utiliser import PeutUtiliser
from database.db import get_conn

class AppareilPieceFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.appareil_service = AppareilService()
        self.piece_service = PieceService()
        self.peut_utiliser_service = PeutUtiliserService()

        # Récupère tous les appareils et construit la map { "id - libelle": id }
        self.appareils = self.appareil_service.get_all()
        self.map_appareil = { f"{a.id} - {a.libelle}": a.id for a in self.appareils }

        # Titre
        ctk.CTkLabel(
            self,
            text="Associer des pièces à un appareil",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(30, 20))

        # Combobox pour choisir l'appareil, on utilise 'command' pour appeler la méthode à chaque sélection
        self.combo_appareil = ctk.CTkComboBox(
            self,
            values=list(self.map_appareil.keys()),
            state="readonly",
            width=500,
            font=ctk.CTkFont(size=16),
            command=self.afficher_pieces_associees  # ← on remplace le bind par command
        )
        self.combo_appareil.pack(padx=20, pady=(0, 40))

        # Cadre comprenant 3 colonnes : pièces associées / flèches / pièces disponibles
        self.frame_contenu = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_contenu.pack(fill="both", expand=True, padx=20, pady=10)
        self.frame_contenu.grid_columnconfigure(0, weight=1)
        self.frame_contenu.grid_columnconfigure(1, weight=0)
        self.frame_contenu.grid_columnconfigure(2, weight=1)
        self.frame_contenu.grid_rowconfigure(1, weight=1)

        # Labels au-dessus des listes
        self.label_associees = ctk.CTkLabel(
            self.frame_contenu,
            text="Pièces associées",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="center"
        )
        self.label_associees.grid(row=0, column=0, sticky="n", pady=(0, 5))

        self.label_disponibles = ctk.CTkLabel(
            self.frame_contenu,
            text="Pièces disponibles",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="center"
        )
        self.label_disponibles.grid(row=0, column=2, sticky="n", pady=(0, 5))

        # Frame pour les pièces associées
        self.frame_associees = ctk.CTkScrollableFrame(self.frame_contenu, fg_color="#1f1f1f")
        self.frame_associees.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        # Frame pour les boutons d'action (flèches)
        self.frame_actions = ctk.CTkFrame(self.frame_contenu)
        self.frame_actions.grid(row=1, column=1, sticky="n")
        self.btn_to_associees = ctk.CTkButton(
            self.frame_actions,
            text="←",
            width=100,
            height=60,
            font=ctk.CTkFont(size=30),
            command=self.ajouter_selection
        )
        self.btn_to_disponibles = ctk.CTkButton(
            self.frame_actions,
            text="→",
            width=100,
            height=60,
            font=ctk.CTkFont(size=30),
            command=self.supprimer_selection
        )
        self.btn_to_associees.pack(pady=(20, 10))
        self.btn_to_disponibles.pack(pady=(10, 20))

        # Frame pour les pièces disponibles
        self.frame_disponibles = ctk.CTkScrollableFrame(self.frame_contenu, fg_color="#1f1f1f")
        self.frame_disponibles.grid(row=1, column=2, sticky="nsew", padx=(10, 0), pady=(0, 10))

        # Variables de sélection
        self.selection_associees = None
        self.selection_disponibles = None
        self.rows_associees = {}
        self.rows_disponibles = {}

        # Si au moins un appareil existe, on sélectionne le premier et on affiche ses pièces
        if self.map_appareil:
            first_key = list(self.map_appareil.keys())[0]
            self.combo_appareil.set(first_key)
            # Appel direct sans event : on fait simplement un appel à la méthode
            self.afficher_pieces_associees(first_key)

    def afficher_pieces_associees(self, selected_key=None):
        """
        Affiche la liste des pièces associées et disponibles pour l'appareil sélectionné.
        'selected_key' est envoyé automatiquement par le 'command' du CTkComboBox.
        """
        # Si la méthode est appelée via 'command', 'selected_key' contient la valeur texte (ex. "1 - Lave-linge")
        # Sinon, on récupère via combo_appareil.get()
        if selected_key:
            appareil_clef = selected_key
        else:
            appareil_clef = self.combo_appareil.get()

        id_appareil = self.map_appareil.get(appareil_clef)
        if id_appareil is None:
            messagebox.showerror("Erreur", "Veuillez sélectionner un appareil valide.")
            return

        # On interroge la base pour récupérer 2 listes : associées / disponibles
        conn = get_conn()
        with conn.cursor() as cursor:
            # Pièces déjà associées à cet appareil
            cursor.execute(
                "SELECT p.id, p.libelle "
                "FROM Piece p "
                "INNER JOIN PeutUtiliser pu ON pu.piece_id = p.id "
                "WHERE pu.appareil_id = %s",
                (id_appareil,)
            )
            associees = cursor.fetchall()

            # Pièces non associées (disponibles pour associer)
            cursor.execute(
                "SELECT p.id, p.libelle "
                "FROM Piece p "
                "WHERE p.id NOT IN (SELECT piece_id FROM PeutUtiliser WHERE appareil_id = %s)",
                (id_appareil,)
            )
            disponibles = cursor.fetchall()

        # Réinitialisation des sélections et des frames
        self.selection_associees = None
        self.selection_disponibles = None
        self.rows_associees.clear()
        self.rows_disponibles.clear()

        for widget in self.frame_associees.winfo_children():
            widget.destroy()
        for widget in self.frame_disponibles.winfo_children():
            widget.destroy()

        # Construction des lignes pour les pièces associées
        for id_associe, libelle in associees:
            row = ctk.CTkFrame(self.frame_associees, fg_color="#2a2a2a")
            row.pack(fill="x", padx=5, pady=2)
            label = ctk.CTkLabel(row, text=libelle, anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=6, pady=6)

            # Chaque ligne doit pouvoir être sélectionnée par clic : on mémorise l'id
            row.bind("<Button-1>", lambda e, pid=id_associe: self.selectionner(pid, True))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, pid=id_associe: self.selectionner(pid, True))

            self.rows_associees[id_associe] = row

        # Construction des lignes pour les pièces disponibles
        for id_dispo, libelle in disponibles:
            row = ctk.CTkFrame(self.frame_disponibles, fg_color="#2a2a2a")
            row.pack(fill="x", padx=5, pady=2)
            label = ctk.CTkLabel(row, text=libelle, anchor="w")
            label.pack(side="left", fill="x", expand=True, padx=6, pady=6)

            row.bind("<Button-1>", lambda e, pid=id_dispo: self.selectionner(pid, False))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda e, pid=id_dispo: self.selectionner(pid, False))

            self.rows_disponibles[id_dispo] = row

    def selectionner(self, pid, associe):
        """
        Met en surbrillance la ligne sélectionnée, et déselectionne l'autre liste.
        - associe=True  : on travaille sur la liste 'associees'
        - associe=False : on travaille sur la liste 'disponibles'
        """
        if associe:
            self.selection_associees = pid
            self.selection_disponibles = None
            for i, row in self.rows_associees.items():
                row.configure(fg_color="#145374" if i == pid else "#2a2a2a")
            for row in self.rows_disponibles.values():
                row.configure(fg_color="#2a2a2a")
        else:
            self.selection_disponibles = pid
            self.selection_associees = None
            for i, row in self.rows_disponibles.items():
                row.configure(fg_color="#145374" if i == pid else "#2a2a2a")
            for row in self.rows_associees.values():
                row.configure(fg_color="#2a2a2a")

    def ajouter_selection(self):
        """
        Déplace la pièce sélectionnée dans 'disponibles' vers 'associees'.
        """
        id_appareil = self.map_appareil.get(self.combo_appareil.get())
        if self.selection_disponibles:
            try:
                self.peut_utiliser_service.ajouter(
                    PeutUtiliser(appareil_id=id_appareil, piece_id=self.selection_disponibles)
                )
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        # On re-affiche immédiatement avec le nouvel état
        self.afficher_pieces_associees()

    def supprimer_selection(self):
        """
        Supprime l’association de la pièce sélectionnée dans 'associees'.
        """
        id_appareil = self.map_appareil.get(self.combo_appareil.get())
        if self.selection_associees:
            try:
                self.peut_utiliser_service.supprimer(id_appareil, self.selection_associees)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        # On re-affiche immédiatement avec le nouvel état
        self.afficher_pieces_associees()
