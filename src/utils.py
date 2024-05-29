import re
import json


def describe_content(value, indent=0):
    indent_str = '  ' * indent 
    if isinstance(value, str):
        return f"{indent_str}{value}"
    elif isinstance(value, list):
        return ', '.join(f"{indent_str}- {describe_content(item, indent + 1)}" for item in value)
    elif isinstance(value, dict):
        return '\n'.join(f"{indent_str}{key}:\n{describe_content(val, indent + 1)}" for key, val in value.items())
    else:
        return f"{indent_str}{str(value)}"
    
def format_date_range(conversationDateRange):
    from_date = conversationDateRange["from"].split("T")[0]
    to_date = conversationDateRange["to"].split("T")[0]
    return f"{from_date} - {to_date}"

def details_to_string(details):
    try:
        return f"{details['short_value']}: \n{details['longer_value']} \n({details['justification']}) \n<{details['score']}>"
    except KeyError:
        return describe_content(details)
    
def extract_json_object(response):
    json_object = re.search(r"\{.*\}", response, re.DOTALL)
    return json.loads(json_object.group(0))


# ```json
# {
#    "issue_summary":(string),
#    "conversation_objective":(string),
#    "context_of_request":(string),
#    "language_and_tone":("formal"|"informal"|"colloquial"|"slang"|"jargon"|"vulgar"|"standard"|"literary"|"technical"),
#    "client_communication_preferences":("email"|"phone calls"|"in-person"|"text messages"|"social media"|"customer support"|"agent ai"),
#    "client_expectations":({name:(string name for the metric), value:("low"|"standard"|"hight"),delta:(average number of expectations between 0 and 100)}),
#    "client_sentiment":({name:(string name for the metric), value:("positive"|"constructive"|"negative"|"neutral"),delta:(average number of satisfaction between -100 and 100)}),
#    "service_quality":({name:(string name for the metric), value:("Very Poor"|"Poor"|"Fair"|"Good"|"Excellent"),delta:(average number of questions correctly answered between 0 and 100)}),
#    "request_complexity_level":({name:(string name for the metric), value:("low"|"standard"|"hight"),delta:(average number of complexity between 0 and 100)}),
#    "situation_sensitivity":({name:(string name for the metric), value:("low"|"standard"|"hight"),delta:(average number of sensitivity between 0 and 100)}),
#    "request_urgency_level":({name:(string name for the metric), value:("low"|"standard"|"hight"),delta:(average number of urgency between 0 and 100)}),
#    "assistant_knowledge_gap":({name:(string name for the metric), value:("never"|"rarely"|"seldom"|"occasionaly"|"sometimes"|"ofthen"|"frequently"|"usualy"|"always"),delta:(average number of gap between 0 and 100)}),
#    "proposed_solutions_relevance":({name:(string name for the metric), value:("Very Poor"|"Poor"|"Fair"|"Good"|"Excellent"),delta:(average number of relevant solutions between -100 and 100)}),
#    "solutions_adaptability":({name:(string name for the metric), value:("Very Poor"|"Poor"|"Fair"|"Good"|"Excellent"),delta:(average number of adapted solutions between -100 and 100)}),
#    "confidentiality_level":({name:(string name for the metric), value:("low"|"standard"|"hight"),delta:(average number of confidentiality level between 0 and 100)}),
#    "issue_identification_ability":({name:(string name for the metric), value:("Very Poor"|"Poor"|"Fair"|"Good"|"Excellent"),delta:(average number of identificated issue between 0 and 100)}),
#    "use_of_customer_data":({name:(string name for the metric), value:("never"|"rarely"|"seldom"|"occasionaly"|"sometimes"|"ofthen"|"frequently"|"usualy"|"always"),delta:(average number of use of user data between 0 and 100)}),
#    "necessary_follow_up":(boolean),
#    "agent_empathetic_approach_use":({name:(string name for the metric), value:("Very Poor"|"Poor"|"Fair"|"Good"|"Excellent"),delta:(average number of empathetic approach quality between -100 and 100)}),
#    "identified_risks":(array of potential risks),
#    "possible_solutions":(array of potential solutions),
#    "negative_publicity_risk":({name:(string name for the metric), value:("low"|"standard"|"hight"),delta:(average chance of negative publicity between 0 and 100)}),
#    "keywords":(array of keywords),   
#    "user_intentions":(array of intentions),
#    "response_accuracy":({name:(string name for the metric), value:("low"|"standard"|"hight"),delta:(average response accuracy between 0 and 100)}),
#    "problem_resolution_rate":({name:(string name for the metric), value:("number of problems/number of resolution"),delta:(average problem resolution rate between 0 and 100)}),
#    "commercial_opportunities":({name:(string name for the metric), value:("low"|"standard"|"hight"),delta:(average chance of commercial opportunities between 0 and 100)}),,
# }
# ```

# check if insights has a name a value and a delta and return all the insights that have those
def filter_insights(data):
    insights = []
    for insight in data:
        if 'name' in insight and 'value' in insight and 'delta' in insight:
            insights.append(insight)
    return insights