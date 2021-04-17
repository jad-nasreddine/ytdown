from sys import exit
from os.path import exists
import time
import sys
import getopt

import json
from pytube import YouTube, Playlist
from urllib.request import urlopen
from bs4 import BeautifulSoup


def update_log(log, m, l):
    """
    update the log
    """
    if l:
        with open(log, 'a') as outfile:
            outfile.write(m + '\n')
      
def extract_url(url, log, logging):
    """
    function that create a beautifulsoup object from the website
    """
    try:
        html = urlopen(url)# open the link
        bs = BeautifulSoup(html.read(), 'html5lib')# create a bs
        return bs
    except Exception as e:# handle the exception
        print("Error opening html link " + str(url))
        update_log(log, "Error: " + format(e), logging)
        exit()
        
def folder_check():
    """
    change the folder where the files will be downloaded
    """
    folder = str(input("Enter Existing path to save the files (leave blank for current directory): "))
    while not exists(folder) and folder != "":
        option = str(input("The entered folder does not exit. Please create it and press (y) to continue, or press (n) to end the program: "))
        if option == 'n':
            exit()
        folder = str(input("Enter Existing path to save the files (leave blank for current directory): "))
        
    return folder

def play_list(bs, option):
    """
    function that finds the list of youtube links
    """    
    tags= bs.find_all(href = True)# find all the tags that contains a hyperlink  
    links = []# Initialize the list of links to empty

    # Fill the array with the hyperlinks containing youtube videos' links
    for t in tags:
        # split the links
        t_split = t["href"].split("/")
        if len(t_split)>=3:# check the external links with a path
            if option == 1:
                if t_split[2] == "www.youtube.com":# check the links with format www.youtube.com/watch
                    if t_split[3].split("?")[0] == "watch":# check the playlist
                        links.append(t["href"])
                elif t_split[2] == "youtu.be":# check the links with format youtu.be/
                    links.append(t["href"])
            else:
                if t_split[2] == "www.youtube.com":# check the links with format www.youtube.com/watch
                    if t_split[3].split("?")[0] == "playlist":# check the playlist
                        links.append(t["href"])
    return links


def option_download(l, data, log, logging):
    """
    function to choose the way you want to download the files
    """
    
    if data[l]['d_opt'] == -1:# choose the type of method to use
        print("   0: if you want to select MIME and Resolution of all the streams to download")
        print("   1: if you want to select manually MIME and Resolution of each stream to download")
        print("   2: if you want to download the first video file")
        print("   3: if you want to ownload the first audio file")
        print("   4: if you want to stop")
        data[l]['d_opt'] = int(input("Enter a valid choice from the above list: "))
        if data[l]['d_opt'] == 4:
            print("The program will stop")
            update_log(log, "User chose to stop the program", logging)
            exit()
        while data[l]['d_opt'] not in range(5):
            data[l]['d_opt'] = int(input("Wrong choice! Enter a valid choice from the above list: "))
        if data[l]['d_opt'] == 0:# The first time the automatic download is called
            data[l]['mime'] = str(input("Enter mime type (e.g. video/mp4, video/webm): "))
            data[l]['res'] = str(input("Enter resolution (e.g. 360p, 720p, 1080p): "))
        update_json(data)
            
    return data

def CrawlPlayList(l, data, seconds, log, logging):
    """
    function that crawl over all the playlists and download the related videos
    """
    if len(data[l]['links'])>0:# If there was some videos downloaded from the playlist
        old = True
    else:
        old = False
        
    play = data[l]['play'].copy()# create a copy to go through
    
    # go through all the play lists
    for link in play:
        try:# handling exception
            p = Playlist(link)
        except:
            print(f'Video {link} is unavaialable, skipping.')
            update_log(log, f'Video {link} is unavaialable, skipping.', logging)
        else:
            if old:
                urls = data[l]['links'].copy()
                old = False
            else:
                urls = p.video_urls
                data[l]['links'] = urls.copy()
                update_json(data)
                
            name = p.title
    
            print("=====Starting to download " + name + " PlayList=====")
            update_log(log, "=====Starting to download " + name + " PlayList=====", logging)
            data = CrawlLinks(urls, data[l]['folder'] + "/" + name, l, data, seconds, log, logging)
            data[l]['play'].pop(0)
            update_json(data)
            update_log(log, "Updated data variable: " + str(data), logging)

            print("=====PLAYLIST " + name.upper() + ": DOWNLOADED=====")
            print("")
            update_log(log, "=====PLAYLIST " + name.upper() + ": DOWNLOADED=====", logging)

            # check if the number of downloaded playlists exceeds the specified number
            if data[l]['play_num'] != -1:
                data[l]['play_num'] = data[l]['play_num'] - 1
                print(str(data[l]['play_num']) + " remaining playlists to download!")
                if data[l]['play_num'] == 0:
                    print("The specified playlists were downloaded! The program will stop")
                    update_log(log, "The specified playlists were downloaded! The program will stop", logging)
                    exit()


def CrawlLinks(playlist, folder, l, data, seconds, log, logging):
    """
    function that crawl over all the links and download the related videos
    """
    
    for link in playlist:
        try:# handling exception
            y = YouTube(link)# get all the streams
        except:
            update_log(log, f'Video {link} is unavaialable, skipping.', logging)
            print(f'Video {link} is unavaialable, skipping.') 
        else:
            name  = y.title# find the title of the video
            streams = y.streams
            if data[l]['d_opt'] == -1:# the first time to enter the program
                print("Enter a downloading option from the below list")
            data = download(name, streams, folder, l, data, logging)
            data[l]['links'].pop(0)# remove the entry from the resume.json
            empty = False
            if len(data[l]['links']) == 0 and len(data[l]['play']) <= 1:
                data.pop(l)
                empty = True
                print("==========ALL VIDEO ARE DOWNLOADED!==========")
                update_log(log, "==========ALL VIDEO ARE DOWNLOADED!==========", logging)
                update_json(data)
           
            if empty:
                exit()
                      
            # check if the number of time exceeds the one specified by user
            if data[l]['time'] != -1:
                print("Elapsed time: " + str((time.time() - seconds)/60) + " minutes")
                if time.time() - seconds > data[l]['time']:
                    print("The time you specified elapsed! The program will stop")
                    update_log(log, "The time you specified elapsed! The program will stop", logging)
                    update_json(data)
                    exit()
            # check if the number of downloaded files exceeds the one specified by user
            if data[l]['link_num'] != -1:
                data[l]['link_num'] = data[l]['link_num'] - 1
                print(str(data[l]['link_num']) + " remaining files to download!")
                if data[l]['link_num'] == 0:
                    print("The specified videos were downloaded! The program will stop")
                    update_log(log, "The specified videos were downloaded! The program will stop", logging)
                    update_json(data)
                    exit()

    return data
    

def update_json(data):
    """
    update the json file
    """
    with open('resume.json', 'w') as outfile:
        json.dump(data, outfile, indent = 4)    
            
def part_download(l, data, option):
    """
    provide the information to stop the download
    """
    
    seconds = 0
    if option < 4:
        print("Choose a number for the method you want to use to stop the program from below:")
        print("   1: stop after certain period of time")
        print("   2: stop after dowloading certain number of videos")
        if option == 2:
            print("   3: stop after dowloading certain number of playlists")
        part = int(input("Enter your choice: "))
        if (part - 1 in range(2)) or (part == 3 and option == 2):# if the choice is within the range
            if part == 1:# stop based on time
                data[l]['time'] = float(input("Enter the period after which you want to stop in minutes: "))*60
                seconds = time.time()
            elif part == 2:# stop based on number of videos
                data[l]['link_num'] = int(input("Enter the number of videos after which you want to stop: "))
            else:
                data[l]['play_num'] = int(input("Enter the number of playlist after which you want to stop: "))
        else:
            print("Invalid value! The program will stop.")
            update_log(log, "Invalid value! The program will stop.", logging)
            exit()
        
        return data, seconds
                    
def download(name, streams, fold, l, data, logging):
    """
    download the files based on the chosen options
    """
    try:        
        if data[l]['d_opt'] == 0:
            print("Starting to download " + name)
            downloaded = auto_download(name, streams, data[l]['mime'], data[l]['res'], fold)
            while not downloaded:
                data[l]['d_opt'] = -1
                print("Provided MIME or Resolution are not available in the video")
                print("Select how you want to continue:")
                data = option_download(l, data, data[l]['log'], logging)
                print("Starting to download " + name)
                downloaded = auto_download(name, streams, data[l]['mime'], data[l]['res'], fold)
                update_log(data[l]['log'], "Updated data variable: " + str(data), logging)
        elif data[l]['d_opt'] == 1:# select manually the stream to download
            print("Starting to download " + name)
            update_log(data[l]['log'], "Starting to download "  + str(data), logging)
            man_download(name, streams, fold)
        elif data[l]['d_opt'] == 2:
            print("Starting to download " + name)
            update_log(data[l]['log'], "Starting to download "  + str(data), logging)
            fvideo_download(name, streams, fold)
        elif data[l]['d_opt'] == 3:
            print("Starting to download " + name)
            update_log(data[l]['log'], "Starting to download "  + str(data), logging)
            faudio_download(name, streams, fold)
        
        print(fold + "/" + name + ": downloaded")
        update_log(data[l]['log'], fold + "/" + name + ": downloaded", logging)
        
    except Exception as e:
        print("Error Downloading Video " + str(name))
        update_log(data[l]['log'], format(e), logging)
        update_json(data)
        exit()
         
    return data

def auto_download(name, streams, mime, res, fold):
    """
    function to download the stream that fits global user preferences about MIME and Resolution
    """
    downloaded = False
    for stream in streams:# search for the provided MIME and Resolution
        if mime in str(stream) and res in str(stream):
            stream.download(fold)# download the file at the specified folder
            downloaded = True
            break
    return downloaded


def man_download(name, streams, fold):
    """
    function to manually choose MIME and Resolution, and download the stream
    """
    i = 1
    for stream in streams:# print all the streams
        print(str(i)+ " " + str(stream))
        i += 1
    num = int(input("Enter authorized stream number from the list above: "))
    while num < 1 or num > len(streams):
        num = int(input("Wrong number! Enter authorized stream number from the list above: "))
    chosen = streams[num-1]
    chosen.download(fold)


def fvideo_download(name, streams, fold):
    """
    function to download the first video stream
    """
    stream = streams.first()
    stream.download(fold)


def faudio_download(name, streams, fold):
    """
    function to download the first audio stream
    """
    stream = streams.filter(only_audio = True).first()
    stream.download(fold)

def main(argv):
    # check the arguments
    log = ''
    logging = False
    try:
        opts, args = getopt.getopt(argv,"hl:",["lfile="])
    except getopt.GetoptError:
        print('error calling the function: ytdown.py -l <logfile>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print('ytdown.py -l <logfile>')
            exit()
        elif opt in ("-l", "--lfile"):
            log = arg
            logging = True
        
    # check if there downloads to be resumed
    r = -1 # If there is no files to resume start over
    if exists('resume.json'):
        with open('resume.json') as json_file:# open the file
            data = json.load(json_file)# put the content in a dictionary
    else:
        f = open('resume.json','w+')
        f.close()
        data = {}
        update_json(data)
        
    if (bool(data)):# check if there are links not fully downloaded
        print("There are still videos not downloaded in the below links")
        links = []
        for i, key in zip(range(len(data)),data.keys()):
            print(str(i+1) + ": " + key + " in " + data[key]['folder'] + " using d_op " + str(data[key]['d_opt']) + " and option " + str(data[key]['option']) + " with MIME = " + data[key]['mime'] + " and RES = " + data[key]['res'] + ". " + str(len(data[key]['play'])) + " playlists and " + str(len(data[key]['links'])) + " links remaining")
            links.append(key)
    
        print("Please choose what you want to do with these files:")
        print("   choose the number of the link that you want to resume, or:")
        print("   choose 0 to delete all the files")
        print("   choose -1 to keep the files and start a new download")
        r = int(input("Choose: "))
        if r+1 not in range(len(data)+2):
            print('Wrong option. The program will stop')
            exit()
            

    # if user chooses to delete the existing file update resume.json with empty dictionary
    if r == 0:
        data = {}
        with open('resume.json', 'w') as outfile:
            json.dump(data, outfile, indent = 4)

    # In case the user does not want to resume any file, start over
    if r <=0:
        # Fetch the folder
        folder = folder_check()# Change the folder to download the files
        if logging:
            log = folder + '/' +log
            f = open(log,'w+')
            f.close()
        
        # choose the type of links
        print('Choose the type of link you want to use from the list below: ')
        print("   1: if the link contains a list of youtube videos")
        print("   2: if the link contains a list of youtube playlists")
        print("   3: if the link is a youtube playlist")
        print("   4: if the link is a youtube video")
        
        option = int(input('Option: '))
        if option-1 not in range(4):
            print('Wrong option! The program will stop')
            update_log(log, "Wrong option! The program will stop", logging)
            exit()
        
        # get the list of links and choose what to do based on the option
        link = str(input('Enter the link with youtube videos to download: '))
        update_log(log, "log for file " + link + ", created on " + str(time.ctime()), logging)
        
        # Initialize the data variable
        data[link]= {
                'folder': "",
                'option': "",
                'd_opt': -1,
                'mime': "",
                'res': "",
                'play': [],
                'links': [],
                'play_num': -1,
                'link_num': -1,
                'time': -1,
                'log': log
        }
        print('log', data[link]['log']) 
        
        # check the videos' options
        data = option_download(link, data, log, False)
        
        if option == 3:#if the link is a youtube playlist
            p = link.split("/")
            if p[2] == 'www.youtube.com' and p[3].split("?")[0] == 'playlist':
                playlist = [link]
            else:
                print("The provided link is not a youtube playlist! The program will stop")
                update_log(log, "The provided link is not a youtube playlist! The program will stop", logging)
                exit()
        elif option == 4:#if the link is a youtube video
            t_split = link.split("/")
            if len(t_split)>=3:# check the external links with a path
                if t_split[2] == "www.youtube.com":# check the links with format www.youtube.com/watch
                    if t_split[3].split("?")[0] == "watch":# check the playlist
                        playlist = [link]
                    else:
                        print("The provided link is not a youtube video! The program will stop")
                        update_log(log, "The provided link is not a youtube video! The program will stop", logging)
                        exit()
                elif t_split[2] == "youtu.be":# check the links with format youtu.be/
                    playlist = [link]
                else:
                    print("The provided link is not a youtube video! The program will stop")
                    update_log(log, "The provided link is not a youtube video! The program will stop", logging)
                    exit()
            else:
                print("The provided link is not a youtube video! The program will stop")
                update_log(log, "The provided link is not a youtube video! The program will stop", logging)
                exit()
        else:#if the link is a list of youtube videos or youtube playlists
            soup = extract_url(link, log, logging)# create the soup
            playlist = play_list(soup, option)# find the list of youtube links
            if len(playlist) == 0:# check if there is no links to youtube
                print("No links to youtube were found! The program will stop")
                update_log(log, "No links to youtube were found! The program will stop", logging)
                exit()
                
        data[link]['option'] = option
        data[link]['folder'] = folder        
        if option == 1 or option == 4:               
            data[link]['links'] = playlist
        else: 
            data[link]['play'] = playlist

        update_json(data)
    else:
        link = links[r-1]
        playlist = data[link]['links']
        option = data[link]['option']
        data[link]['time'] = -1
        data[link]['link_num'] = -1
        data[link]['play_num'] = -1
        if logging == True:# check if the user wants to use the same log file
            print("Do you want to use the old log file: " + data[link]['log'])
            lg = str(input("Press 'y' if you agree: "))
            if lg != "y":
                log = data[link]['folder'] + '/' + log
                data[link]['log'] = log
                f = open(log,'w+')
                f.close()
                update_log(log, "log for Resumed file " + link + ", created on " + str(time.ctime()), logging)
            else:
                log = data[link]['log']
                update_log(log, "\n \n Resuming file " + link + ", created on " + str(time.ctime()), logging)
                
    # partial download
    seconds = 0
    if option < 4:
        part = str(input("If you want to download a part of the videos, press 'y': "))
        if part == 'y':
            data, seconds = part_download(link, data,option)
    
    if logging:
        update_log(log, "initial data variable: " + str(data), logging)
    
    # go over the links
    if option == 1 or option == 4:
        CrawlLinks(playlist, data[link]['folder'], link, data, seconds, log, logging)
    else:
        CrawlPlayList(link, data, seconds, log, logging)

    print("All videos were downloaded!")
    update_log(log, "All videos were downloaded!", logging)
if __name__ == '__main__':
    main(sys.argv[1:])
