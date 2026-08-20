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

   
           def creer_pdf(texte_ia, age, patrimoine, epargne, rendement):
        from io import BytesIO
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        # Styles de texte professionnels
        styles = getSampleStyleSheet()
        style_titre_grand = ParagraphStyle('TitreGrand', parent=styles['Heading1'], fontSize=28, leading=34, textColor=colors.HexColor('#004B87'), alignment=1, spaceAfter=20)
        style_sous_titre_grand = ParagraphStyle('SubGrand', parent=styles['Heading2'], fontSize=15, leading=22, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=180)
        style_mention_garde = ParagraphStyle('MentionGarde', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#94A3B8'), alignment=1)
        
        style_section = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, leading=20, textColor=colors.HexColor('#004B87'), spaceBefore=25, spaceAfter=15, keepWithNext=True)
        style_sous_section = ParagraphStyle('SousSection', parent=styles['Heading3'], fontSize=12, leading=16, textColor=colors.HexColor('#334155'), spaceBefore=12, spaceAfter=6, keepWithNext=True)
        style_corps = ParagraphStyle('Corps', parent=styles['BodyText'], fontSize=10.5, leading=17, textColor=colors.HexColor('#1E293B'), spaceAfter=12)

        # ==========================================
        # PAGE 1 : PAGE DE GARDE
        # ==========================================
        story.append(Spacer(1, 100))
        story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", style_titre_grand))
        story.append(Paragraph("PROJECTION FINANCIÈRE À 20 ANS & OPTIMISATION FISCALE", style_sous_titre_grand))
        story.append(Paragraph("Document confidentiel édité par Cabinet Digital IA<br/>Analyses basées sur des algorithmes prédictifs avancés", style_mention_garde))
        story.append(PageBreak())

        # ==========================================
        # PAGE 2 : SOMMAIRE DU RAPPORT
        # ==========================================
        story.append(Paragraph("SOMMAIRE EXÉCUTIF", style_section))
        story.append(Spacer(1, 20))
        sommaire_data = [
            ["1. Synthèse du profil de l'investisseur et objectifs", "Page 3"],
            ["2. Tableau d'évolution de l'épargne capitalisée (Années 1 à 20)", "Page 4"],
            ["3. Analyse stratégique et fiscale par Intelligence Artificielle", "Page 6"],
            ["   3.1 Stratégie fiscale d'optimisation", "Page 6"],
            ["   3.2 Gestion des risques et sécurisation du capital", "Page 8"],
            ["   3.3 Allocation cible recommandée (Capital et Épargne)", "Page 10"],
            ["4. Annexes techniques et fiches réglementaires", "Page 12"],
            ["   Annexe A : Le guide de l'Assurance-Vie et de la transmission", "Page 12"],
            ["   Annexe B : Le fonctionnement du PEA et des ETF", "Page 13"],
            ["   Annexe C : Le Plan d'Épargne Retraite (PER) et levier TMI", "Page 14"],
            ["5. Mentions légales, décharges et signatures", "Page 15"],
        ]
        st_table = Table(sommaire_data, colWidths=[400, 100])
        st_table.setStyle(TableStyle([
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ]))
        story.append(st_table)
        story.append(PageBreak())

        # ==========================================
        # PAGE 3 : SYNTHÈSE DU PROFIL
        # ==========================================
        story.append(Paragraph("1. Synthèse du profil de l'investisseur", style_section))
        story.append(Paragraph("Ce document à haute valeur ajoutée dresse un panorama complet de vos leviers financiers. Les préconisations cherchent à maximiser l'efficience fiscale de vos placements tout en respectant votre tolérance aux fluctuations des marchés de capitaux.", style_corps))
        story.append(Spacer(1, 15))
        
        donnees_table = [
            [Paragraph("<b>Métrique Patrimoniale</b>", style_corps), Paragraph("<b>Valeur renseignée</b>", style_corps)],
            ["Âge au moment de l'audit", f"{age} ans"],
            ["Patrimoine financier initial", f"{patrimoine:,.0f} €".replace(',', ' ')],
            ["Effort d'épargne récurrent", f"{epargne} € / mois"],
            ["Objectif de rendement net ciblé", f"{rendement} % par an"]
        ]
        t = Table(donnees_table, colWidths=[250, 250])
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
        # PAGES 4 & 5 : TABLEAU ÉVOLUTION FINANCIÈRE SUR 20 ANS
        # ==========================================
        story.append(Paragraph("2. Tableau d'évolution de l'épargne capitalisée", style_section))
        story.append(Paragraph("Ce tableau simule la croissance de votre capital année après année sur deux décennies, en cumulant les intérêts de votre patrimoine de départ et vos injections d'épargne mensuelle.", style_corps))
        story.append(Spacer(1, 10))

        table_finance_data = [[Paragraph("<b>Année</b>", style_corps), Paragraph("<b>Capital initial</b>", style_corps), Paragraph("<b>Épargne versée</b>", style_corps), Paragraph("<b>Intérêts générés</b>", style_corps), Paragraph("<b>Capital Final</b>", style_corps)]]
        
        cap_courant = patrimoine
        r_taux = rendement / 100
        total_epargne_annee = epargne * 12

        for an in range(1, 21):
            interets = (cap_courant + total_epargne_annee / 2) * r_taux
            cap_final = cap_courant + total_epargne_annee + interets
            
            table_finance_data.append([
                f"Année {an}",
                f"{cap_courant:,.0f} €".replace(',', ' '),
                f"{total_epargne_annee:,.0f} €".replace(',', ' '),
                f"{interets:,.0f} €".replace(',', ' '),
                f"{cap_final:,.0f} €".replace(',', ' ')
            ])
            cap_courant = cap_final

        # On divise le tableau pour qu'il s'étale proprement sur 2 pages (Années 1-10 puis 11-20)
        t_fin1 = Table(table_finance_data[:12], colWidths=[80, 105, 105, 105, 105])
        t_fin1.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_fin1)
        
        story.append(PageBreak())
        story.append(Paragraph("2. Tableau d'évolution (Suite et projections à terme)", style_section))
        story.append(Spacer(1, 10))
        
        t_fin2 = Table([table_finance_data[0]] + table_finance_data[12:], colWidths=[80, 105, 105, 105, 105])
        t_fin2.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(t_fin2)

        # ==========================================
        # PAGES 6 À 11 : ANALYSE TEXTUELLE DE L'IA
        # ==========================================
        paragraphes = texte_ia.split('\n')
        for para in paragraphes:
            txt = para.strip()
            if not txt:
                continue
            
            # Sauts de page automatiques basés sur les mots clés de l'IA pour étaler le texte
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

        # ==========================================
        # PAGES 12 À 14 : ANNEXES CLIENTS (Denses et complètes)
        # ==========================================
        story.append(PageBreak())
        story.append(Paragraph("4. Annexes techniques de référence", style_section))
        story.append(Paragraph("ANNEXE A : Le guide de l'Assurance-Vie et de la transmission", style_sous_section))
   
    
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

   
