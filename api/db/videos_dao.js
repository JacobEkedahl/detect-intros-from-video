const MongoClient = require('mongodb').MongoClient;

DBNAME = process.env.db_name
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
                    db.db(DBNAME).collection(collectionKey).find({
                        "$and": queryArray 
                    }).skip(page*limit).limit(limit).toArray(function (err, res) {
                        if (err) {
                            console.log(err);
                            resolve([]);
                        }                       
                        resolve(res);
                    });
                }
                if (db !== null) db.close();
            });
        });
    }

    /**
     * Updates the annotaed intro of a video by querying for the video download url 
     * @param {*} url 
     * @param {*} start 
     * @param {*} end 
     */
    static setIntros(queryArray, start, end) {
        return new Promise(function (resolve, reject) {
            MongoClient.connect(URL, function(err, db) {
                if (err) 
                    reject(err);
                else {
                    db.db(DBNAME).collection(collectionKey).updateMany(
                        { "$and": queryArray },
                        { "$set": { [constants.INTRO_ANNOTATION]: { "start": start, "end": end } } }, 
                        function(err, res) {
                            if (err) 
                                reject(err)
                            resolve(res)
                            db.close();
                        }
                    );
                }
                if (db !== null) db.close();
            });
        });
    }

}
    
