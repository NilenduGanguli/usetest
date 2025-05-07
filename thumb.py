from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import base64

app = FastAPI()

# Mount the static directory to serve the HTML page
app.mount("/static", StaticFiles(directory="static"), name="static")

# Directory containing the files
FILES_DIR = "files"
THUMBNAILS_DIR = os.path.join(FILES_DIR, "thumbnails")

@app.get("/api/files")
async def get_files():
    files_data = {}

    # Iterate over files in the FILES_DIR
    for filename in os.listdir(FILES_DIR):
        file_path = os.path.join(FILES_DIR, filename)

        # Skip if it's a directory (e.g., the thumbnails directory)
        if os.path.isdir(file_path):
            continue

        # Read and encode the file content
        with open(file_path, "rb") as f:
            file_content = f.read()
            file_base64 = base64.b64encode(file_content).decode('utf-8')

        # Construct the thumbnail path
        thumbnail_filename = os.path.splitext(filename)[0] + ".jpg"
        thumbnail_path = os.path.join(THUMBNAILS_DIR, thumbnail_filename)

        # Read and encode the thumbnail if it exists
        if os.path.exists(thumbnail_path):
            with open(thumbnail_path, "rb") as thumb:
                thumbnail_content = thumb.read()
                thumbnail_base64 = base64.b64encode(thumbnail_content).decode('utf-8')
        else:
            thumbnail_base64 = None  # Or set a default image

        # Add the file data to the dictionary
        files_data[filename] = {
            "filename": filename,
            "file_relative_path": os.path.relpath(file_path, start=FILES_DIR),
            "file_binary": file_base64,
            "file_thumbnail": thumbnail_base64
        }

    return JSONResponse(content=files_data)
