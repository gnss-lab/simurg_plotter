import docker
import os
import json
import logging
import shutil
from datetime import datetime, timedelta
from PIL import Image
import imageio
import zipfile
import asyncio
import glob

# Initialize Docker client
client = docker.from_env()

data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def start_docker_container(height, dpi, output_file, request_id, plot_data_path):
    container_name = f"graph_generator_{request_id}"
    try:
        data_dir_request = f"{data_dir}/{request_id}_data"
        os.makedirs(data_dir_request, exist_ok=True)

        logging.info(plot_data_path)

        volume_bindings = {
            os.path.abspath(os.path.dirname(__file__) + '/data'): {
                'bind': '/app/data',
                'mode': 'rw',
            }
        }

        logging.info(f"Starting Docker container: {container_name}")
        client.containers.run(
            "plot-single",
            command=["python", "plot_single.py", str(height), str(dpi), output_file, plot_data_path, request_id],
            name=container_name,
            volumes=volume_bindings,
            remove=True,
            detach=True
        )
        logging.info(f"Docker container {container_name} finished successfully")
    except docker.errors.ContainerError as e:
        logging.error(f"Error in Docker container {container_name}: {e}")
    except docker.errors.ImageNotFound as e:
        logging.error(f"Image not found: {e}")
    except docker.errors.APIError as e:
        logging.error(f"API error: {e}")
    finally:
        if os.path.exists(plot_data_path):
            os.remove(plot_data_path)
        if os.path.exists(data_dir_request):
            shutil.rmtree(data_dir_request)

async def start_docker_container_multiple(height, dpi, request_id, plot_data_path, start_time, end_time, interval_seconds):
    container_name = f"graph_generator_{request_id}"
    try:
        data_dir_request = f"{data_dir}/{request_id}_data"
        os.makedirs(data_dir_request, exist_ok=True)

        volume_bindings = {
            os.path.abspath(data_dir): {
                'bind': '/app/data',
                'mode': 'rw',
            }
        }

        logging.info(f"Starting Docker container: {container_name}")
        container = client.containers.run(
            "plot-single",
            command=["python", "plot_multiple.py", str(height), str(dpi), request_id, plot_data_path, start_time, end_time, str(interval_seconds)],
            name=container_name,
            volumes=volume_bindings,
            remove=True,
            detach=True  # Detach for asynchronous processing
        )
        logging.info(f"Docker container {container_name} started successfully")

        return container, data_dir_request

    except docker.errors.ContainerError as e:
        logging.error(f"Error in Docker container {container_name}: {e}")
        return None, None
    except docker.errors.ImageNotFound as e:
        logging.error(f"Image not found: {e}")
        return None, None
    except docker.errors.APIError as e:
        logging.error(f"API error: {e}")
        return None, None

async def wait_for_container(container):
    result = await asyncio.to_thread(container.wait)
    return result

async def wait_for_containers(containers):
    tasks = [wait_for_container(container) for container in containers]
    results = await asyncio.gather(*tasks)
    return results

def build_animation(images, animation_file):
    imageio.mimsave(animation_file, images, duration=1.0)

def count_images_in_directory(directory):
    return len(glob.glob(os.path.join(directory, '*.png')))

def calculate_total_images(start_time, end_time, interval_seconds, num_intervals=4):
    start = datetime.fromisoformat(start_time)
    end = datetime.fromisoformat(end_time)
    
    total_images = 0
    
    for i in range(num_intervals):
        current_interval_start = start + i * (end - start) / num_intervals
        current_interval_end = start + (i + 1) * (end - start) / num_intervals
        num_timestamps = int((current_interval_end - current_interval_start).total_seconds() / interval_seconds)
        total_images += num_timestamps
    
    return total_images

def create_total_files(request_id, total):
    progress_file = f"./data/{request_id}_total.json"
    with open(progress_file, 'w') as f:
        json.dump({"total": total}, f)

async def start_docker_container_for_intervals(height, dpi, request_id, plot_data_path, start_time, end_time, interval_seconds):
    try:
        interval_start = datetime.fromisoformat(start_time)
        interval_end = datetime.fromisoformat(end_time)

        # Calculate number of intervals
        num_intervals = 4
        interval_duration = (interval_end - interval_start) / num_intervals
        total_files = calculate_total_images(start_time, end_time, interval_seconds)
        create_total_files(request_id, total_files)
        # List to store tasks for started containers
        container_tasks = []
        data_dirs = []
        interval_starts = []
        for i in range(num_intervals):
            # Calculate current interval start and end times
            current_interval_start = interval_start + i * interval_duration
            interval_starts.append(current_interval_start.strftime('%H%M%S'))
            current_interval_end = interval_start + (i + 1) * interval_duration

            # Calculate array of timestamps within the current interval
            timestamps = []
            current_time = current_interval_start
            while current_time < current_interval_end:
                timestamps.append(current_time.isoformat())
                current_time += timedelta(seconds=interval_seconds)

            # Generate unique request_id for each interval and container
            interval_request_id = f"{request_id}_interval{i}"
            interval_plot_data_path = f"{data_dir}/{interval_request_id}_data.json"

            # Adjust plot data with current interval timestamps
            with open(plot_data_path, 'r') as f:
                plot_data = json.load(f)
                plot_data['interval_timestamps'] = timestamps

            with open(interval_plot_data_path, 'w') as f:
                json.dump(plot_data, f)

            container, data_dir_request = await start_docker_container_multiple(height, dpi, interval_request_id, interval_plot_data_path, current_interval_start.isoformat(), current_interval_end.isoformat(), interval_seconds)
            if container:
                container_tasks.append(container)
                data_dirs.append(data_dir_request)

        await wait_for_containers(container_tasks)

        container_image_paths = []
        for i in range(num_intervals):
            interval_dir = f"{data_dir}/{request_id}_interval{i}_data"
            interval_images = glob.glob(os.path.join(interval_dir, '*.png'))
            container_image_paths.extend(interval_images)

        animation_file = f"data/{request_id}_animation.gif"
        images = []
        for img_path in container_image_paths:
            img = Image.open(img_path)
            images.append(img)

        build_animation(images, animation_file)

        zip_file = f"data/{request_id}_images.zip"
        with zipfile.ZipFile(zip_file, 'w') as zf:
            for img_path in container_image_paths:
                zf.write(img_path, os.path.basename(img_path))

        preview_image_path = container_image_paths[0] if container_image_paths else None

        return preview_image_path, animation_file, zip_file

    except Exception as e:
        logging.error(f"Error in start_docker_container_for_intervals: {e}")
        raise e

def stop_and_clean_docker_containers(request_id: str):
    try:
        num_intervals = 4
        for i in range(num_intervals):
            interval_request_id = f"{request_id}_interval{i}"
            container_name = f"graph_generator_{interval_request_id}"
            container = client.containers.get(container_name)
            container.stop()
            container.remove()
            logging.info(f"Container for request_id={request_id} has been stopped and removed")
            # Remove the associated progress file
            progress_file = f"./data/{interval_request_id}_progress.json"
            if os.path.exists(progress_file):
                os.remove(progress_file)

            request_file = f"./data/{interval_request_id}_data.json"
            if os.path.exists(request_file):
                os.remove(request_file)
            # Remove the associated data directory
            data_dir_request = f"{data_dir}/{interval_request_id}_data"
            if os.path.exists(data_dir_request):
                shutil.rmtree(data_dir_request)
                logging.info(f"Data directory for interval_request_id={interval_request_id} has been removed")

            

        # Remove the total images file
        total_file = f"./data/{request_id}_total.json"
        if os.path.exists(total_file):
            os.remove(total_file)
            logging.info(f"Total images file for request_id={request_id} has been removed")

    except docker.errors.NotFound:
        logging.warning(f"Container for request_id={request_id} not found")
    except Exception as e:
        logging.error(f"Error stopping and cleaning up containers for request_id={request_id}: {e}")


def get_container_progress(request_id):
    progress_file = f"./data/{request_id}_progress.json"
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f).get("progress", 0)
    return 0

def get_container_logs(request_id):
    logging.info(f"Fetching logs for container with request_id={request_id}")
    try:
        container = client.containers.get(f"graph_generator_{request_id}")
        logs = container.logs().decode('utf-8')
        return logs
    except docker.errors.NotFound:
        logging.warning(f"Container for request_id={request_id} not found")
        return "not found"
    except Exception as e:
        logging.error(f"Failed to get logs for container with request_id={request_id}: {e}")
        return "error"

def delete_container_and_progress(request_id):
    try:
        container = client.containers.get(f"graph_generator_{request_id}")
        container.remove(force=True)
        logging.info(f"Container for request_id={request_id} has been removed")
    except docker.errors.NotFound:
        logging.warning(f"Container for request_id={request_id} not found")
    
    progress_file = f"./data/{request_id}_progress.json"
    if os.path.exists(progress_file):
        os.remove(progress_file)
