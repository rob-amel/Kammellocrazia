import streamlit as st
import pandas as pd
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni APS", layout="centered")

FILE_RISULTATI = "risultati_anonimi.csv"
FILE_REGISTRO_VOTANTI = "registro_voto_effettuato.txt"

# LISTA SOCI
SOCI_AUTORIZZATI = sorted([
    "Roberto R", "Roberto V", "Andrea", "Marco", "Mara", "Federica", "Giulia", 
    "Chiara", "Alaa", "Costanza", "Lorenzo", "Margherita", 
    "Sofia", "Stefania", "Marcello", "Matilde", "Tommaso", "Leonardo"
])

# CANDIDATI (Aggiorna qui i nomi reali)
CANDIDATI_PRESIDENTE = ["Candidato Pres A", "Candidato Pres B"]
CANDIDATI_CONSIGLIO = ["Consigliere 1", "Consigliere 2", "Consigliere 3", "Consigliere 4", "Consigliere 5", "Consigliere 6"]

# --- FUNZIONI LOGICHE ---
def ha_gia_votato(nome_selezionato):
    if not os.path.isfile(FILE_REGISTRO_VOTANTI):
        return False
    with open(FILE_REGISTRO_VOTANTI, "r") as f:
        return nome_selezionato in f.read().splitlines()

def salva_voto_segreto(voto_dati, nome_utente):
    df = pd.DataFrame([voto_dati])
    if not os.path.isfile(FILE_RISULTATI):
        df.to_csv(FILE_RISULTATI, index=False)
    else:
        df.to_csv(FILE_RISULTATI, mode='a', index=False, header=False)
    with open(FILE_REGISTRO_VOTANTI, "a") as f:
        f.write(nome_utente + "\n")

# --- LOGIN ---
if 'loggato' not in st.session_state:
    st.session_state.loggato = False
    st.session_state.nome_voto = ""

if not st.session_state.loggato:
    st.title("🗳️ Accesso Elezioni APS")
    scelta = st.selectbox("Seleziona il tuo nome:", ["-- Scegli dalla lista --"] + SOCI_AUTORIZZATI)
    
    if st.button("ACCEDI"):
        if scelta != "-- Scegli dalla lista --":
            if ha_gia_votato(scelta):
                st.error(f"{scelta} ha già votato.")
            else:
                st.session_state.loggato = True
                st.session_state.nome_voto = scelta
                st.rerun()
    
    # Area Admin in Sidebar
    with st.sidebar:
        st.header("Admin")
        p_admin = st.text_input("Password", type="password")
        if p_admin == "K_ammello123":
            if os.path.isfile(FILE_RISULTATI):
                st.download_button("SCARICA RISULTATI", pd.read_csv(FILE_RISULTATI).to_csv(index=False), "voti.csv")
    st.stop()

# --- INTERFACCIA DI VOTO DINAMICA ---
st.title("Scheda Elettorale")
st.info(f"Socio: **{st.session_state.nome_voto}**")

# 1. PRESIDENTE
st.subheader("1. Elezione Presidente")
voto_p = st.selectbox("Scegli il Presidente:", ["-- Seleziona --"] + CANDIDATI_PRESIDENTE)

st.divider()

# 2. CONSIGLIO (Filtro istantaneo senza st.form)
st.subheader("2. Elezione Consiglio Direttivo")
st.caption("I nomi già selezionati spariranno automaticamente dagli altri menu.")

# Slot 1
s1 = st.selectbox("Membro 1", ["-- Seleziona --"] + CANDIDATI_CONSIGLIO, key="s1")

# Slot 2 (Filtra s1)
opz2 = [c for c in CANDIDATI_CONSIGLIO if c != s1]
s2 = st.selectbox("Membro 2", ["-- Seleziona --"] + opz2, key="s2")

# Slot 3 (Filtra s1, s2)
opz3 = [c for c in CANDIDATI_CONSIGLIO if c not in [s1, s2]]
s3 = st.selectbox("Membro 3", ["-- Seleziona --"] + opz3, key="s3")

# Slot 4 (Filtra s1, s2, s3)
opz4 = [c for c in CANDIDATI_CONSIGLIO if c not in [s1, s2, s3]]
s4 = st.selectbox("Membro 4", ["-- Seleziona --"] + opz4, key="s4")

st.divider()

# Validazione e Invio
if st.button("INVIA VOTO DEFINITIVO"):
    voti_consiglio = [s1, s2, s3, s4]
    if voto_p == "-- Seleziona --" or "-- Seleziona --" in voti_consiglio:
        st.error("⚠️ Errore: Devi selezionare tutti i 5 membri richiesti (1 Presidente + 4 Consiglieri) prima di inviare.")
    else:
        voto_finale = {
            "Presidente": voto_p,
            "Consigliere_1": s1, "Consigliere_2": s2, 
            "Consigliere_3": s3, "Consigliere_4": s4
        }
        salva_voto_segreto(voto_finale, st.session_state.nome_voto)
        st.success("Voto registrato! Grazie.")
        st.balloons()
        # Reset per chiudere la sessione
        st.session_state.loggato = False
        st.session_state.nome_voto = ""
        # Piccola pausa per mostrare il successo prima del rerun
        import time
        time.sleep(2)
        st.rerun()
