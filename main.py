from fastapi import FastAPI, WebSocket, UploadFile, File, WebSocketDisconnect
from fastapi.responses import JSONResponse
import os
import shutil
import zipfile
import uuid
import json
import io
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
TEMP_DIR = "temp_ws"
os.makedirs(TEMP_DIR, exist_ok=True)

# ----------------------------
# Route 1: GET Zip by docId
# ----------------------------
@app.get("/get-zip/{doc_id}")
async def get_zip(doc_id: str):
    zip_path = os.path.join(TEMP_DIR, f"{doc_id}.zip")
    if not os.path.exists(zip_path):
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(zip_path, media_type="application/zip", filename=f"{doc_id}.zip")

# ----------------------------
# Route 2: POST Zip → JSON
# ----------------------------
@app.post("/upload-zip-json")
async def upload_zip_json(file: UploadFile = File(...)):
    file_bytes = await file.read()
    zip_io = io.BytesIO(file_bytes)
    with zipfile.ZipFile(zip_io) as z:
        file_list = z.namelist()
    return {"files": file_list, "total": len(file_list)}


# --- POST: Upload zip and return session_id ---
@app.post("/upload-zip-start")
async def upload_zip_start(file: UploadFile = File(...)):
    file_bytes = await file.read()
    session_id = str(uuid.uuid4())
    print(session_id)
    extract_path = os.path.join(TEMP_DIR, session_id)
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
        z.extractall(extract_path)

    extracted_files = []
    for root, _, files in os.walk(extract_path):
        for name in files:
            rel_path = os.path.relpath(os.path.join(root, name), extract_path)
            extracted_files.append(rel_path)

    return {"session_id": session_id, "files": extracted_files, "total": len(extracted_files)}

# --- WS: Stream JSON + Files ---
@app.websocket("/ws/stream/{session_id}")
async def websocket_stream(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print("ws : ",session_id)
    folder_path = os.path.join(TEMP_DIR, session_id)
    if not os.path.exists(folder_path):
        await websocket.send_text(json.dumps({"error": "Invalid session_id"}))
        await websocket.close()
        return

    try:
        # Step 1: Send JSON metadata
        extracted_files = []
        for root, _, files in os.walk(folder_path):
            for name in files:
                rel_path = os.path.relpath(os.path.join(root, name), folder_path)
                extracted_files.append(rel_path)

        metadata = {"type": "metadata", "files": extracted_files, "total": len(extracted_files)}
        await websocket.send_text(json.dumps(metadata))

        # Step 2: Stream each file one by one (base64 encoded for binary-safe transfer)
        for rel_path in extracted_files:
            full_path = os.path.join(folder_path, rel_path)
            with open(full_path, "rb") as f:
                file_content = f.read()

            await websocket.send_json({
                "type": "file",
                "filename": rel_path,
                "content": file_content.decode('latin1')  # Keep binary-safe for demo
            })

        await websocket.send_text(json.dumps({"type": "done"}))
    except WebSocketDisconnect:
        print(f"Client disconnected from session {session_id}")
    finally:
        shutil.rmtree(folder_path, ignore_errors=True)
