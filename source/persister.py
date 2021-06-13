import redis
import json
import configparser
import math
from chronometer import Chronometer
from pymongo import MongoClient
import os
import time

# Transform string of bytes to json format
def from_bytes_to_json(bytes_string):
    my_json = bytes_string.decode('utf8')
    data = json.loads(my_json)
    return data

def persist():
    print("PROCESS {} IN PERSISTER".format(os.getpid()))
    config = configparser.ConfigParser()
    config.read("resources/config.ini")

    redis_db = int(config["DEFAULT"]["redis db"])
    client_name = config["DEFAULT"]["mongoDB client"]
    max_per_hour = int(config["PERSISTER"]["max persisted per hour"])
    if(max_per_hour == 0): max_per_hour = math.inf

    r = redis.Redis(db = redis_db)
    client = MongoClient()
    db = client[client_name]

    count = db.collected.estimated_document_count()
    temp_count = 0

    # pop from Redis and insert to MongoDB
    with Chronometer() as t:
        while(True):
            # reset chronometer
            if(float(t) >= 60*60):     # hour
                temp_count = 0
                t.reset()
        
            if(temp_count <= max_per_hour):    # hour
                entry = r.lpop("collector")
                if(entry != None):
                    # insert tweet without labeling to collected
                    result = db.collected.insert_one(from_bytes_to_json(entry))
                    
                    # if the tweet is inserted correctly to the mongoDB, increase temporal counter
                    if(result.acknowledged): temp_count += 1
                        
                    # keep track of tweets in the database
                    count = db.collected.estimated_document_count()
                    if(count % 10 == 0): print("[persister.py...] Total tweets in mongoDB:", count)
            
            else:
                s_secs = 60 - int(float(t))
                print("[persister.py...] Sleeping for {} seconds".format(s_secs))
                time.sleep(s_secs)


if __name__ == '__main__':
    persist()
