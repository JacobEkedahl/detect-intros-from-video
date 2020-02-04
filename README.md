# detect-intros-from-video
- Created by Jacob Ekedahl and Tiago Redaelli

## About
- This repository displays how to find introductions of tvseries from Svtplay.se automatically.
- Requires python of maximum version 3.7
- Run command from root folder (same directory as lib, src exists)
- All video files will be stored inside temp/videos
- Different types of settings are defined in constants.py

## To start
- git clone https://github.com/JacobEkedahl/detect-intros-from-video
- cd detect-intros-from-video
- pip install -r src/requirements.txt

## Configure MongoDB 
This program requires that you have a connection to a mongodb server. To configure the the database and url connection create a file called '.secret.json' and place it inside the application root directory.

    {
        "dbname": "svt",
        "url": "mongodb://host:port/"
    }

## Build a dataset and create a Hidden Markov Model (Requires mongodb to be running)
- python src/main.py --rebuild

## Start software (two processes running)
- Launch api: python src/main --api
- Start scheduler: python src/main --work                                                              