import numpy as np
import neurokit2 as nk

#Detecta els pics R utilitzant NeuroKit2

def deteccio_pics_r_neurokit(ecg, fs): 
#ecg: array 1D amb el senyal ECG
#fs: freqüència de mostreig    

    try:
        ecg_clean = nk.ecg_clean(ecg, sampling_rate=fs)
        _, info = nk.ecg_peaks(ecg_clean, sampling_rate=fs) # la funció retorna (signals, info). Només ens interessa 'info', que conté els índexs dels pics R detectats entre altres coses
        pics_r = info["ECG_R_Peaks"] # del diccionari només volem l'apartat que indica els índexs dels pics R detectats

    except Exception as e:
        print("Error en detecció NeuroKit:", e)
        pics_r = np.array([])
        ecg_clean = ecg


    return pics_r, ecg_clean  #pics_r: array amb els índexs dels pics R detectats
                              #ecg_clean: senyal filtrat

