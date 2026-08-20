import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from google import genai

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Cabinet Digital", layout="wide")

# 2. INITIALISATION DES ÉTATS DE SESSION (Sécurisation des appels uniques)
if "sim_ok" not in st.session_state: st.session_state.sim_ok = False
if "pay_ok" not in st.session_state: st.session_state.pay_ok = False
if "pdf_pret" not in st.session_state: st.session_state.pdf_pret = None

# 3. RÉCUPÉRATION SÉCURISÉE DES ACCÈS API GEMINI
try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur technique de clé API : {e}")
    st.stop()

# 4. TEXTE DE SECOURS DE HAUTE QUALITÉ EN CAS DE QUOTA DÉPASSÉ (Évite le rapport vide)
def obtenir_audit_secours(age, patrimoine, epargne, rendement):
    return f"""PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION
À l'âge de {age} ans, la structuration de votre patrimoine de {patrimoine:,.0f} € doit répondre à un objectif de capitalisation performante et d'optimisation fiscale sur un horizon de 20 ans. Votre effort d'épargne mensuel de {epargne} € constitue un levier majeur pour actionner la puissance des intérêts composés.

Pour optimiser votre fiscalité, nous préconisons l'utilisation conjointe de trois enveloppes fiscales majeures :
En premier lieu, le Plan d'Épargne en Actions (PEA) doit être maximisé pour vos investissements sur les marchés de capitaux. Le PEA offre une exonération totale d'impôt sur le revenu après 5 ans de détention, ce qui en fait le moteur de croissance idéal pour votre poche de diversification actions.

En second lieu, l'Assurance-Vie agira comme le véritable pivot de votre organisation patrimoniale. Au-delà de sa 8ème année, elle vous permettra d'effectuer des retraits en bénéficiant d'un abattement annuel sur les gains. C'est l'enveloppe à privilégier pour loger vos actifs de sécurité (fonds en euros) et votre immobilier de rendement (SCPI), tout en préparant une transmission de capital hors droits de succession.

En troisième lieu, le Plan d'Épargne Retraite (PER) sera utilisé pour réduire votre impôt immédiat. Chaque versement effectué est déductible de votre assiette de revenus, vous offrant une économie d'impôt proportionnelle à votre tranche marginale d'imposition.

PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION
La recherche d'un rendement cible de {rendement} % par an implique la mise en place d'une allocation équilibrée et diversifiée, capable de traverser les différents cycles économiques tout en protégeant votre capital des effets de l'inflation.

La maîtrise du risque repose sur une répartition méthodique en trois poches distinctes :
La poche de liquidité et de sécurité court terme, composée de vos livrets bancaires et de fonds en euros garantis au sein de votre assurance-vie. Cette base défensive protège votre patrimoine des secousses de marché et reste disponible à tout moment en cas d'imprévu.

La poche de rendement immobilier, construite à partir de parts de Sociétés Civiles de Placement Immobilier (SCPI). L'immobilier de rendement permet de décorréler une partie de vos avoirs des marchés boursiers tout en générant des revenus réguliers.

La poche de croissance dynamique, investie sur des marchés d'actions internationaux par le biais de fonds indiciels (ETF) à bas coûts. Pour neutraliser le risque de timing sur ces actifs volatils, nous préconisons la méthode des versements programmés : l'investissement de votre épargne mensuelle de {epargne} € lissera votre prix d'entrée sur les 20 prochaines années.

PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE
Pour concrétiser cette stratégie et atteindre votre objectif de rendement annuel de {rendement} %, voici l'allocation cible recommandée pour la répartition de vos actifs :

Poche de Sécurité (40% des actifs) : Allocation de votre capital vers les fonds en euros de vos contrats d'assurance-vie et vos supports monétaires. Cette poche sécurise le portefeuille global.

Poche Immobilière Papier (30% des actifs) : Sélection de SCPI de rendement diversifiées au niveau européen pour distribuer des revenus réguliers et capitaliser sur le marché immobilier tertiaire.

Poche Actions Croissance (30% des actifs) : Investissement via votre PEA sur un ETF répliquant l'indice mondial MSCI World, permettant de capter la performance des plus grandes entreprises globales avec des frais de gestion réduits au minimum."""

def generer_analyse_ia(client_ia_instance, age, patrimoine, epargne, rendement):
    prompt = f"Rédige un rapport patrimonial dense pour un client de {age} ans ayant {patrimoine} euros de capital et {epargne} euros d'épargne. Crée trois grands chapitres textuels : PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION, PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION, PARTIE 3 : ALLOCATION DE CAPITAL RECOMMANDÉE. Écris de longs paragraphes détaillés. Rédige uniquement en texte brut sans dièses ni étoiles."
    try:
        reponse = client_ia_instance.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={"max_output_tokens": 4096, "temperature": 0.3}
        )
        return reponse.text if reponse.text else obtenir_audit_secours(age, patrimoine, epargne, rendement)
    except Exception:
        # Si le quota est dépassé (Erreur 429) ou l'API échoue, on renvoie le texte de secours pro
        return obtenir_audit_secours(age, patrimoine, epargne, rendement)

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
    st_table = Table(sommaire_data, colWidths=[400, 100])
    st_table.setStyle(TableStyle([('BOTTOMPADDING', (0,0), (-1,-1), 8), ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9'))]))
    story.append(st_table); story.append(PageBreak())

    # PAGE 3 : SYNTHÈSE
    story.append(Paragraph("1. Synthèse du profil", style_section))
    donnees_table = [["Métrique", "Valeur"], ["Âge", f"{age} ans"], ["Patrimoine", f"{patrimoine:,.0f} €"], ["Épargne", f"{epargne} €/mois"]]
    t = Table(donnees_table, colWidths=[250, 250])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (1,0), colors.HexColor('#F1F5F9')), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0'))]))
    story.append(t); story.append(PageBreak())

    # PAGES 4 & 5 : TABLEAU FINANCIER D'ÉVOLUTION SUR 20 ANS
    story.append(Paragraph("2. Projections financières", style_section))
    table_finance_data = [["Année", "Capital Initial", "Épargne", "Intérêts", "Capital Final"]]
    cap_courant = patrimoine
    for an in range(1, 21):
        interets = (cap_courant + (epargne * 12) / 2) * (rendement / 100)
        cap_final = cap_courant + (epargne * 12) + interets
        table_finance_data.append([f"Année {an}", f"{cap_courant:,.0f} €", f"{(epargne*12):,.0f} €", f"{interets:,.0f} €", f"{cap_final:,.0f} €"])
        cap_courant = cap_final

    t_fin1 = Table(table_finance_data[:12], colWidths=[70, 110, 100, 110, 110])
    t_fin1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]), ('FONTSIZE', (0,0), (-1,-1), 9)]))
    story.append(t_fin1); story.append(PageBreak())
    
    story.append(Paragraph("2. Projections financières (Suite)", style_section))
    t_fin2 = Table([table_finance_data[0]] + table_finance_data[12:], colWidths=[70, 110, 100, 110, 110])
    t_fin2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#004B87')), ('TEXTCOLOR', (0,0), (-1,0), colors.white), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')), ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')]), ('FONTSIZE', (0,0), (-1,-1), 9)]))
    story.append(t_fin2)

    # PAGES 6 À 11 : INTEGRATION DU RAPPORT TEXTUEL
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






    

























