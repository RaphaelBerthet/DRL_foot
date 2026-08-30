import numpy as np
from .parametres import LIMITE_NORD_CAGE, LIMITE_SUD_CAGE, LONGUEUR, LARGEUR, LIMITE_EST_TERRAIN, VITESSE_JOUEUR, LIMITE_NORD_TERRAIN, LIMITE_OUEST_TERRAIN, LIMITE_SUD_TERRAIN

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
    state[7] = (joueur.x - joueur.rayon - LIMITE_OUEST_TERRAIN) / LONGUEUR
    state[8] = (LIMITE_EST_TERRAIN - joueur.x - joueur.rayon) / LONGUEUR
    state[9] = (joueur.y - joueur.rayon - LIMITE_NORD_TERRAIN) / LARGEUR
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

def build_state_foot_2v2(taille_state, app, joueur, joueur_allie, joueur_adverse_a, joueur_adverse_b):
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
    state[7] = (joueur.x - joueur.rayon - LIMITE_OUEST_TERRAIN) / LONGUEUR
    state[8] = (LIMITE_EST_TERRAIN - joueur.x - joueur.rayon) / LONGUEUR
    state[9] = (joueur.y - joueur.rayon - LIMITE_NORD_TERRAIN) / LARGEUR
    state[10] = (LIMITE_SUD_TERRAIN - joueur.y - joueur.rayon) / LARGEUR
    state[11] = (joueur_adverse_a.x - joueur.x) / LONGUEUR
    state[12] = (joueur_adverse_a.y - joueur.y) / LARGEUR
    state[13] = (app.balle.x - joueur_adverse_a.x) / LONGUEUR
    state[14] = (app.balle.y - joueur_adverse_a.y) / LARGEUR
    state[15] = (joueur_adverse_b.x - joueur.x) / LONGUEUR
    state[16] = (joueur_adverse_b.y - joueur.y) / LARGEUR
    state[17] = (app.balle.x - joueur_adverse_b.x) / LONGUEUR
    state[18] = (app.balle.y - joueur_adverse_b.y) / LARGEUR
    state[19] = (joueur_allie.x - joueur.x) / LONGUEUR
    state[20] = (joueur_allie.y - joueur.y) / LARGEUR
    state[21] = (app.balle.x - joueur_allie.x) / LONGUEUR
    state[22] = (app.balle.y - joueur_allie.y) / LARGEUR
    if app.balle.possession == joueur.nom:
        state[23] = 1
    elif app.balle.possession == joueur_adverse_a.nom:
        state[23] = -1
    else:
        state[23] = 0

    return state