const ObjectId = require('mongodb').ObjectID

module.exports = class DbUtils {

    static castToId(id) {
        return new ObjectId(id);
    }

}