const MongoClient = require('mongodb').MongoClient;
const collectionKey = 'batchworks';

DBNAME = process.env.db_name
URL = process.env.db_url

module.exports = class BatchWorksDao {

    /**
     * Inserts a server batch process into the database 
     * @param {*} batchwork 
     */
    static insert(batchwork) {
        return new Promise(function (resolve, reject) {
            MongoClient.connect(URL, function(err, db) {
                if (err) 
                    reject(err);
                else {
                    db.db(DBNAME).collection(collectionKey).insertOne(batchwork, function(err, res) {
                        if (err)
                            reject(err);
                        else  
                            resolve(res);
                    });
                }
                if (db !== null) db.close();
            });
        });
    }

    static replace(batchwork) {
        return new Promise(function (resolve, reject) {
            MongoClient.connect(URL, function(err, db) {
                if (err) 
                    reject(err);
                else {
                    db.db(DBNAME).collection(collectionKey).replaceOne( { "_id": batchwork._id }, batchwork, function(err, res) {
                        if (err)
                            reject(err);
                        else  
                            resolve(res);
                    });
                }
                if (db !== null) db.close();
            });
        });
    }

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
}