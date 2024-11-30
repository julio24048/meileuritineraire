
#import des librairies
import math
from random import randrange, randint
import pandas as pd

#définition des dataframes et variabls
df = pd.read_csv("info_communes_parc.csv", sep=";")
elite = 0.2
tx_mutations = 0.1
taille_echantillon = 1500
trajets = pd.DataFrame({"itineraire":[],"kms":[],"pois":[],"hotel_j3":[],"hotel_j7":[]})
nb_etapes = 10
noms_villes = df["insee"].tolist()
nb_iterations = 200

#définition des fonctions

def distance (depart, arrivee) :
    """
    Calcul de la distane à vol d'oiseau entre 2 villes en récupérant leurs latitudes et longituds.
    """
    tmp = df.loc[df["insee"].isin([depart,arrivee]), "lat_centre":"long_centre"]
    x_dep = tmp.iloc[0,1]
    y_dep = tmp.iloc[0,0]
    x_arr = tmp.iloc[1,1]
    y_arr = tmp.iloc[1,0]
    distance = math.acos(math.sin(math.radians(x_dep))*math.sin(math.radians(x_arr))+math.cos(math.radians(x_dep))*math.cos(math.radians(x_arr))*math.cos(math.radians(y_dep-y_arr)))*6371
    return round(distance,1)

def generateur_aleatoire (n_etapes, n_iterations, liste) :
    """
    Renvoie une liste de listes afin de générer des trajets de façon aléatoire.
    """
    trajets = []
    for h in range(n_iterations) :
        liste_voyage = []
        tmp_liste = liste.copy()
        for i in range(n_etapes) :
            nombre_alea = randrange(0, len(tmp_liste), 1)
            liste_voyage.append(tmp_liste[nombre_alea])
            tmp_liste.pop(nombre_alea)
        trajets.append(liste_voyage)
    return trajets

def notation () :
    """
    Cette fonction travaille sur le dataframe trajets.
    Elle effectue les opérations suivantes :
    - calcul de la distance totale du trajet
    - calcul du nombre de pois totaux du trajet
    - renvoi du nombre d'hotels 3 étoiles ou plus aux jours 3 et 7 du parcours
    """
    global trajets
    #decompte distance
    for i in range(taille_echantillon) :
        distance_totale = 0
        nb_poi = 0
        for j in range(9) :
            distance_totale += distance(trajets.iloc[i,0][j],trajets.iloc[i,0][j+1])
        trajets.iloc[i,1] = distance_totale
    #decompte POI
        for k in range(10) :
            valeur = df.loc[df["insee"] == trajets.iloc[i,0][k], "nb_poi"].iloc[0]
            nb_poi += valeur
        trajets.iloc[i,2] = nb_poi
        trajets.iloc[i,3] = df.loc[df["insee"] == trajets.iloc[i,0][2], "nb_hotels_3_etoiles_min"].iloc[0]
        trajets.iloc[i,4] = df.loc[df["insee"] == trajets.iloc[i,0][6], "nb_hotels_3_etoiles_min"].iloc[0]

def mutations (tx_mutation) :
    """
    Création d'une liste de mutants avec 3 possibilités de mutations choisies de façon aléatoire.
    Insertion, échange de place ou inversion de séquence.
    """
    global trajets
    tmp_liste = trajets.sample(frac=tx_mutation).iloc[:,0].tolist()
    liste_mutants = []
    for genome in tmp_liste :
        alea = randint(0,2)
        if alea == 0 :
            gene1 = randrange(0,10)
            gene2 = gene1
            while gene2 == gene1 :
                gene2 = randrange(0,10)
            genome[gene1], genome[gene2] = genome[gene2], genome[gene1]
            liste_mutants.append(genome)
        elif alea == 1 :
            gene1 = randrange(0,10)
            gene2 = gene1
            while gene2 == gene1 :
                gene2 = randrange(0,10)
            gene_mutation = genome[gene2]
            del(genome[gene2])
            genome.insert(gene1 + 1, gene_mutation)
            liste_mutants.append(genome)
        else :
            debut = randrange(0,10)
            fin = randrange(debut + 1,10) if debut != 9 else 9
            debut_liste = genome[0:debut]
            liste_inverse = genome[debut:fin + 1]
            liste_inverse.reverse()
            fin_liste = genome[fin + 1 : 10]
            genome = debut_liste + liste_inverse + fin_liste
            liste_mutants.append(genome)
    return liste_mutants

def croisements(nb_croisements) :
    """
    Imitation d'un processus de brassage génétique de type "reproduction sexuée" par brassage
    entre les séquences de 2 trajets "parents".
    Une dose de mutation est mise en place pour éviter qu'une même ville se retrouve 2 fois
    dans une liste de trajets.
    """
    global trajets
    tmp_liste = trajets.iloc[:,0].tolist()
    liste_croisements = []
    for i in range(nb_croisements) :
        genome_enfant = []
        parent1 = randrange(0,len(tmp_liste))
        parent2 = parent1
        while parent2 == parent1 :
            parent2 = randrange(0,len(tmp_liste))
        for j in range(10) :
            if tmp_liste[parent1][j] not in genome_enfant and tmp_liste[parent2][j] not in genome_enfant :
                alea = randint(0,1)
                genome_enfant.append(tmp_liste[parent1][j]) if alea == 0 else genome_enfant.append(tmp_liste[parent2][j])
            elif (tmp_liste[parent1][j] in genome_enfant and tmp_liste[parent2][j] not in genome_enfant) or (tmp_liste[parent1][j] not in genome_enfant and tmp_liste[parent2][j] in genome_enfant):
                genome_enfant.append(tmp_liste[parent2][j]) if tmp_liste[parent1][j] in genome_enfant else genome_enfant.append(tmp_liste[parent1][j])
            else :
                genes_disponibles = []
                for k in tmp_liste[parent1] + tmp_liste[parent2] :
                    if k not in genes_disponibles and k not in genome_enfant :
                        genes_disponibles.append(k)
                genome_enfant.append(genes_disponibles[randrange(0,len(genes_disponibles))])
        liste_croisements.append(genome_enfant)
    return liste_croisements

#info de prise en charge du premier trajet
print("génération 1 :")
#génération d'une population de trajets de façon aléatoire.
trajets["itineraire"] = generateur_aleatoire(nb_etapes,taille_echantillon, noms_villes)
#notation des trajets de la première génération
notation()
"""
tris et boucles pour connaitre la répartition par déciles des distances en km et les 
nombres de POI. Les trajets sont ensuite triés pour regrouper les trajets des déciles les plus
performants vers les moins performants.
Le départage se fait ensuite au nombre de pois puis de kms.
"""
trajets = trajets.sort_values(by="kms",ascending=True)
trajets["decile_km"] = 0
for i in range(trajets.shape[0]) :
    trajets.iloc[i,5] = math.floor(i / (taille_echantillon / 10)) + 1
trajets = trajets.sort_values(by="pois",ascending=False)
trajets["decile_poi"] = 0
for i in range(trajets.shape[0]) :
    trajets.iloc[i,6] = math.floor(i / (taille_echantillon / 10)) + 1
trajets["decile_cumul"] = 10
for i in range(trajets.shape[0]) :
    for j in range(1,10) :
        if trajets.iloc[i,5] == j and trajets.iloc[i,6] == j :
            trajets.iloc[i,7] = j
trajets = trajets.sort_values(by=["decile_cumul","pois","kms"],ascending=[True,False,True])
#affichage des kms et pois du meilleur tranet en filtrant les trajets où les conditions liées aux hotels sont remplies.
print (
    str(round(trajets[(trajets["hotel_j3"]> 0) & (trajets["hotel_j7"]> 0)].iloc[0,1],1)) + " kms" +
    " - " + str(trajets[(trajets["hotel_j3"]> 0) & (trajets["hotel_j7"]> 0)].iloc[0,2]) + " pois"
)

#itérations pour optimiser le trajet par sélection naturelle sur plusieurs générations
for i in range(2,nb_iterations + 1) :
    """
    on aaplique une stratégie élitaire. On récupère tous les trajets dont les déciles de
    kilométrage et POI sont de 1 à 9. S'ils représentent une population suérieure au nombre
    maximum assignée à l'élite, on sélectionne la quote part des meilleures valeurs du dataframe
    """
    if trajets[trajets["decile_cumul"]!=10].shape[0] < math.floor(taille_echantillon * elite) :
        nextgen = trajets.iloc[0:trajets[trajets["decile_cumul"]!=10].shape[0],0].tolist()
    else :
        nextgen = trajets.iloc[0:math.floor(taille_echantillon * elite),0].tolist()
    #génération des listes de mutants et de croisements
    lesmutants = mutations(tx_mutations)
    nb_croisements = taille_echantillon - len(nextgen) - len(lesmutants)
    lesenfants = croisements(nb_croisements)
    #création la nouvelle génération 
    print(f"génération {i} :")
    #génération d'nu nouveau dataframe à partir des élites conservées, des croisements et des mutants
    trajets = pd.DataFrame({"itineraire":[],"kms":[],"pois":[],"hotel_j3":[],"hotel_j7":[]})
    trajets["itineraire"] = nextgen + lesenfants + lesmutants
    #notation des trajets (même processus que précedemment sauf pour le prompt)
    notation()
    trajets = trajets.sort_values(by="kms",ascending=True)
    trajets["decile_km"] = 0
    for j in range(trajets.shape[0]) :
        trajets.iloc[j,5] = math.floor(j / (taille_echantillon / 10)) + 1
    trajets = trajets.sort_values(by="pois",ascending=False)
    trajets["decile_poi"] = 0
    for k in range(trajets.shape[0]) :
        trajets.iloc[k,6] = math.floor(k / (taille_echantillon / 10)) + 1
    trajets["decile_cumul"] = 10
    for l in range(trajets.shape[0]) :
        for m in range(1,10) :
            if trajets.iloc[l,5] == m and trajets.iloc[l,6] == m :
                trajets.iloc[l,7] = m
    trajets = trajets.sort_values(by=["decile_cumul","pois","kms"],ascending=[True,False,True])
    # dans l'itération seules les caractéristiques sont affichées sauf à la dernière ou on a le détail du trajet
    if i == nb_iterations :
        print ("trajet retenu - " + 
               str(round(trajets[(trajets["hotel_j3"]> 0) & (trajets["hotel_j7"]> 0)].iloc[0,1],1)) + " kms" +
               " - " + str(trajets[(trajets["hotel_j3"]> 0) & (trajets["hotel_j7"]> 0)].iloc[0,2]) + " pois :"
        )
        for i in trajets[(trajets["hotel_j3"] > 0) & (trajets["hotel_j7"] > 0)].iloc[0,0] :
            print(df.loc[df["insee"] == i, "nom"].iloc[0] + " ")
    else : 
        print (
            str(round(trajets[(trajets["hotel_j3"]> 0) & (trajets["hotel_j7"]> 0)].iloc[0,1],1)) + " kms" +
            " - " + str(trajets[(trajets["hotel_j3"]> 0) & (trajets["hotel_j7"]> 0)].iloc[0,2]) + " pois"
        )
