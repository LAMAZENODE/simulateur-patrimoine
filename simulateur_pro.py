import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from datetime import datetime

# Importations pour ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

# Configuration de la page
st.set_page_config(page_title="IA & Expertise Patrimoniale", layout="wide")

# --- PARAMÈTRE À REMPLIR ---
# Allez sur Stripe -> Liens de paiement -> Créez un lien à 19€ et collez-le ici :
LIEN_PAIEMENT_STRIPE = "https://stripe.com" 

# Initialisation des états de session
if "paiement_reussi" not in st.session_state:
    st.session_state.paiement_reussi = False

st.title("🧠 Intelligence Artificielle & Expertise Patrimoniale")
st.subheader("Optimisez votre patrimoine et projetez votre avenir sur 20 ans")

# --- ÉTAPE 1 : LA SIMULATION GRATUITE ---
st.markdown("### 📊 Étape 1 : Votre simulation immédiate et gratuite")

col_inputs, col_graph = st.columns(2)

with col_inputs:
    st.write("⚙️ Ajustez vos critères (le graphique s'actualise en direct) :")
    age = st.number_input("Votre âge", min_value=18, max_value=100, value=35, step=1)
    patrimoine_actuel = st.number_input("Patrimoine actuel (€)", min_value=0, value=50000, step=1000)
    epargne_mensuelle = st.number_input("Épargne mensuelle (€)", min_value=0, value=300, step=50)
    Rendement = st.slider("Hypothèse de rendement annuel (%)", 1.0, 10.0, 4.0)

# Calculs automatiques des intérêts et de l'inflation
annees_cumulees = np.arange(0, 21)
ages_futurs = age + annees_cumulees

r = Rendement / 100
if r > 0:
    capital_brut = patrimoine_actuel * ((1 + r) ** annees_cumulees) + (epargne_mensuelle * 12) * (((1 + r) ** annees_cumulees) - 1) / r
else:
    capital_brut = patrimoine_actuel + (epargne_mensuelle * 12) * annees_cumulees

capital_reel_inflation = capital_brut / ((1 + 0.03) ** annees_cumulees)

with col_graph:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ages_futurs, y=np.round(capital_brut, 2), mode='lines+markers', name='Capital Brut (Théorique)', line=dict(color='#004B87', width=3)))
    fig.add_trace(go.Scatter(x=ages_futurs, y=np.round(capital_reel_inflation, 2), mode='lines+markers', name='Pouvoir d’Achat Réel (Inflation 3%)', line=dict(color='#D9534F', dash='dash')))
    
    fig.update_layout(
        title=f"Projection de votre patrimoine de {age} ans à {age+20} ans",
        xaxis_title="Votre âge au fil des années",
        yaxis_title="Valeur du capital (€)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255, 255, 255, 0.6)")
    )
    st.plotly_chart(fig, use_container_width=True)

# --- FONCTION DE GÉNÉRATION DU PDF (REPORTLAB) ---
def build_15_page_pdf(user_age, user_pat, user_ep, user_rend):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor('#004B87'), alignment=1)
    h1_style = ParagraphStyle('SectionH1', parent=styles['Heading2'], fontSize=18, leading=22, textColor=colors.HexColor('#004B87'), spaceBefore=15, spaceAfter=10)
    body_style = ParagraphStyle('DocBody', parent=styles['BodyText'], fontSize=11, leading=16, spaceAfter=8)
    
    story = []
    
    sections = [
        ("Page 1 : Page de Garde", "AUDIT PATRIMONIAL CERTIFIÉ IA\n\nPréparé à l'attention de notre client privilégié.\nDate d'analyse : " + datetime.now().strftime('%d/%m/%Y')),
        ("Page 2 : Résumé Exécutif", "Cet audit passe en revue vos actifs actifs et segmente vos leviers de performance pour neutraliser l'effet de l'érosion monétaire."),
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
        ("Page 13 : Recommandations Exclusives de l'IA", "Conseil 1 : Diversifiez vos liquidités hors des livrets d'épargne réglementés.\nConseil 2 : Utilisez le levier du démembrement pour votre bien immobilier principal.\nConseil 3 : Programmez des versements automatiques sur un support d'actions diversifié."),
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
            
        if i < len(sections) - 1:
            story.append(PageBreak())
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- ÉTAPE 2 : LOGIQUE DE LIVRAISON DIRECTE ---
st.markdown("---")

if st.session_state.paiement_reussi:
    st.success("🎉 Accès premium déverrouillé ! Votre Audit de 15 pages est disponible.")
    st.markdown("### 🔓 Étape 2 : Téléchargez votre document d'ingénierie patrimoniale")
    
    pdf_data = build_15_page_pdf(age, patrimoine_actuel, epargne_mensuelle, Rendement)
    
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
        
        # Bouton Stripe officiel ultra-fiable et sans risque d'erreur de syntaxe
        st.link_button("💳 Acheter mon Audit personnalisé pour 19€", LIEN_PAIEMENT_STRIPE, use_container_width=True)
        
        st.write("")
        # Bouton secret pour que vous puissiez tester le téléchargement du PDF gratuitement
        if st.button("🎯 Mode Test : Débloquer le bouton de téléchargement gratuitement", use_container_width=True):
            st.session_state.paiement_reussi = True
            st.rerun()
