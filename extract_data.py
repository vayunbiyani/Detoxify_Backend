from bs4 import BeautifulSoup
import re
import pandas as pd


def convert_to_psql_timestamp(timestamp):
    month_map = {
        'Jan': '01',
        'Feb': '02',
        'Mar': '03',
        'Apr': '04',
        'May': '05',
        'Jun': '06',
        'Jul': '07',
        'Aug': '08',
        'Sep': '09',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12'
    }

    parts = timestamp.split(' ')
    month = month_map[parts[0]]
    day = parts[1].replace(',', '')
    year = parts[2].replace(',', '')
    time = parts[3]
    ampm = parts[4]
    hours = time.split(':')[0] if ampm == 'AM' else str(int(time.split(':')[0]) + 12)

    return f"{year}-{month}-{day} {hours}:{time.split(':')[1]}:{time.split(':')[2]}"
        

def extract_data(contents, user_id, user_name):
    chunk_size = 3 * 1024 * 1024  # 1 MB
    start = 0
    end = chunk_size
    data = pd.DataFrame(columns=['video_id', 'video_title', 'video_link', 'channel_link', 'channel_id', 'channel_title', 'user_id'])
    
    while start < len(contents):
        chunk = contents[start:end]
        chunk_data = extract_data_chunk(chunk, user_id, user_name)
        data = pd.concat([data, chunk_data], ignore_index=True)
        start = end
        end += chunk_size
    
    return data


def extract_data_chunk(contents, user_id, user_name):
    soup = BeautifulSoup(contents, 'html.parser')
    divs = soup.find_all('div', class_='content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1')
    data = pd.DataFrame(columns=['video_id', 'video_title', 'video_link', 'channel_link', 'channel_id', 'channel_title', 'user_id'])
    iteration_count = 0
    for div in divs:
        iteration_count += 1
        video_anchor = div.find('a')
        if not video_anchor:
            continue
        video_link = video_anchor['href']
        video_id = video_link.split('v=')[1]
        video_title = div.find('a').text
        channel_link_element = div.find('a', href=re.compile(r'^https://www.youtube.com/channel/'))
        channel_link = channel_link_element['href'] if channel_link_element else None
        channel_id = channel_link.split('/')[-1] if channel_link else None
        channel_title = channel_link_element.text if channel_link_element else None
        full_text = div.get_text()
        timestamp_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2},\s\d{4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\s[A-Z]{3}', full_text)
        date_format = "%b %d, %Y, %I:%M:%S %p IST"
        timestamp = pd.to_datetime(timestamp_match.group(0), format=date_format) if timestamp_match else None
        new_data = pd.DataFrame({
            'video_id': [video_id],
            'video_title': [video_title],
            'video_link': [video_link],
            'channel_link': [channel_link],
            'channel_id': [channel_id],
            'channel_title': [channel_title],
            'user_id': [user_id],
            'timestamp': timestamp
        })
        data = pd.concat([data, new_data], ignore_index=True)  

    return data

# # Read the file
# with open('/Users/vayunbiyani/Desktop/Takeout/YouTube and YouTube Music/history/watch-history.html', 'r') as file:
#     contents = file.read()

# # Call the extract_data function
# user_id = 'your_user_id'
# user_name = 'your_user_name'
# data = extract_data(contents, user_id, user_name)

# # Save the extracted data as a CSV file
# data.to_csv('/Users/vayunbiyani/Desktop/Detoxify/extracted_results.csv', index=False)