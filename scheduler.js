const cron = require('node-cron');
const actions = require('./actions');

let schedulerJob = null;

function getRandomInterval() {
    const minutes = Math.floor(Math.random() * 11) + 5;
    return `*/${minutes} * * * *`;
}

function startScheduler() {
    if (schedulerJob) {
        console.log('⚠️  Scheduler is already running');
        return false;
    }

    const interval = getRandomInterval();
    console.log(`⏰ Starting scheduler with interval: ${interval}`);
    
    schedulerJob = cron.schedule(interval, () => {
        console.log('🤖 Scheduled execution triggered');
        actions.executeRandomScript();
        
        const newInterval = getRandomInterval();
        console.log(`⏰ Next execution in: ${newInterval}`);
        
        schedulerJob.stop();
        schedulerJob = cron.schedule(newInterval, () => {
            console.log('🤖 Scheduled execution triggered');
            actions.executeRandomScript();
        });
    }, {
        scheduled: false
    });

    schedulerJob.start();
    actions.setSchedulerStatus(true);
    console.log('✅ Scheduler started successfully');
    return true;
}

function stopScheduler() {
    if (!schedulerJob) {
        console.log('⚠️  Scheduler is not running');
        return false;
    }

    schedulerJob.stop();
    schedulerJob = null;
    actions.setSchedulerStatus(false);
    console.log('🛑 Scheduler stopped successfully');
    return true;
}

function isRunning() {
    return schedulerJob !== null;
}

module.exports = {
    startScheduler,
    stopScheduler,
    isRunning
}; 