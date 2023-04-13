import gen_monde


# Permet de générer la liste 2D contenant le nombre de mines autour de chaque cellule.

def voisin_matrice(grille):
    '''
    Objectif : déterminer le nombre de mines autour de chaque cellule d'une grille

    Paramètres
    ----------

    Une grille d'objets de types "case"

    Returns
    -------
    null

    '''

    for x in range(0, len(grille)):
        for y in range(0, len(grille)):
            grille[x][y].voisins = nbr_voisin_cellule(grille, x, y)


def nbr_voisin_cellule(grille, x, y):
    '''
    Objectif : déterminer le nombre de mines autour d'une cellule

    Paramètres
    ----------

    x (entier) : numéro de ligne de la cellule choisie
    y (entier) : numéro de colonne de la cellule choisie

    Returns
    -------
    nb (entier) : le nombre de mines aux alentours

    '''

    nb = 0
    if x-1 >= 0 and y-1 >= 0 and grille[x-1][y-1].mine == True:
        nb += 1
    if x-1 >= 0 and grille[x-1][y].mine == True:
        nb += 1
    if x-1 >= 0 and y+1 < len(grille) and grille[x-1][y+1].mine == True:
        nb += 1
    if y-1 >= 0 and grille[x][y-1].mine == True:
        nb += 1
    if y+1 < len(grille) and grille[x][y+1].mine == True:
        nb += 1
    if x+1 < len(grille) and y-1 >= 0 and grille[x+1][y-1].mine == True:
        nb += 1
    if x+1 < len(grille) and grille[x+1][y].mine == True:
        nb += 1
    if x+1 < len(grille) and y+1 < len(grille) and grille[x+1][y+1].mine == True:
        nb += 1
    return nb
