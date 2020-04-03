import praw
import json
import sqlite3
from sqlite3 import Error



"""
Really ghetto and questionable method of crafting SQL query so that the table name is a variable
I use one table per subreddit so this is needed, or the list of queries would need to grow as new subs are added to the list/db
Alternatively I supposed I could just use the fact that there is a field for the subreddit name and just leave that as the identifier along with id
TODO: 
One of:
    - add a check to ensure that the table name exists before executing here
    OR
    - modify table schema so that there is just one (massive) table for everything and abandon this mess
Also add error handling...
"""
def insert_row(conn, table_name, id, title, subreddit_name):
    try:
        pre = "INSERT INTO %s" %(table_name)
        post = "(id, title, subreddit_name) VALUES (?, ?, ?);"
        sql = pre + post  
        data = (id, title, subreddit_name)
        res = ""
        cur = conn.cursor()
        res = cur.execute(sql, data)
        conn.commit()
        print(res)
    except Error as e:
        print(e)


"""
creates a table in the DB for each subreddit if it doesnt already exist
"""
def create_table(conn, nameOfTable):
        res = " "
        sql = 'CREATE TABLE IF NOT EXISTS %s (id text NOT NULL, title text, subreddit_name text, PRIMARY KEY(id))' %(nameOfTable)
        print(sql)
        try:
            cur = conn.cursor()
            res = cur.execute(sql)
        except Error as e:
            print(e)
        finally:
            print(res)
            print("table %s created" %(nameOfTable))
            #conn.close



"""
create a connection to the SQLite DB used to store
info about each thread from each subreddit
"""
def create_connection():
        conn = None
        try:
            conn = sqlite3.connect("TestTableTwo.db")
            #print(sqlite3.version)
        except Error as e:
            print(e)
        
        return conn


def main():
        """Start of program and experimentation"""

        con = create_connection()
        create_table(con, "fgofanart")
        create_table(con, "saber")


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
            #print(subreddit)
            for submission in reddit.subreddit(subreddit).hot(limit=10):
                print(submission.title)
                insert_row(con, subreddit, submission.id, submission.title, subreddit)

        """
        sample of connecting to local sqlite db (archive.db)
        db is created if not present already
        """
        conn = None
        try:
            conn = sqlite3.connect("archive.db")
        except Error as e:
            print(e)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Saber")
        rows = cur.fetchall()

        #for row in rows:
         #   print(row)

class class1(object):
    main()

if __name__ == '__main_':
    main()