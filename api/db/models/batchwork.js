
module.exports = class BatchWork {

    constructor(processName, userIp, args) {
        this._id = null;
        this.process = processName;
        this.args = args
        this.ip = userIp;   
        this.requested = new Date();
        this.started = null 
        this.ended = null
        this.result = null;
        this.status = "pending"; 
    }

    halt() {
        this.status = "halted"
    }

    start() {
        this.status = "working"
        this.started = new Date();
        this.startDelay = (this.started.getTime() - this.requested.getTime())/1000
    }

    finish(result) {
        this.result = result
        this.status = "finished"
        this.ended = new Date();
        this.executionTime = this.getExecutionTime()
    }

    getExecutionTime() {
        var ended = this.ended;
        if (ended == null) 
            ended = new Date();
        this.executionTime = (ended.getTime() - this.started.getTime())/1000
        return this.executionTime 
    }

}