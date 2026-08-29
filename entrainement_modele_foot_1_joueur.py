from packages.build_state import build_state_foot_1_joueur
from packages.entrainement_reseau_neurones import Reseau_neurones
from packages.parametres_reseau_neurones import N_STEP, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2, NB_ITERATIONS_1_PARTIE_FOOT_1_JOUEUR, TAILLE_STATE_FOOT_1J, NB_ACTIONS_POSSIBLES, NB_PARTIES, p_debut, p_fin
import random
import numpy as np
from foot_1_joueur import Foot_1_joueur
import math
from packages.parametres import VITESSE_JOUEUR, NB_EXECUTIONS_1_ACTION
from collections import deque

"""
etat (10): 
    (toutes les distances sont normalisées)
    distance a la balle selon x
    distance a la balle selon y
    vitesse balle selon x
    vitesse balle selon y
    distance balle cages EST selon x
    distance balle-cages selon y (0 si la balle est alignée)
    distance joueur aux 4 limites de terrain
action (9):
    "rien" : 9,
    "gauche" : 1,
    "droite" : 2, 
    "haut" : 3,
    "bas" : 4,
    "gauchehaut" : 5,
    "gauchebas" : 6,
    "droitehaut" : 7,
    "droitebas" : 8
"""

def jouer_une_partie(reseau_neurones, p, partie):
    """Joue une partie complète et alimente le réseau en samples."""
    ## initialisation de la partie
    app = Foot_1_joueur()
    buffer_local = deque()  # stocke (state1, action, reward) en attente

    iteration = 0
    partie_en_cours = True
    but_marque = False
    while partie_en_cours and not but_marque:
        iteration += 1
        if app.joueur1.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
            state1 = build_state_foot_1_joueur(TAILLE_STATE_FOOT_1J, app)
            action = choisir_action(reseau_neurones, state1, p)
            reward, but_marque = executer_action(action, app, partie)
            if iteration >= NB_ITERATIONS_1_PARTIE_FOOT_1_JOUEUR:
                partie_en_cours = False
            state2 = build_state_foot_1_joueur(TAILLE_STATE_FOOT_1J, app)

            buffer_local.append((state1, action, reward, state2, but_marque))

            # dès qu'on a accumulé n transitions, on peut calculer un sample n-step
            if len(buffer_local) >= N_STEP:
                _emettre_sample_n_step(buffer_local, reseau_neurones, N_STEP)
                buffer_local.popleft()

            reseau_neurones.entrainement_reseau(partie)
        else:
            executer_action(None, app, partie)
        if but_marque:
            print(f'partie {partie} : but')

    # à la fin de la partie, vider les transitions restantes (n-step raccourci)
    '''while buffer_local:
        _emettre_sample_n_step(buffer_local, reseau_neurones, len(buffer_local))
        buffer_local.popleft()'''  # on perd les derniers instants pour pas s'embeter dans les calculs


def _emettre_sample_n_step(buffer_local, reseau_neurones, n):
    from packages.parametres_reseau_neurones import gamma
    state1, action, _, _, _ = buffer_local[0]
    G = 0.0
    for i in range(n):
        _, _, r_i, _, _ = buffer_local[i]
        G += (gamma ** i) * r_i
    # état à n pas plus loin (pour le bootstrap), et si la séquence s'est terminée avant n pas
    _, _, _, state_n, terminal_n = buffer_local[min(n, len(buffer_local)) - 1]
    sample = np.concatenate([state1, state_n, [action, G, terminal_n]])
    reseau_neurones.ajout_sample(sample)


def choisir_action(reseau_neurones, state, p):
    if random.random() <= p:
        return random.randint(1, NB_ACTIONS_POSSIBLES)
    return np.argmax(reseau_neurones.calcul_couche_sortie(state)) + 1


def executer_action(action, app, partie):
    joueur1x, joueur1y = app.joueur1.x, app.joueur1.y

    if app.joueur1.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
        app.joueur1.action = action
        app.joueur1.convert_action_vitesse()

    app.balle.verif_collisions([app.joueur1])

    app.balle.deplacement()
    app.joueur1.deplacement(app.balle)

    but_marque = False
    score = app.balle.actu_score1(app.scorej1)
    if score != app.scorej1:
        reward = 10
        but_marque = True
    else:
        reward = -0.001
        if app.balle.balle_tiree:
            reward = 0.1 * app.balle.vx / (VITESSE_JOUEUR * 2)

        distance_J1_balle_sans_bouger_joueur = math.sqrt((app.balle.x - joueur1x) ** 2 + (app.balle.y - joueur1y) ** 2)
        distance_J1_balle_bouger_joueur = math.sqrt((app.balle.x - app.joueur1.x) ** 2 + (app.balle.y - app.joueur1.y) ** 2)
        ## on recompense si ca permet de reduire la distance qu'il y aurait eu sans avoir bougé
        reward += 0.001 * (distance_J1_balle_sans_bouger_joueur - distance_J1_balle_bouger_joueur) / VITESSE_JOUEUR

    return reward, but_marque

def entrainer(nb_parties=NB_PARTIES):
    reseau_neurones = Reseau_neurones("reseau_neurones_foot_1_joueur.npz", TAILLE_STATE_FOOT_1J, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    for partie in range(nb_parties):
        p = p_debut - (p_debut - p_fin) * partie / nb_parties
        if partie % 100 == 0:
            print(f"progression : {partie * 100 / nb_parties} %")
        jouer_une_partie(reseau_neurones, p, partie)
    return reseau_neurones


if __name__ == "__main__":
    entrainer()