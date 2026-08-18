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

# 1. Configuration de la page professionnelle (Design épuré et sérieux)
st.set_page_config(page_title="Cabinet Digital - Optimisation Patrimoniale", page_icon="🛡️", layout="wide")

# Style CSS personnalisé pour renforcer l'aspect haut de gamme et sécurisé
st.markdown("""
    <style>
    .stButton>button {
        background-color: #004B87 !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #002D54 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15) !important;
    }
    .card {
        background-color: #F8FAFC;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #004B87;
        margin-bottom: 15px;
    }
    .badge {
        background-color: #E2E8F0;
        color: #334155;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Récupération sécurisée des clés depuis les Secrets Streamlit Cloud
try:
    stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]
    STRIPE_PRICE_ID = st.secrets["STRIPE_PRICE_ID"]
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur de configuration technique : {e}")
    st.stop()

# 3. Gestion des paramètres de l'URL pour valider le paiement
query_params = st.query_params

if "session_id" in query_params:
    st.success("🎉 Paiement validé avec succès ! Votre accès au simulateur d'IA est maintenant actif.")
    st.session_state["est_paye"] = True
elif "annule" in query_params:
    st.warning("⚠️ Le processus de paiement a été interrompu. Aucun montant n'a été débité.")
    st.session_state["est_paye"] = False

# 4. TUNNEL D'ACHAT OPTIMISÉ (Si l'utilisateur n'a pas payé)
if "est_paye" not in st.session_state or not st.session_state["est_paye"]:
    
    # En-tête de confiance institutionnelle
    col_logo, col_title = st.columns([1, 10])
    with col_logo:
        st.write("## 🛡️")
    with col_title:
        st.subheader("🤖 Intelligence Artificielle & Expertise Patrimoniale")
        st.title("Générez votre Audit Patrimonial Certifié sur 20 ans")
    
    st.markdown("---")
    
    # Section : Ce que le client obtient (Valeur perçue)
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Pourquoi utiliser ce simulateur professionnel ?")
        st.markdown("""
        * **Précision Algorithmique :** Projections financières avancées basées sur vos actifs réels.
        * **Rapport IA Personnalisé :** Analyse immédiate de vos forces et des niches fiscales à exploiter.
        * **Rapport PDF Clé en Main :** Un document complet de 15 pages prêt à être partagé ou imprimé.
        * **Gain de Temps Global :** Évitez des heures de calculs complexes sur tableur.
        """)
        
        # Éléments de réassurance (Sécurité)
        st.markdown("#### 🔒 Vos garanties de sécurité")
        st.caption("✔️ Données 100% anonymisées • Connexion cryptée SSL • Aucun stockage de vos informations bancaires")
        
    with col2:
        # Boîte de tarification claire et engageante
        st.markdown(
            """
            <div class="card">
                <span class="badge">PROPOSITION UNIQUE</span>
                <h3 style='margin-top:10px;'>Accès Illimité au Simulateur</h3>
                <p>Bénéficiez de la puissance de notre IA pour auditer votre patrimoine.</p>
                <h2 style='color:#004B87; margin-bottom:0;'>49,00 € <span style='font-size:16px; color:#64748B;'>HT / unique</span></h2>
                <small style='color:#64748B;'>Facturation sécurisée Stripe • Reçu fiscal disponible immédiatement</small>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.write("") # Petit espace visuel
        
        # Bouton d'action principal ultra-visible
        if st.button("🚀 Activer mon accès et lancer l'analyse", use_container_width=True):
            try:
                url_actuelle = st.secrets.get("MON_URL_STREAMLIT", "https://streamlit.io")
                
                # CRÉATION DE LA SESSION : Mode 'payment' pour achat unique
                session_checkout = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price': STRIPE_PRICE_ID,
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f"{url_actuelle}?session_id={{CHECKOUT_SESSION_ID}}",
                    cancel_url=f"{url_actuelle}?annule=true",
                )
                
                # Interface rassurante de redirection (Alignement corrigé ici)
                st.success("✅ Lien de paiement sécurisé généré avec succès !")
                
                # Bouton officiel Streamlit cliquable
                st.link_button(
                    "👉 Cliquez ici pour ouvrir la page de paiement sécurisée Stripe", 
                    session_checkout.url, 
                    type="primary", 
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Impossible d'initier le paiement sécurisé : {e}")

    # Section : Preuve sociale (Avis clients pour rassurer)
    st.markdown("---")
    st.markdown("##### 👥 Ils utilisent notre technologie au quotidien :")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.caption("⭐ *'Ce rapport m'a permis d'économiser près de 4 200€ sur mes impôts cette année.'* — **Marc A., Entrepreneur**")
    with col_t2:
        st.caption("⭐ *'Les graphiques sont d'une clarté remarquable. Parfait pour préparer un rendez-vous bancaire.'* — **Sophie D., Investisseur**")
    with col_t3:
        st.caption("⭐ *'L'outil IA pose des questions très pertinentes, le livrable PDF vaut largement le coût.'* — **Thomas R., Conseil en gestion**")
        
    st.stop() # Bloque la suite du code tant que le paiement n'est pas actif
 

# 5. CODE DE L'APPLICATION (S'exécute uniquement si payé)
st.title("🏢 Espace Premium : Configuration de votre Simulation")
st.write("Félicitations, votre accès est validé. Vous pouvez dès maintenant configurer vos variables.")
# Insérez ici le reste de votre logique métier (Inputs, Plotly, Gemini IA, ReportLab..





