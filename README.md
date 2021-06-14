# Mapping Emergency-Relevant Social Media

## Treball de fi de grau de: Berta Benet i Cugat
## Director: Carlos Alberto Alejandro Castillo Ocaranza

#### Year 2020-2021
<img src="resources/upf_logo.png" alt="Universitat Pompeu Fabra, Escola d'Enginyeria" width="400"/>

[Download paper](https://drive.google.com/uc?export=download&id=1fy_rW9fMuLHP4-LVPmgxlWrI2weW_0s7)

------------------------

## Pre-requisites

The python libraries needed to run this repository are the following:

- python-twitter
- redis
- chronometer
- pymongo
- pytz
- Shapely
- simpletransformers
- torch

To see the exact requirements see [requirements.txt](requirements.txt)


## Source code

The source code can be found on the [source](source) directory. In order to run the main pipeline the file [main.py](source/main.py) has to be run from the parent directory. The specifications for each file such as the API twitter keys or the persister batch size can be found and changed on the [config.ini](resources/config.ini) file. 

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

The files for the visualization are in the [public](public) directory. The visualization will display itself by running the [index.html](public/index.html) file.

______

## Author's note

The data currently on the repo corresponds to a sample of tweets extracted from the Gloria storm that occurred between January 19th 2020 to January 24th 2020.

