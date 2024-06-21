# Установка

```
git clone https://github.com/gnss-lab/simurg_plotter.git@test_new_manager

cd /app

pip install fastapi uvicorn 

docker build -t plot-single .

uvicorn main:app 
```

