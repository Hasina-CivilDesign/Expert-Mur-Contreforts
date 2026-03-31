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
    

# --- CONFIGURATION DE LA PAGE ---


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

    st.header("3. Paramètres Chantier")
    # C'EST ICI LA NOUVEAUTÉ
    L_totale = st.number_input("Longueur totale du mur (m)", value=10.0, step=1.0, help="Utilisé pour le calcul global des matériaux.")

    # --- SECTION SOUTIEN & CONTACT (LE TON JAUNE) ---
    st.markdown("---")
    st.write("🏗️ **Expertise & Soutien**")
    
    # Message d'information bleu
    st.info("Outil conçu pour l'optimisation des chantiers à Madagascar.")

    # Ton lien Buy Me a Coffee (Bouton Jaune)
    # Tu peux changer l'URL si tu en as une autre
    mon_lien_bmc = "https://www.buymeacoffee.com/hasina.civil"

    st.markdown(f'''
    <a href="{mon_lien_bmc}" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
        alt="Soutenir mon travail" 
        style="height: 45px !important; width: 160px !important; border-radius: 8px;" >
    </a>
    ''', unsafe_allow_html=True)

    st.write("") # Petit espace pour respirer
    
    # Ton Email de contact
    st.markdown("✉️ **Contact :**")
    st.code("hasinarabialahy@gmail.com")
    
    st.caption("© 2026 - Développé par Hasina")

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

  # --- 1. AFFICHAGE DES RÉSULTATS PAR MÈTRE (DANS L'ONGLET 3) ---
    res1, res2 = st.columns(2)
    res1.success(f"Volume Béton : **{vol_beton_ml:.2f} m³/ml**")
    res2.success(f"Poids Acier estimé : **{poids_acier_ml:.0f} kg/ml**")

    # --- 2. CALCUL DES TOTAUX GLOBAUX ---
    vol_global = vol_beton_ml * L_totale
    poids_acier_global = poids_acier_ml * L_totale

    # --- CALCUL DES TOTAUX GLOBAUX ---
    vol_global = vol_beton_ml * L_totale
    poids_acier_global = poids_acier_ml * L_totale

    st.info(f"📍 **Synthèse pour {L_totale}m de linéaire :**")
    
    col_glob1, col_glob2 = st.columns(2)
    col_glob1.metric("Béton Total", f"{vol_global:.2f} m³")
    col_glob2.metric("Acier Total", f"{poids_acier_global:.0f} kg")

# --- 3. SECTION CALCULATEUR DE MATÉRIAUX (HORS DES ONGLETS) ---
st.divider()
st.header("📊 Calculateur de Matériaux (Métré Rapide)")
st.write("Estimez vos quantités pour l'ensemble du mur (Ciment, Sable, Gravier).")

# Le volume est automatiquement lié au calcul du haut !
volume_final = st.number_input("Volume total de béton à traiter (m³)", value=float(vol_global))

type_travaux = st.selectbox("Type de travaux", ["Béton (Dalle, Poteau, Poutre)", "Mortier Moellons", "Mortier Briques"])

col_mat1, col_mat2 = st.columns(2)
with col_mat1:
    dosage = st.selectbox("Dosage Ciment (kg/m³)", [250, 300, 350, 400], index=2)
with col_mat2:
    poids_sac = st.number_input("Poids du sac (kg)", value=50)

# Calculs de dosage (Ratios simplifiés pour le terrain)
if "Béton" in type_travaux:
    # Ratio 1:2:3 -> 1 part ciment, 2 parts sable, 3 parts gravier
    v_sable = volume_final * (2/6)
    v_gravier = volume_final * (3/6)
    masse_ciment = volume_final * dosage
else:
    # Mortier (30% de vide pour moellons, 20% pour briques)
    ratio_v = 0.30 if "Moellons" in type_travaux else 0.20
    vol_mortier = volume_final * ratio_v
    v_sable = vol_mortier * 0.9
    v_gravier = 0
    masse_ciment = vol_mortier * dosage

nb_sacs = masse_ciment / poids_sac

# Affichage Final
r_m1, r_m2, r_m3 = st.columns(3)
r_m1.metric("Ciment (Sacs)", f"{nb_sacs:.1f}")
r_m2.metric("Sable (m³)", f"{v_sable:.2f}")
if v_gravier > 0:
    r_m3.metric("Gravier (m³)", f"{v_gravier:.2f}")

# --- BUDGET ---
# --- BUDGET ESTIMATIF DES MATÉRIAUX ---
with st.expander("💰 Enveloppe Budgétaire (Estimation)"):
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        prix_sac = st.number_input("Prix du sac de ciment (Ar)", value=38000, step=500)
    with col_p2:
        prix_acier_kg = st.number_input("Prix de l'acier (Ar/kg)", value=5500, step=100)

    # Calculs financiers
    total_ciment = nb_sacs * prix_sac
    total_acier = poids_acier_global * prix_acier_kg
    total_chantier = total_ciment + total_acier

    st.markdown("---")
    st.write(f"🛒 **Budget Ciment :** {int(total_ciment):,} Ar".replace(",", " "))
    st.write(f"🏗️ **Budget Acier :** {int(total_acier):,} Ar".replace(",", " "))
    st.subheader(f"💵 TOTAL ESTIMÉ : {int(total_chantier):,} Ar".replace(",", " "))
    
    st.caption("⚠️ Note : Ce budget est une estimation basée sur les ratios de ferraillage. Les prix du sable et gravier ne sont pas inclus ici.")

    # (Attention à bien garder l'indentation vers la droite pour que ce soit sous le 'elif')
    st.warning("⚠️ Recolle ici ton code du mur pour le réactiver.")

 # --- MODULE SEMELLE FILANTE ---
 elif menu == "📐 Semelle Filante":
    st.header("📐 Expertise : Semelle Filante + Longrine")
    st.info("🚧 Ce module est en cours d'intégration. On va transformer ton script Python en interface Web ici.")

 # --- MODULE POUTRE CONTINUE ---
 elif menu == "🌉 Poutre Continue":
    st.header("🌉 Calcul de Poutre Continue (Expert)")
    st.warning("⚠️ Module en cours d'optimisation : Intégration des charges ponctuelles et du ferraillage.")
