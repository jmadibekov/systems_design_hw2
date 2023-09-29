import json
from pathlib import Path

import requests
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/bin/{bin_id}")
def read_item(bin_id: str):
    bin_file = Path(__file__).resolve().parent / f"{bin_id}.json"
    if bin_file.exists():
        print("Reading from cache file")
        with open(bin_file, "r") as f:
            data = json.load(f)
        return data

    else:
        print("Making an API request")
        r = requests.get(
            f"https://old.stat.gov.kz/api/juridical/counter/api/?bin={bin_id}&lang=ru"
        )
        data = r.json()["obj"]
        with open(bin_file, "w") as f:
            json.dump(data, f)
        return data
