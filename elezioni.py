import streamlit as st
import pandas as pd
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni APS", layout="centered")

FILE_RISULTATI = "risultati_anonimi.csv"
FILE_REGISTRO_VOTANTI = "registro_voto_effettuato.txt"

# LISTA SOCI (Nomi esatti come richiesto)
SOCI_AUTORIZZATI = sorted([
    "Roberto", "Andrea", "Marco", "Mara", "Federica", "Giulia", 
    "Chiara", "Alaa", "Costanza", "Lorenzo", "Margherita", 
    "Sofia", "Stefania", "Marcello", "Matilde", "Tommaso", "Leonardo"
])

CANDIDATI_PRESIDENTE = ["INSERIRE NOME QUI 1", "INSERIRE NOME QUI 2", "Scheda Bianca"]
CANDIDATI_CONSIGLIO = ["CANDIDATO 1", "CANDIDATO 2", "CANDIDATO 3", "CANDIDATO 4", "CANDIDATO 5", "Scheda Bianca"]

# --- FUNZIONI LOGICHE ---
def ha_gia_votato(nome_selezionato):
    if not os.path.isfile(FILE_REGISTRO_VOTANTI):
        return False
    with open(FILE_REGISTRO_VOTANTI, "r") as f:
        lista_nomi = f.read().splitlines()
    return nome_selezionato in lista_nomi

def salva_voto_segreto(voto_dati, nome_utente):
    # Salva le preferenze (senza nome)
    df = pd.DataFrame([voto_dati])
    if not os.path.isfile(FILE_RISULTATI):
        df.to_csv(FILE_RISULTATI, index=False)
    else:
        df.to_csv(FILE_RISULTATI, mode='a', index=False, header=False)
    
    # Registra che questo nome ha votato
    with open(FILE_REGISTRO_VOTANTI, "a") as f:
        f.write(nome_utente + "\n")

# --- INTERFACCIA ---

# Controllo sessione
if 'identita_confermata' not in st.session_state:
    st.session_state.identita_confermata = False
    st.session_state.nome_voto = ""

# --- SCHERMATA LOGIN (Solo Nomi) ---
if not st.session_state.identita_confermata:
    st.title("🗳️ Elezioni APS - Accesso")
    st.write("Seleziona il tuo nome per votare.")
    
    scelta = st.selectbox("Seleziona il tuo nome:", ["-- Scegli dalla lista --"] + SOCI_AUTORIZZATI)
    
    if st.button("ACCEDI ALLA SCHEDA DI VOTO"):
        if scelta == "-- Scegli dalla lista --":
            st.error("Devi selezionare un nome per procedere.")
        elif ha_gia_votato(scelta):
            st.error(f"Attenzione: {scelta} ha già inviato un voto. Non è possibile votare due volte.")
        else:
            st.session_state.identita_confermata = True
            st.session_state.nome_voto = scelta
            st.rerun()

    # Accesso Admin nascosto
    with st.sidebar:
        st.header("Admin")
        p_admin = st.text_input("Password Amministratore", type="password")
        if p_admin == "admin_aps_2026":
            if os.path.isfile(FILE_RISULTATI):
                st.download_button("SCARICA RISULTATI CSV", pd.read_csv(FILE_RISULTATI).to_csv(index=False), "voti.csv")
            else:
                st.info("Nessun voto registrato.")
    st.stop()

# --- SCHERMATA DI VOTO (Anonima) ---
st.title(f"Scheda Elettorale di {st.session_state.nome_voto}")
st.info("La tua identità è verificata, ma le tue scelte resteranno segrete.")

with st.form("modulo_voto"):
    # Sezione 1
    st.subheader("1. Elezione Presidente")
    voto_p = st.radio("Candidato:", CANDIDATI_PRESIDENTE)
    
    st.divider()
    
    # Sezione 2
    st.subheader("2. Elezione Consiglio Direttivo")
    st.write("Scegli 4 candidati diversi (o Scheda Bianca).")
    
    s1 = st.selectbox("Membro 1", ["Seleziona..."] + CANDIDATI_CONSIGLIO)
    
    opz2 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or c != s1]
    s2 = st.selectbox("Membro 2", ["Seleziona..."] + opz2)
    
    opz3 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or (c not in [s1, s2])]
    s3 = st.selectbox("Membro 3", ["Seleziona..."] + opz3)
    
    opz4 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or (c not in [s1, s2, s3])]
    s4 = st.selectbox("Membro 4", ["Seleziona..."] + opz4)

    conferma = st.form_submit_button("INVIA VOTO DEFINITIVO")

    if conferma:
        if "Seleziona..." in [s1, s2, s3, s4]:
            st.error("Compila tutti i campi del Consiglio (usa 'Scheda Bianca' se vuoi lasciare vuoto).")
        else:
            voto_finale = {
                "Presidente": voto_p,
                "Consigliere_1": s1,
                "Consigliere_2": s2,
                "Consigliere_3": s3,
                "Consigliere_4": s4
            }
            salva_voto_segreto(voto_finale, st.session_state.nome_voto)
            st.success("Voto inviato con successo! Grazie.")
            st.balloons()
            # Reset sessione
            st.session_state.identita_confermata = False
            st.session_state.nome_voto = ""
            st.info("Sessione chiusa automaticamente.")
