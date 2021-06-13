import twitter
import redis
import configparser
from chronometer import Chronometer
import os

def collect():
    print("PROCESS {} IN COLLECTOR".format(os.getpid()))
    config = configparser.ConfigParser()
    config.read("resources/config.ini")

    # twitter credentials
    credentials = config["CREDENTIALS"]
    api = twitter.Api(consumer_key = credentials["consumer_key"],
                          consumer_secret = credentials["consumer_secret"],
                          access_token_key = credentials["access_token_key"],
                          access_token_secret = credentials["access_token_secret"])

    # location's coordinates
    bb_coords = config["BOUNDING BOX CAT"]
    #bb_coords = config["BOUNDING BOX ESP"]
    #bb_coords = config["BOUNDING BOX USA"]
    location_bounding_box = [bb_coords["coor 1"], bb_coords["coor 2"], bb_coords["coor 3"], bb_coords["coor 4"]] # Catalunya's bounding box

    queue_name = config["DEFAULT"]["queue name"]
    redis_db = int(config["DEFAULT"]["redis db"])

    # twitter stream
    stream = api.GetStreamFilter(locations=location_bounding_box)

    tweets = []
    r = redis.Redis(db = redis_db)

    last_t = 0
    with Chronometer() as t:
        for line in stream:
            try:
                tweet = twitter.Status.NewFromJsonDict(line)
            
                if(int(float(t)) % 10 == 0 and int(float(t)) != last_t):
                    print("[collector.py...] Total tweets:", r.llen(queue_name))
                    last_t = int(float(t))
                r.rpush(queue_name, str(tweet))
            except:
                continue


if __name__ == '__main__':
    collect()


