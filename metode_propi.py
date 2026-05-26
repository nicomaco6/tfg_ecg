import numpy as np
from scipy.signal import butter, filtfilt

FREQ_BAIXA = 5
FREQ_ALTA = 20
ORDRE = 2

DISTANCIA_MINIMA = 0.25 
FACTOR_LLINDAR = 1.5 
FINESTRA_CERCA = 0.12 


def filtre_passabanda(ecg, fs):
    nyquist = fs / 2
    low = FREQ_BAIXA / nyquist
    high = FREQ_ALTA / nyquist

    b, a = butter(ORDRE, [low, high], btype="band")
    ecg_filtrat = filtfilt(b, a, ecg)

    return ecg_filtrat


def normalitzar_senyal(senyal):
    desviacio = np.std(senyal)

    if desviacio == 0:
        return senyal - np.mean(senyal)

    senyal_norm = (senyal - np.mean(senyal)) / desviacio

    return senyal_norm


def calcular_llindar_adaptatiu(senyal_deteccio):
    mitjana = np.mean(senyal_deteccio)
    desviacio = np.std(senyal_deteccio)

    llindar = mitjana + FACTOR_LLINDAR * desviacio

    return llindar


def deteccio_pics_r_propi(ecg, fs):
    """
    Detecta pics R mitjançant:
    filtratge, normalització, valor absolut, llindar adaptatiu,
    màxims locals i distància mínima.
    """

    try:
        # 1. Filtratge passabanda
        ecg_filtrat = filtre_passabanda(ecg, fs)

        # 2. Normalització per evitar problemes d'escala entre datasets
        ecg_norm = normalitzar_senyal(ecg_filtrat)

        # 3. Valor absolut per detectar QRS positius o negatius
        senyal_deteccio = np.abs(ecg_norm)

        # 4. Càlcul del llindar adaptatiu
        llindar = calcular_llindar_adaptatiu(senyal_deteccio)

        # 5. Distància mínima entre pics
        distancia_minima_mostres = max(1, int(DISTANCIA_MINIMA * fs))
        finestra_cerca = max(1, int(FINESTRA_CERCA * fs))

        pics_r = []
        ultim_pic = -distancia_minima_mostres

        # 6. Recorregut mostra a mostra buscant màxims locals
        for i in range(1, len(senyal_deteccio) - 1):
            actual = senyal_deteccio[i]
            anterior = senyal_deteccio[i - 1]
            seguent = senyal_deteccio[i + 1]

            es_maxim_local = actual > anterior and actual > seguent
            supera_llindar = actual > llindar
            prou_lluny = (i - ultim_pic) >= distancia_minima_mostres

            if es_maxim_local and supera_llindar and prou_lluny:
                inici = max(0, i - finestra_cerca)
                final = min(len(senyal_deteccio), i + finestra_cerca)

                pic_local = np.argmax(senyal_deteccio[inici:final])
                pic_refinat = inici + pic_local

                pics_r.append(pic_refinat)
                ultim_pic = pic_refinat

        pics_r = np.array(pics_r, dtype=int)

    except Exception as e:
        print("Error en detecció amb mètode propi:", e)
        pics_r = np.array([])
        ecg_filtrat = ecg

    return pics_r, ecg_filtrat 