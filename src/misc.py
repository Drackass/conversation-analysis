llmJson= {
  "résumé": "La conversation aborde le problème d'un client professionnel cherchant à mettre à jour les plaques d'immatriculation associées à ses badges de télépéage. Le client explique que l'option pour la mise à jour des plaques n'est pas disponible sur la page prévue pour les professionnels, ce qui suggère un besoin d'assistance personnalisée.",
  "catégorie": "Problème",
  "évaluation_precision_réponses": 8,
  "évaluation_pertinence_réponses": 7,
  "qualité_information_fournie": 8,
  "évaluation_richesse_réponses": 7,
  "redondance_information": "Pas de redondance observée, informations complémentaires fournies à chaque étape.",
  "proportion_réponses_renvoi_service_client": "20%",
  "évaluation_agressivité_client": {
    "score_agressivité": 1,
    "pourcentage_phrases_agressives": "0%"
  },
  "questions_sans_réponse": "10%",
  "personnalisation_conseils": 8,
  "résolution_complète_demande": {
    "score_résolution": 7,
    "éléments_amélioration": "Fournir des détails spécifiques sur où exactement la mise à jour peut être réalisée dans l'espace abonné pour les professionnels, et vérifier la mise à jour de l'interface utilisateur pour s'assurer que toutes les options nécessaires sont facilement accessibles."
  },
  "amélioration": {
    "formation_conseillers": [
      "Connaissance des différences dans les interfaces des utilisateurs professionnels et particuliers",
      "Formation sur des scénarios spécifiques aux professionnels pour offrir des solutions plus ciblées et précises"
    ],
    "personnalisation_suivi": [
      "Demander si le client a déjà tenté une mise à jour par d'autres moyens",
      "Expliquer pourquoi certaines options pourraient ne pas être visibles dans l'espace des professionnels"
    ],
    "interactions_positives_négatives": "100% d'interactions neutres à positives, aucune interaction négative détectée.",
    "engagement_suivi": "10%"
  }
}

llmFlatJson= {
  "conversation_category": "Réassurance",
  "client_intention": "Le client souhaite ajouter / mettre à jour les plaques d'immatriculation associées à ses badges de télépéage et recherche des informations pour le faire.",
  "theme": "Gestion des plaques d'immatriculation pour les badges de télépéage",
  "noteworthy_elements_client_needs": "Instructions pour mettre à jour les plaques d'immatriculation sur un badge de télépéage.",
  "noteworthy_elements_service_improvement": "Manque de clarté sur le processus spécifique pour les clients professionnels sur le site web, nécessitant une intervention du service client.",
  "noteworthy_elements_client_frustration": "Le client est confus et légèrement frustré car il ne trouve pas l'option pour mettre à jour les plaques sur le site, en particulier pour les comptes professionnels.",
  "response_accuracy_evaluation_method": "scale_1_to_10",
  "response_accuracy_evaluation_score": 7,
  "response_relevance_evaluation_method": "scale_1_to_10",
  "response_relevance_evaluation_score": 7,
  "information_quality_method": "scale_1_to_10",
  "information_quality_score": 6,
  "information_quality_completeness": "La réponse manque de details spécifiques pour les professionnels, ce qui n'est adapté qu'à des clients généraux jusqu’à ce que le problème spécifique soit mentionné.",
  "response_richness_evaluation_method": "scale_1_to_10",
  "response_richness_evaluation_score": 5,
  "redundant_information": "Les étapes initiales fournies étaient génériques et non adaptées aux professionnels, menant à une redondance dans le processus d'assistance.",
  "website_referral_rate": "50%",
  "client_aggressiveness_evaluation_method": "scale_1_to_10",
  "client_aggressiveness_evaluation_score": 2,
  "client_aggressiveness_evaluation_percentage": 10,
  "unanswered_questions_rate_percentage": 20,
  "advice_personalization_method": "scale_1_to_10",
  "advice_personalization_score": 6,
  "advice_personalization_customization_level": "Generic initial advice, adjusted only after client specifies the professional account issue.",
  "client_demand_resolution_method": "scale_1_to_10",
  "client_demand_resolution_score": 6,
  "client_demand_resolution_needed_elements_for_improvement_0": "Detailed instructions for professionals right from the start",
  "client_demand_resolution_needed_elements_for_improvement_1": "Direct links or clearer navigation paths for professionals on the website",
  "client_demand_resolution_needed_elements_for_improvement_2": "Immediate acknowledgment of different processes for professional accounts in the initial response",
  "counselor_training_knowledge_elements_for_improvement_0_topic": "Understanding the professional accounts management on the website",
  "counselor_training_knowledge_elements_for_improvement_0_importance": 1,
  "counselor_training_knowledge_elements_for_improvement_1_topic": "Immediate identification of client type (professional or personal) in queries",
  "counselor_training_knowledge_elements_for_improvement_1_importance": 2,
  "counselor_training_knowledge_elements_for_improvement_2_topic": "Direct communication techniques to clarify client needs",
  "counselor_training_knowledge_elements_for_improvement_2_importance": 3,
  "personalization_and_follow_up_questions_for_better_understanding_0": "Are there any particular requirements or configurations for your professional account that I should be aware of?",
  "personalization_and_follow_up_questions_for_better_understanding_1": "Would you like a step-by-step walkthrough right now over the phone or a direct link to the specific section for professional account management?",
  "personalization_and_follow_up_questions_for_better_understanding_2": "Is there anything else related to your telepeage badges that needs updating?",
  "personalization_and_follow_up_missing_knowledge": "Specific navigation and options available in professional accounts for updating information.",
  "positive_negative_interactions_percentage_positive_interactions": 70,
  "positive_negative_interactions_percentage_negative_interactions": 30,
  "engagement_and_follow_up_percentage": 40
}

# llmJson= {
#   "conversation_category": "Réassurance",
#   "client_intention": "Le client souhaite ajouter / mettre à jour les plaques d'immatriculation associées à ses badges de télépéage et recherche des informations pour le faire.",
#   "theme": "Gestion des plaques d'immatriculation pour les badges de télépéage",
#   "noteworthy_elements": {
#     "client_needs": "Instructions pour mettre à jour les plaques d'immatriculation sur un badge de télépéage.",
#     "service_improvement": "Manque de clarté sur le processus spécifique pour les clients professionnels sur le site web, nécessitant une intervention du service client.",
#     "client_frustration": "Le client est confus et légèrement frustré car il ne trouve pas l'option pour mettre à jour les plaques sur le site, en particulier pour les comptes professionnels."
#   },
#   "response_accuracy_evaluation": {
#     "method": "scale_1_to_10",
#     "score": 7
#   },
#   "response_relevance_evaluation": {
#     "method": "scale_1_to_10",
#     "score": 7
#   },
#   "information_quality": {
#     "method": "scale_1_to_10",
#     "score": 6,
#     "completeness": "La réponse manque de details spécifiques pour les professionnels, ce qui n'est adapté qu'à des clients généraux jusqu’à ce que le problème spécifique soit mentionné."
#   },
#   "response_richness_evaluation": {
#     "method": "scale_1_to_10",
#     "score": 5
#   },
#   "redundant_information": "Les étapes initiales fournies étaient génériques et non adaptées aux professionnels, menant à une redondance dans le processus d'assistance.",
#   "website_referral_rate": "50%",
#   "client_aggressiveness_evaluation": {
#     "method": "scale_1_to_10",
#     "score": 2,
#     "percentage": 10
#   },
#   "unanswered_questions_rate": {
#     "percentage": 20
#   },
#   "advice_personalization": {
#     "method": "scale_1_to_10",
#     "score": 6,
#     "customization_level": "Generic initial advice, adjusted only after client specifies the professional account issue."
#   },
#   "client_demand_resolution": {
#     "method": "scale_1_to_10",
#     "score": 6,
#     "needed_elements_for_improvement": [
#       "Detailed instructions for professionals right from the start",
#       "Direct links or clearer navigation paths for professionals on the website",
#       "Immediate acknowledgment of different processes for professional accounts in the initial response"
#     ]
#   },
#   "counselor_training": {
#     "knowledge_elements_for_improvement": [
#       {
#         "topic": "Understanding the professional accounts management on the website",
#         "importance": 1
#       },
#       {
#         "topic": "Immediate identification of client type (professional or personal) in queries",
#         "importance": 2
#       },
#       {
#         "topic": "Direct communication techniques to clarify client needs",
#         "importance": 3
#       }
#     ]
#   },
#   "personalization_and_follow_up": {
#     "questions_for_better_understanding": [
#       "Are there any particular requirements or configurations for your professional account that I should be aware of?",
#       "Would you like a step-by-step walkthrough right now over the phone or a direct link to the specific section for professional account management?",
#       "Is there anything else related to your telepeage badges that needs updating?"
#     ],
#     "missing_knowledge": "Specific navigation and options available in professional accounts for updating information."
#   },
#   "positive_negative_interactions": {
#     "percentage_positive_interactions": 70,
#     "percentage_negative_interactions": 30
#   },
#   "engagement_and_follow_up": {
#     "percentage": 40
#   }
# }

# llmFlatJson= {
#   "conversation_category": "Réassurance",
#   "client_intention": "Le client souhaite ajouter / mettre à jour les plaques d'immatriculation associées à ses badges de télépéage et recherche des informations pour le faire.",
#   "theme": "Gestion des plaques d'immatriculation pour les badges de télépéage",
#   "noteworthy_elements_client_needs": "Instructions pour mettre à jour les plaques d'immatriculation sur un badge de télépéage.",
#   "noteworthy_elements_service_improvement": "Manque de clarté sur le processus spécifique pour les clients professionnels sur le site web, nécessitant une intervention du service client.",
#   "noteworthy_elements_client_frustration": "Le client est confus et légèrement frustré car il ne trouve pas l'option pour mettre à jour les plaques sur le site, en particulier pour les comptes professionnels.",
#   "response_accuracy_evaluation_method": "scale_1_to_10",
#   "response_accuracy_evaluation_score": 7,
#   "response_relevance_evaluation_method": "scale_1_to_10",
#   "response_relevance_evaluation_score": 7,
#   "information_quality_method": "scale_1_to_10",
#   "information_quality_score": 6,
#   "information_quality_completeness": "La réponse manque de details spécifiques pour les professionnels, ce qui n'est adapté qu'à des clients généraux jusqu’à ce que le problème spécifique soit mentionné.",
#   "response_richness_evaluation_method": "scale_1_to_10",
#   "response_richness_evaluation_score": 5,
#   "redundant_information": "Les étapes initiales fournies étaient génériques et non adaptées aux professionnels, menant à une redondance dans le processus d'assistance.",
#   "website_referral_rate": "50%",
#   "client_aggressiveness_evaluation_method": "scale_1_to_10",
#   "client_aggressiveness_evaluation_score": 2,
#   "client_aggressiveness_evaluation_percentage": 10,
#   "unanswered_questions_rate_percentage": 20,
#   "advice_personalization_method": "scale_1_to_10",
#   "advice_personalization_score": 6,
#   "advice_personalization_customization_level": "Generic initial advice, adjusted only after client specifies the professional account issue.",
#   "client_demand_resolution_method": "scale_1_to_10",
#   "client_demand_resolution_score": 6,
#   "client_demand_resolution_needed_elements_for_improvement_0": "Detailed instructions for professionals right from the start",
#   "client_demand_resolution_needed_elements_for_improvement_1": "Direct links or clearer navigation paths for professionals on the website",
#   "client_demand_resolution_needed_elements_for_improvement_2": "Immediate acknowledgment of different processes for professional accounts in the initial response",
#   "counselor_training_knowledge_elements_for_improvement_0_topic": "Understanding the professional accounts management on the website",
#   "counselor_training_knowledge_elements_for_improvement_0_importance": 1,
#   "counselor_training_knowledge_elements_for_improvement_1_topic": "Immediate identification of client type (professional or personal) in queries",
#   "counselor_training_knowledge_elements_for_improvement_1_importance": 2,
#   "counselor_training_knowledge_elements_for_improvement_2_topic": "Direct communication techniques to clarify client needs",
#   "counselor_training_knowledge_elements_for_improvement_2_importance": 3,
#   "personalization_and_follow_up_questions_for_better_understanding_0": "Are there any particular requirements or configurations for your professional account that I should be aware of?",
#   "personalization_and_follow_up_questions_for_better_understanding_1": "Would you like a step-by-step walkthrough right now over the phone or a direct link to the specific section for professional account management?",
#   "personalization_and_follow_up_questions_for_better_understanding_2": "Is there anything else related to your telepeage badges that needs updating?",
#   "personalization_and_follow_up_missing_knowledge": "Specific navigation and options available in professional accounts for updating information.",
#   "positive_negative_interactions_percentage_positive_interactions": 70,
#   "positive_negative_interactions_percentage_negative_interactions": 30,
#   "engagement_and_follow_up_percentage": 40
# }

dummyReport='''# Customer Service Analysis Report

## Conversation Summary
The conversation addresses a professional client's issue with updating the license plates associated with their telepeage badges. The client explains that the option to update the plates is not available on the page designed for professionals, indicating a need for personalized assistance.

## Customer Evaluation
- **Precision of Responses:** 8
- **Relevance of Responses:** 7
- **Quality of Provided Information:** 8
- **Richness of Responses:** 7

## Interaction Details
- **Redundant Information:** No observed redundancy, additional information provided at each step.
- **Unanswered Questions:** 10%
- **Response Referral to Customer Service:** 20%
- **Client Aggressiveness Evaluation:**
  - Score: 1
  - Percentage of Aggressive Phrases: 0%

## Resolution of Customer Request
- **Complete Resolution Score:** 7
- **Areas for Improvement:** Provide specific details on where the update can be done in the professional user space and ensure all necessary options are easily accessible on the user interface.

## Suggestions for Improvement
- **Advisor Training:**
  - Understanding the differences in professional and individual user interfaces.
  - Training on specific professional scenarios for more targeted and precise solutions.
- **Personalized Follow-Up:**
  - Inquire if the client has tried updating through other means.
  - Explain why certain options may not be visible in the professional space.
- **Positive/Negative Interactions:** 100% neutral to positive interactions, no negative interactions detected.
- **Follow-Up Engagement:** 10%

---
This report analyzes two customer service interactions with professional clients seeking assistance with updating license plates associated with telepeage badges. The clients highlighted the need for personalized support due to the unavailability of the update option on the designated professional page. The evaluation indicates areas of strength and improvement in responses, resolution quality, and suggestions for enhancing customer service experience.'''


jsonFilterTest= '''{
  "1": {
    "conversation_theme": "Information sur les services de gestion de projets",
    "client_intention": "Obtenir des informations sur les services de gestion de projets",
    "relevant_elements": "Les services offerts, les processus de gestion de projets, les tarifs, la dur\u00e9e du projet du client",
    "highlights": "Le client recherche des informations sur la gestion de projets pour un projet de d\u00e9veloppement logiciel de 6 mois",
    "pain_points": [],
    "conversation_category": "Opportunit\u00e9 commerciale",
    "evaluation": {
      "answer_accuracy_score": 9,
      "answer_relevance_score": 10,
      "information_quality_score": 9,
      "richness_of_answers_score": 8,
      "redundancy_of_information": "",
      "website_or_customer_service_redirect_proportion": 0,
      "client_aggressiveness_score": 0,
      "unanswered_questions_proportion": 0,
      "personalization_of_advice_score": 7,
      "resolution_completion_score": 8
    },
    "improvement_actions": {
      "training_for_advisors": [
        "Familiarit\u00e9 approfondie avec la tarification des projets de diff\u00e9rentes tailles et complexit\u00e9s."
      ],
      "personalization_and_follow_up": [
        "Poser des questions sp\u00e9cifiques pour mieux comprendre les besoins du client et personnaliser les recommandations."
      ],
      "positive_and_negative_interactions": {
        "positive_interaction_percentage": 100,
        "negative_interaction_percentage": 0
      },
      "engagement_and_follow_up": {
        "follow-up_percentage": 0
      }
    }
  },
  "2": {
    "conversation_theme": "Demande de devis pour un projet professionnel",
    "client_intention": "Obtenir des informations sur le devis pour le projet",
    "relevant_elements": "Le client demande un devis pour un projet professionnel et fournit son adresse email pour recevoir les d\u00e9tails.",
    "highlights": "Le client cherche des informations sur le co\u00fbt du projet et fournit son adresse email pour recevoir un devis. Le conseiller s'engage \u00e0 envoyer les informations demand\u00e9es et propose une ouverture pour d'autres questions. La conversation est courte et cordiale, se terminant par des remerciements de la part du client.",
    "pain_points": [],
    "conversation_category": "Opportunit\u00e9 commerciale",
    "evaluation": {
      "answer_accuracy_score": 8,
      "answer_relevance_score": 9,
      "information_quality_score": 8,
      "richness_of_answers_score": 7,
      "redundancy_of_information": "",
      "website_or_customer_service_redirect_proportion": 0,
      "client_aggressiveness_score": 0,
      "unanswered_questions_proportion": 0,
      "personalization_of_advice_score": 7,
      "resolution_completion_score": 9
    },
    "improvement_actions": {
      "training_for_advisors": [
        "Sensibilisation sur la personnalisation des r\u00e9ponses et la richesse des informations fournies.",
        "Formation sur la mani\u00e8re de proposer des sujets connexes pour approfondir l'interaction avec le client."
      ],
      "personalization_and_follow_up": [
        "Poser des questions cibl\u00e9es pour comprendre les besoins sp\u00e9cifiques du client et adapter les recommandations en cons\u00e9quence.",
        "Approfondir les connaissances sur les services offerts pour r\u00e9pondre de mani\u00e8re plus approfondie aux demandes des clients."
      ],
      "positive_and_negative_interactions": {
        "positive_interaction_percentage": 100,
        "negative_interaction_percentage": 0
      },
      "engagement_and_follow_up": {
        "follow-up_percentage": 0
      }
    }
  }
}'''