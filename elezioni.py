import streamlit as st
import pandas as pd
import os
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni Amel Italia", layout="wide")

# CSS PER USARE GLI SLOT PER I NOMI E CENTRARE LE FOTO
st.markdown("""
    <style>
    /* Stile per il testo del nome dentro lo slot (header della colonna) */
    .stMarkdown h3 {
        text-align: center;
        font-size: 1.1rem !important;
        background-color: #262730; /* Colore scuro coordinato */
        color: white;
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 15px !important;
    }

    /* Centratura e distanziamento foto */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        padding-top: 10px;
        padding-bottom: 20px;
    }

    [data-testid="stImage"] img {
        border-radius: 10px;
        width: 100% !important;
        height: auto !important;
        max-width: 180px !important; /* Leggermente più piccole per centrarle meglio */
        border: 2px solid #444;
    }
    
    /* Rimuove margini extra dalle colonne */
    [data-testid="column"] {
        padding: 0 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

FILE_RISULTATI = "risultati_anonimi.csv"
FILE_REGISTRO_VOTANTI = "registro_voto_effettuato.txt"

SOCI_AUTORIZZATI = sorted([
    "Roberto R", "Roberto V", "Andrea", "Marco", "Mara", "Federica", "Giulia", 
    "Chiara", "Alaa", "Costanza", "Lorenzo", "Margherita", "Sofia", 
    "Stefania", "Marcello", "Matilde", "Tommaso", "Leonardo"
])

CANDIDATI_P = {
    "Roberto Renino": "img/Roberto Renino.jpg",
    "Candidato Pres B": "img/pres_b.jpg"
}

CANDIDATI_C = {
    "Lorenzo Cogliolo": "img/Lorenzo Cogliolo.jpg",
    "Margherita Monti": "img/Margherita Monti.jpg",
    "Marco Zac Di Fraia": "img/Marco Zac Di Fraia.jpg",
    "Mara Moreale": "img/Mara Moreale.jpg",
    "Consigliere 5": "img/c5.jpg",
    "Consigliere 6": "img/c6.jpg"
}

# --- FUNZIONI ---
def ha_gia_votato(nome):
    if not os.path.isfile(FILE_REGISTRO_VOTANTI): return False
    with open(FILE_REGISTRO_VOTANTI, "r") as f:
        return nome in f.read().splitlines()

def salva_voto(voto, nome):
    df = pd.DataFrame([voto])
    df.to_csv(FILE_RISULTATI, mode='a', index=False, header=not os.path.isfile(FILE_RISULTATI))
    with open(FILE_REGISTRO_VOTANTI, "a") as f:
        f.write(nome + "\n")

# --- LOGIN ---
if 'loggato' not in st.session_state:
    st.session_state.loggato, st.session_state.nome_voto = False, ""

if not st.session_state.loggato:
    st.title("🗳️ Accesso Elezioni Amel Italia")
    scelta = st.selectbox("Seleziona il tuo nome:", ["-- Scegli dalla lista --"] + SOCI_AUTORIZZATI)
    if st.button("ACCEDI"):
        if scelta != "-- Scegli dalla lista --":
            if ha_gia_votato(scelta): 
                st.error("Hai già votato.")
            else:
                st.session_state.loggato, st.session_state.nome_voto = True, scelta
                st.rerun()
    
    with st.sidebar:
        if st.text_input("Password Admin", type="password") == "K_ammello123":
            if os.path.isfile(FILE_RISULTATI):
                st.download_button("SCARICA RISULTATI", pd.read_csv(FILE_RISULTATI).to_csv(index=False), "voti.csv")
    st.stop()

# --- INTERFACCIA DI VOTO ---
st.title(f"Scheda Elettorale: {st.session_state.nome_voto}")

# SEZIONE PRESIDENTE
st.header("Candidati alla Presidenza")
cols_p = st.columns(len(CANDIDATI_P))
for i, (nome, img_path) in enumerate(CANDIDATI_P.items()):
    with cols_p[i]:
        st.subheader(nome) # Inserisce il nome nello slot superiore
        if os.path.exists(img_path):
            st.image(img_path)
        else:
            st.info("Immagine non disponibile")

# SEZIONE CONSIGLIO
st.header("Candidati al Consiglio Direttivo")
cols_c = st.columns(len(CANDIDATI_C))
for i, (nome, img_path) in enumerate(CANDIDATI_C.items()):
    with cols_c[i]:
        st.subheader(nome) # Inserisce il nome nello slot superiore
        if os.path.exists(img_path):
            st.image(img_path)
        else:
            st.info("Immagine non disponibile")

st.divider()

# SEZIONE SELEZIONE
st.header("Esprimi il tuo voto")
v_pres = st.selectbox("Presidente:", ["-- Seleziona --"] + list(CANDIDATI_P.keys()))

st.subheader("Membri del Consiglio")
c_list = list(CANDIDATI_C.keys())
s1 = st.selectbox("Consigliere 1", ["-- Seleziona --"] + c_list)
s2 = st.selectbox("Consigliere 2", ["-- Seleziona --"] + [c for c in c_list if c != s1])
s3 = st.selectbox("Consigliere 3", ["-- Seleziona --"] + [c for c in c_list if c not in [s1, s2]])
s4 = st.selectbox("Consigliere 4", ["-- Seleziona --"] + [c for c in c_list if c not in [s1, s2, s3]])

if st.button("INVIA VOTO DEFINITIVO"):
    if "-- Seleziona --" in [v_pres, s1, s2, s3, s4]:
        st.error("⚠️ Errore: seleziona tutti i candidati richiesti.")
    else:
        voto = {"Presidente": v_pres, "C1": s1, "C2": s2, "C3": s3, "C4": s4}
        salva_voto(voto, st.session_state.nome_voto)
        st.success("Voto registrato con successo!")
        st.balloons()
        time.sleep(2)
        st.session_state.loggato = False
        st.rerun()

