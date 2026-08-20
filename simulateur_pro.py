import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from google import genai

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Cabinet Digital - Optimisation Patrimoniale", page_icon="🛡️", layout="wide")

# 2. INITIALISATION DES ÉTATS DE SESSION
if "sim_ok" not in st.session_state: st.session_state.sim_ok = False
if "pay_ok" not in st.session_state: st.session_state.pay_ok = False
if "pdf_data" not in st.session_state: st.session_state.pdf_data = None

# 3. ACCÈS SÉCURISÉ API GEMINI
try:
    client_ia = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Erreur Configuration API : {e}")
    st.stop()

# 4. FONCTION COMPACTE DE GÉNÉRATION DU PDF (15 PAGES)
def fabriquer_rapport_pdf(texte_ia, age, patrimoine, epargne, rendement):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    
    styles = getSampleStyleSheet()
    s_titre = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=26, leading=32, textColor=colors.HexColor('#004B87'), alignment=1, spaceAfter=20)
    s_sub = ParagraphStyle('S1', parent=styles['Heading2'], fontSize=14, leading=20, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=180)
    s_sec = ParagraphStyle('S2', parent=styles['Heading2'], fontSize=15, leading=19, textColor=colors.HexColor('#004B87'), spaceBefore=22, spaceAfter=12, keepWithNext=True)
    s_txt = ParagraphStyle('C1', parent=styles['BodyText'], fontSize=10.5, leading=16, textColor=colors.HexColor('#1E293B'), spaceAfter=10)

    # P1: GARDE
    story.append(Spacer(1, 100))
    story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", s_titre))
    story.append(Paragraph("PROJECTION FINANCIÈRE À 20 ANS & OPTIMISATION", s_sub))
    story.append(PageBreak())

    # P2: SOMMAIRE
    story.append(Paragraph("SOMMAIRE EXÉCUTIF", s_sec))
    som_data = [["1. Synthèse du profil", "Page 3"], ["2. Projections comptables (Années 1 à 20)", "Page 4"], ["3. Orientations stratégiques IA", "Page 6"], ["4. Annexes et fiches réglementaires (A à E)", "Page 12"], ["5. Signatures et décharges", "Page 15"]]
    t_som = Table(som_data, colWidths=[400, 100])
    t_som.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 6), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
    story.append(t_som); story.append(PageBreak())

    # P3: PROFIL
    story.append(Paragraph("1. Synthèse du profil de l'investisseur", s_sec))
    story.append(Paragraph("Ce document dresse une analyse approfondie pour optimiser l'efficience fiscale de vos investissements.", s_txt))
    prof_data = [["Âge", f"{age} ans"], ["Patrimoine Initial", f"{patrimoine:,.0f} €"], ["Épargne récurrente", f"{epargne} €/mois"], ["Objectif Rendement", f"{rendement} %/an"]]
    t_prof = Table(prof_data, colWidths=[250, 250])
    t_prof.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), colors.HexColor('#F1F5F9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('PADDING', (0,0), (-1,-1), 6)]))
    story.append(t_prof); story.append(PageBreak())

    # P4 & P5: TABLEAU COMPTABLE SUR 20 ANS
    story.append(Paragraph("2. Tableau d'évolution de l'épargne capitalisée", s_sec))
    fin_data = [[Paragraph("<b>Année</b>", s_txt), Paragraph("<b>Capital Initial</b>", s_txt), Paragraph("<b>Épargne</b>", s_txt), Paragraph("<b>Intérêts</b>", s_txt), Paragraph("<b>Capital Final</b>", s_txt)]]
    courant = patrimoine
    for an in range(1, 21):
        int_gagnes = (courant + (epargne * 12) / 2) * (rendement / 100)
        final = courant + (epargne * 12) + int_gagnes
        fin_data.append([f"Année {an}", f"{courant:,.0f} €", f"{(epargne*12):,.0f} €", f"{int_gagnes:,.0f} €", f"{final:,.0f} €"])
        courant = final

    t_f1 = Table(fin_data[:12], colWidths=[70, 105, 105, 105, 105])
    t_f1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]), ('FONTSIZE', (0,0), (-1,-1), 9)]))
    story.append(t_f1); story.append(PageBreak())
    
    story.append(Paragraph("2. Tableau d'évolution (Suite)", s_sec))
    t_f2 = Table([fin_data[0]] + fin_data[12:], colWidths=[70, 105, 105, 105, 105])
    t_f2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]), ('FONTSIZE', (0,0), (-1,-1), 9)]))
    story.append(t_f2)

    # P6 à P11: TEXTE IA
    for p in texte_ia.split('\n'):
        t_p = p.strip()
        if not t_p: continue
        if "PARTIE" in t_p:
            story.append(PageBreak())
            story.append(Paragraph(t_p, s_sec))
        else:
            story.append(Paragraph(t_p, s_txt))

    # P12 à P14: 5 ANNEXES TECHNIQUES POUR GARANTIR LE VOLUME DE 15 PAGES
    guides = [
        ("A", "L'Assurance-Vie", "Enveloppe centrale pour capitaliser sur le long terme à l'abri de l'impôt immédiat."),
        ("B", "Le PEA (Actions)", "Exonération complète d'impôt sur les plus-values et dividendes après 5 ans."),
        ("C", "Le PER (Retraite)", "PER offrant un puissant levier de déduction fiscale sur vos revenus imposables."),
        ("D", "Les SCPI (Pierre-Papier)", "Placement immobilier collectif distribuant des revenus fonciers réguliers."),
        ("E", "La Succession", "Dispositifs légaux indispensables pour réduire les futurs droits de transmission.")
    ]
    for lettre, titre, desc in guides:
        story.append(PageBreak())
        story.append(Paragraph(f"4. Annexe {lettre} : Guide sur {titre}", s_sec))
        story.append(Paragraph(desc, s_txt))
        story.append(Paragraph("Ce guide récapitule les règles réglementaires et fiscales du marché en vigueur.", s_txt))

    # P15: VALIDATION ET SIGNATURES
    story.append(PageBreak())
    story.append(Paragraph("5. Mentions Légales et Signatures", s_sec))
    story.append(Paragraph("Ce rapport automatisé est délivré à titre informatif. Tout investissement comporte un risque de perte.", s_txt))
    story.append(Spacer(1, 30))
    sig_data = [[Paragraph("<b>Signature Cabinet (IA)</b>", s_txt), Paragraph("<b>Signature Client</b>", s_txt)], ["Document certifié conforme\nCabinet Digital", "Bon pour accord et validation\ndes choix stratégiques"]]
    t_sig = Table(sig_data, colWidths=[250, 250])
    t_sig.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94A3B8')), ('BOTTOMPADDING', (0,0), (-1,-1), 40)]))
    story.append(t_sig)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

# 5. CONSTRUIRE L'INTERFACE UTILISATEUR (STREAMLIT)
st.markdown("### 📊 Étape 1 : Votre simulation immédiate et gratuite")
c_in, c_gr = st.columns([1, 2])

with c_in:
    v_age = st.number_input("Votre âge", min_value=18, max_value=100, value=35)
    v_pat = st.number_input("Patrimoine actuel (€)", min_value=0, value=50000)
    v_epa = st.number_input("Épargne mensuelle (€)", min_value=0, value=300)
    v_ren = st.slider("Hypothèse de rendement annuel (%)", 1.0, 10.0, 4.0)
    if st.button("🧮 Calculer mes projections gratuitement"):
        st.session_state.sim_ok = True
        st.session_state.pdf_data = None

with c_gr:
    if st.session_state.sim_ok:
        ans = np.arange(0, 21)
        caps = v_pat * ((1 + v_ren/100) ** ans) + (v_epa * 12) * ((1 + v_ren/100) ** ans - 1) / (v_ren/100)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ans, y=caps, mode='lines+markers', name='Projection', line=dict(color='#004B87')))
        fig.update_layout(title="Évolution de votre capital", xaxis_title="Années", yaxis_title="Capital (€)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ajustez vos paramètres à gauche puis cliquez sur Calculer.")

# ÉTAPE 2 : LE BLOC COMMERCIAL
if st.session_state.sim_ok:
    st.markdown("---")
    st.markdown("### 🔒 Étape 2 : Obtenez votre Audit Certifié complet (15 pages)")
    col_v, col_ac = st.columns(2)
    with col_v:
        st.markdown("**Contenu du livret de 15 pages :**\n* 📉 Optimisation Fiscale personnalisée.\n* 🛡️ Sécurisation du portefeuille à 20 ans.\n* 🤖 Recommandations algorithmiques d'allocations.")
    with col_ac:
        st.error("💡 Tarif de lancement : 19,00 € TTC (au lieu de 49 €)")
        if st.button("💳 Débloquer mon Audit PDF Complet (19 €)"):
            st.session_state.pay_ok = True

# ÉTAPE 3 : LE BLOC DE TÉLÉCHARGEMENT DIRECT
if st.session_state.pay_ok:
    st.markdown("---")
    st.success("✅ Accès accordé ! Votre livret stratégique a été configuré.")
    
    if st.session_state.pdf_data is None:
        with st.spinner("Analyse des marchés et assemblage du document de 15 pages..."):
            prompt_ia = f"Rédige un rapport patrimonial dense pour un client de {v_age} ans ayant {v_pat}e de capital et {v_epa}e d'épargne par mois. Crée trois chapitres textuels distincts : PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION, PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION, PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE. Écris en texte brut sans dièses ni étoiles."
            try:
                rep = client_ia.models.generate_content(model="gemini-3.6-flash", contents=prompt_ia, config={"max_output_tokens": 4096, "temperature": 0.3})
                txt_ia = rep.text if rep.text else "Audit Standard de performance."
            except Exception as e:
                txt_ia = f"Audit Patrimonial Standard pour un capital de {v_pat} €."




















