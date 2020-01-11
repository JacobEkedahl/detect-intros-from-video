const MongoClient = require('mongodb').MongoClient;

dbname = process.env.db_name
URL = process.env.db_url
const collectionKey = 'videos';
const constants = require("./constants");


module.exports = class VideosDao {

     /**
     * Combines multiple queries and puts a pagination filter on top of it to reduce traffic  
      * @param {*} queryArray 
      * @param {*} page 
      * @param {*} limit 
      */
    static findByMultipleQueries(queryArray, page, limit) {
        return new Promise(function (resolve, reject) {
            MongoClient.connect(URL, function(err, db) {
                if (err) 
                    reject(err);
                else {
                    db.db(dbname).collection(collectionKey).find({
                        "$and": queryArray 
                    }).skip(page*limit).limit(limit).toArray(function (err, res) {
                        if (err) {
                            console.log(err);
                            resolve([]);
                        }                       
                        resolve(res);
                    });
                }
            });
        });
    }

    /**
     * Updates the annotaed intro of a video by querying for the video download url 
     * @param {*} url 
     * @param {*} start 
     * @param {*} end 
     */
    static setIntro(query_url, start, end) {
        return new Promise(function (resolve, reject) {
            MongoClient.connect(URL, function(err, db) {
                if (err) 
                    reject(err);
                else {
                    db.db(dbname).collection(collectionKey).updateOne(
                        {[constants.URL]: query_url},
                        { "$set": { [constants.INTRO_ANNOTATION]: { "start": start, "end": end } } }, 
                        function(err, res) {
                            if (err) 
                                reject(err)
                            resolve(res)
                            db.close();
                        }
                    );
                }
            });
        });
    }


}
    
