# MP3-to-RSS2 Feed

Python 3 script that reates a RSS2 feed for all MP3 files in a given directory, suitable for the usual podcast players.


### Synopsis ###
```./mp3-to-rss2feed.py <mp3 files directory> <feed title> <mp3 files url> [image url]```


### Example ###
Your MP3 files are in directory "/data/mp3files/" and accessible via "https://www.example.net/podcast/".
Now you want to have a nice RSS2 feed for it to be able to subscribe and listen to them with your favourite podcast client.

The following would create a valid RSS2 feed with the title "My Podcast":

```./mp3-to-rss2feed.py "/data/mp3files/" "My Podcast" "https://www.example.net/mypodcast/"```

The script saves the feed file as "podcast.xml" in the MP3 files' directory.
"podcast.xml" contains all MP3 files from "/data/mp3files" sorted from the newest files to the oldest.
Titles and descriptions get read from the MP3 files (ID3 tags title and comment).

If you want you can add a link to an image, which will be shown in your podcast client:
```./mp3-to-rss2feed.py "/data/mp3files/" "My Podcast" "https://www.example.net/mypodcast/" "https://www.example.net/image.png```
