import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. CONFIGURATION DE LA PAGE (UNE SEULE FOIS ICI) ---
st.set_page_config(page_title="Hub Ingénierie Madagascar", layout="wide")

# --- 2. BARRE LATÉRALE : NAVIGATION ---
with st.sidebar:
    st.title("🏗️ Engineering Hub")
    st.subheader("Par Hasina R.")
    
    menu = st.radio(
        "Choisir un module :",
        ["🏠 Accueil", "🧱 Mur à Contreforts", "📐 Semelle Filante", "🌉 Poutre Continue"]
    )
    
    st.divider()
    st.write("✉️ [Contact : hasinarabialahy@gmail.com](mailto:hasinarabialahy@gmail.com)")
    
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
    st.success("Logiciel optimisé pour les chantiers à Madagascar 🇲🇬")

# --- MODULE MUR À CONTREFORTS ---
elif menu == "🧱 Mur à Contreforts":
    st.header("🧱 Expertise : Mur à Contreforts (BAEL)")
    st.write("Calcul complet : Stabilité, Rideau par tranches, Semelle et Contreforts.")
    
    # --- BARRE LATÉRALE DU MUR ---
    with st.sidebar:
        st.header("⚙️ Paramètres Mur")
        gamma_t = st.number_input("Poids volumique terre (kN/m3)", value=16.0)
        phi_deg = st.slider("Angle de frottement φ (°)", 20, 45, 35)
        sigma_sol_adm = st.number_input("Contrainte adm. sol (kPa)", value=200.0)
        fc28 = st.selectbox("Résistance béton fc28 (MPa)", [20, 25, 30], index=1)
    
        H = st.number_input("Hauteur totale H (m)", value=7.65, step=0.1)
        B = st.number_input("Largeur semelle B (m)", value=round(0.45 * H, 2))
        hs = st.number_input("Épaisseur semelle hs (m)", value=round(H / 12, 2))
        e = st.number_input("Entraxe contreforts (m)", value=round(H / 2, 2))
        avant_rideau = st.number_input("Patin (m)", value=round(B * 0.3, 2))
        b0 = st.number_input("Épaisseur contrefort (m)", value=0.30)
        L_cont = st.number_input("Base contrefort (m)", value=round(B - avant_rideau - 0.20, 2))
        L_totale_mur = st.number_input("Longueur totale du mur (m)", value=10.0, step=1.0)

    # --- CALCULS MUR ---
    phi_rad = math.radians(phi_deg)
    ka = (math.tan(math.radians(45) - phi_rad / 2)) ** 2
    gamma_b = 25.0
    fsu = 400 / 1.15
    
    hr_bas, hr_haut = 0.20, 0.15
    hr_moyen = (hr_bas + hr_haut) / 2
    largeur_talon_calc = B - avant_rideau - hr_bas
    
    W_rideau = hr_moyen * (H - hs) * gamma_b
    W_semelle = B * hs * gamma_b
    W_terres = largeur_talon_calc * (H - hs) * gamma_t
    V_reel = W_rideau + W_semelle + W_terres
    
    dist_G = B / 2
    xg_rideau = avant_rideau + (hr_bas / 2)
    xg_terres = B - (largeur_talon_calc / 2)
    Ms_total = (W_rideau * xg_rideau) + (W_semelle * dist_G) + (W_terres * xg_terres)
    
    xv = Ms_total / V_reel
    ex_poids = xv - dist_G
    Qk = 0.5 * ka * gamma_t * (H ** 2)
    Mr_elu = 1.35 * Qk * (H / 3)
    Mg = Mr_elu - (V_reel * ex_poids)
    V_elu = 1.35 * V_reel
    e_finale = Mg / V_elu
    sigma_1 = (V_elu / B) * (1 + 6 * e_finale / B)
    sigma_2 = (V_elu / B) * (1 - 6 * e_finale / B)
    
    tab1, tab2, tab3 = st.tabs(["📊 Stabilité", "🧱 Rideau", "📐 Contrefort & Bilan"])
    
    with tab1:
        st.subheader("Vérification de la Stabilité")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sigma Patin", f"{sigma_1:.2f} kPa")
        c2.metric("Sigma Talon", f"{sigma_2:.2f} kPa")
        c3.metric("Statut Sol", "✅ OK" if sigma_1 <= sigma_sol_adm else "❌ EXCES")
        
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot([0, B], [sigma_1, sigma_2], 'r-', linewidth=2)
        ax.fill_between([0, B], [sigma_1, sigma_2], color='red', alpha=0.1)
        ax.axhline(0, color='black')
        st.pyplot(fig)
    
    with tab2:
        st.subheader("Ferraillage du Rideau")
        tranches = []
        z = 0.5
        H_rideau = H - hs
        while z <= H_rideau:
            e_z = hr_haut + (hr_bas - hr_haut) * (z / H_rideau)
            p_z = ka * gamma_t * z
            m0 = (1.35 * p_z * e ** 2) / 8
            As_t = (0.8 * m0 * 1e-3) / (0.9 * (e_z - 0.05) * fsu) * 1e4
            tranches.append({"Z (m)": round(z, 2), "Ep. (m)": round(e_z, 2), "As (cm²/ml)": round(As_t, 2)})
            z += 1.0
        st.table(pd.DataFrame(tranches))
    
    with tab3:
        st.subheader("Analyse du Contrefort & Bilan")
        H_cont_calc = H - hs
        p_base = ka * gamma_t * H_cont_calc * e
        Mu_cont = 1.35 * (p_base * H_cont_calc / 2) * (H_cont_calc / 3)
        d_cont = L_cont - 0.10
        As_cont = (Mu_cont * 1e-3) / (0.9 * d_cont * fsu) * 1e4
        
        vol_beton_ml = (W_rideau + W_semelle) / 25 + (H_cont_calc * L_cont / 2) * b0 / e
        poids_acier_ml = vol_beton_ml * 90 # Ratio estimatif
        
        st.write(f"Acier Contrefort : **{As_cont:.2f} cm²**")
        st.success(f"Béton Total pour {L_totale_mur}m : **{vol_beton_ml * L_totale_mur:.2f} m³**")
        st.success(f"Acier Total estimé : **{poids_acier_ml * L_totale_mur:.0f} kg**")

# --- MODULE SEMELLE FILANTE ---
elif menu == "📐 Semelle Filante":
    st.header("📐 Expertise : Semelle Filante + Longrine (BAEL)")

    with st.sidebar:
        st.subheader("🏗️ Géométrie & Sol")
        B_sem = st.number_input("Largeur semelle B (m)", value=0.50, step=0.05)
        h_sem = st.number_input("Hauteur semelle h (m)", value=0.25, step=0.05)
        a_pot = st.number_input("Largeur poteau a (m)", value=0.20)
        debord_ext = st.number_input("Débord aux extrémités (m)", value=0.20)
        q_adm_sem = st.number_input("Contrainte admissible (kPa)", value=250.0)
        
        st.subheader("🎯 Charges & Entraxes")
        txt_L = st.text_input("Entraxes (m)", value="2.0 3.0")
        txt_G = st.text_input("Charges G (kN)", value="150 250 300")
        txt_Q = st.text_input("Charges Q (kN)", value="20 20 20")

    try:
        L_list = [float(x) for x in txt_L.split()]
        G_list = [float(x) for x in txt_G.split()]
        Q_list = [float(x) for x in txt_Q.split()]
        L_tot = sum(L_list) + 2 * debord_ext
        Surface = B_sem * L_tot
        
        P_semelle = B_sem * h_sem * L_tot * 25
        N_total_ser = sum(G_list) + sum(Q_list) + P_semelle
        
        # Diagramme de pression
        sigma_moy = N_total_ser / Surface
        st.metric("Pression Moyenne", f"{sigma_moy:.2f} kPa")
        
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        ax2.add_patch(plt.Rectangle((0, 0), L_tot, 0.4, color='grey', alpha=0.3))
        ax2.fill([0, L_tot, L_tot, 0], [0, 0, -sigma_moy/q_adm_sem, -sigma_moy/q_adm_sem], color='orange', alpha=0.2)
        st.pyplot(fig2)
        
    except Exception as e:
        st.error(f"Erreur de données : {e}")

# --- MODULE POUTRE CONTINUE ---
elif menu == "🌉 Poutre Continue":
    st.header("🌉 Calcul de Poutre Continue (Expert)")
    st.warning("⚠️ Module en cours d'optimisation : Intégration des charges ponctuelles.")
