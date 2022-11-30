import pickle

import requests

with open("credentials.pickle", "rb") as f:
    try:
        while True:
            d = pickle.load(f)
            if d["credtype"] == "oxfordapi":
                app_id = d["app_id"]
                app_key = d["app_key"]
    except EOFError:
        pass

language = "en-us"


def defnsyn(w):
    url = (
        r"https://od-api.oxforddictionaries.com:443/api/v2/entries/"
        + language
        + "/"
        + w.lower()
    )
    r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})
    if r.status_code != 200:
        return None, None
    res = r.json()
    s1 = res["results"][0]["lexicalEntries"]
    lexicalCategories = []
    synonyms = []
    defn = ""
    try:
        if len(s1) > 1:
            for i in range(len(s1)):
                lexicalCategories.append(s1[i]["lexicalCategory"]["id"])
            if "verb" in lexicalCategories:
                baseindex = s1[lexicalCategories.index("verb")]["entries"][0]["senses"][
                    0
                ]
                defn = baseindex["shortDefinitions"][0]
                if "synonyms" in baseindex:
                    no = (
                        2
                        if len(baseindex["synonyms"]) > 3
                        else len(baseindex["synonyms"])
                    )
                    while no:
                        synonyms.append(baseindex["synonyms"][no]["text"])
                        no -= 1
                    synonyms.reverse()
            elif "noun" in lexicalCategories:
                baseindex = s1[lexicalCategories.index("noun")]["entries"][0]["senses"][
                    0
                ]
                defn = baseindex["shortDefinitions"][0]
                if "synonyms" in baseindex:
                    no = (
                        3
                        if len(baseindex["synonyms"]) > 3
                        else len(baseindex["synonyms"])
                    )
                    while no:
                        synonyms.append(baseindex["synonyms"][no]["text"])
                        no -= 1
                    synonyms.reverse()
            else:
                baseindex = s1[0]["entries"][0]["senses"][0]
                defn = baseindex["shortDefinitions"][0]
                if "synonyms" in baseindex:
                    no = (
                        3
                        if len(baseindex["synonyms"]) > 3
                        else len(baseindex["synonyms"])
                    )
                    while no:
                        synonyms.append(baseindex["synonyms"][no]["text"])
                        no -= 1
                    synonyms.reverse()
        else:
            baseindex = s1[0]["entries"][0]["senses"][0]
            defn = baseindex["shortDefinitions"][0]
            if "synonyms" in baseindex:
                no = 3 if len(baseindex["synonyms"]) > 3 else len(baseindex["synonyms"])
                while no:
                    synonyms.append(baseindex["synonyms"][no]["text"])
                    no -= 1
                synonyms.reverse()
    except:
        print("err")
        defn = synonyms = ""
    return defn, synonyms
