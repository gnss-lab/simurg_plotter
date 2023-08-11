from .animation import animate_sphere

if __name__ == '__main__':
    file_path = 'files/roti_2015_254_-90_90_N_-180_180_E_3a01.h5'
    central_longitude = 45  # Угол по горизонтали
    central_latitude = 90  # Угол по вертикали

    animate_sphere(file_path, central_longitude, central_latitude)
