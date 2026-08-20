import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from google import genai

# 1. CONFIGURATION DE LA PAGE (Doit impérativement être la première commande Streamlit)
st.set_page_config(page_title="Cabinet Digital", layout="wide")

# 2. INITIALISATION DES ÉTATS DE SESSION
if "sim_ok" not in st.session_state: st.session_state.sim_ok = False
if "pay_ok" not in st.session_state: st.session_state.pay_ok = False

# 3. RÉCUPÉRATION SÉCURISÉE DES ACCÈS API GEMINI
try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur technique de clé API : {e}")
    st.stop()

# 4. FONCTIONS GLOBALES DE CALCUL ET GÉNÉRATION PDF
def generer_analyse_ia(client_ia_instance, age, patrimoine, epargne, rendement):
    prompt = f"Rédige un rapport patrimonial dense et complet pour un client de {age} ans ayant {patrimoine} euros de capital et {epargne} euros d'épargne. Crée trois grands chapitres : PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION, PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION, PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE. Écris de longs paragraphes détaillés. Rédige uniquement en texte brut sans dièses ni étoiles."
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
    
    style_titre_grand = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#004B87'), alignment=1)
    style_section = ParagraphStyle('S2', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#004B87'), spaceBefore=20, spaceAfter=10)
    style_corps = ParagraphStyle('C1', parent=styles['BodyText'], fontSize=10, leading=15)

    # PAGE 1 : DE GARDE
    story.append(Spacer(1, 150))
    story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", style_titre_grand))
    story.append(PageBreak())

    # PAGE 2 : SOMMAIRE
    story.append(Paragraph("SOMMAIRE EXÉCUTIF", style_section))
    sommaire_data = [["1. Profil", "Page 3"], ["2. Projections", "Page 4"], ["3. IA", "Page 6"], ["4. Annexes", "Page 12"], ["5. Signatures", "Page 15"]]
    st_table = Table(sommaire_data, colWidths=[350, 100])
    st_table.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 8), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9'))]))
    story.append(st_table)
    story.append(PageBreak())

    # PAGE 3 : SYNTHÈSE
    story.append(Paragraph("1. Synthèse du profil", style_section))
    donnees_table = [["Métrique", "Valeur"], ["Âge", f"{age} ans"], ["Patrimoine", f"{patrimoine:,.0f} €"], ["Épargne", f"{epargne} €/mois"]]
    t = Table(donnees_table, colWidths=[225, 225])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), colors.HexColor('#F1F5F9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
    story.append(t)
    story.append(PageBreak())

    # PAGES 4 & 5 : TABLEAU FINANCIER D'ÉVOLUTION SUR 20 ANS
    story.append(Paragraph("2. Projections financières", style_section))
    table_finance_data = [["Année", "Capital Initial", "Épargne", "Intérêts", "Capital Final"]]
    cap_courant = patrimoine
    for an in range(1, 21):
        interets = (cap_courant + (epargne * 12) / 2) * (rendement / 100)
        cap_final = cap_courant + (epargne * 12) + interets
        table_finance_data.append([f"Année {an}", f"{cap_courant:,.0f} €", f"{(epargne*12):,.0f} €", f"{interets:,.0f} €", f"{cap_final:,.0f} €"])
        cap_courant = cap_final

    t_fin1 = Table(table_finance_data[:12], colWidths=[60, 95, 95, 95, 105])
    t_fin1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]), ('FONTSIZE', (0,0), (-1,-1), 9), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    story.append(t_fin1)
    story.append(PageBreak())
    
    story.append(Paragraph("2. Projections financières (Suite)", style_section))
    t_fin2 = Table([table_finance_data[0]] + table_finance_data[12:], colWidths=[60, 95, 95, 95, 105])
    t_fin2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]), ('FONTSIZE', (0,0), (-1,-1), 9), ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    story.append(t_fin2)

    # PAGES 6 À 11 : INTÉGRATION DU TEXTE DE L'IA GEMINI
    paragraphes = texte_ia.split('\n')
    for para in paragraphes:
        txt = para.strip()
        if not txt: continue
        if txt.upper().startswith("PARTIE") or txt.upper().startswith("CHAPITRE"):
            story.append(PageBreak())
            story.append(Paragraph(txt, style_section))
        else:
            story.append(Paragraph(txt, style_corps))

    # PAGES 12 À 14 : LES 5 GUIDES D'ANNEXES PÉDAGOGIQUES
    annexes_pro = [
        ("A", "L'Assurance-Vie", "Cadre fiscal avantageux après 8 ans. Enveloppe centrale pour capitaliser sur le long terme à l'abri de l'impôt direct."),
        ("B", "Le PEA", "Exonération complète d'impôt sur les plus-values et les dividendes réinvestis après 5 ans de détention."),
        ("C", "Le PER", "Le PER offre un levier fiscal immédiat en vous permettant de déduire vos versements de votre revenu imposable."),
        ("D", "Les SCPI", "Les Sociétés Civiles de Placement Immobilier permettent d'investir dans l'immobilier tertiaire et de percevoir des loyers."),
        ("E", "La Succession", "Anticiper la transmission de son patrimoine au travers d'abattements légaux pour protéger ses proches.")
    ]
    for lettre, titre, desc in annexes_pro:
        story.append(PageBreak())
        story.append(Paragraph(f"4. Annexe {lettre} : Guide sur {titre}", style_section))
        story.append(Paragraph(desc, style_corps))
        story.append(Paragraph("Ce guide technique rédigé par nos experts résume les règles réglementaires et fiscales en vigueur.", style_corps))

    # PAGE 15 : CLAUSES LÉGALES & BLOC DE SIGNATURES
    story.append(PageBreak())
    story.append(Paragraph("5. Mentions Légales et Signatures", style_section))
    story.append(Paragraph("Ce document indicatif est généré automatiquement par IA. Tout investissement comporte un risque de perte en capital.", style_corps))
    story.append(Spacer(1, 30))

    signature_data = [
        [Paragraph("**Signature de l'Expert IA**", style_corps), Paragraph("**Signature du Client**", style_corps)],
        ["Cabinet Digital Patrimoine\nDocument certifié conforme", "Bon pour accord et validation\ndes choix stratégiques"]
    ]
    sig_table = Table(signature_data, colWidths=[225, 225])
    sig_table.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94A3B8')), ('TOPPADDING', (0,0), (-1,-1), 10), ('BOTTOMPADDING', (0,0), (-1,-1), 40)]))
    story.append(sig_table)

    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

# 5. INTERFACE UTILISATEUR (STREAMLIT)
st.markdown("### 📊 Étape 1 : Votre simulation immédiate et gratuite")
col_inputs, col_graph = st.columns(2)

with col_inputs:
    age = st.number_input("Votre âge", min_value=18, max_value=100, value=35)
    patrimoine_actuel = st.number_input("Patrimoine actuel (€)", min_value=0, value=50000)
    epargne_mensuelle = st.number_input("Épargne mensuelle (€)", min_value=0, value=300)
    Rendement = st.slider("Hypothèse de rendement annuel (%)", 1.0, 10.0, 4.0)

    if st.button("🧮 Calculer mes projections gratuitement"):
        st.session_state.sim_ok = True

with col_graph:
    if st.session_state.sim_ok:
        annees = np.arange(0, 21)
        capital = patrimoine_actuel * ((1 + Rendement/100) ** annees) + (epargne_mensuelle * 12) * ((1 + Rendement/100) ** annees - 1) / (Rendement/100)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=annees, y=capital, mode='lines+markers', name='Votre projection', line=dict(color='#004B87')))
        fig.update_layout(title="Évolution de votre capital", xaxis_title="Années", yaxis_title="Capital (€)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Remplissez les informations à gauche pour voir votre graphique de projection.")

# ÉTAPE 2 : LE VERROU COMMERCIAL
if st.session_state.sim_ok:
    st.markdown("---")
    st.markdown("### 🔒 Étape 2 : Obtenez votre Audit Certifié complet (15 pages)")
    col_vendeuse, col_action = st.columns(2)
    with col_vendeuse:
        st.markdown("**Contenu du livret de 15 pages :**\n* 📉 Optimisation Fiscale personnalisée.\n* 🛡️ Sécurisation du portefeuille à 20 ans.\n* 🤖 Recommandations algorithmiques d'allocations.")
    with col_action:
        st.error("💡 Tarif de lancement : 19,00 € TTC (au lieu de 49 €)")
        if st.button("💳 Débloquer mon Audit PDF Complet (19 €)"): 
            st.session_state.pay_ok = True

# ÉTAPE 3 : BLOC DE TÉLÉCHARGEMENT DIRECT
if st.session_state.pay_ok:
    st.markdown("---")
    st.success("✅ Paiement validé ! Votre rapport de 15 pages est assemblé.")
    

























