import pyxel
from .parametres import NB_EXECUTIONS_1_ACTION, RAYON_JOUEUR, VITESSE_JOUEUR, LIMITE_EST_TERRAIN, LIMITE_NORD_TERRAIN, LIMITE_OUEST_TERRAIN, LIMITE_SUD_TERRAIN
import math
from .balle import Balle
from typing import Any

class Joueur:
    def __init__(self, x: float, y: float, couleur: int, nom: str, GAUCHE: Any=None, DROITE: Any=None, HAUT: Any=None, BAS: Any=None):
        self.x, self.y = x, y
        self.vx, self.vy = 0, 0
        self.rayon = RAYON_JOUEUR
        self.couleur = couleur
        self.commande_haut = HAUT  # valeur 5
        self.commande_bas = BAS  # valeur 7
        self.commande_gauche = GAUCHE  # valeur 2
        self.commande_droite = DROITE  # valeur 3
        self.nom = nom
        self.nb_executions_action = 0

    def convert_consigne_action(self):
        gauche = pyxel.btn(self.commande_gauche)
        droite = pyxel.btn(self.commande_droite)
        haut = pyxel.btn(self.commande_haut)
        bas = pyxel.btn(self.commande_bas)

        if gauche and droite == haut == bas == 0:
            action = 1
        elif droite and gauche == haut == bas == 0:
            action = 2
        elif haut and gauche == droite == bas == 0:
            action = 3
        elif bas and gauche == droite == haut == 0:
            action = 4
        elif gauche and haut and droite == bas == 0:
            action = 5
        elif gauche and bas and droite == haut == 0:
            action = 6
        elif droite and haut and gauche == bas == 0:
            action = 7
        elif droite and bas and gauche == haut == 0:
            action = 8
        else:
            action = 9

        self.action = action

    def convert_action_vitesse(self):
        self.vx, self.vy = 0, 0
        vitesse_diag = math.sqrt(VITESSE_JOUEUR ** 2 / 2)

        if self.action == 1:
            self.vx = - VITESSE_JOUEUR
        elif self.action == 2:
            self.vx = VITESSE_JOUEUR
        elif self.action == 3:
            self.vy = - VITESSE_JOUEUR
        elif self.action == 4:
            self.vy = VITESSE_JOUEUR
        elif self.action == 5:
            self.vx, self.vy = - vitesse_diag, - vitesse_diag
        elif self.action == 6:
            self.vx, self.vy = - vitesse_diag, vitesse_diag
        elif self.action == 7:
            self.vx, self.vy = vitesse_diag, - vitesse_diag
        elif self.action == 8:
            self.vx, self.vy = vitesse_diag, vitesse_diag
        
    def deplacement(self, balle: Balle, joueurs=[]):
        self.nb_executions_action += 1
        if math.sqrt((self.x + self.vx - balle.x) ** 2 + (self.y + self.vy - balle.y) ** 2) > self.rayon + balle.rayon or math.sqrt((self.x - balle.x) ** 2 + (self.y - balle.y) ** 2) <= self.rayon + balle.rayon:
            # on permet aussi au joueur de se debloquer si il est coincé avec la balle (ce n'est pas considere comme une collision dans balle.verif_collisions)
            if math.sqrt((self.x - balle.x) ** 2 + (self.y - balle.y) ** 2) <= self.rayon + balle.rayon:
                JBx = balle.x - self.x
                JBy = balle.y - self.y
                JB = math.sqrt(JBx ** 2 + JBy ** 2)
                x1x = JBx / JB
                x1y = JBy / JB
                coef = 0
                dx = x1x * coef
                dy = x1y * coef
                while math.sqrt((JBx + dx) ** 2 + (JBy + dy) ** 2) <= self.rayon + balle.rayon:
                    coef += 0.1
                    dx = x1x * coef
                    dy = x1y * coef
                self.x -= dx
                self.y -= dy

            else:
                if LIMITE_OUEST_TERRAIN + self.rayon < self.x + self.vx < LIMITE_EST_TERRAIN - self.rayon:
                    self.x += self.vx
                if LIMITE_NORD_TERRAIN + self.rayon < self.y + self.vy < LIMITE_SUD_TERRAIN - self.rayon:
                    self.y += self.vy

            for joueur in joueurs:
                if math.sqrt((self.x - joueur.x) ** 2 + (self.y - joueur.y) ** 2) <= self.rayon + joueur.rayon:
                    JBx = joueur.x - self.x
                    JBy = joueur.y - self.y
                    JB = math.sqrt(JBx ** 2 + JBy ** 2)
                    x1x = JBx / JB
                    x1y = JBy / JB
                    coef = 0
                    dx = x1x * coef
                    dy = x1y * coef
                    while math.sqrt((JBx + dx) ** 2 + (JBy + dy) ** 2) <= self.rayon + joueur.rayon:
                        coef += 0.1
                        dx = x1x * coef
                        dy = x1y * coef
                    self.x -= dx
                    self.y -= dy

            if self.x + self.rayon > LIMITE_EST_TERRAIN:
                self.x = LIMITE_EST_TERRAIN - self.rayon - 1
            elif self.x - self.rayon < LIMITE_OUEST_TERRAIN:
                self.x = LIMITE_OUEST_TERRAIN + self.rayon + 1
            if self.y + self.rayon > LIMITE_SUD_TERRAIN:
                self.y = LIMITE_SUD_TERRAIN - self.rayon - 1
            elif self.y - self.rayon < LIMITE_NORD_TERRAIN:
                self.y = LIMITE_NORD_TERRAIN + self.rayon + 1

    def tracer(self):
        pyxel.circ(self.x, self.y, self.rayon, self.couleur)