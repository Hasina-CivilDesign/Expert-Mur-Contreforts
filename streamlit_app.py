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
# --- MODULE SEMELLE FILANTE (VERSION VARIABLE) ---
elif menu == "📐 Semelle Filante":
    st.header("📐 Expertise : Semelle Filante Multi-Poteaux")

    with st.sidebar:
        st.subheader("Paramètres de la Semelle")
        B_sem = st.number_input("Largeur semelle B (m)", value=0.60, step=0.05)
        h_sem = st.number_input("Hauteur semelle h (m)", value=0.30, step=0.05)
        q_adm = st.number_input("Contrainte sol admissible (kPa)", value=200.0)
        
        st.divider()
        st.subheader("Configuration des Poteaux")
        # Saisie des distances entre poteaux (ex: 3.5 4.2 3.8)
        txt_entraxes = st.text_input("Entraxes entre poteaux (m)", value="3.5 4.0")
        # Saisie des charges G par poteau
        txt_G = st.text_input("Charges G par poteau (kN)", value="120 150 120")
        # Saisie des charges Q par poteau
        txt_Q = st.text_input("Charges Q par poteau (kN)", value="40 50 40")

    # --- LOGIQUE DE CALCUL DYNAMIQUE ---
    try:
        # Conversion des textes en listes de nombres
        list_L = [float(x) for x in txt_entraxes.split()]
        list_G = [float(x) for x in txt_G.split()]
        list_Q = [float(x) for x in txt_Q.split()]

        # Vérification de la cohérence (Nb poteaux = Nb entraxes + 1)
        if len(list_G) != len(list_L) + 1:
            st.error("⚠️ Le nombre de charges G doit être égal au (nombre d'entraxes + 1)")
        else:
            L_totale_calc = sum(list_L)
            G_total = sum(list_G)
            Q_total = sum(list_Q)
            
            poids_propre_sem = B_sem * h_sem * L_totale_calc * 25
            N_total_ser = G_total + Q_total + poids_propre_sem
            
            sigma_sol_calc = N_total_ser / (B_sem * L_totale_calc)

            # --- AFFICHAGE DES RÉSULTATS ---
            st.subheader("Résultats du calcul réel")
            c1, c2, c3 = st.columns(3)
            c1.metric("Longueur Totale", f"{L_totale_calc:.2f} m")
            c2.metric("Charge Totale G+Q", f"{G_total + Q_total:.1f} kN")
            c3.metric("Pression Sol", f"{sigma_sol_calc:.2f} kPa")

            if sigma_sol_calc <= q_adm:
                st.success("✅ La semelle est stable sur toute sa longueur.")
            else:
                st.error("❌ Risque de poinçonnement ou tassement. Augmentez la largeur B.")

            # --- SCHÉMA DE LA SEMELLE ---
            st.write("**Schéma de répartition des charges :**")
            fig3, ax3 = plt.subplots(figsize=(10, 2))
            # Dessin de la semelle
            ax3.add_patch(plt.Rectangle((0, 0), L_totale_calc, 0.3, color='lightgrey'))
            # Dessin des poteaux (flèches)
            current_x = 0
            ax3.annotate(f"P1\n{list_G[0]}kN", (0, 0.3), xytext=(0, 0.8), arrowprops=dict(arrowstyle='->'))
            # --- SCHÉMA DE LA SEMELLE CORRIGÉ ---
            st.write("**Schéma de répartition des charges (Coupe longitudinale) :**")
            fig3, ax3 = plt.subplots(figsize=(10, 3))
            
            # Dessin de la semelle (le béton)
            ax3.add_patch(plt.Rectangle((0, 0), L_totale_calc, 0.3, color='lightgrey', label="Béton"))
            
            # Dessin des poteaux (Flèches verticales)
            current_x = 0
            positions_x = [0] + [sum(list_L[:i+1]) for i in range(len(list_L))]
            
            for i, x_pos in enumerate(positions_x):
                # On dessine une flèche verticale parfaite
                ax3.annotate('', xy=(x_pos, 0.3), xytext=(x_pos, 1.2),
                             arrowprops=dict(facecolor='red', shrink=0.05, width=2, headwidth=8))
                # Texte de la charge au-dessus
                ax3.text(x_pos, 1.3, f"P{i+1}\n{list_G[i]+list_Q[i]}kN", 
                         ha='center', va='bottom', fontweight='bold', color='red')

            ax3.set_xlim(-0.5, L_totale_calc + 0.5)
            ax3.set_ylim(-0.2, 2.0)
            ax3.axis('off') # On cache les axes pour un look "Plan d'ingénieur"
            st.pyplot(fig3)

    except ValueError:
        st.warning("Veuillez entrer des chiffres valides séparés par des espaces.")

# --- MODULE POUTRE CONTINUE ---
elif menu == "🌉 Poutre Continue":
    st.header("🌉 Calcul de Poutre Continue (Expert)")
    st.warning("⚠️ Module en cours d'optimisation : Intégration des charges ponctuelles et du ferraillage.")
