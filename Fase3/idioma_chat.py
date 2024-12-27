import pickle
from deep_translator import GoogleTranslator

def detectar_lang(texto):

    # Cargar el modelo y vectorizador desde el archivo .pkl
    with open(r"datos\modelo_lang_detector.pkl", "rb") as f:
        saved_model = pickle.load(f)
        model = saved_model['model']
        vectorizer = saved_model['vectorizer']

    # Probar el modelo con frases nuevas
    prediccion = model.predict(vectorizer.transform([texto]))
    return prediccion[0]


def traductor(texto, idioma_destino):
    return GoogleTranslator(source='auto', target=idioma_destino).translate(texto)


def traducir(texto):
    lang=detectar_lang(texto)
    lg= "en" if lang=="es" else "es"
    return traductor(texto, lg)
