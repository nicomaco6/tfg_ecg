import numpy as np
from scipy.signal import butter, filtfilt, find_peaks

FREQ_BAIXA = 5
FREQ_ALTA = 15
ORDRE = 2

FINESTRA_INTEGRACIO = 0.15 # segons. Valor típic per a la finestra d'integració en el mètode Pan-Tompkins.
DISTANCIA_MINIMA = 0.25
FINESTRA_CERCA = 0.08
FACTOR_LLINDAR = 0.5

def filtre_passabanda(ecg, fs):
    nyquist = fs / 2
    low = FREQ_BAIXA / nyquist
    high = FREQ_ALTA / nyquist

    b, a = butter(ORDRE, [low, high], btype="band")
    ecg_filtrat = filtfilt(b, a, ecg)

    return ecg_filtrat


def deteccio_pics_r_pan_tompkins(ecg, fs):
    
#Detecta pics R utilitzant una implementació simplificada del mètode Pan-Tompkins.
    

    try:
        # 1. Filtratge passabanda
        ecg_filtrat = filtre_passabanda(ecg, fs)

        # 2. Derivada
        derivada = np.diff(ecg_filtrat, prepend=ecg_filtrat[0]) 

        # 3. Quadrat
        quadrat = derivada ** 2

        # 4. Integració amb finestra mòbil
        finestra = int(FINESTRA_INTEGRACIO * fs)  # 150 ms
        kernel = np.ones(finestra) / finestra
        integrat = np.convolve(quadrat, kernel, mode="same") 

        # 5. Detecció de pics
        distancia_minima = int(DISTANCIA_MINIMA * fs)  # 250 ms
        llindar = np.mean(integrat) + FACTOR_LLINDAR * np.std(integrat)

        pics_integrats, _ = find_peaks(
            integrat,
            height=llindar,
            distance=distancia_minima
        )

        # 6. Reajustar el pic al màxim real del QRS en el senyal filtrat
        pics_r = []

        finestra_cerca = int(FINESTRA_CERCA * fs)  # +-80 ms

        for pic in pics_integrats:
            inici = max(0, pic - finestra_cerca)
            final = min(len(ecg_filtrat), pic + finestra_cerca)

            if final > inici:
                pic_local = np.argmax(ecg_filtrat[inici:final])
                pics_r.append(inici + pic_local)

        pics_r = np.array(pics_r, dtype=int)

    except Exception as e:
        print("Error en detecció Pan-Tompkins:", e)
        pics_r = np.array([])

    return pics_r, ecg_filtrat #canviar entregat pel punt del processament que es vulgui mostrar.
