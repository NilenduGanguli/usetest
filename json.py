from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from starlette.responses import Response
from io import BytesIO
import zipfile
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

app = FastAPI()

@app.get("/download-json-zip")
def download_json_and_zip():
    # Prepare JSON
    json_data = {"message": "This is the JSON part", "status": "success"}
    json_bytes = json.dumps(json_data).encode('utf-8')

    # Prepare ZIP in memory
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr("hello.txt", "This is a file inside the zip.")
    zip_buffer.seek(0)

    # Create multipart response using MultipartEncoder
    multipart_data = MultipartEncoder(
        fields={
            'metadata': ('metadata.json', json_bytes, 'application/json'),
            'archive': ('files.zip', zip_buffer, 'application/zip'),
        }
    )

    return StreamingResponse(multipart_data, media_type=multipart_data.content_type)
