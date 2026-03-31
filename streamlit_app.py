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
    st.header("🌉 Calcul de Poutre Continue (Méthode des 3 Moments)")
    
    # 1. ENTRÉES (Sidebar)
    with st.sidebar:
        st.subheader("📏 Paramètres Poutre")
        n = st.number_input("Nombre de travées", min_value=1, max_value=6, value=2)
        b_poutre = st.number_input("Largeur b (m)", value=0.20)
        h_poutre = st.number_input("Hauteur h (m)", value=0.45)
        gamma_mat = st.number_input("Poids vol. (kN/m³)", value=25.0)
        g_pp = b_poutre * h_poutre * gamma_mat

    # 2. SAISIE DES CHARGES (Main)
    L, G, Q = [], [], []
    cols = st.columns(n)
    for i in range(n):
        with cols[i]:
            st.write(f"**Travée {i+1}**")
            L.append(st.number_input(f"L (m)", value=3.5, key=f"L{i}"))
            g_ext = st.number_input(f"G (kN/m)", value=15.0, key=f"G{i}")
            G.append(g_ext + g_pp)
            Q.append(st.number_input(f"Q (kN/m)", value=5.0, key=f"Q{i}"))

    # 3. CALCULS MATRICIELS (ELU)
    import numpy as np
    P_elu = [1.35*G[i] + 1.5*Q[i] for i in range(n)]
    A_mat = np.zeros((n+1, n+1))
    B_vec = np.zeros(n+1)
    A_mat[0,0], A_mat[-1,-1] = 1, 1 

    for i in range(1, n):
        Lw, Le = L[i-1], L[i]
        A_mat[i, i-1] = Lw / 6
        A_mat[i, i] = (Lw + Le) / 3
        A_mat[i, i+1] = Le / 6
        B_vec[i] = -(P_elu[i-1]*Lw**3 + P_elu[i]*Le**3)/24

    M_elu = np.linalg.solve(A_mat, B_vec)

    # 4. SYNTHÈSE DES RÉSULTATS (Tableau)
    st.subheader("📋 Tableau des Moments et Efforts")
    data_res = []
    for i in range(n):
        xi_max = (L[i]/2) + (M_elu[i+1] - M_elu[i])/(P_elu[i]*L[i])
        mt_max = M_elu[i]*(1-xi_max/L[i]) + M_elu[i+1]*(xi_max/L[i]) + P_elu[i]*xi_max*(L[i]-xi_max)/2
        Vw = abs(-P_elu[i]*L[i]/2 + (M_elu[i]-M_elu[i+1])/L[i])
        Ve = abs(P_elu[i]*L[i]/2 + (M_elu[i]-M_elu[i+1])/L[i])
        data_res.append({"Travée": i+1, "M. Appui G": round(M_elu[i],2), "M. Travée": round(mt_max,2), "M. Appui D": round(M_elu[i+1],2), "V. Max": round(max(Vw, Ve),2)})
    st.table(data_res)

    # 5. GRAPHIQUE UNIQUE (M et V)
    fig, (ax_m, ax_v) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
    plt.subplots_adjust(hspace=0.3)
    
    pos = 0
    for i in range(n):
        x = np.linspace(0, L[i], 100)
        M = M_elu[i]*(1-x/L[i]) + M_elu[i+1]*(x/L[i]) + P_elu[i]*x*(L[i]-x)/2
        V = (-P_elu[i]*L[i]/2 + (M_elu[i]-M_elu[i+1])/L[i]) + P_elu[i]*x
        
        ax_m.plot(pos+x, M, color="#1f77b4", lw=2)
        ax_m.fill_between(pos+x, M, alpha=0.1, color="#1f77b4")
        ax_v.plot(pos+x, V, color="#d62728", lw=2)
        ax_v.fill_between(pos+x, V, alpha=0.1, color="#d62728")
        ax_m.plot(pos, 0, '^k')
        ax_v.plot(pos, 0, 'sk', ms=4)
        pos += L[i]
    
    ax_m.plot(pos, 0, '^k')
    ax_v.plot(pos, 0, 'sk', ms=4)
    ax_m.set_ylabel("Moment (kNm)")
    ax_m.invert_yaxis() # Sens BA
    ax_v.set_ylabel("Tranchant (kN)")
    ax_v.set_xlabel("Position (m)")
    st.pyplot(fig)

    # 6. RÉSUMÉ FERRAILLAGE (Métrics)
    st.divider()
    m_max = max([abs(m) for m in M_elu] + [d['M. Travée'] for d in data_res])
    as_est = (m_max*1e-3)/(0.9*(h_poutre-0.05)*(500/1.15))*1e4
    c1, c2 = st.columns(2)
    c1.metric("Moment Max Absolu", f"{m_max:.3f} kNm")
    c2.metric("Section Acier (As)", f"{as_est:.3f} cm²")

    # --- SECTION FERRAILLAGE RÉEL ---
st.header("🏗️ Choix du Ferraillage Réel")

col_f1, col_f2 = st.columns(2)

with col_f1:
    diametre_base = st.selectbox("Diamètre principal (Travée)", [10, 12, 14, 16], index=1, help="Diamètre des barres de traction en bas")
    nb_barres = st.number_input("Nombre de barres", min_value=2, max_value=6, value=3)
    
    # Calcul de la section réelle fournie
    section_fournie = nb_barres * (3.1415 * (diametre_base/20)**2) # en cm2
    st.write(f"Section Acier fournie : **{section_fournie:.2f} cm²**")

with col_f2:
    st.info("💡 **Mode Optimisation**")
    # Le bouton est désactivé (simulateur de version Pro)
    st.checkbox("Mélanger les diamètres (ex: 2HA12 + 1HA10)", disabled=True)
    if st.button("🚀 Activer l'optimisation économique"):
        st.warning("🔒 **Option Verrouillée** : L'optimisation automatique pour réduire le coût du fer est disponible dans la version **Expertise**. Contactez l'ingénieur pour une note de calcul optimisée.")

# --- VÉRIFICATION ET VOYANTS ---
section_requise = as_estime # On récupère la valeur calculée plus haut
if section_fournie >= section_requise:
    st.success(f"✅ **CONFORME** : {section_fournie:.2f} cm² > {section_requise:.2f} cm²")
else:
    st.error(f"❌ **INSUFFISANT** : Il manque {(section_requise - section_fournie):.2f} cm²")

# --- LE FERRAILLAGE TRANSVERSAL (CADRES) ---
st.subheader("⛓️ Armatures Transversales (Cadres)")
phi_t = st.selectbox("Diamètre cadres", [6, 8], index=0)
st.write(f"Espacement maximum conseillé près des appuis : **15 cm**")
st.caption("Le détail des espacements (Loi de Caquot) est inclus dans la note de calcul exportée.")
