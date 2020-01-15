var express = require('express');
var router = express.Router();
const VideosDao = require("../db/videos_dao");
const constants = require("../db/constants");


const DEFEAULT_LIMIT = 100

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
    if (req.query.prediction.toLowerCase() == "true")  {
      queries.push({[constants.INTRO_PREDICTION]: { $ne: null } });
    } else {
      queries.push({[constants.INTRO_PREDICTION]: null }); 
    }

  if (req.query.annotation !== undefined) 
    if (req.query.annotation.toLowerCase() == "true")  {
      queries.push({[constants.INTRO_ANNOTATION]: { $ne: null } });
    } else {
      queries.push({[constants.INTRO_ANNOTATION]: null }); 
    }
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
 * Annotates intro sequences of videos. Taking either a url or a show/show_id as primary query arguments.
 * Body: {
 *  "start": <float>,
 *  "end": <float
 * }
 */
router.post('/set/intro', function(req, res, next) {
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
  
  var queries = [];
  if (req.query.url !== undefined) {
    queries.push({[constants.URL]: req.query.url});    
  }
  else if (req.query.show !== undefined) {
    queries.push({[constants.SHOW]: req.query.show});   
  }
  else if (req.query.show_id !== undefined) {
    queries.push({[constants.SHOW_ID]: req.query.show_id});    
  }
  else {
    sendResponseObject(res, 400, "Update queries must contain one of the following arguments: url=, show= or show_id=. ");
    return;
  }
  // Extra arguments 
  if (req.query.season !== undefined) 
    queries.push({[constants.SEASON]: Number(req.query.season)});

  if (req.query.episode !== undefined) 
    queries.push({[constants.EPISODE]: Number(req.query.episode)});

  if (req.query.title !== undefined) 
    queries.push({[constants.TITLE]: req.query.title });

  (async () => {  
    var response = await VideosDao.setIntros(queries, start, end);
    if (response.result.n > 0)
      sendResponseObject(res, 200, { "success": response.result });
    else 
      sendResponseObject(res, 404, { "failure": null });
  })();
});

function sendResponseObject(res, statusCode, object) {
  res.writeHead(statusCode, {'Content-Type': 'application/json'});
  res.end(JSON.stringify(object));
}

module.exports = router; 
