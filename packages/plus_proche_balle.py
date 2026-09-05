from .parametres import COEF_FROT_FLUIDE, VITESSE_JOUEUR
import math

def distance_joueur_balle(nb_iterations, J, balle):
    facteur = (1 - (1 - COEF_FROT_FLUIDE) ** nb_iterations) / COEF_FROT_FLUIDE
    return math.sqrt((balle.x + balle.vx * facteur - J.x) ** 2 + (balle.y + balle.vy * facteur - J.y) ** 2)

def nombre_iterations_necessaires(J, balle):

    def atteint(n):
        return (
            distance_joueur_balle(n, J, balle)
            - J.rayon
            - balle.rayon
            < VITESSE_JOUEUR * n
        )

    # Recherche d'une borne supérieure
    n = 1

    while not atteint(n):
        n *= 2

    # On sait maintenant que l'interception est possible à n
    borne_haute = n
    borne_basse = n // 2

    # Recherche dichotomique
    while borne_haute - borne_basse > 1:
        milieu = (borne_basse + borne_haute) // 2

        if atteint(milieu):
            borne_haute = milieu
        else:
            borne_basse = milieu

    return borne_haute

def plus_proche_balle(Ja, Jb, balle):
    Ta = nombre_iterations_necessaires(Ja, balle)
    Tb = nombre_iterations_necessaires(Jb, balle)
    if Ta < Tb:
        return 'joueur a', Ta, Tb
    else:
        return 'joueur b', Tb, Ta

