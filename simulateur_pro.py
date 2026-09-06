import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import stripe
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="IA & Expertise Patrimoniale", layout="wide")

# Configuration de Stripe
STRIPE_SECRET_KEY = st.secrets.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = st.secrets.get("STRIPE_PUBLISHABLE_KEY", "")
PRICE_ID = st.secrets.get("STRIPE_PRICE_ID", "")
APP_URL = st.secrets.get("APP_URL", "http://localhost:8501")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Initialisation des états de session
if "paiement_reussi" not in st.session_state:
    st.session_state.paiement_reussi = False
if "verification_faite" not in st.session_state:
    st.session_state.verification_faite = False
if "donnees_client" not in st.session_state:
    st.session_state.donnees_client = {}
if "stripe_url" not in st.session_state:
    st.session_state.stripe_url = None
if "session_id_manuel" not in st.session_state:
    st.session_state.session_id_manuel = ""

st.title("🧠 Intelligence Artificielle & Expertise Patrimoniale")
st.subheader("Optimisez votre patrimoine et projetez votre avenir sur 20 ans")

# --- ÉTAPE 1 : LA SIMULATION GRATUITE ET IMMÉDIATE ---
st.markdown("### 📊 Étape 1 : Votre simulation immédiate et gratuite")

col_inputs, col_graph = st.columns([1, 2])

with col_inputs:
    st.write("⚙️ Modifiez vos paramètres ci-dessous :")
    age = st.number_input("Votre âge", min_value=18, max_value=100, value=35)
    patrimoine_actuel = st.number_input("Patrimoine actuel (€)", min_value=0, value=50000)
    epargne_mensuelle = st.number_input("Épargne mensuelle (€)", min_value=0, value=300)
    Rendement = st.slider("Hypothèse de rendement annuel (%)", 1.0, 10.0, 4.0)
    
    st.info("💡 Les graphiques à droite se mettent à jour automatiquement.")

with col_graph:
    # Calculs automatiques sans besoin de cliquer sur un bouton
    annees = np.arange(0, 21)
    
    # Formule mathématique de capitalisation (Intérêts composés)
    if Rendement > 0:
        r = Rendement / 100
        capital_brut = patrimoine_actuel * ((1 + r) ** annees) + (epargne_mensuelle * 12) * (((1 + r) ** annees) - 1) / r
    else:
        capital_brut = patrimoine_actuel + (epargne_mensuelle * 12) * annees
        
    # Calcul de la perte de pouvoir d'achat face à une inflation moyenne de 3%
    inflation_rate = 0.03
    capital_reel_inflation = capital_brut / ((1 + inflation_rate) ** annees)
    
    # Création du graphique Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=annees, y=np.round(capital_brut, 2), mode='lines+markers', name='Capital Brut (Théorique)', line=dict(color='#004B87', width=3)))
    fig.add_trace(go.Scatter(x=annees, y=np.round(capital_reel_inflation, 2), mode='lines+markers', name='Pouvoir d’Achat Réel (Inflation 3%)', line=dict(color='#D9534F', dash='dash')))
    
    fig.update_layout(
        title="Évolution de votre capital : L'effet invisible de l'inflation",
        xaxis_title="Années de projection",
        yaxis_title="Valeur (€)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# --- ÉTAPE 2 : LE MODULE DE CONVERSION ET VERROU PAYANT ---
st.markdown("---")

# VÉRIFICATION DE LA SESSION STRIPE VIA URL
query_params = st.query_params
if "session_id" in query_params and not st.session_state.verification_faite:
    session_id = query_params["session_id"]
    try:
        with st.spinner("Vérification sécurisée de votre paiement..."):
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == "paid":
                st.session_state.paiement_reussi = True
                st.session_state.verification_faite = True
                if session.metadata:
                    st.session_state.donnees_client = {
                        "age": int(session.metadata.get("age", age)),
                        "patrimoine": float(session.metadata.get("patrimoine", patrimoine_actuel)),
                        "epargne": float(session.metadata.get("epargne", epargne_mensuelle)),
                        "rendement": float(session.metadata.get("rendement", Rendement))
                    }
    except Exception as e:
        st.error(f"Erreur lors de la vérification : {str(e)}")

# AFFICHAGE DE L'INTERFACE SELON L'ÉTAT DU PAIEMENT
if st.session_state.paiement_reussi:
    st.success("🎉 Paiement validé avec succès ! Votre espace premium est déverrouillé.")
    st.markdown("### 🔓 Étape 2 : Téléchargez votre Audit Certifié complet IA (15 pages)")
    
    # Simulation d'un fichier PDF généré en mémoire
    pdf_buffer = BytesIO()
    pdf_buffer.write(b"Rapport d'Audit Patrimonial Certifie par l'IA de Naima B.")
    pdf_buffer.seek(0)
    
    st.download_button(
        label="📥 Télécharger mon rapport d'audit personnalisé (PDF)",
        data=pdf_buffer,
        file_name=f"Audit_Patrimonial_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
else:
    st.markdown("### 🔒 Étape 2 : Obtenez votre Audit Certifié complet (15 pages)")
    col_vendeuse, col_action = st.columns(2)
    
    with col_vendeuse:
        st.markdown("""
        Le constat graphique est sans appel. Sans stratégie d'optimisation active, l'inflation réduit fortement vos efforts de capitalisation. 
        
        **Ce que contient votre rapport PDF personnalisé de 15 pages rédigé par IA :**
        * 📉 **Optimisation Fiscale** : Analyse approfondie des niches adaptées à votre profil.
        * 🛡️ **Sécurisation** : Stratégies de protection et de diversification de votre épargne.
        * 🤖 **Conseils IA** : Recommandations stratégiques exclusives selon vos variables.
        * 📊 **Tableaux de bord** : Projections chiffrées détaillées année par année.
        * 💰 **Analyse de rentabilité** : Comparatif précis des meilleures enveloppes (PEA, Assurance-vie).
        """)
        
    with col_action:
        st.warning("🎁 Tarif de lancement exceptionnel : 19,00 € TTC (au lieu de 49 €)")
        
        if not STRIPE_SECRET_KEY or not PRICE_ID:
            st.info("ℹ️ Mode démo actif : Stripe n'est pas configuré dans vos secrets Streamlit.")
            if st.button("🎯 Mode Démo - Simuler un accès immédiat au rapport", use_container_width=True):
                st.session_state.paiement_reussi = True
                st.session_state.donnees_client = {
                    "age": age,
                    "patrimoine": patrimoine_actuel,
                    "epargne": epargne_mensuelle,
                    "rendement": Rendement
                }
                st.rerun()
        else:
            def create_checkout_session(a, p, e, r):
                try:
                    success_url = f"{APP_URL}?session_id={{CHECKOUT_SESSION_ID}}"
                    cancel_url = APP_URL
                    
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=["card"],
                        line_items=[{
                            "price": PRICE_ID,
                            "quantity": 1,
                        }],
                        mode="payment",
                        success_url=success_url,
                        cancel_url=cancel_url,
                        metadata={
                            "age": str(a),
                            "patrimoine": str(p),
                            "epargne": str(e),
                            "rendement": str(r),
                        },
                    )
                    return checkout_session.url, checkout_session.id
                except Exception as ex:
                    st.error(f"Erreur de communication avec Stripe: {str(ex)}")
                    return None, None

            if st.button("💳 Acheter mon Audit personnalisé pour 19€", use_container_width=True):
                url, session_id = create_checkout_session(age, patrimoine_actuel, epargne_mensuelle, Rendement)
                if url:
                    st.session_state.stripe_url = url
                    st.session_state.session_id_manuel = session_id
                    st.rerun()
            
            if st.session_state.stripe_url:
                st.markdown(f"""
                <div style="text-align: center; padding: 20px; background-color: #f0f8ff; border-radius: 10px; margin-top: 15px; border: 1px solid #635bff;">
                    <h4>🔄 Redirection de paiement disponible</h4>
                    <p>Cliquez sur le lien officiel ci-dessous pour finaliser votre commande :</p>
                    <a href="{st.session_state.stripe_url}" target="_blank" style="
                        display: inline-block;
                        padding: 12px 30px;
                        background-color: #635bff;
                        color: white;
                        text-decoration: none;
                        border-radius: 5px;
                        font-size: 16px;
                        font-weight: bold;
                    ">
                        🔒 Ouvrir la passerelle Stripe Sécurisée
                    </a>
                </div>
                """, unsafe_allow_html=True)
























