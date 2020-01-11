var express = require('express');
var router = express.Router();
const VideosDao = require("../db/video_dao");
const constants = require("../db/constants");
const PyWrapper = require("../python/exec_python")

router.get('/', function(req, res, next) {
    res.send('services');
});

router.get('/request/intro', function(req, res, next) {

    url = req.query.url 
    if (url == undefined) {
      sendResponseObject(res, 400, "Need to specify video url in post request.");
      return 
    }
    (async () => {  
        try {
            prediction = await PyWrapper.getIntroPredictionByUrl(url);
            sendResponseObject(res, 200, prediction);
        } catch(err) {
            console.log(err)
            sendResponseObject(res, 500, err);
        }
    })();
});
  
router.get('/request/rebuild', function(req, res, next) {
    (async () => {  
        try {
            PyWrapper.rebuild()
            sendResponseObject(res, 200, "Dataset rebuild started...");
        } catch(err) {
            console.log(err)
            sendResponseObject(res, 500, err);
        }
    })();
});
  
function sendResponseObject(res, statusCode, object) {
    res.writeHead(statusCode, {'Content-Type': 'application/json'});
    res.end(JSON.stringify(object));
}module.exports = router;