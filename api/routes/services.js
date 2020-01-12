var express = require('express');
var router = express.Router();
const BatchWorksDao = require("../db/batchworks_dao");
const BatchWork = require("../db/models/batchwork")
const constants = require("../db/constants");
const PyWrapper = require("../python/exec_python")
const DbUtils = require("../db/utils")

var rebuild_semaphore = require('semaphore')(1);
var rebuild_process = {} 
var REBUILD_PID = "rebuild"


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
 * Queries service process repository by query arguments. Pages the query result and limits the fetched result to an amount specified by @DEFAULT_LIMIT 
 */
router.get('/', function(req, res, next) {

    var queries = [];
    if (req.query.id !== undefined) 

        /*
        * Handle rebuild process queries
        */
        if (req.query.id == REBUILD_PID) {
            if (rebuild_process == null) {
                sendResponseObject(res, 404, [{}]); 
            } else {
                rebuild_process.getExecutionTime();
                sendResponseObject(res, 200, prettifyBatchworks([rebuild_process])); 
            }
            return 
        }
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

router.get('/request/rebuild', function(req, res, next) {
    if (rebuild_semaphore.available()) {
        rebuild_semaphore.take(function() {
            (async () => {  
                try {
                    rebuild_process = new BatchWork("rebuild", req.connection.remoteAddress, [""]);
                    rebuild_process.start();
                    rebuild_process._id = REBUILD_PID;
                    sendResponseObject(res, 200, rebuild_process);
                    await PyWrapper.rebuild();
                    rebuild_process.finish();
                    rebuild_process.result = "success";
                } catch (err) {
                    rebuild_process.halt();
                    rebuild_process.result = err;
                } finally {
                    rebuild_semaphore.leave();
                }
            })();
        });
    } else {
        console.log("already rebuilding: sent old request");
        rebuild_process.getExecutionTime();
        sendResponseObject(res, 200, rebuild_process);
    }
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