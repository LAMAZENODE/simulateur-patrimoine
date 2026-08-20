import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
from google import genai

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Cabinet Digital - Audit Patrimonial", layout="wide")

# Initialisation des états de session
if "sim_ok" not in st.session_state: st.session_state.sim_ok = False
if "pay_ok" not in st.session_state: st.session_state.pay_ok = False

try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur technique de clé API : {e}")
    st.stop()

# 2. CONTENU RÉDACTIONNEL EXPERT (DENSE ET HAUT DE GAMME)
def obtenir_audit_secours(age, patrimoine, epargne, rendement):
    return f"""PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION SUR 20 ANS
À l'âge de {age} ans, la structuration de votre patrimoine de {patrimoine:,.0f} € doit répondre à une logique d'efficience fiscale maximale et de capitalisation à long terme. Votre effort d'épargne mensuel de {epargne:,.0f} € constitue un levier d'action exceptionnel pour actionner la puissance des intérêts composés sur les deux prochaines décennies. Dans le contexte réglementaire actuel, l'objectif est de minimiser le frottement fiscal (impôt sur le revenu et prélèvements sociaux) pour maximiser le rendement net de vos avoirs.

Pour y parvenir, notre architecture patrimoniale repose sur la complémentarité de trois enveloppes fiscales majeures :
En premier lieu, le Plan d'Épargne en Actions (PEA) doit être le moteur de croissance principal de votre patrimoine financier. Limité à 150 000 € de versements en numéraire, le PEA offre un cadre d'exonération totale d'impôt sur le revenu pour l'ensemble de vos gains (plus-values et dividendes capitalisés) dès son cinquième anniversaire. Sur un horizon de 20 ans, cette franchise fiscale permet d'accélérer de manière exponentielle la croissance de votre capital en réinvestissant 100 % des performances sans aucune ponction fiscale intermédiaire.

En second lieu, l'Assurance-Vie agira comme le véritable pivot de votre organisation patrimoniale globale. Au-delà de sa huitième année, cette enveloppe vous permettra d'effectuer des rachats partiels en totale franchise d'impôt sur le revenu grâce à un mécanisme d'abattement annuel permanent (4 600 € pour un célibataire, 9 200 € pour un couple marié ou pacsé). C'est l'environnement idéal pour loger vos actifs de sécurité (fonds en euros) et votre immobilier de rendement (SCPI), tout en préparant une transmission de capital d'exception, totalement exonérée de droits de succession jusqu'à 152 500 € par bénéficiaire désigné.

En troisième lieu, le Plan d'Épargne Retraite (PER) sera activé pour transformer votre impôt direct en capital productif. Chaque versement effectué sur ce support est déductible de votre assiette de revenus imposables de l'année en cours. Ce mécanisme procure une économie d'impôt immédiate directement proportionnelle à votre Tranche Marginale d'Imposition (TMI). Pour un contribuable fortement fiscalisé, c'est un outil de levier indispensable qui permet de faire financer une partie de son épargne de long terme par l'administration fiscale.

PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION DU CAPITAL
La recherche d'un objectif de rendement annuel moyen de {rendement} % net implique la mise en place d'une allocation d'actifs rigoureuse et diversifiée. Une gestion des risques moderne ne consiste pas à éviter le risque, mais à le répartir et à le tarifer intelligemment pour traverser sereinement les cycles économiques, les crises de marché et les périodes d'inflation volatile sans jamais compromettre votre solvabilité globale.

Notre méthodologie de sécurisation s'articule autour de trois piliers complémentaires :
Le socle de sécurité défensif (liquidités et fonds en euros) : Composé de votre épargne de précaution immédiate et de fonds en euros de nouvelle génération au sein de votre assurance-vie. Ce compartiment garantit la protection absolue de votre capital et assure une disponibilité permanente des fonds pour faire face aux aléas de la vie ou saisir des opportunités d'investissement à cours décotés.

Le stabilisateur de rendement immobilier papier (SCPI) : L'introduction de parts de Sociétés Civiles de Placement Immobilier permet de décorréler une partie majeure de vos avoirs des fluctuations chaotiques des marchés financiers. En investissant dans l'immobilier tertiaire (bureaux, logistique, santé) diversifié au niveau européen, vous bénéficiez d'une distribution de revenus réguliers régis par des baux commerciaux solides, tout en protégeant votre capital de l'inflation grâce à l'indexation réglementaire des loyers.

Le moteur de performance dynamique (Actions et ETF internationaux) : Pour atteindre votre cible de performance, une quote-part de votre patrimoine doit être exposée aux entreprises mondiales. Nous privilégions l'utilisation de fonds indiciels (ETF) à frais ultra-bas (inférieurs à 0,3 % par an) répliquant de grands indices comme le MSCI World. Afin de neutraliser totalement le risque de timing boursier, nous mettons en place un processus de lissage par versements programmés : l'allocation automatique de votre épargne mensuelle de {epargne:,.0f} € vous permettra d'acheter plus de parts lorsque les marchés baissent et moins lorsqu'ils montent, optimisant mécaniquement votre prix de revient global.

PARTIE 3 : ALLOCATION STRATÉGIQUE DE CAPITAL RECOMMANDÉE
Pour matérialiser ces orientations et sécuriser l'atteinte de vos objectifs de performance, notre comité d'investissement a modélisé l'allocation cible suivante, applicable immédiatement sur votre capital disponible de {patrimoine:,.0f} € ainsi que sur vos flux d'épargne mensuels de {epargne:,.0f} € :

Répartition recommandée pour votre capital initial :
1. Poche Sécurité Globale (40 % des actifs, soit {(patrimoine*0.4):,.0f} €) : À allouer exclusivement vers le fonds en euros garanti de votre contrat d'assurance-vie sélectionné pour son absence de frais d'entrée et sa réserve de rendement.
2. Poche Immobilier Pierre-Papier (30 % des actifs, soit {(patrimoine*0.3):,.0f} €) : À investir sur un panier de 3 SCPI européennes (Allemagne, Espagne, France) afin de générer un flux de revenus réguliers net de fiscalité française grâce aux conventions fiscales internationales.
3. Poche Actions Croissance Internationale (30 % des actifs, soit {(patrimoine*0.3):,.0f} €) : À positionner au sein de votre PEA sur un ETF MSCI World capitalisant, maximisant l'effet multiplicateur des dividendes bruts réinvestis en franchise d'impôt.

Répartition recommandée pour vos versements mensuels de {epargne:,.0f} € :
- 50 % de vos flux, soit {(epargne*0.5):,.0f} € par mois, orientés vers votre PEA sur la ligne ETF Actions Mondiales pour dynamiser activement la construction de votre capital de long terme.
- 30 % de vos flux, soit {(epargne*0.3):,.0f} € par mois, alloués vers des unités de compte de SCPI de rendement au sein de l'assurance-vie pour automatiser la création d'une rente immobilière future.
- 20 % de vos flux, soit {(epargne*0.2):,.0f} € par mois, versés sur le fonds en euros pour consolider en continu votre matelas de sécurité et alimenter votre future réserve d'opportunités."""

def generer_analyse_ia(client_ia_instance, age, patrimoine, epargne, rendement):
    prompt = f"Rédige un rapport patrimonial haut de gamme et très dense pour un client de {age} ans ayant {patrimoine} euros de capital et {epargne} euros d'épargne mensuelle. Rédige de très longs paragraphes d'expert financier. Crée trois grands chapitres textuels : PARTIE 1 : STRATÉGIE FISCALE D'OPTIMISATION SUR 20 ANS, PARTIE 2 : GESTION DES RISQUES ET SÉCURISATION DU CAPITAL, PARTIE 3 : ALLOCATION STRATÉGIE DE CAPITAL RECOMMANDÉE. Rédige uniquement en texte brut sans dièses ni étoiles."
    try:
        reponse = client_ia_instance.models.generate_content(
            model="gemini-3.6-flash", contents=prompt,
            config={"max_output_tokens": 4096, "temperature": 0.3}
        )
        return reponse.text if reponse.text else obtenir_audit_secours(age, patrimoine, epargne, rendement)
    except Exception:
        return obtenir_audit_secours(age, patrimoine, epargne, rendement)

# 3. MOTEUR DE MISE EN PAGE PDF AVEC STYLE ET DESIGN DE CABINET DIGITAL
def ajouter_decorations(canvas, doc):
    """Ajoute des éléments de design professionnels sur chaque page (En-tête, Pied de page, Lignes)"""
    canvas.saveState()
    # Barre de couleur supérieure (En-tête pro)
    canvas.setFillColor(colors.HexColor('#004B87'))
    canvas.rect(0, letter[1] - 25, letter[0], 25, stroke=0, fill=1)
    
    # Texte de l'en-tête
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(colors.white)
    canvas.drawString(50, letter[1] - 16, "CONFIDENTIEL — AUDIT PATRIMONIAL IA EXPERTISE")
    
    # Pied de page (Ligne + Numérotation de page)
    canvas.setStrokeColor(colors.HexColor('#CBD5E1'))
    canvas.setLineWidth(0.5)
    canvas.line(50, 45, letter[0] - 50, 45)
    
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#64748B'))
    canvas.drawString(50, 32, "Cabinet Digital — Document généré par Intelligence Artificielle certifiée")
    canvas.drawRightString(letter[0] - 50, 32, f"Page {doc.page}")
    canvas.restoreState()

def creer_pdf(texte_ia, age, patrimoine, epargne, rendement):
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=60)
    story = []
    styles = getSampleStyleSheet()
    
    # Définition d'une charte graphique haut de gamme












    

























