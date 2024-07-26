from src.components.sidebar import sidebar

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from streamlit_agraph import agraph, Node, Edge, Config

sidebar("Genii • Conversation Analysis | Bubble Chart", '🧞 :violet[Genii] • Conversation Analysis', " 📊 Bubble")

categories = [
    "Support technique",
    "Service client",
    "Technique",
    "Support client",
    "Consultation en optimisation des processus",
    "Technologie",
    "Relation client",
    "Gestion de projets",
    "Gestion de projet",
    "Information",
    "service client",
    "Assistance technique",
    "Sécurité des données",
    "conseils en performance",
    "Information sur la double authentification",
    "CRM intégration",
    "Sécurité",
    "Information partenariat"
]

themes = [
    "Sécurité des comptes",
    "Alertes personnalisées",
    "Interface Utilisateur",
    "Sécurité des données",
    "Service client",
    "Consultation",
    "Sauvegarde",
    "Configuration alertes",
    "Support client",
    "Paiement",
    "Optimisation logiciel",
    "Facturation",
    "Gestion utilisateurs",
    "Partenariat",
    "Gestion de compte",
    "Application mobile",
    "Support technique",
    "Annulation abonnement",
    "Abonnement",
    "Bug report",
    "Problème technique",
    "Problèmes techniques",
    "Amélioration produit",
    "Notifications",
    "Sécurité des logiciels",
    "Formation technologique",
    "Configuration compte",
    "Formation en ligne",
    "Gestion projets",
    "Compatibilité logiciel",
    "Performance logicielle",
    "Protection des données",
    "Intégration logiciel",
    "Migration données",
    "Sécurité",
    "Problème de compte",
    "Intégration logicielle",
    "Démo produit",
    "Outils de gestion",
    "Politique de retour",
    "Récupération de données"
]

sub_themes = [
    "Double authentification",
    "Configuration",
    "Guide de l'Utilisateur",
    "Chiffrement",
    "Attente prolongée",
    "Annulation abonnement",
    "Optimisation processus",
    "Cloud",
    "Exemple alerte",
    "Ticket de support",
    "Problème de carte",
    "Développeurs",
    "Performances",
    "Mode de paiement",
    "Coût supplémentaire",
    "Résolution de problème",
    "Commercial",
    "Gestion des réclamations",
    "Contrat en cours",
    "Compatibilité iPhone",
    "Problème logiciel",
    "Frais",
    "Mise à jour",
    "Application crash",
    "Application se fermant",
    "Logiciel plantage",
    "Interface utilisateur",
    "Remboursement",
    "Problèmes de réception",
    "Amélioration",
    "Mises à jour",
    "Blockchain",
    "Paramètres et permissions",
    "Cybersécurité",
    "Offre de services",
    "Services offerts",
    "Windows 10",
    "Consommation de ressources",
    "Conformité GDPR",
    "CRM",
    "Service cloud",
    "Rapports mensuels",
    "Vérification en deux étapes",
    "Accès refusé",
    "Salesforce",
    "Planification",
    "Petites entreprises",
    "Remboursement logiciel",
    "Perte de fichiers",
    "Changement d'adresse de facturation"
]

categories = ['assistance', 'service client', 'configuration', 'relation client', 'support technique', 'technique', 'sécurité', 'information', 'technologie', 'service', 'informatique', 'support', 'service de consultation']
themes = ['notifications', 'alertes', 'gestion des appels', 'intégration logicielle', 'gestion de compte', 'authentification', 'protection des données', 'migration de données', 'conformité gdpr', 'offres de support', 'récupération de données', 'support technique', 'mise à jour d\'abonnement', 'paiement', 'feedback utilisateur', 'annulation d\'abonnement', 'développeurs', 'amélioration', 'compatibilité', 'mise à jour de sécurité', 'support en direct', 'optimisation des performances', 'sauvegarde', 'application mobile', 'problème logiciel', 'police de retour', 'optimisation des processus', 'demande de démo', 'facturation', 'changement d\'adresse', 'formation en ligne', 'interface utilisateur', 'gestion des commandes', 'suivi de tickets', 'offres pour les petites entreprises', 'communication', 'formation', 'tarification', 'services', 'sécurité', 'partenariat', 'problème de compte', 'alertes personnalisées', 'configuration utilisateur', 'intégration logiciel', 'performance logicielle']
sub_themes = ['création compte et permissions', 'fermeture immédiate de l\'application', 'support dédié', 'accès aux tickets', 'procédure d\'annulation', 'programme de partenariat', 'ajout d\'utilisateur', 'retour de produits', 'problème de chargement', 'exemple alerte', 'conseils généraux', 'accès et réinitialisation du mot de passe', 'adresse de facturation', 'consommation de ressources', 'accompagnement migration', 'demande de remboursement', 'support en direct', 'traitement des requêtes', 'vérification en deux étapes', 'niveau de support', 'planification démo', 'double authentification', 'problèmes de réception', 'crash à l\'ouverture', 'coût', 'téléchargement de rapports', 'demande d\'assistance', 'signalement de bug', 'chiffrement avancé', 'blockchain', 'guide de l\'utilisateur', 'cybersécurité', 'configuration', 'installation et guide', 'création de projets', 'coordination interdépartementale', 'intégration avec crm', 'serveur', 'interface complexe', 'compatibilité avec les iphones', 'commande endommagée', 'attente prolongée', 'procédure d\'annulation', 'méthode de paiement', 'mesures de conformité', 'problème de chargement', 'résiliation pour manque d\'utilité', 'explication facturation mensuelle']

def preprocess_texts(texts):
    # Normalize texts by converting to lowercase and removing duplicates
    normalized_texts = list(set([text.lower() for text in texts]))
    return normalized_texts

def generate_similarity_graph(categories, themes, sub_themes, threshold=0.2):
    # Preprocess texts
    categories = preprocess_texts(categories)
    themes = preprocess_texts(themes)
    sub_themes = preprocess_texts(sub_themes)
    
    # Combine all text data
    all_texts = categories + themes + sub_themes
    all_labels = ['category'] * len(categories) + ['theme'] * len(themes) + ['sub_theme'] * len(sub_themes)
    
    # Generate TF-IDF vectors for all texts
    vectorizer = TfidfVectorizer().fit_transform(all_texts)
    vectors = vectorizer.toarray()
    
    # Calculate cosine similarity matrix
    cosine_matrix = cosine_similarity(vectors)
    
    # Create nodes and edges based on similarity
    nodes = []
    edges = []
    
    # Define sizes and colors for different node types
    size_mapping = {'category': 30, 'theme': 20, 'sub_theme': 10}
    color_mapping = {'category': '#3a365c', 'theme': '#4b3b8f', 'sub_theme': '#a19cb1'}
    
    # Add nodes
    for i, text in enumerate(all_texts):
        node_type = all_labels[i]
        nodes.append(Node(id=f"{node_type}_{text}", label=text, size=size_mapping[node_type], color=color_mapping[node_type]))
    
    # Add edges based on similarity threshold (category > theme > sub_theme)
    num_categories = len(categories)
    num_themes = len(themes)
    
    for i in range(num_categories):
        for j in range(num_categories, num_categories + num_themes):
            if cosine_matrix[i][j] > threshold:
                source = f"category_{all_texts[i]}"
                target = f"theme_{all_texts[j]}"
                edges.append(Edge(source=source, target=target))
    
    for j in range(num_categories, num_categories + num_themes):
        for k in range(num_categories + num_themes, len(all_texts)):
            if cosine_matrix[j][k] > threshold:
                source = f"theme_{all_texts[j]}"
                target = f"sub_theme_{all_texts[k]}"
                edges.append(Edge(source=source, target=target))
    
    # Configuration of the graph
    config = Config(width=750,
                    height=750,
                    directed=False,
                    physics=True,
                    hierarchical=False)
    
    # Display the graph using streamlit-agraph
    return_value = agraph(nodes=nodes, edges=edges, config=config)

generate_similarity_graph(categories, themes, sub_themes, threshold=0.2)


import pandas as pd
from sklearn.manifold import TSNE
import numpy as np
from ast import literal_eval
import streamlit as st

# Load the embeddings
datafile_path = "Reviews.csv"
df = pd.read_csv(datafile_path)

# Convert to a list of lists of floats
matrix = np.array(df.embedding.apply(literal_eval).to_list())

# Create a t-SNE model and transform the data
tsne = TSNE(n_components=2, perplexity=15, random_state=42, init='random', learning_rate=200)
vis_dims = tsne.fit_transform(matrix)
vis_dims.shape

st.write(vis_dims)