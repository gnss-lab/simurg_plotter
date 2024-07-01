import logging
import os
import uuid
from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
from fastapi.responses import FileResponse
from docker_manager import start_docker_container, get_container_progress, delete_container_and_progress, start_docker_container_for_intervals, count_images_in_directory, stop_and_clean_docker_containers
import requests
import aiohttp
import asyncio
import glob

from schemas.schemas import PlotRequest, TimeIntervalRequest, CheckRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This allows all origins. Change this in production.
    allow_credentials=True,
    allow_methods=["*"],  # This allows all methods (GET, POST, etc).
    allow_headers=["*"],  # This allows all headers.
)

logging.basicConfig(level=logging.INFO)

data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def checking_by_mail(mail: str):
    """ 
    Checking all accessible information about queries made by <mail>
    input - <mail> string type email address to check
    output - list of dictionaries with all information about every query
    """ 
    rq = requests.post("https://simurg.iszf.irk.ru/api", 
                        json={"method": "check", 
                              "args": {"email": mail}
                              }
                        )
    return rq.json()

async def download_file(url, save_path, progress_file):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            total = int(response.headers.get('content-length', 0))
            downloaded = 0
            with open(save_path, 'wb') as f:
                async for chunk in response.content.iter_chunked(8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    percent = int(downloaded / total * 100)
                    with open(progress_file, 'w') as pfile:
                        pfile.write(f'{percent}')
                    await asyncio.sleep(0)

            with open(progress_file, 'w') as pfile:
                pfile.write('100')
            os.remove(progress_file)

@app.get("/")
def read_root():
    return {"message": "Welcome to the random graph generator API"}

@app.post("/download_data_file/")
async def download_data_file(request: CheckRequest, background_tasks: BackgroundTasks):
    email = request.email
    url = request.url
    try:
        id_from_url = url.split('id=')[1]
    except IndexError:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    queries = checking_by_mail(email)

    matching_query = next((query for query in queries if query['id'] == id_from_url), None)

    if not matching_query:
        raise HTTPException(status_code=404, detail="Query with the specified ID not found")

    file_path = matching_query['paths'].get('data')

    if not file_path:
        raise HTTPException(status_code=404, detail="Data file not found in the query results")
    download_url = f"https://simurg.space/ufiles/{file_path}"
    save_directory = 'data'
    os.makedirs(save_directory, exist_ok=True)
    save_path = os.path.join(save_directory, os.path.basename(file_path))
    progress_file = os.path.join(save_directory, f'{id_from_url}.progress')
    background_tasks.add_task(download_file, download_url, save_path, progress_file)

    return {"message": "Download started", "file_name": os.path.basename(save_path)}


@app.get("/download_progress/")
async def get_progress(url: str):
    try:
        id_from_url = url.split('id=')[1]
    except IndexError:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    progress_file_path = os.path.join('data', f'{id_from_url}.progress')
    if os.path.exists(progress_file_path):
        with open(progress_file_path, 'r') as pfile:
            progress = pfile.read()
        if progress == '100':
            os.remove(progress_file_path)
        return {"progress": progress}
    else:
        return {"progress": "100"}

@app.post("/generate_plot/")
async def generate_plot(request: PlotRequest, background_tasks: BackgroundTasks):
    try:
        request_id = str(uuid.uuid4())
        output_file = f"{request.file_name}_{request_id}.png"
        plot_data = request.dict()
        plot_data_path = f"{data_dir}/{request.file_name}_{request_id}_data.json"
        
        with open(plot_data_path, 'w') as f:
            json.dump(plot_data, f)
        
        background_tasks.add_task(
            start_docker_container,
            height=request.height,
            dpi=request.dpi,
            output_file=output_file,
            request_id=request_id,
            plot_data_path=plot_data_path
        )

        return {"status": "success", "request_id": request_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_request_progress/")
def get_request_progress(request_id: str):
    progress = get_container_progress(request_id)
    return {"request_id": request_id, "progress": progress}

@app.get("/download_result/")
def download_result(request_id: str = None):
    if request_id:
        files = [f for f in os.listdir(data_dir) if f.endswith('.png') and request_id in f]

    if not files:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = f"{data_dir}/{files[0]}"
    delete_container_and_progress(request_id)

    logging.info(f"Downloading result for request_id={request_id}: {files[0]}")
    return FileResponse(path=file_path, filename=files[0], media_type='application/octet-stream')

@app.post("/generate_archive_and_animation/")
async def generate_archive_and_animation(request: TimeIntervalRequest, background_tasks: BackgroundTasks):
    try:
        request_id = str(uuid.uuid4())
        plot_data = request.plot_request.dict()
        plot_data_path = f"{data_dir}/{request.plot_request.file_name}_{request_id}_data.json"
        
        with open(plot_data_path, 'w') as f:
            json.dump(plot_data, f)
        
        background_tasks.add_task(
            start_docker_container_for_intervals,
            height=request.plot_request.height,
            dpi=request.plot_request.dpi,
            request_id=request_id,
            plot_data_path=plot_data_path,
            start_time=request.start_time,
            end_time=request.end_time,
            interval_seconds=request.interval_seconds
        )

        return {"status": "success", "request_id": request_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_archive_progress/")
async def get_archive_progress(request_id: str):
    try:
        progress_file = f"./data/{request_id}_total.json"
        with open(progress_file, 'r') as f:
            total_images = json.load(f)["total"]
        completed_images = 0

        num_intervals = 4 
        for i in range(num_intervals):
            interval_dir = f"{data_dir}/{request_id}_interval{i}_data"
            completed_images += count_images_in_directory(interval_dir)


        # Calculate progress percentage
        if total_images > 0:
            progress = int((completed_images / total_images) * 100)
        else:
            progress = 0

        return {"request_id": request_id, "progress": progress}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting archive progress: {str(e)}")

@app.get("/get_first_images/")
async def get_first_images(request_id: str):
    try:
        num_intervals = 4
        container_image_paths = []

        for i in range(num_intervals):
            interval_dir = f"data/{request_id}_interval{i}_data"
            interval_images = glob.glob(os.path.join(interval_dir, '*.png'))
            if interval_images:
                # Sort images to ensure consistent order (assuming names are in order or timestamped)
                interval_images.sort()
                first_image_path = interval_images[0]
                container_image_paths.append(first_image_path)

        if not container_image_paths:
            raise HTTPException(status_code=404, detail="No images found for the specified request_id")

        # Return the first images as downloadable files
        first_images = []
        for img_path in container_image_paths:
            first_images.append(FileResponse(path=img_path, filename=os.path.basename(img_path), media_type='image/png'))

        return first_images

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving first images: {str(e)}")

@app.get("/download_animation/")
async def download_animation(request_id: str):
    try:
        animation_file = f"data/{request_id}_animation.gif"

        if not os.path.exists(animation_file):
            raise HTTPException(status_code=404, detail="Animation file not found. Processing might still be ongoing.")

        # Return the animation file as a downloadable file
        return FileResponse(path=animation_file, filename=os.path.basename(animation_file), media_type='image/gif')

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving animation: {str(e)}")

@app.get("/download_images/")
async def download_images(request_id: str):
    try:
        zip_file = f"data/{request_id}_images.zip"

        if not os.path.exists(zip_file):
            raise HTTPException(status_code=404, detail="Image ZIP file not found. Processing might still be ongoing.")

        # Return the ZIP file as a downloadable file
        return FileResponse(path=zip_file, filename=os.path.basename(zip_file), media_type='application/zip')

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving images: {str(e)}")

@app.post("/stop_and_clean/")
def stop_and_clean(request_id: str):
    try:
        stop_and_clean_docker_containers(request_id)
        return {"status": "success", "message": f"Stopped and cleaned up containers for request_id={request_id}"}
    except Exception as e:
        logging.error(f"Error stopping and cleaning up containers for request_id={request_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))