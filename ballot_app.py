import streamlit as st
import time
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Amel Italia Elections", layout="wide")

# --- 2. GOOGLE SHEETS CONNECTION ---
@st.cache_resource
def get_google_sheet():
    """Connect to Google Sheets once"""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    if "gcp_credentials" in st.secrets:
        creds_dict = st.secrets["gcp_credentials"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    else:
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
    
    client = gspread.authorize(creds)
    spreadsheet = client.open("Amel Elections 2026")
    return spreadsheet

def get_voters():
    """Get list of people who already voted"""
    try:
        sheet = get_google_sheet().worksheet("Voters")
        records = sheet.col_values(1)[1:]
        return records
    except Exception as e:
        st.error(f"Connection error: {e}")
        return []

def has_already_voted(name):
    """Check if name has already voted"""
    return name in get_voters()

def save_vote(vote, name):
    """Save vote to Google Sheets"""
    try:
        spreadsheet = get_google_sheet()
        
        sheet_votes = spreadsheet.worksheet("Votes")
        row = [vote["P"]] + [vote[f"C{i+1}"] for i in range(NUM_BOARD_MEMBERS_TO_VOTE)]
        sheet_votes.append_row(row)
        
        sheet_voters = spreadsheet.worksheet("Voters")
        sheet_voters.append_row([name])
        
        return True
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

# --- 3. LOAD DATA FROM FILES ---
def load_members():
    """Load authorized members from file"""
    try:
        with open("members.txt", "r") as f:
            return sorted([line.strip() for line in f if line.strip()])
    except:
        return []

def load_candidates(filename):
    """Load candidates from file (format: name,image_path)"""
    candidates = {}
    try:
        with open(filename, "r") as f:
            for line in f:
                if "," in line:
                    name, path = line.strip().split(",", 1)
                    candidates[name.strip()] = path.strip()
    except:
        pass
    return candidates

AUTHORIZED_MEMBERS = load_members()
PRESIDENT_CANDIDATES = load_candidates("president_candidates.txt")
BOARD_CANDIDATES = load_candidates("board_candidates.txt")
NUM_BOARD_MEMBERS_TO_VOTE = min(4, len(BOARD_CANDIDATES))

# --- 4. SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'voter_name' not in st.session_state:
    st.session_state.voter_name = ""
if 'confirm_vote' not in st.session_state:
    st.session_state.confirm_vote = False
if 'lang' not in st.session_state:
    st.session_state.lang = "en"

# --- 5. CSS ---
st.markdown("""
    <style>
    .stMarkdown h3 {
        text-align: center;
        font-size: 1rem !important;
        background-color: rgba(128, 128, 128, 0.1); 
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
    </style>
    """, unsafe_allow_html=True)

# --- 6. TEXT LABELS (BILINGUAL) ---
LABELS = {
    "en": {
        "title": "Ballot Paper",
        "h1": "1. Election of the President",
        "h2": "2. Election of the Board of Directors",
        "pick_p": "Choose the President:",
        "pick_c_info": f"Select {NUM_BOARD_MEMBERS_TO_VOTE} members for the Board:",
        "c_label": "Board Member",
        "submit": "PROCEED TO VOTE",
        "confirm_title": "⚠️ Confirm your vote",
        "confirm_msg": "You are about to vote for:",
        "confirm_yes": "✅ CONFIRM VOTE",
        "confirm_no": "❌ Go back",
        "error": "⚠️ Please select all required candidates.",
        "error_duplicates": "⚠️ You selected the same candidate multiple times.",
        "success": "✅ Vote registered successfully!",
        "logout": "🚪 Exit",
        "president": "President"
    },
    "it": {
        "title": "Scheda Elettorale",
        "h1": "1. Elezione del Presidente",
        "h2": "2. Elezione del Consiglio Direttivo",
        "pick_p": "Scegli il Presidente:",
        "pick_c_info": f"Seleziona {NUM_BOARD_MEMBERS_TO_VOTE} membri per il Consiglio:",
        "c_label": "Consigliere",
        "submit": "PROCEDI AL VOTO",
        "confirm_title": "⚠️ Conferma il tuo voto",
        "confirm_msg": "Stai per votare:",
        "confirm_yes": "✅ CONFERMA VOTO",
        "confirm_no": "❌ Torna indietro",
        "error": "⚠️ Seleziona tutti i candidati richiesti.",
        "error_duplicates": "⚠️ Hai selezionato lo stesso candidato più volte.",
        "success": "✅ Voto registrato con successo!",
        "logout": "🚪 Esci",
        "president": "Presidente"
    }
}

# --- 7. FUNCTIONS ---
def logout():
    st.session_state.logged_in = False
    st.session_state.voter_name = ""
    st.session_state.confirm_vote = False
    st.session_state.lang = "en"

# --- 8. LOGIN PAGE (ALWAYS ENGLISH) ---
if not st.session_state.logged_in:
    st.title("🗳️ Amel Italia Elections")
    st.markdown("---")
    
    choice = st.selectbox("Select your name:", ["-- Select --"] + AUTHORIZED_MEMBERS)
    
    if st.button("🔑 LOGIN", type="primary"):
        if choice != "-- Select --":
            with st.spinner("Verifying..."):
                if has_already_voted(choice):
                    st.error("❌ You have already voted.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.voter_name = choice
                    # Alaa gets English, everyone else gets Italian
                    st.session_state.lang = "en" if choice == "Alaa" else "it"
                    st.rerun()
        else:
            st.warning("Please select a name")
    
    # Admin sidebar
    with st.sidebar:
        st.markdown("### Admin")
        pwd = st.text_input("Password", type="password")
        if pwd == st.secrets.get("admin_password"):
            st.success("Admin access granted")
            try:
                spreadsheet = get_google_sheet()
                
                sheet_votes = spreadsheet.worksheet("Votes")
                votes = sheet_votes.get_all_records()
                voters = get_voters()
                
                st.metric("Total votes", len(votes))
                st.write(f"**Voted ({len(voters)}):** {', '.join(voters)}")
                
                if votes:
                    st.markdown("---")
                    
                    st.markdown("### 🏆 President Results")
                    president_counts = {}
                    for v in votes:
                        p = v.get("P", "")
                        if p:
                            president_counts[p] = president_counts.get(p, 0) + 1
                    
                    sorted_presidents = sorted(president_counts.items(), key=lambda x: x[1], reverse=True)
                    for name, count in sorted_presidents:
                        st.write(f"**{name}:** {count} votes")
                    
                    st.markdown("---")
                    
                    st.markdown("### 🏆 Board Results")
                    board_counts = {}
                    for v in votes:
                        for i in range(1, 10):
                            c = v.get(f"C{i}", "")
                            if c:
                                board_counts[c] = board_counts.get(c, 0) + 1
                    
                    sorted_board = sorted(board_counts.items(), key=lambda x: x[1], reverse=True)
                    for name, count in sorted_board:
                        st.write(f"**{name}:** {count} votes")
                    
                    st.markdown("---")
                    
                    with st.expander("📊 View raw data"):
                        st.dataframe(votes)
                    
                    import pandas as pd
                    df = pd.DataFrame(votes)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="election_results.csv",
                        mime="text/csv"
                    )
                
            except Exception as e:
                st.error(f"Error: {e}")
    st.stop()

# --- 9. VOTING PAGE (LANGUAGE BASED ON USER) ---
L = LABELS[st.session_state.lang]

col_title, col_logout = st.columns([4, 1])
with col_title:
    st.title(f"🗳️ {L['title']}")
    st.markdown(f"**Voter:** {st.session_state.voter_name}")
with col_logout:
    if st.button(L['logout']):
        logout()
        st.rerun()

st.markdown("---")

# PRESIDENT
st.header(L['h1'])
cols_p = st.columns(len(PRESIDENT_CANDIDATES))
for i, (name, path) in enumerate(PRESIDENT_CANDIDATES.items()):
    with cols_p[i]:
        st.subheader(name)
        try:
            st.image(path)
        except:
            pass

v_pres = st.selectbox(L['pick_p'], ["-- Select --"] + list(PRESIDENT_CANDIDATES.keys()))

st.markdown("---")

# BOARD
st.header(L['h2'])
cols_c = st.columns(len(BOARD_CANDIDATES))
for i, (name, path) in enumerate(BOARD_CANDIDATES.items()):
    with cols_c[i]:
        st.subheader(name)
        try:
            st.image(path)
        except:
            pass

st.info(L['pick_c_info'])

clist = list(BOARD_CANDIDATES.keys())
selections = []

for i in range(NUM_BOARD_MEMBERS_TO_VOTE):
    options = ["-- Select --"] + [c for c in clist if c not in selections]
    sel = st.selectbox(f"{L['c_label']} {i+1}", options, key=f"board_{i}")
    if sel != "-- Select --":
        selections.append(sel)

st.markdown("---")

# SUBMIT VOTE
if not st.session_state.confirm_vote:
    if st.button(L['submit'], type="primary"):
        if v_pres == "-- Select --" or len(selections) < NUM_BOARD_MEMBERS_TO_VOTE:
            st.error(L['error'])
        elif len(selections) != len(set(selections)):
            st.error(L['error_duplicates'])
        else:
            st.session_state.confirm_vote = True
            st.session_state.temp_vote = {"P": v_pres, **{f"C{i+1}": c for i, c in enumerate(selections)}}
            st.rerun()
else:
    st.warning(L['confirm_title'])
    st.markdown(f"**{L['confirm_msg']}**")
    st.markdown(f"- **{L['president']}:** {st.session_state.temp_vote['P']}")
    for i in range(NUM_BOARD_MEMBERS_TO_VOTE):
        st.markdown(f"- **{L['c_label']} {i+1}:** {st.session_state.temp_vote[f'C{i+1}']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(L['confirm_yes'], type="primary"):
            with st.spinner("Saving..."):
                if save_vote(st.session_state.temp_vote, st.session_state.voter_name):
                    st.success(L['success'])
                    st.balloons()
                    time.sleep(2)
                    logout()
                    st.rerun()
    with col2:
        if st.button(L['confirm_no']):
            st.session_state.confirm_vote = False
            st.rerun()