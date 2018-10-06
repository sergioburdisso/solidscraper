
# Example: twitter user timeline downloader

It downloads the user's timeline. To store the output, it creates a folder called `_OUTPUT_`, and inside, creates a folder for each user to store her/his tweets and photos and images. To run the script you just need to specify the user name as an argument, as follows:

````
$ python scraper-twitter-user.py username
````
---

For example, suppose the user we want to crawl is called "user123", after executing the script:

````
$ python scraper-twitter-user.py user123
````

it  will create the following directories and files:

```
    .
    ├──_OUTPUT_                          <- it contains a folder for each user
    │   │
    │   └──user123                       <- user123's folder
    │       │
    │       ├──photos                    <- user123's images
    │       │   +──personal              <- images uploaded by user123
    │       │   +──extern                <- images retweeted by user123
    │       │   │
    │       │   └──profile_picture.jpg   <- the profile picture
    │       │
    │       └──user123.xml               <- xml file with all user123's tweets
    │
    └─scraper-twitter-user.py
```
