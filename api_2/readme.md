# Setup

## To start

1) Install Dependencies

        $ npm install 

2) Run Server 

        $ port=8080 db_name="svt" db_url="mongodb://host:port/" npm start 


# Resource: Videos  

## Query Video Repository 

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
        "introPrediction": null,
        "preprocessed": true,
        "season": 1,
        "episode": 2,
        "show": "exit",
        "showId": "exit",
        "title": "Avsnitt 2",
        "url": "https://www.svtplay.se/video/24136954/exit/exit-avsnitt-2"
    }]

---

## Set Intro 

#### HTTP Request

    POST: "/videos/set/intro?url=<string>"
    BODY: { "start": <float>, "end": <float> }