# Установка

```
git clone --branch test_new_manager https://github.com/gnss-lab/simurg_plotter.git

cd /app

pip install fastapi uvicorn 

docker build -t plot-single .

uvicorn main:app 
```

