import streamlit as st
import pandas as pd
import os
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni Amel Italia", layout="wide")

# CSS AGGIORNATO PER ALLINEAMENTO PERFETTO E SUPPORTO TEMA CHIARO/SCURO
st.markdown("""
    <style>
    /* Uniforma gli slot dei nomi (subheader) */
    .stMarkdown h3 {
        text-align: center;
        font-size: 1rem !important;
        background-color: rgba(128, 128, 128, 0.1); 
        color: inherit;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 10px !important;
        min-height: 70px; /* Altezza fissa per allineare le foto sotto */
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Centratura e uniformità immagini */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        padding-bottom: 20px;
    }

    [data-testid="stImage"] img {
        border-radius: 12px;
        width: 100% !important;
        height: 180px !important; /* Altezza fissa per garantire l'allineamento orizzontale */
        object-fit: cover !important; /* Ritaglia l'immagine per riempire lo spazio senza distorcere */
        max-width: 180px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Riduce lo spazio tra le colonne per far stare tutto in una riga se possibile */
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

# 1. SEZIONE PRESIDENTE (Candidati + Votazione)
st.header("1. Elezione del Presidente")
cols_p = st.columns(len(CANDIDATI_P))
for i, (nome, img_path) in enumerate(CANDIDATI_P.items()):
    with cols_p[i]:
        st.subheader(nome)
        if os.path.exists(img_path):
            st.image(img_path)
        else:
            st.info("Immagine non disponibile")

v_pres = st.selectbox("Scegli il Presidente:", ["-- Seleziona --"] + list(CANDIDATI_P.keys()), key="voto_p")

st.divider()

# 2. SEZIONE CONSIGLIO (Candidati + Votazione)
st.header("2. Elezione del Consiglio Direttivo")

# Visualizzazione Candidati Consiglio (Allineati)
cols_c = st.columns(len(CANDIDATI_C))
for i, (nome, img_path) in enumerate(CANDIDATI_C.items()):
    with cols_c[i]:
        st.subheader(nome)
        if os.path.exists(img_path):
            st.image(img_path)
        else:
            st.info("Immagine non disponibile")

st.info("Seleziona 4 membri diversi per il Consiglio:")
c_list = list(CANDIDATI_C.keys())

# Menu a discesa per i Consiglieri
s1 = st.selectbox("Consigliere 1", ["-- Seleziona --"] + c_list, key="c1")
s2 = st.selectbox("Consigliere 2", ["-- Seleziona --"] + [c for c in c_list if c != s1], key="c2")
s3 = st.selectbox("Consigliere 3", ["-- Seleziona --"] + [c for c in c_list if c not in [s1, s2]], key="c3")
s4 = st.selectbox("Consigliere 4", ["-- Seleziona --"] + [c for c in c_list if c not in [s1, s2, s3]], key="c4")

st.divider()

# INVIO VOTO
if st.button("INVIA VOTO DEFINITIVO"):
    voti_c = [s1, s2, s3, s4]
    if v_pres == "-- Seleziona --" or "-- Seleziona --" in voti_c:
        st.error("⚠️ Errore: Assicurati di aver selezionato il Presidente e tutti i 4 Consiglieri.")
    else:
        voto_finale = {
            "Presidente": v_pres, 
            "Cons_1": s1, "Cons_2": s2, "Cons_3": s3, "Cons_4": s4
        }
        salva_voto(voto_finale, st.session_state.nome_voto)
        st.success("Voto registrato con successo!")
        st.balloons()
        time.sleep(2)
        st.session_state.loggato = False
        st.rerun()
