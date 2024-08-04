import re
from bs4 import BeautifulSoup
import json
from extract_data import extract_data  # Ensure this is implemented correctly
import uuid
import pandas as pd
from youtube_analytics import YouTubeAnalytics  # Ensure you have the YouTubeAnalytics class in youtube_analytics.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/metrics")
async def get_metrics(file: UploadFile = File(...)):
    # Check file size
    file_path = f"/tmp/{file.filename}"
    # with open(file_path, "wb") as f:
    #     f.write(await file.read())
    
    with open(file_path, "r") as f:
        contents = f.read()

    user_id = str(uuid.uuid4())
    data = extract_data(contents, user_id, 'Vayun Somaiya')
    # save as data2.csv
    # data.to_csv('data2.csv', index=False)

    analytics = YouTubeAnalytics(data)

    top_channels = analytics.top_n_channels()
    common_proper_nouns = analytics.common_proper_nouns_weighted()
    videos_per_week = analytics.videos_watched_per_week()
    videos_per_hour = analytics.most_videos_hour_of_day()

    print(videos_per_week.tail(12))
    print(videos_per_week.head(12))
    metrics = {
        "top_channels": top_channels.to_dict(orient='records'),
        "common_proper_nouns": common_proper_nouns.to_dict(orient='records'),
        "videos_per_week": videos_per_week.tail(12).to_dict(orient='records'),
        "videos_per_hour": videos_per_hour.to_dict(orient='records')
    }

    return metrics

@app.post("/top_channels")
async def top_channels(file: UploadFile = File(...), n: int = 10, m: int = 3):
    # Check file size
    if file.spool_max_size > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    with open(file_path, "r") as f:
        contents = f.read()

    user_id = str(uuid.uuid4())
    data = extract_data(contents, user_id, 'Vayun Somaiya')

    analytics = YouTubeAnalytics(data)
    top_channels = analytics.top_n_channels(n=n, m=m)

    return top_channels.to_dict(orient='records')

@app.post("/common_proper_nouns")
async def common_proper_nouns(file: UploadFile = File(...), months: int = 3, top_n: int = 10):
    # Check file size
    if file.spool_max_size > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    with open(file_path, "r") as f:
        contents = f.read()

    user_id = str(uuid.uuid4())
    data = extract_data(contents, user_id, 'Vayun Somaiya')

    analytics = YouTubeAnalytics(data)
    common_proper_nouns = analytics.common_proper_nouns_weighted(months=months, top_n=top_n)

    return common_proper_nouns.to_dict(orient='records')

@app.post("/videos_per_week")
async def videos_per_week(file: UploadFile = File(...)):
    # Check file size
    if file.spool_max_size > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    with open(file_path, "r") as f:
        contents = f.read()

    user_id = str(uuid.uuid4())
    data = extract_data(contents, user_id, 'Vayun Somaiya')

    analytics = YouTubeAnalytics(data)
    videos_per_week = analytics.videos_watched_per_week()

    return videos_per_week.to_dict(orient='records')

@app.post("/videos_per_hour")
async def videos_per_hour(file: UploadFile = File(...), n: int = 3):
    # Check file size
    if file.spool_max_size > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    with open(file_path, "r") as f:
        contents = f.read()

    user_id = str(uuid.uuid4())
    data = extract_data(contents, user_id, 'Vayun Somaiya')

    analytics = YouTubeAnalytics(data)
    videos_per_hour = analytics.most_videos_hour_of_day(n=n)

    return videos_per_hour.to_dict(orient='records')
