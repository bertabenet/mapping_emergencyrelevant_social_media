import json
from collections import Counter
import re
import math
import scipy.cluster.hierarchy as sch
from sklearn.neighbors import NearestCentroid

# compute center of bounding box
def rectangle_center(point):
    x1 = point[0][0]; x2 = point[2][0]
    y1 = point[0][1]; y2 = point[2][1]
    xCenter = (x1 + x2) / 2
    yCenter = (y1 + y2) / 2
    return [xCenter, yCenter]

# compute distance between two points
def distance(p1, p2):
    return math.sqrt(((p1[0]-p2[0])**2)+((p1[1]-p2[1])**2))

def dump_data(dict_A, dict_B1, dict_B2, dict_Z, timerange):
    with open("public/data/" + timerange + "/geojson_clustering_classA.json", 'w') as json_file:
        json.dump(dict_A, json_file)

    with open("public/data/" + timerange + "/geojson_clustering_classB1.json", 'w') as json_file:
        json.dump(dict_B1, json_file)
        
    with open("public/data/" + timerange + "/geojson_clustering_classB2.json", 'w') as json_file:
        json.dump(dict_B2, json_file)
        
    with open("public/data/" + timerange + "/geojson_clustering_classZ.json", 'w') as json_file:
        json.dump(dict_Z, json_file)


def process_clusters(timerange):
    # READ DATA
    with open("data/geojson_last_" + timerange + ".json") as g_json:
        data = json.load(g_json)
        
    if len(data) == 0:
        dump_data([], [], [], [], timerange)
        return 0

    # PROCESS DATA PRE-CLUSTER
    admins = ["Barcelona","Barcelone","Girona","Gérone","Gerona","Lleida","Lérida","Tarragona"]
    municipis = []

    with open("resources/municipis.txt", "r") as f:
        for line in f:
            if line[:4] == "| [[":
                line = line[4:]
                match = re.search('\]', line)
                municipis.append(line[:match.start()])
                
    place_types = ['city', 'neighborhood', 'poi', 'admin']
    map_admin = {"Barcelona": "Barcelona", "Barcelone": "Barcelona", "Girona": "Girona", "Gérone": "Girona", "Gerona": "Girona", "Lleida": "Lleida", "Lérida": "Lleida", "Tarragona": "Tarragona"}

    # CLUSTER
    dict_A = {"type":"FeatureCollection", "features":[]}
    dict_B1 = {"type":"FeatureCollection", "features":[]}
    dict_B2 = {"type":"FeatureCollection", "features":[]}
    dict_Z = {"type":"FeatureCollection", "features":[]}

    distance = 0.15
    distance2 = 0.1

    # 1. CLUSTER ALL
    # retrieve all coordinates
    coord_list = []
    tweets = []
    for tweet in data:
        try: place = tweet["place"]["name"]         # retrieve tweet's place
        except: continue
            
        # discard those cities that are not in Catalunya
        if (tweet["place"]["place_type"] == "city") and place not in municipis: continue
        # only take into account cities, neighbourhoods and points of interest
        if tweet["place"]["place_type"] not in place_types: continue
            
        coords = rectangle_center(tweet["place"]["bounding_box"]["coordinates"][0])
        coord_list.append(coords)
        tweets.append(tweet)

    # retrieve tweets at admin level
    out_tweets = []
    for tweet in data:
        try:
            if (tweet["place"]["place_type"] == "admin") and (tweet["place"]["name"] in admins):  out_tweets.append(tweet)
        except: continue
        if len(out_tweets) == 10: break
        
    # cluster tweets
    features = coord_list
    labels = sch.fcluster(sch.linkage(features), distance, criterion='distance')

    # compute centroids
    if len(Counter(labels)) > 1:
        clf = NearestCentroid()
        clf.fit(features, labels)
        centroids = clf.centroids_
    else: centroids = features

    # classify tweets between B1 and A classes
    B1_clusters = []  # list of clusters with only one tweet
    A_clusters = {}   # key: cluster label, value: centroid of cluster
    for key in Counter(labels):
        if Counter(labels)[key] == 1: B1_clusters.append(key)
        else:
            A_clusters[key] = centroids[key-1]
            
        
    aux_A = {}      # key: cluster label, value: body of tweet
    tweets_A = {}   # key: cluster label, value: tweet
    for tweet, label in zip(tweets, labels):
        place = tweet["place"]["name"]
        user = tweet["user"]["screen_name"]
        try: text = tweet["full_text"]
        except: text = tweet["text"]
            
        # create B1 dictionary
        if label in B1_clusters:
            aux = {"type":"Feature",
                   "properties":{"title": place,
                                 "entries": [{"place": place, "user": user, "text": text}],
                                 "cluster_counter": 1,
                                  "marker_counter": 0},
                   "geometry": {"type": "Point",
                                "coordinates":rectangle_center(tweet["place"]["bounding_box"]["coordinates"][0])}}
            
            dict_B1["features"].append(aux)
        
        # create A dictionary
        elif label in A_clusters.keys():
            clust = label
            try: tweets_A[label].append(tweet)
            except: tweets_A[label] = [tweet]
                
            try:
                aux_A[label]["properties"]["cluster_counter"] += 1
                aux_A[label]["properties"]["entries"].append({"place": place, "user": user, "text": text})
            except:
                aux_A[label] = {"type": "Feature",
                               "properties": {"title": "",
                                              "entries": [{"place": place, "user": user, "text": text}],
                                             "cluster_counter": 1,
                                             "marker_counter": 0},
                               "geometry": {"type": "Point",
                                           "coordinates": list(A_clusters[label])}}
        
        
    # 2. CLUSTER CLASS A
    for k, v in tweets_A.items():
        coord_list = []
        for tweet in v:
            coords = rectangle_center(tweet["place"]["bounding_box"]["coordinates"][0])
            coord_list.append(coords)
        
        features = coord_list
        labels = sch.fcluster(sch.linkage(features), distance2, criterion='distance')
        
        marker_counter = 0
        # classify tweets in B2
        B2_clusters = []  # list of clusters with only one tweet
        for key in Counter(labels):
            if Counter(labels)[key] == 1:
                B2_clusters.append(key)
                marker_counter += 1
                
        for tweet, label in zip(v, labels):
            place = tweet["place"]["name"]
            user = tweet["user"]["screen_name"]
            try: text = tweet["full_text"]
            except: text = tweet["text"]

            # create B2 dictionary
            if label in B2_clusters:
                aux = {"type":"Feature",
                       "properties":{"title": place,
                                     "entries": [{"place": place, "user": user, "text": text}],
                                     "cluster_counter": 1,
                                     "marker_counter": 0},
                       "geometry": {"type": "Point",
                                    "coordinates":rectangle_center(tweet["place"]["bounding_box"]["coordinates"][0])}}

                dict_B2["features"].append(aux)
                aux_A[k]["properties"]["marker_counter"] += 1
                
    # create Z dictionary
    aux_Z = {}
    for tweet in out_tweets:
        place =  map_admin[tweet["place"]["name"]]
        user = tweet["user"]["screen_name"]
        try: text = tweet["full_text"]
        except: text = tweet["text"]
        
        try:
            aux_Z[place]["properties"]["cluster_counter"] += 1
            aux_Z[place]["properties"]["entries"].append({"place": "-", "user": user, "text": text})
        except:
            aux_Z[place] = {"type":"Feature",
                       "properties":{"title": place,
                                     "entries": [{"place": "-", "user": user, "text": text}],
                                     "cluster_counter": 1,
                                     "marker_counter": 0},
                       "geometry": {"type": "Point",
                                    "coordinates": "-"}}
            
    for k, v in aux_Z.items():
        dict_Z["features"].append(v)
        
    # retrieve most common place and add it to the A dictionary
    for k, v in aux_A.items():
        l = [t["place"]["name"] for t in tweets_A[k]]
        place = Counter(l).most_common()[0][0]
        v["properties"]["title"] = place
        v["properties"]["cluster_counter"] -= v["properties"]["marker_counter"]
        dict_A["features"].append(v)
        
    # DUMP DICTIONARIES
    dump_data(dict_A, dict_B1, dict_B2, dict_Z, timerange)

    print("[geoJSON_manager.py...] Created file for \"{}\" range.".format(timerange))
        
if __name__ == "__main__":
    process_clusters("hour")
    process_clusters("day")
    process_clusters("week")
