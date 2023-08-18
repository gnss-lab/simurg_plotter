from simurg_plotter.sphere_animation.animation import animate_sphere

if __name__ == '__main__':
    file_path = r"C:\Users\kuzne\OneDrive\Документы\work\files_for_simurg_plotter\roti_2015_254_-90_90_N_-180_180_E_3a01.h5"
    central_longitude = 104.280606  # Долгота
    central_latitude = 52.289588  # Широта

    # ROTI:          0   - 0.5
    # Variations:   -0.2 - 0.2
    # TecTrusted:    0   - 100
    vmax = 0.5
    vmin = 0

    animate_sphere(file_path, central_longitude, central_latitude,vmax=vmax, vmin=vmin,scale_label="TECu/min", file_path_to_save="animation.gif")
