from packages.build_state import build_state_foot_2v2_J1, build_state_foot_2v2_J2
from packages._2v2_entrainement_reseau_neurones import Reseau_neurones
from packages._2v2_parametres_reseau_neurones import conversions_actions_J2, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2, NB_ITERATIONS_1_PARTIE, TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_PARTIES, p_debut, p_fin
import random
import numpy as np
from foot_2v2 import Foot_2v2
import math
from packages.parametres import VITESSE_JOUEUR, NB_EXECUTIONS_1_ACTION, LONGUEUR
from collections import deque
from packages.plus_proche_balle import plus_proche_balle
from packages.parametres import COEF_FROT_FLUIDE
import time
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
    distance balle aux 4 limites de terrain
    distance joueurs adverses-balle selon x et y
    distance joueur allié selon x et y
    distance joueur-adversaires
    distance joueur allié-balle selon x et y
    possession balle (-1 si c'est l'adversaire, 0 si c'est personne, 1 si c'est le joueur)
action (81):
    "rien" : 9,
    "gauche" : 1,
    "droite" : 2, 
    "haut" : 3,
    "bas" : 4,
    "gauchehaut" : 5,
    "gauchebas" : 6,
    "droitehaut" : 7,
    "droitebas" : 8
    les 9 premiers correspondent a l'action gauche du joueurb, de 10-18, action droite pour Jb etc
"""

def jouer_une_partie(reseau_neurones_J1, reseau_neurones_J2, p, partie, entrainement_actuel, entrainement=True):
    """Joue une partie complète et alimente le réseau en samples."""
    ## initialisation de la partie
    app = Foot_2v2()

    iteration = 0
    partie_en_cours = True
    historique_tirs = []  # on y stocke des tuples (nom du tireur, iteration correspondante, balle.x, balle.y)
    buffer_local = []
    while partie_en_cours:
        iteration += 1
        plus_proche_J1, Tp_J1, Te_J1 = plus_proche_balle(app.joueur1a, app.joueur1b, app.balle)
        plus_proche_J2, Tp_J2, Te_J2 = plus_proche_balle(app.joueur2a, app.joueur2b, app.balle)
        
        if plus_proche_J1 == 'joueur a' and plus_proche_J2 == 'joueur a':
            state1_J1 = build_state_foot_2v2_J1(TAILLE_STATE, app, app.balle, app.joueur1a, app.joueur1b, app.joueur2a, app.joueur2b, Tp_J1, Te_J1)
            state1_J2 = build_state_foot_2v2_J2(TAILLE_STATE, app, app.balle, app.joueur2a, app.joueur2b, app.joueur1a, app.joueur1b, Tp_J2, Te_J2)
        elif plus_proche_J1 == 'joueur a' and plus_proche_J2 == 'joueur b':
            state1_J1 = build_state_foot_2v2_J1(TAILLE_STATE, app, app.balle, app.joueur1a, app.joueur1b, app.joueur2b, app.joueur2a, Tp_J1, Te_J1)
            state1_J2 = build_state_foot_2v2_J2(TAILLE_STATE, app, app.balle, app.joueur2b, app.joueur2a, app.joueur1a, app.joueur1b, Tp_J2, Te_J2)
        elif plus_proche_J1 == 'joueur b' and plus_proche_J2 == 'joueur a':
            state1_J1 = build_state_foot_2v2_J1(TAILLE_STATE, app, app.balle, app.joueur1b, app.joueur1a, app.joueur2a, app.joueur2b, Tp_J1, Te_J1)
            state1_J2 = build_state_foot_2v2_J2(TAILLE_STATE, app, app.balle, app.joueur2a, app.joueur2b, app.joueur1b, app.joueur1a, Tp_J2, Te_J2)
        elif plus_proche_J1 == 'joueur b' and plus_proche_J2 == 'joueur b':
            state1_J1 = build_state_foot_2v2_J1(TAILLE_STATE, app, app.balle, app.joueur1b, app.joueur1a, app.joueur2b, app.joueur2a, Tp_J1, Te_J1)
            state1_J2 = build_state_foot_2v2_J2(TAILLE_STATE, app, app.balle, app.joueur2b, app.joueur2a, app.joueur1b, app.joueur1a, Tp_J2, Te_J2)

        if entrainement_actuel == 'J1':
            action_J1 = choisir_action(reseau_neurones_J1, state1_J1, p)
            action_J2 = int(np.argmax(reseau_neurones_J2.calcul_couche_sortie(state1_J2))) + 1
        elif entrainement_actuel == 'J2':
            action_J2 = choisir_action(reseau_neurones_J2, state1_J2, p)
            action_J1 = int(np.argmax(reseau_neurones_J1.calcul_couche_sortie(state1_J1))) + 1
        if plus_proche_J1 == 'joueur a':
            idx_J1 = action_J1 - 1
            action_J1a = idx_J1 % 9 + 1
            action_J1b = idx_J1 // 9 + 1
        elif plus_proche_J1 == 'joueur b':
            idx_J1 = action_J1 - 1
            action_J1b = idx_J1 % 9 + 1
            action_J1a = idx_J1 // 9 + 1
        if plus_proche_J2 == 'joueur a':
            idx_J2 = action_J2 - 1
            action_J2a = conversions_actions_J2[idx_J2 % 9 + 1]
            action_J2b = conversions_actions_J2[idx_J2 // 9 + 1]
        elif plus_proche_J2 == 'joueur b':
            idx_J2 = action_J2 - 1
            action_J2b = conversions_actions_J2[idx_J2 % 9 + 1]
            action_J2a = conversions_actions_J2[idx_J2 // 9 + 1]

        reward_J1, reward_J2, but_marque, vainqueur, buffer_local, historique_tirs = executer_action(action_J1a, action_J1b, action_J2a, action_J2b, app, iteration, buffer_local, historique_tirs, plus_proche_J1, plus_proche_J2)

        if iteration >= NB_ITERATIONS_1_PARTIE:
            partie_en_cours = False
        if but_marque:
            partie_en_cours = False

        if plus_proche_J1 == 'joueur a' and plus_proche_J2 == 'joueur a':
            state2_J1 = build_state_foot_2v2_J1(TAILLE_STATE, app, app.balle, app.joueur1a, app.joueur1b, app.joueur2a, app.joueur2b, Tp_J1, Te_J1)
            state2_J2 = build_state_foot_2v2_J2(TAILLE_STATE, app, app.balle, app.joueur2a, app.joueur2b, app.joueur1a, app.joueur1b, Tp_J2, Te_J2)
        elif plus_proche_J1 == 'joueur a' and plus_proche_J2 == 'joueur b':
            state2_J1 = build_state_foot_2v2_J1(TAILLE_STATE, app, app.balle, app.joueur1a, app.joueur1b, app.joueur2b, app.joueur2a, Tp_J1, Te_J1)
            state2_J2 = build_state_foot_2v2_J2(TAILLE_STATE, app, app.balle, app.joueur2b, app.joueur2a, app.joueur1a, app.joueur1b, Tp_J2, Te_J2)
        elif plus_proche_J1 == 'joueur b' and plus_proche_J2 == 'joueur a':
            state2_J1 = build_state_foot_2v2_J1(TAILLE_STATE, app, app.balle, app.joueur1b, app.joueur1a, app.joueur2a, app.joueur2b, Tp_J1, Te_J1)
            state2_J2 = build_state_foot_2v2_J2(TAILLE_STATE, app, app.balle, app.joueur2a, app.joueur2b, app.joueur1b, app.joueur1a, Tp_J2, Te_J2)
        elif plus_proche_J1 == 'joueur b' and plus_proche_J2 == 'joueur b':
            state2_J1 = build_state_foot_2v2_J1(TAILLE_STATE, app, app.balle, app.joueur1b, app.joueur1a, app.joueur2b, app.joueur2a, Tp_J1, Te_J1)
            state2_J2 = build_state_foot_2v2_J2(TAILLE_STATE, app, app.balle, app.joueur2b, app.joueur2a, app.joueur1b, app.joueur1a, Tp_J2, Te_J2)

        if entrainement_actuel == 'J1':
            buffer_local.append(np.concatenate([state1_J1, state2_J1, [action_J1, reward_J1, but_marque]]))
        elif entrainement_actuel == 'J2':
            buffer_local.append(np.concatenate([state1_J2, state2_J2, [action_J2, reward_J2, but_marque]]))

        app.balle.joueur_tir = None

        '''if but_marque:
            print(f'partie {partie} : but {vainqueur}')'''

    if entrainement_actuel == 'J1':
        for sample in buffer_local:
            reseau_neurones_J1.ajout_sample(sample)
        if entrainement:
            reseau_neurones_J1.entrainement_reseau()
    elif entrainement_actuel == 'J2':
        for sample in buffer_local:
            reseau_neurones_J2.ajout_sample(sample)
        if entrainement:
            reseau_neurones_J2.entrainement_reseau()

    return vainqueur


def choisir_action(reseau_neurones, state, p):
    if random.random() <= p:
        return random.randint(1, NB_ACTIONS_POSSIBLES)
    return np.argmax(reseau_neurones.calcul_couche_sortie(state)) + 1


def executer_action(action_J1a, action_J1b, action_J2a, action_J2b, app: Foot_2v2, iteration, buffer_local, historique_tirs, plus_proche_J1, plus_proche_J2):
    joueur1ax, joueur1ay = app.joueur1a.x, app.joueur1a.y
    joueur1bx, joueur1by = app.joueur1b.x, app.joueur1b.y
    joueur2ax, joueur2ay = app.joueur2a.x, app.joueur2a.y
    joueur2bx, joueur2by = app.joueur2b.x, app.joueur2b.y

    app.joueur1a.action = action_J1a
    app.joueur1a.convert_action_vitesse()
    app.joueur2a.action = action_J2a
    app.joueur2a.convert_action_vitesse()
    app.joueur1b.action = action_J1b
    app.joueur1b.convert_action_vitesse()
    app.joueur2b.action = action_J2b
    app.joueur2b.convert_action_vitesse()

    app.balle.verif_collisions([app.joueur1a, app.joueur1b, app.joueur2a, app.joueur2b])

    app.balle.deplacement([app.joueur1a, app.joueur1b, app.joueur2a, app.joueur2b])
    app.joueur1a.deplacement(app.balle, [app.joueur2a, app.joueur2b, app.joueur1b])
    app.joueur2a.deplacement(app.balle, [app.joueur1a, app.joueur2b, app.joueur1b])
    app.joueur1b.deplacement(app.balle, [app.joueur2a, app.joueur2b, app.joueur1a])
    app.joueur2b.deplacement(app.balle, [app.joueur1a, app.joueur2a, app.joueur1b])

    reward_J1 = 0
    reward_J2 = 0

    if app.balle.possession == app.joueur1a.nom:
        reward_J2 -= 0.01
        reward_J1 += 0.01
    elif app.balle.possession == app.joueur2a.nom:
        reward_J1 -= 0.01
        reward_J2 += 0.01

    if historique_tirs != []:
        if (app.joueur1a.tir or app.joueur1b.tir or app.joueur2a.tir or app.joueur2b.tir) and historique_tirs[-1][0][-2] == '1':
            # on recompense le tir précédent en fonction de la distance parcourue
            distance_parcourue = app.balle.x - historique_tirs[-1][2]
            buffer_local[historique_tirs[-1][1]][3] += 3 * (distance_parcourue / (VITESSE_JOUEUR * (1 / COEF_FROT_FLUIDE)))
        elif (app.joueur1a.tir or app.joueur1b.tir or app.joueur2a.tir or app.joueur2b.tir) and historique_tirs[-1][0][-2] == '2':
            # on recompense le tir précédent en fonction de la distance parcourue
            distance_parcourue = historique_tirs[-1][2] - app.balle.x
            buffer_local[historique_tirs[-1][1]][3] += 3 * (distance_parcourue / (VITESSE_JOUEUR * (1 / COEF_FROT_FLUIDE)))

    if app.joueur1a.tir:
        if historique_tirs != []:
            if historique_tirs[-1][0][-2] == '1':  # conservation de balle
                buffer_local[historique_tirs[-1][1]][3] += 1  # on ajoute cette reward au sample correspondant
            '''elif historique_tirs[-1][0][-2] == '2':  # bonne défense
                reward_J1 += 2'''
        historique_tirs.append(('joueur 1a', len(buffer_local), app.balle.x, app.balle.y))
    elif app.joueur1b.tir:
        if historique_tirs != []:
            if historique_tirs[-1][0][-2] == '1':  # conservation de balle
                buffer_local[historique_tirs[-1][1]][3] += 1  # on ajoute cette reward au sample correspondant
            '''elif historique_tirs[-1][0][-2] == '2':  # bonne défense
                reward_J1 += 2'''
        historique_tirs.append(('joueur 1b', len(buffer_local), app.balle.x, app.balle.y))
    elif app.joueur2a.tir:
        if historique_tirs != []:
            if historique_tirs[-1][0][-2] == '2':  # conservation de balle
                buffer_local[historique_tirs[-1][1]][3] += 1  # on ajoute cette reward au sample correspondant
            '''elif historique_tirs[-1][0][-2] == '1':  # bonne défense
                reward_J2 += 2'''
        historique_tirs.append(('joueur 2a', len(buffer_local), app.balle.x, app.balle.y))
    elif app.joueur2b.tir:
        if historique_tirs != []:
            if historique_tirs[-1][0][-2] == '2':  # conservation de balle
                buffer_local[historique_tirs[-1][1]][3] += 1  # on ajoute cette reward au sample correspondant
            '''elif historique_tirs[-1][0][-2] == '1':  # bonne défense
                reward_J2 += 2'''
        historique_tirs.append(('joueur 2b', len(buffer_local), app.balle.x, app.balle.y))

    but_marque = False
    score1 = app.balle.actu_score1(app.scorej1)
    score2 = app.balle.actu_score2(app.scorej2)
    vainqueur = ''
    
    if score1 != app.scorej1:
        but_marque = True
        vainqueur = 'joueur1'
        # impossible que historique_tirs soit vide au moment d'un but
        reward_J1 = 100
        reward_J2 = -100
    elif score2 != app.scorej2:
        but_marque = True
        vainqueur = 'joueur2'
        reward_J1 = -100
        reward_J2 = 100

    if True:
        if plus_proche_J1 == 'joueur a':
            distance_J_balle_sans_bouger_joueur = math.sqrt((app.balle.x - joueur1ax) ** 2 + (app.balle.y - joueur1ay) ** 2)
            distance_J_balle_bouger_joueur = math.sqrt((app.balle.x - app.joueur1a.x) ** 2 + (app.balle.y - app.joueur1a.y) ** 2)
            ## on recompense si le joueur le plus proche de la balle s'en rapproche
            reward_J1 += 0.01 * (distance_J_balle_sans_bouger_joueur - distance_J_balle_bouger_joueur) / VITESSE_JOUEUR

        elif plus_proche_J1 == 'joueur b':
            distance_J_balle_sans_bouger_joueur = math.sqrt((app.balle.x - joueur1bx) ** 2 + (app.balle.y - joueur1by) ** 2)
            distance_J_balle_bouger_joueur = math.sqrt((app.balle.x - app.joueur1b.x) ** 2 + (app.balle.y - app.joueur1b.y) ** 2)
            reward_J1 += 0.01 * (distance_J_balle_sans_bouger_joueur - distance_J_balle_bouger_joueur) / VITESSE_JOUEUR
        if plus_proche_J2 == 'joueur a':
            distance_J_balle_sans_bouger_joueur = math.sqrt((app.balle.x - joueur2ax) ** 2 + (app.balle.y - joueur2ay) ** 2)
            distance_J_balle_bouger_joueur = math.sqrt((app.balle.x - app.joueur2a.x) ** 2 + (app.balle.y - app.joueur2a.y) ** 2)
            ## on recompense si le joueur le plus proche de la balle s'en rapproche
            reward_J2 += 0.01 * (distance_J_balle_sans_bouger_joueur - distance_J_balle_bouger_joueur) / VITESSE_JOUEUR

        elif plus_proche_J2 == 'joueur b':
            distance_J_balle_sans_bouger_joueur = math.sqrt((app.balle.x - joueur2bx) ** 2 + (app.balle.y - joueur2by) ** 2)
            distance_J_balle_bouger_joueur = math.sqrt((app.balle.x - app.joueur2b.x) ** 2 + (app.balle.y - app.joueur2b.y) ** 2)
            reward_J2 += 0.01 * (distance_J_balle_sans_bouger_joueur - distance_J_balle_bouger_joueur) / VITESSE_JOUEUR
    
    return reward_J1, reward_J2, but_marque, vainqueur, buffer_local, historique_tirs

def entrainer(nb_parties=NB_PARTIES):
    reseau_neurones_J1 = Reseau_neurones("reseau_neurones_foot_2v2_J1.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    reseau_neurones_J2 = Reseau_neurones("reseau_neurones_foot_2v2_J2.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
    Liste_victoires = []
    partie = 0
    for _ in range(500):
        vainqueur = jouer_une_partie(reseau_neurones_J1, reseau_neurones_J2, 0, partie, 'J1', False)
        if vainqueur == 'joueur1':
            Liste_victoires.append(1)
        elif vainqueur == 'joueur2':
            Liste_victoires.append(-1)
        else:
            Liste_victoires.append(0)
    print()
    print('resultats du test :')
    print(f'WR /500 parties J1 : {Liste_victoires.count(1) * 100 / len(Liste_victoires)} % | WR /500 parties J2 : {Liste_victoires.count(-1) * 100 / len(Liste_victoires)} %')
    print()
    if Liste_victoires.count(1) * 100 / len(Liste_victoires) > Liste_victoires.count(-1) * 100 / len(Liste_victoires):  # si on gagne + de 60 % du temps on actualise reseau J2
        entrainement_actuel = 'J2'
    else:
        entrainement_actuel = 'J1'

    Liste_victoires = []
    for partie in range(nb_parties):
        '''xd = - math.log(p_debut)
        xf = - math.log(p_fin)
        x = xd + (xf - xd) * (partie % 2000) / 2000
        p = math.exp(-x)'''
        p = p_debut - (p_debut - p_fin) * (partie % 1000) / 1000
        vainqueur = jouer_une_partie(reseau_neurones_J1, reseau_neurones_J2, p, partie, entrainement_actuel, True)
        if vainqueur == 'joueur1':
            Liste_victoires.append(1)
        elif vainqueur == 'joueur2':
            Liste_victoires.append(-1)
        else:
            Liste_victoires.append(0)
        '''if partie % 100 == 0:
            print(f'WR J1 : {Liste_victoires.count(1) * 100 / len(Liste_victoires)} % | WR J2 : {Liste_victoires.count(-1) * 100 / len(Liste_victoires)} % | nulles : {Liste_victoires.count(0) * 100 / len(Liste_victoires)} %')
        '''
        if (partie + 1) % 1000 == 0:
            # on realise 500 parties
            Liste_victoires = []
            for _ in range(500):
                vainqueur = jouer_une_partie(reseau_neurones_J1, reseau_neurones_J2, 0, partie, 'J1', False)
                if vainqueur == 'joueur1':
                    Liste_victoires.append(1)
                elif vainqueur == 'joueur2':
                    Liste_victoires.append(-1)
                else:
                    Liste_victoires.append(0)
            print()
            print(f'entrainement {entrainement_actuel}')
            print('resultats du test :')
            print(f'WR /500 parties J1 : {Liste_victoires.count(1) * 100 / len(Liste_victoires)} % | WR /500 parties J2 : {Liste_victoires.count(-1) * 100 / len(Liste_victoires)} %')
            print()
            if Liste_victoires.count(1) * 100 / len(Liste_victoires) > 10 + Liste_victoires.count(-1) * 100 / len(Liste_victoires) and entrainement_actuel == 'J1':  # si on gagne 10% + que J2 on actualise reseau J2
                reseau_neurones_J1.export_reseau(partie)
                entrainement_actuel = 'J2'
                reseau_neurones_J2.vider_samples()  # on vide les samples trop vieux
            elif Liste_victoires.count(1) * 100 / len(Liste_victoires) + 10 < Liste_victoires.count(-1) * 100 / len(Liste_victoires) and entrainement_actuel == 'J2':
                reseau_neurones_J2.export_reseau(partie)
                entrainement_actuel = 'J1'
                reseau_neurones_J1.vider_samples()


if __name__ == "__main__":
    entrainer()
