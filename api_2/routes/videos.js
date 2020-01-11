var express = require('express');
var router = express.Router();
const VideosDao = require("../db/video_dao");
const constants = require("../db/constants");


const DEFAULT_PAGE = 0
const DEFEAULT_LIMIT = 200

/**
 * Queries video repository by arguments. Maximum number of entities fetched is 200 per page.
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

  
  var page = DEFAULT_PAGE
  if (req.query.page !== undefined) 
    page = Number(req.query.page) - 1 
    if (page < 0) page = 0 

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
  
  if (req.query.url == undefined) {
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
    var response = await VideosDao.setIntro(req.query.url, start, end);
    if (response.result.n > 0)
      sendResponseObject(res, 200, "success");
    else 
      sendResponseObject(res, 404, "Failed to update");
  })();
});


const {PythonShell} = require('python-shell')

let options = {
  mode: 'text',
  encoding: 'utf8',
//  pythonPath: 'path/to/python',
  pythonOptions: ['-u'], // get print results in real-time
  scriptPath: './routes/',
  args: ['Hello World!']
};

var shell = new PythonShell('my_script.py', options);

shell.on('message', function (message) {
  console.log("message ", message)
});




/*
PythonShell.run('my_script.py', options, function (err, results) {
  if (err) {
    console.log(err)
    throw err;
  } 
  if (results) {
    console.log(results)
  }
  console.log('finished');
});
*/

router.post('/get/intro', function(req, res, next) {
  
  sendResponseObject(res, 200, req.query.id);
 
});


function sendResponseObject(res, statusCode, object) {
  res.writeHead(statusCode, {'Content-Type': 'application/json'});
  res.end(JSON.stringify(object));
}

module.exports = router; 
