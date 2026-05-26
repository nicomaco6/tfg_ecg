import numpy as np
import pandas as pd
import wfdb
from pathlib import Path

from metode_neurokit import deteccio_pics_r_neurokit
from metode_pan_tompkins import deteccio_pics_r_pan_tompkins
from metode_propi import deteccio_pics_r_propi


# ===============================
# CONFIGURACIÓ
# ===============================

DURADA_SEGMENT_S = 50
TOLERANCIA_MS = 50

RR_MIN_MS = 300
RR_MAX_MS = 2000
DESVIACIO_MAX_MEDIANA = 0.20

BASE_DIR = Path(__file__).resolve().parent
SORTIDA_EXCEL = BASE_DIR / "resultats_tfg.xlsx"


REGISTRES_MITBIH = [
    "100", "101", "102", "103", "104", "105", "106", "107", "108", "109",
    "111", "112", "113", "114", "115", "116", "117", "118", "119",
    "121", "122", "123", "124", "200", "201", "202", "203", "205",
    "207", "208", "209", "210", "212", "213", "214", "215", "217",
    "219", "220", "221", "222", "223", "228", "230", "231", "232",
    "233", "234"
]


SEGMENTS_BUTQDB = {

    "100001": {
        1: (198868, None),
        2: (1, None),
        3: (68061376, None)
    },

    "103001": {
        1: (28800001, None),
        2: (57617154, None),
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "103002": {
        1: (28800001, None),
        2: (58242890, None),
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "103003": {
        1: (28845376, None),
        2: (29410191, None),
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "104001": {
        1: (28800001, None),
        2: (57600001, None),
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "105001": {
        1: (47715156, None),
        2: (47323380, None),
        3: (1, None),
    },

    "111001": {
        1: (19199638, None),
        2: (1, None),
        3: (26430440, None),
    },

    "113001": {
        1: (29239124, None),
        2: (28890143, None),
        3: (36120000, None),
    },

    "114001": {
        1: (28800001, None),
        2: (12776017, None),
        3: (11273944, None),
    },

    "115001": {
        1: (28800001, None),
        2: (57600001, None),
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "118001": {
        1: (28800001, None),
        2: (57600001, None),
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "121001": {
        1: (28924667, None),
        2: (29031976, None),
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "122001": {
        1: (57600001, None),
        2: (58426794, None),
        3: (28800001, None),
    },

    "123001": {
        1: (28812663, None),
        2: (28926043, None),
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "124001": {
        1: (33700000, None),
        2: (28800001, None),
        3: (28892347, None),
    },

    "125001": {
        1: (28800001, None),
        # Classe 2: no hi ha cap segment >= 50 s
        # Classe 3: no hi ha cap segment >= 50 s
    },

    "126001": {
        1: (28800001, None),
        # Classe 2: no hi ha cap segment >= 50 s
        # Classe 3: no hi ha cap segment >= 50 s
    },
}


METODES = {
    "NeuroKit2": deteccio_pics_r_neurokit,
    "Pan-Tompkins": deteccio_pics_r_pan_tompkins,
    "Propi": deteccio_pics_r_propi,
}


# ===============================
# FUNCIONS GENERALS
# ===============================

def calcular_rr_hrv(pics_r, fs):
    rr = (np.diff(pics_r) / fs) * 1000

    if len(rr) > 1:
        sdrr = np.std(rr)
        rmssd_rr = np.sqrt(np.mean(np.diff(rr) ** 2))
    else:
        sdrr = np.nan
        rmssd_rr = np.nan

    return rr, sdrr, rmssd_rr


def filtrar_rr_a_nn(rr):
    rr = np.array(rr)

    if len(rr) == 0:
        return rr

    rr_filtrat = rr[(rr >= RR_MIN_MS) & (rr <= RR_MAX_MS)]

    if len(rr_filtrat) == 0:
        return rr_filtrat

    mediana = np.median(rr_filtrat)

    nn = rr_filtrat[
        np.abs(rr_filtrat - mediana) <= DESVIACIO_MAX_MEDIANA * mediana
    ]

    return nn


def calcular_hrv_intervals(intervals):
    if len(intervals) > 1:
        sdnn = np.std(intervals)
        rmssd_nn = np.sqrt(np.mean(np.diff(intervals) ** 2))
    else:
        sdnn = np.nan
        rmssd_nn = np.nan

    return sdnn, rmssd_nn


def calcular_f1(precisio, sensibilitat):
    if np.isnan(precisio) or np.isnan(sensibilitat):
        return np.nan

    if (precisio + sensibilitat) == 0:
        return np.nan

    return 2 * (precisio * sensibilitat) / (precisio + sensibilitat)


# ===============================
# MIT-BIH
# ===============================

def carregar_mitbih(registre):
    ruta = f"datasets/mitbih/{registre}"

    record = wfdb.rdrecord(ruta)
    ann = wfdb.rdann(ruta, "atr")

    senyal = record.p_signal
    fs = record.fs
    canals = record.sig_name

    canal_0 = canals[0] if len(canals) > 0 else ""
    canal_1 = canals[1] if len(canals) > 1 else ""

    if "MLII" in canals:
        index_canal = canals.index("MLII")
    else:
        index_canal = 0

    ecg = senyal[:, index_canal]
    canal_utilitzat = canals[index_canal]

    return ecg, fs, ann, canal_0, canal_1, canal_utilitzat


def obtenir_pics_reals(ann):
    simbols_batec = [
        "N", "L", "R", "A", "a", "J", "S",
        "V", "F", "e", "j", "E", "/", "f", "Q"
    ]

    mascara = np.array([s in simbols_batec for s in ann.symbol])
    pics_reals = ann.sample[mascara]

    return pics_reals


def calcular_metriques_deteccio(pics_detectats, pics_reals, fs):
    tolerancia_mostres = int((TOLERANCIA_MS / 1000) * fs)

    detectats_usats = np.zeros(len(pics_detectats), dtype=bool)

    tp = 0
    fn = 0

    for pic_real in pics_reals:
        diferencies = np.abs(pics_detectats - pic_real)

        candidats = np.where(
            (diferencies <= tolerancia_mostres) &
            (~detectats_usats)
        )[0]

        if len(candidats) > 0:
            millor = candidats[np.argmin(diferencies[candidats])]
            detectats_usats[millor] = True
            tp += 1
        else:
            fn += 1

    fp = np.sum(~detectats_usats)

    sensibilitat = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else np.nan
    precisio = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else np.nan
    f1 = calcular_f1(precisio, sensibilitat)

    return tp, fp, fn, sensibilitat, precisio, f1


def analitzar_mitbih():
    resultats = []

    for nom_metode, metode_deteccio in METODES.items():
        print(f"\nAnalitzant MIT-BIH amb {nom_metode}...")

        for registre in REGISTRES_MITBIH:
            try:
                ecg, fs, ann, canal_0, canal_1, canal_utilitzat = carregar_mitbih(registre)

                pics_detectats, _ = metode_deteccio(ecg, fs)
                pics_reals = obtenir_pics_reals(ann)

                tp, fp, fn, sensibilitat, precisio, f1 = calcular_metriques_deteccio(
                    pics_detectats,
                    pics_reals,
                    fs
                )

                rr_detectats, sdrr_detectats, rmssd_rr_detectats = calcular_rr_hrv(
                    pics_detectats,
                    fs
                )

                nn_detectats = filtrar_rr_a_nn(rr_detectats)
                sdnn_detectats, rmssd_nn_detectats = calcular_hrv_intervals(nn_detectats)

                rr_reals, sdrr_reals, rmssd_rr_reals = calcular_rr_hrv(
                    pics_reals,
                    fs
                )

                nn_reals = filtrar_rr_a_nn(rr_reals)
                sdnn_reals, rmssd_nn_reals = calcular_hrv_intervals(nn_reals)

                resultats.append({
                    "dataset": "MIT-BIH",
                    "metode": nom_metode,
                    "registre": registre,
                    "fs_Hz": fs,
                    "canal_0": canal_0,
                    "canal_1": canal_1,
                    "canal_utilitzat": canal_utilitzat,
                    "pics_detectats": len(pics_detectats),
                    "pics_reals": len(pics_reals),
                    "TP": tp,
                    "FP": fp,
                    "FN": fn,
                    "precisio_%": precisio,
                    "sensibilitat_%": sensibilitat,
                    "f1_score_%": f1,
                    "num_RR_detectats": len(rr_detectats),
                    "num_NN_detectats": len(nn_detectats),
                    "SDRR_detectats_ms": sdrr_detectats,
                    "RMSSD_RR_detectats_ms": rmssd_rr_detectats,
                    "SDNN_detectats_ms": sdnn_detectats,
                    "RMSSD_NN_detectats_ms": rmssd_nn_detectats,
                    "num_RR_reals": len(rr_reals),
                    "num_NN_reals": len(nn_reals),
                    "SDRR_reals_ms": sdrr_reals,
                    "RMSSD_RR_reals_ms": rmssd_rr_reals,
                    "SDNN_reals_ms": sdnn_reals,
                    "RMSSD_NN_reals_ms": rmssd_nn_reals,
                })

                print(f"  {registre} OK")

            except Exception as e:
                print(f"  Error MIT-BIH registre {registre} amb {nom_metode}: {e}")

                resultats.append({
                    "dataset": "MIT-BIH",
                    "metode": nom_metode,
                    "registre": registre,
                    "error": str(e)
                })

    return resultats


# ===============================
# BUT QDB
# ===============================

def carregar_butqdb(registre_id):
    ruta = f"datasets/butqdb/{registre_id}/{registre_id}_ECG"

    record = wfdb.rdrecord(ruta)

    ecg = record.p_signal[:, 0]
    fs = record.fs

    return ecg, fs


def analitzar_butqdb():
    resultats = []

    for nom_metode, metode_deteccio in METODES.items():
        print(f"\nAnalitzant BUT QDB amb {nom_metode}...")

        for registre_id, classes in SEGMENTS_BUTQDB.items():
            try:
                ecg, fs = carregar_butqdb(registre_id)

                for num_classe, (start, end) in classes.items():

                    if end is None:
                        end_segment = start + int(DURADA_SEGMENT_S * fs)
                    else:
                        end_segment = end

                    end_segment = min(len(ecg), end_segment)

                    ecg_segment = ecg[start:end_segment]

                    if len(ecg_segment) == 0:
                        print(f"  Segment buit {registre_id} classe {num_classe}")
                        continue

                    pics_r, _ = metode_deteccio(ecg_segment, fs)

                    rr, sdrr, rmssd_rr = calcular_rr_hrv(pics_r, fs)

                    nn = filtrar_rr_a_nn(rr)
                    sdnn, rmssd_nn = calcular_hrv_intervals(nn)

                    resultats.append({
                        "dataset": "BUT QDB",
                        "metode": nom_metode,
                        "registre": registre_id,
                        "classe": num_classe,
                        "fs_Hz": fs,
                        "start": start,
                        "end": end_segment,
                        "durada_s": len(ecg_segment) / fs,
                        "pics_detectats": len(pics_r),
                        "num_RR": len(rr),
                        "num_NN": len(nn),
                        "RR_min_ms": np.min(rr) if len(rr) > 0 else np.nan,
                        "RR_max_ms": np.max(rr) if len(rr) > 0 else np.nan,
                        "RR_mitja_ms": np.mean(rr) if len(rr) > 0 else np.nan,
                        "NN_min_ms": np.min(nn) if len(nn) > 0 else np.nan,
                        "NN_max_ms": np.max(nn) if len(nn) > 0 else np.nan,
                        "NN_mitja_ms": np.mean(nn) if len(nn) > 0 else np.nan,
                        "SDRR_ms": sdrr,
                        "RMSSD_RR_ms": rmssd_rr,
                        "SDNN_ms": sdnn,
                        "RMSSD_NN_ms": rmssd_nn,
                    })

                    print(f"  {registre_id} classe {num_classe} OK")

            except Exception as e:
                print(f"  Error BUT QDB registre {registre_id} amb {nom_metode}: {e}")

                resultats.append({
                    "dataset": "BUT QDB",
                    "metode": nom_metode,
                    "registre": registre_id,
                    "error": str(e)
                })

    return resultats


# ===============================
# EXPORTACIÓ
# ===============================

def crear_resums(df_mitbih, df_butqdb):
    df_mitbih_valid = df_mitbih[df_mitbih.get("error").isna()] if "error" in df_mitbih.columns else df_mitbih

    resum_mitbih = df_mitbih_valid.groupby("metode").agg({
        "precisio_%": ["mean", "std"],
        "sensibilitat_%": ["mean", "std"],
        "f1_score_%": ["mean", "std"],
        "SDRR_detectats_ms": ["mean", "std"],
        "SDNN_detectats_ms": ["mean", "std"],
        "RMSSD_RR_detectats_ms": ["mean", "std"],
        "RMSSD_NN_detectats_ms": ["mean", "std"],
    })

    df_butqdb_valid = df_butqdb[df_butqdb.get("error").isna()] if "error" in df_butqdb.columns else df_butqdb

    resum_butqdb = df_butqdb_valid.groupby(["metode", "classe"]).agg({
        "SDRR_ms": ["mean", "std"],
        "SDNN_ms": ["mean", "std"],
        "RMSSD_RR_ms": ["mean", "std"],
        "RMSSD_NN_ms": ["mean", "std"],
        "num_RR": ["mean"],
        "num_NN": ["mean"],
    })

    return resum_mitbih, resum_butqdb


def exportar_excel():
    resultats_mitbih = analitzar_mitbih()
    resultats_butqdb = analitzar_butqdb()

    df_mitbih = pd.DataFrame(resultats_mitbih)
    df_butqdb = pd.DataFrame(resultats_butqdb)

    resum_mitbih, resum_butqdb = crear_resums(df_mitbih, df_butqdb)

    with pd.ExcelWriter(SORTIDA_EXCEL, engine="openpyxl") as writer:
        df_mitbih.to_excel(writer, sheet_name="MIT-BIH", index=False)
        df_butqdb.to_excel(writer, sheet_name="BUT-QDB", index=False)
        resum_mitbih.to_excel(writer, sheet_name="Resum MIT-BIH")
        resum_butqdb.to_excel(writer, sheet_name="Resum BUT-QDB")

    print("\n================================")
    print("EXPORTACIÓ COMPLETADA")
    print("Fitxer generat:", SORTIDA_EXCEL)
    print("================================")


# ===============================
# EXECUCIÓ
# ===============================

if __name__ == "__main__":
    exportar_excel()