import streamlit as st
import joblib
import pandas as pd
import plotly.express as px

# Charger le modèle
model = joblib.load("random_forest_model.pkl")

# Appliquer un style CSS
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .sidebar { background-color: #2E86C1; padding: 20px; }
    .sidebar h1, .sidebar label { color: white; }
    .big-font { font-size:20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.image("logo_banque.jpg", width=150)
st.title("🔍 Prédiction d'Éligibilité au Prêt")
st.markdown('<p class="big-font">Remplissez les informations pour savoir si un prêt sera accepté.</p>', unsafe_allow_html=True)

st.sidebar.header("📋 Informations du client")

# Entrée des données utilisateur
person_age = st.sidebar.slider("Âge", 18, 100, 30)
person_income = st.sidebar.number_input("💰 Revenu Annuel (€)", min_value=5000, max_value=500000, value=50000)
person_emp_length = st.sidebar.slider("🧑‍💼 Ancienneté (années)", 0, 50, 5)
loan_amnt = st.sidebar.number_input("💳 Montant du prêt demandé (€)", min_value=1000, max_value=50000, value=10000)
loan_int_rate = st.sidebar.slider("📈 Taux d'intérêt (%)", 1.0, 30.0, 10.0)

# 🆕 Ajout du ratio prêt/revenu
loan_percent_income = round(loan_amnt / person_income, 2)

# 🆕 Historique de crédit
cb_person_cred_hist_length = st.sidebar.slider("📊 Historique de crédit (années)", 0, 50, 10)

# 🆕 Type de logement
home_ownership = st.sidebar.selectbox("🏠 Type de logement", ["Locataire", "Propriétaire", "Hypothèque"])
home_ownership_map = {
    "Locataire": [1, 0, 0],
    "Propriétaire": [0, 1, 0],
    "Hypothèque": [0, 0, 1]
}

# 🆕 Indicateur de défaut de paiement (Oui/Non)
cb_person_default_on_file = st.sidebar.radio("⚠ Défaut de paiement passé ?", ["Non", "Oui"])
cb_person_default_on_file_1 = 1 if cb_person_default_on_file == "Oui" else 0  # Encode "Oui" = 1

# 🆕 Objectif du prêt (one-hot encoding)
loan_intent = st.sidebar.selectbox("🎯 Objectif du prêt", 
                                   ["Achat immobilier", "Voiture", "Éducation", "Business", "Mariage"])
loan_intent_map = {
    "Achat immobilier": [1, 0, 0, 0, 0],
    "Voiture": [0, 1, 0, 0, 0],
    "Éducation": [0, 0, 1, 0, 0],
    "Business": [0, 0, 0, 1, 0],
    "Mariage": [0, 0, 0, 0, 1]
}

# 🆕 Niveau de risque du prêt (loan grade, one-hot encoding)
loan_grade = st.sidebar.selectbox("🏦 Classement du prêt", ["A", "B", "C", "D", "E", "F"])
loan_grade_map = {
    "A": [1, 0, 0, 0, 0, 0],
    "B": [0, 1, 0, 0, 0, 0],
    "C": [0, 0, 1, 0, 0, 0],
    "D": [0, 0, 0, 1, 0, 0],
    "E": [0, 0, 0, 0, 1, 0],
    "F": [0, 0, 0, 0, 0, 1]
}

# Liste exacte des colonnes utilisées dans l'entraînement du modèle
feature_names = [
    "person_age", "person_income", "person_emp_length", 
    "loan_amnt", "loan_int_rate", "loan_percent_income",
    "cb_person_cred_hist_length", 
    "person_home_ownership_1", "person_home_ownership_2", "person_home_ownership_3",
    "loan_intent_1", "loan_intent_2", "loan_intent_3", "loan_intent_4", "loan_intent_5",
    "loan_grade_1", "loan_grade_2", "loan_grade_3", "loan_grade_4", "loan_grade_5", "loan_grade_6",
    "cb_person_default_on_file_1"
]

# Créer un dataframe avec les valeurs entrées par l'utilisateur
data = pd.DataFrame([[
    person_age, person_income, person_emp_length, loan_amnt, 
    loan_int_rate, loan_percent_income, cb_person_cred_hist_length, 
] + home_ownership_map[home_ownership] + loan_intent_map[loan_intent] + loan_grade_map[loan_grade] + [cb_person_default_on_file_1]],
columns=feature_names)

# Affichage des données envoyées au modèle
st.write("📊 Aperçu des données envoyées au modèle :", data)

# Graphique interactif avec Plotly
fig = px.pie(values=[person_income, loan_amnt], names=["Revenu", "Montant du prêt"], 
             title="Répartition Revenu vs Montant demandé")
st.plotly_chart(fig)

# 🔮 Prédiction de l'éligibilité au prêt
if st.sidebar.button("Prédire l'éligibilité"):
    prediction = model.predict(data)[0]
    
    # Affichage dynamique du résultat
    if prediction == 0:
        st.success("✅ Félicitations ! Le prêt est approuvé !")
        st.balloons()
    else:
        st.error("❌ Désolé, le prêt est refusé.")