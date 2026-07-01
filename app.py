import streamlit as st
import google.generativeai as genai
import pandas as pd
from datetime import datetime

# ==========================================
# CONFIGURATION ET SETUP DE L'API GEMINI
# ==========================================
# Remplacez par votre clé API Google AI Studio
# genai.configure(api_key="VOTRE_CLE_API_GEMINI")

# ==========================================
# CONFIGURATION DE LA PAGE & STYLE (DESIGN MODERNE)
# ==========================================
st.set_page_config(
    page_title="AURA - Votre Hub Académique",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pour le look "Lycée d'Excellence / Tech Moderne"
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366F1, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #6B7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .card {
        background-color: #F9FAFB;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# GESTION DE L'AUTHENTIFICATION (STRICTE)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def login_page():
    st.markdown("<div style='text-align: center; margin-top: 5rem;'>", unsafe_allow_html=True)
    # Affichage du Logo Design demandé
    st.markdown("""
        <div style="display: inline-block; padding: 20px; background: linear-gradient(135deg, #6366F1, #A855F7); border-radius: 24px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3);">
            <span style="font-size: 3rem; color: white; font-weight: 800; letter-spacing: -1px;">A U R A</span>
        </div>
        <h2 style='font-weight: 700;'>Connexion Obligatoire</h2>
        <p style='color: #6B7280;'>Lycée d'Excellence Privé Nevers — Montpellier</p>
    """, unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Identifiant (Email)", placeholder="votre.nom@lycee-nevers.fr")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••")
            
            if st.button("Se connecter", use_container_width=True, type="primary"):
                if username == "Samuel.rougon@lycee-nevers.fr" and password == "310318Ivich?":
                    st.session_state['authenticated'] = True
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")
    st.markdown("</div>", unsafe_with_html=True)

# Blocage si non authentifié
if not st.session_state['authenticated']:
     login_page()
    st.stop()

# ==========================================
# INITIALISATION DES DONNÉES (BASE DE DONNÉES TEMPORAIRE)
# ==========================================
if 'matires' not in st.session_state:
    st.session_state['matires'] = ["Mathématiques (Spé)", "Physique-Chimie (Spé)", "SES (Spé)", "Français", "Histoire-Géo", "LVA", "LVB", "Enseignement Scientifique", "EPS"]

if 'agenda' not in st.session_state:
    st.session_state['agenda'] = pd.DataFrame(columns=['Date', 'Matière', 'Type', 'Description', 'Fait'])

if 'documents' not in st.session_state:
    st.session_state['documents'] = {} # Structure: {Matiere: {Chapitre: [Docs]}}

# ==========================================
# APPLICATION PRINCIPALE (AURA)
# ==========================================

# Sidebar - Logo, Profil et Gestion des Matières
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 25px;">
            <div style="background: linear-gradient(135deg, #6366F1, #A855F7); width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 1.2rem;">A</div>
            <div>
                <h3 style="margin: 0; font-weight: 700; font-size: 1.3rem;">AURA</h3>
                <span style="font-size: 0.8rem; color: #888;">Hub Intelligent</span>
            </div>
        </div>
    """, unsafe_with_html=True)
    
    st.write(f"👤 `Samuel.rougon@lycee-nevers.fr`")
    st.caption("Première • Lycée Nevers")
    st.write("---")
    
    # Navigation principale
    menu = st.radio("Navigation", ["📅 Agenda & Devoirs", "🧠 Espace NotebookLM (IA)", "📂 Mes Matières & Chapitres", "📝 Quiz & QCM Sauvegardés"])
    
    st.write("---")
    # Ajouter/Supprimer des matières dynamiquement
    with st.expander("⚙️ Gérer les matières"):
        nouvelle_matiere = st.text_input("Ajouter une matière")
        if st.button("Ajouter", use_container_width=True):
            if nouvelle_matiere and nouvelle_matiere not in st.session_state['matires']:
                st.session_state['matires'].append(nouvelle_matiere)
                st.rerun()
        
        matiere_a_supprimer = st.selectbox("Supprimer une matière", st.session_state['matires'])
        if st.button("Supprimer", use_container_width=True, type="secondary"):
            st.session_state['matires'].remove(matiere_a_supprimer)
            st.rerun()

# ------------------------------------------
# ONGLET 1 : AGENDA & DEVOIRS
# ------------------------------------------
if menu == "📅 Agenda & Devoirs":
    st.markdown("<h1 class='main-title'>📅 Agenda & Planification</h1>", unsafe_with_html=True)
    st.markdown("<p class='subtitle'>Suivi en temps réel de vos devoirs, contrôles et DS.</p>", unsafe_with_html=True)
    
    # Formulaire d'ajout
    with st.expander("➕ Ajouter un événement à l'agenda", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            date_ev = st.date_input("Date", datetime.now())
        with col2:
            mat_ev = st.selectbox("Matière", st.session_state['matires'])
        with col3:
            type_ev = st.selectbox("Type", ["Devoirs", "Contrôle", "DS (Devoir Surveillé)", "Méthodologie"])
            
        desc_ev = st.text_area("Consignes / Détails")
        if st.button("Ajouter à l'agenda", type="primary"):
            nouvel_ev = pd.DataFrame([{'Date': date_ev.strftime('%Y-%m-%d'), 'Matière': mat_ev, 'Type': type_ev, 'Description': desc_ev, 'Fait': False}])
            st.session_state['agenda'] = pd.concat([st.session_state['agenda'], nouvel_ev], ignore_index=True)
            st.success("Événement ajouté !")
            st.rerun()

    # Affichage des devoirs
    st.markdown("### 📋 Échéances à venir")
    if not st.session_state['agenda'].empty:
        df_sorted = st.session_state['agenda'].sort_values(by='Date')
        for idx, row in df_sorted.iterrows():
            badge_color = "#EF4444" if "DS" in row['Type'] or "Contrôle" in row['Type'] else "#3B82F6"
            st.markdown(f"""
            <div class="card">
                <span style="background-color: {badge_color}; color: white; padding: 4px 10px; border-radius: 8px; font-size: 0.8rem; font-weight: bold; margin-right: 10px;">{row['Type']}</span>
                <strong>{row['Date']} — {row['Matière']}</strong>
                <p style="margin-top: 10px; margin-bottom: 10px;">{row['Description']}</p>
            </div>
            """, unsafe_with_html=True)
            if st.button(f"Marquer comme fait / Supprimer l'échéance {idx}", key=f"del_{idx}"):
                st.session_state['agenda'] = st.session_state['agenda'].drop(idx)
                st.rerun()
    else:
        st.info("Aucun devoir ou contrôle de planifié. Tranquille !")

# ------------------------------------------
# ONGLET 2 : ESPACE NOTEBOOKLM (IA & GENERATION)
# ------------------------------------------
elif menu == "🧠 Espace NotebookLM (IA)":
    st.markdown("<h1 class='main-title'>🧠 Espace NotebookLM intelligent</h1>", unsafe_with_html=True)
    st.markdown("<p class='subtitle'>Importez vos cours (PDF ou Liens) pour générer instantanément vos fiches, QCM et infographies textuelles.</p>", unsafe_with_html=True)
    
    mat_choisie = st.selectbox("Associer le document à quelle matière ?", st.session_state['matires'])
    chap_choisi = st.text_input("Nom du chapitre (ex: Chapitre 1 - Fonctions polynômes)")
    
    source_type = st.radio("Source du cours :", ["Fichier PDF (Mac/PC/iPhone)", "Lien URL / Site Web"])
    
    contenu_cours = ""
    
    if source_type == "Fichier PDF (Mac/PC/iPhone)":
        uploaded_file = st.file_uploader("Choisissez votre fichier de cours (PDF, Texte)", type=["pdf", "txt"])
        if uploaded_file is not None:
            # Simulation de lecture (Dans la version finale, utilisez PyPDF2 pour extraire le texte)
            contenu_cours = f"[Contenu extrait du fichier {uploaded_file.name}] L'élève a importé ses notions clés de {mat_choisie}."
            st.success("Fichier importé avec succès !")
    else:
        url_input = st.text_input("Collez le lien URL ici")
        if url_input:
            contenu_cours = f"[Contenu extrait de l'URL : {url_input}] Concepts clés de {mat_choisie}."
            st.success("Lien pris en compte !")

    if contenu_cours and chap_choisi:
        st.markdown("---")
        st.markdown("### ✨ Que voulez-vous générer avec Gemini ?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 Fiche de Révision", use_container_width=True):
                with st.spinner("Gemini génère votre fiche..."):
                    # Exemple de prompt à l'API :
                    # prompt = f"Fais une fiche de révision structurée sur : {contenu_cours}"
                    st.markdown("<h4>📌 Fiche de Révision Générée</h4>", unsafe_with_html=True)
                    st.info("Voici votre fiche de révision optimisée pour le Lycée Nevers. Elle contient un résumé clair, les définitions majeures et les formules indispensables.")
        
        with col2:
            if st.button("❓ Générer un QCM / Quiz", use_container_width=True):
                with st.spinner("Création du Quiz..."):
                    st.markdown("<h4>🧠 Votre Quiz Flash</h4>", unsafe_with_html=True)
                    st.write("1. Quelle est la règle principale abordée dans ce chapitre ?")
                    st.radio("Options :", ["Réponse A", "Réponse B", "Réponse C"], key="quiz_ex")
        
        with col3:
            if st.button("📊 Infographie Textuelle", use_container_width=True):
                st.markdown("<h4>🖼️ Structure Visuelle du Cours</h4>", unsafe_with_html=True)
                st.code("""
                [ CONCEPT CENTRAL ]
                       │
                       ├─► [ AXE 1 : Fondations ] ──► Formule clé
                       ├─► [ AXE 2 : Applications ] ──► Exercice type
                       └─► [ AXE 3 : Pièges à éviter ]
                """, language="text")
                
        with col4:
            if st.button("💬 Interroger le document", use_container_width=True):
                st.session_state['chat_doc'] = True
                
        if st.session_state.get('chat_doc', False):
            st.write("---")
            question = st.text_input("Posez votre question à Gemini sur ce document :")
            if question:
                st.write(f"🤖 **Gemini :** D'après votre cours de {mat_choisie} sur le chapitre {chap_choisi}, la réponse clé repose sur l'application rigoureuse de la méthodologie étudiée.")

# ------------------------------------------
# ONGLET 3 : DOSSIERS MATIÈRES & MÉTHODOLOGIE
# ------------------------------------------
elif menu == "📂 Mes Matières & Chapitres":
    st.markdown("<h1 class='main-title'>📂 Archivage et Matières</h1>", unsafe_with_html=True)
    
    selected_folder = st.selectbox("Explorer les dossiers de :", st.session_state['matires'])
    
    st.markdown(f"### 🗂️ Chapitres & Fichiers de Méthodologie en {selected_folder}")
    
    # Ajout d'un chapitre factice pour l'organisation
    st.text_input("➕ Créer un nouveau dossier de chapitre / méthode", placeholder="ex: Chapitre 2 ou Fiche Méthode Dissertation")
    st.button("Créer le dossier")
    
    st.markdown("""
    *📂 Aucun document n'est encore archivé spécifiquement dans ce dossier. Allez dans l'onglet **Espace NotebookLM** pour y envoyer des données.*
    """)

# ------------------------------------------
# ONGLET 4 : COMPTEUR DE QCM / QUIZ
# ------------------------------------------
elif menu == "📝 Quiz & QCM Sauvegardés":
    st.markdown("<h1 class='main-title'>📝 Banque de Questions & Quiz</h1>", unsafe_with_html=True)
    st.write("Retrouvez ici tous les QCM générés automatiquement classés par chapitres pour vous tester avant les DS.")
    
    st.info("Espace vide. Générez un QCM depuis l'espace IA pour le voir apparaître ici et mesurer votre score de révision.")
