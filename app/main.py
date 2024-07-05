import logging
import os
import uuid
from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi.responses import FileResponse
from docker_manager import start_docker_container, get_container_progress, delete_container_and_progress, start_docker_container_for_intervals, count_images_in_directory, stop_and_clean_docker_containers
import requests
import aiohttp
import asyncio
import glob
import unlzw3
import base64
import time

from schemas.schemas import PlotRequest, TimeIntervalRequest, MAP2DRequest, GIMRequest

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

import aiohttp
import os

async def download_file(url: str, save_path: str, progress_file: str):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60*60)) as session:  # Увеличиваем общий тайм-аут до 1 часа
            async with session.get(url) as response:
                response.raise_for_status()  # Проверяем успешность ответа

                total_size = int(response.headers.get('Content-Length', 0))
                downloaded_size = 0

                with open(save_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        progress = (downloaded_size / total_size) * 100
                        with open(progress_file, 'w') as pfile:
                            pfile.write(f'{int(progress)}')

    except aiohttp.ClientError as e:
        raise RuntimeError(f"Failed to download file: {e}")

    except asyncio.TimeoutError:
        raise RuntimeError("Download timed out")

    except Exception as e:
        raise RuntimeError(f"An error occurred: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the random graph generator API"}

async def download_gim_file(url, save_path, progress_file):
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


async def uncompress_file(z_path, extract_to, progress_file):
    try:
        with open(z_path, 'rb') as compressed_file, open(extract_to, 'wb') as uncompressed_file:
            uncompressed_file.write(unlzw3.unlzw(compressed_file.read()))
        
        with open(progress_file, 'w') as pfile:
            pfile.write('100')
        os.remove(progress_file)
    except Exception as e:
        raise RuntimeError(f"Failed to uncompress {z_path}: {e}")

@app.post("/find_and_download_gim/")
async def find_and_download_gim(request: GIMRequest, background_tasks: BackgroundTasks):
    gim_sources_response = requests.get(
        "https://api.simurg.space/datafiles/gim_list", 
        params={"d": request.date}
    )
    if gim_sources_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get GIM source list")

    gim_sources = gim_sources_response.json()

    if request.gim_type not in gim_sources:
        raise HTTPException(status_code=404, detail=f"GIM type {request.gim_type} not found for the specified date")

    gim_response = requests.get(
        "https://api.simurg.space/datafiles/gim", 
        params={"d": request.date, "gim_type": request.gim_type}
    )
    if gim_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to download GIM file")

    content_details = gim_response.headers["content-disposition"]
    filename = content_details.replace("attachment; filename=", "").replace('"', '')
    save_path = os.path.join('data', filename)
    extract_to = os.path.join('data', filename.replace('.Z', ''))
    request_id = str(uuid.uuid4())
    progress_file = os.path.join('data', f'{request_id}.progress')

    with open(save_path, 'wb') as f:
        f.write(gim_response.content)
    
    background_tasks.add_task(uncompress_file, save_path, extract_to, progress_file)

    return {"message": "Download and uncompress started", "file_name": filename.replace('.Z', ''), "request_id": request_id}

@app.get("/get_gim_progress/")
async def get_gim_progress(request_id: str):
    try:
        progress_file_path = os.path.join('data', f'{request_id}.progress')
        max_attempts = 5
        attempt = 0

        while attempt < max_attempts:
            if os.path.exists(progress_file_path):
                with open(progress_file_path, 'r') as pfile:
                    progress = pfile.read()
                if progress == '100':
                    os.remove(progress_file_path)
                return {"progress": progress}
            else:
                time.sleep(1)
                attempt += 1
        return {"progress": "0"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting GIM progress: {str(e)}")



@app.post("/find_and_download_map/")
async def find_and_download_data(request: MAP2DRequest, background_tasks: BackgroundTasks):
    queries = checking_by_mail(request.email)
    
    if request.url:
        try:
            id_from_url = request.url.split('id=')[1]
        except IndexError:
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        matching_query = next((query for query in queries if query['id'] == id_from_url), None)
        
        if not matching_query:
            raise HTTPException(status_code=404, detail="Query with the specified ID not found")
    else:
        matching_query = next((query for query in queries if query['type'] == 'map' and query['begin'].startswith(request.date)), None)
        
        if not matching_query:
            raise HTTPException(status_code=404, detail="Query with the specified date not found")

    file_path = matching_query['paths'].get('data')
    if not file_path:
        raise HTTPException(status_code=404, detail="Data file not found in the query results")
    
    download_url = f"https://simurg.space/ufiles/{file_path}"
    save_directory = 'data'
    os.makedirs(save_directory, exist_ok=True)
    save_path = os.path.join(save_directory, os.path.basename(file_path))
    request_id = str(uuid.uuid4())
    progress_file = os.path.join(save_directory, f'{request_id}.progress')
    background_tasks.add_task(download_file, download_url, save_path, progress_file)

    return {
        "message": "Download started",
        "file_name": os.path.basename(save_path),
        "product_type": matching_query['options'].get('product_type', ''),
        "minlat": matching_query['coordinates'].get('minlat', -90),
        "maxlat": matching_query['coordinates'].get('maxlat', 90),
        "minlon": matching_query['coordinates'].get('minlon', -180),
        "maxlon": matching_query['coordinates'].get('maxlon', 180),
        "request_id": request_id
    }


@app.get("/get_map2d_progress/")
async def get_download_progress(request_id: str):
    progress_file_path = os.path.join('data', f'{request_id}.progress')
    
    # Number of attempts to check for the file creation
    max_attempts = 5
    attempt = 0

    while attempt < max_attempts:
        if os.path.exists(progress_file_path):
            with open(progress_file_path, 'r') as pfile:
                progress = pfile.read()
            if progress == '100':
                os.remove(progress_file_path)
            return {"progress": progress}
        else:
            time.sleep(1)  # Wait for 1 second before checking again
            attempt += 1
    
    # If the file does not exist after max_attempts
    return {"progress": "0"}

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

@app.get("/get_plot_progress/")
def get_request_progress(request_id: str):
    progress = get_container_progress(request_id)
    return {"request_id": request_id, "progress": progress}

@app.get("/download_plot/")
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
            total_images = json.load(f)["total"]+2
        completed_images = 0

        num_intervals = 4 
        for i in range(num_intervals):
            interval_dir = f"{data_dir}/{request_id}_interval{i}_data"
            completed_images += count_images_in_directory(interval_dir)

        zip_file = f"{data_dir}/{request_id}_images.zip"
        gif_file = f"{data_dir}/{request_id}_animation.gif"
        if zip_file and gif_file:
            completed_images += 2
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
                interval_images.sort()
                first_image_path = interval_images[0]
                container_image_paths.append(first_image_path)

        if not container_image_paths:
            raise HTTPException(status_code=404, detail="No images found for the specified request_id")

        encoded_images = []
        for img_path in container_image_paths:
            with open(img_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                encoded_images.append(encoded_string)

        return encoded_images

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