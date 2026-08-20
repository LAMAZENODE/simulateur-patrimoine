import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from google import genai

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Cabinet Digital - Optimisation Patrimoniale", page_icon="🛡️", layout="wide")

# 2. INITIALISATION DES ÉTATS DE SESSION
if "simulation_faite" not in st.session_state:
    st.session_state.simulation_faite = False
if "paiement_pdf_ok" not in st.session_state:
    st.session_state.paiement_pdf_ok = False
if "pdf_pret" not in st.session_state:
    st.session_state.pdf_pret = None

# 3. RÉCUPÉRATION SÉCURISÉE DES ACCÈS API GEMINI
try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur de configuration technique d'API : {e}")
    st.stop()

# 4. FONCTIONS GLOBALES DE CALCUL AND GÉNÉRATION PDF
def generer_analyse_ia(client_ia_instance, age, patrimoine, epargne, rendement):
    prompt = f"En tant qu'expert en gestion de patrimoine, rédige un rapport d'audit détaillé pour un client de {age} ans ayant {patrimoine} euros de capital et {epargne} euros d'épargne mensuelle. Rédige trois grandes parties distinctes : PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION, PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION, PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE. N'utilise aucun caractère markdown comme des étoiles ou des dièses."
    try:
        reponse = client_ia_instance.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={"max_output_tokens": 4096, "temperature": 0.3}
        )
        return reponse.text if reponse.text else "Erreur : Contenu vide."
    except Exception as e:
        return f"Erreur technique de l'API Gemini : {str(e)}"

def creer_pdf(texte_ia, age, patrimoine, epargne, rendement):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    
    styles = getSampleStyleSheet()
    style_titre_grand = ParagraphStyle('TitreGrand', parent=styles['Heading1'], fontSize=28, leading=34, textColor=colors.HexColor('#004B87'), alignment=1, spaceAfter=20)
    style_sous_titre_grand = ParagraphStyle('SubGrand', parent=styles['Heading2'], fontSize=15, leading=22, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=180)
    style_mention_garde = ParagraphStyle('MentionGarde', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#94A3B8'), alignment=1)
    style_section = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, leading=20, textColor=colors.HexColor('#004B87'), spaceBefore=25, spaceAfter=15, keepWithNext=True)
    style_corps = ParagraphStyle('Corps', parent=styles['BodyText'], fontSize=10.5, leading=17, textColor=colors.HexColor('#1E293B'), spaceAfter=12)

    # PAGE 1 : DE GARDE
    story.append(Spacer(1, 100))
    story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", style_titre_grand))
    story.append(Paragraph("PROJECTION FINANCIÈRE À 20 ANS", style_sous_titre_grand))
    story.append(Paragraph("Document confidentiel édité par Cabinet Digital IA", style_mention_garde))
    story.append(PageBreak())

    # PAGE 2 : SOMMAIRE
    story.append(Paragraph("SOMMAIRE EXÉCUTIF", style_section))
    sommaire_data = [["1. Synthèse du profil", "Page 3"], ["2. Tableau d'évolution", "Page 4"], ["3. Analyse de l'IA", "Page 6"], ["4. Annexes réglementaires", "Page 12"], ["5. Signatures", "Page 15"]]
    st_table = Table(sommaire_data, colWidths=[400, 100])
    st_table.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 8), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9'))]))
    story.append(st_table)
    story.append(PageBreak())

    # PAGE 3 : SYNTHÈSE
    story.append(Paragraph("1. Synthèse du profil de l'investisseur", style_section))
    donnees_table = [["Âge", f"{age} ans"], ["Patrimoine", f"{patrimoine:,.0f} €"], ["Épargne", f"{epargne} €/mois"], ["Rendement", f"{rendement} %"]]
    t = Table(donnees_table, colWidths=[250, 250])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), colors.HexColor('#F1F5F9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
    story.append(t)
    story.append(PageBreak())

    # PAGES 4 & 5 : TABLEAU COMPTABLE DYNAMIQUE SUR 20 ANS
    story.append(Paragraph("2. Tableau d'évolution de l'épargne capitalisée", style_section))
    table_finance_data = [[Paragraph("<b>Année</b>", style_corps), Paragraph("<b>Capital initial</b>", style_corps), Paragraph("<b>Épargne versée</b>", style_corps), Paragraph("<b>Intérêts générés</b>", style_corps), Paragraph("<b>Capital Final</b>", style_corps)]]
    cap_courant = patrimonio_actuel = patrimoine
    for an in range(1, 21):
        interets = (cap_courant + (epargne * 12) / 2) * (rendement / 100)
        cap_final = cap_courant + (epargne * 12) + interets
        table_finance_data.append([f"Année {an}", f"{cap_courant:,.0f} €", f"{(epargne*12):,.0f} €", f"{interets:,.0f} €", f"{cap_final:,.0f} €"])
        cap_courant = cap_final

    t_fin1 = Table(table_finance_data[:12], colWidths=[80, 105, 105, 105, 105])
    t_fin1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]), ('FONTSIZE', (0,0), (-1,-1), 9), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    story.append(t_fin1)
    story.append(PageBreak())
    
    story.append(Paragraph("2. Tableau d'évolution (Suite)", style_section))
    t_fin2 = Table([table_finance_data[0]] + table_finance_data[12:], colWidths=[80, 105, 105, 105, 105])
    t_fin2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]), ('FONTSIZE', (0,0), (-1,-1), 9), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    story.append(t_fin2)

    # PAGES 6 À 11 : INTÉGRATION DU TEXTE IA
    paragraphes = texte_ia.split('\n')
    for para in paragraphes:
        txt = para.strip()
        if not txt: continue
        if "PARTIE 1" in txt or "STRATÉGIE" in txt:
            story.append(PageBreak())
            story.append(Paragraph("3.1 Stratégie fiscale d'optimisation", style_section))
        elif "PARTIE 2" in txt or "GESTION DES RISQUES" in txt:
            story.append(PageBreak())
            story.append(Paragraph("3.2 Gestion des risques et sécurisation", style_section))
        elif "PARTIE 3" in txt or "ALLOCATION" in txt:
            story.append(PageBreak())
            story.append(Paragraph("3.3 Stratégie d'allocation recommandée", style_section))
        else:
            story.append(Paragraph(txt, style_corps))

    # PAGES 12 À 14 : GUIDE DES 5 ANNEXES POUR ATTEINDRE LES 15 PAGES
    annexes_pro = [
        ("A", "L'Assurance-Vie et la capitalisation", "L'optimisation globale implique l'usage de cette enveloppe pour capitaliser les intérêts sur le long terme à l'abri de l'impôt de base. Les retraits après 8 ans bénéficient d'abattements fiscaux annuels très avantageux."),
        ("B", "Le PEA (Plan d'Épargne en Actions)", "Le PEA est une enveloppe idéale pour dynamiser votre capital sur les marchés européens. Après 5 ans de détention, l'intégralité des gains et dividendes est exonérée d'impôt sur le revenu."),
        ("C", "Le PER (Plan d'Épargne Retraite)", "Le PER offre un levier fiscal immédiat en vous permettant de déduire vos versements de votre revenu imposable. C'est l'outil parfait pour transformer votre impôt en capital pour l'avenir."),
        ("D", "L'Immobilier de Rendement (Pierre-Papier / SCPI)", "Les Sociétés Civiles de Placement Immobilier permettent d'investir dans l'immobilier tertiaire dès quelques centaines d'euros. Elles distribuent des revenus réguliers sous forme de loyers sans aucune contrainte de gestion."),
        ("E", "La Transmission et l'Optimisation Successorale", "Anticiper la transmission de son patrimoine est essentiel pour protéger ses proches. L'utilisation conjointe de l'assurance-vie et des donations permet de réduire drastiquement les futurs droits de succession.")
    ]

    for lettre, titre, description in annexes_pro:
        story.append(PageBreak())
        story.append(Paragraph(f"4. Annexe {lettre} : Guide sur {titre}", style_section))
        story.append(Paragraph(description, style_corps))
        story.append(Paragraph("Ce guide technique rédigé par nos experts résume les règles fiscales en vigueur.", style_corps))

    # PAGE 15 : LEGAL & SIGNATURES
    story.append(PageBreak())
    story.append(Paragraph("5. Mentions Légales et Signatures", style_section))
    story.append(Paragraph("Ce document indicatif est généré automatiquement par IA. Tout investissement comporte un risque de perte en capital.", style_corps))
    story.append(Spacer(1, 30))

    signature_data = [
        [Paragraph("**Signature de l'Expert IA**", style_corps), Paragraph("**Signature du Client**", style_corps)],
        ["Cabinet Digital Patrimoine\nDocument certifié conforme", "Bon pour accord et validation\ndes choix stratégiques"]
    ]
    sig_table = Table(signature_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94A3B8')), ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 40)]))
    story.append(sig_table)

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# 5. INTERFACE UTILISATEUR (STREAMLIT)















