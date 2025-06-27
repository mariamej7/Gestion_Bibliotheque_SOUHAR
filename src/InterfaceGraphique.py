

from collections import Counter
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox



from bibliotheque import Livre, Membre, Bibliotheque
from visualisation import generer_statistiques


from exceptions import (
    LivreIndisponibleError,
    QuotaEmpruntDepasseError,
    MembreInexistantError,
    LivreInexistantError
)
 



# Interface graphique

class InterfaceBibliotheque(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion de Bibliothèque")
        self.geometry("1000x650")

        self.biblio = Bibliotheque()
        self.biblio.chargerData()

        self.notebook = ttk.Notebook(self)
        self.tab_livres = ttk.Frame(self.notebook)
        self.tab_membres = ttk.Frame(self.notebook)
        self.tab_emprunts = ttk.Frame(self.notebook)
        self.tab_stats = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_livres, text="Livres")
        self.notebook.add(self.tab_membres, text="Membres")
        self.notebook.add(self.tab_emprunts, text="Emprunts")
        self.notebook.add(self.tab_stats, text="Statistiques")
        self.notebook.pack(fill="both", expand=True)

        self.init_livres()
        self.init_membres()
        self.init_emprunts()
        self.init_stats()

    def init_livres(self):
        ttk.Label(self.tab_livres, text="Gestion des Livres", font=("Arial", 14)).pack(pady=10)
        self.tree_livres = ttk.Treeview(self.tab_livres, columns=("ISBN", "Titre", "Auteur", "Année", "Genre", "État"), show="headings")
        for col in ("ISBN", "Titre", "Auteur", "Année", "Genre", "État"):
            self.tree_livres.heading(col, text=col)
            self.tree_livres.column(col, width=100, anchor="center")
        self.tree_livres.pack(fill='both', expand=True, padx=10, pady=5)
        self.charger_livres()

        form = tk.Frame(self.tab_livres)
        form.pack(pady=10)
        self.entries_livres = {}
        for i, champ in enumerate(["ISBN", "Titre", "Auteur", "Année", "Genre"]):
            tk.Label(form, text=champ).grid(row=i, column=0, padx=5, pady=5)
            entry = tk.Entry(form)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries_livres[champ] = entry
        tk.Button(form, text="Ajouter Livre", command=self.ajouter_livre).grid(row=5, columnspan=2, pady=10)

    def charger_livres(self):
        for i in self.tree_livres.get_children():
            self.tree_livres.delete(i)
        for livre in self.biblio.livres:
            etat = "Disponible" if livre.disponible else "Emprunté"
            self.tree_livres.insert('', 'end', values=(livre.ISBN, livre.titre, livre.auteur, livre.annee, livre.genre, etat))

    def ajouter_livre(self):
        try:
            donnees = {champ: entry.get().strip() for champ, entry in self.entries_livres.items()}
            livre = Livre(**donnees)
            self.biblio.ajouter_livre(livre)
            self.biblio.sauvegarderData()
            self.charger_livres()
            messagebox.showinfo("Succès", f"Livre '{livre.titre}' ajouté.")
            for entry in self.entries_livres.values():
                entry.delete(0, tk.END)
            self.update_comboboxes()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def init_membres(self):
        ttk.Label(self.tab_membres, text="Gestion des Membres", font=("Arial", 14)).pack(pady=10)
        self.tree_membres = ttk.Treeview(self.tab_membres, columns=("ID", "Nom", "Livres empruntés"), show="headings")
        for col in ("ID", "Nom", "Livres empruntés"):
            self.tree_membres.heading(col, text=col)
            self.tree_membres.column(col, width=150, anchor="center")
        self.tree_membres.pack(fill='both', expand=True, padx=10, pady=5)
        self.charger_membres()

        form = tk.Frame(self.tab_membres)
        form.pack(pady=10)
        tk.Label(form, text="ID").grid(row=0, column=0)
        self.entry_id = tk.Entry(form)
        self.entry_id.grid(row=0, column=1)
        tk.Label(form, text="Nom").grid(row=1, column=0)
        self.entry_nom = tk.Entry(form)
        self.entry_nom.grid(row=1, column=1)
        tk.Button(form, text="Ajouter Membre", command=self.ajouter_membre).grid(row=2, columnspan=2, pady=10)

    def charger_membres(self):
        for i in self.tree_membres.get_children():
            self.tree_membres.delete(i)
        for membre in self.biblio.membres:
            self.tree_membres.insert('', 'end', values=(membre.ID, membre.nom, len(membre.livres_empruntes)))

    def ajouter_membre(self):
        id_ = self.entry_id.get().strip()
        nom = self.entry_nom.get().strip()
        if not id_.isdigit():
            messagebox.showerror("Erreur", "ID invalide")
            return
        try:
            membre = Membre(id_, nom)
            self.biblio.enregistrer_membre(membre)
            self.biblio.sauvegarderData()
            self.charger_membres()
            messagebox.showinfo("Succès", f"Membre '{nom}' ajouté.")
            self.entry_id.delete(0, tk.END)
            self.entry_nom.delete(0, tk.END)
            self.update_comboboxes()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def init_emprunts(self):
        ttk.Label(self.tab_emprunts, text="Emprunter/Rendre un livre", font=("Arial", 14)).pack(pady=10)
        frame = tk.Frame(self.tab_emprunts)
        frame.pack(pady=20)

        tk.Label(frame, text="ID Membre").grid(row=0, column=0)
        self.combo_membre = ttk.Combobox(frame, state="readonly")
        self.combo_membre.grid(row=0, column=1)

        tk.Label(frame, text="Titre Livre").grid(row=1, column=0)
        self.combo_livre = ttk.Combobox(frame, state="readonly")
        self.combo_livre.grid(row=1, column=1)

        tk.Button(frame, text="Emprunter", command=self.emprunter_livre).grid(row=2, column=0, pady=10)
        tk.Button(frame, text="Rendre", command=self.rendre_livre).grid(row=2, column=1, pady=10)

        self.tab_emprunts.bind("<Visibility>", lambda e: self.update_comboboxes())

    def update_comboboxes(self):
        self.combo_membre['values'] = [str(m.ID) for m in self.biblio.membres]
        self.combo_livre['values'] = [l.titre for l in self.biblio.livres]

    def emprunter_livre(self):
        ID = self.combo_membre.get()
        titre = self.combo_livre.get()
        if not ID or not titre:
            messagebox.showerror("Erreur", "Veuillez sélectionner un membre et un livre.")
            return
        try:
            self.biblio.emprunter_livre(ID, titre)
            self.biblio.sauvegarderData()
            self.charger_livres()
            self.charger_membres()
            messagebox.showinfo("Succès", f"Le membre {ID} a emprunté '{titre}'.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def rendre_livre(self):
        ID = self.combo_membre.get()
        titre = self.combo_livre.get()
        if not ID or not titre:
            messagebox.showerror("Erreur", "Veuillez sélectionner un membre et un livre.")
            return
        try:
            self.biblio.rendre_livre(ID, titre)
            self.biblio.sauvegarderData()
            self.charger_livres()
            self.charger_membres()
            messagebox.showinfo("Succès", f"Le membre {ID} a rendu '{titre}'.")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def init_stats(self):
        ttk.Label(self.tab_stats, text=f"Statistiques de la bibliothèque", font=("Consolas", 14)).pack(pady=20)
        btn_stats = tk.Button(self.tab_stats, text="Afficher les statistiques", command=lambda: generer_statistiques(self.biblio))
        btn_stats.pack()

if __name__ == "__main__":
    app = InterfaceBibliotheque()
    app.mainloop()
