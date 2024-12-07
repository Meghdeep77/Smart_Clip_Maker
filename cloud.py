from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse,RedirectResponse
from fastapi.staticfiles import StaticFiles
import VidApi
import json
import os
import shutil
progress_file = "progress.json"

app = FastAPI()
app.mount("/Templates", StaticFiles(directory="./Templates"), name="Templates")

def clear_folder(folder_path: str):
    """
    Deletes all files in the specified folder.
    If the folder doesn't exist, it will be created.
    """
    if os.path.exists(folder_path):
        # Remove all files and subfolders
        shutil.rmtree(folder_path)
    # Recreate the folder to ensure it's empty
    os.makedirs(folder_path)
def update_progress(status: str):
    try:
        with open(progress_file, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    data["status"] = status  # Directly update the top-level key

    with open(progress_file, "w") as file:
        json.dump(data, file)

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("Templates/Home.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

@app.post("/update")
async def create_clips(video_url: str = Form(...)):
    clear_folder("Final_OGdim")
    clear_folder("Final_Resize")
    update_progress("Started")
    videdit = VidApi.VideoClip(video_url,100)
    videdit.get_video_clip()
    VidApi.create_zip_file('Final_OGdim')
    VidApi.create_zip_file('Final_Resize')
    update_progress("Finished")
    return RedirectResponse(url="/completed", status_code=303)


@app.get("/progress", response_class=JSONResponse)
async def progress():
    try:
        with open(progress_file, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"status": "Unknown"}  # Default fallback
    return JSONResponse(content=data)

@app.get("/completed", response_class=HTMLResponse)
async def completed():
    try:
        with open("Templates/Completed.html", "r") as file:
            html_content = file.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

@app.get("/download/original")
def download_original():
    """
    Endpoint to download the ZIP file containing video clips in original dimensions.
    """
    file_path = "Final_OGdim.zip"  # Replace with the actual path to the original ZIP file
    return FileResponse(
        path=file_path,
        media_type="application/zip",
        filename="Original_Dimensions.zip"
    )

@app.get("/download/shorts")
def download_shorts():
    """
    Endpoint to download the ZIP file containing shorts-compatible video clips.
    """
    file_path = "Final_Resize.zip"  # Replace with the actual path to the shorts-compatible ZIP file
    return FileResponse(
        path=file_path,
        media_type="application/zip",
        filename="Shorts_Compatible.zip"
    )