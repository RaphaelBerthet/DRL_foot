NB_PARTIES = 10000000
NB_ITERATIONS_1_PARTIE = 1000
p_debut = 0.2
p_fin = 0.1
TAILLE_STATE = 24
NB_ACTIONS_POSSIBLES = 81  # on suppose les actions numérotées 1, 2, ... NB_ACTIONS_POSSIBLES
NB_SAMPLES_MAX = 600000
NB_SAMPLES_DEBUT_ENTRAINEMENT = 10000
TAILLE_BATCHS = 400
NB_ENTRAINEMENT_BATCH = 1
gamma = 0.95
learning_rate = 0.0001
ACTU_W_TARGET = 500  # tous les ... majs du reseau
PERIODE_STOCKAGE_PC = 480000 // ACTU_W_TARGET  # toutes les ... majs du reseau
NB_NEURONES_LAYER1 = 256
NB_NEURONES_LAYER2 = 256
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