import re
import json
import streamlit as st

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

def flatten_json(nested_json: dict, exclude: list=[''], sep: str='-') -> dict:
    """
    Flatten a list of nested dicts.
    """
    out = dict()
    def flatten(x: (list, dict, str), name: str='', exclude=exclude):
        if type(x) is dict:
            for a in x:
                if a not in exclude:
                    flatten(x[a], f'{name}{a}{sep}')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, f'{name}{i}{sep}')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out


def extract_json_structure(data):
    if isinstance(data, dict):
        return {key: extract_json_structure(value) for key, value in data.items()}
    elif isinstance(data, list):
        if len(data) > 0:
            return [extract_json_structure(data[0])]
        else:
            return []
    else:
        return type(data).__name__
    


def formalize_messages(json_input):
    formatted_output = []
    for entry in json_input:
        if entry['role'] == 'user':
            formatted_output.append(f"User:\n{entry['content']}\n\n")
        elif entry['role'] == 'assistant':
            formatted_output.append(f"Assistant:\n{entry['content']}\n\n")
    
    return ''.join(formatted_output)