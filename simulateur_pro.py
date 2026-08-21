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

    # Fonction améliorée pour générer un contenu IA détaillé
    def generer_analyse_ia(client_ia_instance, age, patrimoine, epargne, rendement):
        prompt = f"""
        En tant qu'expert en gestion de patrimoine, rédige un rapport d'audit détaillé, sérieux et haut de gamme de 15 pages.
        Profil du client :
        - Âge : {age} ans
        - Patrimoine actuel : {patrimoine} €
        - Épargne mensuelle : {epargne} €
        - Objectif de rendement annuel : {rendement}%
        
        Rédige obligatoirement les 9 parties distinctes suivantes avec des paragraphes denses et détaillés :

        PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION
        Développe des conseils sur le PEA, l'Assurance-Vie et le PER adaptés à un profil de {age} ans. Explique comment optimiser la fiscalité sur 20 ans. Détaille les plafonds de versement, les avantages fiscaux, les stratégies de retrait.

        PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION
        Explique comment répartir le capital entre fonds sécurisés (Euro) et actifs de croissance (Actions/ETF) pour traverser les cycles économiques. Analyse les différents profils de risque et les stratégies de diversification.

        PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE
        Donne une proposition concrète de répartition en pourcentages (ex: 40% Immobilier, 40% Actions, 20% Monétaire) avec justifications détaillées pour chaque classe d'actifs.

        PARTIE 4 : STRATÉGIE D'INVESTISSEMENT IMMOBILIER
        Analyse les opportunités d'investissement immobilier, les différents types de biens, les avantages fiscaux (Pinel, Denormandie), et les stratégies de financement.

        PARTIE 5 : PLANIFICATION DE LA RETRAITE
        Projette l'évolution du capital sur 20 ans, estime le revenu complémentaire généré, et propose des stratégies pour optimiser la transition vers la retraite.

        PARTIE 6 : OPTIMISATION DE LA TRANSMISSION PATRIMONIALE
        Développe les stratégies de donation, les avantages du Pacte Dutreil, l'optimisation successorale et les mécanismes de réduction des droits de succession.

        PARTIE 7 : ANALYSE MACRO-ÉCONOMIQUE ET TENDANCES
        Analyse les tendances économiques actuelles, l'inflation, les taux d'intérêt, et leur impact potentiel sur le patrimoine du client.

        PARTIE 8 : STRATÉGIE D'ÉPARGNE DE PRÉCAUTION
        Explique l'importance de l'épargne de précaution, les livrets réglementés, et propose une stratégie de constitution d'un matelas de sécurité.

        PARTIE 9 : CONCLUSION ET PLAN D'ACTION
        Synthèse des recommandations principales et proposition d'un plan d'action concret sur 5 ans avec des objectifs chiffrés.

        Important : Rédige des paragraphes complets et très denses. N'utilise aucun caractère markdown. Utilise uniquement du texte brut.
        """
        try:
            if client_ia_instance is None:
                from google import genai
                CLE_API = st.secrets["GEMINI_API_KEY"]
                client_ia_instance = genai.Client(api_key=CLE_API)
                
            reponse = client_ia_instance.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
            )
            if reponse.text:
                return reponse.text
            else:
                return "Erreur : Le contenu retourné par l'IA est vide."
        except Exception as e:
            return f"Erreur technique de l'API Gemini : {str(e)}"

    # Fonction de création du PDF enrichie pour atteindre 15 pages
    def creer_pdf(texte_ia, age, patrimoine, epargne, rendement):
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        import random
        from datetime import datetime
        
        pdf_buffer = BytesIO()
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
        style_highlight = ParagraphStyle('Highlight', parent=styles['Normal'], fontSize=11, leading=18, textColor=colors.HexColor('#004B87'), spaceAfter=12, leftIndent=20, rightIndent=20, alignment=1)

        # ==========================================
        # PAGE 1 : PAGE DE GARDE PROFESSIONNELLE
        # ==========================================
        story.append(Spacer(1, 100))
        story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", style_titre_grand))
        story.append(Paragraph("PROJECTION FINANCIÈRE À 20 ANS & OPTIMISATION FISCALE", style_sous_titre_grand))
        story.append(Paragraph("Document confidentiel édité par Cabinet Digital IA<br/>Analyses basées sur des algorithmes prédictifs avancés", style_mention_garde))
        story.append(Spacer(1, 50))
        story.append(Paragraph(f"Rapport généré le : {datetime.now().strftime('%d/%m/%Y')}", style_mention_garde))
        story.append(PageBreak())

        # ==========================================
        # PAGE 2 : SOMMAIRE
        # ==========================================
        story.append(Paragraph("SOMMAIRE", style_section))
        story.append(Spacer(1, 10))
        sommaire = [
            "1. Synthèse du Profil de l'Investisseur",
            "2. Stratégie Fiscale d'Optimisation",
            "3. Gestion des Risques et Sécurisation",
            "4. Allocation de Capital Recommandée",
            "5. Stratégie d'Investissement Immobilier",
            "6. Planification de la Retraite",
            "7. Optimisation de la Transmission Patrimoniale",
            "8. Analyse Macro-Économique et Tendances",
            "9. Stratégie d'Épargne de Précaution",
            "10. Conclusion et Plan d'Action",
            "11. Annexes"
        ]
        for item in sommaire:
            story.append(Paragraph(item, style_corps))
            story.append(Spacer(1, 8))
        story.append(PageBreak())

        # ==========================================
        # PAGE 3 : SYNTHÈSE DU PROFIL & TABLEAU
        # ==========================================
        story.append(Paragraph("1. Synthèse du profil de l'investisseur", style_section))
        story.append(Paragraph("Le présent rapport approfondi est établi sur la base des informations financières déclarées par l'utilisateur. Les calculs et projections visent à maximiser l'efficience du capital sur un horizon de deux décennies.", style_corps))
        story.append(Spacer(1, 15))
        
        # Tableau récapitulatif
        donnees_table = [
            [Paragraph("<b>Métrique Patrimoniale</b>", style_corps), Paragraph("<b>Valeur renseignée</b>", style_corps)],
            ["Âge de l'investisseur", f"{age} ans"],
            ["Patrimoine initial", f"{patrimoine:,.0f} €"],
            ["Effort d'épargne mensuel", f"{epargne} € / mois"],
            ["Objectif de rendement ciblé", f"{rendement} % par an"],
            ["Horizon d'investissement", "20 ans"],
            ["Profil de risque estimé", "Équilibré"]
        ]
        t = Table(donnees_table, colWidths=[250, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (1,0), colors.HexColor('#F1F5F9')),
            ('TEXTCOLOR', (0,0), (1,0), colors.HexColor('#004B87')),
            ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ]))
        story.append(t)
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("Projection du capital estimé à 20 ans :", style_corps))
        projection = patrimoine * ((1 + rendement/100) ** 20) + (epargne * 12) * ((1 + rendement/100) ** 20 - 1) / (rendement/100)
        style_projection = ParagraphStyle('Projection', parent=styles['Normal'], fontSize=18, leading=22, textColor=colors.HexColor('#004B87'), alignment=1)
        story.append(Paragraph(f"<b>{projection:,.0f} €</b>", style_projection))
        story.append(PageBreak())

        # ==========================================
        # PAGES 4 À 12 : INJECTION DU TEXTE DE L'IA
        # ==========================================
        paragraphes = texte_ia.split('\n')
        partie_count = 0
        for para in paragraphes:
            txt = para.strip()
            if not txt:
                continue
            
            # Gestion des sauts de page intelligents basés sur le texte de l'IA
            if "PARTIE" in txt and ("STRATÉGIE" in txt or "GESTION" in txt or "ALLOCATION" in txt or "IMMOBILIER" in txt or "RETRAITE" in txt or "TRANSMISSION" in txt or "MACRO" in txt or "PRÉCAUTION" in txt or "CONCLUSION" in txt):
                partie_count += 1
                if partie_count > 1:
                    story.append(PageBreak())
                story.append(Paragraph(txt, style_section))
            else:
                story.append(Paragraph(txt, style_corps))

        # ==========================================
        # PAGES 13-14 : ANNEXES DÉTAILLÉES
        # ==========================================
        story.append(PageBreak())
        story.append(Paragraph("ANNEXE A : Le Fonctionnement de l'Assurance-Vie", style_section))
        
        annexe_a_text = """
        L'Assurance-Vie est une enveloppe fiscale unique en France. Elle permet de capitaliser des intérêts en report d'imposition. 
        Après 8 ans, les retraits bénéficient d'un abattement annuel de 4 600 € pour une personne seule (9 200 € pour un couple). 
        C'est l'outil idéal pour loger des fonds en euros sécurisés et des unités de compte diversifiées.
        
        En cas de transmission, les sommes versées avant l'âge de 70 ans bénéficient d'une exonération de droits de succession 
        jusqu'à 152 500 € par bénéficiaire désigné, ce qui en fait un outil de transmission hors du commun.
        
        Avantages fiscaux détaillés :
        - Exonération d'impôt sur le revenu pour les intérêts capitalisés
        - Abattement de 4 600 €/an après 8 ans
        - Transmission avantageuse avec exonération jusqu'à 152 500 €
        - Possibilité de versements programmés pour lisser l'investissement
        """
        story.append(Paragraph(annexe_a_text, style_corps))
        
        story.append(PageBreak())
        story.append(Paragraph("ANNEXE B : Le Fonctionnement du PEA (Plan d'Épargne en Actions)", style_section))
        
        annexe_b_text = """
        Le PEA est destiné à l'investissement sur les marchés actions européennes. Sa limite de versement est fixée à 150 000 €. 
        Après 5 ans de détention, les gains et dividendes sont totalement exonérés d'impôt sur le revenu. 
        Seuls les prélèvements sociaux (17,2%) s'appliquent lors des retraits.
        
        Caractéristiques principales :
        - Plafond de versement : 150 000 €
        - Délai de détention minimum : 5 ans
        - Exonération d'impôt sur le revenu après 5 ans
        - Possibilité d'investir dans des ETF européens
        - Gestion pilotée ou libre
        
        Stratégies recommandées :
        - DCA (Dollar Cost Averaging) pour lisser les entrées
        - Répartition sectorielle équilibrée
        - Réinvestissement systématique des dividendes
        """
        story.append(Paragraph(annexe_b_text, style_corps))
        
        story.append(PageBreak())
        story.append(Paragraph("ANNEXE C : Le Fonctionnement du PER (Plan d'Épargne Retraite)", style_section))
        
        annexe_c_text = """
        Le PER est l'enveloppe dédiée à la préparation de la retraite. Il offre une déduction fiscale immédiate et un complément 
        de revenu à la retraite. Les versements sont déductibles du revenu imposable dans la limite du plafond annuel.
        
        Avantages fiscaux :
        - Déduction immédiate des versements du revenu imposable
        - Fiscalité allégée à la sortie (option rente ou capital)
        - Transmissibilité en cas de décès
        
        Stratégies recommandées :
        - Arbitrage progressif vers les fonds sécurisés à l'approche de la retraite
        - Optimisation du plafond de déduction annuel
        - Planification du mode de sortie (rente ou capital)
        """
        story.append(Paragraph(annexe_c_text, style_corps))

        # ==========================================
        # PAGE 15 : MENTIONS LÉGALES ET CONCLUSION
        # ==========================================
        story.append(PageBreak())
        story.append(Paragraph("CONCLUSION GÉNÉRALE ET PLAN D'ACTION", style_section))
        conclusion_text = """
        Ce rapport d'audit patrimonial a pour objectif de vous fournir une vision claire et structurée de votre situation financière 
        actuelle et des perspectives d'évolution sur 20 ans. Les recommandations formulées s'appuient sur une analyse approfondie 
        de votre profil et des meilleures pratiques en matière de gestion de patrimoine.
        
        Plan d'action recommandé :
        1. Ouvrir un PEA pour bénéficier de l'exonération fiscale à long terme
        2. Souscrire une Assurance-Vie pour la diversification et la transmission
        3. Construire une épargne de précaution de 3 à 6 mois de salaire
        4. Étudier les opportunités d'investissement immobilier adaptées
        5. Mettre en place une stratégie de donation progressive
        6. Réévaluer annuellement sa stratégie avec un conseiller
        """
        story.append(Paragraph(conclusion_text, style_corps))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("MENTIONS LÉGALES", style_section))
        legal_text = """
        Ce document est généré de manière automatisée par une intelligence artificielle à des fins purement informatives et pédagogiques. 
        Il ne constitue en aucun cas un conseil en investissement personnalisé, une incitation à acheter ou à vendre des instruments financiers.
        
        Les performances passées ne préjugent pas des performances futures. Tout investissement comporte des risques de perte en capital. 
        Le Cabinet Digital vous invite à consulter un Conseiller en Investissements Financiers (CIF) habilité avant toute prise de décision financière.
        
        Données personnelles : Conformément au RGPD, vos données sont traitées de manière confidentielle et ne sont pas conservées.
        
        © 2026 Cabinet Digital IA - Tous droits réservés
        """
        story.append(Paragraph(legal_text, style_corps))

        # Génération finale du document
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    # Récupération sécurisée ou secours de la variable globale client_ia
    instance_ia = client_ia if 'client_ia' in globals() else None

    # Exécution du processus
    with st.spinner("Analyse des marchés et génération de votre rapport complet sur 15 pages..."):
        texte_rapport = generer_analyse_ia(instance_ia, age, patrimoine_actuel, epargne_mensuelle, Rendement)
        pdf_data = creer_pdf(texte_rapport, age, patrimoine_actuel, epargne_mensuelle, Rendement)

    # Bouton de téléchargement
    st.download_button(
        label="⬇️ Télécharger l'Audit Patrimonial Complet (15 pages)",
        data=pdf_data,
        file_name=f"Audit_Patrimonial_{age}ans.pdf",
        mime="application/pdf"
    )
    
    st.info("""
    📄 Votre rapport de 15 pages contient :
    - Page 1 : Page de garde professionnelle
    - Page 2 : Sommaire détaillé
    - Page 3 : Synthèse de votre profil avec projections
    - Pages 4-12 : 9 parties d'analyse personnalisée par IA
    - Pages 13-14 : Annexes détaillées sur les enveloppes fiscales
    - Page 15 : Conclusion, plan d'action et mentions légales
    """)













    

























