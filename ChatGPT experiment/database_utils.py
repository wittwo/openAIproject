from typing import Any, Dict
import requests
import os
from Secrets import DATABASE_INTERFACE_BEARER_TOKEN

SEARCH_TOP_K = 1


def upsert_file(directory: str):
    """
    Upload all files under a directory to the vector database.
    """
    url = "http://localhost:8000/upsert-file"
    headers = {"Authorization": "Bearer " + DATABASE_INTERFACE_BEARER_TOKEN}
    files = []
    for filename in os.listdir(directory):
        
        if os.path.isfile(os.path.join(directory, filename)):
            
            file_path = os.path.join(directory, filename)
            with open(file_path, "rb") as f:
                
                file_content = f.read()
                files.append(("file", (filename, file_content, "text/plain")))
                
            response = requests.post(url,
                                     headers=headers,
                                     files=files,
                                     timeout=600)
            
            if response.status_code == 200:
                print(filename + " uploaded successfully.")
            else:
                print(
                    f"Error: {response.status_code} {response.content} for uploading "
                    + filename)


def upsert(id: str, content: str):
    """
    Upload one piece of text to the database.
    """
    url = "http://localhost:8000/upsert"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + DATABASE_INTERFACE_BEARER_TOKEN,
    }

    data = {
        "documents": [{
            "id": id,
            "text": content,
        }]
    }
    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        print("uploaded successfully.")
    else:
        print(f"Error: {response.status_code} {response.content}")


def query_database(query_prompt: str) -> Dict[str, Any]:
    """
    Query vector database to retrieve chunk with user's input question.
    """
    url = "http://localhost:8000/query"
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {DATABASE_INTERFACE_BEARER_TOKEN}",
    }
    data = {"queries": [{"query": query_prompt, "top_k": SEARCH_TOP_K}]}

    response = requests.post(url, json=data, headers=headers, timeout=600)

    if response.status_code == 200:
        result = response.json()
        # process the result
        return result
    else:
        raise ValueError(f"Error: {response.status_code} : {response.content}")


if __name__ == "__main__":
    upsert_file("C:\Python\AI\Pine\A\Data")
    #upsert("Karolina Hayduchyk","""Karolina Hayduchyk (Web&Graphic Designer): "Cześć, cieszę się, że mogłam zostać częścią waszego zespołu!

#Więc coś o mnie….ukończyłam Wzornictwo Przemysłowe, ale moje serce zabiło mocniej do wymiaru 2D, dlatego zostałam przy szeroko pojętych obrazkach.

#Na co dzień uwielbiam tworzyć ilustracje, przede wszystkim te dla dzieci. Mam przyjemność tworzyć z polskimi firmami wzory na tkaniny, kartki na urodzinki i wiele innych fajnych rzeczy. Więc w skrócie kocham rysować!

#Poza tym jestem wielbicielką leśnych spacerów i obserwacji pszczół. Pszczoły mają szczególne miejsce w moim sercu, tuż obok piesków, kaczek i muchomorów.""")