import pyxel
from packages.parametres import *
from packages.tracer_terrain import tracer_terrain
from packages.balle import Balle
from packages.joueur import Joueur
from packages.affichage_scores import afficher_scores
from packages.build_state import build_state_foot_2v2
from packages._2v2_parametres_reseau_neurones import TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2
from packages._2v2_entrainement_reseau_neurones import Reseau_neurones
import numpy as np
import random
import math

class Foot_2v2:
    def __init__(self):
        cote = random.choice([0, 100])
        R = 50
        teta = random.randint(0, 359) * math.pi / 180
        self.balle = Balle(LONGUEUR // 2 - 50 + math.cos(teta) * R + cote, LARGEUR // 2 + math.sin(teta) * R)        
        self.scorej1 = 0
        self.scorej2 = 0
        self.reseau_neurones_J1a = Reseau_neurones("reseau_neurones_foot_2v2_J1a.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
        self.reseau_neurones_J2a = Reseau_neurones("reseau_neurones_foot_2v2_J2a.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
        self.reseau_neurones_J1b = Reseau_neurones("reseau_neurones_foot_2v2_J1b.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)
        self.reseau_neurones_J2b = Reseau_neurones("reseau_neurones_foot_2v2_J2b.npz", TAILLE_STATE, NB_ACTIONS_POSSIBLES, NB_NEURONES_LAYER1, NB_NEURONES_LAYER2)

        pyxel.init(LONGUEUR, LARGEUR, title=TITRE)
        pyxel.mouse(True)
        self.joueur1a = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1')
        self.joueur2a = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2  - 50, COULEUR_J2, 'joueur2')
        self.joueur1b = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1')
        self.joueur2b = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2')


    def update(self):
        if self.joueur1a.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
            state_J1a = build_state_foot_2v2(TAILLE_STATE, self, app.joueur1a, app.joueur1b, app.joueur2a, app.joueur2b)
            state_J2a = build_state_foot_2v2(TAILLE_STATE, self, app.joueur2a, app.joueur2b, app.joueur1a, app.joueur1b)
            self.joueur1a.action = int(np.argmax(self.reseau_neurones_J1a.calcul_couche_sortie(state_J1a))) + 1
            self.joueur2a.action = int(np.argmax(self.reseau_neurones_J2a.calcul_couche_sortie(state_J2a))) + 1
            self.joueur1a.convert_action_vitesse()
            self.joueur2a.convert_action_vitesse()

            state_J1b = build_state_foot_2v2(TAILLE_STATE, self, app.joueur1b, app.joueur1a, app.joueur2a, app.joueur2b)
            state_J2b = build_state_foot_2v2(TAILLE_STATE, self, app.joueur2b, app.joueur2a, app.joueur1a, app.joueur1b)
            self.joueur1b.action = int(np.argmax(self.reseau_neurones_J1b.calcul_couche_sortie(state_J1b))) + 1
            self.joueur2b.action = int(np.argmax(self.reseau_neurones_J2b.calcul_couche_sortie(state_J2b))) + 1
            self.joueur1b.convert_action_vitesse()
            self.joueur2b.convert_action_vitesse()
   
        self.balle.verif_collisions([self.joueur1a, self.joueur2a, self.joueur1b, self.joueur2b])

        self.balle.deplacement()
        self.joueur1a.deplacement(self.balle, [self.joueur2a, self.joueur2b, self.joueur1b])
        self.joueur2a.deplacement(self.balle, [self.joueur1a, self.joueur1b, self.joueur2b])
        self.joueur1b.deplacement(self.balle, [self.joueur2a, self.joueur2b, self.joueur1a])
        self.joueur2b.deplacement(self.balle, [self.joueur1a, self.joueur1b, self.joueur2a])

        score = self.balle.actu_score1(self.scorej1)
        if score != self.scorej1:
            self.scorej1 = score
            cote = random.choice([0, 100])
            R = 50
            teta = random.randint(0, 359) * math.pi / 180
            self.balle = Balle(LONGUEUR // 2 - 50 + math.cos(teta) * R + cote, LARGEUR // 2 + math.sin(teta) * R)
            self.joueur1a = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1')
            self.joueur2a = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2  - 50, COULEUR_J2, 'joueur2')
            self.joueur1b = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1')
            self.joueur2b = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2')


        score = self.balle.actu_score2(self.scorej2)
        if score != self.scorej2:
            self.scorej2 = score
            cote = random.choice([0, 100])
            R = 50
            teta = random.randint(0, 359) * math.pi / 180
            self.balle = Balle(LONGUEUR // 2 - 50 + math.cos(teta) * R + cote, LARGEUR // 2 + math.sin(teta) * R)
            self.joueur1a = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1')
            self.joueur2a = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2  - 50, COULEUR_J2, 'joueur2')
            self.joueur1b = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1')
            self.joueur2b = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2')

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
