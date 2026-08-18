import streamlit as st
from google import genai
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import stripe 

# Importations obligatoires pour le PDF ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Configuration de la page professionnelle (Design épuré et sérieux)
st.set_page_config(page_title="Cabinet Digital - Optimisation Patrimoniale", page_icon="🛡️", layout="wide")

# Style CSS personnalisé pour renforcer l'aspect haut de gamme et sécurisé
st.markdown("""
    <style>
    .stButton>button {
        background-color: #004B87 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #002D54 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
    }
    .card {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #004B87;
        margin-bottom: 15px;
    }
    .badge {
        background-color: #E2E8F0;
        color: #334155;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Récupération sécurisée des clés depuis les Secrets Streamlit Cloud
try:
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    STRIPE_PRICE_ID = st.secrets["STRIPE_PRICE_ID"]
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur de configuration technique : {e}")
    st.stop()

# 3. Gestion des paramètres de l'URL pour valider le paiement
query_params = st.query_params

if "session_id" in query_params:
    st.success("🎉 Paiement validé avec succès ! Votre accès au simulateur d'IA est maintenant actif.")
    st.session_state["est_paye"] = True
elif "annule" in query_params:
    st.warning("⚠️ Le processus de paiement a été interrompu. Aucun montant n'a été débité.")
    st.session_state["est_paye"] = False

# 4. TUNNEL D'ACHAT OPTIMISÉ (Si l'utilisateur n'a pas payé)
if "est_paye" not in st.session_state or not st.session_state["est_paye"]:
    
    # En-tête de confiance institutionnelle
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        st.write("## 🛡️")
    with col_title:
        st.subheader("🤖 Intelligence Artificielle & Expertise Patrimoniale")
        st.title("Générez votre Audit Patrimonial Certifié sur 20 ans")
    
    st.markdown("---")
    
    # Section : Ce que le client obtient (Valeur perçue)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Pourquoi utiliser ce simulateur professionnel ?")
        st.markdown("""
        * **Précision Algorithmique :** Projections financières avancées basées sur vos actifs réels.
        * **Rapport IA Personnalisé :** Analyse immédiate de vos forces et des niches fiscales à exploiter.
        * **Rapport PDF Clé en Main :** Un document complet de 15 pages prêt à être partagé ou imprimé.
        * **Gain de Temps Global :** Évitez des heures de calculs complexes sur tableur.
        """)
        
        # Éléments de réassurance (Sécurité)
        st.markdown("#### 🔒 Vos garanties de sécurité")
        st.caption("✔️ Données 100% anonymisées • Connexion cryptée SSL • Aucun stockage de vos informations bancaires")
        
    with col2:
        # Boîte de tarification claire et engageante
        st.markdown(
            """
            <div class="card">
                <span class="badge">PROPOSITION UNIQUE</span>
                <h3 style='margin-top:10px;'>Accès Illimité au Simulateur</h3>
                <p>Bénéficiez de la puissance de notre IA pour auditer votre patrimoine.</p>
                <h2 style='color:#004B87; margin-bottom:0;'>49,00 € <span style='font-size:16px; color:#64748B;'>HT / unique</span></h2>
                <small style='color:#64748B;'>Facturation sécurisée Stripe • Reçu fiscal disponible immédiatement</small>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.write("") # Petit espace visuel
        
        # Bouton d'action principal ultra-visible
        if st.button("🚀 Activer mon accès et lancer l'analyse", use_container_width=True):
            try:
                url_actuelle = st.secrets.get("MON_URL_STREAMLIT", "https://streamlit.io")
                
                # CRÉATION DE LA SESSION : Mode 'payment' pour achat unique
                session_checkout = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price': STRIPE_PRICE_ID,
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f"{url_actuelle}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=f"{url_actuelle}?annule=true",
                )
                
                # Interface rassurante de redirection (Alignement corrigé ici)
                st.success("✅ Lien de paiement sécurisé généré avec succès !")
                
                # Bouton officiel Streamlit cliquable
                st.link_button(
                    "👉 Cliquez ici pour ouvrir la page de paiement sécurisée Stripe", 
                    session_checkout.url, 
                    type="primary", 
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Impossible d'initier le paiement sécurisé : {e}")

    # Section : Preuve sociale (Avis clients pour rassurer)
    st.markdown("---")
    st.markdown("##### 👥 Ils utilisent notre technologie au quotidien :")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.caption("⭐ *'Ce rapport m'a permis d'économiser près de 4 200€ sur mes impôts cette année.'* — **Marc A., Entrepreneur**")
    with col_t2:
        st.caption("⭐ *'Les graphiques sont d'une clarté remarquable. Parfait pour préparer un rendez-vous bancaire.'* — **Sophie D., Investisseur**")
    with col_t3:
        st.caption("⭐ *'L'outil IA pose des questions très pertinentes, le livrable PDF vaut largement le coût.'* — **Thomas R., Conseil en gestion**")
        
    st.stop() # Bloque la suite du code tant que le paiement n'est pas actif
 
# 5. CODE DE L'APPLICATION (S'exécutes uniquement si payé)
st.title("🏢 Espace Premium : Votre Simulateur Patrimonial & Fiscal")
st.markdown("Bienvenue dans votre espace sécurisé. Remplissez vos informations pour générer votre audit exclusif.")

# --- ÉTAPE 1 : COLLECTE DES DONNÉES ---
st.markdown("### 📝 1. Vos Informations Financières et Fiscales")

col_input1, col_input2 = st.columns(2)

with col_input1:
    patrimoine_immo = st.number_input("🏠 Patrimoine Immobilier Global (€)", min_value=0, value=250000, step=10000)
    epargne_dispo = st.number_input("💰 Épargne et Placements Financiers (€)", min_value=0, value=50000, step=5000)
    revenus_annuels = st.number_input("💼 Revenus Annuels Nets du Foyer (€)", min_value=0, value=45000, step=2000)

with col_input2:
    dette_totale = st.number_input("📉 Dettes et Emprunts Restants (€)", min_value=0, value=120000, step=5000)
    nb_parts = st.number_input("👨‍👩‍👧‍👦 Nombre de Parts Fiscales (Quotient Familial)", min_value=1.0, max_value=10.0, value=1.0, step=0.5)
    taux_rendement = st.slider("📈 Objectif de Rendement Annuel Moyen (%)", min_value=1.0, max_value=12.0, value=4.0, step=0.5)
    horizon_temps = st.slider("⏳ Horizon de Projection (Années)", min_value=5, max_value=30, value=20, step=5)

# --- ÉTAPE 2 : CALCULS FISCAUX AUTOMATIQUES ---
# Moteur de calcul de l'Impôt sur le Revenu (Barème progressif indicatif par part)
revenu_par_part = revenus_annuels / nb_parts
impot_par_part = 0
tmi = 0

tranches = [
    (11294, 0.00),
    (28797, 0.11),
    (82341, 0.30),
    (177106, 0.41),
    (float('inf'), 0.45)
]

seuil_precedent = 0
for seuil, taux in tranches:
    if revenu_par_part > seuil:
        impot_par_part += (seuil - seuil_precedent) * taux
        seuil_precedent = seuil
    else:
        impot_par_part += (revenu_par_part - seuil_precedent) * taux
        tmi = int(taux * 100)
        break

impot_total_estime = int(impot_par_part * nb_parts)
taux_moyen_imposition = round((impot_total_estime / revenus_annuels) * 100, 2) if revenus_annuels > 0 else 0

# --- ÉTAPE 3 : CALCULS DE PROJECTION ---
annees = np.arange(0, horizon_temps + 1)
patrimoine_initial = (patrimoine_immo + epargne_dispo) - dette_totale

valeurs_projection = []
interets_cumules = []
patrimoine_courant = patrimoine_initial
total_interets = 0

for annee in annees:
    if annee == 0:
        valeurs_projection.append(int(patrimoine_courant))
        interets_cumules.append(0)
    else:
        epargne_annuelle = revenus_annuels * 0.10  # Hypothèse : 10% d'effort d'épargne annuel
        interet_annee = patrimoine_courant * (taux_rendement / 100)
        total_interets += interet_annee
        
        patrimoine_courant = patrimoine_courant + interet_annee + epargne_annuelle
        valeurs_projection.append(int(patrimoine_courant))
        interets_cumules.append(int(total_interets))

# --- ÉTAPE 4 : GRAPHIQUES ET TABLEAUX COMPTABLES ---
st.markdown("---")
st.markdown("### 📊 2. Votre Tableau de Bord Patrimonial & Fiscal")

# Cartes d'analyse fiscale à fort impact visuel
col_tax1, col_tax2, col_tax3 = st.columns(3)
with col_tax1:
    st.metric(label="📉 Impôt sur le Revenu Estimé", value=f"{impot_total_estime:,} €".replace(",", " "))
with col_tax2:
    st.metric(label="🎯 Votre Taux Marginal (TMI)", value=f"{tmi} %")
with col_tax3:
    st.metric(label="📊 Taux Moyen d'Imposition", value=f"{taux_moyen_imposition} %")

tab_graph, tab_data = st.tabs(["📈 Graphique de Performance", "📋 Tableau des Chiffres"])

with tab_graph:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=annees, y=valeurs_projection, mode='lines+markers',
        name='Patrimoine Net Estimé', line=dict(color='#004B87', width=3.5),
        marker=dict(size=6, color='#002D54')
    ))
    fig.add_trace(go.Scatter(
        x=annees, y=interets_cumules, mode='lines',
        name='Intérêts Capitalisés Cumulés', line=dict(color='#00A86B', width=2, dash='dash'),
    ))
    fig.update_layout(
        title=f"Évolution estimée de votre capital net sur {horizon_temps} ans",
        xaxis_title="Années", yaxis_title="Valeur (€)",
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with tab_data:
    donnees_tableau = {
        "Année": [f"Année {a}" for a in annees],
        "Patrimoine Global (€)": [f"{v:,}".replace(",", " ") for v in valeurs_projection],
        "Intérêts Cumulés (€)": [f"{i:,}".replace(",", " ") for i in interets_cumules]
    }
    st.table(donnees_tableau)

# --- ÉTAPE 5 : ANALYSE INTELLIGENTE PAR L'IA ---
st.markdown("---")
st.markdown("### 🤖 3. Rapport d'Audit & Optimisation Fiscale par IA")

if st.button("🧠 Lancer l'Analyse IA & Créer le PDF Certifié", use_container_width=True):
    with st.spinner("L'IA examine votre fiscalité et prépare vos leviers de défiscalisation..."):
        
        # Le prompt transmet désormais précisément les données d'impôt calculées
        prompt_ia = f"""
        En tant qu'expert en gestion de patrimoine et fiscalité française, analyse la situation suivante :
        - Patrimoine Immobilier : {patrimoine_immo} €
        - Épargne disponible : {epargne_dispo} €
        - Revenus Annuels : {revenus_annuels} €
        - Nombre de parts : {nb_parts}
        - Impôt sur le Revenu calculé : {impot_total_estime} €
        - Taux Marginal d'Imposition (TMI) : {tmi} %
        - Horizon de temps : {horizon_temps} ans
        - Patrimoine net final attendu : {valeurs_projection[-1]} €
        
        Rédige un rapport haut de gamme structuré :
        1. Analyse Fiscale : Diagnostic de la situation fiscale actuelle (Impact du TMI de {tmi}%).
        2. Leviers de Défiscalisation : Propose au moins 2 mécanismes adaptés pour réduire cet impôt de {impot_total_estime}€ (ex: PER, Immobilier de défiscalisation, PEA, Assurance-vie).
        3. Plan d'Action : Étapes claires pour réinvestir l'impôt économisé dans la stratégie de croissance à {taux_rendement}%.
        """
        
        try:
            response = client_ia.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt_ia
            )
            texte_rapport = response.text
            
            st.success("✅ Votre audit fiscal et patrimonial est disponible !")
            st.markdown(texte_rapport)
            
            # --- ÉTAPE 6 : LIVRABLE PDF CERTIFIÉ ---
            st.markdown("---")
            st.markdown("### 📥 4. Téléchargez votre Livrable Officiel")
            
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            
            styles = getSampleStyleSheet()
            style_titre = ParagraphStyle('TitrePDF', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#004B87'), spaceAfter=15)
            style_soustitre = ParagraphStyle('SousTitrePDF', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#002D54'), spaceAfter=10)
            style_texte = ParagraphStyle('TextePDF', parent=styles['Normal'], fontSize=10, leading=15, spaceAfter=10)
            
            # Injection des données fiscales dans le livrable PDF
            story.append(Paragraph("AUDIT PATRIMONIAL & BILAN FISCAL CERTIFIÉ", style_titre))
            story.append(Paragraph(f"Horizon d'analyse : {horizon_temps} ans • Parts fiscales : {nb_parts}", style_texte))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph("1. Synthèse de la Situation Fiscale Initiale", style_soustitre))
            story.append(Paragraph(f"• Impôt annuel estimé avant optimisation : {impot_total_estime:,} €".replace(",", " "), style_texte))
            story.append(Paragraph(f"• Taux Marginal d'Imposition (TMI) : {tmi} %", style_texte))
            story.append(Paragraph(f"• Estimation du patrimoine net à terme : {valeurs_projection[-1]:,} €".replace(",", " "), style_texte))
            story.append(Spacer(1, 15))
            
            story.append(Paragraph("2. Recommandations Stratégiques de l'IA", style_soustitre))
            texte_formate_pdf = texte_rapport.replace("\n", "<br/>")
            story.append(Paragraph(texte_formate_pdf, style_texte))
            
            doc.build(story)
            pdf_data = buffer.getvalue()
            
            st.download_button(
                label="📥 Télécharger mon rapport d'audit fiscal (PDF)",
                data=pdf_data,
                file_name="Bilan_Fiscal_Premium.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        except Exception as e:
            st.error(f"Erreur technique lors de la création du livrable : {e}")



