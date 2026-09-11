import pyxel
from packages.parametres import *
from packages.tracer_terrain import tracer_terrain
from packages.balle import Balle
from packages.joueur import Joueur
from packages.affichage_scores import afficher_scores
from packages.build_state import build_state_foot_2v2_J1, build_state_foot_2v2_J2
from packages._2v2_parametres_reseau_neurones import conversions_actions_J2, TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2
from packages._2v2_entrainement_reseau_neurones import Reseau_neurones
import numpy as np
import random
import math
import time
from packages.plus_proche_balle import plus_proche_balle

class Foot_2v2:
    def __init__(self):
        self.c = 0
        dy = random.randint(-150, 150)
        self.balle = Balle(LONGUEUR // 2 + random.choice([-150, 150]), LARGEUR // 2 + dy)      
        self.scorej1 = 0
        self.scorej2 = 0
        self.reseau_neurones_J1 = Reseau_neurones("reseau_neurones_foot_2v2_J1.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
        self.reseau_neurones_J2 = Reseau_neurones("reseau_neurones_foot_2v2_J2.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)

        pyxel.init(LONGUEUR, LARGEUR, title=TITRE)
        pyxel.mouse(True)
        self.joueur1a = Joueur(LONGUEUR / 2 - 200, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1')
        self.joueur2a = Joueur(LONGUEUR / 2 + 200, LARGEUR / 2  - 50, COULEUR_J2, 'joueur2')
        self.joueur1b = Joueur(LONGUEUR / 2 - 200, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1')
        self.joueur2b = Joueur(LONGUEUR / 2 + 200, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2')


    def update(self):
        self.c += 1

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

        action_J1 = int(np.argmax(self.reseau_neurones_J1.calcul_couche_sortie(state1_J1))) + 1
        action_J2 = int(np.argmax(self.reseau_neurones_J2.calcul_couche_sortie(state1_J2))) + 1
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

        self.joueur1a.action = action_J1a
        self.joueur1b.action = action_J1b
        self.joueur2a.action = action_J2a
        self.joueur2b.action = action_J2b

        self.joueur1a.convert_action_vitesse()
        self.joueur2a.convert_action_vitesse()
        self.joueur1b.convert_action_vitesse()
        self.joueur2b.convert_action_vitesse()

        self.balle.verif_collisions([self.joueur1a, self.joueur2a, self.joueur1b, self.joueur2b])

        app.balle.deplacement([app.joueur1a, app.joueur1b, app.joueur2a, app.joueur2b])
        self.joueur1a.deplacement(self.balle, [self.joueur2a, self.joueur2b, self.joueur1b])
        self.joueur2a.deplacement(self.balle, [self.joueur1a, self.joueur1b, self.joueur2b])
        self.joueur1b.deplacement(self.balle, [self.joueur2a, self.joueur2b, self.joueur1a])
        self.joueur2b.deplacement(self.balle, [self.joueur1a, self.joueur1b, self.joueur2a])

        score = self.balle.actu_score1(self.scorej1)
        if score != self.scorej1:
            self.scorej1 = score
            dy = random.randint(-150, 150)
            self.balle = Balle(LONGUEUR // 2 + random.choice([-150, 150]), LARGEUR // 2 + dy)      
            self.joueur1a = Joueur(LONGUEUR / 2 - 200, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1')
            self.joueur2a = Joueur(LONGUEUR / 2 + 200, LARGEUR / 2  - 50, COULEUR_J2, 'joueur2')
            self.joueur1b = Joueur(LONGUEUR / 2 - 200, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1')
            self.joueur2b = Joueur(LONGUEUR / 2 + 200, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2')


        score = self.balle.actu_score2(self.scorej2)
        if score != self.scorej2:
            self.scorej2 = score
            dy = random.randint(-150, 150)
            self.balle = Balle(LONGUEUR // 2 + random.choice([-150, 150]), LARGEUR // 2 + dy)      
            self.joueur1a = Joueur(LONGUEUR / 2 - 200, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1')
            self.joueur2a = Joueur(LONGUEUR / 2 + 200, LARGEUR / 2  - 50, COULEUR_J2, 'joueur2')
            self.joueur1b = Joueur(LONGUEUR / 2 - 200, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1')
            self.joueur2b = Joueur(LONGUEUR / 2 + 200, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2')

    def draw(self):
        pyxel.cls(COULEUR_BORD)

        tracer_terrain()
        self.balle.tracer()
        self.joueur1a.tracer()
        self.joueur2a.tracer()
        self.joueur1b.tracer()
        self.joueur2b.tracer()

        afficher_scores(self.scorej1, self.scorej2)


if __name__ == "__main__":
    app = Foot_2v2()
    pyxel.run(app.update, app.draw)
