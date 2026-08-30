from packages.build_state import build_state_foot_2v2
from packages._2v2_entrainement_reseau_neurones import Reseau_neurones
from packages._2v2_parametres_reseau_neurones import N_STEP, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2, NB_ITERATIONS_1_PARTIE, TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_PARTIES, p_debut, p_fin
import random
import numpy as np
from foot_2v2 import Foot_2v2
import math
from packages.parametres import VITESSE_JOUEUR, NB_EXECUTIONS_1_ACTION
from collections import deque

"""
etat (24): 
    (toutes les distances sont normalisées)
    distance a la balle selon x
    distance a la balle selon y
    vitesse balle selon x
    vitesse balle selon y
    distance balle cages OUEST selon x
    distance balle cages EST selon x
    distance balle-cages selon y (0 si la balle est alignée)
    distance joueur aux 4 limites de terrain
    distance joueurs adverses selon x et y
    distance joueurs adverses-balle selon x et y
    distance joueur allié selon x et y
    distance joueur allié-balle selon x et y
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

def jouer_une_partie(reseau_neurones_J1a, reseau_neurones_J1b, reseau_neurones_J2a, reseau_neurones_J2b, p, partie):
    """Joue une partie complète et alimente le réseau en samples."""
    ## initialisation de la partie
    app = Foot_2v2()
    buffer_local_J1a = deque()  # stocke (state1, action, reward) en attente
    buffer_local_J1b = deque()  # stocke (state1, action, reward) en attente
    buffer_local_J2a = deque()  # stocke (state1, action, reward) en attente
    buffer_local_J2b = deque()  # stocke (state1, action, reward) en attente

    iteration = 0
    partie_en_cours = True
    while partie_en_cours:
        iteration += 1
        if app.joueur1a.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
            state1_J1a = build_state_foot_2v2(TAILLE_STATE, app, app.joueur1a, app.joueur1b, app.joueur2a, app.joueur2b)
            action_J1a = choisir_action(reseau_neurones_J1a, state1_J1a, p)
            state1_J2a = build_state_foot_2v2(TAILLE_STATE, app, app.joueur2a, app.joueur2b, app.joueur1a, app.joueur1b)
            action_J2a = choisir_action(reseau_neurones_J2a, state1_J2a, p)
            state1_J1b = build_state_foot_2v2(TAILLE_STATE, app, app.joueur1b, app.joueur1a, app.joueur2a, app.joueur2b)
            action_J1b = choisir_action(reseau_neurones_J1b, state1_J1b, p)
            state1_J2b = build_state_foot_2v2(TAILLE_STATE, app, app.joueur2b, app.joueur2a, app.joueur1a, app.joueur1b)
            action_J2b = choisir_action(reseau_neurones_J2b, state1_J2b, p)
            reward_J1a, reward_J1b, reward_J2a, reward_J2b, but_marque, vainqueur = executer_action(action_J1a, action_J1b, action_J2a, action_J2b, app, partie)

            if iteration >= NB_ITERATIONS_1_PARTIE:
                partie_en_cours = False
            if but_marque:
                partie_en_cours = False

            state2_J1a = build_state_foot_2v2(TAILLE_STATE, app, app.joueur1a, app.joueur1b, app.joueur2a, app.joueur2b)
            state2_J2a = build_state_foot_2v2(TAILLE_STATE, app, app.joueur2a, app.joueur2b, app.joueur1a, app.joueur1b)
            state2_J1b = build_state_foot_2v2(TAILLE_STATE, app, app.joueur1b, app.joueur1a, app.joueur2a, app.joueur2b)
            state2_J2b = build_state_foot_2v2(TAILLE_STATE, app, app.joueur2b, app.joueur2a, app.joueur1a, app.joueur1b)

            buffer_local_J1a.append((state1_J1a, action_J1a, reward_J1a, state2_J1a, but_marque))
            buffer_local_J2a.append((state1_J2a, action_J2a, reward_J2a, state2_J2a, but_marque))
            buffer_local_J1b.append((state1_J1b, action_J1b, reward_J1b, state2_J1b, but_marque))
            buffer_local_J2b.append((state1_J2b, action_J2b, reward_J2b, state2_J2b, but_marque))

            # dès qu'on a accumulé n transitions, on peut calculer un sample n-step
            if len(buffer_local_J1a) >= N_STEP:
                _emettre_sample_n_step(buffer_local_J1a, reseau_neurones_J1a, N_STEP)
                buffer_local_J1a.popleft()
                _emettre_sample_n_step(buffer_local_J2a, reseau_neurones_J2a, N_STEP)
                buffer_local_J2a.popleft()
                _emettre_sample_n_step(buffer_local_J1b, reseau_neurones_J1b, N_STEP)
                buffer_local_J1b.popleft()
                _emettre_sample_n_step(buffer_local_J2b, reseau_neurones_J2b, N_STEP)
                buffer_local_J2b.popleft()

            reseau_neurones_J1a.entrainement_reseau(partie)
            reseau_neurones_J2a.entrainement_reseau(partie)
            reseau_neurones_J1b.entrainement_reseau(partie)
            reseau_neurones_J2b.entrainement_reseau(partie)

        else:
            executer_action(None, None, None, None, app, partie)
        if but_marque:
            print(f'partie {partie} : but {vainqueur}')

    # à la fin de la partie, vider les transitions restantes (n-step raccourci)
    '''while buffer_local:
        _emettre_sample_n_step(buffer_local, reseau_neurones, len(buffer_local))
        buffer_local.popleft()'''  # on perd les derniers instants pour pas s'embeter dans les calculs

    return vainqueur


def _emettre_sample_n_step(buffer_local, reseau_neurones, n):
    from packages._2v2_parametres_reseau_neurones import gamma
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


def executer_action(action_J1a, action_J1b, action_J2a, action_J2b, app: Foot_2v2, partie):

    if app.joueur1a.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
        app.joueur1a.action = action_J1a
        app.joueur1a.convert_action_vitesse()
        app.joueur2a.action = action_J2a
        app.joueur2a.convert_action_vitesse()
        app.joueur1b.action = action_J1b
        app.joueur1b.convert_action_vitesse()
        app.joueur2b.action = action_J2b
        app.joueur2b.convert_action_vitesse()

    app.balle.verif_collisions([app.joueur1a, app.joueur2a, app.joueur1b, app.joueur2b])

    app.balle.deplacement()
    app.joueur1a.deplacement(app.balle, [app.joueur2a, app.joueur2b, app.joueur1b])
    app.joueur2a.deplacement(app.balle, [app.joueur1a, app.joueur2b, app.joueur1b])
    app.joueur1b.deplacement(app.balle, [app.joueur2a, app.joueur2b, app.joueur1a])
    app.joueur2b.deplacement(app.balle, [app.joueur1a, app.joueur2a, app.joueur1b])

    but_marque = False
    score1 = app.balle.actu_score1(app.scorej1)
    score2 = app.balle.actu_score2(app.scorej2)
    vainqueur = ''
    if score1 != app.scorej1:
        reward_J1a = 10
        reward_J2a = -10
        reward_J1b = 10
        reward_J2b = -10
        but_marque = True
        vainqueur = 'joueur1'
    elif score2 != app.scorej2:
        reward_J1a = -10
        reward_J2a = 10
        reward_J1b = -10
        reward_J2b = 10
        but_marque = True
        vainqueur = 'joueur2'

    else:
        reward_J1a = 0
        reward_J1b = 0
        reward_J2a = 0
        reward_J2b = 0

    return reward_J1a, reward_J1b, reward_J2a, reward_J2b, but_marque, vainqueur

def entrainer(nb_parties=NB_PARTIES):
    reseau_neurones_J1a = Reseau_neurones("reseau_neurones_foot_2v2_J1a.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    reseau_neurones_J2a = Reseau_neurones("reseau_neurones_foot_2v2_J2a.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    reseau_neurones_J1b = Reseau_neurones("reseau_neurones_foot_2v2_J1b.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    reseau_neurones_J2b = Reseau_neurones("reseau_neurones_foot_2v2_J2b.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    victoires_J1 = 0
    victoires_J2 = 0
    Liste_victoires = []
    for partie in range(nb_parties):
        p = p_debut - (p_debut - p_fin) * partie / nb_parties
        vainqueur = jouer_une_partie(reseau_neurones_J1a, reseau_neurones_J1b, reseau_neurones_J2a, reseau_neurones_J2b, p, partie)

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