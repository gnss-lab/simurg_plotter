from simurg_plotter.multiprocess_sphere_animation.visualization import animate_sphere

if __name__ == '__main__':
    import time

    start_time = time.time()

    file_path = r'C:\Users\kuzne\OneDrive\Документы\work\files_for_simurg_plotter\roti_2015_254_-90_90_N_-180_180_E_3a01.h5'
    central_longitude = 37.6156  # Долгота
    central_latitude = 55.7522  # Широта

    animate_sphere(file_path, central_longitude, central_latitude, output_filename='animation.gif')

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Программа выполнена за {elapsed_time:.2f} секунд")
