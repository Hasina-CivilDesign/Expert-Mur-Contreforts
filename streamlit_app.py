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
    st.write("✉️ [hasinarabialahy@gmail.com](mailto:hasinarabialahy@gmail.com)")
    
    mon_lien_bmc = "https://www.buymeacoffee.com/hasina.civil"
    st.markdown(f'''
    <a href="{mon_lien_bmc}" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Soutenir" style="height: 40px !important; width: 145px !important;" >
    </a>
    ''', unsafe_allow_html=True)

# --- 3. LOGIQUE D'AFFICHAGE ---

if menu == "🏠 Accueil":
    st.header("Bienvenue sur votre Hub d'Ingénierie Structure")
    st.write("Sélectionnez un module dans le menu à gauche pour commencer vos calculs.")
    st.info("🚀 **Précision & Rapidité** : Logiciel optimisé pour les chantiers à Madagascar 🇲🇬")

elif menu == "🧱 Mur à Contreforts":
    st.header("🏗️ Logiciel d'Expertise : Mur à Contreforts (BAEL)")
    
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
        L_totale = st.number_input("Longueur totale du mur (m)", value=10.0)

    # Calculs Mur
    phi_rad = math.radians(phi_deg)
    ka = (math.tan(math.radians(45) - phi_rad / 2)) ** 2
    gamma_b, fsu = 25.0, 400 / 1.15
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
    Mg, V_elu = Mr_elu - (V_reel * ex_poids), 1.35 * V_reel
    e_mur = Mg / V_elu
    sig1_m = (V_elu / B) * (1 + 6 * e_mur / B)
    sig2_m = (V_elu / B) * (1 - 6 * e_mur / B)

    tab1, tab2, tab3 = st.tabs(["📊 Stabilité", "🧱 Rideau", "📐 Contrefort & Bilan"])

    with tab1:
        st.subheader("Vérification de la Stabilité")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sigma Patin", f"{sig1_m:.2f} kPa")
        c2.metric("Sigma Talon", f"{sig2_m:.2f} kPa")
        c3.metric("Statut Sol", "✅ OK" if sig1_m <= sigma_sol_adm else "❌ EXCES")
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot([0, B], [sig1_m, sig2_m], 'r-')
        ax.fill_between([0, B], [sig1_m, sig2_m], color='red', alpha=0.1)
        st.pyplot(fig)

    with tab2:
        st.subheader("Ferraillage du Rideau")
        tranches, as_max_m, z, Hr = [], 0, 0.5, H - hs
        while z <= Hr:
            e_z = hr_haut + (hr_bas - hr_haut) * (z / Hr)
            p_z = ka * gamma_t * z
            m0 = (1.35 * p_z * e ** 2) / 8
            As_z = (0.8 * m0 * 1e-3) / (0.9 * (e_z - 0.05) * fsu) * 1e4
            as_max_m = max(as_max_m, As_z)
            tranches.append({"Profondeur (m)": round(z, 2), "As (cm²/ml)": round(As_z, 2)})
            z += 1.0
        st.table(pd.DataFrame(tranches))

    with tab3:
        st.subheader("Analyse du Contrefort & Bilan")
        vol_m = (W_rideau + W_semelle) / 25 + ((H-hs) * L_cont / 2) * b0 / e
        poids_a = vol_m * (110 if as_max_m > 7 else 80)
        st.metric("Volume Béton Total", f"{vol_m * L_totale:.2f} m³")
        st.metric("Poids Acier Total", f"{poids_a * L_totale:.0f} kg")

elif menu == "📐 Semelle Filante":
    st.header("📐 Expertise : Semelle Filante + Longrine")
    
    with st.sidebar:
        st.header("⚙️ Paramètres")
        nb_p = st.number_input("Nombre de poteaux", min_value=2, value=3)
        deb_e = st.number_input("Débord extrémités (m)", value=0.20)
        B_s = st.number_input("Largeur semelle B (m)", value=0.60)
        h_s = st.number_input("Hauteur semelle h (m)", value=0.30)
        q_adm = st.number_input("Contrainte adm. sol (kPa)", value=200.0)
        
        st.info("Séparez les valeurs par un espace")
        ent_str = st.text_input("Entraxes (m)", value="2.0 3.0")
        G_s = st.text_input("Charges G (kN)", value="150 250 300")
        Q_s = st.text_input("Charges Q (kN)", value="20 20 20")

    try:
        ents = [float(x) for x in ent_str.split()]
        Gs = [float(x) for x in G_s.split()]
        Qs = [float(x) for x in Q_s.split()]

        L_t = sum(ents) + 2 * deb_e
        S_s = B_s * L_t
        P_s = B_s * h_s * L_t * 25.0
        
        N_ser = sum(Gs) + sum(Qs) + P_s
        px = [deb_e]
        for ex in ents: px.append(px[-1] + ex)
        
        xcg = sum((Gs[i]+Qs[i]) * px[i] for i in range(nb_p)) / sum(Gs[i]+Qs[i] for i in range(nb_p))
        exc = (L_t / 2) - xcg
        
        s1 = (N_ser / S_s) * (1 + 6 * exc / L_t)
        s2 = (N_ser / S_s) * (1 - 6 * exc / L_t)

        t1, t2 = st.tabs(["📊 Stabilité Expert", "🏗️ Ferraillage"])
        
        with t1:
            st.subheader("Analyse de Portance & Équilibre")
            c1, c2, c3 = st.columns(3)
            c1.metric("Pression Max", f"{max(s1, s2):.2f} kPa")
            c2.metric("Excentricité", f"{exc:.3f} m")
            c3.metric("Sol", "✅ OK" if max(s1, s2) <= q_adm else "❌ EXCES")

            fig2, ax2 = plt.subplots(figsize=(10, 5))
            ax2.plot([0, L_t], [s1, s2], 'b-', linewidth=3, label="Pression Sol")
            ax2.fill_between([0, L_t], [s1, s2], alpha=0.1, color='blue')
            ax2.axhline(q_adm, color='red', linestyle='--', label="Limite Sol")
            ax2.axvline(xcg, color='green', linestyle=':', label="G des charges")
            ax2.axvspan(L_t/3, 2*L_t/3, color='yellow', alpha=0.1, label="Tiers Central")
            
            for i, p in enumerate(px):
                ax2.annotate('↓', (p, max(s1, s2)*1.1), ha='center', fontsize=15)
                ax2.text(p, max(s1, s2)*1.2, f"P{i+1}", ha='center')
                
            ax2.set_xlabel("Longueur (m)")
            ax2.set_ylabel("kPa")
            ax2.legend()
            st.pyplot(fig2)

        with t2:
            st.write("Charges pour Longrine (ELU) :")
            st.success(f"G linéaire : {(sum(Gs)+P_s)/L_t:.2f} kN/m")
            st.success(f"Q linéaire : {sum(Qs)/L_t:.2f} kN/m")

    except Exception as err:
        st.error(f"Vérifiez vos saisies : {err}")

elif menu == "🌉 Poutre Continue":
    st.header("🌉 Calcul de Poutre Continue (Longrine)")
    st.info("Prêt pour l'intégration de la méthode de Caquot.")
