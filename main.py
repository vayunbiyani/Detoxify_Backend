import pandas as pd
import uvicorn  # Ensure pandas is imported
from extract_data import extract_data  # Ensure this is implemented correctly
from extract_json import convert_json_to_dataframe  # Import your method
import uuid
from youtube_analytics import YouTubeAnalytics  # Ensure you have the YouTubeAnalytics class in youtube_analytics.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

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
        data.to_csv('extracted_results.csv', index=False)
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

@app.post("/get_metrics_json")
async def get_metrics_json(file: UploadFile = File(...)):
    logger.info("get_metrics_json endpoint accessed")
    file_path = f"/tmp/{file.filename}"

    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        logger.info(f"File {file.filename} saved to {file_path}")
        
        with open(file_path, "r") as f:
            json_data = json.load(f)
        logger.debug(f"JSON data loaded from file: {json_data[:2]}...")  # Log the first 2 items for brevity

        user_id = str(uuid.uuid4())
        data = convert_json_to_dataframe(json_data, user_id)
        logger.debug(f"Converted JSON data to DataFrame: {data.head()}")
        # Convert all datetime columns to naive datetime (without timezone), handling mixed formats
        data['timestamp'] = pd.to_datetime(data['timestamp'], format='mixed')
        data['timestamp'] = data['timestamp'].dt.tz_localize(None)  # Use the .dt accessor here
        logger.debug(f"Converted JSON data to DataFrame: {data.head()}")

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

        logger.info("Metrics calculated successfully for JSON file input")
        return metrics

    except Exception as e:
        logger.error(f"Error processing JSON metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem"
    )