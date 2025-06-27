# Statistiques
import csv
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime, timedelta



from bibliotheque import  Bibliotheque

def generer_statistiques(biblio):
    plt.figure(figsize=(12, 4))

    genres = Counter(livre.genre for livre in biblio.livres)
    plt.subplot(1, 3, 1)
    plt.pie(genres.values(), labels=genres.keys(), autopct='%1.1f%%')
    plt.title("Par genre")

    auteurs = Counter(livre.auteur for livre in biblio.livres).most_common(10)
    if auteurs:
        noms, quantites = zip(*auteurs)
        plt.subplot(1, 3, 2)
        plt.barh(noms, quantites)
        plt.title("Top auteurs")
        plt.xlabel("Livres")

    try:
        with open(biblio.historique_file, 'r') as f:
            dates = []
            for row in csv.reader(f, delimiter=';'):
                try:
                    dates.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"))
                except (ValueError, IndexError):
                    continue
        dernier_mois = datetime.now() - timedelta(days=30)
        recents = [d for d in dates if d >= dernier_mois]
        plt.subplot(1, 3, 3)
        plt.hist(recents, bins=30)
        plt.title("Activité 30 derniers jours")
        plt.xlabel("Date")
        plt.ylabel("Actions")
    except FileNotFoundError:
        print("Aucun historique trouvé.")

    plt.tight_layout()
    plt.savefig("stats.png")
    plt.show()