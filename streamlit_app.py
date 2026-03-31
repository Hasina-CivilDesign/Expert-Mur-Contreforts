import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Hub Ingénierie Madagascar", layout="wide")

# --- 2. BARRE LATÉRALE : NAVIGATION ---
with st.sidebar:
    st.title("🏗️ Engineering Hub")
    st.subheader("Par Hasina R.")
    
    # Le Menu de sélection
    menu = st.radio(
        "Choisir un module :",
        ["🏠 Accueil", "🧱 Mur à Contreforts", "📐 Semelle Filante", "🌉 Poutre Continue"]
    )
    
    st.divider()
    st.write("✉️ [Contact : hasinarabialahy@gmail.com](mailto:hasinarabialahy@gmail.com)")
    
    # Ton bouton Buy Me a Coffee
    st.markdown('''
    <a href="https://www.buymeacoffee.com/hasina.civil" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Soutenir" style="height: 40px !important; width: 145px !important;" >
    </a>
    ''', unsafe_allow_html=True)

# --- 3. LOGIQUE D'AFFICHAGE ---

# --- MODULE ACCUEIL ---
if menu == "🏠 Accueil":
    st.header("Bienvenue sur votre Hub d'Ingénierie Structure")
    st.write("""
    Cet outil a été développé pour automatiser les calculs de génie civil selon les normes **BAEL**.
    Sélectionnez un module dans le menu à gauche pour commencer vos calculs.
    """)
    st.info("🚀 **Précision & Rapidité** : Gagnez du temps sur vos descentes de charges et vos ferraillages.")
    
    # Petit message pour le patron s'il passe par là
    st.success("Logiciel optimisé pour les chantiers à Madagascar 🇲🇬")

# --- MODULE MUR À CONTREFORTS ---
elif menu == "🧱 Mur à Contreforts":
    st.header("🧱 Expertise : Mur à Contreforts (BAEL)")
    
    # >>> ICI : COLLE TOUT TON ANCIEN CODE DU MUR <<<
    # (Attention à bien garder l'indentation vers la droite pour que ce soit sous le 'elif')
    st.warning("⚠️ Recolle ici ton code du mur pour le réactiver.")

# --- MODULE SEMELLE FILANTE ---
# --- MODULE SEMELLE FILANTE ---
elif menu == "📐 Semelle Filante":
    st.header("📐 Expertise : Semelle Filante + Longrine")

    # --- BARRE LATÉRALE POUR LA SEMELLE ---
    with st.sidebar:
        st.subheader("Paramètres de la Semelle")
        B_sem = st.number_input("Largeur semelle B (m)", value=0.60, step=0.05)
        h_sem = st.number_input("Hauteur semelle h (m)", value=0.30, step=0.05)
        q_adm = st.number_input("Contrainte sol admissible (kPa/kN/m²)", value=200.0)
        
        st.subheader("Charges Poteaux")
        g_poteau = st.number_input("Charge Permanente G totale (kN)", value=150.0)
        q_poteau = st.number_input("Charge Variable Q totale (kN)", value=50.0)
        
        st.subheader("Géométrie du projet")
        L_totale_sem = st.number_input("Longueur totale de la semelle (m)", value=10.0)
        dist_poteaux = st.text_input("Entraxes entre poteaux (m)", value="3.5 3.5 3.0")

    # --- CALCULS ---
    # (On simplifie la logique de ton script pour l'affichage Streamlit)
    N_elu = 1.35 * g_poteau + 1.5 * q_poteau
    surface_sem = B_sem * L_totale_sem
    poids_propre_sem = B_sem * h_sem * L_totale_sem * 25 # 25 kN/m3 pour le BA
    
    N_total_ser = (g_poteau + q_poteau + poids_propre_sem)
    sigma_sol_calc = N_total_ser / surface_sem

    # --- AFFICHAGE DES RÉSULTATS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Pression sur le sol", f"{sigma_sol_calc:.2f} kPa")
        if sigma_sol_calc <= q_adm:
            st.success("✅ Capacité portante OK")
        else:
            st.error("❌ Sol insuffisant ! Augmentez B.")

    with col2:
        st.metric("Charge Totale (ELS)", f"{N_total_ser:.2f} kN")

    # Petit graphique de la section
    fig2, ax2 = plt.subplots(figsize=(6, 2))
    ax2.add_patch(plt.Rectangle((0, 0), B_sem, h_sem, color='grey', alpha=0.5, label="Semelle"))
    ax2.set_xlim(-0.2, B_sem + 0.2)
    ax2.set_ylim(-0.1, h_sem + 0.2)
    ax2.set_title("Coupe de la Semelle")
    st.pyplot(fig2)

    st.info("💡 Prochaine amélioration : Calcul du ferraillage transversal automatique.")
    st.header("📐 Expertise : Semelle Filante + Longrine")
    st.info("🚧 Ce module est en cours d'intégration. On va transformer ton script Python en interface Web ici.")

# --- MODULE POUTRE CONTINUE ---
elif menu == "🌉 Poutre Continue":
    st.header("🌉 Calcul de Poutre Continue (Expert)")
    st.warning("⚠️ Module en cours d'optimisation : Intégration des charges ponctuelles et du ferraillage.")
