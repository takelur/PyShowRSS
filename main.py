import os
import feedparser
import time
import requests
import signal
import sys

from loguru import logger

# Checks if the script is in the initial run
initialFlag = True
# List of feed URLs
feedURLs = []
# List of webhook URLs
webHooks = []
# List of old episodes
old_episodes = []

# Configure logger
logger.add("config/pyshowrss.log", rotation="1 MB", retention=3, level="INFO")


def getFeedURLs():
    feeds = []
    try:
        with open("config/feeds.txt", "r") as f:
            t_feeds = f.readlines()
    except Exception as e:
        print("Error, most likely config/feeds.txt was not found")
        logger.error(f"Most likely the config/feeds.txt file was not found:\n {e}")
        sys.exit(1)
    for URL in t_feeds:
        feeds.append(URL.strip("\n"))
    return feeds

# Works with feeds from showrss.info
def parseFeeds(feedURLs):
    episodes = []
    for feed in feedURLs:
        d = feedparser.parse(feed)
        # get the first 20 entries (or less)
        for i in range(min(20, len(d.entries))):
            episodes.append(d.entries[i].title)
    return episodes


def checkDuplicates(episodes, old_episodes):
    new_episodes = []
    for episode in episodes:
        if episode not in old_episodes:
            new_episodes.append(episode)
    return new_episodes


def getwebhookURLs():
    webHooks = []
    try:
        with open("config/webhooks.txt", "r") as f:
            t_webHooks = f.readlines()
    except Exception as e:
        print("Error, most likely config/webhooks.txt was not found")
        logger.error(f"Most likely the config/webhooks.txt file was not found:\n {e}")
        sys.exit(1)
    for webhook in t_webHooks:
        webHooks.append(webhook.strip("\n"))
    return webHooks

# Discord webhook
def webHookAlert(new_episodes, webHooks):
    for webhook in webHooks:
        for episode in new_episodes:
            print("Found new episode: " + episode)
            logger.info("Found new episode: " + episode)
            data = {"content": "Ny episode: " + episode}
            try:
                requests.post(webhook, json=data)
            except Exception as e:
                print("Could not post webhook!")
                logger.error(f"Could not post webhook: {e}")
                sys.exit(1)

# Termination print
def termination_handler(signal, frame):
    print("The script was terminated")
    logger.warning("The script was terminated")
    for webhook in webHooks:
        data = {"content": "The script was terminated!"}
        requests.post(webhook, json=data)
    sys.exit(1)

# Register the termination handler function
signal.signal(signal.SIGINT, termination_handler)
signal.signal(signal.SIGTERM, termination_handler)

if __name__ == '__main__':
    if initialFlag:
        print("The script was started")
        logger.info("The script was started")
        data = {"content": "The script was started"}
        try:
            for webhook in webHooks:
                requests.post(webhook, json=data)
        except Exception as e:
            logger.exception(f"Failed to post to webhook:\n {e}")
            sys.exit(1)
        feedURLs = getFeedURLs()
        episodes = parseFeeds(feedURLs)
        webHooks = getwebhookURLs()
        webHookAlert(episodes, webHooks)
        old_episodes = episodes[:]
        initialFlag = False

    while True:
        episodes = parseFeeds(feedURLs)
        new_episodes = checkDuplicates(episodes, old_episodes)
        if new_episodes:
            webHookAlert(new_episodes, webHooks)
            old_episodes = episodes[:]
        print("Looked for new episodes at time: " + time.strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("Looked for new episodes")
        # Check for new episodes every hour
        time.sleep(3600)
        