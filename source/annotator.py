from datetime import datetime, timedelta
import pytz
import pickle
import configparser
from pymongo import MongoClient
from chronometer import Chronometer
import os
import random
import json
import time
from shapely.geometry import Polygon, Point
import sys

from simpletransformers.classification import ClassificationModel, ClassificationArgs
from scipy.special import softmax
from geoJSON_manager import process_clusters

# from a string create a datetime object
def create_datetime(string, fmt):
    return datetime.strptime(string, fmt)
     
# create range of time where to annotate tweets
def set_minmax_datetimes(min_str, max_str, fmt = "%Y-%m-%d %H:%M:%S"):
    min_datetime = create_datetime(min_str, fmt)
    max_datetime = create_datetime(max_str, fmt)

    tmz_catalunya = pytz.timezone('Europe/Madrid')
    min_datetime = tmz_catalunya.localize(min_datetime)
    max_datetime = tmz_catalunya.localize(max_datetime)
    
    return min_datetime, max_datetime
    
# create range of time given a timerange
def set_minmax_datetimes_timerange(timerange):

    max_datetime = pytz.utc.localize(datetime.utcnow())
    
    if timerange == "hour": return max_datetime - timedelta(hours = 1), max_datetime
    elif timerange == "day": return max_datetime - timedelta(days = 1), max_datetime
    elif timerange == "week": return max_datetime - timedelta(days = 7), max_datetime
    
    else: return None, None

def load_model(model_name):
    model_args = ClassificationArgs()
    model_args.multiprocessing_chunksize = 1
    return ClassificationModel("deberta", model_name, use_cuda = True, args=model_args)
    
def predict_prob(model, text):
    predictions, raw_outputs = model.predict(text)
    probabilities = softmax(raw_outputs, axis=1)
    return [row[1] for row in probabilities]
    
    
def random_points_within(poly, num_points):
    min_x, min_y, max_x, max_y = poly.bounds

    points = []

    while len(points) < num_points:
        random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            points.append(random_point)

    return points

def annotate(timerange):
    print("PROCESS {} IN ANNOTATOR".format(os.getpid()))
    max_prob = 0
    
    if(timerange != "hour" and timerange != "day" and timerange != "week"):
        print("[annotator.py...] Not a valid timerange... exiting annotator")
        return 1
        
    config = configparser.ConfigParser()
    config.read("resources/config.ini")

    client_name = config["DEFAULT"]["mongoDB client"]
    batch_size = int(config["ANNOTATOR"]["batch size"])
    model_name = config["ANNOTATOR"]["model"]

    client = MongoClient()
    db = client[client_name]

    # load model
    model = load_model(model_name)

    min_datetime, max_datetime = set_minmax_datetimes_timerange(timerange)

    # initialize geoJson dict
    place_types = ['city', 'neighborhood', 'poi']
    max_predicting_batch = 300

    while True:
        lst = []
        to_predict = []
        final_predictions = []

        last_t = 0
        tweet_counter = 0
        
        inverted_col = db.collected.find({"$query": {}, "$orderby": {"$natural" : -1}})
        point_list = []
        for tweet in inverted_col:
            #if tweet_counter >= batch_size: break
            
            try: text = tweet["full_text"]
            except: text = tweet["text"]
            
            tweet_time = datetime.strptime(tweet["created_at"], '%a %b %d %H:%M:%S %z %Y')
            if tweet_time < min_datetime or tweet_time > max_datetime: break
            #print(tweet_time.strftime("%Y-%m-%d %H:%M:%S"))
            
            # if the key place exists
            if "place" in tweet.keys():
                # discard the ones that are not in Spain
                if tweet["place"]["country_code"] != "ES": continue
                
                # only take into account cities, neighbourhoods and points of interest
                if tweet["place"]["place_type"] not in place_types: continue
                
                tweet_counter += 1
                
                tweet.pop("_id", None)
                lst.append(tweet)
                to_predict.append(text)
                if len(to_predict) == max_predicting_batch:
                    predictions = predict_prob(model, to_predict)
                    final_predictions += predictions
                    to_predict = []
                
        if(len(to_predict) > 0):
            predictions = predict_prob(model, to_predict)
            final_predictions += predictions
            
        for l, pred in zip(lst, final_predictions):
            l["crisis_prob"] = pred
            
        lst = sorted(lst, key=lambda k: k["crisis_prob"], reverse=True)
        for i, l in enumerate(lst):
            if l["crisis_prob"] < 0.5:
                min_prob_index = i
                lst = lst[:min_prob_index]
                break
                    
        # sort list by higher crisis prob
        if len(lst) > batch_size:
            lst = sorted(lst, key=lambda k: k["crisis_prob"])[:batch_size]
        
        with open("data/geojson_last_" + timerange + ".json", 'w') as json_file:
            json.dump(lst, json_file) #json.dump(dict_, json_file)
            
            
        print("[annotator.py...] File updated. Max probability in file: {:.2f}".format(max_prob))
        
        # call geoJSON manager
        process_clusters(timerange)
        
        time.sleep(60*60)
        
        
if __name__ == "__main__":
    annotate("hour")
    annotate("day")
    annotate("week")
