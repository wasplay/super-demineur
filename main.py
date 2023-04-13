import pygame
import interface

# VARIABLES POUR GARDER LA NOTION DU TEMPS
t = 0
# deltaTime = 0  --- décalé dans Game_vars
getTicksLastFrame = 0

# Variables d'état du jeu

class Game_vars:
    # VARIABLES GENERALES
    state = 0  # quel menu est allumé ?
    transitioning = False  # est-ce qu'on passe à un autre menu ?
    t_prog = 0  # progrès de la transition (0 -> 1)
    scene_time = 0  # combien de temps depuis le dernier changement de scène ?
    # combien de temps depuis le dernier changement de scène ? (avec 1ips de retard)
    prevScene_time = 0
    deltaTime = 0  # temps écoulé depuis la dernière image

    # VARIABLES D'ETAT DU JEU
    difficulty = 1  # ...
    size = 20  # taille du terrain
    diff_size = [6, 10, 15, 20]  # taille du terrain selon la difficulté
    map = []  # le terrain du jeu
    timer = 0  # le chrono
    required_cases = 0  # cases requises pour gagner
    current_cases = 0  # cases obtenues pour le moment
    digitsCount_cases = 0  # nombres de chiffres de required_cases
    game_state = 0  # -1 = défaite, 1 = victoire, 0 = partie en cours
    lives = 0  # il me semble que ça veut dire vie en anglais
    livesCount = 0  # combien de vies pour commencer ? (0 par défaut)
    firstMove = True  # passe de False à True lors de la première action du joueur

    # TRUCS D'ANIMATION
    animBacklog_cases = []  # backlog des cases à collecter
    progressbar_x = 0  # position de l'extrémité de la barre de progression
    shake = 0  # quantité de screen shake

    # INPUTS
    mouse_pos = (0, 0)  # position de jerry
    lmouse_click = False  # clic gauche ?
    rmouse_click = False  # clic droit ? (oh un drapeau !!)
    hover = False  # la souris est-elle sur un bouton ?
    prevHover = False  # la souris était-elle sur un bouton la dernière image ?


# on crée une instance de cette énorme classe pour qu'elle soit partagée entre les scripts facilement
game_vars = Game_vars()

# les différents menus
scenes = [interface.null_scene, interface.menu, interface.game]

# Boucle principale

def main_logic():
    global getTicksLastFrame, t

    # POUR GARDER LA NOTION DU TEMPS
    t = pygame.time.get_ticks()  # nombre de ms depuis le lancement du jeu
    game_vars.deltaTime = (t - getTicksLastFrame) / 1000.0
    getTicksLastFrame = t
    game_vars.scene_time += game_vars.deltaTime

    # on met à jour t_prog pour qu'il s'approche lentement de sa valeur cible (0 ou 1), l'interpolation linéaire c'est très pratique
    speed = game_vars.deltaTime * 8
    if game_vars.transitioning:
        game_vars.t_prog = interface.lerp(game_vars.t_prog, 0, speed)
    else:
        game_vars.t_prog = interface.lerp(game_vars.t_prog, 1, speed)

    # on récupère les inputs avant d'exécuter le script de la scène allumée
    interface.inputs(game_vars)
    scenes[game_vars.state]()
    # si l'utilisateur a cliqué, on retire son clic pour qu'il ne soit pris en compte qu'une fois
    game_vars.lmouse_click = False
    game_vars.rmouse_click = False  # pareil pour le clic droit
    game_vars.prevHover = game_vars.hover

    # c'est comme ça que prevScene_time a un retard de 1ips pour pouvoir comparer l'évolution de la variable (et pouvoir faire des bouts de scripts qui s'exécutent toutes les X secondes par exemple)
    game_vars.prevScene_time = game_vars.scene_time
    # si on est dans la scène jeu ET que le joueur a joué ET que la partie n'est pas terminée, alors le chrono est en marche
    if game_vars.state == 2 and game_vars.firstMove == False and game_vars.game_state == 0:
        game_vars.timer += game_vars.deltaTime

    pygame.display.update()  # on met à jour l'écran


# on commence par transitionner de la scène vide (celle allumée par défaut) au menu
interface.change_scene(0.5, 1, game_vars)

while True:
    main_logic()  # c'est si simple vu d'ici
    # clock=pygame.time.Clock()
    # clock.tick(60) # nombre d'images par seconde
