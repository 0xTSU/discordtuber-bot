import requests

from bs4 import BeautifulSoup

import json

import os
from dotenv import load_dotenv

channel_str = ""

class channelTube():
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        self.json_soup = None
        self.rss_feed = None
        self.about = None
        self.video_page = None

        # Channel
        self.channel_name = None
        self.avatar = None
        self.subs = None

        # About
        self.total_views = None

        # Recent Video
        self.vid_title = None
        self.vid_thumb = None
        self.vid_link = None

        # Live Stream
        self.is_live = False
        self.live_status = None
        self.live_link = None
        self.live_thumb = None

        # XML
        self.vid_pubdate = None
        self.vid_desc = None
        self.vid_views = None
        self.vid_index_num = None

    def setChannel(self):

        self.channel_name = self.json_soup['header']['c4TabbedHeaderRenderer']['title']
        self.subs = self.json_soup['header']['c4TabbedHeaderRenderer']['subscriberCountText']['simpleText']
        #todo make exception for community tab
        self.total_views = self.about['contents']['twoColumnBrowseResultsRenderer']['tabs'][6]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['channelAboutFullMetadataRenderer']['viewCountText']['simpleText']

        avatar = self.json_soup['header']['c4TabbedHeaderRenderer']['avatar']['thumbnails']

        for i in range(len(avatar)):
            if (i == len(avatar) - 1):
                self.avatar = avatar[i]['url']

    def setVid(self):
        video_index = self.json_soup['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']
        
        for i in range(len(video_index['items']) - 1):

            vid_status = video_index['items'][i]['gridVideoRenderer']['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['style']
            thumbnail_index = video_index['items'][i]['gridVideoRenderer']['thumbnail']['thumbnails']

            if vid_status == "LIVE":

                self.live_status = vid_status
                self.is_live = True
                self.live_link = "https://www.youtube.com/watch?v=" + video_index['items'][i]['gridVideoRenderer']['videoId']
                for u in range(len(thumbnail_index)):
                    if u == len(thumbnail_index) - 1:
                        self.live_thumb = thumbnail_index[u]['url']

            if i == 0 and vid_status == "UPCOMING": 

                if self.live_status == "LIVE":
                    self.live_status = vid_status

                self.is_live = False

            if vid_status == "DEFAULT":

                self.vid_title = video_index['items'][i]['gridVideoRenderer']['title']['runs'][0]['text']
                self.vid_link = "https://www.youtube.com/watch?v=" + video_index['items'][i]['gridVideoRenderer']['videoId']
                self.vid_index_num = i
                for u in range(len(thumbnail_index)):
                    if u == len(thumbnail_index) - 1:
                        self.vid_thumb = thumbnail_index[u]['url']
                break

    def setVidDetails(self):
        desc_ind = self.rss_feed.find_all(('media:description'))
        for i in range(len(desc_ind)):
            if i == self.vid_index_num:
                self.vid_desc = desc_ind[i]
        
        pub_ind = self.rss_feed.find_all('published')
        for i in range(len(pub_ind)):
            if i == self.vid_index_num:
                self.vid_pubdate = pub_ind[i]

    def crawl(self, channel_id):
        url = "https://www.youtube.com/channel/" + channel_id + "/videos"
        request = requests.get(url, headers=self.headers)
        # todo. kiara's channel messes it up
        self.json_soup = json.loads(request.text.split('var ytInitialData = ')[1].split(';')[0])

        url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id
        request = requests.get(url, headers=self.headers)
        self.rss_feed = BeautifulSoup(request.text, 'lxml')

        url = "https://www.youtube.com/channel/" + channel_id + "/about"
        request = requests.get(url, headers=self.headers)
        self.about = json.loads(request.text.split('var ytInitialData = ')[1].split(';')[0])

        self.setChannel()
        self.setVid()
        self.setVidDetails()
        

if __name__ == "__main__":
    example = channelTube()

    example.crawl(channel_str)
    print(example.vid_thumb)

