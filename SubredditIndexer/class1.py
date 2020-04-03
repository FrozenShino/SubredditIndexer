import praw
import json
import sqlite3
from sqlite3 import Error

"""
global vars
"""
DB_NAME = "TestTableTwo.db"
LIMIT = 2000

"""
should probably be moved into their own class/module/package (gotta remember how that works in python...)
change so that an instance of the subreddit is passed in instead of the 'reddit' object? need to learn more about methods/functions, classes and passing vars
need a method that checks whether a specific submission is already in the able, and a counter
    exit loop/stop trying to insert after counter == 3
"""

def get_from_hot(reddit, conn, table_name):
    
    subreddit = reddit.subreddit(table_name)
    #for submission in reddit.subreddit(table_name).hot(limit=LIMIT):
    for submission in subreddit.hot(limit=LIMIT):
        insert_row(conn, subreddit, submission.id, submission.title, submission.name, submission.permalink, submission.shortlink, subreddit.name, submission.url, "/r/" + subreddit.display_name, "hot", submission.created_utc, " ", False, False)

def get_from_new(reddit, conn, table_name):
    
    subreddit = reddit.subreddit(table_name)
    for submission in reddit.subreddit(table_name).new(limit=LIMIT):
        insert_row(conn, subreddit, submission.id, submission.title, submission.name, submission.permalink, submission.shortlink, subreddit.name, submission.url, "/r/" + subreddit.display_name, "new", submission.created_utc, " ", False, False)

def get_from_rising(reddit, conn, table_name):
    
    subreddit = reddit.subreddit(table_name)
    for submission in reddit.subreddit(table_name).rising(limit=LIMIT):
        insert_row(conn, subreddit, submission.id, submission.title, submission.name, submission.permalink, submission.shortlink, subreddit.name, submission.url, "/r/" + subreddit.display_name, "rising", submission.created_utc, " ", False, False)

def get_from_top(reddit, conn, table_name):
    
    subreddit = reddit.subreddit(table_name)
    for submission in reddit.subreddit(table_name).top(limit=LIMIT):
        insert_row(conn, subreddit, submission.id, submission.title, submission.name, submission.permalink, submission.shortlink, subreddit.name, submission.url, "/r/" + subreddit.display_name, "top", submission.created_utc, " ", False, False)

def get_from_controversial(reddit, conn, table_name):
    
    subreddit = reddit.subreddit(table_name)
    for submission in reddit.subreddit(table_name).controversial(limit=LIMIT):
        insert_row(conn, subreddit, submission.id, submission.title, submission.name, submission.permalink, submission.shortlink, subreddit.name, submission.url, "/r/" + subreddit.display_name, "controversial", submission.created_utc, " ", False, False)

def get_from_gilded(reddit, conn, table_name):
    
    subreddit = reddit.subreddit(table_name)
    for submission in reddit.subreddit(table_name).gilded(limit=LIMIT):
        insert_row(conn, subreddit, submission.id, " ", submission.name, submission.permalink, " ", subreddit.name, " ", "/r/" + subreddit.display_name, "gilded", submission.created_utc, " ", False, False)


def select_data():
    """
        sample of connecting to local sqlite db (archive.db)
        db is created if not present already
        NOT CURRENTLY BEING USED
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
    except Error as e:
        print(e)
    cur = conn.cursor()
    cur.execute("SELECT * FROM Saber")
    rows = cur.fetchall()

    for row in rows:
        print(row)

"""
Really ghetto and questionable method of crafting SQL query so that the table name is a variable
I use one table per subreddit so this is needed, or the list of queries would need to grow as new subs are added to the list/db
Alternatively I supposed I could just use the fact that there is a field for the subreddit name and just leave that as the identifier along with id
TODO: 
One of:
    - add a check to ensure that the table name exists before executing here
    OR
    - modify table schema so that there is just one (massive) table for everything and abandon this mess
- add error handling...
"""
def insert_row(conn, table_name, submission_id, submission_title, submission_name, submission_permalink, submission_shortlink, subreddit_id, submission_url, subreddit_name, filter, epoch_time, converted_timestamp, download_attempted, download_completed):
    try:
        pre = "INSERT INTO %s" %(table_name)
        post = "(id, title, name, permalink, shortlink, subreddit_id, url, subreddit_name_prefixed, filter, epoch_time, converted_time, download_attempted, download_completed) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
        sql = pre + post  
        data = (submission_id, submission_title, submission_name, submission_permalink, submission_shortlink, subreddit_id, submission_url, subreddit_name, filter, epoch_time, converted_timestamp, download_attempted, download_completed)
        res = ""
        cur = conn.cursor()
        res = cur.execute(sql, data)
        conn.commit()
        #print(res)
    except Error as e:
        print(e)


"""
creates a table in the DB for each subreddit if it doesnt already exist
"""
def create_table(conn, nameOfTable):
        res = " "
        #sql = 'CREATE TABLE IF NOT EXISTS %s (id text NOT NULL, title text, subreddit_name text, PRIMARY KEY(id))' %(nameOfTable)
        sql = ('CREATE TABLE %s (id text NOT NULL, title text, name text, permalink text, shortlink text, subreddit_id text, url text, ' +
                                        'subreddit_name_prefixed text, filter text, epoch_time real, converted_time text, download_attempted text, ' +
                                        'download_completed text, PRIMARY KEY(id))') %(nameOfTable)
        #print(sql)
        try:
            cur = conn.cursor()
            res = cur.execute(sql)
        except Error as e:
            print(e)
        finally:
            #print(res)
            print("table %s created" %(nameOfTable))



"""
create a connection to the SQLite DB used to store
info about each thread from each subreddit
"""
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        print("Connection establed to database")
    except Error as e:
        print("Error connecting to database")
        print(e)
        
    return conn


def main():
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
        for subreddit in json_subreddits["subreddit"]:
            listOfSubreddits.append(subreddit["name"])


        """
        establish connection to local sqlite db
        loop through list of desired subreddits and create a table for each in the db if it doesnt already exist
        """
        conn = create_connection()
        for subreddit in listOfSubreddits:
            create_table(conn, subreddit)


        """
        loops through each subreddit
        currently grabs the 10 threads in "hot" for each sub
        maybe move creat_table calls in between the for loops?
        """
        for subreddit in listOfSubreddits:
            get_from_hot(reddit, conn, subreddit)
            get_from_new(reddit, conn, subreddit)
            get_from_top(reddit, conn, subreddit)
            get_from_rising(reddit, conn, subreddit)
            get_from_controversial(reddit, conn, subreddit)
            get_from_gilded(reddit, conn, subreddit)

        conn.close
       
class class1(object):
    print("Starting script...")
    main()

if __name__ == '__main_':
    main()