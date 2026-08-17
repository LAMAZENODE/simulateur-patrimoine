import streamlit as st
from google import genai
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import stripe 

# Importations obligatoires pour le PDF ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Configuration de la page professionnelle
st.set_page_config(page_title="Simulateur Patrimonial Pro", page_icon="📈", layout="wide")

# 2. Récupération sécurisée des clés depuis les Secrets Streamlit Cloud
try:
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    STRIPE_PRICE_ID = st.secrets["STRIPE_PRICE_ID"]
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur de configuration des clés : {e}")
    st.stop()

st.title("📈 Outil Pro : Simulateur de Projection Patrimoniale")

# 3. Gestion des paramètres de l'URL pour valider le paiement
query_params = st.query_params

if "session_id" in query_params:
    st.success("🎉 Accès Professionnel Débloqué ! Vous pouvez utiliser le simulateur.")
    st.session_state["est_paye"] = True
elif "annule" in query_params:
    st.error("❌ Le paiement n'a pas été finalisé. L'accès reste restreint.")
    st.session_state["est_paye"] = False

# 4. Tunnel de paiement : Bloque l'application si l'utilisateur n'a pas payé
if "est_paye" not in st.session_state or not st.session_state["est_paye"]:
    st.info("💳 Cet outil d'analyse patrimoniale par IA est réservé aux abonnés professionnels.")
    
    if st.button("🛒 Activer mon abonnement mensuel (49€/mois)", use_container_width=True):
        try:
            url_actuelle = st.secrets.get("MON_URL_STREAMLIT", "https://streamlit.io")
            
            # Création de la page de paiement sécurisée Stripe
            session_checkout = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': STRIPE_PRICE_ID,
                    'quantity': 1,
                }],
                mode='subscription', 
                success_url=f"{url_actuelle}?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{url_actuelle}?annule=true",
            )
            st.link_button("Aller vers la page de paiement sécurisée", session_checkout.url, use_container_width=True)
        except Exception as e:
            st.error(f"Erreur lors de l'ouverture du tunnel Stripe : {e}")
    st.stop() # Bloque la suite du code tant que le paiement n'est pas fait

# =========================================================================
# 5. INTERFACE ET CODE MATHÉMATIQUE (Uniquement pour les utilisateurs payés)
# =========================================================================

st.write("Générez des simulations financières probabilistes et téléchargez le rapport PDF pour vos clients.")

# Barre latérale : Paramètres d'entrée du client
st.sidebar.header("⚙️ Paramètres du Client")
capital_initial = st.sidebar.number_input("Capital initial (€)", min_value=0, value=10000, step=1000)
epargne_mensuelle = st.sidebar.number_input("Épargne mensuelle (€)", min_value=0, value=200, step=50)
duree_annees = st.sidebar.slider("Durée de l'investissement (années)", min_value=1, max_value=40, value=20)

st.sidebar.header("📊 Hypothèses de Rendement")
rendement_moyen = st.sidebar.slider("Rendement annuel attendu (%)", min_value=0.0, max_value=15.0, value=6.0, step=0.5) / 100
volatilitet = st.sidebar.slider("Volatilité / Risque (%)", min_value=0.0, max_value=30.0, value=10.0, step=0.5) / 100

# Moteur de calcul mathématique (Suites et Écarts-types)
mois = np.arange(0, duree_annees * 12 + 1)
annees_X = mois / 12

rendement_mensuel = (1 + rendement_moyen) ** (1 / 12) - 1
volatilite_mensuelle = volatilitet / np.sqrt(12)

r_pessimiste = rendement_mensuel - volatilite_mensuelle
r_realiste = rendement_mensuel
r_optimiste = rendement_mensuel + volatilite_mensuelle

def calculer_evolution(capital, epargne, taux_mensuel, nb_mois):
    evolution = []
    for m in nb_mois:
        if taux_mensuel == 0:
            valeur = capital + epargne * m
        else:
            composition_capital = capital * ((1 + taux_mensuel) ** m)
            composition_epargne = epargne * (((1 + taux_mensuel) ** m - 1) / taux_mensuel)
            valeur = composition_capital + composition_epargne
        evolution.append(valeur)
    return np.array(evolution)

capital_pessimiste = calculer_evolution(capital_initial, epargne_mensuelle, r_pessimiste, mois)
capital_realiste = calculer_evolution(capital_initial, epargne_mensuelle, r_realiste, mois)
capital_optimiste = calculer_evolution(capital_initial, epargne_mensuelle, r_optimiste, mois)

# Affichage des résultats clés
total_verse = capital_initial + (epargne_mensuelle * duree_annees * 12)
final_realiste = capital_realiste[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Total des versements", f"{total_verse:,.0f} €".replace(",", " "))
col2.metric("Projection (Scénario Réaliste)", f"{final_realiste:,.0f} €".replace(",", " "))
col3.metric("Intérêts générés (Estimés)", f"{(final_realiste - total_verse):,.0f} €".replace(",", " "))

# Graphique interactif Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(x=annees_X, y=capital_optimiste, mode='lines', name='Optimiste (Haut)', line=dict(color='rgba(46, 204, 113, 0.4)', width=1)))
fig.add_trace(go.Scatter(x=annees_X, y=capital_pessimiste, mode='lines', name='Pessimiste (Bas)', line=dict(color='rgba(231, 76, 60, 0.4)', width=1), fill='tonexty', fillcolor='rgba(52, 152, 219, 0.1)'))
fig.add_trace(go.Scatter(x=annees_X, y=capital_realiste, mode='lines', name='Scénario Médian', line=dict(color='#2980b9', width=3)))

fig.update_layout(
    title="Évolution probable du patrimoine",
    xaxis_title="Années",
    yaxis_title="Valeur du portefeuille (€)",
    legend_orientation="h",
    margin=dict(l=20, r=20, t=40, b=20),
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

# 6. Bouton IA : Génération du rapport d'analyse pour le client
st.subheader("📝 Analyse patrimoniale automatique (IA)")

if "rapport_texte" not in st.session_state:
    st.session_state["rapport_texte"] = ""

if st.button("🤖 Rédiger le rapport de synthèse", use_container_width=True):
    with st.spinner("Rédaction du rapport pro par l'IA..."):
        try:
            prompt = (
                f"Tu es un expert en gestion de patrimoine de haut niveau. "
                f"Rédige un rapport de synthèse clair, formel et vendeur pour un conseiller financier à destination de son client.\n\n"
                f"Données de la simulation :\n"
                f"- Apport initial : {capital_initial} €\n"
                f"- Effort d'épargne mensuel : {epargne_mensuelle} €\n"
                f"- Durée du placement : {duree_annees} ans\n"
                f"- Total versé par le client : {total_verse} €\n"
                f"- Valeur finale estimée (médiane) : {final_realiste:.0f} €\n"
                f"- Scénario pessimiste limite : {capital_pessimiste[-1]:.0f} €\n"
                f"- Scénario optimiste limite : {capital_optimiste[-1]:.0f} €\n\n"
                f"Structure attendue :\n"
                f"1. Résumé de la stratégie\n"
                f"2. Analyse du couple rendement/risque (expliquant la volatilité de {volatilitet*100}%)\n"
                f"3. Conclusion et recommandation d'action.\n"
                f"N'utilise aucune étoile de mise en forme Markdown."
            )

            reponse = client_ia.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            st.session_state["rapport_texte"] = reponse.text
            
        except Exception as e:
            st.error(f"Erreur IA : {e}")

if st.session_state["rapport_texte"]:
    st.markdown("---")
    st.info("📋 **Document d'analyse généré :**")
    st.write(st.session_state["rapport_texte"])

    # Fonction pour créer le fichier PDF
    def generer_pdf_professionnel(texte):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, title="Bilan Patrimonial")
        styles = getSampleStyleSheet()
        
        style_titre = ParagraphStyle(
            'TitreDoc', parent=styles['Heading1'], 
            textColor=colors.HexColor("#2980b9"), fontSize=22, spaceAfter=20
        )
        style_texte = ParagraphStyle(
            'TexteDoc', parent=styles['Normal'], 
            fontSize=11, leading=16, spaceAfter=12
        )
        
        story = []
        story.append(Paragraph("📊 BILAN DE PROJECTION PATRIMONIALE", style_titre))
        story.append(Spacer(1, 15))
        
        lignes = texte.split('\n')
        for ligne in lignes:
            if ligne.strip():
                story.append(Paragraph(ligne, style_texte))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    pdf_document = generer_pdf_professionnel(st.session_state["rapport_texte"])
    
    st.download_button(
        label="📥 Télécharger le rapport officiel au format PDF",
        data=pdf_document,
        file_name="Bilan_Patrimoine_Client.pdf",
        mime="application/pdf",
        use_container_width=True
    )


