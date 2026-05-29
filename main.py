# Abans d'executar el programa, instal·lar les dependències:
# pip install -r requirements.txt

import numpy as np
import matplotlib.pyplot as plt
import wfdb
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MaxNLocator

from metode_neurokit import deteccio_pics_r_neurokit
from metode_pan_tompkins import deteccio_pics_r_pan_tompkins
from metode_propi import deteccio_pics_r_propi


BASE_DIR = Path(__file__).resolve().parent

DURADA_SEGMENT_S = 15
TOLERANCIA_MS = 50

RR_MIN_MS = 300
RR_MAX_MS = 2000
DESVIACIO_MAX_MEDIANA = 0.20


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


# ===============================
# FUNCIONS GENERALS
# ===============================

def seleccionar_configuracio():
    resultat = {}

    # ===============================
    # FINESTRA PRINCIPAL
    # ===============================

    finestra = tk.Tk()
    finestra.title("Sistema d'anàlisi ECG")
    finestra.configure(bg="#0f172a")

    try:
        finestra.state("zoomed")  # Windows
    except Exception:
        amplada = finestra.winfo_screenwidth()
        altura = finestra.winfo_screenheight()
        finestra.geometry(f"{amplada}x{altura}+0+0")

    finestra.minsize(1000, 650)

    # ===============================
    # ESTIL
    # ===============================

    estil = ttk.Style()
    estil.theme_use("clam")

    estil.configure(
        "Modern.TCombobox",
        fieldbackground="#ffffff",
        background="#ffffff",
        foreground="#111827",
        arrowcolor="#2563eb",
        bordercolor="#cbd5e1",
        lightcolor="#cbd5e1",
        darkcolor="#cbd5e1",
        padding=8
    )

    finestra.option_add("*TCombobox*Listbox.font", ("Segoe UI", 11))

    # ===============================
    # FUNCIONS AUXILIARS
    # ===============================

    def sortir():
        resultat["cancelat"] = True
        finestra.destroy()

    def crear_label(parent, text, row):
        tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#334155"
        ).grid(row=row, column=0, sticky="w", pady=(0, 7))

    def crear_combo(parent, values, row, valor_inicial=0):
        combo = ttk.Combobox(
            parent,
            values=values,
            state="readonly",
            width=34,
            font=("Segoe UI", 12),
            style="Modern.TCombobox"
        )
        combo.current(valor_inicial)
        combo.grid(row=row, column=0, sticky="ew", pady=(0, 24), ipady=5)
        return combo

    def aplicar_hover(boto, color_normal, color_hover):
        boto.bind("<Enter>", lambda event: boto.config(bg=color_hover))
        boto.bind("<Leave>", lambda event: boto.config(bg=color_normal))

    finestra.protocol("WM_DELETE_WINDOW", sortir)
    finestra.bind("<Escape>", lambda event: sortir())

    # ===============================
    # CONTENIDOR GENERAL
    # ===============================

    contenidor = tk.Frame(finestra, bg="#0f172a")
    contenidor.pack(expand=True, fill="both")

    contenidor.grid_rowconfigure(0, weight=1)
    contenidor.grid_columnconfigure(0, weight=1)

    wrapper = tk.Frame(contenidor, bg="#0f172a")
    wrapper.grid(row=0, column=0)

    wrapper.grid_columnconfigure(0, weight=1)
    wrapper.grid_columnconfigure(1, weight=1)

    # ===============================
    # PANEL ESQUERRE
    # ===============================

    panel_esquerre = tk.Frame(
        wrapper,
        bg="#1e293b",
        width=440,
        height=520
    )
    panel_esquerre.grid(row=0, column=0, sticky="nsew")
    panel_esquerre.grid_propagate(False)

    accent = tk.Frame(panel_esquerre, bg="#38bdf8", height=6)
    accent.pack(fill="x", side="top")

    contingut_esquerre = tk.Frame(panel_esquerre, bg="#1e293b")
    contingut_esquerre.pack(expand=True, fill="both", padx=42, pady=42)

    tk.Label(
        contingut_esquerre,
        text="ECG",
        font=("Segoe UI", 38, "bold"),
        bg="#1e293b",
        fg="#38bdf8"
    ).pack(anchor="w")

    tk.Label(
        contingut_esquerre,
        text="Sistema automàtic\nde processament",
        font=("Segoe UI", 24, "bold"),
        bg="#1e293b",
        fg="#ffffff",
        justify="left"
    ).pack(anchor="w", pady=(8, 18))

    tk.Label(
        contingut_esquerre,
        text=(
            "Anàlisi de senyals electrocardiogràfics\n"
            "mitjançant detecció de pics R, càlcul\n"
            "d'intervals RR/NN i paràmetres HRV."
        ),
        font=("Segoe UI", 12),
        bg="#1e293b",
        fg="#cbd5e1",
        justify="left"
    ).pack(anchor="w", pady=(0, 28))

    separador = tk.Frame(contingut_esquerre, bg="#334155", height=1)
    separador.pack(fill="x", pady=(4, 24))

    caracteristiques = [
        ("✓", "Validació sobre MIT-BIH"),
        ("✓", "Anàlisi de qualitat amb BUT QDB"),
        ("✓", "Comparació entre mètodes QRS"),
        ("✓", "Visualització gràfica dels resultats")
    ]

    for icona, text in caracteristiques:
        fila = tk.Frame(contingut_esquerre, bg="#1e293b")
        fila.pack(anchor="w", pady=6)

        tk.Label(
            fila,
            text=icona,
            font=("Segoe UI", 12, "bold"),
            bg="#1e293b",
            fg="#38bdf8",
            width=2
        ).pack(side="left")

        tk.Label(
            fila,
            text=text,
            font=("Segoe UI", 11),
            bg="#1e293b",
            fg="#e5e7eb"
        ).pack(side="left", padx=(8, 0))

    # ===============================
    # PANEL DRET
    # ===============================

    panel_dret = tk.Frame(
        wrapper,
        bg="#ffffff",
        width=500,
        height=520
    )
    panel_dret.grid(row=0, column=1, sticky="nsew")
    panel_dret.grid_propagate(False)

    formulari = tk.Frame(panel_dret, bg="#ffffff")
    formulari.pack(expand=True, fill="both", padx=55, pady=45)

    tk.Label(
        formulari,
        text="Configuració de l'anàlisi",
        font=("Segoe UI", 22, "bold"),
        bg="#ffffff",
        fg="#0f172a"
    ).grid(row=0, column=0, sticky="w", pady=(0, 8))

    tk.Label(
        formulari,
        text="Selecciona el mètode i els registres que vols processar.",
        font=("Segoe UI", 11),
        bg="#ffffff",
        fg="#64748b"
    ).grid(row=1, column=0, sticky="w", pady=(0, 30))

    formulari.grid_columnconfigure(0, weight=1)

    # ===============================
    # VALORS DELS DESPLEGABLES
    # ===============================

    registres_mitbih = [
        "100", "101", "102", "103", "104", "105", "106", "107", "108", "109",
        "111", "112", "113", "114", "115", "116", "117", "118", "119",
        "121", "122", "123", "124", "200", "201", "202", "203", "205",
        "207", "208", "209", "210", "212", "213", "214", "215", "217",
        "219", "220", "221", "222", "223", "228", "230", "231", "232",
        "233", "234"
    ]

    registres_butqdb = [
        "100001", "103001", "103002", "103003", "104001", "105001",
        "111001", "113001", "114001", "115001", "118001", "121001",
        "122001", "123001", "124001", "125001", "126001"
    ]

    # ===============================
    # CAMPS
    # ===============================

    crear_label(formulari, "Mètode de detecció", 2)
    metode_combo = crear_combo(
        formulari,
        ["NeuroKit2", "Pan-Tompkins", "Propi"],
        3
    )

    crear_label(formulari, "Registre MIT-BIH", 4)
    registre_mitbih_combo = crear_combo(
        formulari,
        registres_mitbih,
        5
    )

    crear_label(formulari, "Registre BUT QDB", 6)
    registre_butqdb_combo = crear_combo(
        formulari,
        registres_butqdb,
        7
    )

    # ===============================
    # BOTONS
    # ===============================

    zona_botons = tk.Frame(formulari, bg="#ffffff")
    zona_botons.grid(row=8, column=0, sticky="ew", pady=(10, 0))

    zona_botons.grid_columnconfigure(0, weight=1)
    zona_botons.grid_columnconfigure(1, weight=1)

    def confirmar():
        metode = metode_combo.get()
        registre_mitbih = registre_mitbih_combo.get()
        registre_butqdb = registre_butqdb_combo.get()

        if metode == "NeuroKit2":
            resultat["metode_deteccio"] = deteccio_pics_r_neurokit
            resultat["nom_metode"] = "NeuroKit2"

        elif metode == "Pan-Tompkins":
            resultat["metode_deteccio"] = deteccio_pics_r_pan_tompkins
            resultat["nom_metode"] = "Pan-Tompkins"

        elif metode == "Propi":
            resultat["metode_deteccio"] = deteccio_pics_r_propi
            resultat["nom_metode"] = "Propi"

        resultat["registre_mitbih"] = str(BASE_DIR / "datasets" / "mitbih" / registre_mitbih)
        resultat["registre_butqdb_id"] = registre_butqdb
        resultat["registre_butqdb"] = str(BASE_DIR / "datasets" / "butqdb" / registre_butqdb / f"{registre_butqdb}_ECG")

        finestra.destroy()

    boto_sortir = tk.Button(
        zona_botons,
        text="Sortir",
        command=sortir,
        font=("Segoe UI", 11, "bold"),
        bg="#e2e8f0",
        fg="#0f172a",
        activebackground="#cbd5e1",
        activeforeground="#0f172a",
        relief="flat",
        padx=22,
        pady=12,
        cursor="hand2"
    )
    boto_sortir.grid(row=0, column=0, sticky="ew", padx=(0, 10))

    boto_executar = tk.Button(
        zona_botons,
        text="Executar",
        command=confirmar,
        font=("Segoe UI", 11, "bold"),
        bg="#2563eb",
        fg="#ffffff",
        activebackground="#1d4ed8",
        activeforeground="#ffffff",
        relief="flat",
        padx=22,
        pady=12,
        cursor="hand2"
    )
    boto_executar.grid(row=0, column=1, sticky="ew", padx=(10, 0))

    aplicar_hover(boto_sortir, "#e2e8f0", "#cbd5e1")
    aplicar_hover(boto_executar, "#2563eb", "#1d4ed8")

    tk.Label(
        formulari,
        text="Prem Enter per executar · Prem Esc per sortir",
        font=("Segoe UI", 9),
        bg="#ffffff",
        fg="#94a3b8"
    ).grid(row=9, column=0, sticky="ew", pady=(22, 0))

    finestra.bind("<Return>", lambda event: confirmar())

    finestra.mainloop()

    if resultat.get("cancelat"):
        raise SystemExit("Execució cancel·lada per l'usuari.")

    if not resultat:
        raise SystemExit("Execució cancel·lada per l'usuari.")

    return (
        resultat["metode_deteccio"],
        resultat["nom_metode"],
        resultat["registre_mitbih"],
        resultat["registre_butqdb"],
        resultat["registre_butqdb_id"]
    )


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


def format_valor(valor, unitat=""):
    if np.isnan(valor):
        return "No disponible"
    return f"{valor:.2f} {unitat}".strip()


# ===============================
# DASHBOARD BUT QDB
# ===============================

def afegir_targeta(ax, y, titol, linies):
    MARGE_SUPERIOR = 0.03
    MARGE_INFERIOR = 0.02
    MARGE_LATERAL  = 0.06
    ESPAI_TITOL    = 0.065
    ESPAI_LINIA    = 0.048

    altura = MARGE_SUPERIOR + ESPAI_TITOL + (len(linies) * ESPAI_LINIA) + MARGE_INFERIOR

    rect = FancyBboxPatch(
        (0.03, y - altura),
        0.94,
        altura,
        boxstyle="round,pad=0",
        linewidth=1,
        edgecolor="#d0d0d0",
        facecolor="#f9f9f9",
        transform=ax.transAxes,
        clip_on=False
    )
    ax.add_patch(rect)

    ax.text(
        0.03 + MARGE_LATERAL,
        y - MARGE_SUPERIOR,
        titol,
        fontsize=11,
        fontweight="bold",
        transform=ax.transAxes,
        va="top",
        clip_on=False
    )

    y_text = y - MARGE_SUPERIOR - ESPAI_TITOL

    for etiqueta, valor in linies:
        ax.text(0.03 + MARGE_LATERAL, y_text, etiqueta,
                fontsize=9.5, transform=ax.transAxes, va="top", clip_on=False)
        ax.text(0.94 - MARGE_LATERAL, y_text, valor,
                fontsize=9.5, transform=ax.transAxes, va="top", ha="right", clip_on=False)
        y_text -= ESPAI_LINIA

    return altura


def crear_figura_butqdb(dades):
    fig = plt.figure(figsize=(16, 9))

    gs = GridSpec(
        2, 3, figure=fig,
        width_ratios=[1.25, 1.25, 1.25],
        height_ratios=[1.25, 1],
        wspace=0.25, hspace=0.35
    )

    ax_ecg  = fig.add_subplot(gs[0, 0:2])
    ax_rr   = fig.add_subplot(gs[1, 0])
    ax_nn   = fig.add_subplot(gs[1, 1])
    ax_info = fig.add_subplot(gs[:, 2])

    temps   = dades["temps_segment"]
    ecg_fil = dades["ecg_segment_filtrat"]
    pics    = dades["pics_r_segment"]
    rr      = dades["rr"]
    nn      = dades["nn"]

    # ===============================
    # ECG
    # ===============================

    ax_ecg.plot(temps, ecg_fil, color="black", linewidth=1, label="ECG filtrat")
    ax_ecg.scatter(temps[pics], ecg_fil[pics], color="red", s=35, label="Pics R detectats", zorder=3)
    ax_ecg.set_title("ECG i detecció de pics R", fontsize=12, fontweight="bold")
    ax_ecg.set_xlabel("Temps (s)")
    ax_ecg.set_ylabel("Amplitud (uV)")
    ax_ecg.grid(alpha=0.3)
    ax_ecg.legend(loc="upper right")

    # ===============================
    # RANG COMÚ RR / NN
    # ===============================

    if len(rr) > 0 and len(nn) > 0:
        xmin_h = min(np.min(rr), np.min(nn))
        xmax_h = max(np.max(rr), np.max(nn))
    elif len(rr) > 0:
        xmin_h, xmax_h = np.min(rr), np.max(rr)
    elif len(nn) > 0:
        xmin_h, xmax_h = np.min(nn), np.max(nn)
    else:
        xmin_h, xmax_h = None, None

    if xmin_h is not None and xmin_h == xmax_h:
        xmin_h -= 1
        xmax_h += 1

    # ===============================
    # HISTOGRAMA RR
    # ===============================

    if len(rr) > 0:
        mitja = np.mean(rr)
        ax_rr.hist(rr, bins=30, range=(xmin_h, xmax_h), color="#8bbce8", edgecolor="black", alpha=0.85)
        ax_rr.set_xlim(xmin_h, xmax_h)
        ax_rr.axvline(mitja, color="red", linestyle="--", linewidth=2, label=f"Mitjana RR: {mitja:.2f} ms")
        ax_rr.legend(fontsize=8)

    ax_rr.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax_rr.set_title("Distribució dels intervals RR", fontsize=11, fontweight="bold")
    ax_rr.set_xlabel("Interval RR (ms)")
    ax_rr.set_ylabel("Freqüència")
    ax_rr.grid(alpha=0.3)

    # ===============================
    # HISTOGRAMA NN
    # ===============================

    if len(nn) > 0:
        mitja = np.mean(nn)
        ax_nn.hist(nn, bins=30, range=(xmin_h, xmax_h), color="#8fd19e", edgecolor="black", alpha=0.85)
        ax_nn.set_xlim(xmin_h, xmax_h)
        ax_nn.axvline(mitja, color="red", linestyle="--", linewidth=2, label=f"Mitjana NN: {mitja:.2f} ms")
        ax_nn.legend(fontsize=8)

    ax_nn.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax_nn.set_title("Distribució dels intervals NN", fontsize=11, fontweight="bold")
    ax_nn.set_xlabel("Interval NN (ms)")
    ax_nn.set_ylabel("Freqüència")
    ax_nn.grid(alpha=0.3)

    # ===============================
    # PANEL DRET
    # ===============================

    ax_info.axis("off")
    ax_info.set_xlim(0, 1)
    ax_info.set_ylim(0, 1)

    info_general = [
        ("Base de dades:",          "BUT QDB"),
        ("Registre:",               dades["registre_id"]),
        ("Classe:",                 f"Classe {dades['num_classe']}"),
        ("Durada analitzada:",      f"{temps[-1]:.1f} s"),
        ("Freqüència de mostreig:", f"{dades['fs']} Hz"),
        ("Mètode:",                 dades["nom_metode"]),
        ("Canal utilitzat:",        "Canal 0")
    ]
    info_deteccio = [
        ("Pics R detectats:", str(len(pics))),
        ("Intervals RR:",     str(len(rr))),
        ("Intervals NN:",     str(len(nn)))
    ]
    info_hrv = [
        ("SDRR:",        format_valor(dades["sdrr"],     "ms")),
        ("RMSSD (RR):",  format_valor(dades["rmssd_rr"], "ms")),
        ("SDNN:",        format_valor(dades["sdnn"],     "ms")),
        ("RMSSD (NN):",  format_valor(dades["rmssd_nn"], "ms"))
    ]

    y = 0.99
    for titol, linies in [
        ("Informació general", info_general),
        ("Detecció de pics R", info_deteccio),
        ("Paràmetres HRV",     info_hrv),
    ]:
        altura = afegir_targeta(ax_info, y, titol, linies)
        y -= altura + 0.02

    fig.suptitle(
        f"Anàlisi ECG - Registre {dades['registre_id']} | Classe {dades['num_classe']} | {dades['nom_metode']}",
        fontsize=14, fontweight="bold"
    )
    return fig


# ===============================
# MIT-BIH: PRECISIÓ DEL DETECTOR
# ===============================

def carregar_mitbih(registre):
    record = wfdb.rdrecord(registre)
    ann = wfdb.rdann(registre, "atr")

    senyal = record.p_signal
    fs = record.fs
    canals = record.sig_name

    if "MLII" in canals:
        index_canal = canals.index("MLII")
    else:
        index_canal = 0

    ecg = senyal[:, index_canal]
    canal_utilitzat = canals[index_canal]

    print("\n===============================")
    print("REGISTRE MIT-BIH")
    print("===============================")
    print("Registre:", registre)
    print("Freqüència de mostreig:", fs, "Hz")
    print("Canals:", canals)
    print("Canal utilitzat:", canal_utilitzat)
    print("Shape:", senyal.shape)

    return ecg, fs, ann, canal_utilitzat


def obtenir_pics_reals(ann):

    # wfdb.show_ann_labels() per veure els simbols i les seves etiquetes
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

    precisio = tp / (tp + fp) * 100 if (tp + fp) > 0 else np.nan
    sensibilitat = tp / (tp + fn) * 100 if (tp + fn) > 0 else np.nan
    f1_score = 2 * (precisio * sensibilitat) / (precisio + sensibilitat) if (precisio + sensibilitat) > 0 else np.nan

    return tp, fp, fn, precisio, sensibilitat, f1_score


def crear_figura_mitbih(dades):
    fig = plt.figure(figsize=(16, 9))

    gs = GridSpec(
        2, 3, figure=fig,
        width_ratios=[1.25, 1.25, 1.25],
        height_ratios=[1.25, 1],
        wspace=0.25, hspace=0.35
    )

    ax_ecg          = fig.add_subplot(gs[0, 0:2])
    ax_rr_reals     = fig.add_subplot(gs[1, 0])
    ax_rr_detectats = fig.add_subplot(gs[1, 1])
    ax_info         = fig.add_subplot(gs[:, 2])

    registre_id = Path(dades["registre"]).name

    # ===============================
    # ECG + PICS DEL TRAM VISUALITZAT
    # ===============================

    ax_ecg.plot(dades["temps"], dades["ecg_filtrat"], color="black", linewidth=1, label="ECG filtrat")
    ax_ecg.scatter(
        dades["temps"][dades["pics_detectats_tram"]],
        dades["ecg_filtrat"][dades["pics_detectats_tram"]],
        color="red", s=35, label="Pics detectats", zorder=3
    )
    ax_ecg.scatter(
        dades["temps"][dades["pics_reals_tram"]],
        dades["ecg_filtrat"][dades["pics_reals_tram"]],
        marker="x", color="black", s=45, linewidths=1.5, label="Pics reals", zorder=4
    )
    ax_ecg.set_title("ECG i comparació de pics R", fontsize=12, fontweight="bold")
    ax_ecg.set_xlabel("Temps (s)")
    ax_ecg.set_ylabel("Amplitud (uV)")
    ax_ecg.grid(alpha=0.3)
    ax_ecg.legend(loc="upper right")

    # ===============================
    # RANG COMÚ RR REALS / RR DETECTATS
    # ===============================

    rr_reals     = dades["rr_reals"]
    rr_detectats = dades["rr_detectats"]

    if len(rr_reals) > 0 and len(rr_detectats) > 0:
        xmin = min(np.min(rr_reals), np.min(rr_detectats))
        xmax = max(np.max(rr_reals), np.max(rr_detectats))
    elif len(rr_reals) > 0:
        xmin, xmax = np.min(rr_reals), np.max(rr_reals)
    elif len(rr_detectats) > 0:
        xmin, xmax = np.min(rr_detectats), np.max(rr_detectats)
    else:
        xmin, xmax = None, None

    if xmin is not None and xmin == xmax:
        xmin -= 1
        xmax += 1

    # ===============================
    # HISTOGRAMA RR REALS
    # ===============================

    if len(rr_reals) > 0:
        mitja = np.mean(rr_reals)
        ax_rr_reals.hist(rr_reals, bins=30, range=(xmin, xmax), color="#8bbce8", edgecolor="black", alpha=0.85)
        ax_rr_reals.set_xlim(xmin, xmax)
        ax_rr_reals.axvline(mitja, color="red", linestyle="--", linewidth=2, label=f"Mitjana RR real: {mitja:.2f} ms")
        ax_rr_reals.legend(fontsize=8)

    ax_rr_reals.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax_rr_reals.set_title("Distribució dels intervals RR reals", fontsize=11, fontweight="bold")
    ax_rr_reals.set_xlabel("Interval RR real (ms)")
    ax_rr_reals.set_ylabel("Freqüència")
    ax_rr_reals.grid(alpha=0.3)

    # ===============================
    # HISTOGRAMA RR DETECTATS
    # ===============================

    if len(rr_detectats) > 0:
        mitja = np.mean(rr_detectats)
        ax_rr_detectats.hist(rr_detectats, bins=30, range=(xmin, xmax), color="#f4a261", edgecolor="black", alpha=0.85)
        ax_rr_detectats.set_xlim(xmin, xmax)
        ax_rr_detectats.axvline(mitja, color="red", linestyle="--", linewidth=2, label=f"Mitjana RR detectat: {mitja:.2f} ms")
        ax_rr_detectats.legend(fontsize=8)

    ax_rr_detectats.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax_rr_detectats.set_title("Distribució dels intervals RR detectats", fontsize=11, fontweight="bold")
    ax_rr_detectats.set_xlabel("Interval RR detectat (ms)")
    ax_rr_detectats.set_ylabel("Freqüència")
    ax_rr_detectats.grid(alpha=0.3)

    # ===============================
    # PANEL DRET
    # ===============================

    ax_info.axis("off")
    ax_info.set_xlim(0, 1)
    ax_info.set_ylim(0, 1)

    info_general = [
        ("Base de dades:",          "MIT-BIH"),
        ("Registre:",               registre_id),
        ("Durada visualitzada:",    f"{dades['temps'][-1]:.1f} s"),
        ("Freqüència de mostreig:", f"{dades['fs']} Hz"),
        ("Mètode:",                 dades["nom_metode"]),
        ("Canal utilitzat:",        dades["canal_utilitzat"])
    ]
    info_deteccio = [
        ("Pics detectats totals:", str(dades["total_pics_detectats"])),
        ("Pics reals totals:",     str(dades["total_pics_reals"])),
        ("TP:",                    str(dades["tp"])),
        ("FP:",                    str(dades["fp"])),
        ("FN:",                    str(dades["fn"])),
        ("Tolerància:",            f"{TOLERANCIA_MS} ms")
    ]
    info_metriques = [
        ("Precisió:",     format_valor(dades["precisio"],     "%")),
        ("Sensibilitat:", format_valor(dades["sensibilitat"], "%")),
        ("F1-score:",     format_valor(dades["f1_score"],     "%"))
    ]

    y = 0.99
    for titol, linies in [
        ("Informació general",            info_general),
        ("Resultats globals de detecció", info_deteccio),
        ("Mètriques de rendiment",        info_metriques),
    ]:
        altura = afegir_targeta(ax_info, y, titol, linies)
        y -= altura + 0.02

    fig.suptitle(
        f"Anàlisi ECG - Registre {registre_id} | MIT-BIH | {dades['nom_metode']}",
        fontsize=14, fontweight="bold"
    )
    return fig


# ===============================
# BUT QDB
# ===============================

def carregar_butqdb(registre):
    record = wfdb.rdrecord(registre)

    senyal = record.p_signal
    fs = record.fs
    canals = record.sig_name
    ecg = senyal[:, 0]

    durada = len(ecg) / fs

    print("\n===============================")
    print("REGISTRE BUT QDB")
    print("===============================")
    print("Registre:", registre)
    print("Freqüència de mostreig:", fs, "Hz")
    print("Canals:", canals)
    print("Shape del senyal:", senyal.shape)
    print("Durada senyal (s):", durada)
    print("Min:", np.min(ecg))
    print("Max:", np.max(ecg))
    print("Unitats:", record.units[0])

    return ecg, fs


# ===============================
# CÀLCUL DE DADES (sense mostrar)
# ===============================

def calcular_dades_mitbih(registre):
    ecg, fs, ann, canal_utilitzat = carregar_mitbih(registre)

    pics_detectats, ecg_filtrat = metode_deteccio(ecg, fs)
    pics_reals = obtenir_pics_reals(ann)

    tp, fp, fn, precisio, sensibilitat, f1_score = calcular_metriques_deteccio(
        pics_detectats, pics_reals, fs
    )

    print(f"\n--- Resultats detecció MIT-BIH | {nom_metode} ---")
    print("Pics detectats:", len(pics_detectats))
    print("Pics reals:", len(pics_reals))
    print(f"TP: {tp}  FP: {fp}  FN: {fn}")
    print(f"Precisió: {precisio:.3f}%  Sensibilitat: {sensibilitat:.3f}%  F1: {f1_score:.3f}%")

    inici = 0
    final = int(DURADA_SEGMENT_S * fs)
    ecg_tram   = ecg_filtrat[inici:final]
    temps_tram = np.arange(len(ecg_tram)) / fs

    tram_detectats = (pics_detectats >= inici) & (pics_detectats < final)
    tram_reals     = (pics_reals     >= inici) & (pics_reals     < final)

    pics_detectats_tram = pics_detectats[tram_detectats] - inici
    pics_reals_tram     = pics_reals[tram_reals]         - inici

    rr_detectats, _, _ = calcular_rr_hrv(pics_detectats, fs)
    rr_reals,     _, _ = calcular_rr_hrv(pics_reals,     fs)

    return dict(
        temps=temps_tram,
        ecg_filtrat=ecg_tram,
        pics_detectats_tram=pics_detectats_tram,
        pics_reals_tram=pics_reals_tram,
        rr_detectats=rr_detectats,
        rr_reals=rr_reals,
        tp=tp, fp=fp, fn=fn,
        precisio=precisio,
        sensibilitat=sensibilitat,
        f1_score=f1_score,
        registre=registre,
        nom_metode=nom_metode,
        fs=fs,
        canal_utilitzat=canal_utilitzat,
        total_pics_detectats=len(pics_detectats),
        total_pics_reals=len(pics_reals)
    )


def calcular_dades_butqdb(ecg, fs, registre_id, num_classe):
    """Retorna les dades calculades o None si la classe no existeix."""
    if registre_id not in SEGMENTS_BUTQDB:
        return None
    if num_classe not in SEGMENTS_BUTQDB[registre_id]:
        return None

    start, end = SEGMENTS_BUTQDB[registre_id][num_classe]
    if end is None:
        end = start + int(DURADA_SEGMENT_S * fs)
    end = min(len(ecg), end)

    ecg_segment = ecg[start:end]
    if len(ecg_segment) == 0:
        return None

    temps_segment = np.arange(len(ecg_segment)) / fs
    pics_r_segment, ecg_segment_filtrat = metode_deteccio(ecg_segment, fs)

    rr, sdrr, rmssd_rr = calcular_rr_hrv(pics_r_segment, fs)
    nn = filtrar_rr_a_nn(rr)
    sdnn, rmssd_nn = calcular_hrv_intervals(nn)

    return dict(
        temps_segment=temps_segment,
        ecg_segment_filtrat=ecg_segment_filtrat,
        pics_r_segment=pics_r_segment,
        rr=rr, nn=nn,
        sdrr=sdrr, rmssd_rr=rmssd_rr,
        sdnn=sdnn, rmssd_nn=rmssd_nn,
        registre_id=registre_id,
        num_classe=num_classe,
        nom_metode=nom_metode,
        fs=fs
    )


# ===============================
# NAVEGACIÓ ENTRE PANTALLES
# ===============================

def navegar_pantalles(pantalles):
    """
    pantalles: llista de dicts amb claus:
      - "tipus": "mitbih" | "butqdb" | "no_disponible"
      - "titol": str (per la barra de navegació)
      - "dades": dict (per crear la figura) o None
      - "missatge": str (només per "no_disponible")
    """

    estat = {"index": 0, "figures": {}, "tornar_menu": False}

    def obtenir_figura(i):
        if i not in estat["figures"]:
            p = pantalles[i]
            if p["tipus"] == "mitbih":
                estat["figures"][i] = crear_figura_mitbih(p["dades"])
            elif p["tipus"] == "butqdb":
                estat["figures"][i] = crear_figura_butqdb(p["dades"])
            else:
                estat["figures"][i] = None
        return estat["figures"][i]

    def mostrar(i):
        estat["index"] = i
        p = pantalles[i]
        total = len(pantalles)

        indicador.config(text=f"{p['titol']}  ({i + 1} / {total})")

        # Botó esquerre: "Tornar al menú" a la primera, "Anterior" a la resta
        if i == 0:
            boto_esquerre.config(
                text="☰  Tornar al menú",
                command=tornar_menu,
                bg="#475569",
                state="normal"
            )
            boto_esquerre.bind("<Enter>", lambda e: boto_esquerre.config(bg="#64748b"))
            boto_esquerre.bind("<Leave>", lambda e: boto_esquerre.config(bg="#475569"))
        else:
            boto_esquerre.config(
                text="◀  Anterior",
                command=anar_anterior,
                bg="#334155",
                state="normal"
            )
            boto_esquerre.bind("<Enter>", lambda e: boto_esquerre.config(bg="#475569"))
            boto_esquerre.bind("<Leave>", lambda e: boto_esquerre.config(bg="#334155"))

        # Botó dret: "Finalitzar" a l'última, "Següent" a la resta
        if i == total - 1:
            boto_dret.config(
                text="Finalitzar  ✕",
                command=finalitzar,
                bg="#dc2626",
                state="normal"
            )
            boto_dret.bind("<Enter>", lambda e: boto_dret.config(bg="#b91c1c"))
            boto_dret.bind("<Leave>", lambda e: boto_dret.config(bg="#dc2626"))
        else:
            boto_dret.config(
                text="Següent  ▶",
                command=anar_seguent,
                bg="#2563eb",
                state="normal"
            )
            boto_dret.bind("<Enter>", lambda e: boto_dret.config(bg="#1d4ed8"))
            boto_dret.bind("<Leave>", lambda e: boto_dret.config(bg="#2563eb"))

        # Neteja i mostra la figura
        for widget in marc_figura.winfo_children():
            widget.destroy()

        if p["tipus"] == "no_disponible":
            contenidor_msg = tk.Frame(marc_figura, bg="#f8fafc")
            contenidor_msg.pack(expand=True)

            tk.Label(
                contenidor_msg,
                text="⚠",
                font=("Segoe UI", 48),
                bg="#f8fafc",
                fg="#cbd5e1"
            ).pack()

            tk.Label(
                contenidor_msg,
                text=p["missatge"],
                font=("Segoe UI", 24),
                bg="#f8fafc",
                fg="#64748b",
                justify="center"
            ).pack(pady=(12, 0))
            
        else:
            fig = obtenir_figura(i)
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, master=marc_figura)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

    def anar_anterior():
        if estat["index"] > 0:
            mostrar(estat["index"] - 1)

    def anar_seguent():
        if estat["index"] < len(pantalles) - 1:
            mostrar(estat["index"] + 1)

    def tornar_menu():
        estat["tornar_menu"] = True
        plt.close("all")
        finestra.destroy()

    def finalitzar():
        plt.close("all")
        finestra.destroy()

    # ===============================
    # FINESTRA DE NAVEGACIÓ
    # ===============================

    finestra = tk.Tk()
    finestra.title("Anàlisi ECG")

    try:
        finestra.state("zoomed")
    except Exception:
        amplada = finestra.winfo_screenwidth()
        altura  = finestra.winfo_screenheight()
        finestra.geometry(f"{amplada}x{altura}+0+0")

    finestra.configure(bg="#1e293b")

    # Barra de navegació inferior
    barra = tk.Frame(finestra, bg="#1e293b", pady=10)
    barra.pack(side="bottom", fill="x", padx=20)

    boto_esquerre = tk.Button(
        barra,
        font=("Segoe UI", 11, "bold"),
        padx=24, pady=10, cursor="hand2",
        relief="flat", fg="white"
    )
    boto_esquerre.pack(side="left")

    indicador = tk.Label(
        barra, text="",
        font=("Segoe UI", 12),
        bg="#1e293b", fg="#cbd5e1"
    )
    indicador.pack(side="left", expand=True)

    boto_dret = tk.Button(
        barra,
        font=("Segoe UI", 11, "bold"),
        padx=24, pady=10, cursor="hand2",
        relief="flat", fg="white"
    )
    boto_dret.pack(side="right")

    # Àrea de la figura
    marc_figura = tk.Frame(finestra, bg="#f8fafc")
    marc_figura.pack(fill="both", expand=True)

    # Navegació amb fletxes del teclat
    finestra.bind("<Left>",  lambda e: anar_anterior())
    finestra.bind("<Right>", lambda e: anar_seguent())

    mostrar(0)
    finestra.mainloop()

    return estat["tornar_menu"]


# ===============================
# EXECUCIÓ
# ===============================

while True:
    metode_deteccio, nom_metode, registre_mitbih, registre_butqdb, registre_butqdb_id = seleccionar_configuracio()

    # 1) Precalcular totes les dades
    print("\nCalculant MIT-BIH...")
    dades_mitbih = calcular_dades_mitbih(registre_mitbih)

    print("\nCarregant BUT QDB...")
    ecg_butqdb, fs_butqdb = carregar_butqdb(registre_butqdb)

    print("\nCalculant BUT QDB classes...")
    dades_butqdb = {}
    for classe in [1, 2, 3]:
        dades_butqdb[classe] = calcular_dades_butqdb(ecg_butqdb, fs_butqdb, registre_butqdb_id, classe)

    # 2) Construir llista de pantalles
    pantalles = [
        {
            "tipus": "mitbih",
            "titol": f"MIT-BIH · Registre {Path(registre_mitbih).name}",
            "dades": dades_mitbih
        }
    ]

    for classe in [1, 2, 3]:
        if dades_butqdb[classe] is not None:
            pantalles.append({
                "tipus": "butqdb",
                "titol": f"BUT QDB · {registre_butqdb_id} · Classe {classe}",
                "dades": dades_butqdb[classe]
            })
        else:
            pantalles.append({
                "tipus": "no_disponible",
                "titol": f"BUT QDB · {registre_butqdb_id} · Classe {classe}",
                "dades": None,
                "missatge": (
                    f"El registre {registre_butqdb_id} no té cap segment\n"
                    f"de Classe {classe} disponible."
                )
            })

    # 3) Mostrar navegador; si retorna True, tornem al menú
    tornar = navegar_pantalles(pantalles)
    if not tornar:
        break