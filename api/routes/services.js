var express = require('express');
var router = express.Router();
const BatchWorksDao = require("../db/batchworks_dao");
const BatchWork = require("../db/models/batchwork")
const constants = require("../db/constants");
const PyWrapper = require("../python/exec_python")
const DbUtils = require("../db/utils")

const DEFEAULT_LIMIT = 200

/*  
    Timestamp for when the next delete all query will take place
 */
const LAST_REFRESHED = new Date()

function prettifyBatchwork(batchwork) {
    delete batchwork["requested"];
    delete batchwork["ip"];
    delete batchwork["ended"];
    return batchwork
}

function prettifyBatchworks(batchworkList) {
    for (var i = 0; i < batchworkList.length; i++) {
        prettifyBatchwork(batchworkList[i]);
    }
    return batchworkList;
}

/**
 * Queries video repository by query arguments. Pages the query result and limits the fetched result to an amount specified by @DEFAULT_LIMIT 
 */
router.get('/', function(req, res, next) {

    var queries = [];
    if (req.query.id !== undefined) 
        queries.push({[constants.ID]: DbUtils.castToId(req.query.id) });
    
    // Additional Query argumetns could be added here...

    // Page operator    
    var page = 0
    if (req.query.page !== undefined) 
      page = Number(req.query.page) - 1;
      if (page < 0) page = 0;
  
    // Limit operator 
    var limit = DEFEAULT_LIMIT;
    if (req.query.limit !== undefined) 
      limit = Number(req.query.limit)
      if (limit > DEFEAULT_LIMIT)
        limit = DEFEAULT_LIMIT;
  
    if (queries.length == 0) {
        sendResponseObject(res, 400, "No valid query arguments found.");
        return 
    }
    
    (async () => {  
      var batchworks = await BatchWorksDao.findByMultipleQueries(queries, page, limit);
      sendResponseObject(res, 200, prettifyBatchworks(batchworks));
    })();
  });

router.get('/request/predict-intro', function(req, res, next) {

    url = req.query.url 
    if (url == undefined) {
      sendResponseObject(res, 400, "Need to specify video url in post request.");
      return 
    }
    (async () => {  
        var batchwork = new BatchWork("predict-intro", req.connection.remoteAddress, [url]);
        try {
            result = await BatchWorksDao.insert(batchwork);
            batchwork._id = result.insertedId 
            var clone = JSON.parse(JSON.stringify(batchwork));
            sendResponseObject(res, 200, prettifyBatchwork(clone));
            batchwork.start()
        } catch(err) {
            console.log(err)
            sendResponseObject(res, 500, err);
            return;
        }
        try {
            prediction = await PyWrapper.getIntroPredictionByUrl(url);
            batchwork.finish({ "prediction": prediction });
            BatchWorksDao.replace(batchwork);
        } catch(err) {
            console.log(err);
            batchwork.halt();
            BatchWorksDao.replace(batchwork);
        }
    })();
});
  
router.get('/kill', function(req, res, next) {
    // Only capable of killing processes which has not yet started...
    return "Not yet implemented"
});

function sendResponseObject(res, statusCode, object) {
    res.writeHead(statusCode, {'Content-Type': 'application/json'});
    res.end(JSON.stringify(object));
}

module.exports = router;