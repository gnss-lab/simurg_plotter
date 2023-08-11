import h5py
import pandas as pd
import numpy as np

def get_all_data(file_path):
    data = {}

    def visit_item(name, obj):
        if isinstance(obj, h5py.Group) and name == '/data':
            visit_group(name, obj)
        elif isinstance(obj, h5py.Dataset):
            data[obj.name] = obj[()]

    def visit_group(name, group):
        group.visititems(visit_item)

    with h5py.File(file_path, 'r') as file:
        file.visititems(visit_item)

    return data

def find_min_max(all_data):
    all_min_values = []
    all_max_values = []

    for _, df in all_data:
        min_value = np.min(df['vals'])
        max_value = np.max(df['vals'])

        all_min_values.append(min_value)
        all_max_values.append(max_value)

    global_min_value = np.min(all_min_values)
    global_max_value = np.max(all_max_values)

    print(f"Минимальное значение среди всех датафреймов: {global_min_value}")
    print(f"Максимальное значение среди всех датафреймов: {global_max_value}")

    return global_max_value, global_min_value
