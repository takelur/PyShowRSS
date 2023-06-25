import feedparser
import time
import requests
import signal

# Checks if the script is in the initial run
initialFlag = True
# List of feed URLs
feedURLs = []
# List of webhook URLs
webHooks = []
# List of old episodes
old_episodes = []


def getFeedURLs():
    feeds = []
    try:
        with open('feeds.txt', 'r') as f:
            t_feeds = f.readlines()
    except IOError:
        print('Feil: feeds.txt ikke funnet')
        exit()
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
        with open('webhooks.txt', 'r') as f:
            t_webHooks = f.readlines()
    except IOError:
        print('Feil: webhooks.txt ikke funnet')
        exit()
    for webhook in t_webHooks:
        webHooks.append(webhook.strip("\n"))
    return webHooks

# Funker på Discord
def webHookAlert(new_episodes, webHooks):
    for webhook in webHooks:
        for episode in new_episodes:
            print("New episode: " + episode)
            data = {"content": "Ny episode: " + episode}
            requests.post(webhook, json=data)

# Termination print
def termination_handler(signal, frame):
    for webhook in webHooks:
        data = {"content": "Scriptet er avsluttet"}
        requests.post(webhook, json=data)
        print("Scriptet er avsluttet")

# Register the termination handler function
signal.signal(signal.SIGINT, termination_handler)
signal.signal(signal.SIGTERM, termination_handler)

if __name__ == '__main__':
    if initialFlag:
        feedURLs = getFeedURLs()
        episodes = parseFeeds(feedURLs)
        webHooks = getwebhookURLs()
        webHookAlert(episodes, webHooks)
        old_episodes = episodes[:]
        initialFlag = False
        data = {"content": "Scriptet er startet"}
        for webhook in webHooks:
            requests.post(webhook, json=data)
        print("Scriptet er startet")

    while True:
        episodes = parseFeeds(feedURLs)
        new_episodes = checkDuplicates(episodes, old_episodes)
        if new_episodes:
            webHookAlert(new_episodes, webHooks)
            old_episodes = episodes[:]
        print("Sjekka etter nye episoder kl: " + time.strftime("%H:%M:%S"))
        time.sleep(21600)
        