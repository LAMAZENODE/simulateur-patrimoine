import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from google import genai

# 1. CONFIGURATION INITIALE DE LA PAGE
st.set_page_config(page_title="Cabinet Digital", layout="wide")

# Initialisation rigoureuse des états système
if "sim_ok" not in st.session_state: st.session_state.sim_ok = False
if "pay_ok" not in st.session_state: st.session_state.pay_ok = False
if "pdf_pret" not in st.session_state: st.session_state.pdf_pret = None

try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur technique de clé API : {e}")
    st.stop()

# 2. ALGORITHME D'AUDIT DE SECOURS EN CAS DE SATURE DE QUOTAS (429)
def obtenir_audit_secours(age, patrimoine, epargne, rendement):
    return f"""PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION
A {age} ans, la structuration de votre patrimoine de {patrimoine:,.0f} € doit répondre à un objectif de capitalisation performante sur 20 ans. Votre effort d'épargne mensuel de {epargne} € maximisera l'effet des intérêts composés. Nous préconisons le Plan d'Épargne en Actions (PEA) pour l'exonération d'impôt après 5 ans, et l'Assurance-Vie pour sa fiscalité adoucie après 8 ans et ses avantages successoraux. Le PER complétera ce dispositif pour réduire votre impôt immédiat.

PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION
La recherche d'un rendement cible de {rendement} % par an implique une diversification méthodique. La poche de sécurité court terme utilisera les fonds en euros garantis. La poche immobilière s'appuiera sur des parts de SCPI pour générer des loyers réguliers décorrélés des marchés boursiers. Enfin, la poche de croissance investira en actions internationales via des ETF. L'investissement programmé de vos {epargne} € par mois lissera le risque de marché.

PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE
Pour concrétiser cette stratégie, voici l'allocation cible recommandée :
- Poche de Sécurité (40% des actifs) : Fonds en euros pour stabiliser le portefeuille global.
- Poche Immobilière Papier (30% des actifs) : Sélection de SCPI de rendement diversifiées.
- Poche Actions Croissance (30% des actifs) : Investissement via votre PEA sur un ETF mondial MSCI World."""

def generer_analyse_ia(client_ia_instance, age, patrimoine, epargne, rendement):
    prompt = f"Rédige un rapport patrimonial dense pour un client de {age} ans ayant {patrimoine} euros de capital et {epargne} euros d'épargne. Crée trois grands chapitres textuels : PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION, PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION, PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE. Écris en texte brut sans dièses ni étoiles."
    try:
        reponse = client_ia_instance.models.generate_content(
            model="gemini-3.6-flash", contents=prompt,
            config={"max_output_tokens": 4096, "temperature": 0.3}
        )
        return reponse.text if reponse.text else obtenir_audit_secours(age, patrimoine, epargne, rendement)
    except Exception:
        return obtenir_audit_secours(age, patrimoine, epargne, rendement)

# 3. MOTEUR DE CONSTRUCTION ET COMPILATION DU PDF DE 15 PAGES
def creer_pdf(texte_ia, age, patrimoine, epargne, rendement):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    
    style_titre = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#004B87'), alignment=1)
    style_section = ParagraphStyle('S2', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#004B87'), spaceBefore=20, spaceAfter=10)
    style_corps = ParagraphStyle('C1', parent=styles['BodyText'], fontSize=10, leading=15)

    # PAGE 1 : DE GARDE
    story.append(Spacer(1, 150))
    story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", style_titre))
    story.append(PageBreak())

    # PAGE 2 : SOMMAIRE
    story.append(Paragraph("SOMMAIRE EXÉCUTIF", style_section))
    t_som = Table([["1. Profil", "Page 3"], ["2. Projections", "Page 4"], ["3. IA", "Page 6"], ["4. Annexes", "Page 12"], ["5. Signatures", "Page 15"]], colWidths=[380, 100])
    t_som.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 8), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9'))]))
    story.append(t_som); story.append(PageBreak())

    # PAGE 3 : SYNTHÈSE
    story.append(Paragraph("1. Synthèse du profil", style_section))
    t_p = Table([["Métrique", "Valeur"], ["Âge", f"{age} ans"], ["Patrimoine", f"{patrimoine:,.0f} €"], ["Épargne", f"{epargne} €/mois"]], colWidths=[240, 240])
    t_p.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), colors.HexColor('#F1F5F9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
    story.append(t_p); story.append(PageBreak())

    # PAGES 4 & 5 : TABLEAUX COMPTABLES DYNAMIQUES
    story.append(Paragraph("2. Projections financières", style_section))
    table_finance_data = [["Année", "Capital Initial", "Épargne", "Intérêts", "Capital Final"]]
    cap_courant = patrimoine
    for an in range(1, 21):
        interets = (cap_courant + (epargne * 12) / 2) * (rendement / 100)
        cap_final = cap_courant + (epargne * 12) + interets
        table_finance_data.append([f"Année {an}", f"{cap_courant:,.0f} €", f"{(epargne*12):,.0f} €", f"{interets:,.0f} €", f"{cap_final:,.0f} €"])
        cap_courant = cap_final

    t_fin1 = Table(table_finance_data[:12], colWidths=[80, 100, 100, 100, 100])
    t_fin1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('FONTSIZE', (0,0), (-1,-1), 9)]))
    story.append(t_fin1); story.append(PageBreak())
    
    story.append(Paragraph("2. Projections financières (Suite)", style_section))
    t_fin2 = Table([table_finance_data[0]] + table_finance_data[12:], colWidths=[80, 100, 100, 100, 100])
    t_fin2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('FONTSIZE', (0,0), (-1,-1), 9)]))
    story.append(t_fin2)

    # PAGES 6 À 11 : INTÉGRATION INTELLIGENTE DU TEXTE IA
    paragraphes = texte_ia.split('\n')
    for para in paragraphes:
        txt = para.strip()
        if txt:
            if txt.upper().startswith("PARTIE") or txt.upper().startswith("CHAPITRE"):
                story.append(PageBreak()); story.append(Paragraph(txt, style_section))
            else:
                story.append(Paragraph(txt, style_corps))

    # PAGES 12 À 14 : LES 5 ANNEXES PÉDAGOGIQUES
    annexes = [
        ("A", "L'Assurance-Vie", "Cadre fiscal avantageux après 8 ans. Idéal pour capitaliser sur le long terme à l'abri de l'impôt direct."),
        ("B", "Le PEA", "Exonération complète d'impôt sur les plus-values et les dividendes réinvestis après 5 ans de détention."),
        ("C", "Le PER", "Le PER offre un levier fiscal immédiat en vous permettant de déduire vos versements du revenu imposable."),
        ("D", "Les SCPI", "Les Sociétés Civiles de Placement Immobilier permettent d'investir dans la pierre et de percevoir des loyers."),
        ("E", "La Succession", "Anticiper la transmission de son patrimoine au travers d'abattements légaux pour protéger ses proches.")
    ]
    for lettre, titre, desc in annexes:
        story.append(PageBreak())
        story.append(Paragraph(f"4. Annexe {lettre} : Guide sur {titre}", style_section))
        story.append(Paragraph(desc, style_corps))
        story.append(Paragraph("Ce guide technique rédigé par nos experts résume les règles réglementaires et fiscales en vigueur.", style_corps))

    # PAGE 15 : MENTIONS LÉGALES ET COMPTEUR DE SIGNATURES
    story.append(PageBreak())
    story.append(Paragraph("5. Mentions Légales et Signatures", style_section))
    story.append(Paragraph("Ce document indicatif est généré automatiquement par IA. Tout investissement comporte un risque de perte en capital.", style_corps))
    story.append(Spacer(1, 30))
    t_s = Table([["Signature de l'Expert IA", "Signature du Client"], ["Certifié conforme", "Bon pour accord"]], colWidths=[240, 240])
    t_s.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94A3B8')), ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 40)]))
    story.append(t_s)

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# 4. CONSTRUIRE L'INTERFACE UTILISATEUR COMPLÈTE (STREAMLIT)
st.markdown("### 📊 Étape 1 : Votre simulation immédiate et gratuite")
col_inputs, col_graph = st.columns(2)

with col_inputs:
    age = st.number_input("Votre âge", min_value=18, max_value=100, value=35)
    patrimoine_actuel = st.number_input("Patrimoine actuel (€)", min_value=0, value=50000)
    epargne_mensuelle = st.number_input("Épargne mensuelle (€)", min_value=0, value=300)
    Rendement = st.slider("Hypothèse de rendement annuel (%)", 1.0, 10.0, 4.0)
    if st.button("🧮 Calculer mes projections gratuitement"):
        st.session_state.sim_ok = True
        st.session_state.pdf_pret = None

with col_graph:
    if st.session_state.sim_ok:
        annees = np.arange(0, 21)
        capital = patrimoine_actuel * ((1 + Rendement/100) ** annees) + (epargne_mensuelle * 12) * ((1 + Rendement/100) ** annees - 1) / (Rendement/100)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=annees, y=capital, mode='lines+markers', name='Votre projection', line=dict(color='#004B87')))










    

























