
module.exports = class BatchWork {

    constructor(processName, userIp, args) {
        this._id = null;
        this.process = processName;
        this.args = args
        this.ip = userIp;   
        this.requested = new Date()
        this.started = null 
        this.ended = null
        this.result = null;
        this.status = "pending"
    }

    halt() {
        this.status = "halted"
        this.ended = new Date()
        this.executionTime = this.getExecutionTime()
    }

    start() {
        this.status = "working"
        this.started = new Date()
        var started = this.started
        if (started == null) started = new Date()
        this.startDelay = this.getStartingDelay()
    }

    finish(result) {
        this.result = result
        this.status = "finished"
        this.ended = new Date()
        this.executionTime = this.getExecutionTime()
    }

    getStartingDelay() {
        var started = this.started
        if (started == null) 
            started = new Date()
        this.startDelay = (started.getTime() - this.requested.getTime())/1000
        return this.startDelay
    }

    getExecutionTime() {
        var ended = this.ended
        if (ended == null) 
            ended = new Date()
        var started = this.started
        if (started == null) 
            started = new Date()
        this.executionTime = (ended.getTime() - started.getTime())/1000
        return this.executionTime 
    }

    hasEnded() {
        return this.ended != null;
    }

    isPending() {
        return this.status == "pending";
    }
    

}