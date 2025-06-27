from stdnum import isbn
import json
import csv
import re
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, timedelta

from bibliotheque import Livre, Membre, Bibliotheque
from visualisation import generer_statistiques


from exceptions import (
    LivreIndisponibleError,
    QuotaEmpruntDepasseError,
    MembreInexistantError,
    LivreInexistantError
)
 
def verifierEntierPositif(i):
    if not i.isdigit():
        raise ValueError("doit etre un nombre positif")
    return int(i)

def menu():
    biblio = Bibliotheque()
    biblio.chargerData()

    while True:
        print("\n=== GESTION BIBLIOTHÈQUE ===")
        print("1. Ajouter un livre")
        print("2. Inscrire un membre")
        print("3. Emprunter un livre")
        print("4. Rendre un livre")
        print("5. Lister tous les livres")
        print("6. Afficher les statistiques")
        print("7. Sauvegarder et quitter")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            isbn_code = input("ISBN : ").strip()
            try:
                if not isbn.is_valid(isbn_code):
                    print("Erreur : ISBN invalide.")
                    continue  # retourne au menu
            except Exception as e:
                print(f"Erreur lors de la validation de l'ISBN : {e}")
                continue
            try:
                titre = input("Titre : ").strip()
                if not titre:
                    raise ValueError("Le titre ne peut pas être vide.")
                auteur = input("Auteur : ").strip()
                if not auteur:
                    raise ValueError("L'auteur ne peut pas être vide.")
                while True:
                    annee_str = input("Année : ").strip()
                    if not annee_str:
                        print("L'année ne peut pas être vide.")
                        continue
                    if not annee_str.isdigit():
                        print("L'année doit être un nombre.")
                        continue
                    annee = int(annee_str)
                    break  
                
                if not genre:
                    raise ValueError("Le genre ne peut pas être vide.")
                livre = Livre(isbn_code, titre, auteur, annee, genre)
                biblio.ajouter_livre(livre)
                biblio.sauvegarderData()
                print("Livre ajouté avec succès.")
            except Exception as e:
                print(f"Erreur lors de l'ajout du livre : {e}") 

        elif choix == "2":
            id_membre = input("ID du membre : ").strip()
            try:
                id_membre=verifierEntierPositif(id_membre)
            except ValueError as e:
                print(f"Erreur lors de l'ajout d'membre : {e}")
                break
            try:    
                nom = input("Nom du membre : ").strip()
                if not nom:
                    raise ValueError("Le nom ne peut pas être vide.")
                membre = Membre(id_membre, nom)
                biblio.enregistrer_membre(membre)
                biblio.sauvegarderData()
            except Exception as e:
                print(f"Erreur : {e}")

        elif choix == "3":
            id_membre = input("ID du membre : ")
            try:
                membre = biblio.trouver_membre(id_membre)
            except MembreInexistantError as e:
                print(f"Erreur  Membre introuvable : {e}")

            titre = input("Titre du livre à emprunter : ")
            try:
                livre = biblio.trouver_livre(titre)
            except LivreInexistantError as e:
                print(f"Erreur  livre introuvable : {e}")

            biblio.emprunter_livre(membre, livre)
            
            


        elif choix == "4":
            id_membre = input("ID du membre : ")
            try:
                membre = biblio.trouver_membre(id_membre)
            except MembreInexistantError as e:
                print(f"Erreur  Membre introuvable : {e}")

            titre = input("Titre du livre à emprunter : ")
            try:
                livre = biblio.trouver_livre(titre)
            except LivreInexistantError as e:
                print(f"Erreur  livre introuvable : {e}")
            biblio.rendre_livre(membre, livre)

        elif choix == "5":
            biblio.afficher_livres()

        elif choix == "6":
            generer_statistiques(biblio)

        elif choix == "7":
            biblio.sauvegarderData()
            print("Données sauvegardées. Au revoir !")
            break

        else:
            print("Choix invalide, veuillez réessayer.")

if __name__ == "__main__":
    menu()
