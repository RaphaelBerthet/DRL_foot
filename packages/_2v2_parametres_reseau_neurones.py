NB_PARTIES = 1000000
NB_ITERATIONS_1_PARTIE = 200
p_debut = 0.6
p_fin = 0.6
TAILLE_STATE = 25
NB_ACTIONS_POSSIBLES = 81  # on suppose les actions numérotées 1, 2, ... NB_ACTIONS_POSSIBLES
NB_SAMPLES_MAX = 30000
NB_SAMPLES_DEBUT_ENTRAINEMENT = 3000
TAILLE_BATCHS = 128
NB_ENTRAINEMENT_BATCH = 4
gamma = 0.99
learning_rate = 0.0001
ACTU_W_TARGET = 1000  # tous les ... majs du reseau
PERIODE_STOCKAGE_PC = 480000 // ACTU_W_TARGET  # toutes les ... majs du reseau
NB_NEURONES_LAYER1 = 254
NB_NEURONES_LAYER2 = 128
MAX_NORME_GRADIENT = 10  # norme 2
DELTA_HUBER_LOSS = 1

conversions_actions_J2 = {
    9 : 9,
    1 : 2,
    2 : 1,
    3 : 4,
    4 : 3,
    5 : 8,
    6 : 7,
    7 : 6,
    8 : 5
}