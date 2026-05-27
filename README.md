**Nicolás Martín Costa**  
Treball Final de Grau - Grau en Enginyeria Biomèdica  
Universitat de Girona

Aquest repositori conté el codi desenvolupat per al Treball de Fi de Grau:

**Desenvolupament i validació d’un sistema automàtic de processament de senyal ECG per a l’anàlisi del ritme cardíac**

El sistema permet carregar registres ECG, aplicar diferents mètodes de detecció QRS, visualitzar els pics R detectats i calcular paràmetres de variabilitat de la freqüència cardíaca a partir dels intervals RR i NN.

## Contingut del repositori

L’estructura principal del projecte és la següent:

```text
tfg_ecg/
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
- `exportar_resultats.py`: script auxiliar per generar automàticament un fitxer Excel amb els resultats globals i per registre.
- `requirements.txt`: fitxer amb les llibreries necessàries per executar el projecte.

## Requeriments d’instal·lació

Per executar el projecte cal disposar de Python instal·lat. Les dependències necessàries es poden instal·lar amb la comanda següent:

```bash
pip install -r requirements.txt
```

El fitxer `requirements.txt` inclou les llibreries principals utilitzades pel projecte:

```text
numpy
matplotlib
wfdb
neurokit2
scipy
pandas
openpyxl
```

La interfície gràfica utilitza `tkinter`, que habitualment ja s’inclou amb la instal·lació estàndard de Python. En cas que no estigui disponible, caldrà instal·lar-lo o activar-lo segons el sistema operatiu utilitzat.

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
tfg_ecg/
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

En executar-lo, s’obre una interfície inicial que permet seleccionar:

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

3. Prémer el botó **Executar**.

4. El sistema mostrarà primer els resultats corresponents al dataset MIT-BIH, incloent:

- tram ECG visualitzat,
- pics R detectats,
- anotacions reals del registre,
- histogrames dels intervals RR reals i detectats,
- valors de TP, FP i FN,
- precisió, sensibilitat i F1-score.

5. A continuació, es mostraran les pantalles corresponents al dataset BUT QDB, amb:

- detecció dels pics R sobre el tram analitzat,
- histograma dels intervals RR,
- histograma dels intervals NN,
- SDRR,
- SDNN,
- RMSSD calculada sobre RR,
- RMSSD calculada sobre NN.

Si el registre seleccionat no disposa d’un tram vàlid per a una determinada classe de qualitat, el programa mostra una pantalla informativa indicant que aquella classe no està disponible.

## Navegació dins la interfície

La navegació entre pantalles es realitza mitjançant els botons situats a la part inferior de la interfície:

- **Següent**: avança a la pantalla següent.
- **Anterior**: torna a la pantalla anterior.
- **Tornar al menú**: permet tornar a la pantalla inicial per seleccionar una nova configuració.
- **Finalitzar**: tanca l’execució del programa.

També es poden utilitzar les fletxes del teclat per avançar o retrocedir entre pantalles.

## Exportació de resultats

Per generar el fitxer Excel amb els resultats agregats de l’anàlisi, cal executar:

```bash
python exportar_resultats.py
```

Aquest script genera automàticament el fitxer:

```text
resultats_tfg.xlsx
```

Aquest fitxer no s’inclou directament al repositori, ja que es pot obtenir executant l’script corresponent a partir del codi i de les dades descarregades.

## Notes sobre reproduïbilitat

Per reproduir correctament l’anàlisi cal:

1. Instal·lar les dependències indicades.
2. Descarregar les bases de dades originals.
3. Col·locar-les dins la carpeta `datasets/` amb l’estructura indicada.
4. Executar `main.py` per visualitzar els resultats.
5. Executar `exportar_resultats.py` si es vol generar el fitxer Excel amb els resultats agregats.

Les rutes del projecte estan definides respecte a la ubicació dels fitxers Python, de manera que la carpeta `datasets/` ha d’estar situada al nivell arrel del projecte.

## Autor

Nicolás Martín Costa  
Grau en Enginyeria Biomèdica  
Universitat de Girona
