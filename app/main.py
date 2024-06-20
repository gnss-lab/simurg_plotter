import logging
import os
import uuid
from fastapi import FastAPI, Form, HTTPException, BackgroundTasks, File, UploadFile
import json
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
from fastapi.responses import FileResponse
from docker_manager import start_docker_container, get_container_progress, get_container_logs, delete_container_and_progress

app = FastAPI()

logging.basicConfig(level=logging.INFO)

data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

class PlotBase(BaseModel):
    row: int = 0
    col: int = 0
    plot_type: str
    data_file: str = "./data/dtec_2_10_2017_001_-90_90_N_-180_180_E_3d57.h5"
    title: str
    timestamp: str = "2017-01-01T00:00:00"
    rowspan: int = 1
    colspan: int = 1
    colorbar: bool = True

class Map2DPlot(PlotBase):
    plot_type: str = "map2d"
    min_lat: float = -90
    max_lat: float = 90
    min_lon: float = -180
    max_lon: float = 180

class GIMPlot(PlotBase):
    plot_type: str = "gim"

class IPPMercatorPlot(PlotBase):
    plot_type: str = "ipp_mercator"

class IPPPolarPlot(PlotBase):
    plot_type: str = "ipp_polar"

class DSTPlot(PlotBase):
    plot_type: str = "dst"
    delimiter: str = ','

class PlotRequest(BaseModel):
    height: int = 9
    dpi: int = 300
    file_name: str = "test"
    nrows: int = 1
    ncols: int = 1
    plots: List[Union[Map2DPlot, GIMPlot, IPPMercatorPlot, IPPPolarPlot, DSTPlot]]

@app.get("/")
def read_root():
    return {"message": "Welcome to the random graph generator API"}

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

# @app.get("/list_graphs/")
# def list_graphs():
#     try:
#         files = [f for f in os.listdir(data_dir) if f.endswith('.png')]
#         return {"files": files}
#     except FileNotFoundError:
#         logging.error("Directory not found")
#         raise HTTPException(status_code=404, detail="Directory not found")
#     except Exception as e:
#         logging.error(f"Error listing graphs: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/download_graph/")
# def download_graph(filename: str):
#     file_path = f"{data_dir}/{filename}"
#     if os.path.exists(file_path):
#         logging.info(f"Downloading graph: {filename}")
#         return FileResponse(path=file_path, media_type='image/png', filename=filename)
#     else:
#         logging.error(f"File not found: {filename}")
#         raise HTTPException(status_code=404, detail="File not found")

@app.get("/get_request_progress/")
def get_request_progress(request_id: str):
    progress = get_container_progress(request_id)
    return {"request_id": request_id, "progress": progress}

# @app.get("/get_request_logs/")
# def get_request_logs(request_id: str):
#     logs = get_container_logs(request_id)
#     return {"request_id": request_id, "logs": logs}

@app.get("/download_result/")
def download_result(request_id: str = None, filename: str = None):
    if request_id:
        files = [f for f in os.listdir(data_dir) if f.endswith('.png') and request_id in f]
    elif filename:
        files = [filename] if os.path.exists(f"{data_dir}/{filename}") else []

    if not files:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = f"{data_dir}/{files[0]}"
    delete_container_and_progress(request_id)

    logging.info(f"Downloading result for request_id={request_id}: {files[0]}")
    return FileResponse(path=file_path, filename=files[0], media_type='application/octet-stream')

# @app.post("/range_start_date_end_date/")
# async def set_date_range(
#     request_id: str = Form(...),
#     start_date: str = Form(...),
#     end_date: str = Form(...)
# ):
#     try:
#         download_data(request_id, start_date, end_date)
#         return {"status": "success", "message": "Download started"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/check_download/")
# def check_download(request_id: str):
#     try:
#         status = check_data_download(request_id)
#         return {"status": "success", "download_status": status}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.post("/download_ok/")
# def download_ok(request_id: str):
#     try:
#         process_data(request_id)
#         return {"status": "success", "message": "Download verified and processing started"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/check_proc_status/")
# def check_proc_status(request_id: str):
#     try:
#         status = get_container_status(request_id)
#         return {"status": "success", "processing_status": status}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/ok_tokens/")
# def ok_tokens(request_id: str):
#     try:
#         # Dummy function to return tokens, can be replaced with actual logic
#         tokens = {"token1": "value1", "token2": "value2"}
#         return {"status": "success", "tokens": tokens}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
