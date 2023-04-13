import pygame
from pygame.locals import *
import threading as th  # permet d'utiliser les timers
from random import uniform
from sys import exit  # permet de quitter le jeu avec la croix windows

import gen_monde
import voisins

# correspond aux effets d'onde de choc dans le jeu
class shockwave:
    lifetime = 1
    ogLifetime = 1
    pos = (0, 0)
    color = (0, 0, 0)
    width = 1
    speed = 1
    size = 1


# INITIALISATION PYGAME
pygame.init()
pygame.display.set_caption("Super Démineur")
icon = pygame.image.load("Graphics/mine.png")
pygame.display.set_icon(icon)

logo_font = pygame.font.Font("Graphics/font.ttf", 70)
ui_font = pygame.font.Font("Graphics/mono_font.ttf", 30)
bt_font = pygame.font.Font("Graphics/font.ttf", 30)
tiny_font = pygame.font.Font("Graphics/font.ttf", 20)
cases_font = pygame.font.Font("Graphics/mono_font.ttf", 12)

# UI
snd_hover = pygame.mixer.Sound('Audio/hover.ogg')
snd_hover.set_volume(0.5)
snd_button = pygame.mixer.Sound('Audio/button.ogg')
snd_back = pygame.mixer.Sound('Audio/back.ogg')
snd_up = pygame.mixer.Sound('Audio/up.ogg')
snd_down = pygame.mixer.Sound('Audio/down.ogg')
snd_intro = pygame.mixer.Sound('Audio/intro.ogg')
snd_intro.set_volume(0.5)

# GAME
game_hover = pygame.mixer.Sound('Audio/game_hover.ogg')
game_hover.set_volume(0.1)
game_damage = pygame.mixer.Sound('Audio/game_damage.ogg')
game_defeat = pygame.mixer.Sound('Audio/game_defeat.ogg')
game_victory = pygame.mixer.Sound('Audio/game_victory.ogg')
game_empty = pygame.mixer.Sound('Audio/game_empty.ogg')
game_collect = pygame.mixer.Sound('Audio/game_collect2.ogg')
game_collect.set_volume(0.5)
game_flag = pygame.mixer.Sound('Audio/game_flag.ogg')
game_flag.set_volume(0.5)
game_unflag = pygame.mixer.Sound('Audio/game_unflag.ogg')
game_unflag.set_volume(0.5)

fen_axex = 512
fen_axey = 512
fen = pygame.display.set_mode((fen_axex, fen_axey))
pygame.display.update()

# notre magnifique palette de couleurs
orange = (221, 161, 81)
dark_orange = (188, 108, 37)
bckg = (254, 250, 224)
dark_bckg = (239, 210, 160)
green = (60, 200, 20)
nice_red = (166, 41, 22)

# la liste qui stocke les ondes de chocs affichées à l'écran
shockwaves = []

# les difficultées dispo
diff_names = ["Facile", "Normal", "Difficile", "BRUTAL EXTREME"]
lives_names = ["Désactivées", "1", "2", "3 (Max)"]

# la classe "game_vars" issue du script main.py
g_vars = 0

# SCENE 0 - Fonction qui dessine l'écran de démarrage (vide)
def null_scene():
    fen.fill(bckg)

# Fonction qui récupère les infos liées à la souris et aux évenements windows (ici, fermeture de l'application)
def inputs(game_vars):
    global g_vars
    g_vars = game_vars
    g_vars.hover = False

    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            g_vars.lmouse_click = True
        if event.type == MOUSEBUTTONDOWN and event.button == 3:
            g_vars.rmouse_click = True
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    g_vars.mouse_pos = pygame.mouse.get_pos()

# SCENE 1 - Fonction qui dessine le menu
def menu():
    fen.fill(bckg)  # on rempli le fond de la couleur "bckg"
    tp = g_vars.t_prog  # tp = transition progress

    # Voir les commentaires dans les fonctions en dessous
    draw_text(logo_font, "Super Démineur", (fen_axex/2, 60), lerp_vector(bckg, orange, tp), bckg)

    draw_button(((fen_axex/2), fen_axey/2 - 70), (250*tp, 50*tp), "Mode: " + diff_names[g_vars.difficulty], diff_select)

    txtVies = "Vies : " + lives_names[g_vars.livesCount]
    draw_button(((fen_axex/2), fen_axey/2), (250*tp, 50*tp), txtVies, lives_setting)

    draw_button((fen_axex/2, fen_axey/2 + 70), (250*tp, 50*tp), "Jouer", jouer)

    draw_text(tiny_font, "Clic-gauche pour détruire une case",
              (fen_axex/2, 410), lerp_vector(bckg, dark_bckg, tp), bckg)
    draw_text(tiny_font, "Clic-droit pour poser un drapeau",
              (fen_axex/2, 430), lerp_vector(bckg, dark_bckg, tp), bckg)
    draw_text(tiny_font, "Le nombre sur une case = le nombre de mines qui l'entoure",
              (fen_axex/2, 450), lerp_vector(bckg, dark_bckg, tp), bckg)
    draw_text(tiny_font, "Bonne chance !", (fen_axex/2, 480),
              lerp_vector(bckg, dark_bckg, tp), bckg)

# SCENE 2 - Fonction qui dessine le jeu
def game():
    fen.fill(bckg)
    tp = g_vars.t_prog

    # TIMER (avec chiffres formatés en XX:XX) --------------
    txt = f"{str(int(g_vars.timer//60)).zfill(2)}:{str(int(g_vars.timer%60)).zfill(2)}"
    draw_text(ui_font, txt, (450, 20), lerp_vector(bckg, dark_bckg, tp), bckg)

    # CASES RESTANTES (partie centrale de l'interface) --------------
    draw_counter()

    # VIES (si activées) ------------------
    if g_vars.livesCount > 0:
        for i in range(3):
            spr = "Graphics/heart_filled.png"
            if g_vars.lives < i + 1:
                spr = "Graphics/heart_empty.png"
            draw_sprite((25 + 40*i, 23), spr, round(g_vars.t_prog * 255))

    # LES CASES ------------------
    for i in range(g_vars.size*g_vars.size):
        x = i % g_vars.size
        y = i // g_vars.size
        s = clamp(g_vars.scene_time - (x + y)*0.05, 0, 0.2)*5
        draw_case(get_case_pos(x, y), (round(15*s), round(15*s)), x, y)

    # ANIMATION DE LA COLLECTE PROGRESSIVE DES CASES
    # On execute cette section toutes les 0.05 secondes
    if g_vars.scene_time % 0.05 < g_vars.prevScene_time % 0.05:
        if g_vars.animBacklog_cases != []:  # Si la liste des cases à collecter n'est pas vide
            pos = g_vars.animBacklog_cases[0]
            # on lance l'animation (se déclenche si center_anim != -1)
            g_vars.map[pos[0]][pos[1]].center_anim = 0
            g_vars.current_cases += 1
            g_vars.animBacklog_cases.pop(0)
            if game_collect.get_num_channels() == 0:  # si le son n'est pas en cours de lecture
                game_collect.play()

            if g_vars.current_cases == g_vars.required_cases:  # Si on a collecté toutes les cases, victoire !
                create_shockwave(get_case_pos(pos[0], pos[1]), green, 1, 500, 5, 15)
                create_shockwave(get_case_pos(pos[0], pos[1]), green, 1, 1000, 20, 15)
                g_vars.shake += 1
                g_vars.game_state = 1
                game_victory.play()
        else:
            game_collect.stop()

    # ANIMATION DES ONDES DE CHOC
    for s in shockwaves:
        if s.lifetime > 0:
            s.lifetime -= g_vars.deltaTime
            s.size += s.speed * g_vars.deltaTime
            draw_rect(s.pos, [s.size] * 2, s.color, max(round(s.width * clamp(s.lifetime/s.ogLifetime, 0, 10)), 1))
        else:  # si l'onde de choc a dépassé son espérance de vie, on la supprime
            shockwaves.remove(s)

    if g_vars.shake > 0:  # mise à jour du screen shake
        g_vars.shake = max(g_vars.shake - g_vars.deltaTime * 4, 0)

    # Bouton (on l'adapte selon le contexte)
    if g_vars.game_state == 0:
        draw_button((fen_axex/2, 485), (140*tp, 40*tp), "Abandonner", back)
    else:
        draw_button((fen_axex/2, 485), (140*tp, 40*tp), "Retour", back)

# ACTIONS DES BOUTONS ---------

# Action du bouton difficulté
def diff_select():
    g_vars.difficulty = (g_vars.difficulty + 1) % len(diff_names)

    if g_vars.difficulty == 0:
        snd_down.play()
    else:
        snd_up.play()

# Action du bouton vies
def lives_setting():
    g_vars.livesCount = (g_vars.livesCount + 1) % len(lives_names)

    if g_vars.livesCount == 0:
        snd_down.play()
    else:
        snd_up.play()

# Action du bouton jouer (lance la scène de jeu puis initialise toutes les variables qu'il faut)
def jouer():
    change_scene(0.5, 2, g_vars)
    snd_button.play()

    g_vars.size = g_vars.diff_size[g_vars.difficulty]
    g_vars.lives = g_vars.livesCount
    g_vars.map = gen_monde.generation_matrice_bombe(g_vars)
    g_vars.firstMove = True
    g_vars.timer = 0
    g_vars.current_cases = 0
    g_vars.game_state = 0

# Action du bouton retour/abandonner de la scène de jeu
def back():
    g_vars.animBacklog_cases = []
    change_scene(0.5, 1, g_vars)
    snd_back.play()

# FONCTIONS QUI DESSINENT L'INTERFACE ---------

# Fonction qui dessine un bouton avec lequel on peut interagir
def draw_button(pos, size, title, func):
    global g_vars
    if g_vars.mouse_pos[0] > (pos[0] - size[0]/2) and g_vars.mouse_pos[0] < (pos[0] + size[0]/2) and g_vars.mouse_pos[1] > (pos[1] - size[1]/2) and g_vars.mouse_pos[1] < (pos[1] + size[1]/2) and not g_vars.transitioning:  # si la souris survole le bouton
        draw_rect((pos[0] - 5, pos[1] + 5), size, dark_orange)  # on dessine l'ombre
        g_vars.hover = True
        if not g_vars.prevHover:
            snd_hover.play()

        if g_vars.lmouse_click:  # et on permet le clic
            func()
    draw_rect(pos, size, orange)
    if not g_vars.transitioning:  # on cache le texte quand le jeu est en transition d'une scène à l'autre
        draw_text(bt_font, title, pos, bckg, orange)


# nous donne les coordonnées sur l'écran des cases à partir de leur position x/y
def get_case_pos(x, y):
    shake = (round(uniform(-g_vars.shake, g_vars.shake)),
             round(uniform(-g_vars.shake, g_vars.shake)))
    return (fen_axex/2 + round(20 * (-g_vars.size/2 + x + 0.5)) + shake[0], fen_axey/2 + round(20 * (-g_vars.size/2 + y + 0.5)) + shake[1])

# Fonction qui dessine les cases du jeu
def draw_case(pos, size, x, y):
    global g_vars
    case = g_vars.map[x][y]  # simplifie les écritures

    # si la souris survole la case ET la case n'est pas découverte ET le jeu est toujours en cours et non en transition/fini, alors on peut interagir avec
    if g_vars.mouse_pos[0] > (pos[0] - size[0]/2) and g_vars.mouse_pos[0] < (pos[0] + size[0]/2) and g_vars.mouse_pos[1] > (pos[1] - size[1]/2) and g_vars.mouse_pos[1] < (pos[1] + size[1]/2) and not case.uncovered and g_vars.game_state == 0 and not g_vars.transitioning:
        draw_rect(pos, (size[0] + 4, size[1] + 4), dark_orange, 3)  # on dessine les contours
        g_vars.hover = True
        if not g_vars.prevHover:
            game_hover.play()

        if g_vars.lmouse_click:
            # si c'est la première case sur laquelle on clique, alors on supprime la mine en dessous (si il y en a une) et on calcul le nombre de voisin de toutes les cases du terrain
            if g_vars.firstMove:
                g_vars.firstMove = False
                for i in range(9):
                    if pointValide(g_vars.map, ((x-1) + i%3, (y-1) + i//3)):
                        if g_vars.map[(x-1) + i%3][(y-1) + i//3].mine:
                            g_vars.map[(x-1) + i%3][(y-1) + i//3].mine = False
                            g_vars.required_cases += 1
                voisins.voisin_matrice(g_vars.map)
            if test_case(g_vars.map, x, y):  # on teste la case, retourne True si c'est une mine
                if g_vars.lives > 0:  # si on a des vies, on les perd
                    g_vars.lives -= 1
                    create_shockwave(pos, nice_red, 0.5, 500, 5, 15)
                    g_vars.shake += 1
                    game_damage.play()
                else:  # sinon, perdu !
                    g_vars.game_state = -1
                    create_shockwave(pos, nice_red, 1, 500, 5, 15)
                    create_shockwave(pos, nice_red, 1, 1000, 20, 15)
                    g_vars.shake += 4
                    game_defeat.play()
            create_shockwave(pos, dark_orange, 0.2, 200, 1, 15)  # animation du clic
        if g_vars.rmouse_click:  # on rajoute ou enlève le drapeau avec un clic droit
            if case.flag == 0:
                case.flag = 1
                game_flag.play()
            else:
                case.flag = 0
                game_unflag.play()

    # si l'animation de la collection de la case est commencée ou si le jeu est terminé, alors on dessine l'intérieur de la case
    if case.center_anim != -1 or g_vars.game_state != 0:
        if case.mine:  # on dessine le p'tit icône mine
            draw_sprite(pos, "Graphics/mine.png")
        elif case.voisins > 0:  # ou le nombre de voisins, mais pas les deux
            draw_text(cases_font, str(case.voisins), pos, nice_red, bckg)
        draw_rect(pos, size, orange, 2)  # le contour
        # l'animation du centre de la case qui s'en va, remplir notre barre de façon satisfaisante
        if case.center_anim < 0.2 and case.center_anim != -1:
            draw_rect(lerp_vector(pos, (g_vars.progressbar_x, 40), case.center_anim * 5), (8, 8), dark_bckg)
            case.center_anim += g_vars.deltaTime
    else:  # sinon on dessine juste un carré
        draw_rect(pos, size, orange)

    # si on a posé un drapeau ET que la case n'est pas découverte ET que le jeu est toujours en cours, alors on dessine (et anime !) le petit drapeau
    if case.flag > 0 and case.uncovered == False and g_vars.game_state == 0:
        if case.flag < 4 and g_vars.scene_time % 0.1 < g_vars.prevScene_time % 0.1:
            case.flag += 1  # on avance l'animation d'une image 0.1s
        draw_sprite(pos, "Graphics/flag_spr/flag_" + str(case.flag - 1) + ".png")

# Fonction pour écrire du texte
def draw_text(font, str, pos, color, bckg_color):
    text = font.render(str, True, color, bckg_color)
    textRect = text.get_rect()
    textRect.center = pos
    fen.blit(text, textRect)

# Fonction pour dessiner le compteur et la barre  qui comptent les cases en jeu
def draw_counter():
    if g_vars.firstMove == False:
        # On met le même nombre de chiffres à droite et à gauche pour que ce soit joli
        txt = f"{str(g_vars.current_cases).zfill(g_vars.digitsCount_cases)}/{g_vars.required_cases}"
        color = lerp_vector(bckg, dark_bckg, g_vars.t_prog)
        text = ui_font.render(txt, True, color, bckg)
        textRect = text.get_rect()
        textRect.center = (fen_axex/2, 20)
        fen.blit(text, textRect)

        # La barre de progression (on dessine le contour puis l'intérieur)
        draw_rect((fen_axex/2, 40), (textRect.width, 10), color, 2)
        pygame.draw.rect(fen, color, pygame.Rect(fen_axex/2 - textRect.width/2, 35,
                         round((g_vars.current_cases/g_vars.required_cases) * textRect.width), 10))
        g_vars.progressbar_x = fen_axex/2 - textRect.width/2 + g_vars.current_cases/g_vars.required_cases * textRect.width

# Fonction pour dessiner des images
def draw_sprite(pos, sprite, alpha=255):
    spr = pygame.image.load(sprite).convert_alpha()
    if alpha != 255:
        spr.set_alpha(alpha)
    sprRect = spr.get_rect()
    sprRect.center = pos
    fen.blit(spr, sprRect)
    # pygame.display.flip()

# draw ... rect-angle (plein (si outline = 0) ou avec contour !)
def draw_rect(pos, size, color, outline=0):
    if outline == 0:
        pygame.draw.rect(fen, color, pygame.Rect(
            pos[0] - size[0]/2, pos[1] - size[1]/2, size[0], size[1]))
    else:
        pygame.draw.rect(fen, color, pygame.Rect(
            pos[0] - size[0]/2, pos[1] - size[1]/2, size[0], size[1]), outline)

# On crée une instance d'une onde de choc (s'exécute une fois pas onde de choc !)
def create_shockwave(pos, color, lifetime, speed, width, size=1):
    s = shockwave()
    s.lifetime = lifetime
    s.ogLifetime = lifetime
    s.pos = pos
    s.color = color
    s.width = width
    s.speed = speed
    s.size = size
    shockwaves.append(s)

# FONCTIONS QUI CHANGENT LA SCENE AFFICHÉE A L'ÉCRAN --------

# on exécute d'abord celle-là, qui changera la scène dans "cooldown" secondes (avec la fonction en dessous)
def change_scene(cooldown, scene, game_vars):
    game_vars.transitioning = True
    game_vars.t_prog = 1
    t = th.Timer(cooldown, change_scene_execute, args=[scene, game_vars])
    t.start()


def change_scene_execute(scene, game_vars):
    if game_vars.state == 0 and scene == 1:
        snd_intro.play()
    game_vars.state = scene
    game_vars.t_prog = 0
    game_vars.transitioning = False
    game_vars.scene_time = 0

# FONCTIONS MATHS ASSEZ PRATIQUES ---------

# interpolation linéaire avec une seule valeur
def lerp(b, a, c):
    return (c*a)+((1-c)*b)

# .. pareil mais avec un vecteur
def lerp_vector(b, a, c):
    return sum_vector(prod_vector([c] * len(a), a), prod_vector([1-c] * len(a), b))

# encadrer une valeur
def clamp(val, mini, maxi):
    return min(max(val, mini), maxi)

# somme de deux vecteurs
def sum_vector(a, b):
    l = []
    for i in range(len(a)):
        l.append(a[i] + b[i])
    return l

# produit de deux vecteurs (pas un produit vectoriel !!)
def prod_vector(a, b):
    l = []
    for i in range(len(a)):
        l.append(a[i]*b[i])
    return l

# REMPLISSAGE RECURSIF DES CASES -----------------
def pointValide(grille, point):
    """
    Un point est jugé valide si il est dans les limites de notre tableau
    Input

    - La matrice
    - Les coordonnées du point de départ de la diffusion
    
    Return :
    Cette fonction renvoie True ou False selon la validité du point 
    """
    return point[0] >= 0 and point[1] >= 0 and point[0] < len(grille) and point[1] < len(grille)


def remplissageDiffusionRecursif(grille, test_grille, x, y):
    """
    Le but de cette fonction est de dévoiler les cases qui n'ont pas de mines aux alentours

    Input :
    - Les voisins sous forme de matrice
    - Les coordonnées du point de départ de la diffusion

    Return :
    Cette fonction ne renvoie rien, elle change juste l'état de cases dont les voisins sont nuls (covered à uncovered) 
    """
    if grille[x][y].mine == False and grille[x][y].uncovered == False:
        g_vars.animBacklog_cases.append((x, y))
        grille[x][y].uncovered = True

    if grille[x][y].voisins == 0 and test_grille[x][y] == False:
        test_grille[x][y] = True
        # for i in range(1, 8, 2):
        for i in range(9):
            pos = (x - 1 + i % 3, y - 1 + i//3)
            if pointValide(grille, pos):
                remplissageDiffusionRecursif(
                    grille, test_grille, pos[0], pos[1])


def test_case(grille, x, y):

    test_grille = [[False for i in range(len(grille))]
                   for i in range(len(grille))]
    # Si on se trouve sur une mine
    if grille[x][y].mine == True:
        grille[x][y].uncovered = True
        # on skip l'animation du carré qui va vers le haut vu que la case ne s'ajoute pas au compteur
        grille[x][y].center_anim = 0.2
        return True
    else:
        # Si on ne se trouve pas sur une mine on va regarder le nombre de voisins que possède la mine
        # Si elle a des mines aux alentours on ne dévloile que le nombre de mines aux alentours
        remplissageDiffusionRecursif(grille, test_grille, x, y)
        game_empty.play()
        return False
