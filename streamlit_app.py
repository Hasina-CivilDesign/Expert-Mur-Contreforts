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
    
    menu = st.radio(
        "Choisir un module :",
        ["🏠 Accueil", "🧱 Mur à Contreforts", "📐 Semelle Filante", "🌉 Poutre Continue"]
    )
    
    st.divider()
    st.write("✉️ [Contact : hasinarabialahy@gmail.com](mailto:hasinarabialahy@gmail.com)")
    
    mon_lien_bmc = "https://www.buymeacoffee.com/hasina.civil"
    st.markdown(f'''
    <a href="{mon_lien_bmc}" target="_blank">
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

    # --- BARRE LATÉRALE : SAISIE DES DONNÉES ---
    with st.sidebar:
        st.header("1. Paramètres Sol & Béton")
        gamma_t = st.number_input("Poids volumique terre (kN/m3)", value=16.0)
        phi_deg = st.slider("Angle de frottement φ (°)", 20, 45, 35)
        sigma_sol_adm = st.number_input("Contrainte adm. sol (kPa)", value=200.0)
        fc28 = st.selectbox("Résistance béton fc28 (MPa)", [20, 25, 30], index=1)

        st.header("2. Géométrie du Mur")
        H = st.number_input("Hauteur totale H (m)", value=7.65, step=0.1)
        B = st.number_input("Largeur semelle B (m)", value=round(0.45 * H, 2))
        hs = st.number_input("Épaisseur semelle hs (m)", value=round(H / 12, 2))
        e = st.number_input("Entraxe contreforts (m)", value=round(H / 2, 2))
        avant_rideau = st.number_input("Patin (Avant-mur) (m)", value=round(B * 0.3, 2))
        b0 = st.number_input("Épaisseur contrefort (m)", value=0.30)
        L_cont = st.number_input("Largeur contrefort à la base (m)", value=round(B - avant_rideau - 0.20, 2))

        st.header("3. Paramètres Chantier")
        L_totale = st.number_input("Longueur totale du mur (m)", value=10.0, step=1.0)

    # --- MOTEUR DE CALCUL ---
    phi_rad = math.radians(phi_deg)
    ka = (math.tan(math.radians(45) - phi_rad / 2)) ** 2
    gamma_b = 25.0
    fsu = 400 / 1.15

    hr_bas, hr_haut = 0.20, 0.15
    hr_moyen = (hr_bas + hr_haut) / 2
    largeur_talon_calcul = B - avant_rideau - hr_bas

    W_rideau = hr_moyen * (H - hs) * gamma_b
    W_semelle = B * hs * gamma_b
    W_terres = largeur_talon_calcul * (H - hs) * gamma_t
    V_reel = W_rideau + W_semelle + W_terres

    dist_G = B / 2
    xg_rideau = avant_rideau + (hr_bas / 2)
    xg_terres = B - (largeur_talon_calcul / 2)
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

    # --- AFFICHAGE DES ONGLETS ---
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
        as_max_trouve = 0
        z = 0.5
        H_rideau = H - hs
        while z <= H_rideau:
            e_z = hr_haut + (hr_bas - hr_haut) * (z / H_rideau)
            p_z = ka * gamma_t * z
            m0 = (1.35 * p_z * e ** 2) / 8
            As_t = (0.8 * m0 * 1e-3) / (0.9 * (max(e_z, 0.1) - 0.05) * fsu) * 1e4
            as_max_trouve = max(as_max_trouve, As_t)
            tranches.append({"Profondeur (m)": round(z, 2), "As (cm²/ml)": round(As_t, 2)})
            z += 1.0
        st.table(pd.DataFrame(tranches))

    with tab3:
        st.subheader("Analyse du Contrefort")
        H_cont_calc = H - hs
        p_base = ka * gamma_t * H_cont_calc * e
        Mu_cont = 1.35 * (p_base * H_cont_calc / 2) * (H_cont_calc / 3)
        d_cont = L_cont - 0.10
        As_cont = (Mu_cont * 1e-3) / (0.9 * d_cont * fsu) * 1e4
        st.metric("Acier Contrefort (As)", f"{As_cont:.2f} cm²")

        # BILAN QUANTITATIF
        vol_beton_ml = (W_rideau + W_semelle) / 25 + (H_cont_calc * L_cont / 2) * b0 / e
        poids_acier_ml = vol_beton_ml * (110 if as_max_trouve > 7 else 80)
        vol_global = vol_beton_ml * L_totale
        poids_acier_global = poids_acier_ml * L_totale

        st.divider()
        res1, res2 = st.columns(2)
        res1.success(f"Volume Béton : **{vol_global:.2f} m³**")
        res2.success(f"Acier Estimé : **{poids_acier_global:.0f} kg**")

    # --- CALCULATEUR DE MATÉRIAUX (Toujours dans le menu Mur) ---
    st.divider()
    st.header("📊 Calculateur de Matériaux (Métré Rapide)")
    volume_final = st.number_input("Volume total de béton (m³)", value=float(vol_global))
    type_travaux = st.selectbox("Type de travaux", ["Béton (Dosage 350)", "Mortier Moellons", "Mortier Briques"])
    
    dosage = st.selectbox("Dosage Ciment (kg/m³)", [250, 300, 350, 400], index=2)
    nb_sacs = (volume_final * dosage) / 50
    v_sable = volume_final * 0.4
    v_gravier = volume_final * 0.8 if "Béton" in type_travaux else 0

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Ciment (Sacs)", f"{nb_sacs:.1f}")
    col_m2.metric("Sable (m³)", f"{v_sable:.2f}")
    col_m3.metric("Gravier (m³)", f"{v_gravier:.2f}")

    with st.expander("💰 Enveloppe Budgétaire"):
        prix_sac = st.number_input("Prix sac Ciment (Ar)", value=38000)
        total_ciment = nb_sacs * prix_sac
        st.subheader(f"Total Ciment : {int(total_ciment):,} Ar".replace(",", " "))

# --- AUTRES MODULES ---
elif menu == "📐 Semelle Filante":
    st.header("📐 Expertise : Semelle Filante")
    st.info("Module en cours d'intégration.")

elif menu == "🌉 Poutre Continue":
    st.header("🌉 Calcul de Poutre Continue")
    st.warning("Module en cours d'optimisation.")
