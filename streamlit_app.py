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
    st.header("📐 Expertise : Semelle Filante + Longrine (BAEL)")

    # --- 1. SAISIE DES DONNÉES (Barre latérale) ---
    with st.sidebar:
        st.subheader("🏗️ Géométrie & Sol")
        B_sem = st.number_input("Largeur semelle B (m)", value=0.50, step=0.05)
        h_sem = st.number_input("Hauteur semelle h (m)", value=0.25, step=0.05)
        a_pot = st.number_input("Largeur poteau a (m)", value=0.20)
        debord_ext = st.number_input("Débord aux extrémités (m)", value=0.20)
        q_adm = st.number_input("Contrainte admissible sol (kPa/kN/m²)", value=250.0)
        
        st.subheader("🌱 Remblai sur débords")
        h_remblai = st.number_input("Hauteur du remblai (m)", value=0.60, step=0.10)
        gamma_remblai = st.number_input("Poids vol. remblai (kN/m³)", value=18.0)

        st.subheader("🎯 Charges & Entraxes")
        txt_L = st.text_input("Entraxes entre poteaux (m)", value="2.0 3.0")
        txt_G = st.text_input("Charges G par poteau (kN)", value="150 250 300")
        txt_Q = st.text_input("Charges Q par poteau (kN)", value="20 20 20")

    # --- 2. LE MOTEUR DE CALCUL ---
    try:
        # Conversion des listes
        L_list = [float(x) for x in txt_L.split()]
        G_list = [float(x) for x in txt_G.split()]
        Q_list = [float(x) for x in txt_Q.split()]
        
        # Longueur et Surface
        L_tot = sum(L_list) + 2 * debord_ext
        Surface = B_sem * L_tot
        
        # Poids propres et Remblai
        P_semelle = B_sem * h_sem * L_tot * 25
        l_debord_transv = (B_sem - a_pot) / 2
        P_remblai = gamma_remblai * h_remblai * l_debord_transv * 2 * L_tot
        
        N_total_ser = sum(G_list) + sum(Q_list) + P_semelle + P_remblai
        
        # Calcul de l'Excentricité (Centre de Gravité)
        positions = [debord_ext]
        for d_in in L_list:
            positions.append(positions[-1] + d_in)
        
        P_poteaux = [G_list[i] + Q_list[i] for i in range(len(G_list))]
        x_cg = sum(P_poteaux[i] * positions[i] for i in range(len(G_list))) / sum(P_poteaux)
        e = (L_tot / 2) - x_cg
        
        # Contraintes aux bords (Formule de Navier)
        sigma1 = (N_total_ser / Surface) * (1 + 6 * e / L_tot)
        sigma2 = (N_total_ser / Surface) * (1 - 6 * e / L_tot)

        # --- 3. AFFICHAGE DU SCHÉMA DE PRESSION (Avant les onglets) ---
        st.subheader("📈 Diagramme des pressions (ELS)")
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Dessin de la semelle (gris)
        ax.add_patch(plt.Rectangle((0, 0), L_tot, 0.4, color='grey', alpha=0.3, label="Semelle"))
        
        # Dessin du diagramme de pression (orange)
        # On normalise sigma par rapport à q_adm pour que le dessin reste dans le cadre
        y1 = -sigma1 / q_adm
        y2 = -sigma2 / q_adm
        x_press = [0, L_tot, L_tot, 0]
        y_press = [0, 0, y2, y1]
        ax.fill(x_press, y_press, color='orange', alpha=0.2, label="Pression Sol")
        ax.plot(x_press, y_press, color='orange', lw=2)

        # Ligne de limite q_adm (y = -1 car sigma/q_adm = 1)
        ax.axhline(-1, color='red', linestyle='--', label="Limite q_adm")

        # Flèches des poteaux (noires)
        for i, pos_x in enumerate(positions):
            ax.annotate(f"P{i+1}\n{P_poteaux[i]}kN", xy=(pos_x, 0.4), xytext=(pos_x, 1.2),
                         ha='center', arrowprops=dict(facecolor='black', shrink=0.05, width=1))

        ax.set_ylim(-1.5, 1.8)
        ax.axis('off')
        ax.legend(loc='upper right', fontsize='small')
        st.pyplot(fig)

        # --- 4. AFFICHAGE DES RÉSULTATS DÉTAILLÉS (Onglets) ---
        tab1, tab2, tab3 = st.tabs(["📊 Stabilité & Sol", "🦾 Ferraillage", "📝 Métré Longrine"])

        with tab1:
            st.subheader("Vérification de la portance")
            c1, c2, c3 = st.columns(3)
            c1.metric("Poids Remblai", f"{P_remblai:.1f} kN")
            c2.metric("σ1 (Max)", f"{sigma1:.2f} kPa")
            c3.metric("σ2 (Min)", f"{sigma2:.2f} kPa")

            if sigma1 > q_adm:
                st.error(f"❌ SOL INSUFFISANT : {sigma1:.2f} > {q_adm} kPa")
            elif sigma2 < 0:
                st.warning(f"⚠️ Soulèvement détecté (σ2 = {sigma2:.2f} < 0)")
            else:
                st.success("✅ Portance du sol validée !")

        with tab2:
            st.subheader("Ferraillage Transversal (Console)")
            M_trans = (sigma1 * l_debord_transv**2) / 2
            st.write(f"Moment transversal max : **{M_trans:.2f} kN.m/m**")
            
            d = h_sem - 0.05
            As = (M_trans * 10**6) / (0.9 * d * 1000 * 435)
            As_min = 0.0015 * 1000 * h_sem * 1000
            
            st.info(f"Section calculée : {As:.1f} mm²/m")
            st.info(f"Section minimale : {As_min:.1f} mm²/m")
            st.success(f"➡️ Retenir : **{max(As, As_min):.1f} mm²/m**")

        with tab3:
            st.subheader("Préparation pour la Poutre Continue")
            q_G_longrine = (sum(G_list) + P_semelle + P_remblai) / L_tot
            q_Q_longrine = sum(Q_list) / L_tot
            st.code(f"Charge G : {q_G_longrine:.2f} kN/m")
            st.code(f"Charge Q : {q_Q_longrine:.2f} kN/m")
            st.write("💡 *Utilisez ces valeurs comme charges réparties dans le module Poutre.*")

    except Exception as err:
        st.error(f"Erreur : {err}. Vérifiez que le nombre de charges correspond au nombre d'appuis.")

# --- MODULE POUTRE CONTINUE ---
elif menu == "🌉 Poutre Continue":
    st.header("🌉 Calcul de Poutre Continue (Expert)")
    st.warning("⚠️ Module en cours d'optimisation : Intégration des charges ponctuelles et du ferraillage.")
