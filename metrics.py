from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import fake


app = FastAPI()
app.mount("/static", StaticFiles(directory="../d3-gauges/dist"), name="static")


@app.get("/metrics/fake.json")
def metrics_fake():
    return fake.readMetrics()


@app.get("/metrics/live.json")
def metrics_live():
    return {}
