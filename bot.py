import praw
import time
from praw.errors import RateLimitExceeded
from praw.objects import MoreComments
from requests.exceptions import HTTPError
from responses import responses

queue = [[], [], []]
seen = []

r = praw.Reddit('Khaled 0.9.1 by JoelOtter')


def process_queue():
    for i, q in enumerate(queue):
        for j in range(5):
            if len(q) == 0:
                break
            c = q[-1]
            com = r.get_submission(c).comments[0]
            for rep in com.replies:
                if "dj khaled" in rep.body.lower():
                    try:
                        newc = rep.reply(responses[i])
                    except RateLimitExceeded:
                        break
                    queue[i].remove(c)
                    if i < 2:
                        queue[i + 1].insert(0, newc.permalink)
                    print "Repled with comment " + newc.permalink
                    break


def process_new():
    subr = r.get_subreddit('all')
    for sub in subr.get_hot(limit=100):
        if sub.permalink in seen:
            break
        for c in sub.comments:
            if isinstance(c, MoreComments):
                continue
            text = c.body.lower()
            if "dj khaled" in text:
                try:
                    newc = c.reply('Say my name, baby.')
                except RateLimitExceeded:
                    break
                seen.append(sub.permalink)
                with open('./seen.txt', 'a') as s_f:
                    s_f.write(sub.permalink + '\n')
                queue[0].insert(0, newc.permalink)
                print 'New comment ' + newc.permalink
                break


# Initialise
with open('./seen.txt', 'r') as f:
    for line in f:
        seen.append(line)
r.login()

while True:
    try:
        process_queue()
        process_new()
    except HTTPError:
        continue
    time.sleep(60)
