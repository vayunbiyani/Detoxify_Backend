import pandas as pd
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    video_id_match = re.search(r'v=([^&]+)', url)
    if video_id_match:
        return video_id_match.group(1)
    return None

def convert_json_to_dataframe(json_data, user_id):
    """Convert the given JSON data to a pandas DataFrame with the required format."""
    
    # Prepare lists to hold data for each column
    video_ids = []
    video_titles = []
    video_links = []
    channel_links = []
    channel_ids = []
    channel_titles = []
    timestamps = []
    
    for entry in json_data:
        # Skip entries that have "details": [{"name": "From Google Ads"}]
        if entry.get("details") == [{"name": "From Google Ads"}]:
            continue
        
        video_link = entry.get("titleUrl", "")
        video_title = entry.get("title", "")
        timestamp = entry.get("time", "")
        
        # Extract video ID from URL
        video_id = extract_video_id(video_link)
        
        # channel link is entry["subtitles"][0]["url"]
        # channel title is entry["subtitles"][0]["name"]
        # channel id is channel link split by "/" last element
        logger.debug(f"Entry: {entry}")
        subtitles = entry.get("subtitles", [])
        subtitle = subtitles[0] if subtitles else None
        if subtitle:
            channel_link = subtitle["url"]
            channel_title = subtitle["name"]
        else:
            channel_link = ""
            channel_title = ""

        if channel_link:
            channel_id = channel_link.split("/")[-1]
        else:
            channel_id = ""

        # Append extracted data to respective lists
        video_ids.append(video_id)
        video_titles.append(video_title)
        video_links.append(video_link)
        channel_links.append(channel_link)
        channel_ids.append(channel_id)
        channel_titles.append(channel_title)
        timestamps.append(timestamp)
    
    # Create DataFrame from collected data
    df = pd.DataFrame({
        'video_id': video_ids,
        'video_title': video_titles,
        'video_link': video_links,
        'channel_link': channel_links,
        'channel_id': channel_ids,
        'channel_title': channel_titles,
        'user_id': user_id,
        'timestamp': pd.to_datetime(timestamps, format='mixed').tz_localize(None)
    })
    
    return df
