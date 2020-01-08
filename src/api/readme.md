# Resource: Videos  

## Get Video by URL

Returns a json object containing video information. 

#### HTTP Request

    GET: "/videos/get/url"

#### Query Parameters

    BODY: { "url": "https://www.svtplay.se/video/24136938/exit/exit-avsnitt-1" }

#### HTTP Response 

    {
        "downloaded": true,
        "episode": 2,
        "introAnnotation": {
            "end": 222.0,
            "start": 209.5
        },
        "introPrediction": null,
        "preprocessed": true,
        "season": 1,
        "show": "exit",
        "showId": "exit",
        "title": "Avsnitt 2",
        "url": "https://www.svtplay.se/video/24136954/exit/exit-avsnitt-2"
    }

---

## Get All Videos 

Returns all videos managed by the system. 

#### HTTP Request

    GET: "/videos/get/all"

#### HTTP Response

    {
        "0": {
            "downloaded": true,
            "episode": 1,
            "introAnnotation": {
                "end": 115.0,
                "start": 41.0
            },
            "introPrediction": null,
            "preprocessed": true,
            "season": 1,
            "show": "allt jag inte minns",
            "showId": "allt-jag-inte-minns",
            "title": "Avsnitt 1",
            "url": "https://www.svtplay.se/video/23536930/allt-jag-inte-minns/allt-jag-inte-minns-sasong-1-avsnitt-1"
        },
        ...
    }

---

## Get Videos By Show (and Season) 

Queries for videos by show id and optinally by season index. Example: `/videos/get/var-tid-ar-nu/1`

#### HTTP Request

    GET: "/videos/get/<string:show_id>/<int:season>"

#### HTTP Response

    {
        "0": { ... }, "1": { ... }, ...
    }

---

## Annotate Video Intro 
Allows for manual annotation of video intros. 

#### HTTP Request

    POST: "/videos/set/intro-annotation"

#### Query Parameters

    BODY: { 
        "url": "https://www.svtplay.se/video/24136938/exit/exit-avsnitt-1" 
        "start": 50.5,
        "end": 65.0
    }
    
#### HTTP Response 

    { "success": True }

## Get Video Prediction 
Returns a prediction of a specified URL, if none exists this request may take some time to complete. 

    GET: "/videos/get/intro-prediction"

#### Query Parameters

    BODY: { "url": "https://www.svtplay.se/video/24136938/exit/exit-avsnitt-1" }

#### HTTP Response 

    {   
        "intro": {
            "start": 50.0, "end": 70.0
        }, 
        "type": "introPrediction" (or "introAnnotation")
    }

---

# Resource: Models  

## Rebuild Model

Rebuilds the model with all the current annotated videos. 

#### HTTP Request

    POST: "/videos/rebuild"

#### HTTP Response 

  { "success": True }
