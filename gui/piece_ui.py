import tkinter as tk
from tkinter import ttk, messagebox
from services.piece_service import PieceService
from models.piece import Piece

class PieceUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Gestion des Pièces")
        self.service = PieceService()

        self.frame = tk.Frame(master, padx=10, pady=10)
        self.frame.pack(fill="both", expand=True)

        # Champs de formulaire
        tk.Label(self.frame, text="Libellé").grid(row=0, column=0, sticky="e")
        self.entry_libelle = tk.Entry(self.frame)
        self.entry_libelle.grid(row=0, column=1)

        tk.Label(self.frame, text="Stock actuel").grid(row=1, column=0, sticky="e")
        self.entry_stock = tk.Entry(self.frame)
        self.entry_stock.grid(row=1, column=1)

        tk.Label(self.frame, text="Prix").grid(row=2, column=0, sticky="e")
        self.entry_prix = tk.Entry(self.frame)
        self.entry_prix.grid(row=2, column=1)

        tk.Label(self.frame, text="Description").grid(row=3, column=0, sticky="e")
        self.entry_description = tk.Entry(self.frame)
        self.entry_description.grid(row=3, column=1)

        # Boutons
        tk.Button(self.frame, text="Ajouter", command=self.ajouter).grid(row=4, column=0, pady=10)
        tk.Button(self.frame, text="Modifier", command=self.modifier).grid(row=4, column=1)
        tk.Button(self.frame, text="Supprimer", command=self.supprimer).grid(row=4, column=2)
        tk.Button(self.frame, text="Recharger", command=self.charger_pieces).grid(row=4, column=3)

        # Table de résultats
        self.tree = ttk.Treeview(self.frame, columns=("id", "libelle", "stock", "prix", "description"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.grid(row=5, column=0, columnspan=4, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.charger_pieces()

    def charger_pieces(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for piece in self.service.get_all():
            self.tree.insert("", "end", values=(piece.id, piece.libelle, piece.stockActuel, piece.prix, piece.description))

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            values = self.tree.item(selected[0])["values"]
            self.entry_libelle.delete(0, tk.END)
            self.entry_libelle.insert(0, values[1])
            self.entry_stock.delete(0, tk.END)
            self.entry_stock.insert(0, values[2])
            self.entry_prix.delete(0, tk.END)
            self.entry_prix.insert(0, values[3])
            self.entry_description.delete(0, tk.END)
            self.entry_description.insert(0, values[4])

    def get_selected_id(self):
        selected = self.tree.selection()
        if selected:
            return self.tree.item(selected[0])["values"][0]
        return None

    def ajouter(self):
        try:
            piece = Piece(
                id=None,
                libelle=self.entry_libelle.get(),
                stockActuel=int(self.entry_stock.get()),
                prix=float(self.entry_prix.get()),
                description=self.entry_description.get()
            )
            self.service.ajouter(piece)
            self.charger_pieces()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def modifier(self):
        id = self.get_selected_id()
        if id is None:
            messagebox.showwarning("Attention", "Aucune pièce sélectionnée.")
            return
        try:
            piece = Piece(
                id=id,
                libelle=self.entry_libelle.get(),
                stockActuel=int(self.entry_stock.get()),
                prix=float(self.entry_prix.get()),
                description=self.entry_description.get()
            )
            self.service.mettre_a_jour(piece)
            self.charger_pieces()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def supprimer(self):
        id = self.get_selected_id()
        if id is None:
            messagebox.showwarning("Attention", "Aucune pièce sélectionnée.")
            return
        try:
            self.service.supprimer(id)
            self.charger_pieces()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
