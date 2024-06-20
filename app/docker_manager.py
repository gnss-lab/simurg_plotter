import docker
import os
import json
import logging
import shutil

# Initialize Docker client
client = docker.from_env()

data_dir = "./data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

def start_docker_container(height, dpi, output_file, request_id, plot_data, data_files):
    container_name = f"graph_generator_{request_id}"
    try:
        # logging.info(plot_data)
        plot_data_str = json.dumps(plot_data)
        plot_data_path = f"{data_dir}/{request_id}_data.json"
        logging.info(plot_data_path)
        
        with open(plot_data_path, 'w') as f:
            f.write(plot_data_str)
        
        data_dir_request = f"{data_dir}/{request_id}_data"
        os.makedirs(data_dir_request, exist_ok=True)
        
        for file in data_files:
            shutil.copy(file, data_dir_request)
        
        volume_bindings = {
    os.path.abspath(os.path.dirname(__file__) + '/data'): {
        'bind': '/app/data',
        'mode': 'rw',
    }
}
        
        logging.info(f"Starting Docker container: {container_name}")
        client.containers.run(
            "plot_single",
            command=["python", "plot_single.py", str(height), str(dpi), output_file, f"./data/{request_id}_data.json"],
            name=container_name,
            volumes=volume_bindings,
            remove=False,
            detach=False
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
