import streamlit as st
import pandas as pd
import os
import time

# --- 1. CONFIGURAZIONE E INIZIALIZZAZIONE ---
st.set_page_config(page_title="Elezioni Amel Italia", layout="wide")

# Inizializziamo subito le variabili di stato per evitare AttributeError
if 'loggato' not in st.session_state:
    st.session_state.loggato = False
if 'nome_voto' not in st.session_state:
    st.session_state.nome_voto = ""
if 'lang' not in st.session_state:
    st.session_state.lang = "it"  # Lingua predefinita

# --- 2. CSS ---
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
    [data-testid="column"] { padding: 0 5px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATI E TRADUZIONI ---
FILE_RISULTATI = "risultati_anonimi.csv"
FILE_REGISTRO_VOTANTI = "registro_voto_effettuato.txt"

SOCI_AUTORIZZATI = sorted(["Roberto R", "Roberto V", "Andrea", "Marco", "Mara", "Federica", "Giulia", "Chiara", "Alaa", "Costanza", "Lorenzo", "Margherita", "Sofia", "Stefania", "Marcello", "Matilde", "Tommaso", "Leonardo"])

CANDIDATI_P = {"Roberto Renino": "img/Roberto Renino.jpg", "Candidato Pres B": "img/pres_b.jpg"}
CANDIDATI_C = {
    "Lorenzo Cogliolo": "img/Lorenzo Cogliolo.jpg", "Margherita Monti 2": "img/Margherita Monti.jpg",
    "Marco Zac Di Fraia": "img/Marco Zac Di Fraia.jpg", "Mara Moreale": "img/Mara Moreale.jpg",
    "Consigliere 5": "img/c5.jpg", "Consigliere 6": "img/c6.jpg"
}

texts = {
    "it": {
        "title": "Scheda Elettorale", "h1": "1. Elezione del Presidente", "h2": "2. Elezione del Consiglio Direttivo",
        "pick_p": "Scegli il Presidente:", "pick_c_info": "Seleziona 4 membri diversi per il Consiglio:",
        "c_label": "Consigliere", "submit": "INVIA VOTO DEFINITIVO", "error": "⚠️ Seleziona tutti i candidati.",
        "success": "Voto registrato!", "voted_err": "Hai già votato."
    },
    "en": {
        "title": "Ballot Paper", "h1": "1. Election of the President", "h2": "2. Election of the Board of Directors",
        "pick_p": "Choose the President:", "pick_c_info": "Select 4 different members for the Board:",
        "c_label": "Board Member", "submit": "SUBMIT FINAL VOTE", "error": "⚠️ Please select all candidates.",
        "success": "Vote registered!", "voted_err": "You have already voted."
    }
}

# --- 4. LOGICA ---
def ha_gia_votato(nome):
    if not os.path.isfile(FILE_REGISTRO_VOTANTI): return False
    with open(FILE_REGISTRO_VOTANTI, "r") as f:
        return nome in f.read().splitlines()

def salva_voto(voto, nome):
    df = pd.DataFrame([voto])
    df.to_csv(FILE_RISULTATI, mode='a', index=False, header=not os.path.isfile(FILE_RISULTATI))
    with open(FILE_REGISTRO_VOTANTI, "a") as f:
        f.write(nome + "\n")

# --- 5. INTERFACCIA ---
if not st.session_state.loggato:
    st.title("🗳️ Accesso Elezioni Amel Italia")
    scelta = st.selectbox("Nome / Name:", ["-- Scegli / Select --"] + SOCI_AUTORIZZATI)
    if st.button("ACCEDI / LOGIN"):
        if scelta != "-- Scegli / Select --":
            if ha_gia_votato(scelta):
                st.error("Hai già votato / Already voted.")
            else:
                st.session_state.loggato = True
                st.session_state.nome_voto = scelta
                st.session_state.lang = "en" if scelta == "Alaa" else "it"
                st.rerun()
    
    with st.sidebar:
        if st.text_input("Admin", type="password") == "K_ammello123":
            if os.path.isfile(FILE_RISULTATI):
                st.download_button("Download CSV", pd.read_csv(FILE_RISULTATI).to_csv(index=False), "voti.csv")
    st.stop()

# Ora carichiamo le traduzioni in base alla lingua confermata
L = texts[st.session_state.lang]

st.title(f"{L['title']}: {st.session_state.nome_voto}")

# PRESIDENTE
st.header(L['h1'])
cp = st.columns(len(CANDIDATI_P))
for i, (nome, path) in enumerate(CANDIDATI_P.items()):
    with cp[i]:
        st.subheader(nome)
        if os.path.exists(path): st.image(path)

v_pres = st.selectbox(L['pick_p'], ["-- Select --"] + list(CANDIDATI_P.keys()))

st.divider()

# CONSIGLIO
st.header(L['h2'])
cc = st.columns(len(CANDIDATI_C))
for i, (nome, path) in enumerate(CANDIDATI_C.items()):
    with cc[i]:
        st.subheader(nome)
        if os.path.exists(path): st.image(path)

st.info(L['pick_c_info'])
clist = list(CANDIDATI_C.keys())
s1 = st.selectbox(f"{L['c_label']} 1", ["-- Select --"] + clist)
s2 = st.selectbox(f"{L['c_label']} 2", ["-- Select --"] + [c for c in clist if c != s1])
s3 = st.selectbox(f"{L['c_label']} 3", ["-- Select --"] + [c for c in clist if c not in [s1, s2]])
s4 = st.selectbox(f"{L['c_label']} 4", ["-- Select --"] + [c for c in clist if c not in [s1, s2, s3]])

if st.button(L['submit']):
    if "-- Select --" in [v_pres, s1, s2, s3, s4]:
        st.error(L['error'])
    else:
        salva_voto({"P": v_pres, "C1": s1, "C2": s2, "C3": s3, "C4": s4}, st.session_state.nome_voto)
        st.success(L['success'])
        st.balloons()
        time.sleep(2)
        st.session_state.loggato = False
        st.rerun()
