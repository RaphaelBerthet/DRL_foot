import pyxel
from packages.parametres import *
from packages.tracer_terrain import tracer_terrain
from packages.balle import Balle
from packages.joueur import Joueur
from packages.affichage_scores import afficher_scores
import random
import math

class Foot_2v2:
    def __init__(self, afficher_pyxel: bool=False):
        cote = random.choice([0, 100])
        R = 50
        teta = random.randint(0, 359) * math.pi / 180
        self.balle = Balle(LONGUEUR // 2 - 50 + math.cos(teta) * R + cote, LARGEUR // 2 + math.sin(teta) * R)
        self.scorej1 = 0
        self.scorej2 = 0
        self.afficher_pyxel = afficher_pyxel
        if self.afficher_pyxel:
            pyxel.init(LONGUEUR, LARGEUR, title=TITRE)
            pyxel.mouse(True)
            self.joueur1a = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1', pyxel.KEY_Q, pyxel.KEY_D, pyxel.KEY_Z, pyxel.KEY_S)
            self.joueur2a = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 - 50, COULEUR_J2, 'joueur2', pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_UP, pyxel.KEY_DOWN)
            self.joueur1b = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1', pyxel.KEY_Q, pyxel.KEY_D, pyxel.KEY_Z, pyxel.KEY_S)
            self.joueur2b = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2', pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_UP, pyxel.KEY_DOWN)
        else:
            self.joueur1a = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1')
            self.joueur2a = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2  - 50, COULEUR_J2, 'joueur2')
            self.joueur1b = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1')
            self.joueur2b = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2')

    def update(self):
     
        if self.joueur1a.nb_executions_action % NB_EXECUTIONS_1_ACTION == 0:
            self.joueur1a.convert_consigne_action()
            self.joueur1a.convert_action_vitesse()
            self.joueur2a.convert_consigne_action()
            self.joueur2a.convert_action_vitesse()
            self.joueur1b.convert_consigne_action()
            self.joueur1b.convert_action_vitesse()
            self.joueur2b.convert_consigne_action()
            self.joueur2b.convert_action_vitesse()

        self.balle.verif_collisions([self.joueur1a, self.joueur2a, self.joueur1b, self.joueur2b])

        self.balle.deplacement()
        self.joueur1a.deplacement(self.balle, [self.joueur2a, self.joueur1b, self.joueur2b])
        self.joueur2a.deplacement(self.balle, [self.joueur1a, self.joueur1b, self.joueur2b])
        self.joueur1b.deplacement(self.balle, [self.joueur2a, self.joueur1a, self.joueur2b])
        self.joueur2b.deplacement(self.balle, [self.joueur1a, self.joueur1b, self.joueur2a])

        score = self.balle.actu_score1(self.scorej1)
        if score != self.scorej1:
            self.scorej1 = score
            cote = random.choice([0, 100])
            R = 50
            teta = random.randint(0, 359) * math.pi / 180
            self.balle = Balle(LONGUEUR // 2 - 50 + math.cos(teta) * R + cote, LARGEUR // 2 + math.sin(teta) * R)
            if self.afficher_pyxel:
                self.joueur1a = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1', pyxel.KEY_Q, pyxel.KEY_D, pyxel.KEY_Z, pyxel.KEY_S)
                self.joueur2a = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 - 50, COULEUR_J2, 'joueur2', pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_UP, pyxel.KEY_DOWN)
                self.joueur1b = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1', pyxel.KEY_Q, pyxel.KEY_D, pyxel.KEY_Z, pyxel.KEY_S)
                self.joueur2b = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2', pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_UP, pyxel.KEY_DOWN)
            else:
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
            if self.afficher_pyxel:
                self.joueur1a = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 - 50, COULEUR_J1, 'joueur1', pyxel.KEY_Q, pyxel.KEY_D, pyxel.KEY_Z, pyxel.KEY_S)
                self.joueur2a = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 - 50, COULEUR_J2, 'joueur2', pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_UP, pyxel.KEY_DOWN)
                self.joueur1b = Joueur(LONGUEUR / 2 - 50, LARGEUR / 2 + 50, COULEUR_J1, 'joueur1', pyxel.KEY_Q, pyxel.KEY_D, pyxel.KEY_Z, pyxel.KEY_S)
                self.joueur2b = Joueur(LONGUEUR / 2 + 50, LARGEUR / 2 + 50, COULEUR_J2, 'joueur2', pyxel.KEY_LEFT, pyxel.KEY_RIGHT, pyxel.KEY_UP, pyxel.KEY_DOWN)
            else:
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
    app = Foot_2v2(True)
    pyxel.run(app.update, app.draw)
