# Установка

```
git clone --branch test_new_manager https://github.com/gnss-lab/simurg_plotter.git

cd /app

conda create -n app python=3.10
conda activate app

pip install docker fastapi uvicorn pydantic aiohttp imageio Pillow unlzw3

docker build -t plot-single .

uvicorn main:app 
```

