from pymongo import MongoClient
import re
import pandas as pd
import configparser
import sys
import json

def sample_training_set(db, batch_size, filename):
    # define crisisLex vocabulary
    crisisLex = []
    path = "resources/"
    with open(path + "CrisisLexRec.txt", 'r') as f:
        for line in f:
            crisisLex.append(line[:-1])
            
    id_list = []   # keep track of the randomly selected tweets

    # create empty dataframe
    df = pd.DataFrame(columns = ["id", "text", "crisis_label"])

    count = 0
    for i in range(batch_size):
        found = False
        while(not found):
            count += 1
            
            # select random tweet
            rdm_tweet = list(db.collected.aggregate([{ "$sample": { "size": 1 } }]))[0]

            # check that tweet is not already selected
            if(rdm_tweet["id"] not in id_list):

                # define tweet's text
                if "full_text" in rdm_tweet.keys(): text = rdm_tweet["full_text"]
                else: text = rdm_tweet["text"]

                # find if it has any match with the crisisLex list, if it does add it to the dataframe
                for vocab in crisisLex:
                    search = re.search(vocab, text.lower())
                    if(search != None):
                        found = True
                        id_list.append(rdm_tweet["id"])
                        if len(id_list) % 1 == 0:
                            print("[classifier.py...]", len(id_list), "tweets")
                        
                        # add row to dataframe
                        df = df.append({"id": rdm_tweet["id"], "text": text,"crisis_label": 0}, ignore_index=True)
                        break
                        
    print("In order to create a file of", batch_size, "entries, I had to visit a total of", count, "tweets")
    # write dataframe into csv
    df.to_csv("results/" + filename)


def consume_labeled_training_set(db, filename):
    # read sample_training_set.csv
    df = pd.read_csv("results/" + filename, sep = ";")
    for index, row in df.iterrows():
        try:
            tweet = json.loads(row.to_json())                           # transform the tweet into a json
            
            found = db.collected.find_one({"id_str": str(tweet["id"])}) # find tweet on collected database
            found["crisis_label"] = tweet["crisis_label"]               # add crisis label to whole tweet
            
            db.manually_annotated.insert_one(found)                     # insert tweet to manually annotated
            db.collected.delete_one({"id": tweet["id"]})                # delete tweet from collected if possible
            
        except:
            continue
            
    print("File consumed!")
           
            
config = configparser.ConfigParser()
config.read("resources/config.ini")

client_name = config["DEFAULT"]["mongoDB client"]       # define MongoDB's database name
batch_size = int(config["CLASSIFIER"]["batch size"])    # define batch size
client = MongoClient()
db = client[client_name]


if len(sys.argv) > 2:
    if sys.argv[1] == "create":                         # create csv file
        sample_training_set(db, batch_size, sys.argv[2])
        
    elif sys.argv[1] == "consume":                      # read csv file
        consume_labeled_training_set(db, sys.argv[2])
    else:
        print("[classifier.py...]", sys.argv[1], "is not a valid argument")
else:
    print("[classifier.py...] Not enough arguments. Valid arguments: create / consume + filename")


