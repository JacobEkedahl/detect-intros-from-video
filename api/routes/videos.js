var express = require('express');
var router = express.Router();
const VideosDao = require("../db/video_dao");
const constants = require("../db/constants");
const PyWrapper = require("../python/exec_python")

const DEFEAULT_LIMIT = 200

//const mutex = new Mutex();
//var id = 0


class  LongJob {
  constructor(id) {
    this.id = id, 

    this.result = null
    this.started = new Date();
    this.ended = null 

  }
}

/**
 * Queries video repository by query arguments. Pages the query result and limits the fetched result to an amount specified by @DEFAULT_LIMIT 
 */
router.get('/', function(req, res, next) {

  var queries = [];
  if (req.query.url !== undefined)
    queries.push({[constants.URL]: req.query.url});

  if (req.query.show !== undefined) 
    queries.push({[constants.SHOW]: req.query.show});

  if (req.query.show_id !== undefined) 
    queries.push({[constants.SHOW_ID]: req.query.show_id});

  if (req.query.season !== undefined) 
    queries.push({[constants.SEASON]: Number(req.query.season)});
  
  if (req.query.episode !== undefined) 
    queries.push({[constants.EPISODE]: Number(req.query.episode)});
  
  if (req.query.title !== undefined) 
    queries.push({[constants.TITLE]: req.query.title });

  if (req.query.prediction !== undefined) 
    queries.push({[constants.INTRO_PREDICTION]: { 
      $exists:  req.query.prediction.toLowerCase() === 'true', $ne: null } 
    }); // intro prediction exists 

  if (req.query.annotation !== undefined) 
    queries.push({[constants.INTRO_ANNOTATION]: {
      $exists:  req.query.annotation.toLowerCase() === 'true', $ne: null } 
    }); // intro annotation exists 

  // Page operator    
  var page = 0
  if (req.query.page !== undefined) 
    page = Number(req.query.page) - 1 
    if (page < 0) page = 0 

  // Limit operator 
  var limit = DEFEAULT_LIMIT
  if (req.query.limit !== undefined) 
    limit = Number(req.query.limit)
    if (limit > DEFEAULT_LIMIT)
      limit = DEFEAULT_LIMIT

  if (queries.length == 0) 
    queries.push({}); // query all 
  
  (async () => {  
    var videos = await VideosDao.findByMultipleQueries(queries, page, limit);
    sendResponseObject(res, 200, videos);
  })();
});


/**
 * Annotates a intro sequence for a video by url
 */
router.post('/set/intro', function(req, res, next) {
  url = req.query.url 
  if (url == undefined) {
    sendResponseObject(res, 400, "Need to specify video url in post request.");
    return 
  }
  if ((req.body.start == undefined) || (req.body.end == undefined)) {
    sendResponseObject(res, 400, "Request body must contain start and end time denoted in seconds.");
    return 
  }
  start = req.body.start 
  end = req.body.end 
  if (isNaN(start) || isNaN(end)) {
    sendResponseObject(res, 400, "Request body must contain start and end time denoted in seconds.");
    return 
  }
  if (start > end) {
    sendResponseObject(res, 400, "Start may not exceed end.");
    return 
  }
  (async () => {  
    var response = await VideosDao.setIntro(url, start, end);
    if (response.result.n > 0)
      sendResponseObject(res, 200, "success");
    else 
      sendResponseObject(res, 404, "Failed to update");
  })();
});

function sendResponseObject(res, statusCode, object) {
  res.writeHead(statusCode, {'Content-Type': 'application/json'});
  res.end(JSON.stringify(object));
}

module.exports = router; 
