import streamlit as st
import plotly.graph_objects as go
import numpy as np
from io import BytesIO
import stripe
from datetime import datetime

# Configuration de Stripe - À MODIFIER AVEC VOS VRAIES CLÉS
STRIPE_SECRET_KEY = st.secrets.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = st.secrets.get("STRIPE_PUBLISHABLE_KEY", "")
PRICE_ID = st.secrets.get("STRIPE_PRICE_ID", "")

# URL DE VOTRE APPLICATION - À MODIFIER !
# Pour Streamlit Cloud : "https://votre-app.streamlit.app"
# Pour localhost : "http://localhost:8501"
APP_URL = st.secrets.get("APP_URL", "http://localhost:8501")

# Initialiser Stripe si configuré
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Initialisation des états
if "simulation_faite" not in st.session_state:
    st.session_state.simulation_faite = False
if "paiement_reussi" not in st.session_state:
    st.session_state.paiement_reussi = False
if "verification_faite" not in st.session_state:
    st.session_state.verification_faite = False
if "donnees_client" not in st.session_state:
    st.session_state.donnees_client = {}

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
        annees = np.arange(0, 21)
        capital = patrimoine_actuel * ((1 + Rendement/100) ** annees) + (epargne_mensuelle * 12) * ((1 + Rendement/100) ** annees - 1) / (Rendement/100)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=annees, y=capital, mode='lines+markers', name='Votre projection', line=dict(color='#004B87')))
        fig.update_layout(title="Évolution estimée de votre patrimoine", xaxis_title="Années", yaxis_title="Capital (€)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Remplissez les informations à gauche pour voir votre graphique de projection.")

# --- ÉTAPE 2 : LE VERROU PAYANT AVEC STRIPE ---
if st.session_state.simulation_faite:
    st.markdown("---")
    st.markdown("### 🔒 Étape 2 : Obtenez votre Audit Certifié complet (15 pages)")
    
    col_vendeuse, col_action = st.columns(2)
    
    with col_vendeuse:
        st.markdown("""
        **Ce que contient votre rapport PDF personnalisé :**
        * 📉 **Optimisation Fiscale** : Analyse approfondie des niches adaptées
        * 🛡️ **Sécurisation** : Stratégies de protection et diversification
        * 🤖 **Conseils IA** : Recommandations stratégiques exclusives
        * 📊 **Tableaux de bord** : Projections détaillées année par année
        * 💰 **Analyse de rentabilité** : Comparatif des enveloppes fiscales
        """)
        
    with col_action:
        st.error("💡 Tarif de lancement : 19,00 € TTC (au lieu de 49 €)")
        
        # Vérifier si Stripe est configuré
        if not STRIPE_SECRET_KEY or not PRICE_ID:
            st.warning("⚠️ Mode démo : Le paiement Stripe n'est pas configuré.")
            
            # Mode démo UNIQUEMENT pour le développement
            if st.button("🎯 Mode Démo - Obtenir le rapport gratuitement", use_container_width=True):
                st.session_state.paiement_reussi = True
                st.session_state.donnees_client = {
                    "age": age,
                    "patrimoine": patrimoine_actuel,
                    "epargne": epargne_mensuelle,
                    "rendement": Rendement
                }
                st.success("✅ Mode démo activé ! Votre rapport est prêt.")
                st.rerun()
        else:
            # Fonction pour créer une session Stripe Checkout avec URL fixe
            def create_checkout_session(age, patrimoine, epargne, rendement):
                try:
                    # Utiliser une URL fixe et valide
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
                            "age": str(age),
                            "patrimoine": str(patrimoine),
                            "epargne": str(epargne),
                            "rendement": str(rendement),
                        },
                    )
                    return checkout_session.url
                except Exception as e:
                    st.error(f"Erreur Stripe: {str(e)}")
                    return None
            
            if st.button("💳 Payer 19€ et télécharger mon Audit", use_container_width=True):
                url = create_checkout_session(age, patrimoine_actuel, epargne_mensuelle, Rendement)
                if url:
                    # Rediriger vers Stripe Checkout
                    st.markdown(f"""
                        <meta http-equiv="refresh" content="0;url={url}">
                        <div style="text-align: center; padding: 50px;">
                            <h3>🔄 Redirection vers Stripe en cours...</h3>
                            <p>Si la redirection ne fonctionne pas, <a href="{url}" target="_blank">cliquez ici</a></p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Erreur lors de la création de la session de paiement")

    # Vérification du paiement Stripe
    if not st.session_state.paiement_reussi and not st.session_state.verification_faite:
        query_params = st.query_params
        if "session_id" in query_params:
            session_id = query_params["session_id"]
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                if session.payment_status == "paid":
                    st.session_state.paiement_reussi = True
                    st.session_state.verification_faite = True
                    if session.metadata:
                        st.session_state.donnees_client = {
                            "age": int(session.metadata.get("age", 35)),
                            "patrimoine": float(session.metadata.get("patrimoine", 50000)),
                            "epargne": float(session.metadata.get("epargne", 300)),
                            "rendement": float(session.metadata.get("rendement", 4.0))
                        }
                    st.success("✅ Paiement validé ! Votre rapport est prêt.")
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur de vérification: {str(e)}")
                st.session_state.verification_faite = True

# --- ÉTAPE 3 : ACCÈS AU PDF APRÈS PAIEMENT ---
if st.session_state.paiement_reussi:
    st.markdown("---")
    st.markdown("### 📥 Téléchargez votre document")
    st.balloons()
    
    # Récupérer les données du client
    if st.session_state.donnees_client:
        age_client = st.session_state.donnees_client.get("age", age)
        patrimoine_client = st.session_state.donnees_client.get("patrimoine", patrimoine_actuel)
        epargne_client = st.session_state.donnees_client.get("epargne", epargne_mensuelle)
        rendement_client = st.session_state.donnees_client.get("rendement", Rendement)
    else:
        age_client = age
        patrimoine_client = patrimoine_actuel
        epargne_client = epargne_mensuelle
        rendement_client = Rendement

    # Fonction pour générer un contenu riche
    def generer_contenu_riche(age, patrimoine, epargne, rendement):
        projection_20 = patrimoine * ((1 + rendement/100) ** 20) + (epargne * 12) * ((1 + rendement/100) ** 20 - 1) / (rendement/100)
        projection_10 = patrimoine * ((1 + rendement/100) ** 10) + (epargne * 12) * ((1 + rendement/100) ** 10 - 1) / (rendement/100)
        
        def fmt(n):
            return f"{n:,.0f}".replace(",", " ")
        
        contenu = f"""
        PARTIE 1 : ANALYSE APPROFONDIE DE LA SITUATION PATRIMONIALE ACTUELLE

        1.1 Diagnostic financier complet
        À l'âge de {age} ans, vous disposez d'un patrimoine initial de {fmt(patrimoine)} euros. Cette situation vous place dans une catégorie d'investisseur avec un potentiel de croissance significatif sur un horizon de 20 ans. Votre capacité d'épargne mensuelle de {epargne} euros représente un effort d'épargne soutenable qui, bien investi, peut générer une richesse considérable à long terme.

        1.2 Analyse du ratio d'épargne
        Le ratio d'épargne de {(epargne*12/patrimoine*100):.1f}% par rapport à votre patrimoine actuel est un indicateur clé de votre capacité à accumuler de la richesse. Comparé à la moyenne nationale française qui se situe autour de 15%, votre situation est {'supérieure' if epargne*12/patrimoine*100 > 15 else 'inférieure'} à la moyenne.

        1.3 Projection sur 10 ans (point intermédiaire)
        À 10 ans, avec une hypothèse de rendement de {rendement}%, votre patrimoine pourrait atteindre environ {fmt(projection_10)} euros. Ce jalon intermédiaire est crucial pour évaluer la pertinence de votre stratégie d'investissement.

        1.4 Projection à 20 ans (objectif final)
        À 20 ans, votre patrimoine projeté s'élèverait à {fmt(projection_20)} euros, soit une multiplication par {(projection_20/patrimoine):.1f} de votre capital initial. Cette projection prend en compte la capitalisation des intérêts composés, véritable moteur de la création de richesse à long terme.

        PARTIE 2 : STRATÉGIE D'OPTIMISATION FISCALE EXHAUSTIVE

        2.1 L'Assurance-Vie : l'enveloppe fiscale par excellence
        L'Assurance-Vie constitue le socle de toute stratégie patrimoniale moderne. Ses avantages fiscaux sont multiples :
        - Après 8 ans de détention, l'abattement annuel sur les rachats s'élève à 4 600 euros pour une personne seule et 9 200 euros pour un couple
        - La transmission bénéficie d'une exonération de droits de succession jusqu'à 152 500 euros par bénéficiaire pour les versements avant 70 ans
        - Les intérêts capitalisés sont en report d'imposition, permettant une croissance sans frottement fiscal

        Pour votre profil de {age} ans, voici la stratégie optimale :
        - Phase 1 (0-10 ans) : Allocation dynamique à 70% en unités de compte (actions/ETF) et 30% en fonds euros
        - Phase 2 (11-15 ans) : Allocation équilibrée à 50/50
        - Phase 3 (16-20 ans) : Allocation prudente à 30/70 pour sécuriser les gains

        2.2 Le PEA (Plan d'Épargne en Actions) : l'outil de croissance
        Le PEA est l'instrument idéal pour investir en actions européennes. Ses atouts :
        - Plafond de versement : 150 000 euros
        - Exonération totale d'impôt sur le revenu après 5 ans
        - Seuls les prélèvements sociaux (17.2%) s'appliquent

        Stratégie PEA recommandée :
        - Versement initial : 30% de votre capacité d'investissement
        - DCA (Dollar Cost Averaging) : versements mensuels de {(epargne*0.4):.0f} euros
        - Répartition : 60% en ETF MSCI World, 40% en actions européennes sélectionnées

        2.3 Le PER (Plan d'Épargne Retraite) : l'avantage fiscal immédiat
        Le PER offre une déduction fiscale significative sur vos revenus. Pour un TMI de 30%, chaque versement de 1 000 euros ne vous coûte que 700 euros nets.

        - Versement annuel optimal : {min(epargne*12*0.3, 3000):.0f} euros
        - Répartition suggérée : 50% en actions, 30% en diversifié, 20% en monétaire
        - Sortie en rente pour bénéficier d'une fiscalité avantageuse

        2.4 Optimisation du couple fiscal Assurance-Vie/PEA
        La combinaison Assurance-Vie + PEA permet de couvrir tous les horizons d'investissement :
        - PEA : pour la partie "croissance" à long terme
        - Assurance-Vie : pour la diversification et la transmission
        - PER : pour la préparation de la retraite

        PARTIE 3 : GESTION DES RISQUES ET SÉCURISATION DU PATRIMOINE

        3.1 Analyse des risques du portefeuille actuel
        Votre patrimoine actuel de {fmt(patrimoine)} euros est exposé à plusieurs risques :
        - Risque d'inflation : érode le pouvoir d'achat de l'épargne non investie
        - Risque de marché : volatilité des actifs financiers
        - Risque de liquidité : immobilisation éventuelle du capital
        - Risque fiscal : optimisation insuffisante

        3.2 Stratégie de diversification optimale
        La diversification est le seul "repas gratuit" en finance. Une répartition idéale pour votre profil :

        - 40% en actions (ETF MSCI World + actions européennes)
        - 30% en obligations (fonds en euros + obligations d'État)
        - 20% en immobilier (SCPI + immobilier physique)
        - 10% en liquidités (fonds de sécurité + livrets réglementés)

        3.3 Protection contre les aléas de la vie
        - Constitution d'un matelas de sécurité de 3 à 6 mois de salaire
        - Souscription d'une prévoyance (arrêt de travail, invalidité)
        - Mise en place d'une assurance emprunteur pour les crédits

        3.4 Stratégie de sortie progressive
        - À {age+5} ans : rééquilibrage vers plus de sécurité
        - À {age+10} ans : 60% en fonds sécurisés
        - À {age+15} ans : 80% en fonds sécurisés
        - À {age+20} ans : préparation de la transmission

        PARTIE 4 : ALLOCATION DÉTAILLÉE DES ACTIFS AVEC TABLEAUX

        4.1 Répartition stratégique globale
        Classe d'actifs           | Pourcentage | Montant estimé | Rendement attendu
        --------------------------|-------------|----------------|------------------
        Actions                   | 40%         | {fmt(patrimoine*0.4)} euros    | {(rendement*1.2):.1f}%
        Obligations/Assurance-Vie | 30%         | {fmt(patrimoine*0.3)} euros    | {(rendement*0.7):.1f}%
        Immobilier (SCPI)         | 20%         | {fmt(patrimoine*0.2)} euros    | {(rendement*0.9):.1f}%
        Liquidités/Sécurité       | 10%         | {fmt(patrimoine*0.1)} euros    | 2.0%

        4.2 Détail de la poche Actions
        - 50% en ETF MSCI World (exposition aux grandes capitalisations mondiales)
        - 30% en ETF Euro Stoxx 600 (exposition aux valeurs européennes)
        - 20% en sélection de valeurs "dividendes" (entreprises ayant un historique de distribution)

        4.3 Détail de la poche Obligations
        - 60% en fonds euros (capital garanti, rendement autour de 2-3%)
        - 40% en obligations d'État de qualité (Allemagne, France, pays nordiques)

        4.4 Détail de la poche Immobilier
        - 70% en SCPI de rendement (bureaux, commerces, logistique)
        - 30% en immobilier physique (résidence principale ou investissement locatif)

        PARTIE 5 : STRATÉGIE D'INVESTISSEMENT IMMOBILIER APPROFONDIE

        5.1 Analyse des opportunités du marché
        Le marché immobilier français offre plusieurs opportunités selon les zones :
        - Grandes métropoles : rendements entre 3-4% avec forte plus-value potentielle
        - Villes moyennes : rendements entre 5-7% avec des prix d'entrée plus accessibles
        - Zones tendues : optimisation via la location meublée (LMNP)

        5.2 Dispositifs fiscaux à privilégier
        - Loi Pinel : réduction d'impôt de 12 à 21% sur 6-12 ans
        - Denormandie : rénovation en centre-ville avec réduction d'impôt
        - LMNP (Loueur Meublé Non Professionnel) : amortissement déductible

        5.3 Stratégie d'investissement recommandée
        - Phase 1 : Acquisition d'un bien en Pinel dans une zone tendue
        - Phase 2 : Investissement en SCPI pour diversifier
        - Phase 3 : Acquisition d'une résidence principale avec optimisation du crédit

        5.4 Simulation de rentabilité
        Pour un investissement de {fmt(patrimoine*0.2)} euros en SCPI :
        - Rendement locatif annuel : {(rendement*0.9):.1f}%
        - Revenus annuels estimés : {fmt(patrimoine*0.2*rendement/100*0.9)} euros
        - Fiscalité réduite grâce à l'amortissement et aux charges

        PARTIE 6 : PLANIFICATION DE LA RETRAITE SUR 20 ANS

        6.1 Évolution du capital retraite
        Année | Âge | Capital estimé | Revenu complémentaire
        ------|-----|----------------|----------------------
        0     | {age}  | {fmt(patrimoine)} euros    | 0 euros/mois
        5     | {age+5}| {fmt(patrimoine * ((1 + rendement/100) ** 5) + (epargne * 12) * ((1 + rendement/100) ** 5 - 1) / (rendement/100))} euros | {((patrimoine * ((1 + rendement/100) ** 5) + (epargne * 12) * ((1 + rendement/100) ** 5 - 1) / (rendement/100))*rendement/100/12):.0f} euros
        10    | {age+10}| {fmt(projection_10)} euros | {((projection_10*rendement/100/12)):.0f} euros
        15    | {age+15}| {fmt(patrimoine * ((1 + rendement/100) ** 15) + (epargne * 12) * ((1 + rendement/100) ** 15 - 1) / (rendement/100))} euros | {(patrimoine * ((1 + rendement/100) ** 15) + (epargne * 12) * ((1 + rendement/100) ** 15 - 1) / (rendement/100)*rendement/100/12):.0f} euros
        20    | {age+20}| {fmt(projection_20)} euros | {((projection_20*rendement/100/12)):.0f} euros

        6.2 Stratégie de désépargne progressive
        À partir de l'âge de {age+20} ans, la stratégie évolue :
        - Taux de retrait annuel recommandé : 4% (rule of 4%)
        - Revenu annuel complémentaire : environ {fmt(projection_20*0.04)} euros
        - Objectif : maintenir le capital à long terme

        6.3 Optimisation de la fiscalité à la retraite
        - Utilisation prioritaire du PEA pour les retraits (exonérés d'impôt)
        - Recours à l'Assurance-Vie après 8 ans pour bénéficier des abattements
        - Optimisation des tranches d'imposition

        6.4 Préparation des scénarios alternatifs
        Scénario optimiste (+2% de rendement) : {fmt(patrimoine * ((1 + (rendement+2)/100) ** 20) + (epargne * 12) * ((1 + (rendement+2)/100) ** 20 - 1) / ((rendement+2)/100))} euros
        Scénario pessimiste (-2% de rendement) : {fmt(patrimoine * ((1 + (rendement-2)/100) ** 20) + (epargne * 12) * ((1 + (rendement-2)/100) ** 20 - 1) / ((rendement-2)/100))} euros

        PARTIE 7 : OPTIMISATION DE LA TRANSMISSION PATRIMONIALE

        7.1 Les outils de transmission avantageuse
        - Donations au profit des enfants : abattement de 100 000 euros tous les 15 ans
        - Pacte Dutreil : exonération partielle des droits de mutation pour les entreprises
        - Assurance-Vie : transmission hors succession dans la limite de 152 500 euros par bénéficiaire
        - Démembrement de propriété : répartition usufruit/nue-propriété

        7.2 Stratégie de donation progressive
        - À {age+5} ans : donation de {fmt(patrimoine*0.1)} euros en nue-propriété
        - À {age+10} ans : donation de {fmt(patrimoine*0.15)} euros en nue-propriété
        - À {age+15} ans : donation de {fmt(patrimoine*0.2)} euros en nue-propriété
        - À {age+20} ans : donation complémentaire pour optimiser la fiscalité

        7.3 Optimisation du couple fiscal
        La combinaison des abattements successifs permet de transmettre sans frottement fiscal :
        - Période de 15 ans : renouvellement des abattements
        - Utilisation de l'Assurance-Vie pour les bénéficiaires désignés
        - Constitution d'une SCI pour faciliter la transmission immobilière

        7.4 Protection du conjoint
        - Droit de douaire : protection du conjoint survivant
        - Contrat de mariage : communauté universelle ou participation aux acquêts
        - Clause bénéficiaire de l'Assurance-Vie au bénéfice du conjoint

        PARTIE 8 : ANALYSE MACRO-ÉCONOMIQUE ET PERSPECTIVES

        8.1 Contexte économique actuel
        - Taux d'inflation : 2-3% sur la période
        - Croissance économique : 1-1.5% par an
        - Politique monétaire : orientation accommodante
        - Taux d'intérêt : stabilité à moyen terme

        8.2 Perspectives par classe d'actifs
        Actions :
        - Croissance des bénéfices : 5-7% par an
        - Ratio cours/bénéfice : 15-18x
        - Rendement des dividendes : 2-3%

        Obligations :
        - Taux des emprunts d'État : 3-4%
        - Spread de crédit : 1-2% pour les entreprises
        - Durée de sensibilité : à surveiller

        Immobilier :
        - Valorisation des SCPI : évolution contrôlée
        - Taux de vacance : 5-8%
        - Rendements locatifs : 4-6%

        8.3 Adaptation de la stratégie aux cycles
        - Phase de croissance : surpondérer les actions
        - Phase de ralentissement : privilégier les obligations et l'immobilier
        - Phase de reprise : réallocation progressive vers les actifs risqués

        8.4 Scénarios alternatifs
        Scénario de croissance élevée : {fmt(patrimoine * ((1 + (rendement+3)/100) ** 20) + (epargne * 12) * ((1 + (rendement+3)/100) ** 20 - 1) / ((rendement+3)/100))} euros
        Scénario de croissance modérée : {fmt(patrimoine * ((1 + (rendement)/100) ** 20) + (epargne * 12) * ((1 + (rendement)/100) ** 20 - 1) / ((rendement)/100))} euros
        Scénario de récession : {fmt(patrimoine * ((1 + (rendement-3)/100) ** 20) + (epargne * 12) * ((1 + (rendement-3)/100) ** 20 - 1) / ((rendement-3)/100))} euros

        PARTIE 9 : STRATÉGIE D'ÉPARGNE DE PRÉCAUTION

        9.1 Constitution du matelas de sécurité
        Objectif : {fmt(epargne*12*0.5)} euros (6 mois de salaire)
        - Épargne via livret A : {fmt(epargne*12*0.3)} euros
        - Épargne via LDDS : {fmt(epargne*12*0.2)} euros
        - Épargne via compte à terme : {fmt(epargne*12*0.5)} euros

        9.2 Gestion des imprévus
        - Constitution d'une réserve pour travaux et réparations
        - Provision pour études des enfants
        - Provision pour santé et dépendance

        9.3 Optimisation des liquidités
        - Livret A : 3% de rendement net
        - LDDS : 3% de rendement net
        - Compte à terme : 3.5% de rendement brut
        - Fonds monétaires : rendement ajusté au marché

        9.4 Intégration dans la stratégie globale
        - L'épargne de précaution n'est pas un coût d'opportunité mais une assurance
        - Garantie de ne pas devoir vendre des actifs au mauvais moment
        - Permet de saisir les opportunités d'investissement

        PARTIE 10 : PLAN D'ACTION CONCRET ET DÉTAILLÉ

        10.1 Objectifs annuels chiffrés
        Année 1 : Constitution du matelas de sécurité ({fmt(epargne*12*0.5)} euros)
        Année 2 : Ouverture et première alimentation du PEA ({fmt(epargne*12*0.3)} euros)
        Année 3 : Souscription à une Assurance-Vie ({fmt(epargne*12*0.4)} euros)
        Année 4 : Premier investissement immobilier
        Année 5 : Réévaluation complète de la stratégie

        10.2 Agenda des rendez-vous
        - T0 : Consultation avec un CIF
        - T+1 mois : Ouverture des comptes
        - T+3 mois : Premier investissement
        - T+6 mois : Bilan intermédiaire
        - T+12 mois : Révision annuelle

        10.3 Indicateurs de suivi
        - Taux d'épargne trimestriel
        - Performance relative par rapport aux objectifs
        - Niveau de risque du portefeuille
        - Ratio d'endettement

        10.4 Calendrier des actions
        Janvier : Révision de la stratégie fiscale
        Avril : Optimisation de la déclaration d'impôts
        Juillet : Bilan du premier semestre
        Octobre : Préparation des investissements de fin d'année

        PARTIE 11 : CONCLUSION GÉNÉRALE ET SYNTHÈSE

        11.1 Synthèse des recommandations majeures
        1. Mettre en place une stratégie d'investissement diversifiée sur 20 ans
        2. Optimiser la fiscalité via le trio PEA/Assurance-Vie/PER
        3. Constituer une épargne de précaution
        4. Préparer progressivement la transmission
        5. Réévaluer annuellement la stratégie

        11.2 Objectifs à 5, 10 et 20 ans
        - À 5 ans : Atteindre un patrimoine de {fmt(patrimoine * ((1 + rendement/100) ** 5) + (epargne * 12) * ((1 + rendement/100) ** 5 - 1) / (rendement/100))} euros
        - À 10 ans : Atteindre un patrimoine de {fmt(projection_10)} euros
        - À 20 ans : Atteindre un patrimoine de {fmt(projection_20)} euros

        11.3 Bénéfices attendus de la stratégie
        - Sécurité financière à long terme
        - Optimisation fiscale légale et efficace
        - Transmission maîtrisée du patrimoine
        - Indépendance financière à la retraite
        - Résilience face aux aléas économiques

        ANNEXE 1 : GLOSSAIRE DES TERMES FINANCIERS
        - PEA : Plan d'Épargne en Actions - enveloppe fiscale pour investir en actions
        - PER : Plan d'Épargne Retraite - enveloppe pour préparer la retraite
        - SCPI : Société Civile de Placement Immobilier - investissement collectif immobilier
        - ETF : Exchange Traded Fund - fonds indiciel coté
        - DCA : Dollar Cost Averaging - lissage des entrées en bourse

        ANNEXE 2 : TABLEAUX COMPARATIFS
        Enveloppe fiscale | Avantages | Inconvénients | Utilisation idéale
        ------------------|-----------|---------------|-------------------
        PEA               | Exonération d'impôt après 5 ans | Plafond de 150 000 euros | Actions long terme
        Assurance-Vie     | Transmission avantageuse | Frais de gestion | Diversification
        PER               | Déduction immédiate | Blocage jusqu'à la retraite | Préparation retraite

        ANNEXE 3 : RÉFÉRENCES LÉGISLATIVES
        - Code général des impôts, articles 125-0 A (PEA)
        - Code des assurances, articles L131-1 à L132-3 (Assurance-Vie)
        - Code général des impôts, articles 158-0 (PER)
        - Loi de finances pour l'optimisation fiscale

        ANNEXE 4 : CONTACTS ET RESSOURCES
        - Cabinet Digital IA : contact@cabinetdigital-ia.fr
        - Numéro vert : 0 800 123 456
        - Site web : www.cabinetdigital-ia.fr
        - Consultations gratuites : serviceclient@cabinetdigital-ia.fr
        """
        return contenu

    # Fonction de création du PDF
    def creer_pdf_riche(age, patrimoine, epargne, rendement):
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
        story = []
        
        styles = getSampleStyleSheet()
        style_titre_grand = ParagraphStyle('TitreGrand', parent=styles['Heading1'], fontSize=28, leading=34, textColor=colors.HexColor('#004B87'), alignment=1, spaceAfter=20)
        style_sous_titre = ParagraphStyle('SousTitre', parent=styles['Heading2'], fontSize=16, leading=22, textColor=colors.HexColor('#475569'), alignment=1, spaceAfter=200)
        style_mentions = ParagraphStyle('Mentions', parent=styles['Normal'], fontSize=9, leading=12, textColor=colors.HexColor('#94A3B8'), alignment=1)
        style_section = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=16, leading=20, textColor=colors.HexColor('#004B87'), spaceBefore=20, spaceAfter=15, keepWithNext=True)
        style_corps = ParagraphStyle('Corps', parent=styles['BodyText'], fontSize=10.5, leading=17, textColor=colors.HexColor('#1E293B'), spaceAfter=12)
        
        def fmt(n):
            return f"{n:,.0f}".replace(",", " ")
        
        # Page de garde
        story.append(Spacer(1, 80))
        story.append(Paragraph("AUDIT PATRIMONIAL CERTIFIÉ", style_titre_grand))
        story.append(Paragraph("PROJECTION FINANCIÈRE À 20 ANS", style_sous_titre))
        story.append(Spacer(1, 30))
        story.append(Paragraph("Document confidentiel - Cabinet Digital IA", style_mentions))
        story.append(Paragraph(f"Généré le : {datetime.now().strftime('%d %B %Y')}", style_mentions))
        story.append(Paragraph(f"Profil client : {age} ans - {fmt(patrimoine)} euros de patrimoine", style_mentions))
        story.append(PageBreak())
        
        # Sommaire
        story.append(Paragraph("SOMMAIRE DÉTAILLÉ", style_section))
        sommaire = [
            "Partie 1 : Analyse approfondie de la situation patrimoniale",
            "Partie 2 : Stratégie d'optimisation fiscale exhaustive",
            "Partie 3 : Gestion des risques et sécurisation du patrimoine",
            "Partie 4 : Allocation détaillée des actifs avec tableaux",
            "Partie 5 : Stratégie d'investissement immobilier approfondie",
            "Partie 6 : Planification de la retraite sur 20 ans",
            "Partie 7 : Optimisation de la transmission patrimoniale",
            "Partie 8 : Analyse macro-économique et perspectives",
            "Partie 9 : Stratégie d'épargne de précaution",
            "Partie 10 : Plan d'action concret et détaillé",
            "Partie 11 : Conclusion générale et synthèse",
            "Annexes : Glossaire, tableaux comparatifs, législation, contacts"
        ]
        for item in sommaire:
            story.append(Paragraph(item, style_corps))
            story.append(Spacer(1, 8))
        story.append(PageBreak())
        
        # Contenu
        texte_ia = generer_contenu_riche(age, patrimoine, epargne, rendement)
        paragraphes = texte_ia.split('\n')
        for para in paragraphes:
            txt = para.strip()
            if not txt:
                continue
            if "PARTIE" in txt:
                if "ANNEXE" not in txt:
                    story.append(PageBreak())
                story.append(Paragraph(txt, style_section))
            else:
                story.append(Paragraph(txt, style_corps))
        
        # Conclusion et mentions
        story.append(PageBreak())
        story.append(Paragraph("CONCLUSION FINALE", style_section))
        projection_20 = patrimoine * ((1 + rendement/100) ** 20) + (epargne * 12) * ((1 + rendement/100) ** 20 - 1) / (rendement/100)
        conclusion = f"""
        Ce rapport d'audit patrimonial de 15 pages vous offre une vision complète et stratégique de votre situation financière.
        
        Votre capital projeté à 20 ans : {fmt(projection_20)} euros
        Revenu complémentaire annuel estimé : {fmt(projection_20*rendement/100)} euros
        """
        story.append(Paragraph(conclusion, style_corps))
        
        story.append(Spacer(1, 20))
        story.append(Paragraph("MENTIONS LÉGALES", style_section))
        legal = """
        Ce document a été généré automatiquement par une intelligence artificielle à des fins informatives et pédagogiques.
        
        Il ne constitue pas un conseil en investissement personnalisé au sens de la réglementation en vigueur.
        Les performances passées ne préjugent pas des performances futures.
        
        © 2026 Cabinet Digital IA - Tous droits réservés
        """
        story.append(Paragraph(legal, style_corps))
        
        doc.build(story)
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()

    # Génération du PDF
    with st.spinner("Génération de votre rapport complet sur 15 pages..."):
        pdf_data = creer_pdf_riche(age_client, patrimoine_client, epargne_client, rendement_client)

    # Bouton de téléchargement
    st.download_button(
        label="⬇️ Télécharger l'Audit Patrimonial Complet (15 pages)",
        data=pdf_data,
        file_name=f"Audit_Patrimonial_Complet_{age_client}ans.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    
    st.success("✅ Votre rapport est prêt ! Il contient 15 pages d'analyses détaillées.")

else:
    if st.session_state.simulation_faite:
        st.info("💳 Effectuez le paiement pour accéder à votre rapport complet de 15 pages.")



















    

























