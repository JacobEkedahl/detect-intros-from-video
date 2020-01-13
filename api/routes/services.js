var express = require('express');
var router = express.Router();
const BatchWork = require("../db/models/batchwork")
const constants = require("../db/constants");
const PyWrapper = require("../python/exec_python")
const DbUtils = require("../db/utils")


const PREDICTION_LIMIT = 1;                     // Maximum number of parallell predictions
const HOURS_BETWEEN_PURGES = 1;                 // How often to loop through all entries and purge old ones 
const MINUTES_THAT_WORK_REMAIN_AFTER_END = 10;


var rebuild_semaphore = require('semaphore')(1);
var batchwork_id_semaphore = require('semaphore')(1);
var predict_semaphore = require('semaphore')(PREDICTION_LIMIT);
var rebuild_id; 
var batchworkIndex = 0;
var batchworks = {};
var lastUpdatedTime = (new Date(2020, 0, 1)).getTime(); 

function getId() {
    purgeOldEntries();
    return new Promise(function (resolve, reject) {
        batchwork_id_semaphore.take(function() {
            batchworkIndex = (batchworkIndex + 1) % 10000000;
            if (batchworkIndex == 0) 
                batchworkIndex++;
            batchwork_id_semaphore.leave();
            resolve(batchworkIndex);
        });
    });
}

function purgeOldEntries() {
    var timeNow = (new Date()).getTime();
    var hoursSinceLastPurge = (timeNow- lastUpdatedTime)/(1000*3600);
    if (hoursSinceLastPurge < HOURS_BETWEEN_PURGES)
        return;
    var len = Object.keys(batchworks).length 
    for (var id in batchworks) {
        batchwork = batchworks[id];
        if (batchwork.hasEnded()) {
            if ((timeNow - batchwork.ended.getTime())/(1000) > MINUTES_THAT_WORK_REMAIN_AFTER_END) {
                delete batchworks[id];
            }
        }
    }
    console.log("Purged: " + (len - Object.keys(batchworks).length) + " entities.");
    lastUpdatedTime = (new Date()).getTime();
}

/*
    Clones and removes certain attributes before sending back to the client
*/
function prettifyBatchwork(batchwork) {
    var clone = JSON.parse(JSON.stringify(batchwork));
    delete clone["requested"];
    delete clone["ip"];
    delete clone["ended"];
    return clone
}

function prettifyBatchworks(batchworkList) {
    var resultList = []
    for (var i = 0; i < batchworkList.length; i++) {
        resultList.push(prettifyBatchwork(batchworkList[i]));
    }
    return resultList
}

router.get('/', function(req, res, next) {

    var id = req.query.id;
    if (id !== undefined) {
        if (id in batchworks) {
            var batchwork = batchworks[id];
            batchwork.getExecutionTime();
            batchwork.getStartingDelay();
            sendResponseObject(res, 200, prettifyBatchworks([batchwork]));
        } else {
            sendResponseObject(res, 404, [{}]); 
        }
    } else {
        sendResponseObject(res, 400, "Need to specify query id.");
    }
  });

router.get('/request/predict-intro', function(req, res, next) {

    url = req.query.url 
    if (url == undefined) {
      sendResponseObject(res, 400, "Need to specify video url in post request.");
      return 
    }
    var batchwork = new BatchWork("predict-intro", req.connection.remoteAddress, [url]);
    (async () => {  
        batchwork._id = await getId();
        batchworks[batchwork._id] = batchwork;
        sendResponseObject(res, 200, prettifyBatchwork(batchwork));
    })();
    predict_semaphore.take(function() {
        try {
            (async () => {  
                console.log("started");
                try {
                    batchwork.start();
                    prediction = await PyWrapper.getIntroPredictionByUrl(url);
                    batchwork.finish({ "prediction": prediction });
                } catch(err) {
                    console.log(err);
                    batchwork.result = err;
                    batchwork.halt();
                }
            })();
        } finally {
            predict_semaphore.leave();
        }
    });
});

router.get('/request/rebuild', function(req, res, next) {
    if (rebuild_semaphore.available()) {
        rebuild_semaphore.take(function() {
            (async () => {  
                var batchwork = new BatchWork("rebuild", req.connection.remoteAddress, [""]);
                var id =  await getId();
                batchwork.start();
                batchwork._id = id;
                rebuild_id = id; 
                batchworks[id] = batchwork
                sendResponseObject(res, 200, prettifyBatchwork(batchwork));
                try {
                    await PyWrapper.rebuild();
                    batchwork.finish();
                    batchwork.result = "success";
                } catch (err) {
                    batchwork.halt();
                    batchwork.result = err;
                } finally {
                    rebuild_semaphore.leave();
                }
            })();
        });

    } else {
        var batchwork = batchworks[rebuild_id];
        batchwork.getExecutionTime();
        batchwork.getStartingDelay();
        sendResponseObject(res, 200, prettifyBatchwork(batchwork));
    }
});

router.get('/kill', function(req, res, next) {
    return "Not yet implemented"
});

function sendResponseObject(res, statusCode, object) {
    res.writeHead(statusCode, {'Content-Type': 'application/json'});
    res.end(JSON.stringify(object));
}

module.exports = router;