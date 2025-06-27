import json
import csv
import re
from datetime import datetime

# Classes métier

class Livre:
    def __init__(self, ISBN, titre, auteur, annee, genre, disponible=True):
        self.ISBN = ISBN
        self.titre = titre
        self.auteur = auteur
        self.annee = annee
        self.genre = genre
        self.disponible = disponible

    def __str__(self):
        etat = "emprunté" if not self.disponible else "disponible"
        return f"Livre(ISBN={self.ISBN}, titre={self.titre}, auteur={self.auteur}, annee={self.annee}, genre={self.genre}, état={etat})"

    def emprunter(self):
        if not self.disponible:
            raise LivreIndisponibleError("Le livre est déjà emprunté.")
        self.disponible = False

    def rendre(self):
        if self.disponible:
            raise Exception("Le livre n'a pas été emprunté.")
        self.disponible = True

    def to_dict(self):
        return {
            "ISBN": self.ISBN,
            "titre": self.titre,
            "auteur": self.auteur,
            "annee": self.annee,
            "genre": self.genre,
            "disponible": self.disponible
        }



class Membre:
    def __init__(self, ID, nom):
        self.ID = int(ID)
        self.nom = nom
        self.livres_empruntes = []

    def __str__(self):
        return f"(ID: {self.ID}, Nom: {self.nom}, Livres empruntés: {len(self.livres_empruntes)})"

    def emprunter_livre(self, livre):
        if len(self.livres_empruntes) >= 3:
            raise QuotaEmpruntDepasseError("Le membre a atteint le quota maximal d'emprunts.")
        livre.emprunter()
        self.livres_empruntes.append(livre)

    def rendre_livre(self, livre):
        if livre not in self.livres_empruntes:
            raise Exception("Ce livre n'a pas été emprunté par ce membre.")
        livre.rendre()
        self.livres_empruntes.remove(livre)

class Bibliotheque:
    def __init__(self):
        self.livres = []
        self.membres = []
        self.historique_file = "historique.csv"

    def ajouter_livre(self, livre):
        if any(l.ISBN == livre.ISBN for l in self.livres):
            raise Exception(f"Un livre avec l'ISBN {livre.ISBN} existe déjà.")
        self.livres.append(livre)

    def enregistrer_membre(self, membre):
        if any(m.ID == membre.ID for m in self.membres):
            raise Exception(f"Un membre avec l'ID {membre.ID} existe déjà.")
        self.membres.append(membre)

    def trouver_livre(self, titre):
        livre = next((l for l in self.livres if l.titre == titre), None)
        if not livre:
            raise LivreInexistantError(f"Livre '{titre}' introuvable.")
        return livre

    def trouver_membre(self, ID):
        membre = next((m for m in self.membres if m.ID == int(ID)), None)
        if not membre:
            raise MembreInexistantError(f"Membre avec ID {ID} introuvable.")
        return membre

   

    def emprunter_livre(self, membre, livre):
        membre.emprunter_livre(livre)
        self.log_action(livre.ISBN, membre.ID, "emprunt")

    def rendre_livre(self, membre, livre):
        membre.rendre_livre(livre)
        self.log_action(livre.ISBN, membre.ID, "rendu")

        

    def log_action(self, isbn, id_membre, action):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.historique_file, "a", newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([date, isbn, id_membre, action])

    def exporter_emprunts_csv(self, fichier_sortie="emprunts_export.csv"):
        try:
            with open(self.historique_file, 'r') as f_in, open(fichier_sortie, 'w', newline='') as f_out:
                lecteur = csv.reader(f_in, delimiter=';')
                ecrivain = csv.writer(f_out)
                ecrivain.writerow(["Date", "ISBN", "ID Membre", "Action"])
                for ligne in lecteur:
                    ecrivain.writerow(ligne)
            return True
        except FileNotFoundError:
            return False

    def sauvegarderData(self):
        with open("livres.json", "w", encoding='utf-8') as f:
            json.dump([l.to_dict() for l in self.livres], f, ensure_ascii=False, indent=2)
        with open("membres.json", "w", encoding='utf-8') as f:
            json.dump([
                {
                    "ID": m.ID,
                    "nom": m.nom,
                    "livres_empruntes": [l.ISBN for l in m.livres_empruntes]
                } for m in self.membres
            ], f, ensure_ascii=False, indent=2)

    def chargerData(self):
        try:
            with open("livres.json", "r", encoding='utf-8') as f:
                livres_data = json.load(f)
                self.livres = [Livre(**l) for l in livres_data]
            livres_dict = {l.ISBN: l for l in self.livres}
            with open("membres.json", "r", encoding='utf-8') as f:
                membres_data = json.load(f)
                self.membres = []
                for m in membres_data:
                    membre = Membre(m["ID"], m["nom"])
                    for isbn in m["livres_empruntes"]:
                        if isbn in livres_dict:
                            membre.livres_empruntes.append(livres_dict[isbn])
                    self.membres.append(membre)
        except FileNotFoundError:
            self.livres = []
            self.membres = []

    def afficher_livres(self):
        print("Liste des livres dans la bibliothèque :")
        for livre in self.livres:
            print(livre)

    def __str__(self):
        return f"Bibliothèque: {len(self.membres)} membres, {len(self.livres)} livres."
