# Mapping Emergency-Relevant Social Media

## Treball de fi de grau de: Berta Benet i Cugat
## Director: Carlos Alberto Alejandro Castillo Ocaranza

#### Year 2020-2021
<img src="resources/images/upf_logo.png" alt="Universitat Pompeu Fabra, Escola d'Enginyeria" width="400"/>

[Download paper](https://drive.google.com/uc?export=download&id=1PlbtJIB-NN8F7z3de8_1UEocbQSCLXHe)

------------------------

## Pre-requisites

### Python

The python libraries needed to run this repository are the following:

- python-twitter
- redis
- chronometer
- pymongo
- pytz
- Shapely
- simpletransformers
- torch

To see the exact requirements see [requirements.txt](requirements.txt).

### Twitter API

To be able to collect tweets, you need to create a Twitter Developer account. In order to do so, you must first go to the [Twitter Developer Portar](https://developer.twitter.com/en/portal/dashboard) and login with your [Twitter](https://twitter.com/home) account (in the case you do not have one you can create it by free). Then go to the **Projects & Apps** tab and below **Standalone Apps** click the button that says **+ Create App**.

<img src="resources/images/screenshot 1 2.png" alt="Screenshot 1 and 2">

Then name the App with an understandable title. When clicking the **Next** button, the app will be created and will appear on the App list. Finally enter the App and click on the **Keys and Tokens** tab. By clicking **Regenerate** on the **Consumer Keys** and **Generate** on **Authentication Tokens** you will have access to the `consumer_key`, `consumer_secret`, `access_token_key` and `access_token_secret` that you will have to enter on the [config.ini](resources/config.ini) file. 

<img src="resources/images/screenshot 3 4.png" alt="Screenshot 3 and 4">


### Redis

The collector step on this project uses the Redis database to store all real-time captured tweets. In order to install the Redis database refer to the official [Redis documentation](https://redis.io).

### MongoDB

The persister step uses the MongoDB database to move the tweets from the Redis database to MongoDB. In order to install MongoDB refer to the official [MongoDB documentation](https://www.mongodb.com).

## Source code

The source code can be found on the [source](source) directory. In order to run the main pipeline the file [main.py](source/main.py) has to be run from the parent directory. The specifications (parameters) for each file such as the API twitter keys or the persister batch size can be found and changed on the [config.ini](resources/config.ini) file. 

#### Call main pipeline
```
python source/main.py
```

#### Call manual labeling
```
python source/classifier.py create new_csv_file.csv   # create mode
python source/classifier.py consume new_csv_file.csv  # consume mode
```

Due to its heavy size, the model used cannot be found in this repository. To download it just click the following link below.


## Download model

Download the model from [here](https://drive.google.com/uc?export=download&id=11DLldxP1Ll3vqX4CxrQMKF5VdiY11TdS).

## Visualization

The files for the visualization are in the [public/](public) directory. The visualization will display itself by running the [index.html](public/index.html) file.

The demo data found in [data/](data) and [public/data/](public/data) is a sample of 1411 tweets that were positively classified by our algorithm. These posts were provided by Lorini et al. (2019). These tweets' timestamps are between January 19th 2020 and January 24th 2020.

## Training sets

The training set can found in [labeled\_training\_sets/](labeled_training_sets). Inside this folder there are 86 files that correspond to 21 extracted from the area of Catalonia and 63 coming from the area of Spain. The 2 remaning files which are [ca\_label.csv](labeled_training_sets/ca_label.csv) and [es\_label.csv](labeled_training_sets/es_label.csv) contain tweets in Catalan and Spanish, respectively, extracted during the Gloria storm and were provided by Vitiugin & Castillo (2019).

_____

## References

Lorini, V., Castillo, C., Dottori, F., Kalas, M., Nappo, D., & Salamon, P. (2019). Integrating social media into a pan-European flood awareness system: A multilingual approach. *Proceedings of the International ISCRAM Conference, 2019-May*(May 2019), 646–659.

Vitiugin, F., & Castillo, C. (2019). Comparison of social media in English and Russian during emergencies and mass convergence events. *Proceedings of the International ISCRAM Conference, 2019-May*(May), 857–866.


