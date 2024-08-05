import re
from bs4 import BeautifulSoup
import json
from extract_data import extract_data  # Ensure this is implemented correctly
import uuid
import pandas as pd
from youtube_analytics import YouTubeAnalytics  # Ensure you have the YouTubeAnalytics class in youtube_analytics.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the YouTube Analytics API!"}

@app.post("/metrics")
async def get_metrics(file: UploadFile = File(...)):
    logger.info("Metrics endpoint accessed")
    file_path = f"/tmp/{file.filename}"
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File {file.filename} saved to {file_path}")
        
        with open(file_path, "r") as f:
            contents = f.read()

        user_id = str(uuid.uuid4())
        data = extract_data(contents, user_id, 'Vayun Somaiya')
        logger.debug(f"Extracted data: {data.head()}")

        analytics = YouTubeAnalytics(data)
        
        top_channels = analytics.top_n_channels()
        common_proper_nouns = analytics.common_proper_nouns_weighted()
        videos_per_week = analytics.videos_watched_per_week()
        videos_per_hour = analytics.most_videos_hour_of_day()

        metrics = {
            "top_channels": top_channels.to_dict(orient='records'),
            "common_proper_nouns": common_proper_nouns.to_dict(orient='records'),
            "videos_per_week": videos_per_week.tail(12).to_dict(orient='records'),
            "videos_per_hour": videos_per_hour.to_dict(orient='records')
        }

        logger.info("Metrics calculated successfully")
        return metrics

    except Exception as e:
        logger.error(f"Error processing metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/top_channels")
async def top_channels(file: UploadFile = File(...), n: int = 10, m: int = 3):
    logger.info("Top channels endpoint accessed")
    if file.spool_max_size > 50 * 1024 * 1024:  # 50 MB limit
        logger.warning("File too large")
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path = f"/tmp/{file.filename}"
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File {file.filename} saved to {file_path}")
        
        with open(file_path, "r") as f:
            contents = f.read()

        user_id = str(uuid.uuid4())
        data = extract_data(contents, user_id, 'Vayun Somaiya')
        logger.debug(f"Extracted data: {data.head()}")

        analytics = YouTubeAnalytics(data)
        top_channels = analytics.top_n_channels(n=n, m=m)
        logger.info("Top channels calculated successfully")

        return top_channels.to_dict(orient='records')

    except Exception as e:
        logger.error(f"Error processing top channels: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/common_proper_nouns")
async def common_proper_nouns(file: UploadFile = File(...), months: int = 3, top_n: int = 10):
    logger.info("Common proper nouns endpoint accessed")
    if file.spool_max_size > 50 * 1024 * 1024:  # 50 MB limit
        logger.warning("File too large")
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path = f"/tmp/{file.filename}"
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File {file.filename} saved to {file_path}")
        
        with open(file_path, "r") as f:
            contents = f.read()

        user_id = str(uuid.uuid4())
        data = extract_data(contents, user_id, 'Vayun Somaiya')
        logger.debug(f"Extracted data: {data.head()}")

        analytics = YouTubeAnalytics(data)
        common_proper_nouns = analytics.common_proper_nouns_weighted(months=months, top_n=top_n)
        logger.info("Common proper nouns calculated successfully")

        return common_proper_nouns.to_dict(orient='records')

    except Exception as e:
        logger.error(f"Error processing common proper nouns: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/videos_per_week")
async def videos_per_week(file: UploadFile = File(...)):
    logger.info("Videos per week endpoint accessed")
    if file.spool_max_size > 50 * 1024 * 1024:  # 50 MB limit
        logger.warning("File too large")
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path = f"/tmp/{file.filename}"
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File {file.filename} saved to {file_path}")
        
        with open(file_path, "r") as f:
            contents = f.read()

        user_id = str(uuid.uuid4())
        data = extract_data(contents, user_id, 'Vayun Somaiya')
        logger.debug(f"Extracted data: {data.head()}")

        analytics = YouTubeAnalytics(data)
        videos_per_week = analytics.videos_watched_per_week()
        logger.info("Videos per week calculated successfully")

        return videos_per_week.to_dict(orient='records')

    except Exception as e:
        logger.error(f"Error processing videos per week: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/videos_per_hour")
async def videos_per_hour(file: UploadFile = File(...), n: int = 3):
    logger.info("Videos per hour endpoint accessed")
    if file.spool_max_size > 50 * 1024 * 1024:  # 50 MB limit
        logger.warning("File too large")
        raise HTTPException(status_code=413, detail="File too large")
    
    file_path = f"/tmp/{file.filename}"
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File {file.filename} saved to {file_path}")
        
        with open(file_path, "r") as f:
            contents = f.read()

        user_id = str(uuid.uuid4())
        data = extract_data(contents, user_id, 'Vayun Somaiya')
        logger.debug(f"Extracted data: {data.head()}")

        analytics = YouTubeAnalytics(data)
        videos_per_hour = analytics.most_videos_hour_of_day(n=n)
        logger.info("Videos per hour calculated successfully")

        return videos_per_hour.to_dict(orient='records')

    except Exception as e:
        logger.error(f"Error processing videos per hour: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
