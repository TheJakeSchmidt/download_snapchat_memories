# Snapchat Memories downloader

Snapchat keeps your Memories (including old stories), but holds them hostage. It's very difficult to extract your
Memories from Snapchat with the timestamps intact:

- You can export Memories (100 at a time) from the app, either into another app or to local storage, but the EXIF
  metadata is stripped.
- You can request a dump of your data from Snapchat at https://accounts.snapchat.com/accounts/downloadmydata, but what
  you get is an HTML file with an individual "Download" button for each photo and video.
- The HTML page also has the timestamp next to each "Download" button. You can click every Download button and then try
  to associate the timestamp from the table with the files that were downloaded, but you'll find that each filename is a
  UUID, each URL contains 3 different UUIDs, and the UUID from the filename appears nowhere in the URL.

The script in this repository is the solution. If you request your data from Snapchat at
https://accounts.snapchat.com/accounts/downloadmydata, unzip it (the filename will look like mydata_1234567890123.zip),
and run the script like this:

```
$ git clone https://github.com/TheJakeSchmidt/download_snapchat_memories.git
$ cd download_snapchat_memories
$ virtualenv env
$ source env/bin/activate
$ pip install beautifulsoup4 dateparser pyexif pytz requests tqdm
$ python download_snapchat_memories.py --mydata_path=/path/to/mydata_1234567890123
```

... you'll get a snapchat_memories/ directory with your properly-timestamped photos and videos. If you have a GPS track
file (e.g. from your Google Location History), you can subsequently add geotags too:

```
exiftool -geotag location_history.kml snapchat_memories/*
```

This script has only been tested on Linux, but it might work on Windows too, if you have pyexif and exiftool installed.