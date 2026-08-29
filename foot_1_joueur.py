import pyxel
from packages.parametres import *
from packages.tracer_terrain import tracer_terrain
from packages.balle import Balle
from packages.joueur import Joueur
from packages.affichage_scores import afficher_scores
import random
import math

class Foot_1_joueur:
    def __init__(self, utiliser_pyxel=False):
        # on place la balle sur un cercle autour du joueur
        R = random.randint(50, 100)
        teta = random.randint(0, 359) * math.pi / 180
        self.balle = Balle(LONGUEUR // 2 - 50 + math.cos(teta) * R, LARGEUR // 2 + math.sin(teta) * R)
        self.utiliser_pyxel = utiliser_pyxel
        self.scorej1 = 0
        self.c = 0
        if utiliser_pyxel:
            pyxel.init(LONGUEUR, LARGEUR, title=TITRE)
            pyxel.mouse(True)
            self.joueur1 = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2, COULEUR_J1, 'joueur1', pyxel.KEY_Q, pyxel.KEY_D, pyxel.KEY_Z, pyxel.KEY_S)
        else:
            self.joueur1 = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2, COULEUR_J1, 'joueur1')


    def update(self):
        self.c += 1
        if self.c % 100 == 0:
            print(self.c)

        if self.joueur1.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
            self.joueur1.convert_consigne_action()
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
            if self.utiliser_pyxel:
                self.joueur1 = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2, COULEUR_J1, 'joueur1', pyxel.KEY_Q, pyxel.KEY_D, pyxel.KEY_Z, pyxel.KEY_S)
            else:
                self.joueur1 = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2, COULEUR_J1, 'joueur1')

    def draw(self):
        pyxel.cls(COULEUR_BORD)

        tracer_terrain()
        self.balle.tracer()
        self.joueur1.tracer()

        afficher_scores(self.scorej1)

if __name__ == "__main__":
    app = Foot_1_joueur(True)
    pyxel.run(app.update, app.draw)

