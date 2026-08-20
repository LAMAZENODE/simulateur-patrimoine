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
    st.markdown("### 📥 Téléchargez votre document")

    # Fonction pour générer le contenu du rapport avec Gemini
    def generer_analyse_ia(age, patrimoine, epargne, rendement):
        prompt = f"""
        En tant qu'expert en gestion de patrimoine, rédige un rapport d'audit synthétique, sérieux et haut de gamme pour un client.
        Profil du client :
        - Âge : {age} ans
        - Patrimoine actuel : {patrimoine} €
        - Épargne mensuelle : {epargne} €
        - Objectif de rendement annuel : {rendement}%
        
        Rédige trois sections distinctes et professionnelles :
        1. STRATÉGIE FISCALE : Analyse des niches fiscales adaptées (ex: PEA, Assurance-Vie, PER pour la retraite).
        2. GESTION DES RISQUES : Conseils pour sécuriser ce portefeuille sur un horizon de 20 ans.
        3. ALLOCATION RECOMMANDÉE : Suggestions concrètes de répartition des actifs.
        Conserve un ton expert, fluide et rassurant. Ne mets pas de caractères de mise en forme markdown complexes (pas de dièses ou d'étoiles).
        """
        try:
            reponse = client_ia.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return reponse.text
        except Exception as e:
            return f"Analyse standard : Stratégie d'optimisation patrimoniale recommandée pour un capital de {patrimoine} € avec un effort d'épargne continu."

  
        # Fonction pour créer le fichier PDF ReportLab
    def creer_pdf(texte_ia, age, patrimoine, epargne):
        # 🚨 IMPORTS DE SÉCURITÉ LOCAUX POUR ÉVITER LES NAMEERROR
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        story = []
        
        # Styles de texte
        styles = getSampleStyleSheet()
        style_titre = ParagraphStyle('Titre', parent=styles['Heading1'], fontSize=24, leading=28, textColor=colors.HexColor('#004B87'), spaceAfter=20)
        style_sous_titre = ParagraphStyle('SousTitre', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#334155'), spaceAfter=15)
        style_corps = ParagraphStyle('Corps', parent=styles['BodyText'], fontSize=11, leading=16, textColor=colors.HexColor('#1E293B'), spaceAfter=12)
        
        # Structure du document PDF
        story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ — IA EXPERTISE", style_titre))
        story.append(Paragraph(f"<b>Profil analysé :</b> {age} ans | <b>Patrimoine de départ :</b> {patrimoine} € | <b>Épargne :</b> {epargne} € / mois", style_sous_titre))
        story.append(Spacer(1, 15))
        
        # Découpage du texte de l'IA par paragraphes
        paragraphes = texte_ia.split('\n')
        for para in paragraphes:
            if para.strip():
                story.append(Paragraph(para.strip(), style_corps))
        
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()


    # Déclenchement de la génération automatique
    with st.spinner("Génération de votre rapport certifié en cours..."):
        texte_rapport = generer_analyse_ia(age, patrimoine_actuel, epargne_mensuelle, Rendement)
        pdf_data = creer_pdf(texte_rapport, age, patrimoine_actuel, epargne_mensuelle)

    # Bouton de téléchargement réel alimenté par ReportLab
    st.download_button(
        label="⬇️ Télécharger l'Audit Patrimonial Complet (PDF)",
        data=pdf_data,
        file_name=f"Audit_Patrimonial_{age}ans.pdf",
        mime="application/pdf"
    )

  
    
