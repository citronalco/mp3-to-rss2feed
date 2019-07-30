# MP3 to Atom Feed

Creates a RSS Atom feed for all MP3 files in a given directory, suitable for the usual podcast players.


### Synopsis ###
```./mp3-to-atomfeed.pl <mp3 files directory> <feed title> <mp3 files url>```


### Example ###
Your MP3 files are in directory "/data/mp3files/" and accessible via https below "https://www.example.net/public/podcast/".
The following would create a valid RSS Atom feed with the title "My Podcast":

```./mp3-to-atomfeed.pl "/data/mp3files/" "My Podcast" "https://www.example.net/public/podcast"```

The script saves the feed file as "podcast.xml" in the MP3 files' directory.
"podcast.xml" contains all MP3 files from "/data/mp3files" sorted from the newest files to the oldest.
Titles and descriptions get read from the MP3 files (ID3 tags title and comment).
