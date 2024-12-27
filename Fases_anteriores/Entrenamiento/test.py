import pickle
from sklearn.feature_extraction.text import CountVectorizer

with open("datos\\modelo_lang_detector.pkl", "rb") as f:
    saved = pickle.load(f)
    model = saved['model']
    cnt = saved['vectorizer']

prediccion = model.predict(cnt.transform(["I have to repair my airplane"]))
prediccion2 = model.predict(cnt.transform(["tell me a joke"]))
prediccion3 = model.predict(cnt.transform(["hola, ¿cómo estás?"]))

print(prediccion)
print(prediccion2)
print(prediccion3)