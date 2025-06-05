# gui/appareil_ui.py
import customtkinter as ctk
from tkinter import messagebox
from services.appareil_service import AppareilService
from models.appareil import Appareil

class AppareilFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.service = AppareilService()
        self.selected_id = None
        self.selected_row_frame = None
        self.rows = []

        # === Titre ===
        self.title = ctk.CTkLabel(self, text="Gestion des Appareils", font=ctk.CTkFont(size=20, weight="bold"))
        self.title.pack(pady=10)

        # === Conteneur principal ===
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # === Table ===
        self.table = ctk.CTkScrollableFrame(self.main_frame, fg_color="#3a3a3a")
        self.table.grid(row=0, column=0, sticky="nsew", padx=(0, 20), pady=10)
        for i in range(2):
            self.table.grid_columnconfigure(i, weight=1, uniform="column")
        self._create_header()

        # === Boutons ===
        self.button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.button_frame.grid(row=0, column=1, sticky="ns", padx=10)
        self.button_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.btn_ajouter = ctk.CTkButton(self.button_frame, text="Ajouter", width=150, height=40, corner_radius=8, command=self.ajouter)
        self.btn_ajouter.grid(row=1, column=0, pady=(2, 4))

        self.btn_modifier = ctk.CTkButton(self.button_frame, text="Modifier", width=150, height=40, corner_radius=8, command=self.modifier)
        self.btn_modifier.grid(row=2, column=0, pady=(2, 4))

        self.btn_supprimer = ctk.CTkButton(self.button_frame, text="Supprimer", width=150, height=40, corner_radius=8, command=self.supprimer)
        self.btn_supprimer.grid(row=3, column=0, pady=(2, 4))

        self.btn_recharger = ctk.CTkButton(self.button_frame, text="Recharger", width=150, height=40, corner_radius=8, command=self.charger_appareils)
        self.btn_recharger.grid(row=4, column=0, pady=(2, 4))

        self.btn_initialiser = ctk.CTkButton(self.button_frame, text="Initialiser", width=150, height=40, corner_radius=8, command=self.initialiser)
        self.btn_initialiser.grid(row=5, column=0, pady=(2, 4))

        # === Formulaire ===
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.form_frame.grid_columnconfigure(0, weight=1)
        self.form_frame.grid_columnconfigure(1, weight=4)

        self.entry_libelle = self._add_labeled_entry(self.form_frame, "Libellé", 0, 0)

        self.charger_appareils()

    def _add_labeled_entry(self, frame, label, row, column):
        lbl = ctk.CTkLabel(frame, text=label)
        lbl.grid(row=row, column=column, sticky="w", padx=5)
        entry = ctk.CTkEntry(frame)
        entry.grid(row=row, column=column + 1, sticky="ew", padx=5, pady=5)
        return entry

    def _create_header(self):
        header_frame = ctk.CTkFrame(self.table, fg_color="#3a3a3a")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        header_frame.grid_columnconfigure((0, 1), weight=1, uniform="header")

        headers = ["ID", "Libellé"]
        for i, title in enumerate(headers):
            label = ctk.CTkLabel(header_frame, text=title, anchor="w", text_color="lightgray", font=ctk.CTkFont(size=14, weight="bold"))
            label.grid(row=0, column=i, sticky="ew", padx=6, pady=6)

        separator = ctk.CTkFrame(self.table, height=2, fg_color="#5a5a5a")
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 4))

    def charger_appareils(self):
        for row_frame in self.rows:
            row_frame.destroy()
        self.rows.clear()

        appareils = self.service.get_all()
        for i, appareil in enumerate(appareils):
            self.afficher_ligne(appareil, i)

    def afficher_ligne(self, appareil, index):
        row_frame = ctk.CTkFrame(self.table, fg_color="#3a3a3a", cursor="hand2")
        row_frame.grid(row=index + 2, column=0, columnspan=2, sticky="ew", padx=0, pady=2)
        row_frame.grid_columnconfigure((0, 1), weight=1, uniform="row")

        values = [str(appareil.id), appareil.libelle]
        for i, val in enumerate(values):
            label = ctk.CTkLabel(row_frame, text=val, anchor="w", text_color="white", font=ctk.CTkFont(size=14))
            label.grid(row=0, column=i, sticky="ew", padx=6, pady=6)

        row_frame.bind("<Button-1>", lambda e, a=appareil, rf=row_frame: self.selectionner(a, rf))
        for widget in row_frame.winfo_children():
            widget.bind("<Button-1>", lambda e, a=appareil, rf=row_frame: self.selectionner(a, rf))

        self.rows.append(row_frame)

    def selectionner(self, appareil, row_frame):
        if self.selected_row_frame and self.selected_row_frame.winfo_exists():
            self.selected_row_frame.configure(fg_color="#3a3a3a")
        row_frame.configure(fg_color="#1f6aa5")
        self.selected_row_frame = row_frame

        self.selected_id = appareil.id
        self.entry_libelle.delete(0, "end")
        self.entry_libelle.insert(0, appareil.libelle)

    def ajouter(self):
        try:
            appareil = Appareil(
                id=None,
                libelle=self.entry_libelle.get()
            )
            self.service.ajouter(appareil)
            self.charger_appareils()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def modifier(self):
        if self.selected_id is None:
            messagebox.showwarning("Attention", "Aucun appareil sélectionné.")
            return
        try:
            appareil = Appareil(
                id=self.selected_id,
                libelle=self.entry_libelle.get()
            )
            self.service.mettre_a_jour(appareil)
            self.charger_appareils()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def supprimer(self):
        if self.selected_id is None:
            messagebox.showwarning("Attention", "Aucun appareil sélectionné.")
            return
        try:
            self.service.supprimer(self.selected_id)
            self.selected_id = None
            self.selected_row_frame = None
            self.charger_appareils()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def initialiser(self):
        self.entry_libelle.delete(0, "end")

        if self.selected_row_frame and self.selected_row_frame.winfo_exists():
            self.selected_row_frame.configure(fg_color="#3a3a3a")

        self.selected_row_frame = None
        self.selected_id = None
