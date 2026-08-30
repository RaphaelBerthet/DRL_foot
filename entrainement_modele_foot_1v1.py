from packages.build_state import build_state_foot_1v1
from packages.entrainement_reseau_neurones import Reseau_neurones
from packages.parametres_reseau_neurones import N_STEP, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2, NB_ITERATIONS_1_PARTIE_FOOT_1V1, TAILLE_STATE_FOOT_1V1, NB_ACTIONS_POSSIBLES, NB_PARTIES, p_debut, p_fin
import random
import numpy as np
from foot_1v1 import Foot_1v1
import math
from packages.parametres import VITESSE_JOUEUR, NB_EXECUTIONS_1_ACTION
from collections import deque

"""
etat (16): 
    (toutes les distances sont normalisées)
    distance a la balle selon x
    distance a la balle selon y
    vitesse balle selon x
    vitesse balle selon y
    distance balle cages OUEST selon x
    distance balle cages EST selon x
    distance balle-cages selon y (0 si la balle est alignée)
    distance joueur aux 4 limites de terrain
    distance joueur adverse selon x et y
    distance joueur adverse-balle selon x et y
    possession balle (-1 si c'est l'adversaire, 0 si c'est personne, 1 si c'est le joueur)
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

def jouer_une_partie(reseau_neurones_J1, reseau_neurones_J2, p, partie):
    """Joue une partie complète et alimente le réseau en samples."""
    ## initialisation de la partie
    app = Foot_1v1()
    buffer_local_J1 = deque()  # stocke (state1, action, reward) en attente
    buffer_local_J2 = deque()  # stocke (state1, action, reward) en attente

    iteration = 0
    partie_en_cours = True
    while partie_en_cours:
        iteration += 1
        if app.joueur1.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
            state1_J1 = build_state_foot_1v1(TAILLE_STATE_FOOT_1V1, app, app.joueur1, app.joueur2)
            action_J1 = choisir_action(reseau_neurones_J1, state1_J1, p)
            state1_J2 = build_state_foot_1v1(TAILLE_STATE_FOOT_1V1, app, app.joueur2, app.joueur1)
            action_J2 = choisir_action(reseau_neurones_J2, state1_J2, p)
            reward_J1, reward_J2, but_marque, vainqueur = executer_action(action_J1, action_J2, app, partie)
            if iteration >= NB_ITERATIONS_1_PARTIE_FOOT_1V1:
                partie_en_cours = False
            if but_marque:
                partie_en_cours = False
            state2_J1 = build_state_foot_1v1(TAILLE_STATE_FOOT_1V1, app, app.joueur1, app.joueur2)
            state2_J2 = build_state_foot_1v1(TAILLE_STATE_FOOT_1V1, app, app.joueur2, app.joueur1)

            buffer_local_J1.append((state1_J1, action_J1, reward_J1, state2_J1, but_marque))
            buffer_local_J2.append((state1_J2, action_J2, reward_J2, state2_J2, but_marque))

            # dès qu'on a accumulé n transitions, on peut calculer un sample n-step
            if len(buffer_local_J1) >= N_STEP:
                _emettre_sample_n_step(buffer_local_J1, reseau_neurones_J1, N_STEP)
                buffer_local_J1.popleft()
                _emettre_sample_n_step(buffer_local_J2, reseau_neurones_J2, N_STEP)
                buffer_local_J2.popleft()

            reseau_neurones_J1.entrainement_reseau(partie)
            reseau_neurones_J2.entrainement_reseau(partie)
        else:
            executer_action(None, None, app, partie)
        if but_marque:
            print(f'partie {partie} : but {vainqueur}')

    # à la fin de la partie, vider les transitions restantes (n-step raccourci)
    '''while buffer_local:
        _emettre_sample_n_step(buffer_local, reseau_neurones, len(buffer_local))
        buffer_local.popleft()'''  # on perd les derniers instants pour pas s'embeter dans les calculs

    return vainqueur


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


def executer_action(action_J1, action_J2, app, partie):
    joueur1x, joueur1y = app.joueur1.x, app.joueur1.y
    joueur2x, joueur2y = app.joueur2.x, app.joueur2.y

    if app.joueur1.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
        app.joueur1.action = action_J1
        app.joueur1.convert_action_vitesse()
        app.joueur2.action = action_J2
        app.joueur2.convert_action_vitesse()

    app.balle.verif_collisions([app.joueur1, app.joueur2])

    app.balle.deplacement()
    app.joueur1.deplacement(app.balle, [app.joueur2])
    app.joueur2.deplacement(app.balle, [app.joueur1])


    but_marque = False
    score1 = app.balle.actu_score1(app.scorej1)
    score2 = app.balle.actu_score2(app.scorej2)
    vainqueur = ''
    if score1 != app.scorej1:
        reward_J1 = 10
        reward_J2 = -10
        but_marque = True
        vainqueur = 'joueur1'
    elif score2 != app.scorej2:
        reward_J1 = -10
        reward_J2 = 10
        but_marque = True
        vainqueur = 'joueur2'

    else:
        reward_J1 = - 0.001
        reward_J2 = - 0.001
        if app.balle.balle_tiree == True:
            if app.balle.possession == 'joueur1':
                reward_J1 = 0.1 * max(app.balle.vx / (VITESSE_JOUEUR), app.balle.vx / (4 * VITESSE_JOUEUR))
                reward_J2 = 0
            elif app.balle.possession == 'joueur2':
                reward_J2 = 0.1 * max(- app.balle.vx / (VITESSE_JOUEUR), - app.balle.vx / (4 * VITESSE_JOUEUR))
                reward_J1 = 0
            else:
                reward_J1 = 0.1 * max(app.balle.vx / (VITESSE_JOUEUR), app.balle.vx / (4 * VITESSE_JOUEUR))
                reward_J2 = 0.1 * max(- app.balle.vx / (VITESSE_JOUEUR), - app.balle.vx / (4 * VITESSE_JOUEUR))

        distance_J1_balle_sans_bouger_joueur = math.sqrt((app.balle.x - joueur1x) ** 2 + (app.balle.y - joueur1y) ** 2)
        distance_J1_balle_bouger_joueur = math.sqrt((app.balle.x - app.joueur1.x) ** 2 + (app.balle.y - app.joueur1.y) ** 2)
        distance_J2_balle_sans_bouger_joueur = math.sqrt((app.balle.x - joueur2x) ** 2 + (app.balle.y - joueur2y) ** 2)
        distance_J2_balle_bouger_joueur = math.sqrt((app.balle.x - app.joueur2.x) ** 2 + (app.balle.y - app.joueur2.y) ** 2)
        ## on recompense si ca permet de reduire la distance qu'il y aurait eu sans avoir bougé
        reward_J1 += 0.003 * (distance_J1_balle_sans_bouger_joueur - distance_J1_balle_bouger_joueur) / VITESSE_JOUEUR
        reward_J2 += 0.003 * (distance_J2_balle_sans_bouger_joueur - distance_J2_balle_bouger_joueur) / VITESSE_JOUEUR
    
    return reward_J1, reward_J2, but_marque, vainqueur

def entrainer(nb_parties=NB_PARTIES):
    reseau_neurones_J1 = Reseau_neurones("reseau_neurones_foot_1v1_J1.npz", TAILLE_STATE_FOOT_1V1, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    reseau_neurones_J2 = Reseau_neurones("reseau_neurones_foot_1v1_J2.npz", TAILLE_STATE_FOOT_1V1, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    victoires_J1 = 0
    victoires_J2 = 0
    Liste_victoires = []
    for partie in range(nb_parties):
        p = p_debut - (p_debut - p_fin) * partie / nb_parties
        vainqueur = jouer_une_partie(reseau_neurones_J1, reseau_neurones_J2, p, partie)

        if vainqueur == 'joueur1':
            victoires_J1 += 1
            Liste_victoires.append(1)
        elif vainqueur == 'joueur2':
            victoires_J2 += 1
            Liste_victoires.append(-1)
        else:
            Liste_victoires.append(0)
        Liste_victoires = Liste_victoires[-100:]
        if partie % 10 == 0:
            numero_partie = partie + 1
            print(f'WR J1 : {victoires_J1 * 100 / numero_partie} % | WR J2 : {victoires_J2 * 100 / numero_partie} % | nulles : {(numero_partie - victoires_J1 - victoires_J2) * 100 / numero_partie} %')
            print(f'WR /100 parties J1 : {Liste_victoires.count(1) * 100 / len(Liste_victoires)} % | WR /100 parties J2 : {Liste_victoires.count(-1) * 100 / len(Liste_victoires)} %')

if __name__ == "__main__":
    entrainer()