import streamlit as st
import pandas as pd
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni APS - Voto Segreto", layout="centered")

FILE_RISULTATI = "risultati_anonimi.csv"
FILE_REGISTRO_VOTANTI = "registro_chi_ha_votato.txt"

# LISTA AVENTI DIRITTO
SOCI_AUTORIZZATI = [
    "Roberto", "Andrea", "Marco", "Mara", "Federica", "Giulia", 
    "Chiara", "Alaa", "Costanza", "Lorenzo", "Margherita", 
    "Sofia", "Stefania", "Marcello", "Matilde", "Tommaso", "Leonardo"
]

CANDIDATI_PRESIDENTE = ["INSERIRE NOME QUI 1", "INSERIRE NOME QUI 2", "Scheda Bianca"]
CANDIDATI_CONSIGLIO = ["NOME 1", "NOME 2", "NOME 3", "NOME 4", "NOME 5", "Scheda Bianca"]

# --- FUNZIONI DI CONTROLLO ---
def ha_gia_votato(nome_socio):
    if not os.path.isfile(FILE_REGISTRO_VOTANTI):
        return False
    with open(FILE_REGISTRO_VOTANTI, "r") as f:
        votanti = f.read().splitlines()
    return nome_socio in votanti

def registra_voto_segreto(dati_voto, nome_socio):
    # 1. Salva il voto nel file dei risultati (SENZA NOME)
    df = pd.DataFrame([dati_voto])
    if not os.path.isfile(FILE_RISULTATI):
        df.to_csv(FILE_RISULTATI, index=False)
    else:
        df.to_csv(FILE_RISULTATI, mode='a', index=False, header=False)
    
    # 2. Segna il socio come "ha votato" nel registro separato
    with open(FILE_REGISTRO_VOTANTI, "a") as f:
        f.write(nome_socio + "\n")

# --- LOGICA DI ACCESSO ---
if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False
    st.session_state.nome_socio = ""

if not st.session_state.autenticato:
    st.title("🗳️ Accesso al Voto")
    nome_input = st.selectbox("Seleziona il tuo nome:", [""] + sorted(list(set(SOCI_AUTORIZZATI))))
    
    if st.button("Entra nella cabina elettorale"):
        if nome_input == "":
            st.warning("Seleziona il tuo nome.")
        elif ha_gia_votato(nome_input):
            st.error(f"Spiacente {nome_input}, risulta che tu abbia già votato.")
        else:
            st.session_state.autenticato = True
            st.session_state.nome_socio = nome_input
            st.rerun()
    st.stop()

# --- INTERFACCIA DI VOTO ---
st.title("Cabina Elettorale")
st.info(f"Utente: **{st.session_state.nome_socio}** | Il tuo voto rimarrà anonimo.")

with st.form("scheda_voto"):
    st.header("1. Elezione Presidente")
    voto_p = st.radio("Seleziona un candidato:", CANDIDATI_PRESIDENTE)

    st.markdown("---")
    st.header("2. Elezione Consiglio Direttivo (4 slot)")
    st.caption("Puoi votare fino a 4 persone diverse. Un nome scelto in uno slot sparisce dagli altri.")

    s1 = st.selectbox("Slot 1", ["Seleziona..."] + CANDIDATI_CONSIGLIO)
    
    opz2 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or c != s1]
    s2 = st.selectbox("Slot 2", ["Seleziona..."] + opz2)
    
    opz3 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or (c != s1 and c != s2)]
    s3 = st.selectbox("Slot 3", ["Seleziona..."] + opz3)
    
    opz4 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or (c not in [s1, s2, s3])]
    s4 = st.selectbox("Slot 4", ["Seleziona..."] + opz4)

    conferma = st.form_submit_button("INVIA SCHEDA")

    if conferma:
        if "Seleziona..." in [s1, s2, s3, s4]:
            st.error("Compila tutti i 4 slot del consiglio (usa 'Scheda Bianca' se necessario).")
        else:
            voto_finale = {
                "Presidente": voto_p,
                "Consigliere_1": s1,
                "Consigliere_2": s2,
                "Consigliere_3": s3,
                "Consigliere_4": s4
            }
            registra_voto_segreto(voto_finale, st.session_state.nome_socio)
            st.success("Voto registrato con successo!")
            st.balloons()
            st.session_state.autenticato = False
            st.info("Sessione chiusa. Grazie!")

# --- AREA ADMIN (SIDEBAR) ---
with st.sidebar:
    st.header("🔒 Area Amministratore")
    password_admin = st.text_input("Inserisci Password Admin", type="password")
    
    # Password suggerita: admin_aps_2024 (cambiala qui sotto)
    if password_admin == "admin_aps_2024":
        st.success("Accesso Admin Garantito")
        if os.path.isfile(FILE_RISULTATI):
            df = pd.read_csv(FILE_RISULTATI)
            st.write(f"Voti totali ricevuti: {len(df)}")
            st.download_button(
                label="Scarica Risultati (CSV)",
                data=df.to_csv(index=False),
                file_name="risultati_finali.csv",
                mime="text/csv"
            )
        else:
            st.info("Ancora nessun voto nel database.")import streamlit as st
import pandas as pd
import os

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="Elezioni APS", layout="centered")

FILE_VOTI = "voti_elezioni.csv"
# Lista soci autorizzati (Puoi caricarla da un altro CSV se preferisci)
SOCI_AUTORIZZATI = ["SOCIO001", "SOCIO002", "SOCIO003", "SOCIO004", "SOCIO005"] 

CANDIDATI_PRESIDENTE = ["INSERIRE NOME QUI 1", "INSERIRE NOME QUI 2", "Scheda Bianca"]
CANDIDATI_CONSIGLIO = ["NOME 1", "NOME 2", "NOME 3", "NOME 4", "NOME 5", "Scheda Bianca"]

# --- FUNZIONI UTILI ---
def ha_gia_votato(socio_id):
    if not os.path.isfile(FILE_VOTI):
        return False
    df = pd.read_csv(FILE_VOTI)
    return socio_id in df['ID_Socio'].astype(str).values

def salva_voto(dati):
    df = pd.DataFrame([dati])
    if not os.path.isfile(FILE_VOTI):
        df.to_csv(FILE_VOTI, index=False)
    else:
        df.to_csv(FILE_VOTI, mode='a', index=False, header=False)

# --- INTERFACCIA DI LOGIN ---
if 'autenticato' not in st.session_state:
    st.session_state.autenticato = False
    st.session_state.socio_id = ""

if not st.session_state.autenticato:
    st.title("🔑 Accesso Area Voto")
    input_id = st.text_input("Inserisci il tuo Codice Socio (es. SOCIO001):").strip().upper()
    
    if st.button("Accedi"):
        if input_id in SOCI_AUTORIZZATI:
            if ha_gia_votato(input_id):
                st.error("Risulta che tu abbia già espresso il tuo voto. Non è possibile votare due volte.")
            else:
                st.session_state.autenticato = True
                st.session_state.socio_id = input_id
                st.rerun()
        else:
            st.error("Codice Socio non valido.")
    
    st.stop() # Blocca l'esecuzione qui finché non si è loggati

# --- INTERFACCIA DI VOTO (Se autenticato) ---
st.title(f"🗳️ Benvenuto Socio {st.session_state.socio_id}")
st.info("Esprimi le tue preferenze e conferma in fondo alla pagina.")

# SEZIONE 1: PRESIDENTE
st.header("1. Elezione Presidente")
voto_pres = st.radio("Candidato Presidente:", CANDIDATI_PRESIDENTE)

st.markdown("---")

# SEZIONE 2: CONSIGLIO DIRETTIVO
st.header("2. Elezione Consiglio Direttivo (4 slot)")

col1, col2 = st.columns(2)
with col1:
    s1 = st.selectbox("Slot 1:", ["Seleziona..."] + CANDIDATI_CONSIGLIO)
    # Filtro dinamico per Slot 2
    opz2 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or c != s1]
    s2 = st.selectbox("Slot 2:", ["Seleziona..."] + opz2)

with col2:
    # Filtro dinamico per Slot 3
    opz3 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or c not in [s1, s2]]
    s3 = st.selectbox("Slot 3:", ["Seleziona..."] + opz3)
    # Filtro dinamico per Slot 4
    opz4 = [c for c in CANDIDATI_CONSIGLIO if c == "Scheda Bianca" or c not in [s1, s2, s3]]
    s4 = st.selectbox("Slot 4:", ["Seleziona..."] + opz4)

if st.button("CONFERMA E INVIA VOTO"):
    voti_c = [s1, s2, s3, s4]
    if "Seleziona..." in voti_c:
        st.error("Devi compilare tutti e 4 gli slot del Consiglio (puoi usare 'Scheda Bianca').")
    else:
        dati_voto = {
            "ID_Socio": st.session_state.socio_id,
            "Presidente": voto_pres,
            "Consigliere_1": s1,
            "Consigliere_2": s2,
            "Consigliere_3": s3,
            "Consigliere_4": s4
        }
        salva_voto(dati_voto)
        st.success("Voto inviato! La sessione verrà chiusa.")
        # Reset sessione per sicurezza
        st.session_state.autenticato = False 
        st.balloons()
        st.info("Puoi chiudere la pagina.")

# --- ADMIN PANEL (Sidebar) ---
with st.sidebar:
    st.header("Area Amministratore")
    pwd = st.text_input("Password Admin", type="password")
    if pwd == "admin_aps_2024":
        if os.path.isfile(FILE_VOTI):
            df_risultati = pd.read_csv(FILE_VOTI)
            st.write(f"Voti totali: {len(df_risultati)}")
            st.download_button("Scarica Risultati CSV", df_risultati.to_csv(index=False), "risultati.csv")
        else:
            st.write("Nessun voto presente.")

