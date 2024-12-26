import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix,classification_report
from sklearn.ensemble import ExtraTreesClassifier

os.chdir("./datos")


def file2sentences(filename):
  txt = ""

  with open(filename,"r",encoding="utf-8") as f:
    txt = f.read()

  txt = txt.replace("?",".")
  txt = txt.replace("!",".")
  txt = txt.replace("»","")
  txt = txt.replace("«","")
  txt = txt.replace(":","")
  txt = txt.replace(";","")
  txt = txt.replace("...",".")
  txt = txt.replace("…",".")
  txt = txt.replace("\n",".")
  txt = txt.replace("  "," ")
  txt = txt.replace("“","")
  txt = txt.replace("„","")
  txt = txt.replace("”","")

  sentences = txt.split(".")

  for i in range(len(sentences)):
    sentences[i] = sentences[i].strip()

  sentences = [x for x in sentences if x != ""]

  return sentences


spanish = file2sentences("espanol.txt")
english = file2sentences("ingles.txt")

spanish[100:110]

X = np.array(spanish + english)
y = np.array(['es']*len(spanish) + ['en']*len(english) )

X.shape

df = pd.DataFrame({'sentence':X,'language':y})

df.sample(20)

df['language'].value_counts().plot(kind = 'bar')

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)

cnt = CountVectorizer(analyzer = 'char',ngram_range=(2,2),binary=True)

cnt.fit(X_train)

len(cnt.get_feature_names_out())

model = LogisticRegression()

model.fit(cnt.transform(X_train),y_train)
y_pred = model.predict(cnt.transform(X_test))

confusion_matrix(y_test,y_pred)

print(classification_report(y_test,y_pred))

model.classes_

#prueba de español e ingles
test = [
("Hello, how are you?", 'English sentence'),
("See you tomorrow", 'English sentence'),
("I would like a dish of frijoles or even a good ensalada española", 'English sentence with Spanish words'),
("Ensalada or aguacate? I can't choose" , 'English sentence with many Spanish words'),
("hola, ¿cómo estás?", 'Spanish sentence'),
('Estamos de weekend', 'Spanish sentence with English word'),
('weekend', 'English word'),
('remote work', 'English expression'),
('universidad', 'Spanish word'),
('Que tengas un buen día', 'Spanish sentence'),
('bosque', 'Spanish word'),
('carro', 'Spanish word'),
('Haremos un buen trip al bosque', 'Spanish sentence with English word'),
('hyperparameters', 'English word not present in original corpus'),
('machine learning', 'English expression not present in original corpus '),
('I met Annalisa en Madrid and she told me she wanted una tortilla de patatas', 'English sentence with Spanish words'),
('I met Annalisa en Madrid and she told me she wanted una tortilla de patatas', 'English sentence with Spanish words'),
('Tengo que reparar mi avioneta', 'Spanish sentence'),
('I have to repair my airplane', 'English sentence')
        ]


pred = model.predict(cnt.transform([x[0] for x in test]))

for i in range(len(test)):
  print("Sentence: {}".format(test[i][0]))
  print("Comment: {}".format(test[i][1]))
  print("Predicted language: {}".format(pred[i]))
  print("-----------------------")

# Guardar modelo
with open("modelo_lang_detector.pkl","wb") as f:
  pickle.dump(model,f)

### Esto usarlo en otro archivo para usar el modelo ---------------------------------------------
# Cargar modelo
with open("modelo_lang_detector.pkl","rb") as f:
  model = pickle.load(f)

# probar modelo y guardar la prediccion en una variable
prediccion = model.predict(cnt.transform(["I have to repair my airplane"]))
prediccion2 = model.predict(cnt.transform(["Hola mucho gusto"]))

print(prediccion)
print(prediccion2)