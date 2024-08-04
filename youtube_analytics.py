import pandas as pd
from collections import Counter
import spacy
from tqdm import tqdm
import pandas as pd

class YouTubeAnalytics:
    def __init__(self, df):
        self.df = df
        self.nlp = spacy.load("en_core_web_sm")
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.current_date = pd.to_datetime('now')

    def top_n_channels(self, n=10, m=3):
        months_ago = self.current_date - pd.DateOffset(months=m)
        df_filtered = self.df[self.df['timestamp'] >= months_ago]
        top_channels = df_filtered['channel_title'].value_counts().head(n)
        top_channels_df = top_channels.reset_index()
        top_channels_df.columns = ['channel_title', 'count']
        return top_channels_df

    def calculate_weight(self, date):
        days_difference = (self.current_date - date).days
        if days_difference > 90:
            return 0
        return 1 - (days_difference / 90)

    def common_proper_nouns_weighted(self, months=3, top_n=10):
        def filter_proper_nouns(proper_nouns):
            exclude_words = {'shorts', 'audio', 'remix', 'official music video', 'official video', 'video'}
            return [noun for noun in proper_nouns if noun.lower() not in exclude_words]

        def extract_proper_nouns(text):
            doc = self.nlp(text)
            proper_nouns = [ent.text for ent in doc.ents if ent.label_ in ('PERSON', 'GPE', 'ORG', 'PRODUCT', 'EVENT')]
            return filter_proper_nouns(proper_nouns)

        self.df['weight'] = self.df['timestamp'].apply(self.calculate_weight)
        months_ago = self.current_date - pd.DateOffset(months=months)
        df_filtered = self.df[self.df['timestamp'] >= months_ago]

        chunk_size = 1000
        all_proper_nouns = []

        for start in tqdm(range(0, len(df_filtered), chunk_size)):
            end = min(start + chunk_size, len(df_filtered))
            chunk = df_filtered.iloc[start:end]
            chunk['proper_nouns'] = chunk['video_title'].apply(extract_proper_nouns)

            for _, row in chunk.iterrows():
                for noun in row['proper_nouns']:
                    all_proper_nouns.append((noun, row['weight']))

        proper_noun_weighted_counts = Counter()
        for noun, weight in all_proper_nouns:
            proper_noun_weighted_counts[noun] += weight

        common_proper_nouns = proper_noun_weighted_counts.most_common(top_n)
        common_proper_nouns_df = pd.DataFrame(common_proper_nouns, columns=['proper_noun', 'weighted_count'])
        return common_proper_nouns_df

    def videos_watched_per_week(self):
        self.df['week_start'] = self.df['timestamp'].dt.to_period('W').dt.start_time
        videos_per_week = self.df.groupby('week_start').size().reset_index(name='count')
        return videos_per_week

    def most_videos_hour_of_day(self, n=3):
        n_weeks_ago = self.current_date - pd.DateOffset(weeks=n)
        df_filtered = self.df[self.df['timestamp'] >= n_weeks_ago]
        df_filtered['hour'] = df_filtered['timestamp'].dt.hour
        videos_per_hour = df_filtered['hour'].value_counts().sort_index()
        videos_per_hour_df = videos_per_hour.reset_index()
        videos_per_hour_df.columns = ['hour', 'count']
        return videos_per_hour_df



# df = pd.read_csv('extracted_results.csv')
# analytics = YouTubeAnalytics(df)
# print(analytics.top_n_channels()) 
# print(analytics.common_proper_nouns_weighted()) 
# print(analytics.videos_watched_per_week()) 
# print(analytics.most_videos_hour_of_day())
# print(analytics.top_n_channels()) 
# print(analytics.common_proper_nouns_weighted()) 
# print(analytics.videos_watched_per_week()) 
# print(analytics.most_videos_hour_of_day())