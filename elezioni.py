import streamlit as st
import pandas as pd
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni APS - Voto Segreto", layout="centered")

FILE_RISULTATI = "risultati_anonimi.csv"
FILE_REGISTRO_VOTANTI = "registro_chi_ha_votato.txt"

# LISTA AVENTI DIRITTO (Aggiornata e pulita dai duplicati)
SOCI_AUTORIZZATI = sorted([
    "Roberto", "Andrea", "Marco", "Mara", "Federica", "Giulia", 
    "Chiara", "Alaa", "Costanza", "Lorenzo", "Margherita", 
    "Sofia", "Stefania", "Marcello", "Matilde", "Tommaso", "Leonardo"
])

CANDIDATI_PRESIDENTE = ["INSERIRE NOME QUI 1", "INSERIRE NOME QUI 2", "Scheda Bianca"]
CANDIDATI_CONSIGLIO = ["NOME 1", "NOME 2", "NOME 3", "NOME 4", "NOME 5", "Scheda Bianca"]

# --- FUNZIONI DI SISTEMA ---
def ha_gia_votato(nome_socio):
    if not os.path.isfile(FILE_REGISTRO_VOTANTI):
        return False
    with open(FILE_REGISTRO_VOTANTI, "r") as f:
        votanti = f.read().splitlines()
    return nome_socio in votanti

def registra_voto_segreto(dati_voto, nome_socio):
    # Salva il voto (ANONIMO)
    df = pd.DataFrame([dati_voto])
    if not os.path.isfile(FILE_RISULTATI):
        df.to_csv(FILE_RISULTATI, index=False)
    else:
        df.to_csv(FILE_RISULTATI, mode='a', index=False, header=False)
    
    # Segna il nome nel registro per impedire il rientro
    with open(FILE_REGISTRO_VOTANTI, "a") as f:
        f.write(nome_socio + "\n")

# --- GESTIONE SESSIONE ---
if 'loggato' not in st.session_state:
    st.session_state.loggato = False
if 'user_nome' not in st.session_state:
    st.session_state.user_nome = ""

# --- SCHERMATA DI LOGIN ---
if not st.session_state.loggato:
    st.title("🗳️ Accesso Votazioni APS")
    st.write("Seleziona il tuo nome per accedere alla cabina elettorale digitale.")
    
    nome_selezionato = st.selectbox("Io sono:", ["-- Seleziona il tuo nome --"] + SOCI_AUTORIZZATI)
    
    if st.button("ACCEDI AL VOTO"):
        if nome_selezionato == "-- Seleziona il tuo nome --":
            st.error("Per favore, seleziona il tuo nome dalla lista.")
        elif ha_gia_votato(nome_selezionato):
            st.error(f"Spiacente {nome_selezionato}, risulta che tu abbia già espresso il tuo voto.")
        else:
            st.session_state.loggato = True
            st.session_state.user_nome = nome_selezionato
            st.rerun()
    
    # Area Admin nascosta nella login per comodità
    with st.expander("Accesso Amministratore"):
        pass_admin = st.text_input("Password", type="password")
        if pass_admin == "admin_aps_2024":
            if os.path.isfile(FILE_RISULTATI):
                st.download_button("SCARICA VOTI (CSV)", pd.read_csv(FILE_RISULTATI).to_csv(index=False), "risultati.csv")
            else:
                st.warning("Nessun voto registrato.")
    st.stop()

# --- INTERFACCIA DI VOTO (Accessibile solo dopo Login) ---
st.title(f"Cabina Elettorale: {st.session_state.user_nome}")
st.warning("Il tuo voto è segreto. Il sistema registra che hai votato, ma non associa il tuo nome alle tue scelte.")

with st.form("scheda"):
    # SEZIONE 1
    st.header("1. Elezione Presidente")
    voto_p = st.radio("Scegli un candidato Presidente:", CANDIDATI_PRESIDENTE)
    
    st.markdown("---")
    
    # SEZIONE 2
    st.header("2. Elezione Consiglio Direttivo")
    st.write("Seleziona 4 nomi diversi.")
    
    s1 = st.selectbox("Primo Consigliere", ["Seleziona..."] + CANDIDATI_CONSIGLIO)
    
    # Filtri dinamici per evitare doppioni
    opz2 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or c != s1]
    s2 = st.selectbox("Secondo Consigliere", ["Seleziona..."] + opz2)
    
    opz3 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or (c != s1 and c != s2)]
    s3 = st.selectbox("Terzo Consigliere", ["Seleziona..."] + opz3)
    
    opz4 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or (c not in [s1, s2, s3])]
    s4 = st.selectbox("Quarto Consigliere", ["Seleziona..."] + opz4)

    invia = st.form_submit_button("INVIA IL VOTO DEFINITIVAMENTE")

    if invia:
        if "Seleziona..." in [s1, s2, s3, s4]:
            st.error("Devi completare tutti i 4 slot del Consiglio.")
        else:
            voto_data = {
                "Presidente": voto_p,
                "Consigliere_1": s1,
                "Consigliere_2": s2,
                "Consigliere_3": s3,
                "Consigliere_4": s4
            }
            registra_voto_segreto(voto_data, st.session_state.user_nome)
            st.success("Voto inviato! Grazie per aver partecipato.")
            st.balloons()
            # Pulizia sessione
            st.session_state.loggato = False
            st.session_state.user_nome = ""
            st.info("La sessione è stata chiusa per proteggere la tua privacy.")
