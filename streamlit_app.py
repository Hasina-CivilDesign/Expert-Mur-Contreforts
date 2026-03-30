import streamlit as st
import math
import matplotlib.pyplot as plt
import pandas as pd

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Expert Mur Contreforts", layout="wide")

st.title("🏗️ Logiciel d'Expertise : Mur à Contreforts (BAEL)")
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

    e = st.number_input("Entraxe contreforts (m)", value=round(H / 2, 2),
                        help="Réduire l'entraxe diminue fortement le ferraillage du rideau.")

    avant_rideau = st.number_input("Patin (Avant-mur) (m)", value=round(B * 0.3, 2))
    b0 = st.number_input("Épaisseur contrefort (m)", value=0.30)

    L_cont_sug = round(B - avant_rideau - 0.20, 2)
    L_cont = st.number_input("Largeur contrefort à la base (m)", value=L_cont_sug)

# --- MOTEUR DE CALCUL ---
phi_rad = math.radians(phi_deg)
ka = (math.tan(math.radians(45) - phi_rad / 2)) ** 2
gamma_b = 25.0
fsu = 400 / 1.15

# Stabilité
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

# --- AFFICHAGE ---
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
    ax.set_xlabel("Largeur semelle (m)")
    ax.set_ylabel("Pression (kPa)")
    st.pyplot(fig)

with tab2:
    st.subheader("Ferraillage du Rideau")


    def verifier_densite(as_calc):
        if as_calc > 10: return "❌ TROP DENSE"
        if as_calc > 7: return "⚠️ ÉLEVÉ"
        return "✅ OK"


    tranches = []
    as_max_trouve = 0
    z = 0.5
    H_rideau = H - hs

    while z <= H_rideau:
        e_z = hr_haut + (hr_bas - hr_haut) * (z / H_rideau)
        p_z = ka * gamma_t * z
        m0 = (1.35 * p_z * e ** 2) / 8
        As_t = (0.8 * m0 * 1e-3) / (0.9 * (e_z - 0.05) * fsu) * 1e4
        if As_t > as_max_trouve: as_max_trouve = As_t

        tranches.append({
            "Profondeur (m)": round(z, 2),
            "Épaisseur (m)": round(e_z, 2),
            "As (cm²/ml)": round(As_t, 2),
            "Conseil": verifier_densite(As_t)
        })
        z += 1.0

    if as_max_trouve > 7:
        st.warning(
            f"💡 **Conseil** : Ferraillage élevé ({as_max_trouve:.2f} cm²). Réduisez l'entraxe ({e}m) pour économiser de l'acier.")

    st.table(pd.DataFrame(tranches))

with tab3:
    st.subheader("Analyse du Contrefort")
    H_cont_calc = H - hs
    p_base = ka * gamma_t * H_cont_calc * e
    Mu_cont = 1.35 * (p_base * H_cont_calc / 2) * (H_cont_calc / 3)

    # CALCUL DU FERRAILLAGE PRINCIPAL DU CONTREFORT (Traction arrière)
    d_cont = L_cont - 0.10
    As_cont = (Mu_cont * 1e-3) / (0.9 * d_cont * fsu) * 1e4

    st.info(f"Moment de flexion à la base : **{Mu_cont:.2f} kNm**")

    col_c1, col_c2 = st.columns(2)
    col_c1.metric("Largeur utilisée (m)", f"{L_cont} m")
    col_c2.metric("Acier Contrefort (As)", f"{As_cont:.2f} cm²")

    if As_cont > 40:
        st.error("⚠️ Section d'acier du contrefort très élevée. Augmentez la largeur L_cont ou l'épaisseur b0.")

    # --- AJOUT DU BILAN QUANTITATIF FINAL ---
    st.divider()
    st.subheader("📈 Bilan Quantitatif Global (au mètre linéaire)")

    # Calcul du volume de béton (Rideau + Semelle + Contreforts répartis sur l'entraxe)
    vol_beton_ml = (W_rideau + W_semelle) / 25 + (H_cont_calc * L_cont / 2) * b0 / e

    # Estimation du poids d'acier (Ratio moyen 80kg/m3 + ajustement selon As_max)
    ratio_base = 80
    if as_max_trouve > 7 or As_cont > 30:
        ratio_base = 110  # On augmente le ratio si c'est dense

    poids_acier_ml = vol_beton_ml * ratio_base

    res1, res2 = st.columns(2)
    res1.success(f"Volume Béton : **{vol_beton_ml:.2f} m³/ml**")
    res2.success(f"Poids Acier estimé : **{poids_acier_ml:.0f} kg/ml**")

    st.caption(
        "Note : Le bilan acier est une estimation basée sur un ratio kg/m³ adaptable selon la densité des armatures calculées.")

# --- SECTION SOUTIEN ---
st.sidebar.markdown("---")
st.sidebar.write("🏗️ **Expertise & Soutien**")
st.sidebar.info("Cet outil est conçu pour faciliter le travail des ingénieurs sur le terrain.")

# Ton lien (même en attente, on le met !)
mon_lien_bmc = "https://www.buymeacoffee.com/hasina.civil"

st.sidebar.markdown(f'''
<a href="{mon_lien_bmc}" target="_blank">
    <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
    alt="Soutenir mon travail" 
    style="height: 50px !important;width: 180px !important;" >
</a>
''', unsafe_allow_html=True)

st.sidebar.write("✉️ [Contact : hasinarabialahy@gmail.com](mailto:hasinarabialahy@gmail.com)")

import streamlit as st

# --- SECTION CALCULATEUR DE CHANTIER (Métré Rapide) ---
st.divider()
st.header("📊 Calculateur de Matériaux (Métré Rapide)")
st.write("Estimez vos quantités de ciment, sable et gravier en un clic.")

# Choix du type de travaux
type_travaux = st.selectbox(
    "Quel type de travaux ?",
    ["Béton (Dalle, Poteau, Poutre)", "Mortier pour Moellons", "Mortier pour Briques"]
)

# Volume total à couler
volume_total = st.number_input("Volume total à réaliser (m³)", min_value=0.1, value=1.0, step=0.1)

col1, col2 = st.columns(2)

with col1:
    # Dosage ciment
    if type_travaux == "Béton (Dalle, Poteau, Poutre)":
        dosage = st.selectbox("Dosage Ciment (kg/m³)", [250, 300, 350, 400], index=2)
    else:
        dosage = st.selectbox("Dosage Ciment (kg/m³)", [150, 200, 250, 300], index=1)

with col2:
    # Poids du sac
    poids_sac = st.number_input("Poids d'un sac (kg)", value=50)

# --- CALCULS ---
if type_travaux == "Béton (Dalle, Poteau, Poutre)":
    # Ratio standard 1:2:3
    v_ciment = volume_total * (1/6)
    v_sable = volume_total * (2/6)
    v_gravier = volume_total * (3/6)
    masse_ciment = volume_total * dosage
    nb_sacs = masse_ciment / poids_sac
    titre = "RÉSULTATS BÉTON"
    
else:
    # Pour le mortier (moellons ou briques)
    # On estime le volume de mortier nécessaire dans le mur (ex: 30% pour moellons, 20% pour briques)
    ratio_mortier = 0.30 if "Moellons" in type_travaux else 0.20
    v_mortier_reel = volume_total * ratio_mortier
    masse_ciment = v_mortier_reel * dosage
    nb_sacs = masse_ciment / poids_sac
    v_sable = v_mortier_reel * 0.9 # Estimation sable pour mortier
    v_gravier = 0
    titre = f"RÉSULTATS {type_travaux.upper()}"

# --- AFFICHAGE DES RÉSULTATS ---
st.subheader(f"🏗️ {titre}")
res1, res2, res3 = st.columns(3)

with res1:
    st.metric("Ciment (Sacs)", f"{nb_sacs:.1f}")
with res2:
    st.metric("Sable (m³)", f"{v_sable:.2d}" if v_sable > 0 else f"{v_sable:.3f}")
with res3:
    if v_gravier > 0:
        st.metric("Gravier (m³)", f"{v_gravier:.3f}")

# --- PETIT BONUS BUDGET (Optionnel) ---
with st.expander("💰 Estimation du Budget (Ar)"):
    prix_sac = st.number_input("Prix d'un sac de ciment (Ar)", value=38000, step=500)
    budget_ciment = nb_sacs * prix_sac
    st.write(f"**Budget Ciment estimé : {int(budget_ciment):,} Ar**".replace(",", " "))

