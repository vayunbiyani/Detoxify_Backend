import pandas as pd

from youtube_analytics import YouTubeAnalytics 


df = pd.read_csv('extracted_results.csv')
analytics = YouTubeAnalytics(df)
# print(analytics.top_n_channels()) 
# print(analytics.common_proper_nouns_weighted()) 
# print(analytics.videos_watched_per_week()) 
# print(analytics.most_videos_hour_of_day())
# print(analytics.top_n_channels()) 
# print(analytics.common_proper_nouns_weighted()) 
print(analytics.videos_watched_per_week().tail(12)) 
# print(analytics.most_videos_hour_of_day())