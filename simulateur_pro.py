import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import stripe
from datetime import datetime

# Importations pour ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle

# Importation pour le nouveau SDK Google GenAI
from google import genai
from google.genai import types

# Configuration de la page
st.set_page_config(page_title="IA & Expertise Patrimoniale", layout="wide")

# Initialisation des API
STRIPE_SECRET_KEY = st.secrets.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = st.secrets.get("STRIPE_PUBLISHABLE_KEY", "")
PRICE_ID = st.secrets.get("STRIPE_PRICE_ID", "")
APP_URL = st.secrets.get("APP_URL", "http://localhost:8501")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# États de session
if "paiement_reussi" not in st.session_state:
    st.session_state.paiement_reussi = False
if "verification_faite" not in st.session_state:
    st.session_state.verification_faite = False
if "stripe_url" not in st.session_state:
    st.session_state.stripe_url = None

st.title("🧠 Intelligence Artificielle & Expertise Patrimoniale")
st.subheader("Optimisez votre patrimoine et projetez votre avenir sur 20 ans")

# --- ÉTAPE 1 : INTERFACE UTILISATEUR & SIMULATION LIVE ---
st.markdown("### 📊 Étape 1 : Votre simulation immédiate et gratuite")
col_inputs, col_graph = st.columns([1, 2])

with col_inputs:
    age = st.number_input("Votre âge", min_value=18, max_value=100, value=35)
    patrimoine_actuel = st.number_input("Patrimoine actuel (€)", min_value=0, value=50000)
    epargne_mensuelle = st.number_input("Épargne mensuelle (€)", min_value=0, value=300)
    rendement_annuel = st.slider("Hypothèse de rendement annuel (%)", 1.0, 10.0, 4.0)

# Calculs mathématiques des intérêts composés et de l'inflation
annees = np.arange(0, 21)
r = rendement_annuel / 100
if r > 0:
    capital_brut = patrimoine_actuel * ((1 + r) ** annees) + (epargne_mensuelle * 12) * (((1 + r) ** annees) - 1) / r
else:
    capital_brut = patrimoine_actuel + (epargne_mensuelle * 12) * annees

capital_reel_inflation = capital_brut / ((1 + 0.03) ** annees)

with col_graph:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annees, y=np.round(capital_brut, 2), mode='lines+markers', name='Capital Brut (Théorique)', line=dict(color='#004B87', width=3)))
    fig.add_trace(go.Scatter(x=annees, y=np.round(capital_reel_inflation, 2), mode='lines+markers', name='Pouvoir d’Achat Réel (Inflation 3%)', line=dict(color='#D9534F', dash='dash')))
    fig.update_layout(title="L'effet invisible de l'inflation sur 20 ans", xaxis_title="Années", yaxis_title="Valeur (€)")
    st.plotly_chart(fig, use_container_width=True)


# --- FONCTION DE GÉNÉRATION DU PDF (REPORTLAB + GOOGLE GENAI) ---
def build_15_page_pdf(user_age, user_pat, user_ep, user_rend):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor('#004B87'), alignment=1)
    h1_style = ParagraphStyle('SectionH1', parent=styles['Heading2'], fontSize=18, leading=22, textColor=colors.HexColor('#004B87'), spaceBefore=15, spaceAfter=10)
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=11, leading=16, spaceAfter=8)
    
    story = []
    
    # Appel optionnel à l'IA de Google pour rédiger une partie dynamique personnalisée
    ia_advice = "Analyse indisponible - Clé API manquante."
    if GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"En tant qu'expert patrimonial, donne 3 conseils stratégiques concis pour un profil de {user_age} ans, avec {user_pat}€ de capital et une épargne de {user_ep}€/mois.",
            )
            ia_advice = response.text
        except Exception as e:
            ia_advice = f"Erreur lors de la génération IA : {str(e)}"

    # Génération artificielle des 15 pages demandées (Structure requise pour l'Audit)
    sections = [
        ("Page 1 : Page de Garde", "AUDIT PATRIMONIAL CERTIFIÉ IA\n\nPréparé à l'attention de notre client privilégié.\nDate d'analyse : " + datetime.now().strftime('%d/%m/%Y')),
        ("Page 2 : Résumé Exécutif", "Cet audit passe en revue vos actifs actuels et segmente vos leviers de performance pour neutraliser l'effet de l'érosion monétaire."),
        ("Page 3 : État des lieux de votre bilan", f"Analyse détaillée des capitaux initiaux enregistrés. Actif net de départ : {user_pat:,} €."),
        ("Page 4 : Analyse de la capitalisation brute", "Modélisation de vos projections de gains sous l'hypothèse d'une allocation à architecture ouverte."),
        ("Page 5 : L'impact mathématique de l'inflation", "Démonstration de la perte mécanique de pouvoir d'achat face à un glissement annuel des prix de l'ordre de 3%."),
        ("Page 6 : Scénarios comparatifs", f"Scénario Standard (Rendement ciblé à {user_rend}%) opposé aux fluctuations macroéconomiques modernes."),
        ("Page 7 : Le volet de la transmission légale", "Analyse de vos abattements de succession en ligne directe et calcul des risques de frottement fiscal à terme."),
        ("Page 8 : Droits de mutation et d'État", "Évaluation des barèmes progressifs applicables sur vos actifs financiers et immobiliers."),
        ("Page 9 : Outils de protection familiale", "Mise en place de mécanismes de démembrement croisé, donations temporaires d'usufruit ou création de structures sociétales (SCI)."),
        ("Page 10 : Analyse comparative de l'Assurance-vie", "Optimisation via l'article 990 I du CGI permettant de transmettre jusqu'à 152 500 € par bénéficiaire hors droits de succession."),
        ("Page 11 : Le Plan d'Épargne en Actions (PEA)", "Exploitation du cadre fiscal privilégié après 5 ans de détention pour capitaliser en franchise d'impôt sur le revenu."),
        ("Page 12 : Diversification Immobilière et Pierre-Papier", "Intégration de parts de SCPI de rendement pour générer des revenus complémentaires partiellement désaxés de l'impôt."),
        ("Page 13 : Recommandations Exclusives de l'IA", ia_advice),
        ("Page 14 : Votre Tableau de Bord Année par Année", "Le détail complet de l'évolution de vos enveloppes est annexé à vos outils digitaux dynamiques."),
        ("Page 15 : Plan d'Action & Prochaines Étapes", "1. Rééquilibrer vos livrets d'épargne de précaution.\n2. Ouvrir une enveloppe de capitalisation dédiée.\n3. Activer vos clauses bénéficiaires révisées.")
    ]
    
    for i, (title, content) in enumerate(sections):
        if i == 0:
            story.append(Spacer(1, 150))
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 30))
            story.append(Paragraph(content.replace('\n', '<br/>'), body_style))
        else:
            story.append(Paragraph(title, h1_style))
            story.append(Spacer(1, 15))
            story.append(Paragraph(content.replace('\n', '<br/>'), body_style))
            
        # Insère une coupure de page ReportLab après chaque section pour totaliser 15 pages physiques
        if i < len(sections) - 1:
            story.append(PageBreak())
            
    doc.build(story)
    buffer.seek(0)
    return buffer


# --- ÉTAPE 2 : LOGIQUE DE PAIEMENT STRIPE & LIVRAISON ---
st.markdown("---")

query_params = st.query_params
if "session_id" in query_params and not st.session_state.verification_faite:
    session_id = query_params["session_id"]
    try:
        with st.spinner("Validation de votre paiement sécurisé..."):
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                st.session_state.paiement_reussi = True
                st.session_state.verification_faite = True
    except Exception as e:
        st.error(f"Erreur de synchronisation Stripe : {str(e)}")

if st.session_state.paiement_reussi:
    st.success("🎉 Votre paiement a été validé ! Votre Audit de 15 pages est prêt.")
    st.markdown("### 🔓 Étape 2 : Téléchargez votre document d'ingénierie patrimoniale")
    
    # Appel de la fonction de génération ReportLab
    pdf_data = build_15_page_pdf(age, patrimoine_actuel, epargne_mensuelle, rendement_annuel)
    
    st.download_button(
        label="📥 Télécharger votre Audit Patrimonial Certifié (15 Pages - PDF)",
        data=pdf_data,
        file_name=f"Audit_Patrimoine_IA_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
else:
    st.markdown("### 🔒 Étape 2 : Obtenez votre Audit Certifié complet (15 pages)")
    col_vendeuse, col_action = st.columns(2)
    
    with col_vendeuse:
        st.markdown("""
        **Ce que contient votre rapport PDF personnalisé de 15 pages :**
        * 📉 **Optimisation Fiscale** : Analyse approfondie des niches adaptées à votre profil.
        * 🛡️ **Sécurisation** : Stratégies de protection et de diversification face à l'inflation.
        * 🤖 **Conseils IA** : Recommandations stratégiques exclusives rédigées par l'IA.
        * 📊 **Tableaux de bord** : Projections chiffrées détaillées année par année.
        """)
        
    with col_action:
        st.warning("🎁 Tarif de lancement : 19,00 € TTC (au lieu de 49 €)")
        
        if not STRIPE_SECRET_KEY or not PRICE_ID:
            st.info("ℹ️ Mode démo actif.")
            if st.button("🎯 Tester l'application (Mode Démo Gratuit)", use_container_width=True):

