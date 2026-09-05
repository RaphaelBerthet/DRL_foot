import pyxel
from packages.parametres import *
from packages.tracer_terrain import tracer_terrain
from packages.balle import Balle
from packages.joueur import Joueur
from packages.affichage_scores import afficher_scores
from packages.build_state import build_state_foot_1_joueur
from packages._1_joueur_parametres_reseau_neurones import TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2
from packages._1_joueur_entrainement_reseau_neurones import Reseau_neurones
import numpy as np
import random
import math

p = 0.7  # proba de faire une action random (pour voir les conséquences)

class Foot_1_joueur:
    def __init__(self):
        R = random.randint(50, 100)
        teta = random.randint(0, 359) * math.pi / 180
        self.balle = Balle(LONGUEUR // 2 - 50 + math.cos(teta) * R, LARGEUR // 2 + math.sin(teta) * R)
        self.scorej1 = 0
        self.reseau_neurones = Reseau_neurones("reseau_neurones_foot_1_joueur_test10.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)

        pyxel.init(LONGUEUR, LARGEUR, title=TITRE)
        pyxel.mouse(True)
        self.joueur1 = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2, COULEUR_J1, 'joueur1')

    def update(self):
        # Le réseau produit un vecteur de 9 scores (indices 0 à 8), alors que
        # les actions du jeu sont numérotées de 1 à 9.
        # if self.joueur1.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
        if True:
            state = build_state_foot_1_joueur(TAILLE_STATE, self)
            self.joueur1.action = int(np.argmax(self.reseau_neurones.calcul_couche_sortie(state))) + 1
            
            if random.random() < p:
                self.joueur1.action = random.randint(1, 9)
            else:
                self.joueur1.action = 5
            self.joueur1.convert_action_vitesse()

        self.balle.verif_collisions([self.joueur1])

        self.balle.deplacement()
        self.joueur1.deplacement(self.balle)

        score = self.balle.actu_score1(self.scorej1)
        if score != self.scorej1:
            self.scorej1 = score
            R = random.randint(50, 100)
            teta = random.randint(0, 359) * math.pi / 180
            self.balle = Balle(LONGUEUR // 2 - 50 + math.cos(teta) * R, LARGEUR // 2 + math.sin(teta) * R)
            self.joueur1 = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2, COULEUR_J1, 'joueur1')

    def draw(self):
        pyxel.cls(COULEUR_BORD)

        tracer_terrain()
        self.balle.tracer()
        self.joueur1.tracer()

        afficher_scores(self.scorej1)

if __name__ == "__main__":
    app = Foot_1_joueur()
    pyxel.run(app.update, app.draw)
