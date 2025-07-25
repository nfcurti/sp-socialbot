const cron = require('node-cron');
const actions = require('./actions');

let schedulerJob = null;

function getRandomInterval() {
    // Random interval between 5-15 minutes
    const minutes = Math.floor(Math.random() * 11) + 5;
    console.log(`⏰ Next execution scheduled in ${minutes} minutes`);
    return minutes;
}

function scheduleNext() {
    if (!schedulerJob) return; // Scheduler was stopped
    
    const minutes = getRandomInterval();
    
    setTimeout(() => {
        if (!schedulerJob) return; // Scheduler was stopped during timeout
        
        console.log('🤖 Scheduled execution triggered');
        actions.executeRandomScript();
        
        // Schedule the next execution recursively
        scheduleNext();
    }, minutes * 60 * 1000); // Convert minutes to milliseconds
}

function startScheduler() {
    if (schedulerJob !== null) {
        console.log('⚠️  Scheduler is already running');
        return false;
    }

    console.log('⏰ Starting scheduler with random intervals (5-15 minutes)');
    
    // Use a simple flag to track if scheduler is running
    schedulerJob = true;
    
    // Execute immediately on start
    console.log('🤖 Initial execution triggered');
    actions.executeRandomScript();
    
    // Schedule the next execution
    scheduleNext();
    
    actions.setSchedulerStatus(true);
    console.log('✅ Scheduler started successfully');
    return true;
}

function stopScheduler() {
    if (schedulerJob === null) {
        console.log('⚠️  Scheduler is not running');
        return false;
    }

    schedulerJob = null; // This will stop the recursive scheduling
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