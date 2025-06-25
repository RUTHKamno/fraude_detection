from matplotlib import pyplot as plt
from sklearn.discriminant_analysis import StandardScaler
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pickle
import warnings
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="🔒 Détection Fraudes Bancaires",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)
PREDICTION_DATA = {
    'transaction_info': {},
    'prediction_results': {},
    'has_prediction': False
}

genre_mapping = {
    'femelle': 0,
    'male': 1
}

region_mapping = {
    'Houston': 0.3950,
    'Orlando': 0.3168,
    'Miami': 0.2881,
}

type_carte_mapping = {
    'Mastercard': 0,
    'Visa': 1,
}

# CSS personnalisé pour le thème bleu-vert-rouge
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: #e5e7eb;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        color: #e5e7eb;
    }
    
    /* Default text color for all elements */
    .stApp, .stApp * {
        color: #e5e7eb !important;
    }
    
    /* Override for specific elements that should keep their colors */
    h1, h2, h3 {
        color: #3b82f6 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    .metric-card {
        background: linear-gradient(145deg, rgba(59,130,246,0.1) 0%, rgba(37,99,235,0.1) 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(59,130,246,0.3);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        margin: 10px 0;
        
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(59,130,246,0.3);
        border-color: rgba(59,130,246,0.6);
    }
    
    .prediction-card {
        background: linear-gradient(145deg, rgba(59,130,246,0.15) 0%, rgba(37,99,235,0.15) 100%);
        padding: 25px;
        border-radius: 20px;
        border: 2px solid rgba(59,130,246,0.4);
        backdrop-filter: blur(15px);
        transition: all 0.4s ease;
        text-align: center;
    }
    
    .prediction-card:hover {
        transform: scale(1.02);
        box-shadow: 0 15px 35px rgba(59,130,246,0.4);
    }
    
    .form-card {
        background: linear-gradient(145deg, rgba(59,130,246,0.1) 0%, rgba(37,99,235,0.1) 100%);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(59,130,246,0.3);
        backdrop-filter: blur(10px);
        margin: 20px 0;
        color: #e5e7eb !important;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, rgba(59,130,246,0.1) 0%, rgba(37,99,235,0.1) 100%);
    }
    
    .stSelectbox > div > div {
        background-color: rgba(59,130,246,0.1);
        border: 1px solid rgba(59,130,246,0.3);
        color: #e5e7eb !important;
    }
    
    
    .fraud-alert {
        background: linear-gradient(145deg, rgba(239,68,68,0.2) 0%, rgba(220,38,38,0.1) 100%);
        border: 2px solid #ef4444;
        border-radius: 15px;
        padding: 20px;
        animation: pulse 2s infinite;
        text-align: center;
        color: #fecaca !important;
    }
    
    .fraud-alert h2, .fraud-alert h3, .fraud-alert p {
        color: #fecaca !important;
    }
    
    .safe-alert {
        background: linear-gradient(145deg, rgba(34,197,94,0.2) 0%, rgba(22,163,74,0.1) 100%);
        border: 2px solid #22c55e;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        color: #bbf7d0 !important;
    }
    
    .safe-alert h2, .safe-alert h3, .safe-alert p {
        color: #bbf7d0 !important;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6 0%, #2563eb 100%);
        color: #e5e7eb !important;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59,130,246,0.4);
        color: #e5e7eb !important;
        font-weight: bold !important;
        background: linear-gradient(45deg, #2563eb 0%, #1d4ed8 100%) !important;
    }
    
    .stButton > button:focus {
        color: #e5e7eb !important;
        font-weight: bold !important;
        background: linear-gradient(45deg, #3b82f6 0%, #2563eb 100%) !important;
        box-shadow: 0 0 0 0.2rem rgba(59,130,246,0.25);
    }
    
    .stButton > button:active {
        color: #e5e7eb !important;
        font-weight: bold !important;
        background: linear-gradient(45deg, #3b82f6 0%, #2563eb 100%) !important;
    }
    
    .nav-button {
        background: linear-gradient(45deg, #3b82f6 0%, #2563eb 100%);
        color: #e5e7eb !important;
        padding: 10px 20px;
        border: none;
        border-radius: 25px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: bold;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(59,130,246,0.3);
        color: #e5e7eb !important;
        font-weight: bold !important;
    }
    
    .nav-button.active {
        background: linear-gradient(45deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 4px 10px rgba(59,130,246,0.5);
        color: #e5e7eb !important;
        font-weight: bold !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        color: #e5e7eb !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #e5e7eb !important;
    }
    
    /* Labels */
    label {
        color: #e5e7eb !important;
    }
    
    /* Success elements */
    .success-text {
        color: #22c55e !important;
    }
    
    /* Warning elements */
    .warning-text {
        color: #f59e0b !important;
    }
    
    /* Error elements */
    .error-text {
        color: #ef4444 !important;
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(45deg, #22c55e 0%, #16a34a 100%);
        color: white !important;
        border: none;
        border-radius: 25px;
        padding: 10px 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(34,197,94,0.4);
        background: linear-gradient(45deg, #16a34a 0%, #15803d 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

def update_prediction_data(user_inputs, prediction, probability):
    """
    Update the global prediction data array
    """
    global PREDICTION_DATA
    
    PREDICTION_DATA['transaction_info'] = {
        'age': user_inputs['age'],
        'salaire': user_inputs['salaire'],
        'score_credit': user_inputs['score_credit'],
        'montant_transaction': user_inputs['montant_transaction'],
        'anciennete_compte': user_inputs['anciennete_compte'],
        'genre': user_inputs['genre'],
        'type_carte': user_inputs['type_carte'],
        'region': user_inputs['region']
    }
    
    PREDICTION_DATA['prediction_results'] = {
        'prediction': prediction,
        'probability': probability,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    PREDICTION_DATA['has_prediction'] = True

def get_prediction_data():
    """
    Retrieve prediction data from global array
    """
    global PREDICTION_DATA
    return PREDICTION_DATA

# Fonction pour charger les données
@st.cache_data
def load_data():
    # Simuler des données si le fichier n'existe pas
    try:
        df = pd.read_csv('fraude_bancaire_synthetique_final.csv')
    except FileNotFoundError:
        # Générer des données synthétiques pour la démonstration
        return
    return df
@st.cache_data
def load_data_clean():
    # Simuler des données si le fichier n'existe pas
    try:
        data_clean = pd.read_csv('data_clean.csv')
    except FileNotFoundError:
        # Générer des données synthétiques pour la démonstration
        return
    return data_clean

# Fonction pour charger le modèle (simulé)
@st.cache_resource
def load_model():
    # Simuler un modèle si le fichier n'existe pas
    try:
        with open('model.pkl', 'rb') as file:
            model = pickle.load(file)
    except FileNotFoundError:
       return
    return model

# Fonction pour générer un rapport PDF
def generate_pdf_report(transaction_data, prediction_result, probability):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Style personnalisé
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#1e3a8a')
    )
    
    # Titre
    story.append(Paragraph("🔒 RAPPORT D'ANALYSE DE FRAUDE BANCAIRE", title_style))
    story.append(Spacer(1, 12))
    
    # Informations générales
    story.append(Paragraph(f"<b>Date d'analyse:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"<b>ID Transaction:</b> TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Résultat de l'analyse
    if prediction_result == 1:
        story.append(Paragraph("<b>🚨 RÉSULTAT: FRAUDE DÉTECTÉE</b>", 
                             ParagraphStyle('Alert', parent=styles['Normal'], 
                                          textColor=colors.red, fontSize=14, spaceAfter=12)))
        story.append(Paragraph(f"Probabilité de fraude: <b>{probability[1]:.1%}</b>", styles['Normal']))
        story.append(Paragraph("⚠️ Recommandation: Vérification manuelle requise", styles['Normal']))
    else:
        story.append(Paragraph("<b>✅ RÉSULTAT: TRANSACTION LÉGITIME</b>", 
                             ParagraphStyle('Safe', parent=styles['Normal'], 
                                          textColor=colors.green, fontSize=14, spaceAfter=12)))
        story.append(Paragraph(f"Probabilité de légitimité: <b>{probability[0]:.1%}</b>", styles['Normal']))
        story.append(Paragraph("✅ Recommandation: Transaction approuvée", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Détails de la transaction
    story.append(Paragraph("<b>DÉTAILS DE LA TRANSACTION</b>", styles['Heading2']))
    
    transaction_details = [
        ['Paramètre', 'Valeur', 'Évaluation'],
        ['Âge du client', f"{transaction_data['age']} ans", evaluate_age(transaction_data['age'])],
        ['Salaire annuel', f"{transaction_data['salaire']:,}€", evaluate_salary(transaction_data['salaire'])],
        ['Score de crédit', str(transaction_data['score_credit']), evaluate_credit_score(transaction_data['score_credit'])],
        ['Montant transaction', f"{transaction_data['montant_transaction']:,.2f}€", evaluate_amount(transaction_data['montant_transaction'], transaction_data['salaire'])],
        ['Ancienneté compte', f"{transaction_data['anciennete_compte']:.1f} ans", evaluate_account_age(transaction_data['anciennete_compte'])],
        ['Type de carte', transaction_data['type_carte'], "Standard"],
        ['Région', transaction_data['region'], "Standard"],
        ['Genre', transaction_data['genre'], "Standard"],
    ]
    
    table = Table(transaction_details)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Analyse des facteurs de risque
    story.append(Paragraph("<b>ANALYSE DES FACTEURS DE RISQUE</b>", styles['Heading2']))
    risk_factors = analyze_risk_factors(transaction_data)
    for factor in risk_factors:
        story.append(Paragraph(f"• {factor}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Recommandations
    story.append(Paragraph("<b>RECOMMANDATIONS</b>", styles['Heading2']))
    recommendations = get_recommendations(transaction_data, prediction_result)
    for rec in recommendations:
        story.append(Paragraph(f"• {rec}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Fonctions d'évaluation pour le rapport
def evaluate_age(age):
    if age < 25 or age > 70:
        return "⚠️ Risque élevé"
    elif age < 30 or age > 65:
        return "⚡ Risque modéré"
    else:
        return "✅ Normal"

def evaluate_salary(salary):
    if salary < 25000:
        return "⚠️ Faible revenu"
    elif salary > 100000:
        return "💰 Revenu élevé"
    else:
        return "✅ Normal"

def evaluate_credit_score(score):
    if score < 500:
        return "🚨 Très risqué"
    elif score < 650:
        return "⚠️ Risque modéré"
    else:
        return "✅ Bon score"

def evaluate_amount(amount, salary):
    monthly_salary = salary / 12
    if amount > monthly_salary * 0.5:
        return "⚠️ Montant élevé"
    elif amount > monthly_salary * 0.2:
        return "⚡ Montant modéré"
    else:
        return "✅ Normal"

def evaluate_account_age(age):
    if age < 1:
        return "⚠️ Compte récent"
    elif age < 3:
        return "⚡ Compte moyen"
    else:
        return "✅ Compte établi"

def analyze_risk_factors(data):
    factors = []
    
    if data['age'] < 25:
        factors.append("Âge jeune - profil à risque statistiquement plus élevé")
    if data['score_credit'] < 600:
        factors.append("Score de crédit faible - historique de crédit problématique")
    if data['montant_transaction'] > (data['salaire'] / 12) * 0.3:
        factors.append("Montant de transaction élevé par rapport au revenu mensuel")
    if data['anciennete_compte'] < 2:
        factors.append("Compte récent - moins d'historique pour validation")
    
    if not factors:
        factors.append("Aucun facteur de risque majeur identifié")
    
    return factors

def get_recommendations(data, prediction):
    recommendations = []
    
    if prediction == 1:
        recommendations.extend([
            "Suspendre temporairement la transaction",
            "Contacter le client pour vérification d'identité",
            "Vérifier l'activité récente du compte",
            "Analyser le pattern de dépenses habituel",
            "Considérer une authentification renforcée"
        ])
    else:
        recommendations.extend([
            "Autoriser la transaction",
            "Surveiller les transactions suivantes si montant inhabituel",
            "Mettre à jour le profil de risque du client"
        ])
    
    return recommendations

# Fonction pour exporter les transactions frauduleuses
def export_fraudulent_transactions(df):
    fraudulent_df = df[df['fraude'] == 1].copy()
    
    # Ajouter des colonnes d'analyse
    fraudulent_df['date_detection'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    fraudulent_df['statut'] = 'FRAUDE_CONFIRMÉE'
    fraudulent_df['risque_montant'] = fraudulent_df.apply(
        lambda x: 'ÉLEVÉ' if x['montant_transaction'] > (x['salaire']/12)*0.3 else 'MODÉRÉ', axis=1
    )
    
    # Réorganiser les colonnes
    columns_order = ['date_detection', 'statut', 'age', 'genre', 'salaire', 'score_credit', 
                    'montant_transaction', 'risque_montant', 'type_carte', 'region', 
                    'anciennete_compte', 'fraude']
    
    return fraudulent_df[columns_order]

# Navigation
def show_navigation():
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1 style='color: #e5e7eb'>🔒 Système de Détection des Fraudes Bancaires 🏦</h1>
        <p style='font-size: 18px; color: #3b82f6;'>Intelligence Artificielle pour la Sécurité Financière</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🏠 Accueil", key="nav_accueil"):
            st.session_state.page = "accueil"
    
    with col2:
        if st.button("📊 Statistiques", key="nav_stats"):
            st.session_state.page = "statistiques"
    
    with col3:
        if st.button("🎯 Prédiction", key="nav_prediction"):
            st.session_state.page = "prediction"

# Page d'accueil
def show_accueil():
    st.markdown("<h2 style='color: #e5e7eb;'>🏠 Bienvenue dans le Système de Détection des Fraudes</h2>", unsafe_allow_html=True)
    
    # Chargement des données pour les métriques
    df = load_data()
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #e5e7eb;'>📊 Total Transactions</h3>
            <h2 style='color: #e5e7eb;'>{len(df):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        fraud_count = df['fraude'].sum()
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #e5e7eb;'>🚨 Fraudes Détectées</h3>
            <h2 style='color: #ef4444;'>{int(fraud_count):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        fraud_rate = (fraud_count / len(df.dropna(subset=['fraude']))) * 100
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #e5e7eb;'>📈 Taux de Fraude</h3>
            <h2 style='color: #ef4444;'>{fraud_rate:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        avg_amount = df['montant_transaction'].mean()
        st.markdown(f"""
        <div class='metric-card'>
            <h3 style='color: #e5e7eb;'>💰 Montant Moyen</h3>
            <h2 style='color: #22c55e;'>{avg_amount:,.0f}€</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Description du système
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='form-card'>
            <h3>🎯 Fonctionnalités</h3>
            <ul>
                <li>📊 <strong>Analyse statistique</strong> complète des données</li>
                <li>🔍 <strong>Prédiction en temps réel</strong> des fraudes</li>
                <li>📈 <strong>Visualisations interactives</strong> des tendances</li>
                <li>🤖 <strong>Modèle Random Forest</strong> optimisé</li>
                <li>⚡ <strong>Interface intuitive</strong> et rapide</li>
                <li>📄 <strong>Rapports PDF détaillés</strong></li>
                <li>📊 <strong>Export des données frauduleuses</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class='form-card'>
            <h3>🛡️ Sécurité & Performance</h3>
            <ul>
                <li>🔒 <strong>Détection avancée</strong> des patterns suspects</li>
                <li>⚡ <strong>Prédictions instantanées</strong> en moins d'1 seconde</li>
                <li>📊 <strong>Précision élevée</strong> du modèle d'IA</li>
                <li>🎯 <strong>Réduction des faux positifs</strong></li>
                <li>📈 <strong>Amélioration continue</strong> des performances</li>
                <li>📋 <strong>Traçabilité complète</strong> des analyses</li>
                <li>🔍 <strong>Analyse approfondie</strong> des facteurs de risque</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Page statistiques
def show_statistiques():
    st.markdown("<h2 style='color: #e5e7eb;'> 📊 Analyse Statistique des Données </h2>", unsafe_allow_html=True)
    
    df = load_data()
    
    # Bouton d'export des transactions frauduleuses
    st.markdown("### 📥 Export des Données")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("📋 Exporter Fraudes (CSV)", key="export_csv"):
            fraudulent_df = export_fraudulent_transactions(df)
            csv = fraudulent_df.to_csv(index=False)
            st.download_button(
                label="💾 Télécharger CSV",
                data=csv,
                file_name=f"fraudes_detectees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Exporter Fraudes (Excel)", key="export_excel"):
            fraudulent_df = export_fraudulent_transactions(df)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                fraudulent_df.to_excel(writer, sheet_name='Fraudes_Detectees', index=False)
                
                # Ajouter une feuille de statistiques
                stats_df = pd.DataFrame({
                    'Métrique': ['Total Fraudes', 'Montant Moyen Fraude', 'Région la Plus Touchée', 
                               'Type Carte le Plus Touché', 'Âge Moyen Fraudeur'],
                    'Valeur': [
                        len(fraudulent_df),
                        f"{fraudulent_df['montant_transaction'].mean():,.2f}€",
                        fraudulent_df['region'].mode().iloc[0] if len(fraudulent_df) > 0 else 'N/A',
                        fraudulent_df['type_carte'].mode().iloc[0] if len(fraudulent_df) > 0 else 'N/A',
                        f"{fraudulent_df['age'].mean():.1f} ans" if len(fraudulent_df) > 0 else 'N/A'
                    ]
                })
                stats_df.to_excel(writer, sheet_name='Statistiques', index=False)
            
            processed_data = output.getvalue()
            st.download_button(
                label="💾 Télécharger Excel",
                data=processed_data,
                file_name=f"rapport_fraudes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col3:
        st.info(f"🔍 {df['fraude'].sum()} transactions frauduleuses détectées sur {len(df)} transactions totales")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='color: #e5e7eb;'> 📊 Distribution des Fraudes par Région </h3>", unsafe_allow_html=True)
        fraud_by_region = df.groupby('region')['fraude'].agg(['count', 'sum']).reset_index()
        fraud_by_region['taux'] = (fraud_by_region['sum'] / fraud_by_region['count']) * 100
        
        fig = px.bar(fraud_by_region, x='region', y='taux',
                    color='taux', color_continuous_scale=['#22c55e', '#f59e0b', '#ef4444'],
                    title="Taux de Fraude par Région (%)")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<h3 style='color: #e5e7eb;'> 💳 Fraudes par Type de Carte </h3>", unsafe_allow_html=True)
        fraud_by_card = df.groupby('type_carte')['fraude'].agg(['count', 'sum']).reset_index()
        
        fig = px.pie(fraud_by_card, values='sum', names='type_carte',
                    color_discrete_sequence=['#ef4444', '#f59e0b', '#3b82f6'],
                    title="Répartition des Fraudes par Type de Carte")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='color: #e5e7eb;'> 🎯 Score de Crédit vs Fraudes </h3>", unsafe_allow_html=True)
        df_clean = df.dropna()
        fig = px.box(df_clean, x='fraude', y='score_credit',
                    color='fraude', color_discrete_map={0: '#22c55e', 1: '#ef4444'},
                    title="Distribution du Score de Crédit par Statut de Fraude")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Montant vs Âge (Fraudes)")
        fraud_data = df_clean[df_clean['fraude'] == 1]
        safe_data = df_clean[df_clean['fraude'] == 0].sample(n=min(200, len(fraud_data)))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=safe_data['age'], y=safe_data['montant_transaction'],
            mode='markers', name='Transactions Sûres',
            marker=dict(color='#22c55e', opacity=0.6)
        ))
        fig.add_trace(go.Scatter(
            x=fraud_data['age'], y=fraud_data['montant_transaction'],
            mode='markers', name='Fraudes',
            marker=dict(color='#ef4444', size=8)
        ))
        fig.update_layout(
            title="Montant des Transactions par Âge",
            xaxis_title="Âge",
            yaxis_title="Montant (€)",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font=dict(color='white'),
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques détaillées
    st.markdown("### 📈 Statistiques Détaillées")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Variables Numériques")
        numeric_stats = df[['age', 'salaire', 'score_credit', 'montant_transaction', 'anciennete_compte']].describe()
        st.dataframe(numeric_stats.round(2))
    
    with col2:
        st.markdown("#### Variables Catégorielles")
        st.write("**Type de Carte:**")
        st.write(df['type_carte'].value_counts())
        st.write("**Région:**")
        st.write(df['region'].value_counts())
        st.write("**Genre:**")
        st.write(df['genre'].value_counts())

# Page prédiction
def show_prediction():
    df = load_data()
    data_clean = load_data_clean()
    st.markdown("## 🎯 Prédiction de Fraude")
    
    # Formulaire de prédiction (sans st.form)
    st.markdown("### 📝 Informations de la Transaction")
        
    col1, col2 = st.columns(2)
        
    with col1:
        st.markdown("#### Informations Personnelles")
        age = st.slider("Âge", min_value=0, max_value=60, value=30, step=1)
        salaire = st.slider("Salaire annuel (€)", min_value=0, max_value=5000000, value=1000, step=100000)
        genre_options = df['genre'].dropna().unique().tolist()
        genre = st.selectbox("Genre", genre_options)
        anciennete = st.slider("Ancienneté du compte (années)", min_value=0.0, max_value=50.0, value=5.0, step=0.1)
        
    with col2:
        st.markdown("#### Informations Transaction")
        score_credit = st.slider("Score de crédit", min_value=0, max_value=850, value=650)
        montant = st.slider("Montant de la transaction (€)", min_value=0.0, max_value=5000000.0, value=1000.0, step=100000.0)
        type_carte_options = df['type_carte'].dropna().unique().tolist()
        type_carte = st.selectbox("Type de carte", type_carte_options)
        region_options = df['region'].dropna().unique().tolist()
        region = st.selectbox("Région", region_options)
        
    submitted = st.button("🔍 Analyser la Transaction")
        
    if submitted:
        # Chargement du modèle
        try:
            model = load_model()
            
            # Préparation des données pour le modèle (avec encodage)
            input_data = pd.DataFrame({
                'age': [age],
                'salaire': [salaire],
                'score_credit': [score_credit],
                'montant_transaction': [montant],
                'anciennete_compte': [anciennete],
                'type_carte': [type_carte_mapping.get(type_carte, 0)],
                'region': [region_mapping.get(region, 1)],
                'genre': [genre_mapping.get(genre, 0)],
                
                
            })
            st.table(input_data)
            # standardisons input_data
            scaler = StandardScaler()
            data_clean = data_clean.drop(['fraude'], axis=1)
            scaler.fit_transform(data_clean)
            input_data_scaled = scaler.transform(input_data)
            
            # Prédiction
            prediction = model.predict(input_data_scaled)[0]
            probability = model.predict_proba(input_data_scaled)[0]

            
            # *** CORRECTION: Passer les valeurs originales de l'utilisateur ***
            user_inputs = {
                'age': age,
                'salaire': salaire,
                'score_credit': score_credit,
                'montant_transaction': montant,
                'anciennete_compte': anciennete,
                'genre': genre,
                'type_carte': type_carte,
                'region': region
            }
                        
            # Mettre à jour le tableau global avec les valeurs originales
            update_prediction_data(user_inputs, prediction, probability)
            
            st.markdown("---")
            st.markdown("### 🔍 Résultats de l'Analyse")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                if prediction == 1:
                    st.markdown(f"""
                    <div class='fraud-alert'>
                        <h2>⚠️ FRAUDE DÉTECTÉE</h2>
                        <h3>Probabilité de fraude: {probability[1]:.1%}</h3>
                        <p>🚨 Cette transaction présente des caractéristiques suspectes</p>
                        <p>⚡ Recommandation: Vérification manuelle requise</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='safe-alert'>
                        <h2>✅ TRANSACTION SÛRE</h2>
                        <h3>Probabilité de légitimité: {probability[0]:.1%}</h3>
                        <p>💳 Cette transaction semble légitime</p>
                        <p>✅ Recommandation: Transaction approuvée</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # *** NOUVEAU: Graphique des probabilités ***
            st.markdown("### 📊 Visualisation des Probabilités")
            
            # Création des données pour le graphique
            prob_data = pd.DataFrame({
                'Classe': ['Légitime', 'Frauduleuse'],
                'Probabilité': [probability[0], probability[1]],
                'Couleur': ['#28a745' if probability[0] > probability[1] else '#6c757d', 
                           '#dc3545' if probability[1] > probability[0] else '#6c757d']
            })
            
            # Création du graphique avec matplotlib
            fig, ax = plt.subplots(figsize=(8, 4))
            bars = ax.bar(prob_data['Classe'], prob_data['Probabilité'], 
                        color=prob_data['Couleur'], alpha=0.8, edgecolor='black', linewidth=1.5)

            # Personnalisation du graphique
            ax.set_ylabel('Probabilité', fontsize=12, fontweight='bold')
            ax.set_xlabel('Type de Transaction', fontsize=12, fontweight='bold')
            ax.set_title('Probabilités de Prédiction par Classe', fontsize=14, fontweight='bold', pad=15)
            ax.set_ylim(0, 1)

            # Ajout des valeurs sur les barres
            for i, (bar, prob) in enumerate(zip(bars, prob_data['Probabilité'])):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                    f'{prob:.1%}', ha='center', va='bottom', 
                    fontsize=11, fontweight='bold')

            # Ajout d'une ligne de référence à 50%
            ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7, linewidth=2)
            ax.text(0.5, 0.52, 'Seuil de décision (50%)', ha='center', va='bottom', 
                transform=ax.transData, fontsize=9, style='italic')

            # Amélioration de l'apparence
            ax.grid(axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_linewidth(0.5)
            ax.spines['bottom'].set_linewidth(0.5)

            # Affichage du graphique dans Streamlit
            st.pyplot(fig)
            plt.close()  # Libérer la mémoire

            # Alternative avec Plotly (plus interactif)
            st.markdown("#### 📈 Graphique Interactif")
            fig_plotly = px.bar(
                prob_data, 
                x='Classe', 
                y='Probabilité',
                color='Classe',
                color_discrete_map={'Légitime': '#28a745', 'Frauduleuse': '#dc3545'},
                title="Probabilités de Prédiction - Vue Interactive",
                text='Probabilité'
            )

            # Personnalisation du graphique Plotly
            fig_plotly.update_traces(
                texttemplate='%{text:.1%}', 
                textposition='outside',
                textfont_size=12
            )
            fig_plotly.update_layout(
                yaxis_title="Probabilité",
                xaxis_title="Type de Transaction",
                showlegend=False,
                height=350,
                yaxis=dict(range=[0, 1.1]),
                title_font_size=14
            )

            # Ligne de référence à 50%
            fig_plotly.add_hline(y=0.5, line_dash="dash", line_color="gray", 
                            annotation_text="Seuil de décision (50%)")

            st.plotly_chart(fig_plotly, use_container_width=True)
            # Détails de l'analyse
            st.markdown("### 📊 Détails de l'Analyse")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Données Saisies")
                st.write(f"**Âge:** {age} ans")
                st.write(f"**Salaire:** {salaire:,}€")
                st.write(f"**Score crédit:** {score_credit}")
                st.write(f"**Genre:** {genre}")
            
            with col2:
                st.write(f"**Montant:** {montant:,}€")
                st.write(f"**Type carte:** {type_carte}")
                st.write(f"**Région:** {region}")
                st.write(f"**Ancienneté:** {anciennete} ans")
                
        except Exception as e:
            st.error(f"Erreur lors du chargement du modèle: {str(e)}")
            st.info("Assurez-vous que le fichier 'model.pkl' est présent dans le répertoire.")

    # Section PDF - Maintenant en dehors du bloc if submitted
    global PREDICTION_DATA
    if PREDICTION_DATA['has_prediction']:
        st.markdown("---")
        st.markdown("### 📄 Génération de Rapport")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # *** RETRIEVE DATA FROM GLOBAL ARRAY ***
            data = get_prediction_data()
            transaction_data = data['transaction_info']
            prediction_results = data['prediction_results']
                
            try:
                # Pass data from global array to PDF function
                pdf_buffer = generate_pdf_report(
                    transaction_data, 
                    prediction_results['prediction'], 
                    prediction_results['probability']
                )
                    
                st.download_button(
                    label="💾 Télécharger Rapport PDF",
                    data=pdf_buffer,
                    file_name=f"rapport_analyse_fraude_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
                                    
            except Exception as e:
                st.error(f"Erreur lors de la génération du PDF: {str(e)}")
                st.write(f"Debug - Erreur détaillée: {str(e)}")
        
        with col2:
            st.info("""
            📋 **Le rapport PDF contient:**
            - Résultat détaillé de l'analyse
            - Évaluation de chaque paramètre
            - Analyse des facteurs de risque
            - Recommandations personnalisées
            - Traçabilité complète
            """)   
def main():
    # Initialiser la session state
    if 'page' not in st.session_state:
        st.session_state.page = 'accueil'
    
    # Navigation
    show_navigation()
    
    st.markdown("---")
    
    # Afficher la page correspondante
    if st.session_state.page == 'accueil':
        show_accueil()
    elif st.session_state.page == 'statistiques':
        show_statistiques()
    elif st.session_state.page == 'prediction':
        show_prediction()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: #3b82f6;'>
        <p>🔒 Système de Détection des Fraudes Bancaires - Powered by Random Forest & Streamlit</p>
        <p>⚡ Modèle pré-entraîné optimisé pour une détection précise et rapide</p>
        <p>📄 Rapports PDF détaillés • 📊 Export Excel/CSV • 🔍 Analyse approfondie</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
