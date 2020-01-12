
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
        this.executionTime = 0 
        this.startDelay = 0
    }

    halt() {
        this.status = "halted"
        this.duration = (this.ended.getTime() - this.started.getTime())/1000
    }

    start() {
        this.status = "working"
        this.started = new Date();
        this.duration = 0;
        this.startDelay = (this.started.getTime() - this.requested.getTime())/1000
    }

    finish(result) {
        this.result = result
        this.status = "finished"
        this.ended = new Date();
        this.duration = (this.ended.getTime() - this.started.getTime())/1000
    }

}