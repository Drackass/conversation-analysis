import json
import re

def verifyStructureTable(df, required_columns):
    return all(column in df.columns for column in required_columns)

def extractStructureTypesFromObject(data):
    if isinstance(data, dict):
        return {key: extractStructureTypesFromObject(value) for key, value in data.items()}
    elif isinstance(data, list):
        if len(data) > 0:
            return [extractStructureTypesFromObject(data[0])]
        else:
            return []
    else:
        return type(data).__name__
    
def flattenJson(nested_json: dict, exclude: list=[''], sep: str='-') -> dict:
    """
    Flatten a list of nested dicts.
    """
    out = dict()
    def flatten(x: (list, dict, str), name: str='', exclude=exclude): # type: ignore
        if type(x) is dict:
            for a in x:
                if a not in exclude:
                    flatten(x[a], f'{name}{a}{sep}')
        elif type(x) is list:
            out[name[:-1]] = "- " + "\n- ".join(str(item) for item in x)
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out

def extractJsonObjectFromText(response):
    json_object = re.search(r"\{.*\}", response, re.DOTALL)
    if json_object is not None:
        return json.loads(json_object.group(0))
    else:
        return None