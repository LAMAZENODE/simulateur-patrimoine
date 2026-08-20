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

   
           # Fonction modifiée avec paramètres de configuration avancés
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
        
        Important : Rédige des paragraphes complets, riches et denses. N'utilise aucun caractère markdown (pas de *, pas de #, pas de -). Utilisez uniquement du texte brut.
        """
        try:
            if client_ia_instance is None:
                from google import genai
                CLE_API = st.secrets["GEMINI_API_KEY"]
                client_ia_instance = genai.Client(api_key=CLE_API)
                
            # 🚀 AJOUT DE LA CONFIGURATION POUR AUGMENTER LA TAILLE DU TEXTE
            reponse = client_ia_instance.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config={
                    "max_output_tokens": 4096,  # Force l'IA à écrire un long texte sans couper
                    "temperature": 0.3          # Rend l'IA plus stable et professionnelle sur les chiffres
                }
            )
            if reponse.text:
                return reponse.text
            else:
                return "Erreur : Le contenu retourné par l'IA est vide."
        except Exception as e:
            return f"Erreur technique de l'API Gemini : {str(e)}"



      # Fonction de création du PDF enrichie pour atteindre un gros volume de pages
    def creer_pdf(texte_ia, age, patrimoine, epargne, rendement):
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        pdf_buffer = BytesIO()
        # Marges standardisées
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        # Styles de texte professionnels
        styles = getSampleStyleSheet()
        style_titre_grand = ParagraphStyle('TitreGrand', parent=styles['Heading1'], fontSize=28, leading=34, textColor=colors.HexColor('#004B87'), alignment=1, spaceAfter=20)
        style_sous_titre_grand = ParagraphStyle('SubGrand', parent=styles['Heading2'], fontSize=16, leading=22, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=200)
        style_mention_garde = ParagraphStyle('MentionGarde', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#94A3B8'), alignment=1)
        
        style_section = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, leading=20, textColor=colors.HexColor('#004B87'), spaceBefore=20, spaceAfter=15, keepWithNext=True)
        style_corps = ParagraphStyle('Corps', parent=styles['BodyText'], fontSize=10.5, leading=17, textColor=colors.HexColor('#1E293B'), spaceAfter=12)
        style_annexe_titre = ParagraphStyle('AnnexeTitre', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#1E293B'), spaceBefore=15, spaceAfter=10)

        # ==========================================
        # PAGE 1 : PAGE DE GARDE PROFESSIONNELLE
        # ==========================================
        story.append(Spacer(1, 100))
        story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", style_titre_grand))
        story.append(Paragraph("PROJECTION FINANCIÈRE À 20 ANS & OPTIMISATION FISCALE", style_sous_titre_grand))
        story.append(Paragraph("Document confidentiel édité par Cabinet Digital IA<br/>Analyses basées sur des algorithmes prédictifs avancés", style_mention_garde))
        story.append(PageBreak()) # Saut à la page suivante

        # ==========================================
        # PAGE 2 : SYNTHÈSE DU PROFIL & TABLEAU
        # ==========================================
        story.append(Paragraph("1. Synthèse du profil de l'investisseur", style_section))
        story.append(Paragraph("Le présent rapport approfondi est établi sur la base des informations financières déclarées par l'utilisateur. Les calculs et projections visent à maximiser l'efficience du capital sur un horizon de deux décennies.", style_corps))
        story.append(Spacer(1, 15))
        
        # Tableau récapitulatif
        donnees_table = [
            [Paragraph("<b>Métrique Patrimoniale</b>", style_corps), Paragraph("<b>Valeur renseignée</b>", style_corps)],
            ["Âge de l'investisseur", f"{age} ans"],
            ["Patrimoine initial", f"{patrimoine:,.0f} €".replace(',', ' ')],
            ["Effort d'épargne mensuel", f"{epargne} € / mois"],
            ["Objectif de rendement ciblé", f"{rendement} % par an"]
        ]
        t = Table(donnees_table, colWidths=[250, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0,0), (1,0), colors.HexColor('#004B87')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        story.append(t)
        story.append(PageBreak())

        # ==========================================
        # PAGES 3 À X : INJECTION DU TEXTE DE L'IA
        # ==========================================
        paragraphes = texte_ia.split('\n')
        for para in paragraphes:
            txt = para.strip()
            if not txt:
                continue
            
            # Gestion des sauts de page intelligents basés sur le texte de l'IA
            if "PARTIE" in txt or "STRATÉGIE" in txt or "GESTION" in txt or "ALLOCATION" in txt:
                story.append(PageBreak()) # On force une nouvelle page pour chaque grande partie
                story.append(Paragraph(txt, style_section))
            else:
                story.append(Paragraph(txt, style_corps))

        # ==========================================
        # PAGES ANNEXES : EXPLICATIONS DES ENVELOPPES (Fixes)
        # ==========================================
        story.append(PageBreak())
        story.append(Paragraph("ANNEXE A : Le Fonctionnement de l'Assurance-Vie", style_section))
        story.append(Paragraph("L'Assurance-Vie est une enveloppe fiscale unique en France. Elle permet de capitaliser des intérêts en report d'imposition. Après 8 ans, les retraits bénéficient d'un abattement annuel de 4 600 € pour une personne seule. C'est l'outil idéal pour loger des fonds en euros sécurisés et des unités de compte diversifiées.", style_corps))
        story.append(Paragraph("En cas de transmission, les sommes versées avant l'âge de 70 ans bénéficient d'une exonération de droits de succession jusqu'à 152 500 € par bénéficiaire désigné, ce qui en fait un outil de transmission hors du commun.", style_corps))

        story.append(PageBreak())
        story.append(Paragraph("ANNEXE B : Le Fonctionnement du PEA (Plan d'Épargne en Actions)", style_section))
        story.append(Paragraph("Le PEA est destiné à l'investissement sur les marchés actions européens. Sa limite de versement est fixée à 150 000 €. Après 5 ans de détention, les gains et dividendes sont totalement exonérés d'impôt sur le revenu. Seuls les prélèvements sociaux (17,2%) s'appliquent lors des retraits.", style_corps))

        story.append(PageBreak())
        story.append(Paragraph("ANNEXE C : Clauses de non-responsabilité et Mentions Légales", style_section))
        story.append(Paragraph("Ce document est généré de manière automatisée par une intelligence artificielle à des fins purement informatives et pédagogiques. Il ne constitue en aucun cas un conseil en investissement personnalisé, une incitation à acheter ou à vendre des instruments financiers.", style_corps))
        story.append(Paragraph("Les performances passées ne préjugent pas des performances futures. Tout investissement comporte des risques de perte en capital. Le Cabinet Digital vous invite à consulter un Conseiller en Investissements Financiers (CIF) habilité avant toute prise de décision financière.", style_corps))

        # Génération finale du document
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

   
