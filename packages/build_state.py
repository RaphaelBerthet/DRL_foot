import numpy as np
from .parametres import LIMITE_NORD_CAGE, LIMITE_SUD_CAGE, LONGUEUR, LARGEUR, LIMITE_EST_TERRAIN, VITESSE_JOUEUR, LIMITE_NORD_TERRAIN, LIMITE_OUEST_TERRAIN, LIMITE_SUD_TERRAIN
import math
from math import cos, sin, sqrt

def build_state_foot_1_joueur(taille_state, app):
    state = np.zeros(taille_state, dtype=np.float32)
    state[0] = (app.balle.x - app.joueur1.x) / LONGUEUR
    state[1] = (app.balle.y - app.joueur1.y) / LARGEUR
    state[2] = app.balle.vx / (VITESSE_JOUEUR * 2)
    state[3] = app.balle.vy / (VITESSE_JOUEUR * 2)
    state[4] = (LIMITE_EST_TERRAIN - app.balle.x - app.balle.rayon) / LONGUEUR
    if app.balle.y - 2 * app.balle.rayon < LIMITE_NORD_CAGE:
        state[5] = (LIMITE_NORD_CAGE - (app.balle.y - 2 * app.balle.rayon)) / (LARGEUR / 2)  # > 0
    elif LIMITE_SUD_CAGE < app.balle.y + 2 * app.balle.rayon:
        state[5] = (LIMITE_SUD_CAGE - (app.balle.y + 2 * app.balle.rayon)) / (LARGEUR / 2)  # < 0
    else:
        state[5] = 0
    state[6] = (app.joueur1.x - app.joueur1.rayon - LIMITE_OUEST_TERRAIN) / LONGUEUR
    state[7] = (LIMITE_EST_TERRAIN - app.joueur1.x - app.joueur1.rayon) / LONGUEUR
    state[8] = (app.joueur1.y - app.joueur1.rayon - LIMITE_NORD_TERRAIN) / LARGEUR
    state[9] = (LIMITE_SUD_TERRAIN - app.joueur1.y - app.joueur1.rayon) / LARGEUR

    return state

def build_state_foot_1v1(taille_state, app, joueur, joueur_adverse):
    state = np.zeros(taille_state, dtype=np.float32)
    state[0] = (app.balle.x - joueur.x) / LONGUEUR
    state[1] = (app.balle.y - joueur.y) / LARGEUR
    state[2] = app.balle.vx / (VITESSE_JOUEUR * 2)
    state[3] = app.balle.vy / (VITESSE_JOUEUR * 2)
    state[4] = (app.balle.x + 2 * app.balle.rayon - LIMITE_OUEST_TERRAIN) / LONGUEUR
    state[5] = (LIMITE_EST_TERRAIN - app.balle.x - 2 * app.balle.rayon) / LONGUEUR
    if app.balle.y - 2 * app.balle.rayon < LIMITE_NORD_CAGE:
        state[6] = (LIMITE_NORD_CAGE - (app.balle.y - 2 * app.balle.rayon)) / (LARGEUR / 2)  # > 0
    elif LIMITE_SUD_CAGE < app.balle.y + 2 * app.balle.rayon:
        state[6] = (LIMITE_SUD_CAGE - (app.balle.y + 2 * app.balle.rayon)) / (LARGEUR / 2)  # < 0
    else:
        state[6] = 0
    state[7] = (app.balle.x - app.balle.rayon - LIMITE_OUEST_TERRAIN) / LONGUEUR
    state[8] = (LIMITE_EST_TERRAIN - app.balle.x - app.balle.rayon) / LONGUEUR
    state[9] = (app.balle.y - app.balle.rayon - LIMITE_NORD_TERRAIN) / LARGEUR
    state[10] = (LIMITE_SUD_TERRAIN - joueur.y - joueur.rayon) / LARGEUR
    state[11] = (joueur_adverse.x - joueur.x) / LONGUEUR
    state[12] = (joueur_adverse.y - joueur.y) / LARGEUR
    state[13] = (app.balle.x - joueur_adverse.x) / LONGUEUR
    state[14] = (app.balle.y - joueur_adverse.y) / LARGEUR
    if app.balle.possession == joueur.nom:
        state[15] = 1
    elif app.balle.possession == joueur_adverse.nom:
        state[15] = -1
    else:
        state[15] = 0

    return state

def build_state_foot_2v2_J1(taille_state, app, balle, J1p, J1e, J2p, J2e, Tp, Te):
    '''l'indice p designe le joueur qui peut atteindre la balle plus rapidement (proche), e pour eloigné'''
    state = np.zeros(taille_state, dtype=np.float32)

    rpB = math.sqrt((balle.x - J1p.x) ** 2 + (balle.y - J1p.y) ** 2) / LONGUEUR
    tetapB = math.atan2(balle.y - J1p.y, balle.x - J1p.x)
    state[0], state[1], state[2] = rpB, cos(tetapB), sin(tetapB)

    reB = math.sqrt((balle.x - J1e.x) ** 2 + (balle.y - J1e.y) ** 2) / LONGUEUR
    tetaeB = math.atan2(balle.y - J1e.y, balle.x - J1e.x)
    state[3], state[4], state[5] = reB, cos(tetaeB), sin(tetaeB)

    rpaB = math.sqrt((balle.x - J2p.x) ** 2 + (balle.y - J2p.y) ** 2) / LONGUEUR
    tetapaB = math.atan2(balle.y - J2p.y, balle.x - J2p.x)
    state[6], state[7], state[8] = rpaB, cos(tetapaB), sin(tetapaB)

    reaB = math.sqrt((balle.x - J2e.x) ** 2 + (balle.y - J2e.y) ** 2) / LONGUEUR
    tetaeaB = math.atan2(balle.y - J2e.y, balle.x - J2e.x)
    state[9], state[10], state[11] = reaB, cos(tetaeaB), sin(tetaeaB)

    vB = math.sqrt(balle.vx ** 2 + balle.vy ** 2) / VITESSE_JOUEUR
    tetavB = math.atan2(balle.vy, balle.vx)
    state[12], state[13], state[14] = vB, cos(tetavB), sin(tetavB)

    rep = math.sqrt((J1p.x - J1e.x) ** 2 + (J1p.y - J1e.y) ** 2) / LONGUEUR
    tetaep = math.atan2(J1p.y - J1e.y, J1p.x - J1e.x)
    state[15], state[16], state[17] = rep, cos(tetaep), sin(tetaep)

    state[18], state[19], state[20], state[21] = (LIMITE_EST_TERRAIN - balle.x) / LONGUEUR, (LIMITE_OUEST_TERRAIN - balle.x) / LONGUEUR, (LIMITE_NORD_TERRAIN - balle.y) / LARGEUR, (LIMITE_SUD_TERRAIN - balle.y) / LARGEUR
    state[22] = (balle.y - LARGEUR / 2) / LARGEUR
    if app.balle.possession == J1p.nom:
        state[23] = 1
    elif app.balle.possession == J2p.nom:
        state[23] = -1
    else:
        state[23] = 0
    state[24] = (Te - Tp) / 100

    return state

def build_state_foot_2v2_J2(taille_state, app, balle, J2p, J2e, J1p, J1e, Tp, Te):
    '''l'indice p designe le joueur qui peut atteindre la balle plus rapidement (proche), e pour eloigné'''
    state = np.zeros(taille_state, dtype=np.float32)
    rpB = math.sqrt((balle.x - J2p.x) ** 2 + (balle.y - J2p.y) ** 2) / LONGUEUR
    tetapB = math.atan2(balle.y - J2p.y, balle.x - J2p.x) + math.pi
    state[0], state[1], state[2] = rpB, cos(tetapB), sin(tetapB)

    reB = math.sqrt((balle.x - J2e.x) ** 2 + (balle.y - J2e.y) ** 2) / LONGUEUR
    tetaeB = math.atan2(balle.y - J2e.y, balle.x - J2e.x) + math.pi
    state[3], state[4], state[5] = reB, cos(tetaeB), sin(tetaeB)

    rpaB = math.sqrt((balle.x - J1p.x) ** 2 + (balle.y - J1p.y) ** 2) / LONGUEUR
    tetapaB = math.atan2(balle.y - J1p.y, balle.x - J1p.x) + math.pi
    state[6], state[7], state[8] = rpaB, cos(tetapaB), sin(tetapaB)

    reaB = math.sqrt((balle.x - J1e.x) ** 2 + (balle.y - J1e.y) ** 2) / LONGUEUR
    tetaeaB = math.atan2(balle.y - J1e.y, balle.x - J1e.x) + math.pi
    state[9], state[10], state[11] = reaB, cos(tetaeaB), sin(tetaeaB)

    vB = math.sqrt(balle.vx ** 2 + balle.vy ** 2) / VITESSE_JOUEUR
    tetavB = math.atan2(balle.vy, balle.vx) + math.pi
    state[12], state[13], state[14] = vB, cos(tetavB), sin(tetavB)

    rep = math.sqrt((J2p.x - J2e.x) ** 2 + (J2p.y - J2e.y) ** 2) / LONGUEUR
    tetaep = math.atan2(J2p.y - J2e.y, J2p.x - J2e.x) + math.pi
    state[15], state[16], state[17] = rep, cos(tetaep), sin(tetaep)

    state[18], state[19], state[20], state[21] = -(LIMITE_OUEST_TERRAIN - balle.x) / LONGUEUR, -(LIMITE_EST_TERRAIN - balle.x) / LONGUEUR, -(LIMITE_SUD_TERRAIN - balle.y) / LARGEUR, -(LIMITE_NORD_TERRAIN - balle.y) / LARGEUR
    state[22] = - (balle.y - LARGEUR / 2) / LARGEUR
    if app.balle.possession == J2p.nom:
        state[23] = 1
    elif app.balle.possession == J1p.nom:
        state[23] = -1
    else:
        state[23] = 0
    state[24] = (Te - Tp) / 100

    return state

'''def build_state_foot_2v2(angle_vision, app, joueur, joueur_allie, joueur_adverse_a, joueur_adverse_b):
    distance_joueur_allie = math.sqrt((joueur_allie.x - joueur.x) ** 2 + (joueur_allie.y - joueur.y) ** 2)
    distance_adversaire_a = math.sqrt((joueur_adverse_a.x - joueur.x) ** 2 + (joueur_adverse_a.y - joueur.y) ** 2)
    distance_adversaire_b = math.sqrt((joueur_adverse_b.x - joueur.x) ** 2 + (joueur_adverse_b.y - joueur.y) ** 2)
    distance_balle = math.sqrt((app.balle.x - joueur.x) ** 2 + (app.balle.y - joueur.y) ** 2)
    if joueur_allie.y - joueur.y >= 0:
        angle_joueur_allie = math.acos((joueur_allie.x - joueur.x) / distance_joueur_allie)
    else:
        angle_joueur_allie = math.acos((joueur_allie.x - joueur.x) / distance_joueur_allie) + math.pi
    if joueur_adverse_a.y - joueur.y >= 0:
        angle_joueur_adverse_a = math.acos((joueur_adverse_a.x - joueur.x) / distance_adversaire_a)
    else:
        angle_joueur_adverse_a = math.acos((joueur_adverse_a.x - joueur.x) / distance_adversaire_a) + math.pi
    if joueur_adverse_b.y - joueur.y >= 0:
        angle_joueur_adverse_b = math.acos((joueur_adverse_b.x - joueur.x) / distance_adversaire_b)
    else:
        angle_joueur_adverse_b = math.acos((joueur_adverse_b.x - joueur.x) / distance_adversaire_b) + math.pi
    if app.balle.y - joueur.y >= 0:
        angle_balle = math.acos((app.balle.x - joueur.x) / distance_balle)
    else:
        angle_balle = math.acos((app.balle.x - joueur.x) / distance_balle) + math.pi

    state = np.zeros(4 * int(360 / angle_vision) + 5, dtype=np.float32)
    # on s'occupe d'abord de la balle
    if angle_joueur_adverse_b % angle_vision == angle_joueur_adverse_a % angle_vision:
        ## les 2 sont dans le meme cone du champs de vision du joueur
        if distance_adversaire_a < distance_adversaire_b:
            angle_joueur_adverse_b = 500  # cet angle ne sera pas traité car il est trop grand
        else:
            angle_joueur_adverse_a = 500
    for i in range(int(360 / angle_vision)):
        if i == angle_balle % angle_vision:
            valeur = distance_balle / LONGUEUR
        else:
            valeur = 0
        state[4 * i] = valeur
        if i == angle_joueur_allie % angle_vision:
            valeur = distance_joueur_allie / LONGUEUR
        else:
            valeur = 0
        state[4 * i + 1] = valeur
        if i == angle_joueur_adverse_a % angle_vision:
            valeur = distance_adversaire_a / LONGUEUR
        else:
            valeur = 0
        state[4 * i + 2] = valeur
        if i == angle_joueur_adverse_b % angle_vision:
            valeur = distance_adversaire_b / LONGUEUR
        else:
            valeur = 0
        state[4 * i + 3] = valeur
    # on ajoute les infos sur la vitesse de balle et sa position par rapport aux cages
    state[-5] = app.balle.vx
    state[-4] = app.balle.vy
    state[-3] = (LARGEUR / 2 - app.balle.y) / (LARGEUR / 2)
    state[-2] = (app.balle.x + 2 * app.balle.rayon - LIMITE_OUEST_TERRAIN) / LONGUEUR
    state[-1] = (LIMITE_EST_TERRAIN - app.balle.x - 2 * app.balle.rayon) / LONGUEUR

    return state'''