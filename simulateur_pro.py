import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO


# Initialisation des états
if "simulation_faite" not in st.session_state:
    st.session_state.simulation_faite = False
if "paiement_pdf_ok" not in st.session_state:
    st.session_state.paiement_pdf_ok = False

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

with col_graph:
    if st.session_state.simulation_faite:
        # Calcul rapide pour le graphique teaser
        annees = np.arange(0, 21)
        capital = patrimoine_actuel * ((1 + Rendement/100) ** annees) + (epargne_mensuelle * 12) * ((1 + Rendement/100) ** annees - 1) / (Rendement/100)
        
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
        
        # Simulation du bouton Stripe à petit prix
        if st.button("💳 Télécharger mon Audit PDF Complet (19 €)"):
            st.session_state.paiement_pdf_ok = True
            st.success("Paiement validé ! Votre rapport est prêt.")
     # --- ÉTAPE 3 : ACCÈS AU PDF APRÈS PAIEMENT ---
if st.session_state.paiement_pdf_ok:
    st.markdown("### 📥 Téléchargez votre document")

   
        # Fonction modifiée avec le modèle Gemini à jour
    def generer_analyse_ia(client_ia_instance, age, patrimoine, epargne, rendement):
        prompt = f"""
        En tant qu'expert en gestion de patrimoine, rédige un rapport d'audit détaillé, sérieux et haut de gamme.
        Profil du client :
        - Âge : {age} ans
        - Patrimoine actuel : {patrimoine} €
        - Épargne mensuelle : {epargne} €
        - Objectif de rendement annuel : {rendement}%
        
        Rédige obligatoirement trois grandes parties distinctes :
        
        PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION
        Développe des conseils sur le PEA, l'Assurance-Vie et le PER adaptés à un profil de {age} ans. Explique comment optimiser la fiscalité sur 20 ans.
        
        PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION
        Explique comment répartir le capital entre fonds sécurisés (Euro) et actifs de croissance (Actions/ETF) pour traverser les cycles économiques.
        
        PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE
        Donne une proposition concrète de répartition en pourcentages (ex: 40% Immobilier, 40% Actions, 20% Monétaire).
        
        Important : Rédige des paragraphes complets et denses. N'utilise aucun caractère markdown (pas de *, pas de #, pas de -). Utilisez uniquement du texte brut.
        """
        try:
            if client_ia_instance is None:
                from google import genai
                CLE_API = st.secrets["GEMINI_API_KEY"]
                client_ia_instance = genai.Client(api_key=CLE_API)
                
            # 🚀 CORRECTION : Utilisation de gemini-3.6-flash
            reponse = client_ia_instance.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            if reponse.text:
                return reponse.text
            else:
                return "Erreur : Le contenu retourné par l'IA est vide."
        except Exception as e:
            return f"Erreur technique de l'API Gemini : {str(e)}"


    # Fonction de création du PDF ReportLab
    def creer_pdf(texte_ia, age, patrimoine, epargne, rendement):
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        # Styles de texte
        styles = getSampleStyleSheet()
        style_titre = ParagraphStyle('Titre', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor('#004B87'), spaceAfter=5)
        style_sous_titre = ParagraphStyle('SousTitre', parent=styles['Heading2'], fontSize=12, leading=16, textColor=colors.HexColor('#475569'), spaceAfter=20)
        style_section = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#004B87'), spaceBefore=15, spaceAfter=10, keepWithNext=True)
        style_corps = ParagraphStyle('Corps', parent=styles['BodyText'], fontSize=10.5, leading=16, textColor=colors.HexColor('#1E293B'), spaceAfter=12)
        
        # En-tête du document
        story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", style_titre))
        story.append(Paragraph("Document d'orientation stratégique édité par Intelligence Artificielle", style_sous_titre))
        story.append(Spacer(1, 10))
        
        # Tableau récapitulatif (Correction des largeurs de colonnes fixées à 250 et 250)
        donnees_table = [
            [Paragraph("<b>Métrique Patrimoniale</b>", style_corps), Paragraph("<b>Valeur renseignée</b>", style_corps)],
            ["Âge de l'investisseur", f"{age} ans"],
            ["Patrimoine initial", f"{patrimoine:,.0f} €".replace(',', ' ')],
            ["Effort d'épargne mensuel", f"{epargne} € / mois"],
            ["Objectif de rendement ciblé", f"{rendement} % par an"]
        ]
        t = Table(donnees_table, colWidths=[250, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0,0), (1,0), colors.HexColor('#004B87')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))
        
        # Injection du texte de l'IA
        paragraphes = texte_ia.split('\n')
        for para in paragraphes:
            txt = para.strip()
            if not txt:
                continue
            
            if "PARTIE" in txt or "STRATÉGIE" in txt or "GESTION" in txt or "ALLOCATION" in txt:
                story.append(Paragraph(txt, style_section))
            else:
                story.append(Paragraph(txt, style_corps))
        
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    # Récupération sécurisée ou secours de la variable globale client_ia
    instance_ia = client_ia if 'client_ia' in globals() else None

    # Exécution du processus
    with st.spinner("Analyse des marchés et génération de votre rapport complet..."):
        texte_rapport = generer_analyse_ia(instance_ia, age, patrimoine_actuel, epargne_mensuelle, Rendement)
        pdf_data = creer_pdf(texte_rapport, age, patrimoine_actuel, epargne_mensuelle, Rendement)

    # Bouton de téléchargement
    st.download_button(
        label="⬇️ Télécharger l'Audit Patrimonial Complet (PDF)",
        data=pdf_data,
        file_name=f"Audit_Patrimonial_{age}ans.pdf",
        mime="application/pdf"
    )

   
