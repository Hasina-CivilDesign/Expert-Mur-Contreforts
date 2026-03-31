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

if menu == "🏠 Accueil":
    st.header("Bienvenue sur votre Hub d'Ingénierie Structure")
    st.write("""
    Cet outil a été développé pour automatiser les calculs de génie civil selon les normes **BAEL**.
    Sélectionnez un module dans le menu à gauche pour commencer vos calculs.
    """)
    st.info("🚀 **Précision & Rapidité** : Gagnez du temps sur vos descentes de charges et vos ferraillages.")
    st.success("Logiciel optimisé pour les chantiers à Madagascar 🇲🇬")

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

        st.header("3. Paramètres Chantier")
        L_totale_mur = st.number_input("Longueur totale du mur (m)", value=10.0, step=1.0)

    # --- MOTEUR DE CALCUL ---
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

    dist_G, xg_rideau, xg_terres = B / 2, avant_rideau + (hr_bas / 2), B - (largeur_talon_calcul / 2)
    Ms_total = (W_rideau * xg_rideau) + (W_semelle * dist_G) + (W_terres * xg_terres)
    xv = Ms_total / V_reel
    ex_poids = xv - dist_G
    Qk = 0.5 * ka * gamma_t * (H ** 2)
    Mr_elu = 1.35 * Qk * (H / 3)
    Mg, V_elu = Mr_elu - (V_reel * ex_poids), 1.35 * V_reel
    e_finale = Mg / V_elu
    sigma_1 = (V_elu / B) * (1 + 6 * e_finale / B)
    sigma_2 = (V_elu / B) * (1 - 6 * e_finale / B)

    tab1, tab2, tab3 = st.tabs(["📊 Stabilité", "🧱 Rideau", "📐 Contrefort & Bilan"])

    with tab1:
        st.subheader("📊 Analyse de la Stabilité & Portance")
        res_a, res_b, res_c = st.columns(3)
        res_a.metric("Sigma Patin (σ1)", f"{sigma_1:.2f} kPa")
        res_b.metric("Sigma Talon (σ2)", f"{sigma_2:.2f} kPa")
        
        if sigma_1 > sigma_sol_adm:
            res_c.error("❌ SOL INSUFFISANT")
        elif sigma_2 < 0:
            res_c.warning("⚠️ RISQUE DE SOULÈVEMENT")
        else:
            res_c.success("✅ STABILITÉ OK")

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot([0, B], [sigma_1, sigma_2], 'r-', linewidth=3, label="Pression (kPa)")
        ax.fill_between([0, B], [sigma_1, sigma_2], color='red', alpha=0.1)
        ax.axhline(sigma_sol_adm, color='black', linestyle='--', label=f"Limite Sol ({sigma_sol_adm} kPa)")
        ax.set_xlabel("Largeur de la semelle B (m)")
        ax.set_ylabel("Contrainte (kPa)")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        st.pyplot(fig)

    with tab2:
        st.subheader("Ferraillage du Rideau (Dalle entre contreforts)")
        tranches, as_max_trouve, z, H_rideau = [], 0, 0.5, H - hs
        while z <= H_rideau:
            e_z = hr_haut + (hr_bas - hr_haut) * (z / H_rideau)
            p_z = ka * gamma_t * z
            m0 = (1.35 * p_z * e ** 2) / 8 # Moment en travée dalle
            As_t = (0.8 * m0 * 1e-3) / (0.9 * (e_z - 0.05) * fsu) * 1e4
            as_max_trouve = max(as_max_trouve, As_t)
            tranches.append({"Profondeur (m)": round(z, 2), "As (cm²/ml)": round(As_t, 2)})
            z += 1.0
        st.table(pd.DataFrame(tranches))
        
        st.info(f"💡 **Conseil Optimisation** : L'entraxe actuel est de {e}m. En le réduisant à {round(e*0.8, 2)}m, vous pourriez diminuer la section d'acier du rideau d'environ 30%.")

    with tab3:
        st.subheader("Analyse du Contrefort & Quantités")
        H_cont_calc = H - hs
        p_base = ka * gamma_t * H_cont_calc * e
        Mu_cont = 1.35 * (p_base * H_cont_calc / 2) * (H_cont_calc / 3)
        As_cont = (Mu_cont * 1e-3) / (0.9 * (L_cont - 0.10) * fsu) * 1e4
        st.metric("Acier Contrefort (As principal)", f"{As_cont:.2f} cm²")

        vol_beton_ml = (W_rideau + W_semelle) / 25 + (H_cont_calc * L_cont / 2) * b0 / e
        ratio_base = 110 if (as_max_trouve > 7 or As_cont > 30) else 80
        poids_acier_ml = vol_beton_ml * ratio_base
        vol_global = vol_beton_ml * L_totale_mur
        poids_acier_global = poids_acier_ml * L_totale_mur

        st.divider()
        st.info(f"📍 Synthèse pour {L_totale_mur}m de mur :")
        g1, g2 = st.columns(2)
        g1.metric("Béton Total", f"{vol_global:.2f} m³")
        g2.metric("Acier Total", f"{poids_acier_global:.0f} kg")

    # --- CALCULATEUR DE MATÉRIAUX & BUDGET ---
    st.divider()
    st.header("📊 Métré & Enveloppe Budgétaire")
    c1, c2 = st.columns(2)
    prix_sac = c1.number_input("Prix sac ciment (Ar)", value=38000)
    prix_acier = c2.number_input("Prix acier (Ar/kg)", value=5500)

    # Calcul sacs (dosage 350kg/m3 par défaut)
    nb_sacs = (vol_global * 350) / 50
    total_ciment = nb_sacs * prix_sac
    total_acier = poids_acier_global * prix_acier
    total_general = total_ciment + total_acier

    st.success(f"💰 **Total Estimé (Ciment + Acier) : {int(total_general):,} Ar**".replace(",", " "))
    
    with st.expander("🔍 Détails du budget"):
        st.write(f"- Ciment ({int(nb_sacs)} sacs) : {int(total_ciment):,} Ar")
        st.write(f"- Acier ({int(poids_acier_global)} kg) : {int(total_acier):,} Ar")
        st.caption("Note: Les prix du sable et gravier ne sont pas inclus ici.")

elif menu == "📐 Semelle Filante":
    st.header("📐 Expertise : Semelle Filante + Longrine")
    
    with st.sidebar:
        st.header("⚙️ Paramètres Semelle")
        nb_poteaux = st.number_input("Nombre de poteaux", min_value=2, value=3)
        debord_ext = st.number_input("Débord aux extrémités (m)", value=0.20)
        B_semelle = st.number_input("Largeur semelle B (m)", value=0.60)
        h_semelle = st.number_input("Hauteur semelle h (m)", value=0.30)
        a_poteau = st.number_input("Largeur poteau a (m)", value=0.20)
        
        st.header("🌍 Sol & Matériaux")
        qadm = st.number_input("Contrainte adm. sol (kPa)", value=200.0)
        fyd = 500
        gamma_beton = 25.0
        
        st.header("🧱 Longrine & Remblai")
        B_longrine = st.number_input("Largeur longrine (m)", value=0.20)
        h_longrine = st.number_input("Hauteur longrine (m)", value=0.45)
        H_remblai = st.number_input("Hauteur remblai au-dessus semelle (m)", value=0.50)
        gamma_rem = st.number_input("Poids vol. remblai (kN/m³)", value=18.0)

        st.header("🏗️ Charges Poteaux")
        entraxe_str = st.text_input(f"Entraxes ({nb_poteaux-1} valeurs)", value="2.0 3.0")
        G_str = st.text_input(f"Charges G en kN ({nb_poteaux} valeurs)", value="150 250 300")
        Q_str = st.text_input(f"Charges Q en kN ({nb_poteaux} values)", value="20 20 20")

    try:
        entraxes = [float(x) for x in entraxe_str.split()]
        G_list = [float(x) for x in G_str.split()]
        Q_list = [float(x) for x in Q_str.split()]

        if len(entraxes) != nb_poteaux - 1 or len(G_list) != nb_poteaux or len(Q_list) != nb_poteaux:
            st.error("❌ Erreur : Nombre de valeurs incorrect.")
        else:
            # --- CALCULS GÉOMÉTRIQUES & POIDS ---
            L_totale = sum(entraxes) + 2 * debord_ext
            S_semelle = B_semelle * L_totale
            
            # Poids propre semelle, longrine et remblai
            P_semelle = S_semelle * h_semelle * gamma_beton
            P_longrine = B_longrine * h_longrine * L_totale * gamma_beton
            
            l_debord_transv = (B_semelle - B_longrine) / 2 # Débord de chaque côté de la longrine
            P_remblai = gamma_rem * H_remblai * (l_debord_transv * 2) * L_totale
            
            # --- CALCUL DU CENTRE DE GRAVITÉ (CG) ---
            pos_x = [debord_ext]
            for ex in entraxes: pos_x.append(pos_x[-1] + ex)
            
            P_poteaux_total = [G_list[i] + Q_list[i] for i in range(nb_poteaux)]
            x_cg = sum(P_poteaux_total[i] * pos_x[i] for i in range(nb_poteaux)) / sum(P_poteaux_total)
            
            # --- CALCUL DE L'EXCENTRICITÉ ---
            x_milieu = L_totale / 2
            excentricite = x_cg - x_milieu
            
            # Charge totale de service
            N_total_ser = sum(P_poteaux_total) + P_semelle + P_longrine + P_remblai
            
            # --- CALCUL DES CONTRAINTES (Navier) ---
            sig1 = (N_total_ser / S_semelle) * (1 + 6 * excentricite / L_totale)
            sig2 = (N_total_ser / S_semelle) * (1 - 6 * excentricite / L_totale)
            sig_max = max(sig1, sig2)

            t1, t2 = st.tabs(["📊 Analyse Stabilité", "🏗️ Ferraillage & Charges"])

            with t1:
                st.subheader("📊 Analyse de la Portance & Équilibre")
                res_a, res_b, res_c = st.columns(3)
                res_a.metric("Pression Max", f"{sig_max:.2f} kPa")
                res_b.metric("Excentricité (e)", f"{excentricite:.3f} m")
                res_c.metric("Position CG", f"{x_cg:.2f} m")

                # Graphique Expert
                fig2, ax2 = plt.subplots(figsize=(10, 5))
                ax2.axvspan(L_totale/3, 2*L_totale/3, color='yellow', alpha=0.2, label="Tiers Central (Zone Stable)")
                ax2.plot([0, L_totale], [sig1, sig2], color='navy', linewidth=3, label="Diagramme des contraintes")
                ax2.fill_between([0, L_totale], [sig1, sig2], alpha=0.1, color='blue')
                ax2.axhline(qadm, color='red', linestyle='--', label=f"Limite Sol ({qadm} kPa)")
                ax2.axvline(x_milieu, color='black', linestyle='--', alpha=0.5, label="Axe Central Semelle")
                ax2.axvline(x_cg, color='green', linewidth=2, label=f"R (Charge Totale) à {x_cg:.2f}m")
                
                for i, p_pos in enumerate(pos_x):
                    ax2.annotate('↓', (p_pos, sig_max*1.05), ha='center', fontsize=15, color='black')
                    ax2.text(p_pos, sig_max*1.15, f"P{i+1}", ha='center', fontweight='bold')
                
                ax2.set_xlabel("Longueur de la semelle (m)")
                ax2.set_ylabel("Pression (kPa)")
                ax2.set_ylim(bottom=0)
                ax2.legend(loc='upper right', fontsize='small')
                ax2.grid(True, linestyle=':', alpha=0.6)
                st.pyplot(fig2)

                # Diagnostic
                st.divider()
                if abs(excentricite) <= L_totale / 6:
                    st.success(f"✅ **L'excentricité ({abs(excentricite):.3f}m)** est dans le tiers central. La semelle est entièrement comprimée.")
                else:
                    st.warning(f"⚠️ **Attention** : L'excentricité est hors du tiers central. Risque de décollement.")
                
                if sig_max > qadm:
                    st.error(f"❌ **Dépassement** : La pression au sol ({sig_max:.1f} kPa) dépasse la capacité admissible ({qadm} kPa).")

            with t2:
                st.subheader("🧱 Ferraillage Transversal de la Semelle (par ml)")
                
                # Calcul simplifié à l'ELU (majoration arbitraire ~1.4 pour l'exemple)
                # La contrainte nette qui fait fléchir la semelle = Réaction Sol - Poids Propres
                p_net_ser = sig_max - (h_semelle * gamma_beton) - (H_remblai * gamma_rem)
                p_net_elu = p_net_ser * 1.4 
                
                # Moment fléchissant dans la console (débord)
                M_transv_elu = p_net_elu * (l_debord_transv**2) / 2
                
                # Section d'acier BAEL
                d_utile = h_semelle - 0.05
                fsu = fyd / 1.15
                As_calc = (M_transv_elu * 1e-3) / (0.9 * d_utile * fsu) * 1e4 # en cm²/ml
                
                # Section minimale (règle des 0.15% à 0.20%)
                As_min = 0.0015 * 100 * (h_semelle * 100)
                As_final = max(As_calc, As_min)

                c_a, c_b = st.columns(2)
                c_a.metric("Moment fléchissant (ELU estimé)", f"{M_transv_elu:.2f} kNm/ml")
                c_b.metric("Section d'acier (As)", f"{As_final:.2f} cm²/ml")
                
                if As_final == As_min:
                    st.info("💡 La section calculée est très faible, on applique le **ferraillage minimum forfaitaire BAEL**.")

                st.divider()
                st.subheader("⏬ Descente de charges pour la Longrine")
                q_G_longrine = (sum(G_list) + P_semelle + P_longrine + P_remblai) / L_totale
                q_Q_longrine = sum(Q_list) / L_totale
                
                st.write(f"Charge permanente G répartie au sol : **{q_G_longrine:.2f} kN/m**")
                st.write(f"Charge d'exploitation Q répartie au sol : **{q_Q_longrine:.2f} kN/m**")
                st.success("👉 Notez ces valeurs pour dimensionner et ferrailler la longrine dans le module 'Poutre Continue'.")

    except Exception as e:
        st.error(f"Erreur de calcul : Vérifiez vos données saisies ({e})")

elif menu == "🌉 Poutre Continue":
    st.header("🌉 Calcul Exact : Méthode des 3 Moments")
    st.write("Ce module calcule les moments exacts (Clapeyron) pour une poutre continue sous charges réparties.")

    # 1. SAISIE DES DONNÉES
    with st.sidebar:
        st.subheader("📏 Géométrie & Matériau")
        n = st.number_input("Nombre de travées", min_value=1, max_value=6, value=2)
        b_poutre = st.number_input("Largeur b (m)", value=0.20)
        h_poutre = st.number_input("Hauteur h (m)", value=0.45)
        gamma_mat = st.number_input("Poids vol. (kN/m³)", value=25.0)
        g_pp = b_poutre * h_poutre * gamma_mat
        st.info(f"Poids propre auto : {g_pp:.2f} kN/m")

    # Colonnes pour saisir L, G, Q par travée
    st.subheader("🏗️ Chargement par travée")
    L = []
    G = []
    Q = []
    cols_input = st.columns(n)
    for i in range(n):
        with cols_input[i]:
            st.write(f"**Travée {i+1}**")
            L.append(st.number_input(f"L (m)", value=3.5, key=f"Lt{i}"))
            g_saisi = st.number_input(f"G hors PP", value=15.0, key=f"Gt{i}")
            G.append(g_saisi + g_pp)
            Q.append(st.number_input(f"Q (kN/m)", value=5.0, key=f"Qt{i}"))

    # 2. MOTEUR DE CALCUL (Ton script adapté)
    if n >= 1:
        # Résolution matricielle pour ELU (1.35G + 1.5Q)
        import numpy as np
        
        P_elu = [1.35*G[i] + 1.5*Q[i] for i in range(n)]
        
        # Matrice A et Vecteur B
        A_mat = np.zeros((n+1, n+1))
        B_vec = np.zeros(n+1)
        A_mat[0,0], A_mat[-1,-1] = 1, 1 # Appuis de rive simples (M=0)

        for i in range(1, n):
            L_prev, L_curr = L[i-1], L[i]
            A_mat[i, i-1] = L_prev / 6
            A_mat[i, i] = (L_prev + L_curr) / 3
            A_mat[i, i+1] = L_curr / 6
            B_vec[i] = -(P_elu[i-1]*L_prev**3 + P_elu[i]*L_curr**3)/24

        M_elu = np.linalg.solve(A_mat, B_vec)

        # 3. AFFICHAGE DES RÉSULTATS
        st.divider()
        res_m, res_v = st.columns([2, 1])
        
        with res_m:
            st.subheader("📈 Diagramme des Moments (ELU)")
            fig_poutre, ax_poutre = plt.subplots(figsize=(10, 4))
            pos_x = 0
            for i in range(n):
                x_vals = np.linspace(0, L[i], 50)
                # Equation de la parabole avec moments aux appuis
                M_vals = M_elu[i]*(1 - x_vals/L[i]) + M_elu[i+1]*(x_vals/L[i]) + P_elu[i]*x_vals*(L[i]/2 - x_vals/2)
                
                ax_poutre.plot(pos_x + x_vals, -M_vals, color="red", linewidth=2)
                ax_poutre.fill_between(pos_x + x_vals, -M_vals, alpha=0.1, color="red")
                
                # Dessin appuis
                ax_poutre.plot(pos_x, 0, '^k', markersize=10)
                pos_x += L[i]
            ax_poutre.plot(pos_x, 0, '^k', markersize=10)
            ax_poutre.axhline(0, color='black', linewidth=1)
            ax_poutre.set_ylabel("Moment (kNm)")
            st.pyplot(fig_poutre)

        with res_v:
            st.subheader("📋 Moments aux Appuis")
            for i, m in enumerate(M_elu):
                st.write(f"Appui {i+1} : **{abs(m):.2f} kNm**")

        # ... (après le calcul de M_elu par la matrice) ...

        # 3. CALCUL DES MOMENTS EN TRAVÉE ET EFFORTS TRANCHANTS
        st.subheader("📋 Résultats Détaillés (ELU)")
        
        # Création d'un tableau pour l'affichage
        data_travées = []
        
        pos_x = 0
        for i in range(n):
            L_i = L[i]
            p_i = P_elu[i]
            Mw = M_elu[i]   # Moment Appui Gauche (West)
            Me = M_elu[i+1] # Moment Appui Droit (East)
            
            # Calcul de la position du moment max (X_i) dans la travée
            # Formule : x = L/2 + (Me - Mw)/(p*L)
            xi_max = (L_i / 2) + (Me - Mw) / (p_i * L_i)
            
            # Calcul du moment max en travée
            mt_max = Mw * (1 - xi_max/L_i) + Me * (xi_max/L_i) + p_i * xi_max * (L_i - xi_max) / 2
            
            # Effort tranchant aux appuis
            Vw = -p_i * L_i / 2 + (Mw - Me) / L_i
            Ve = p_i * L_i / 2 + (Mw - Me) / L_i
            
            data_travées.append({
                "Travée": i + 1,
                "L (m)": L_i,
                "M. Gauche (kNm)": round(Mw, 2),
                "M. Travée (kNm)": round(mt_max, 2),
                "M. Droit (kNm)": round(Me, 2),
                "V. Max (kN)": round(max(abs(Vw), abs(Ve)), 2)
            })

        # Affichage sous forme de beau tableau Streamlit
        st.table(data_travées)

        # --- MISE À JOUR DU GRAPHIQUE AVEC POINTS MAX ---
        with st.expander("📊 Voir le Diagramme des Moments"):
            fig_poutre, ax_poutre = plt.subplots(figsize=(10, 4))
            pos_current = 0
            for i in range(n):
                x_vals = np.linspace(0, L[i], 100)
                M_vals = M_elu[i]*(1 - x_vals/L[i]) + M_elu[i+1]*(x_vals/L[i]) + P_elu[i]*x_vals*(L[i] - x_vals)/2
                
                ax_poutre.plot(pos_current + x_vals, -M_vals, color="#1f77b4", linewidth=2.5)
                ax_poutre.fill_between(pos_current + x_vals, -M_vals, alpha=0.15, color="#1f77b4")
                
                # Ajout du texte pour le moment max en travée sur le graphe
                xi_plot = (L[i]/2) + (M_elu[i+1] - M_elu[i])/(P_elu[i]*L[i])
                mt_plot = M_elu[i]*(1 - xi_plot/L[i]) + M_elu[i+1]*(xi_plot/L[i]) + P_elu[i]*xi_plot*(L[i] - xi_plot)/2
                ax_poutre.text(pos_current + xi_plot, -mt_plot - 2, f"{mt_plot:.1f}", 
                               ha='center', color='blue', fontsize=9, fontweight='bold')
                
                pos_current += L[i]
            
            ax_poutre.axhline(0, color='black', linewidth=1.5)
            ax_poutre.invert_yaxis() # Inversion pour le sens "béton armé"
            st.pyplot(fig_poutre)
            
            # Calcul Ferraillage Rapide sur l'appui le plus sollicité
            m_max_appui = abs(min(M_elu))
            d_poutre = h_poutre - 0.05
            as_appui = (m_max_appui * 1e-3) / (0.9 * d_poutre * (500/1.15)) * 1e4
            st.warning(f"As max appui : **{as_appui:.2f} cm²**")

    st.success("🇲🇬 Logiciel validé : Prêt pour l'exportation des ferraillages !")
