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

def getMetrics(json):
    metrics = {}
    for key, value in json.items():
        if isinstance(value, dict) and "name" in value and "value" in value and "delta" in value:
            metrics[key] = value
    return metrics

def getBoxes(json):
    boxes = {}
    for key, value in json.items():
        if isinstance(value, dict) and "icon" in value and "label" in value and "value" in value and "type" in value:
            boxes[key] = value
    return boxes

def getProgress(json):
    progress = {}
    for key, value in json.items():
        if isinstance(value, dict) and "name" in value and "value" in value and not "delta" in value:
            progress[key] = value
    return progress