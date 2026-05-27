**Nicolás Martín Costa**  
Treball Final de Grau - Grau en Enginyeria Biomèdica

Aquest repositori conté el codi desenvolupat per al Treball de Fi de Grau:

**Desenvolupament i validació d’un sistema automàtic de processament de senyal ECG per a l’anàlisi del ritme cardíac**

El sistema permet carregar registres ECG, aplicar diferents mètodes de detecció QRS, visualitzar els pics R detectats i calcular paràmetres de variabilitat de la freqüència cardíaca a partir dels intervals RR i NN.

## Contingut del repositori

L’estructura principal del projecte és la següent:

```text
TFG_ECG/
│
├── main.py
├── metode_neurokit.py
├── metode_pan_tompkins.py
├── metode_propi.py
├── exportar_resultats.py
├── requirements.txt
├── README.md
```

## Fitxers principals

- `main.py`: programa principal del sistema. Permet seleccionar el mètode de detecció, carregar els registres ECG i visualitzar els resultats mitjançant una interfície gràfica.
- `metode_neurokit.py`: implementació de la detecció QRS mitjançant NeuroKit2.
- `metode_pan_tompkins.py`: implementació del detector basat en l’algorisme Pan-Tompkins.
- `metode_propi.py`: implementació del mètode propi de detecció QRS.
- `exportar_resultats.py`: script auxiliar per generar automàticament un fitxer Excel amb els resultats agregats.
- `requirements.txt`: fitxer amb les llibreries necessàries per executar el projecte.

## Requeriments d’instal·lació

Per executar el projecte cal disposar de Python instal·lat. Les llibreries necessàries es poden instal·lar amb la comanda següent:

```bash
pip install -r requirements.txt
```

El fitxer `requirements.txt` inclou les dependències principals:

```text
numpy
matplotlib
wfdb
neurokit2
scipy
pandas
openpyxl
```

La interfície gràfica utilitza `tkinter`, que habitualment ja s’inclou amb la instal·lació estàndard de Python.

## Bases de dades

Les bases de dades utilitzades no s’inclouen directament al repositori a causa de la seva mida. Per reproduir l’anàlisi, cal descarregar-les des de les seves fonts originals:

```text
MIT-BIH Arrhythmia Database:
https://physionet.org/content/mitdb/1.0.0/

Brno University of Technology ECG Quality Database (BUT QDB):
https://physionet.org/content/butqdb/
```

Un cop descarregades, les bases de dades s’han de col·locar dins una carpeta anomenada `datasets/`, situada al mateix nivell que `main.py`.

L’estructura esperada és la següent:

```text
TFG_ECG/
│
├── main.py
├── exportar_resultats.py
├── requirements.txt
├── README.md
│
└── datasets/
    ├── mitbih/
    │   ├── 100.dat
    │   ├── 100.hea
    │   ├── 100.atr
    │   └── ...
    │
    └── butqdb/
        ├── 100001/
        │   ├── 100001_ECG.dat
        │   ├── 100001_ECG.hea
        │   └── ...
        └── ...
```

És important mantenir aquesta estructura perquè el programa pugui localitzar correctament els registres ECG.

## Execució del programa principal

Per iniciar el sistema, cal executar:

```bash
python main.py
```

En executar-lo, s’obre una interfície inicial on l’usuari pot seleccionar:

1. El mètode de detecció QRS.
2. El registre del dataset MIT-BIH.
3. El registre del dataset BUT QDB.

Els mètodes disponibles són:

- NeuroKit2
- Pan-Tompkins
- Mètode propi

Un cop seleccionats els paràmetres, cal prémer el botó **Executar**.

## Exemple bàsic de funcionament

Un exemple simple d’ús seria:

1. Executar el programa principal:

```bash
python main.py
```

2. Seleccionar a la interfície:

```text
Mètode de detecció: Propi
Registre MIT-BIH: 100
Registre BUT QDB: 122001
```

3. Prémer **Executar**.

4. El sistema mostrarà primer els resultats corresponents al dataset MIT-BIH, incloent:

- tram ECG analitzat,
- pics detectats,
- anotacions reals,
- histogrames dels intervals RR,
- valors de TP, FP i FN,
- precisió, sensibilitat i F1-score.

5. A continuació, es mostraran les pantalles corresponents al dataset BUT QDB, amb:

- detecció dels pics R,
- histograma dels intervals RR,
- histograma dels intervals NN,
- SDRR,
- SDNN,
- RMSSD calculada sobre RR,
- RMSSD calculada sobre NN.

La navegació entre pantalles es realitza mitjançant els botons de la interfície.

## Exportació de resultats

Per generar el fitxer Excel amb els resultats agregats, cal executar:

```bash
python exportar_resultats.py
```

Aquest script genera automàticament el fitxer:

```text
resultats_tfg.xlsx
```

Aquest fitxer no s’inclou directament al repositori, ja que es pot obtenir executant l’script corresponent.

## Notes sobre reproduïbilitat

Per reproduir correctament l’anàlisi cal:

1. Instal·lar les dependències indicades.
2. Descarregar les bases de dades originals.
3. Col·locar-les dins la carpeta `datasets/` amb l’estructura indicada.
4. Executar `main.py` o `exportar_resultats.py` segons el tipus d’anàlisi que es vulgui realitzar.

## Autor

Nicolás Martín Costa  
Grau en Enginyeria Biomèdica  
Universitat de Girona
