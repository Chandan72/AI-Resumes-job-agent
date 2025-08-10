import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
from typing import Callable, Optional
import os

logger = logging.getLogger(__name__)

class NewsCurationScheduler:
    def __init__(self, curation_function: Callable, timezone: str = "Asia/Kolkata"):
        """
        Initialize the scheduler for news curation
        
        Args:
            curation_function: Function to execute for news curation
            timezone: Timezone for scheduling (default: Asia/Kolkata for IST)
        """
        self.curation_function = curation_function
        self.timezone = pytz.timezone(timezone)
        self.scheduler = BackgroundScheduler(timezone=self.timezone)
        self.is_running = False
        
        # Get scheduling time from environment or use defaults
        self.schedule_hour = int(os.getenv('SCHEDULER_HOUR', 10))
        self.schedule_minute = int(os.getenv('SCHEDULER_MINUTE', 0))
        
        logger.info(f"Initialized scheduler for {timezone} timezone")
        logger.info(f"Daily execution scheduled for {self.schedule_hour:02d}:{self.schedule_minute:02d}")
    
    def start(self):
        """Start the scheduler"""
        try:
            if not self.is_running:
                # Add the daily job
                self.scheduler.add_job(
                    func=self._execute_curation,
                    trigger=CronTrigger(
                        hour=self.schedule_hour,
                        minute=self.schedule_minute,
                        timezone=self.timezone
                    ),
                    id='daily_news_curation',
                    name='Daily News Curation at 10 AM IST',
                    replace_existing=True
                )
                
                # Start the scheduler
                self.scheduler.start()
                self.is_running = True
                
                logger.info("News curation scheduler started successfully")
                logger.info(f"Next execution scheduled for {self.scheduler.get_job('daily_news_curation').next_run_time}")
                
            else:
                logger.warning("Scheduler is already running")
                
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the scheduler"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("News curation scheduler stopped")
            else:
                logger.warning("Scheduler is not running")
                
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    def _execute_curation(self):
        """Execute the news curation function"""
        try:
            logger.info("Executing scheduled news curation...")
            start_time = datetime.now()
            
            # Execute the curation function
            result = self.curation_function()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"News curation completed successfully in {execution_time:.2f} seconds")
            logger.info(f"Result: {result}")
            
        except Exception as e:
            logger.error(f"Error during scheduled news curation: {e}")
            # You might want to send notifications here for failed executions
    
    def trigger_manual_execution(self) -> bool:
        """
        Manually trigger news curation
        
        Returns:
            bool: True if execution was successful, False otherwise
        """
        try:
            logger.info("Manual news curation triggered")
            start_time = datetime.now()
            
            # Execute the curation function
            result = self.curation_function()
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            logger.info(f"Manual news curation completed successfully in {execution_time:.2f} seconds")
            logger.info(f"Result: {result}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error during manual news curation: {e}")
            return False
    
    def get_next_execution_time(self) -> Optional[datetime]:
        """Get the next scheduled execution time"""
        try:
            job = self.scheduler.get_job('daily_news_curation')
            if job and job.next_run_time:
                return job.next_run_time
            return None
        except Exception as e:
            logger.error(f"Error getting next execution time: {e}")
            return None
    
    def get_scheduler_status(self) -> dict:
        """Get current scheduler status"""
        try:
            job = self.scheduler.get_job('daily_news_curation')
            next_run = job.next_run_time if job else None
            
            return {
                'is_running': self.is_running,
                'next_execution': next_run.isoformat() if next_run else None,
                'timezone': str(self.timezone),
                'schedule_time': f"{self.schedule_hour:02d}:{self.schedule_minute:02d}",
                'total_jobs': len(self.scheduler.get_jobs())
            }
        except Exception as e:
            logger.error(f"Error getting scheduler status: {e}")
            return {
                'is_running': False,
                'error': str(e)
            }
    
    def modify_schedule(self, hour: int, minute: int):
        """
        Modify the daily schedule
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
        """
        try:
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time values")
            
            # Remove existing job
            if self.scheduler.get_job('daily_news_curation'):
                self.scheduler.remove_job('daily_news_curation')
            
            # Add new job with updated schedule
            self.scheduler.add_job(
                func=self._execute_curation,
                trigger=CronTrigger(
                    hour=hour,
                    minute=minute,
                    timezone=self.timezone
                ),
                id='daily_news_curation',
                name=f'Daily News Curation at {hour:02d}:{minute:02d}',
                replace_existing=True
            )
            
            self.schedule_hour = hour
            self.schedule_minute = minute
            
            logger.info(f"Schedule updated to {hour:02d}:{minute:02d}")
            
        except Exception as e:
            logger.error(f"Error modifying schedule: {e}")
            raise
    
    def pause_job(self):
        """Pause the daily news curation job"""
        try:
            job = self.scheduler.get_job('daily_news_curation')
            if job:
                job.pause()
                logger.info("Daily news curation job paused")
            else:
                logger.warning("No daily news curation job found to pause")
        except Exception as e:
            logger.error(f"Error pausing job: {e}")
    
    def resume_job(self):
        """Resume the daily news curation job"""
        try:
            job = self.scheduler.get_job('daily_news_curation')
            if job:
                job.resume()
                logger.info("Daily news curation job resumed")
            else:
                logger.warning("No daily news curation job found to resume")
        except Exception as e:
            logger.error(f"Error resuming job: {e}")