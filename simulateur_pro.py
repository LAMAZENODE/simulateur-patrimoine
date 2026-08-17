
    import streamlit as st
from google import genai
import plotly.graph_objects as go
import numpy as np

# 1. Configuration de la page professionnelle
st.set_page_config(page_title="Simulateur Patrimonial Pro", page_icon="📈", layout="wide")

# 2. Configuration IA Sécurisée (Plus de clé visible dans le code)
try:
    CLE_API = st.secrets["GEMINI_API_KEY"]
    client_ia = genai.Client(api_key=CLE_API)
except Exception as e:
    st.error(f"Erreur d'initialisation : {e}")
    st.stop()





st.title("📈 Outil Pro : Simulateur de Projection Patrimoniale")
st.write("Générez des simulations financières probabilistes pour vos clients en un clic.")

# 3. Barre latérale : Paramètres d'entrée du client
st.sidebar.header("⚙️ Paramètres du Client")
capital_initial = st.sidebar.number_input("Capital initial (€)", min_value=0, value=10000, step=1000)
epargne_mensuelle = st.sidebar.number_input("Épargne mensuelle (€)", min_value=0, value=200, step=50)
duree_annees = st.sidebar.slider("Durée de l'investissement (années)", min_value=1, max_value=40, value=20)

st.sidebar.header("📊 Hypothèses de Rendement")
rendement_moyen = st.sidebar.slider("Rendement annuel attendu (%)", min_value=0.0, max_value=15.0, value=6.0, step=0.5) / 100
volatilitet = st.sidebar.slider("Volatilité / Risque (%)", min_value=0.0, max_value=30.0, value=10.0, step=0.5) / 100

# 4. Moteur de calcul mathématique (Suites et Écarts-types)
# Création des vecteurs de temps
mois = np.arange(0, duree_annees * 12 + 1)
annees_X = mois / 12

# Calcul du rendement mensuel équivalent : (1 + R_annuel)^(1/12) - 1
rendement_mensuel = (1 + rendement_moyen) ** (1 / 12) - 1
volatilite_mensuelle = volatilitet / np.sqrt(12)

# Scénarios basés sur la distribution normale (Z-score)
# Optimiste (+1 écart-type), Réaliste (Moyen), Pessimiste (-1 écart-type)
r_pessimiste = rendement_mensuel - volatilite_mensuelle
r_realiste = rendement_mensuel
r_optimiste = rendement_mensuel + volatilite_mensuelle

def calculer_evolution(capital, epargne, taux_mensuel, nb_mois):
    # Formule mathématique de la suite géométrique :
    # Capital_n = Capital_0 * (1+r)^n + Epargne * [((1+r)^n - 1) / r]
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

# Génération des données pour les 3 courbes
capital_pessimiste = calculer_evolution(capital_initial, epargne_mensuelle, r_pessimiste, mois)
capital_realiste = calculer_evolution(capital_initial, epargne_mensuelle, r_realiste, mois)
capital_optimiste = calculer_evolution(capital_initial, epargne_mensuelle, r_optimiste, mois)

# 5. Affichage des résultats clés
total_verse = capital_initial + (epargne_mensuelle * duree_annees * 12)
final_realiste = capital_realiste[-1]

col1, col2, col3 = st.columns(3)
col1.metric("Total des versements", f"{total_verse:,.0f} €".replace(",", " "))
col2.metric("Projection (Scénario Réaliste)", f"{final_realiste:,.0f} €".replace(",", " "))
col3.metric("Intérêts générés (Estimés)", f"{(final_realiste - total_verse):,.0f} €".replace(",", " "))

# 6. Graphique interactif Plotly (Zone de projection)
fig = go.Figure()

# Courbe Optimiste
fig.add_trace(go.Scatter(x=annees_X, y=capital_optimiste, mode='lines', name='Optimiste (Haut)', line=dict(color='rgba(46, 204, 113, 0.4)', width=1)))
# Courbe Pessimiste
fig.add_trace(go.Scatter(x=annees_X, y=capital_pessimiste, mode='lines', name='Pessimiste (Bas)', line=dict(color='rgba(231, 76, 60, 0.4)', width=1), fill='tonexty', fillcolor='rgba(52, 152, 219, 0.1)'))
# Courbe Réaliste (Centrale)
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

# 7. Bouton IA : Génération du rapport d'analyse pour le client
st.subheader("📝 Analyse patrimoniale automatique (IA)")

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
                f"2. Analyse du couple rendement/risque (explique brièvement la volatilité de {volatilitet*100}%)\n"
                f"3. Conclusion et recommandation d'action."
            )

            reponse = client_ia.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            st.markdown("---")
            st.info("📋 **Document prêt à copier-coller pour votre client :**")
            st.write(reponse.text)
            
        except Exception as e:
            st.error(f"Erreur IA : {e}")

