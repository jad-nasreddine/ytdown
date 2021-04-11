# ytdown
A python module to download youtube videos from different location using pytube library

# Features
- Fetch all links to youtube playlists and videos and download the videos
- Allow user to choose resolution and encoding
- Allow user to download a number of the videos available in the website and resume downloading later on
- Allow user to choose the folder to download the videos
- Allow user to save a log file
# Quistart
## Installation
ytdown is test on python 3.7, but it may work with previous python 3 versions. It requires the installation of urllib3 and the latest version of pytube. To install the latter use:
```bash
python -m pip install git+https://github.com/pytube/pytube
```
To install ytdown, download the python file available in this repository
## Using ytdown
From the command line, you can write
```bash
python ytdown.py -l log.txt
```
The option -l log.txt is used in case you want to have a log file.
From here the program will guide you.
