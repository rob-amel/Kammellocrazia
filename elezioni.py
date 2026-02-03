import streamlit as st
import pandas as pd
import os
import time

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni Amel Italia", layout="wide")

# CSS OTTIMIZZATO: Forza l'arrotondamento rimuovendo i contenitori bianchi di Streamlit
st.markdown("""
    <style>
    .candidate-card {
        text-align: center;
        padding: 15px;
        border: 1px solid #eee;
        border-radius: 15px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Selettore mirato per l'immagine interna */
    [data-testid="stImage"] > img {
        border-radius: 50% !important;
        aspect-ratio: 1 / 1 !important;
        object-fit: cover !important;
        border: 4px solid #007bff !important;
        width: 150px !important;
        height: 150px !important;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """, unsafe_allow_html=True)

FILE_RISULTATI = "risultati_anonimi.csv"
FILE_REGISTRO_VOTANTI = "registro_voto_effettuato.txt"

# LISTA SOCI AGGIORNATA
SOCI_AUTORIZZATI = sorted([
    "Roberto R", "Roberto V", "Andrea", "Marco", "Mara", "Federica", "Giulia", 
    "Chiara", "Alaa", "Costanza", "Lorenzo", "Margherita", "Sofia", 
    "Stefania", "Marcello", "Matilde", "Tommaso", "Leonardo"
])

# DATI CANDIDATI (Nomi e percorsi aggiornati)
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
                st.error(f"Spiacente, {scelta} ha già votato.")
            else:
                st.session_state.loggato, st.session_state.nome_voto = True, scelta
                st.rerun()
    
    with st.sidebar:
        st.header("Area Amministratore")
        if st.text_input("Password Admin", type="password") == "K_ammello123":
            if os.path.isfile(FILE_RISULTATI):
                st.download_button("SCARICA RISULTATI CSV", pd.read_csv(FILE_RISULTATI).to_csv(index=False), "voti_elezioni.csv")
            else:
                st.info("Nessun voto registrato.")
    st.stop()

# --- INTERFACCIA DI VOTO ---
st.title(f"Scheda Elettorale: {st.session_state.nome_voto}")

# VISUALIZZAZIONE FOTO CANDIDATI
st.header("Candidati alla Presidenza")
cols_p = st.columns(len(CANDIDATI_P))
for i, (nome, img_path) in enumerate(CANDIDATI_P.items()):
    with cols_p[i]:
        st.markdown('<div class="candidate-card">', unsafe_allow_html=True)
        if os.path.exists(img_path):
            st.image(img_path)
        else:
            st.warning(f"Foto di {nome} non trovata")
        st.write(f"**{nome}**")
        st.markdown('</div>', unsafe_allow_html=True)

st.header("Candidati al Consiglio Direttivo")
cols_c = st.columns(len(CANDIDATI_C))
for i, (nome, img_path) in enumerate(CANDIDATI_C.items()):
    with cols_c[i]:
        st.markdown('<div class="candidate-card">', unsafe_allow_html=True)
        if os.path.exists(img_path):
            st.image(img_path)
        else:
            st.warning(f"Foto di {nome} non trovata")
        st.write(f"**{nome}**")
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# SEZIONE SELEZIONE (DINAMICA - Scomparsa nomi già scelti)
st.header("Esprimi il tuo voto")
v_pres = st.selectbox("Seleziona il Presidente:", ["-- Seleziona --"] + list(CANDIDATI_P.keys()))

st.subheader("Membri del Consiglio")
st.info("Scegli 4 membri diversi. Ogni nome selezionato sparirà dagli slot successivi.")
c_list = list(CANDIDATI_C.keys())

s1 = st.selectbox("Consigliere 1", ["-- Seleziona --"] + c_list)
s2 = st.selectbox("Consigliere 2", ["-- Seleziona --"] + [c for c in c_list if c != s1])
s3 = st.selectbox("Consigliere 3", ["-- Seleziona --"] + [c for c in c_list if c not in [s1, s2]])
s4 = st.selectbox("Consigliere 4", ["-- Seleziona --"] + [c for c in c_list if c not in [s1, s2, s3]])

st.divider()

if st.button("INVIA VOTO DEFINITIVO"):
    voti_c = [s1, s2, s3, s4]
    if "-- Seleziona --" in [v_pres] + voti_c:
        st.error("⚠️ Errore: Devi selezionare tutti i 5 candidati richiesti (1 Presidente e 4 Consiglieri).")
    else:
        voto_finale = {
            "Presidente": v_pres, 
            "Consigliere_1": s1, 
            "Consigliere_2": s2, 
            "Consigliere_3": s3, 
            "Consigliere_4": s4
        }
        salva_voto(voto_finale, st.session_state.nome_voto)
        st.success("Voto registrato con successo! La sessione verrà chiusa.")
        st.balloons()
        time.sleep(3)
        # Log out automatico
        st.session_state.loggato = False
        st.session_state.nome_voto = ""
        st.rerun()
