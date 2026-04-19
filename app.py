import streamlit as st
from scraper import scrape_directory_index, extract_personal_website, scrape_professor_data
from ai_agent import find_best_matches, generate_dossier, draft_outreach_email, model

# --- PAGE CONFIG & STYLING ---
st.set_page_config(page_title="Faculty Connect", page_icon="🎓", layout="centered")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #2D6CC0;'>🎓 UCR Faculty Matchmaker</h1>
    <p style='text-align: center; font-size: 18px; color: #64748B;'>AI-Powered Undergraduate Research Networking</p>
    <hr>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "step" not in st.session_state: st.session_state.step = 1
if "directory_data" not in st.session_state: st.session_state.directory_data = []
if "matches" not in st.session_state: st.session_state.matches = ""
if "match_history" not in st.session_state: st.session_state.match_history = ""
if "major" not in st.session_state: st.session_state.major = ""
if "interest" not in st.session_state: st.session_state.interest = ""

# --- STEP 1: INITIAL SEARCH ---
if st.session_state.step == 1:
    st.header("Step 1: Discover Your Match")
    st.session_state.major = st.text_input("What is your major?", placeholder="e.g., Computer Science")
    st.session_state.interest = st.text_input("What is your research interest?", placeholder="e.g., Machine Learning")

    if st.button("Scan Directory & Find Matches", type="primary"):
        if not st.session_state.major or not st.session_state.interest:
            st.warning("Please enter both fields.")
        else:
            with st.spinner("Loading directory cache..."):
                st.session_state.directory_data = scrape_directory_index()
            if not st.session_state.directory_data:
                st.error("Could not load directory data.")
            else:
                with st.spinner("Analyzing profiles..."):
                    st.session_state.matches = find_best_matches(st.session_state.directory_data, st.session_state.interest)
                    st.session_state.step = 2
                    st.rerun()

# --- STEP 2: AI MATCHES ---
elif st.session_state.step == 2:
    st.header("Step 2: AI Match Results")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Profiles Scanned", f"{len(st.session_state.directory_data)}")
    col2.metric("Target Major", st.session_state.major)
    col3.metric("Status", "Honest Matches Found")
    
    # Premium UI Card for Matches
    custom_card = f"""
    <div style="
        background-color: #1E293B; 
        padding: 20px; 
        border-radius: 10px; 
        border-left: 5px solid #F59E0B; 
        color: #F8FAFC; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
        font-size: 16px; 
        line-height: 1.6;">
        {st.session_state.matches}
    </div>
    """
    st.markdown(custom_card, unsafe_allow_html=True)
    
    if st.button("🔄 Suggest 3 Different Professors"):
        with st.spinner("Digging deeper into the directory..."):
            st.session_state.match_history += f"\n{st.session_state.matches}"
            st.session_state.matches = find_best_matches(
                st.session_state.directory_data, 
                st.session_state.interest,
                st.session_state.match_history
            )
            st.rerun()
            
    st.divider()
    
    # --- STEP 3: DEEP DIVE ---
    st.subheader("Step 3: Deep Dive & Strategy")
    prof_names = [prof['name'] for prof in st.session_state.directory_data]
    selected_name = st.selectbox("Select a Professor to investigate:", prof_names)
    
    selected_prof_dict = next(prof for prof in st.session_state.directory_data if prof['name'] == selected_name)
    
    st.markdown(f"🔗 **[Click here to view {selected_name}'s official UCR Profile]({selected_prof_dict['url']})**")
    st.caption("Pro-Tip: If the automatic scraper fails, click the link above, find their personal Lab Website, and paste it below.")
    
    manual_url = st.text_input("Optional: Paste their personal Lab Website URL here:", placeholder="http://...")
    
    colA, colB = st.columns([1, 4])
    with colA:
        if st.button("Generate Strategy", type="primary"):
            if manual_url:
                target_url = manual_url
            else:
                with st.spinner("Hunting for lab website..."):
                    lab_url = extract_personal_website(selected_prof_dict['url'])
                    target_url = lab_url if lab_url else selected_prof_dict['url']
                
            with st.spinner(f"Vacuuming data from: {target_url}"):
                selected_prof_dict['research_text'] = scrape_professor_data(target_url)
                
            with st.spinner("Writing personalized dossier..."):
                st.session_state.current_dossier = generate_dossier(selected_prof_dict, st.session_state.major, st.session_state.interest)
            st.session_state.selected_prof_dict = selected_prof_dict
    with colB:
        if st.button("Start Over"):
            st.session_state.clear()
            st.rerun()

    # --- STEP 4: THE TOOLKIT (DOSSIER & EMAIL) ---
    if "current_dossier" in st.session_state:
        st.success("Strategy Dossier Generated Successfully!")
        
        # Premium UI Card for Dossier
        dossier_card = f"""
        <div style="
            background-color: #1E293B; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 5px solid #F59E0B; 
            color: #F8FAFC; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
            font-size: 16px; 
            line-height: 1.6;">
            {st.session_state.current_dossier}
        </div>
        """
        st.markdown(dossier_card, unsafe_allow_html=True)
        
        with st.expander("🔍 View Raw Scraped Lab Data"):
            st.write(st.session_state.selected_prof_dict.get('research_text', 'No raw text available.'))
            
        st.divider()
        st.subheader("Step 4: Make the Connection")
        
        # --- Email Drafter ---
        if st.button("✉️ Draft Cold Email"):
            with st.spinner("Writing email..."):
                email = draft_outreach_email(st.session_state.selected_prof_dict, st.session_state.major, st.session_state.interest, st.session_state.current_dossier)