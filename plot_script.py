import sys
import matplotlib.pyplot as plt
import numpy as np
import os
import logging
import time

def generate_random_plot(width, height, dpi, output_file):
    try:
        logging.info(f"Starting plot generation: width={width}, height={height}, dpi={dpi}, output_file={output_file}")
        x = np.linspace(0, 10, 100)
        y = np.sin(x) + np.random.normal(0, 0.5, 100)

        plt.figure(figsize=(width/dpi, height/dpi), dpi=dpi)
        plt.plot(x, y)
        plt.title("Random Plot")
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        time.sleep(30)
        output_path = os.path.join("/data", output_file)
        plt.savefig(output_path)
        plt.close()
        logging.info(f"Plot successfully saved to {output_path}")
    except Exception as e:
        logging.error(f"Error generating plot: {e}")

if __name__ == "__main__":
    width = int(sys.argv[1])
    height = int(sys.argv[2])
    dpi = int(sys.argv[3])
    output_file = sys.argv[4]
    generate_random_plot(width, height, dpi, output_file)
