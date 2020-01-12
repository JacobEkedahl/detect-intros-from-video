const {PythonShell} = require('python-shell')

module.exports = class PyWrapper {

    /**
     * Performs an intro prediction on the specified url 
     * @param {*} url 
     */
    static getIntroPredictionByUrl(url) {
        let options = {
            mode: 'text',
            encoding: 'utf8',
//          pythonPath: 'path/to/python',
            pythonOptions: ['-u'],  // get print results in real-time
            scriptPath: './src/', 
            args: ["--predict", url] 
        };
        return new Promise(function (resolve, reject) {
/*
            Returns the stdout from running main.py and loops through the results to find if any predictions were made
*/
            PythonShell.run('main.py', options, function (err, results) {
                if (err) {
                    reject(err);
                } 
                if (results) {
                    console.log(results)
                    for (var i = 0; i < results.length; i++) {
                        if (results[i] == "_PREDICTION_") {
                            var result = results[i + 1];
                            console.log(result)
                            result = result.replace(/\'/g, "\"");
                            resolve(JSON.parse(result))
                            return;
                        }
                    }
                    resolve(null)
                }
            });
        });
    }

    static rebuild() {
        let options = {
            mode: 'text',
            encoding: 'utf8',
//          pythonPath: 'path/to/python',
            pythonOptions: ['-u'],  // get print results in real-time
            scriptPath: './src/', 
            args: ["--rebuild"] 
        };
        return new Promise(function (resolve, reject) {
/*
            Returns the stdout from running main.py and loops through the results to find if any predictions were made
*/
            PythonShell.run('main.py', options, function (err, results) {
                if (err) {
                    reject(err);
                } 
                if (results) {
                    console.log(results)
                    resolve()
                }
            });
        });
    }

}
   