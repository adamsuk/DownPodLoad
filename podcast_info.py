#!/usr/bin/env python

"""
podcast_info
    Script used to obtain all podcast information
    This is written in the form of a class.

    Rewrite of get_podcasts.py using object orientated
    programming and seperating obtaining the info and
    downloading the podcasts.

v1.0.1
    Removed 'podcast_link':entry.link from episodes[entry.title]
    in podcast_episodes.
"""
from django.utils.encoding import smart_str, smart_unicode
import dateparser
import feedparser
import os
import re
import urllib2
import sys
from my_podcasts import dicpod

debug = True

class PodcastInfo(object):
    """This is a class to obtain all podcast info

    Attributes:
        name: A string representing the podcast name
        rss_url: URL where all podcasts can be obtained
        podcast_data: dictionary containing podcast specific data
            podcast_downloaded: boolean to set podcast download
                                status in current location
    """

    def __init__(self, name, rss_url):
        self.name = name
        self.rss_url = rss_url
        # initialisation of episodes dictionary
        self.episodes = {}

    def podcast_episodes(self):
        """Probes the rss_url for all podcast data"""
        # print details of current podcast
        feed = feedparser.parse(self.rss_url)
        feed_title = feed['feed']['title']
        feed_entries = feed.entries

        for entry in feed.entries:
            date = dateparser.parse(entry['published'].replace('-','+'))
            reordered_date = ('%d-%02d-%02d' % (date.year, date.month,\
                date.day))
            mp3_urls = list(set(self.get_url('.mp3', entry)))
            m4a_urls = list(set(self.get_url('.m4a', entry)))
            # try to encode title to string
            try:
                entry.title = entry.title.encode()
            except UnicodeEncodeError:
                entry.title = smart_str(entry.title)
                
            # download name requires no special characters
            download_name = re.sub('[\\/*?"<>|]', '', re.sub(':', ' -',\
                entry.title)) # previously article_title
            # set download_name to include reordered published date
            download_name = reordered_date + ' - ' + download_name
            # set new entry in episodes dictionary
            self.episodes[entry.title] = {'download_name':download_name,
                                          'mp3_link':mp3_urls,
                                          'm4a_link':m4a_urls,
                                          'published':reordered_date
                                          }
                                              
        return self.episodes
    
    def get_url(self, substring, dictionary):
        """finds substring in dictionary"""
        for key, value in sorted(dictionary.items()):
            # try is for handling Booleans
            try:
                if substring in value:
                    yield value
                elif isinstance(value, dict):
                    for result in self.get_url(substring, value):
                        yield result
                elif isinstance(value, list):
                    for list_item in value:
                        for result in self.get_url(substring, list_item):
                            yield result
            except:
                pass

def podcast_info_init():
    """
    Function to initiate PodcastInfo for each key in the dicpod
    dictionary - when ran as a script
    """
    # initiate dicpod data
    req_podcasts = dicpod()

    # initiate podcast_info dictionary - which will contain the
    # PodcastInfo class for each req_podcast key
    podcast_info = {}

    # scroll through dicpod keys and initate PodcastInfo
    for k,v in sorted(req_podcasts.items()):
        print(k)
        podcast_info[k] = PodcastInfo(k,v).podcast_episodes()
        print(podcast_info[k])
        input('Continue?')

if __name__ == '__main__':
    podcast_info_init()
