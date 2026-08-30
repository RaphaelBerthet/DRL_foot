from .parametres import VITESSE_JOUEUR, COULEUR_BALLE, RAYON_BALLE, COEF_FROT_FLUIDE, FROT_SEC, LIMITE_EST_CAGE_DROITE, LIMITE_EST_TERRAIN, LIMITE_NORD_CAGE, LIMITE_NORD_TERRAIN, LIMITE_OUEST_CAGE_GAUCHE, LIMITE_OUEST_TERRAIN, LIMITE_SUD_CAGE, LIMITE_SUD_TERRAIN
import math
import pyxel
import random
from collections import Counter

class Balle:
    def __init__(self, x: float, y: float, vitesse_aleatoire_debut: bool=False):
        self.x, self.y = x, y
        self.rayon = RAYON_BALLE
        self.possession = ''
        self.balle_tiree = False
        if vitesse_aleatoire_debut:
            angle = random.randint(0, 359) * math.pi / 180
            self.vx = math.cos(angle) * VITESSE_JOUEUR / 2
            self.vy = math.sin(angle) * VITESSE_JOUEUR / 2
        else:
            self.vx = 0
            self.vy = 0

    def verif_collisions(self, joueurs):  # maj de la vitesse
        self.balle_tiree = False
        for joueur in joueurs:
            joueur.tir = False
        Fx, Fy = 0, 0
        c = 0
        joueur_possession = []
        for joueur in joueurs:
            if math.sqrt((joueur.x + joueur.vx - self.x - self.vx) ** 2 + (joueur.y + joueur.vy - self.y - self.vy) ** 2) <= self.rayon + joueur.rayon and not math.sqrt((joueur.x - self.x) ** 2 + (joueur.y - self.y) ** 2) <= self.rayon + joueur.rayon:
                # on le compte uniquement si la balle est pas dans l'obstacle
                OBx = self.x - joueur.x
                OBy = self.y - joueur.y
                OB = math.sqrt(OBx ** 2 + OBy ** 2)
                Fx += VITESSE_JOUEUR * OBx / OB
                Fy += VITESSE_JOUEUR * OBy / OB
                c += 1
                joueur_possession.append(joueur.nom)
                self.balle_tiree = True
                joueur.tir = True

        if c == 1:
            ## 1 seul joueur a tapé la balle ie il a la possession
            self.possession = joueur_possession[0]
        elif c > 1:
            if len(Counter(joueur_possession).keys()) == 1:
                self.possession = joueur_possession[0]
            else:
                self.possession = ''

        self.vx += Fx * 2
        self.vy += Fy * 2

        if LIMITE_NORD_TERRAIN + self.rayon > self.y + self.vy or (LIMITE_NORD_CAGE + self.rayon > self.y + self.vy and (self.x + self.vx - self.rayon < LIMITE_OUEST_TERRAIN or self.x + self.vx + self.rayon > LIMITE_EST_TERRAIN)):
            self.vy = abs(self.vy)
        elif self.y + self.vy > LIMITE_SUD_TERRAIN - self.rayon or (LIMITE_SUD_CAGE - self.rayon < self.y + self.vy and (self.x + self.vx - self.rayon < LIMITE_OUEST_TERRAIN or self.x + self.vx + self.rayon > LIMITE_EST_TERRAIN)):
            self.vy = - abs(self.vy)

        if (LIMITE_NORD_CAGE + self.rayon <= self.y + self.vy <= LIMITE_SUD_CAGE - self.rayon and self.x + self.vx - self.rayon < LIMITE_OUEST_CAGE_GAUCHE) or (not (LIMITE_NORD_CAGE + self.rayon <= self.y + self.vy <= LIMITE_SUD_CAGE - self.rayon) and self.x + self.vx - self.rayon < LIMITE_OUEST_TERRAIN):
            self.vx = abs(self.vx)
        elif (LIMITE_NORD_CAGE + self.rayon <= self.y + self.vy <= LIMITE_SUD_CAGE - self.rayon and self.x + self.vx + self.rayon > LIMITE_EST_CAGE_DROITE) or (not (LIMITE_NORD_CAGE + self.rayon <= self.y + self.vy <= LIMITE_SUD_CAGE - self.rayon) and self.x + self.vx + self.rayon > LIMITE_EST_TERRAIN):
            self.vx = - abs(self.vx) 



    def deplacement(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 1 - COEF_FROT_FLUIDE
        self.vy *= 1 - COEF_FROT_FLUIDE
        if self.vx ** 2 + self.vy ** 2 <= FROT_SEC ** 2:
            self.vx = 0
            self.vy = 0
            self.possession = ''

    def actu_score1(self, score: int):
        if self.x - self.rayon >= LIMITE_EST_TERRAIN and LIMITE_NORD_CAGE + self.rayon <= self.y <= LIMITE_SUD_CAGE - self.rayon:
            score += 1
        return score

    def actu_score2(self, score: int):
        if self.x + self.rayon <= LIMITE_OUEST_TERRAIN and LIMITE_NORD_CAGE + self.rayon <= self.y <= LIMITE_SUD_CAGE - self.rayon:
            score += 1
        return score

    def tracer(self):
        pyxel.circ(self.x, self.y, self.rayon, COULEUR_BALLE)