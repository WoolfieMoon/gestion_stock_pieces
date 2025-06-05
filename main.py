# gui/main.py

import customtkinter as ctk
from gui.piece_ui import PieceFrame
from gui.fournisseur_ui import FournisseurFrame
from gui.appareil_ui import AppareilFrame
from gui.mouvement_ui import MouvementFrame
from gui.appareil_piece_ui import AppareilPieceFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Application de gestion")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.geometry("1000x600")

        # === Barre de navigation ===
        self.navbar = ctk.CTkFrame(self, height=50)
        self.navbar.pack(fill="x")

        # === Conteneur principal pour les frames ===
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True)

        # Instanciation des différents onglets (frames)
        self.frames = {
            "Mouvements": MouvementFrame(self.content_frame),
            "Appareils": AppareilFrame(self.content_frame),
            "Pièces": PieceFrame(self.content_frame),
            "Assoc. Appareil/Pièce": AppareilPieceFrame(self.content_frame),
            "Fournisseurs": FournisseurFrame(self.content_frame)
        }

        # Au départ, on cache toutes les frames
        for frame in self.frames.values():
            frame.pack_forget()

        # Création des boutons dans la navbar
        self.buttons = {}
        for i, name in enumerate(self.frames):
            btn = ctk.CTkButton(
                self.navbar,
                text=name,
                fg_color="transparent",          # par défaut, inactif = transparent
                hover_color="#444444",
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=0,
                command=lambda n=name: self.show_frame(n)
            )
            btn.grid(row=0, column=i, padx=(0, 0), pady=0, sticky="ew")
            # On aligne la grille pour que chaque bouton prenne la même largeur
            self.navbar.grid_columnconfigure(i, weight=1)
            self.buttons[name] = btn

        # On affiche par défaut l’onglet “Mouvements”
        self.show_frame("Mouvements")

    def show_frame(self, name):
        """
        Affiche la frame associée au bouton 'name' et met à jour la couleur des onglets.
        """

        # 1) Cacher toutes les frames
        for frame in self.frames.values():
            frame.pack_forget()

        # 2) Afficher la frame demandée
        self.frames[name].pack(fill="both", expand=True)

        # 3) Mettre à jour la couleur de chaque bouton : actif / inactif
        for btn_name, btn in self.buttons.items():
            if btn_name == name:
                # Couleur du bouton actif
                btn.configure(
                    fg_color="#1f6aa5",
                    text_color="white"
                )
            else:
                # Couleur des boutons inactifs
                btn.configure(
                    fg_color="transparent",
                    text_color="white"
                )


if __name__ == "__main__":
    app = App()
    app.mainloop()
