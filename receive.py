import requests

with open("example.zip", "rb") as f:
    files = {'file': ('example.zip', f, 'application/zip')}
    response = requests.post("http://localhost:8000/upload-zip-files", files=files)

with open("response.eml", "wb") as out:
    out.write(response.content)
