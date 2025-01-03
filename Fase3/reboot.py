import os

files_to_delete = ["chat_data_user.csv", "tfidf_vectorizer.pkl"]

for file in files_to_delete:
    if os.path.exists(file):
        os.remove(file)
        print(f"{file} ha sido eliminado.")
    else:
        print(f"{file} no existe.")