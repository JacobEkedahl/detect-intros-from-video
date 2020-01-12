var express = require('express');
var router = express.Router();
const BatchWorksDao = require("../db/batchworks_dao");
const BatchWork = require("../db/models/batchwork")
const constants = require("../db/constants");
const PyWrapper = require("../python/exec_python")
const DbUtils = require("../db/utils")


const PREDICTION_LIMIT = 1;

var rebuild_semaphore = require('semaphore')(1);
var batchwork_id_semaphore = require('semaphore')(1);
var predict_semaphore = require('semaphore')(PREDICTION_LIMIT);
var rebuild_id; 
var batchworkIndex = 0;
var batchworks = {};

function getId() {
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

/*
    Removes certain elements from the batchwork entity.
*/
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

router.get('/', function(req, res, next) {

    var id = req.query.id;
    if (id !== undefined) {
        if (id in batchworks) {
            var batchwork = batchworks[id];
            batchwork.getExecutionTime();
            var clone = JSON.parse(JSON.stringify(batchwork));
            sendResponseObject(res, 200, prettifyBatchworks([clone]));
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
    predict_semaphore.take(function() {
        try {
            (async () => {  
            var batchwork = new BatchWork("predict-intro", req.connection.remoteAddress, [url]);
                batchwork._id = await getId();
                batchwork.start();
                batchworks[batchwork._id] = batchwork;
                var clone = JSON.parse(JSON.stringify(batchwork));
                sendResponseObject(res, 200, prettifyBatchwork(clone));

                try {
                    prediction = await PyWrapper.getIntroPredictionByUrl(url);
                    batchwork.finish({ "prediction": prediction });
                } catch(err) {
                    console.log(err);
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
                sendResponseObject(res, 200, prettifyBatchwork(JSON.parse(JSON.stringify(batchwork))));

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
        sendResponseObject(res, 200, prettifyBatchwork(JSON.parse(JSON.stringify(batchwork))));
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