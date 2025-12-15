"""
Background tasks for admin_panel app using django-q.

These tasks can be queued and executed asynchronously.
"""
from django_q.tasks import async_task, schedule
from django.utils import timezone
from datetime import timedelta
from .models import Campaign, Schedule, RadioStation
from django.contrib import messages
import logging

logger = logging.getLogger()


def process_campaign_statistics(campaign_id):
    """
    Process campaign statistics in the background.
    
    Args:
        campaign_id: The ID of the campaign to process
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        schedules = campaign.schedules.all()
        
        # Calculate statistics
        total_schedules = schedules.count()
        active_schedules = schedules.filter(schedule_status='Submitted').count()
        pending_schedules = schedules.filter(schedule_status='Pending Review (Admin)').count()
        
        logger.info(
            f"Campaign {campaign.name}: "
            f"Total={total_schedules}, Active={active_schedules}, Pending={pending_schedules}"
        )
        
        return {
            'success': True,
            'campaign_id': campaign_id,
            'total_schedules': total_schedules,
            'active_schedules': active_schedules,
            'pending_schedules': pending_schedules,
        }
    except Campaign.DoesNotExist:
        logger.error(f"Campaign with id {campaign_id} does not exist")
        return {'success': False, 'error': 'Campaign not found'}
    except Exception as e:
        logger.error(f"Error processing campaign statistics: {str(e)}")
        return {'success': False, 'error': str(e)}


# tasks.py
import logging
from admin_panel.models import Campaign, Schedule

logger = logging.getLogger(__name__)

def update_schedule_status(campaign_id, new_status='Pending Review (Station Partner)'):
    """
    Update schedule statuses in background using Django-Q2.
    """
    try:
        campaign = Campaign.objects.get(uuid=campaign_id)
        schedules = campaign.schedules.all()

        for schedule in schedules:
            old_status = schedule.schedule_status

            if old_status == 'Pending Review (Admin)':
                schedule.schedule_status = new_status
                schedule.save()

                logger.info(
                    f"Schedule '{schedule.name}': Status updated from '{old_status}' to '{new_status}'"
                )
            else:
                logger.info(
                    f"Schedule '{schedule.name}': Skipped (Current status: {old_status})"
                )

        logger.info(
            f"Campaign '{campaign.name}' status update task finished."
        )

        return {
            'success': True,
            'campaign_id': campaign_id,
            'updated_count': schedules.count()
        }

    except Campaign.DoesNotExist:
        return {'success': False, 'error': f"Campaign {campaign_id} does not exist"}

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {'success': False, 'error': str(e)}

def bulk_update_radio_stations(station_ids, update_data):
    """
    Bulk update radio stations in the background.
    
    Args:
        station_ids: List of station IDs to update
        update_data: Dictionary of fields to update
    """
    try:
        updated_count = 0
        stations = RadioStation.objects.filter(id__in=station_ids)
        
        for station in stations:
            for key, value in update_data.items():
                if hasattr(station, key):
                    setattr(station, key, value)
            station.save()
            updated_count += 1
        
        logger.info(f"Bulk updated {updated_count} radio stations")
        
        return {
            'success': True,
            'updated_count': updated_count,
            'total_requested': len(station_ids),
        }
    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        return {'success': False, 'error': str(e)}


def send_campaign_notification(campaign_id, notification_type='update'):
    """
    Send notification about campaign changes (placeholder for email/notification logic).
    
    Args:
        campaign_id: The ID of the campaign
        notification_type: Type of notification ('update', 'created', 'deleted')
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        
        # Placeholder for actual notification logic
        # In production, you would send emails, push notifications, etc.
        logger.info(
            f"Notification sent for campaign {campaign.name} "
            f"(type: {notification_type})"
        )
        
        return {
            'success': True,
            'campaign_id': campaign_id,
            'notification_type': notification_type,
        }
    except Campaign.DoesNotExist:
        logger.error(f"Campaign with id {campaign_id} does not exist")
        return {'success': False, 'error': 'Campaign not found'}
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return {'success': False, 'error': str(e)}


def cleanup_old_schedules(days_old=30):
    """
    Cleanup old schedules that are expired and completed.
    
    Args:
        days_old: Number of days to look back for cleanup
    """
    try:
        cutoff_date = timezone.now().date() - timedelta(days=days_old)
        
        # Find expired and completed schedules
        old_schedules = Schedule.objects.filter(
            end_date__lt=cutoff_date,
            schedule_status__in=['Completed', 'Expired']
        )
        
        count = old_schedules.count()
        # Uncomment to actually delete:
        # old_schedules.delete()
        
        logger.info(f"Found {count} old schedules for cleanup (older than {days_old} days)")
        
        return {
            'success': True,
            'schedules_found': count,
            'cutoff_date': str(cutoff_date),
        }
    except Exception as e:
        logger.error(f"Error in cleanup: {str(e)}")
        return {'success': False, 'error': str(e)}


# Example of scheduling a recurring task
def schedule_daily_cleanup():
    """
    Schedule a daily cleanup task.
    Call this once to set up the recurring schedule.
    """
    schedule(
        'admin_panel.tasks.cleanup_old_schedules',
        30,  # days_old parameter
        schedule_type='D',  # Daily
        repeats=-1,  # Repeat indefinitely
        next_run=timezone.now() + timedelta(hours=1),
    )

