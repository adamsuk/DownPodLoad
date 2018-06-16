#!/usr/bin/env python

"""
v0.3 - call to find_file in run_me to obtain podcast dictionary
       of name/url pairs.
       
v0.2 - podcast information now obtained from podcast_info

v0.1 - initial write of download_podcasts script

This is the main calling function for the podcast downloader

download_podcasts.py
    Module to check podcasts already downloaded in a specfic
    location.
"""

debug = False
download = True

# print statements
if debug: print '\n'
if debug: print 'download_podcasts.py'
if debug: print '\n'

import sys
import os
import re
import urllib2
from django.utils.encoding import smart_str, smart_unicode

# my local imports
from common import color
from my_podcasts import dicpod
from podcast_info import PodcastInfo
from find_file import find_file

def convert_m4a_to_mp3(file):
    """
    does the good stuff - required now m4a files can now be found
    """
    if isinstance(file,list):
        for each_file in file:
            convert_m4a_to_mp3(each_file)
    else:
        # delete me later
        if os.path.isfile(file+'.mp3'):
            os.remove(file+'.mp3')
        os.system("ffmpeg -i '"+file+".m4a'  -acodec libmp3lame -ab 192k '"+file+".mp3'")
        # delete me later
        if os.path.isfile(file+'.m4a'):
            os.remove(file+'.m4a')
        print('Converted all .m4a files')

def check_dirs(root, req_pod_dic):
    """
    Checks directories in current run location against 
    my_podcast dictionary and makes missing directories
    """
    _, dirs,_ = os.walk(root).next()
    # set exist_dirs
    exits_dirs = dirs
    # list of podcasts requested
    requested_podcasts = req_pod_dic.keys()
    # difference between podcasts got and requested
    missing_dirs = list(set(requested_podcasts) - set(dirs))

    # make directories for missing podcasts
    for missing_dir in missing_dirs:
        os.mkdir(missing_dir)
        print 'Made directory:',missing_dir,'\n'
        
    # return directories that already existed
    return exits_dirs

def get_files(dirs):
    """
    Obtains a list of .mp3 files in a given directory
    """
    exist_files = {}
    
    for direc in dirs:
        
        # obtain list of files in dir
        _,_,files = os.walk(direc).next()
        
        # set exist_files dictionary with
        #    key - directory
        #    value - list of files that exist
        # POTENTIAL FOR TAG TO RSS DATA COMPARISONS FOR
        # FILES WITH DIFFERENT NAMES
        #for file in files:
        #    print os.stat(os.path.join(direc,file))
        #    from mutagen.easyid3 import EasyID3
        #    from mutagen.mp3 import MP3
        #    audio = MP3(os.path.join(direc,file), ID3=EasyID3)
        #    audio.pprint()
        exist_files[direc] = files
    return exist_files
    
def download_missing(root, pod_name, podcast, old_pods):
    """Uses podcast_info to obtain all required info"""
    print color.BOLD + color.UNDERLINE + pod_name + color.END
    # scroll through episodes in podcast
    for ep, info in sorted(podcast.items()):
        # download missing podcasts
        print 'Evaluating: ' + ep
        # match name ie download_name without special characters
        check_name = re.sub('[\\/*?"<>|]', '', re.sub(':', ' -',\
                     str(ep)))
        
        # check if episode name is in the found .mp3 files
        if any(str(check_name) in string for string in old_pods):
            # obtain full string of match
            match = [s for s in old_pods if check_name in s]
            # check downloaded episode equals download_name
            if len(match) == 1 and match[0] == info['download_name'] + '.mp3':
                pass
            # else if only one match rename to download_name
            elif len(match) == 1:
                print('RENAME! '+str(match[0])+' to '+\
                    info['download_name']+'.mp3')
                os.rename(os.path.join(root,pod_name,str(match[0])), os.path.join(root,pod_name,info['download_name']+'.mp3'))
                
            # else print error message
            else:
                print('Too many matches in download location for'+ep)
        else:
            print('DOWNLOAD: ' + info['download_name'])
            
            # iterate through mp3 urls - allows some failed
            # urls to exist
            n = 0
            
            # if download 'True' set complete to 'False'
            if download:
                complete = False
            else:
                complete = True
            
            # if debug print mp3 url
            if debug: print(info['mp3_link'][n])
            
            # go through while podcast until podcast downloaded
            # or all options exhausted
            while not complete:
                try:
                    if info['mp3_link']:
                        # use urllib2 to download mp3 file
                        mp3file = urllib2.urlopen(info['mp3_link'][n])
                        with open(os.path.join(root,pod_name,\
                                  info['download_name']+'.mp3'),'wb') as output:
                            output.write(mp3file.read())
                        n += 1
                        complete = True
                    elif info['m4a_link']:
                        # use urllib2 to download mp3 file
                        m4afile = urllib2.urlopen(info['m4a_link'][n])
                        with open(os.path.join(root,pod_name,\
                                  info['download_name']+'.m4a'),'wb') as output:
                            output.write(m4afile.read())
                            convert_m4a_to_mp3(os.path.join(root,pod_name,\
                                               info['download_name']))
                        n += 1
                        complete = True
                except:
                    print color.BOLD + pod_name + ': ' + str(ep) + color.END
                    n += 1
                    # exit if outside of mp3_urls/m4a_urls range
                    if info['mp3_link']:
                        if n >= len(info['mp3_link']):
                            complete = True
                    elif info['m4a_link']:
                        if n >= len(info['m4a_link']):
                            complete = True
    
def run_me():
    # set root directory
    root = os.getcwd()
    print(root)
    # find instances of file in base directory
    base_pod_locs = find_file(root)
    # for each element in base_pod_locs find name/urls,
    # find downloaded and download missing
    for base_pod_loc in base_pod_locs:
        root = base_pod_loc
        os.chdir(root)
        # required podcast dictionary
        req_pods = dicpod()
        # check directories in run location
        old_dirs = check_dirs(root, req_pods)
        # check all old files
        old_files = get_files(old_dirs)
        # download all required podcasts
        for pod,rss_url in sorted(req_pods.items()):
            # get podcast info
            req_pods[pod] = PodcastInfo(pod, rss_url).podcast_episodes()
            # if directory had to be made no old_files key exists
            # make it
            if pod not in old_files.keys():
                old_files[pod] = []
            # run each podcast through download_missing function
            download_missing(root, pod, req_pods[pod], old_files[pod])
    
if __name__ == '__main__':
    run_me()

