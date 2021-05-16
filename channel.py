import requests
from bs4 import BeautifulSoup
import json

class channelTube():
    def __init__(self, channel_id = None):

        self.headers = {"User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"}
        self.channel_id = channel_id
        self.crawlChannel(channel_id)

        # Channel 
        channel_dict = self.setNameAndSubs()
        self.channel_name = channel_dict[0]
        self.subs = channel_dict[1]
        self.avatar = self.setAvatar()

        # About Page
        self.total_views = self.setTotalViews()

        # Recent Video
        self.vid_title = None # setVid()
        self.vid_thumb = None # setVid()
        self.vid_link = None # setVid()
        self.setVid()
        self.vid_pubdate = self.setVidPub()
        self.vid_desc = self.setVidDesc()

        # Live Stream
        self.live_index_num = None
        self.is_live = self.setLiveStatus()
        if self.is_live:
            self.setLiveDetails()
            
        else:
            self.live_status = None # setLiveDetails()
            self.live_link = None # setLiveDetails()
            self.live_thumb = None # setLiveDetails()
            self.live_index_num = None # setLiveDetails()

        # Video Page
        self.crawlVideo()
        self.vid_views = self.setVidViews()

    def setNameAndSubs(self):
        channel_dict = []
        channel_dict.append(self.json_soup['header']['c4TabbedHeaderRenderer']['title'])
        channel_dict.append(self.json_soup['header']['c4TabbedHeaderRenderer']['subscriberCountText']['simpleText'])
        return channel_dict

    def setTotalViews(self):
        tab_index = self.about['contents']['twoColumnBrowseResultsRenderer']['tabs']
        for i in range(len(tab_index)):
            if tab_index[i]['tabRenderer']['title'] == "About":
                total_views = tab_index[i]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['channelAboutFullMetadataRenderer']['viewCountText']['simpleText']
                break
        return total_views

    def setAvatar(self):
        avatar = self.json_soup['header']['c4TabbedHeaderRenderer']['avatar']['thumbnails']
        for i in range(len(avatar)):
            if (i == len(avatar) - 1):
                avatar = avatar[i]['url']
        return avatar

    def setLiveStatus(self): 
        x = False
        video_index = self.json_soup['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
        for i in range(len(video_index) - 1):
            status = video_index[i]['gridVideoRenderer']['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['style']
            if status == "LIVE":
                self.live_index_num = i
                x = True
                break
        return x

    def setLiveDetails(self):
        video_index = self.json_soup['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
        self.live_status = video_index[self.live_index_num]['gridVideoRenderer']['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['style']
        thumbnail_index = video_index[self.live_index_num]['gridVideoRenderer']['thumbnail']['thumbnails']
        self.live_thumb = thumbnail_index[len(thumbnail_index) - 1]['url']
        self.live_link = "https://youtube.com/watch?v=" + video_index[self.live_index_num]['gridVideoRenderer']['videoId']


    def setVid(self):
        video_index = self.json_soup['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['gridRenderer']['items']
        
        for i in range(len(video_index) - 1):
            vid_status = video_index[i]['gridVideoRenderer']['thumbnailOverlays'][0]['thumbnailOverlayTimeStatusRenderer']['style']
            if vid_status == "DEFAULT":
                self.vid_index_num = i
                break

        thumbnail_index = video_index[self.vid_index_num]['gridVideoRenderer']['thumbnail']['thumbnails']
        self.vid_title = video_index[self.vid_index_num]['gridVideoRenderer']['title']['runs'][0]['text']
        self.vid_link = "https://www.youtube.com/watch?v=" + video_index[self.vid_index_num]['gridVideoRenderer']['videoId']
        self.vid_thumb = thumbnail_index[len(thumbnail_index) - 1]['url']

    def setVidDesc(self):
        desc_ind = self.rss_feed.find_all(('media:description'))
        for i in range(len(desc_ind)):
            if i == self.vid_index_num:
                desc = desc_ind[i]
                break
        return desc.text
    
    def setVidPub(self):
        pub_ind = self.rss_feed.find_all('published')
        for i in range(len(pub_ind)):
            if i == self.vid_index_num:
                pubdate = pub_ind[i]
                break
        return pubdate.text

    def setVidViews(self):
        x = self.video_page['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
        return x

    def crawlChannel(self, channel_id):
        if channel_id[:2] == "UC":   
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

    def crawlVideo(self):
        url = self.vid_link
        request = requests.get(url, headers=self.headers)
        self.video_page = json.loads(request.text.split('var ytInitialData = ')[1].split(';')[0])

        
    def update(self):
        self.crawlChannel(self.channel_id)
        self.crawlVideo()

        channel_dict = self.setNameAndSubs()
        self.channel_name = channel_dict[0]
        self.subs = channel_dict[1]
        self.avatar = self.setAvatar()
        self.total_views = self.setTotalViews()
        self.setVid()
        self.vid_pubdate = self.setVidPub()
        self.vid_desc = self.setVidDesc()
        self.is_live = self.setLiveStatus()
        if self.is_live:
            self.setLiveDetails()
        else:
            self.live_status = None # setLiveDetails()
            self.live_link = None # setLiveDetails()
            self.live_thumb = None # setLiveDetails()
            self.live_index_num = None # setLiveDetails()

        # Video Page
        self.crawlVideo()
        self.vid_views = self.setVidViews()
