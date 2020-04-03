import praw
import json
class class1(object):
    """Start of program and experimentation"""

    reddit = praw.Reddit('IndexSubreddits')
    #print(reddit.read_only, reddit.config.client_id, reddit.config.client_secret, reddit.config.user_agent, reddit.config.username, reddit.config.password)

    """
    reads json file that contains name of subreddits to be searched
    might be easier to just use a txt file? 
    """
    json_subreddits = ""
    with open('subreddits.json') as json_file:
        json_subreddits = json.load(json_file)
        

    """
    puts all subreddits into a list
    """
    listOfSubreddits = []
    for sub in json_subreddits["subreddit"]:
        listOfSubreddits.append(sub["name"])

    """
    loops through each subreddit
    currently grabs the 10 threads in "hot" for each sub
    """
    for subreddit in listOfSubreddits:
        print(subreddit)
        for submission in reddit.subreddit(subreddit).hot(limit=10):
            print(submission.title)

    """
    """