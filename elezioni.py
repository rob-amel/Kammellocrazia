import streamlit as st
import pandas as pd
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni APS", layout="centered")

FILE_RISULTATI = "risultati_anonimi.csv"
FILE_REGISTRO_VOTANTI = "registro_voto_effettuato.txt"

# LISTA SOCI (Aggiornata con i due Roberto)
SOCI_AUTORIZZATI = sorted([
    "Roberto R", "Roberto V", "Andrea", "Marco", "Mara", "Federica", "Giulia", 
    "Chiara", "Alaa", "Costanza", "Lorenzo", "Margherita", 
    "Sofia", "Stefania", "Marcello", "Matilde", "Tommaso", "Leonardo"
])

# CANDIDATI (Sostituire i segnaposto con i nomi reali)
CANDIDATI_PRESIDENTE = ["INSERIRE NOME QUI 1", "INSERIRE NOME QUI 2"]
CANDIDATI_CONSIGLIO = ["NOME 1", "NOME 2", "NOME 3", "NOME 4", "NOME 5", "NOME 6", "NOME 7"]

# --- FUNZIONI LOGICHE ---
def ha_gia_votato(nome_selezionato):
    if not os.path.isfile(FILE_REGISTRO_VOTANTI):
        return False
    with open(FILE_REGISTRO_VOTANTI, "r") as f:
        lista_nomi = f.read().splitlines()
    return nome_selezionato in lista_nomi

def salva_voto_segreto(voto_dati, nome_utente):
    df = pd.DataFrame([voto_dati])
    if not os.path.isfile(FILE_RISULTATI):
        df.to_csv(FILE_RISULTATI, index=False)
    else:
        df.to_csv(FILE_RISULTATI, mode='a', index=False, header=False)
    
    with open(FILE_REGISTRO_VOTANTI, "a") as f:
        f.write(nome_utente + "\n")

# --- GESTIONE SESSIONE ---
if 'loggato' not in st.session_state:
    st.session_state.loggato = False
    st.session_state.nome_voto = ""

# --- LOGIN ---
if not st.session_state.loggato:
    st.title("🗳️ Accesso Elezioni APS")
    scelta = st.selectbox("Seleziona il tuo nome:", ["-- Scegli dalla lista --"] + SOCI_AUTORIZZATI)
    
    if st.button("ACCEDI"):
        if scelta == "-- Scegli dalla lista --":
            st.error("Seleziona il tuo nome.")
        elif ha_gia_votato(scelta):
            st.error(f"{scelta} ha già votato.")
        else:
            st.session_state.loggato = True
            st.session_state.nome_voto = scelta
            st.rerun()

    with st.sidebar:
        st.header("Admin")
        p_admin = st.text_input("Password Amministratore", type="password")
        if p_admin == "K_ammello123":
            if os.path.isfile(FILE_RISULTATI):
                st.download_button("SCARICA RISULTATI CSV", pd.read_csv(FILE_RISULTATI).to_csv(index=False), "voti.csv")
            else:
                st.info("Nessun voto.")
    st.stop()

# --- SCHERMATA DI VOTO ---
st.title("Scheda Elettorale")
st.warning(f"Socio: {st.session_state.nome_voto} | Il voto è segreto.")

with st.form("modulo_voto"):
    # PRESIDENTE
    st.subheader("1. Elezione Presidente")
    voto_p = st.radio("Seleziona il Presidente:", ["Scegli..."] + CANDIDATI_PRESIDENTE)
    
    st.divider()
    
    # CONSIGLIO (Filtri dinamici a cascata)
    st.subheader("2. Elezione Consiglio Direttivo")
    st.caption("Seleziona 4 membri differenti.")
    
    # Slot 1
    s1 = st.selectbox("Membro 1", ["Scegli..."] + CANDIDATI_CONSIGLIO)
    
    # Slot 2 (esclude s1)
    opz2 = [c for c in CANDIDATI_CONSIGLIO if c != s1]
    s2 = st.selectbox("Membro 2", ["Scegli..."] + opz2)
    
    # Slot 3 (esclude s1, s2)
    opz3 = [c for c in CANDIDATI_CONSIGLIO if c not in [s1, s2]]
    s3 = st.selectbox("Membro 3", ["Scegli..."] + opz3)
    
    # Slot 4 (esclude s1, s2, s3)
    opz4 = [c for c in CANDIDATI_CONSIGLIO if c not in [s1, s2, s3]]
    s4 = st.selectbox("Membro 4", ["Scegli..."] + opz4)

    invia = st.form_submit_button("INVIA VOTO")

    if invia:
        # Validazione: nessun "Scegli..." deve essere presente
        voti_consiglio = [s1, s2, s3, s4]
        if voto_p == "Scegli..." or "Scegli..." in voti_consiglio:
            st.error("ERRORE: Devi esprimere una preferenza per ogni carica (1 Presidente e 4 Consiglieri).")
        else:
            voto_finale = {
                "Presidente": voto_p,
                "Consigliere_1": s1,
                "Consigliere_2": s2,
                "Consigliere_3": s3,
                "Consigliere_4": s4
            }
            salva_voto_segreto(voto_finale, st.session_state.nome_voto)
            st.success("Voto registrato con successo!")
            st.balloons()
            st.session_state.loggato = False
            st.info("Sessione chiusa.")
