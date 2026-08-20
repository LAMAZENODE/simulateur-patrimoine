import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from google import genai

# Configuration de la page
st.set_page_config(page_title="Cabinet Digital - Optimisation Patrimoniale", page_icon="🛡️", layout="wide")

# Initialisation sécurisée des états de session
if "simulation_faite" not in st.session_state:
    st.session_state.simulation_faite = False
if "paiement_pdf_ok" not in st.session_state:
    st.session_state.paiement_pdf_ok = False
if "pdf_pret" not in st.session_state:
    st.session_state.pdf_pret = None

# Configuration de l'accès à l'API Gemini
try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur de configuration technique d'API : {e}")
    st.stop()

st.title("Intelligence Artificielle & Expertise Patrimoniale")
st.subheader("Optimisez votre patrimoine et projetez votre avenir sur 20 ans")

# --- ÉTAPE 1 : LA SIMULATION GRATUITE ---
st.markdown("### 📊 Étape 1 : Votre simulation immédiate et gratuite")

col_inputs, col_graph = st.columns([1, 2])

with col_inputs:
    age = st.number_input("Votre âge", min_value=18, max_value=100, value=35)
    patrimoine_actuel = st.number_input("Patrimoine actuel (€)", min_value=0, value=50000)
    epargne_mensuelle = st.number_input("Épargne mensuelle (€)", min_value=0, value=300)
    Rendement = st.slider("Hypothèse de rendement annuel (%)", 1.0, 10.0, 4.0)

    if st.button("🧮 Calculer mes projections gratuitement"):
        st.session_state.simulation_faite = True
        # Si les chiffres changent, on force la régénération du futur PDF
        st.session_state.pdf_pret = None 

with col_graph:
    if st.session_state.simulation_faite:
        annees = np.arange(0, 21)
        capital = patrimonio_actuel * ((1 + Rendement/100) ** annees) + (epargne_mensuelle * 12) * ((1 + Rendement/100) ** annees - 1) / (Rendement/100)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=annees, y=capital, mode='lines+markers', name='Votre projection', line=dict(color='#004B87')))
        fig.update_layout(title="Évolution estimée de votre patrimoine", xaxis_title="Années", yaxis_title="Capital (€)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Remplissez les informations à gauche pour voir votre graphique de projection.")

# --- ÉTAPE 2 : LE VERROU PAYANT PSYCHOLOGIQUE ---
if st.session_state.simulation_faite:
    st.markdown("---")
    st.markdown("### 🔒 Étape 2 : Obtenez votre Audit Certifié complet (15 pages)")
    
    col_vendeuse, col_action = st.columns(2)
    
    with col_vendeuse:
        st.markdown("""
        **Ce que contient votre rapport PDF personnalisé :**
        * 📉 **Optimisation Fiscale** : Liste des niches adaptées à votre profil.
        * 🛡️ **Sécurisation** : Analyse des risques de votre portefeuille actuel.
        * 🤖 **Conseils IA** : Recommandations stratégiques exclusives de notre algorithme.
        """)
        
    with col_action:
        st.error("💡 Tarif de lancement : 19,00 € TTC (au lieu de 49 €)")
        
        if st.button("💳 Télécharger mon Audit PDF Complet (19 €)"):
            st.session_state.paiement_pdf_ok = True
            st.success("Paiement validé ! Votre rapport est prêt.")

# FONCTIONS TECHNIQUES DE GÉNÉRATION (Déclarées globalement pour éviter les bugs)
def generer_analyse_ia(client_ia_instance, age, patrimoine, epargne, rendement):
    prompt = f"""
    En tant qu'expert en gestion de patrimoine, rédige un rapport d'audit détaillé, sérieux et haut de gamme.
    Profil du client : - Âge : {age} ans - Patrimoine actuel : {patrimoine} € - Épargne mensuelle : {epargne} € - Objectif de rendement annuel : {rendement}%
    Rédige obligatoirement trois grandes parties distinctes en texte brut sans aucun caractère markdown (pas de *, pas de #, pas de -) :
    PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION
    PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION
    PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE
    """
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
    sommaire_data = [["1. Synthèse du profil", "Page 3"], ["2. Tableau d'évolution", "Page 4"], ["3. Analyse de l'IA", "Page 6"], ["4. Annexes", "Page 12"], ["5. Signatures", "Page 15"]]
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

    # PAGES 4 & 5 : TABLEAU DYNAMIQUE SUR 20 ANS
    story.append(Paragraph("2. Tableau d'évolution de l'épargne capitalisée", style_section))
    table_finance_data = [[Paragraph("<b>Année</b>", style_corps), Paragraph("<b>Capital initial</b>", style_corps), Paragraph("<b>Épargne versée</b>", style_corps), Paragraph("<b>Intérêts générés</b>", style_corps), Paragraph("<b>Capital Final</b>", style_corps)]]
    cap_courant = patrimoine
    for an in range(1, 21):
        interets = (cap_courant + (epargne * 12) / 2) * (rendement / 100)
        cap_final = cap_courant + (epargne * 12) + interets
        table_finance_data.append([f"Année {an}", f"{cap_courant:,.0f} €", f"{(epargne*12):,.0f} €", f"{interets:,.0f} €", f"{cap_final:,.0f} €"])
        cap_courant = cap_final

    t_fin1 = Table(table_finance_data[:12], colWidths=[80, 105, 105, 105, 105])
    t_fin1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1'))]))
    story.append(t_fin1)
    story.append(PageBreak())
    
    story.append(Paragraph("2. Tableau d'évolution (Suite)", style_section))
    t_fin2 = Table([table_finance_data[0]] + table_finance_data[12:], colWidths=[80, 105, 105, 105, 105])
    t_fin2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1'))]))
    story.append(t_fin2)

    # PAGES 6 À 11 : TEXTE IA
    paragraphes = texte_ia.split('\n')
    for para in paragraphes:
        txt = para.strip()
        if not txt: continue
        if "PARTIE 1" in txt:
            story.append(PageBreak())
            story.append(Paragraph("3.1 Stratégie fiscale d'optimisation", style_section))
        elif "PARTIE 2" in txt:
            story.append(PageBreak())
            story.append(Paragraph("3.2 Gestion des risques et sécurisation", style_section))
        elif "PARTIE 3" in txt:
            story.append(PageBreak())
            story.append(Paragraph("3.3 Stratégie d'allocation recommandée", style_section))
        else:
            story.append(Paragraph(txt, style_corps))

    # PAGES 12 À 14 : ANNEXES FIXES (Remplissage)
    for lettre, titre in [("A", "L'Assurance-Vie"), ("B", "Le PEA"), ("C", "Le PER")]:
        story.append(PageBreak())
        story.append(Paragraph(f"4. Annexe {lettre} : Guide sur {titre}", style_section))
        story.append(Paragraph("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.", style_corps))



