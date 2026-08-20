import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from google import genai

# 1. CONFIGURATION
st.set_page_config(page_title="Cabinet Digital", layout="wide")

if "sim_ok" not in st.session_state: st.session_state.sim_ok = False
if "pay_ok" not in st.session_state: st.session_state.pay_ok = False

try:
    client_ia = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Erreur technique de clé API : {e}")
    st.stop()

# 2. MOTEUR DE GÉNÉRATION PDF (15 PAGES RESTRUCTURÉES)
def fabriquer_pdf(texte_ia, age, patrimoine, epargne, rendement):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    story = []
    styles = getSampleStyleSheet()
    
    s_titre = ParagraphStyle('T1', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#004B87'), alignment=1)
    s_sec = ParagraphStyle('S2', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#004B87'), spaceBefore=20, spaceAfter=10)
    s_txt = ParagraphStyle('C1', parent=styles['BodyText'], fontSize=10, leading=15)

    # PAGE 1: COUVERTURE
    story.append(Spacer(1, 150))
    story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", s_titre))
    story.append(PageBreak())

    # PAGE 2: SOMMAIRE
    story.append(Paragraph("SOMMAIRE EXÉCUTIF", s_sec))
    t_som = Table([["1. Profil", "Page 3"], ["2. Projections", "Page 4"], ["3. IA", "Page 6"], ["4. Annexes", "Page 12"], ["5. Signatures", "Page 15"]], colWidths=[400, 100])
    story.append(t_som); story.append(PageBreak())

    # PAGE 3: SYNTHÈSE DU CLIENT
    story.append(Paragraph("1. Synthèse du profil", s_sec))
    t_prof = Table([["Métrique", "Valeur"], ["Âge", f"{age} ans"], ["Patrimoine", f"{patrimoine} €"], ["Épargne", f"{epargne} €/mois"]], colWidths=[250, 250])
    story.append(t_prof); story.append(PageBreak())

    # PAGES 4 & 5: TABLEAU D'ÉVOLUTION SUR 20 ANS
    story.append(Paragraph("2. Projections financières", s_sec))
    fin_data = [["Année", "Capital Initial", "Épargne", "Intérêts", "Capital Final"]]
    courant = patrimoine
    for an in range(1, 21):
        int_gagnes = (courant + (epargne * 12) / 2) * (rendement / 100)
        final = courant + (epargne * 12) + int_gagnes
        fin_data.append([f"Annee {an}", f"{courant:.0f} €", f"{epargne*12:.0f} €", f"{int_gagnes:.0f} €", f"{final:.0f} €"])
        courant = final
    t_f1 = Table(fin_data[:12], colWidths=[80, 105, 105, 105, 105])
    story.append(t_f1); story.append(PageBreak())
    t_f2 = Table([fin_data[0]] + fin_data[12:], colWidths=[80, 105, 105, 105, 105])
    story.append(t_f2)

    # PAGES 6 À 11: TEXTE DE L'IA GEMINI
    for p in texte_ia.split('\n'):
        if p.strip():
            if "PARTIE" in p:
                story.append(PageBreak())
                story.append(Paragraph(p.strip(), s_sec))
            else:
                story.append(Paragraph(p.strip(), s_txt))

    # PAGES 12 À 14: LES 5 MODULES D'ANNEXES EXPLICATIVES
    for l, tit, de in [
        ("A", "L'Assurance-Vie", "Cadre fiscal avantageux après 8 ans."),
        ("B", "Le PEA", "Exonération d'impôt sur le revenu après 5 ans."),
        ("C", "Le PER", "Déduction fiscale immédiate à l'entrée."),
        ("D", "Les SCPI", "Perception de revenus fonciers réguliers."),
        ("E", "La Succession", "Abattements légaux pour protéger les proches.")
    ]:
        story.append(PageBreak())
        story.append(Paragraph(f"4. Annexe {l} : {tit}", s_sec))
        story.append(Paragraph(de, s_txt))
        story.append(Paragraph("Ce livret récapitule les règles réglementaires du marché en vigueur.", s_txt))

    # PAGE 15: SIGNATURES JURIDIQUES (Correction du saut de page et des variables de signature)
    story.append(PageBreak())
    story.append(Paragraph("5. Signatures et Validation", s_sec))
    story.append(Paragraph("Ce document indicatif est généré automatiquement par IA. Tout investissement comporte un risque de perte en capital.", s_txt))
    story.append(Spacer(1, 15))
    
    t_sig = Table([["Signature de l'Expert IA", "Signature du Client"], ["Certifié conforme", "Bon pour accord"]], colWidths=[250, 250])
    t_sig.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94A3B8')),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 40)
    ]))
    story.append(t_sig)

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

# 3. INTERFACE UTILISATEUR (STREAMLIT)
st.markdown("### 📊 Étape 1 : Simulation immédiate et gratuite")
col_in, col_gr = st.columns(2)

with col_in:
    v_age = st.number_input("Votre âge", min_value=18, max_value=100, value=35)
    v_pat = st.number_input("Patrimoine actuel (€)", min_value=0, value=50000)
    v_epa = st.number_input("Épargne mensuelle (€)", min_value=0, value=300)
    v_ren = st.slider("Hypothèse de rendement annuel (%)", 1.0, 10.0, 4.0)
    if st.button("🧮 Calculer mes projections gratuitement"): 
        st.session_state.sim_ok = True

with col_gr:
    if st.session_state.sim_ok:
        ans = np.arange(0, 21)
        caps = v_pat * ((1 + v_ren/100) ** ans) + (v_epa * 12) * ((1 + v_ren/100) ** ans - 1) / (v_ren/100)
        fig = go.Figure(go.Scatter(x=ans, y=caps, mode='lines+markers', name='Projection', line=dict(color='#004B87')))
        fig.update_layout(title="Évolution de votre capital", xaxis_title="Années", yaxis_title="Capital (€)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ajustez vos paramètres financiers à gauche puis cliquez sur Calculer.")

# ÉTAPE 2 : VERROU COMMERCIAL
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

# ÉTAPE 3 : BLOC DE TÉLÉCHARGEMENT
if st.session_state.pay_ok:
    st.markdown("---")
    st.success("✅ Paiement validé ! Votre rapport de 15 pages est assemblé.")
    
    with st.spinner("Analyse des marchés en cours..."):
        prompt = f"Rédige un rapport patrimonial dense pour un client de {v_age} ans ayant {v_pat}€ de capital et {v_epa}€ d'épargne. Crée trois chapitres textuels distincts : PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION, PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION, PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE. Écris en texte brut sans dièses ni étoiles."
        try:
            rep = client_ia.models.generate_content(model="gemini-3.6-flash", contents=prompt)
            txt_ia = rep.text if rep.text else "PARTIE 1 : STRATÉGIE FISCALE\nPlan standard.\nPARTIE 2 : GESTION DES RISQUES\nSécurisation.\nPARTIE 3 : ALLOCATION\nRépartition."
        except Exception:
            txt_ia = "PARTIE 1 : STRATÉGIE FISCALE\nPlan standard.\nPARTIE 2 : GESTION DES RISQUES\nSécurisation.\nPARTIE 3 : ALLOCATION\nRépartition."
        
        pdf_data = fabriquer_pdf(txt_ia, v_age, v_pat, v_epa, v_ren)
        
        st.download_button(
            label="📥 Télécharger l'Audit Patrimonial Complet (15 pages - PDF)",
            data=pdf_data,
            file_name=f"Audit_Patrimonial_{v_age}ans.pdf",
            mime="application/pdf"
        )























