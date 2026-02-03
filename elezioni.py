import streamlit as st
import pandas as pd
import os

# CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Elezioni APS - Votazione Online", layout="centered")

# --- DATABASE CANDIDATI (Modifica qui i nomi) ---
CANDIDATI_PRESIDENTE = ["INSERIRE NOME QUI 1", "INSERIRE NOME QUI 2", "Scheda Bianca"]
CANDIDATI_CONSIGLIO = ["NOME CONSIGLIERE 1", "NOME CONSIGLIERE 2", "NOME CONSIGLIERE 3", "NOME CONSIGLIERE 4", "NOME CONSIGLIERE 5", "Scheda Bianca"]

FILE_VOTI = "voti_elezioni.csv"

def salva_voto(dati):
    df = pd.DataFrame([dati])
    # Se il file non esiste, crea con header, altrimenti aggiunge riga
    if not os.path.isfile(FILE_VOTI):
        df.to_csv(FILE_VOTI, index=False)
    else:
        df.to_csv(FILE_VOTI, mode='a', index=False, header=False)

st.title("🗳️ Rinnovo Cariche Sociali APS")
st.markdown("---")

# SEZIONE 1: PRESIDENTE
st.header("Sezione 1: Elezione Presidente")
voto_pres = st.radio("Seleziona il candidato Presidente:", CANDIDATI_PRESIDENTE)

st.markdown("---")

# SEZIONE 2: CONSIGLIO DIRETTIVO (Logica di esclusione)
st.header("Sezione 2: Elezione Consiglio Direttivo")
st.info("Puoi esprimere fino a 4 preferenze diverse. Un candidato già selezionato non apparirà negli slot success.")

# Slot 1
opzioni_1 = CANDIDATI_CONSIGLIO
slot1 = st.selectbox("Primo membro del consiglio:", ["Seleziona..."] + opzioni_1)

# Slot 2 (Filtra Slot 1)
opzioni_2 = [c for c in CANDIDATI_CONSIGLIO if c != slot1 or c == "Scheda Bianca"]
slot2 = st.selectbox("Secondo membro del consiglio:", ["Seleziona..."] + opzioni_2)

# Slot 3 (Filtra Slot 1 e 2)
opzioni_3 = [c for c in CANDIDATI_CONSIGLIO if (c not in [slot1, slot2]) or c == "Scheda Bianca"]
slot3 = st.selectbox("Terzo membro del consiglio:", ["Seleziona..."] + opzioni_3)

# Slot 4 (Filtra Slot 1, 2 e 3)
opzioni_4 = [c for c in CANDIDATI_CONSIGLIO if (c not in [slot1, slot2, slot3]) or c == "Scheda Bianca"]
slot4 = st.selectbox("Quarto membro del consiglio:", ["Seleziona..."] + opzioni_4)

st.markdown("---")

# INVIO VOTO
if st.button("INVIA IL TUO VOTO"):
    # Validazione rapida
    voti_consiglio = [slot1, slot2, slot3, slot4]
    if "Seleziona..." in voti_consiglio:
        st.error("Per favore, completa tutte le selezioni del Consiglio Direttivo prima di inviare.")
    else:
        risultati = {
            "Presidente": voto_pres,
            "Consigliere_1": slot1,
            "Consigliere_2": slot2,
            "Consigliere_3": slot3,
            "Consigliere_4": slot4
        }
        salva_voto(risultati)
        st.success("Voto registrato con successo! Grazie per aver partecipato.")
        st.balloons()
        # Nota: In una web app reale qui andrebbe un redirect o un blocco sessione per evitare voti multipli.

# SEZIONE ADMIN (Accessibile solo via codice o URL segreto)
# Per scaricare il file, l'admin può aggiungere '?admin=true' all'URL o semplicemente gestire il file sul server.
if st.sidebar.checkbox("Accesso Admin"):
    password = st.sidebar.text_input("Inserisci Password Admin", type="password")
    if password == "admin123": # Cambia questa password
        if os.path.isfile(FILE_VOTI):
            with open(FILE_VOTI, "rb") as file:
                st.sidebar.download_button(
                    label="Scarica Risultati CSV",
                    data=file,
                    file_name="risultati_elezioni.csv",
                    mime="text/csv"
                )
        else:
            st.sidebar.warning("Nessun voto ancora registrato.")