import streamlit as st
import pandas as pd
import os
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni Amel Italia", layout="wide")

# CSS PER ALLINEAMENTO PERFETTO E SUPPORTO TEMA
st.markdown("""
    <style>
    .stMarkdown h3 {
        text-align: center;
        font-size: 1rem !important;
        background-color: rgba(128, 128, 128, 0.1); 
        color: inherit;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 10px !important;
        min-height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        padding-bottom: 20px;
    }

    [data-testid="stImage"] img {
        border-radius: 12px;
        width: 100% !important;
        height: 180px !important; 
        object-fit: cover !important; 
        max-width: 180px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    [data-testid="column"] {
        padding: 0 5px !important;
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
    "Margherita Monti 2": "img/Margherita Monti.jpg",
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

# --- GESTIONE SESSIONE E LINGUA ---
if 'loggato' not in st.session_state:
    st.session_state.loggato, st.session_state.nome_voto = False, ""
    st.session_state.lang = "it"

# --- LOGIN ---
if not st.session_state.loggato:
    st.title("🗳️ Accesso Elezioni Amel Italia")
    scelta = st.selectbox("Seleziona il tuo nome / Select your name:", ["-- Scegli dalla lista --"] + SOCI_AUTORIZZATI)
    if st.button("ACCEDI / LOGIN"):
        if scelta != "-- Scegli dalla lista --":
            if ha_gia_votato(scelta): 
                st.error("Hai già votato / You have already voted.")
            else:
                st.session_state.loggato = True
                st.session_state.nome_voto = scelta
                # Imposta inglese se l'utente è Alaa
                st.session_state.lang = "en" if scelta == "Alaa" else "it"
                st.rerun()
    st.stop()

# --- DIZIONARIO TRADUZIONI ---
texts = {
    "it": {
        "title": "Scheda Elettorale",
        "socio": "Socio",
        "h1": "1. Elezione del Presidente",
        "h2": "2. Elezione del Consiglio Direttivo",
        "pick_p": "Scegli il Presidente:",
        "pick_c_info": "Seleziona 4 membri diversi per il Consiglio:",
        "c_label": "Consigliere",
        "submit": "INVIA VOTO DEFINITIVO",
        "error": "⚠️ Errore: seleziona tutti i candidati richiesti.",
        "success": "Voto registrato con successo!",
        "footer": "La sessione verrà chiusa."
    },
    "en": {
        "title": "Ballot Paper",
        "socio": "Member",
        "h1": "1. Election of the President",
        "h2": "2. Election of the Board of Directors",
        "pick_p": "Choose the President:",
        "pick_c_info": "Select 4 different members for the Board:",
        "c_label": "Board Member",
        "submit": "SUBMIT FINAL VOTE",
        "error": "⚠️ Error: Please select all required candidates.",
        "success": "Vote registered successfully!",
        "footer": "Session will be closed."
    }
}
L = texts[st.session_state.lang]

# --- INTERFACCIA DI VOTO ---
st.title(f"{L['title']}: {st.session_state.nome_voto}")

# 1. SEZIONE PRESIDENTE
st.header(L['h1'])
cols_p = st.columns(len(CANDIDATI_P))
for i, (nome, img_path) in enumerate(CANDIDATI_P.items()):
    with cols_p[i]:
        st.subheader(nome)
        if os.path.exists(img_path):
            st.image(img_path)

v_pres = st.selectbox(L['pick_p'], ["-- Seleziona/Select --"] + list(CANDIDATI_P.keys()))

st.divider()

# 2. SEZIONE CONSIGLIO
st.header(L['h2'])
cols_c = st.columns(len(CANDIDATI_C))
for i, (nome, img_path) in enumerate(CANDIDATI_C.items()):
    with cols_c[i]:
        st.subheader(nome)
        if os.path.exists(img_path):
            st.image(img_path)

st.info(L['pick_c_info'])
c_list = list(CANDIDATI_C.keys())

s1 = st.selectbox(f"{L['c_label']} 1", ["-- Seleziona/Select --"] + c_list)
s2 = st.selectbox(f"{L['c_label']} 2", ["-- Seleziona/Select --"] + [c for c in c_list if c != s1])
s3 = st.selectbox(f"{L['c_label']} 3", ["-- Seleziona/Select --"] + [c for c in c_list if c not in [s1, s2]])
s4 = st.selectbox(f"{L['c_label']} 4", ["-- Seleziona/Select --"] + [c for c in c_list if c not in [s1, s2, s3]])

st.divider()

if st.button(L['submit']):
    voti_c = [s1, s2, s3, s4]
    if "-- Seleziona/Select --" in [v_pres] + voti_c:
        st.error(L['error'])
    else:
        voto_finale = {"Presidente": v_pres, "C1": s1, "C2": s2, "C3": s3, "C4": s4}
        salva_voto(voto_finale, st.session_state.nome_voto)
        st.success(L['success'])
        st.balloons()
        time.sleep(2)
        st.session_state.loggato = False
        st.rerun()
