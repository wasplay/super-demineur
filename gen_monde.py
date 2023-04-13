# Importation des modules
import math
from random import uniform


class case:
    mine = False  # mine ?
    flag = 0  # drapeau ? (et son image d'animation)
    uncovered = False  # découvert ?
    voisins = 0  # nombre de voisins ?
    center_anim = -1  # progression de l'animation quand on clique sur la case


# Création du monde (Définition de sa taille)
def generation_matrice(taille):
    grille = []
    for i in range(taille):
        line = []
        for i in range(taille):
            line.append(case())
        grille.append(line)

    return grille


# Permet d'afficher le monde de façon lisible sur la console
def afficher_monde(grille):

    s = len(grille)

    for i in range(s):
        for j in range(s):
            if grille[i][j].mine == True:
                print("X\t", end="")
            else:
                print(".\t", end="")
        print()


# Permet de générer la matrice contenant les bombes et les cases vides en fonction de la taille du monde(niveau de difficulté)
def generation_matrice_bombe(g_vars):

    g_vars.required_cases = g_vars.size * g_vars.size
    taille = g_vars.size
    grille = generation_matrice(taille)
    proba = 0.2

    for i in range(taille):
        for j in range(taille):
            if uniform(0, 1) < proba:
                grille[i][j].mine = True
                g_vars.required_cases -= 1

    g_vars.digitsCount_cases = len(str(g_vars.required_cases))

    return grille
