# Setup

## To start

1) Install Dependencies

        $ npm install 

2) Run Server 

        $ port=8080 db_name="svt" db_url="mongodb://host:port/" npm start 


# API

## 1. Query Video Repository 

Returns a list of videos and related video information. The maximum amount of videos returned in one query is 200 to scroll between them one can use the page operator. The limit operator restricts how many videos can be returned.

#### HTTP Request

    GET: "/videos"

Example: ```/videos?show=vår tid är nu&season=1&prediction=true```

#### Query Parameters

        &url=<string>  
        &show=<string>
        &show_id=<string>
        &title=<string>
        &season=<int>
        &episode=<int>
        &prediction=<bool>
        &annotation=<bool>      
        &limit=<int>
        &page=<int>

#### HTTP Response 

    [{
        "downloaded": true,
        "introAnnotation": {
            "end": 222.0,
            "start": 209.5
        },
        "introPrediction":{
            "end": 220.0,
            "start": 211.0
        },
        "preprocessed": true,
        "season": 1,
        "episode": 2,
        "show": "exit",
        "showId": "exit",
        "title": "Avsnitt 2",
        "url": "https://www.svtplay.se/video/24136954/exit/exit-avsnitt-2"
    }]

---

## 2. Set Intro 

Allows for mannual annotation of intro sequences of videos matching the query arguments. Be careful to not override previously done work. The query argument must contain at least the video url or the show name or show id. 

#### HTTP Request
    POST: "/videos/set/intro"

Example: ```/videos/set/intro?url=https://www.svtplay.se/video/24206422/var-tid-ar-nu/var-tid-ar-nu-sasong-3-vip```

#### Query Parameters
    &url=<string>   
    &show=<string>
    &show_id=<string>
    &title=<string>
    &season=<int>
    &episode=<int>
#### Content
    BODY: { "start": <float>, "end": <float> }

---
## 3. Request Intro Prediction 

Requests the server to perform an intro prediction on videos with matching query arguments. Returns a service process instance with an unique id. The id can be used to periodically query for the result.

#### HTTP Request
    GET: "/request/predict-intro"
    
Example: ```/services/request/predict-intro?url=https://www.svtplay.se/video/23536930/allt-jag-inte-minns/allt-jag-inte-minns-sasong-1-avsnitt-1```

#### Query Parameters
    &url=<string>  

#### HTTP Response 

    {
        "_id": "5e1a8d0dd1b9dc1008af6731",
        "process": "predict-intro",
        "args": [
            "https://www.svtplay.se/video/23536930/allt-jag-inte-minns/allt-jag-inte-minns-sasong-1-avsnitt-1"
        ],
        "started": null,
        "result": null,
        "status": "pending",
        "executionTime": 0,
        "startDelay": 0
    }

---
## 4. Query Service Processes 

Returns requested service processes matching the query arguments. To extract a successful result simply poll the service-id and wait for the result to not be null. Notice that status has 4 different states: "pending", "working", "finished" and "halted". Halted indicating that the process was unexpectadly interrupted. 

Calculating where the intro is may take a few seconds or a couple of minutes depending on how much preprocessing has been done on related videos of the same show and season.

#### HTTP Request
    GET: "/services"
    
Example: ```/services?id=5e1a8c9b9e7286458c704010```

#### Query Parameters
    &id=<string>  

#### HTTP Response 

    [{
        "_id": "5e1a8c9b9e7286458c704010",
        "process": "predict-intro",
        "args": [
            "https://www.svtplay.se/video/23536930/allt-jag-inte-minns/allt-jag-inte-minns-sasong-1-avsnitt-1"
        ],
        "started": "2020-01-12T03:03:55.694Z",
        "result": {
            "prediction": {
                "start": 40.2,
                "end": 116.7
            }
        },
        "status": "finished",
        "executionTime": 6.333,
        "startDelay": 0.033
    }]

---

## 5. Rebuild Dataset 

This will retrain the model based on all existing annotated videos previously stored. Notice that this is a very long process and may take a few hours to complete. 

#### HTTP Request
    GET: "/services/request/rebuild"
    
#### HTTP Response 

    {
        "_id": "rebuild",
        "process": "rebuild",
        "args": [
            ""
        ],
        "ip": "::1",
        "requested": "2020-01-12T19:20:34.986Z",
        "started": "2020-01-12T19:20:34.987Z",
        "ended": null,
        "result": null,
        "status": "working",
        "startDelay": 0.001,
        "executionTime": 12.185
    }