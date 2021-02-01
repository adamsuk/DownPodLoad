#!/usr/bin/env python

"""
my_podcasts:
    func - dicpod
    A dictionary of all my podcasts.
        key - name of the podcast in my file directory
        value - html address of rss feed for podcast
Version History:
v0.1 17/03/18 - basic dictionary on podcasts and rss urls
v0.2 24/04/18 - update to dicpod function to read text file
                'my_pods.txt' for podcast names and urls.
"""

debug = False

# print statements
if debug: print '\n'
if debug: print 'my_podcasts.py'
if debug: print '\n'

def dicpod(text_file='my_pods.txt'):
    """
    Function to read each line from text_file as a 
    podcast name and rss url pair.
    """
    # open text file
    with open(text_file) as f:
        # read each line as an element, and filter empty lines
        raw_text = list(filter(None,f.read().split('\n')))

    # initialise pods dictionary
    pods = {}

    # split raw data by tabs to gain name rss url pairs
    for raw_line in raw_text:
        pod = raw_line.split('\t')
        pods[pod[0]] = pod[1]

    return pods

if __name__ == '__main__':
    pods = dicpod()
    print(pods)
