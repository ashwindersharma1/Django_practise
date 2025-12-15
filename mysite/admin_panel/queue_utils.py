"""
Utility functions for working with django-q queues.
"""
from django_q.models import OrmQ
from django.utils import timezone
from datetime import timedelta


def get_queue_stats():
    """
    Get statistics about the queue.
    
    Returns:
        dict: Queue statistics including pending, successful, failed counts
    """
    stats = {
        'pending': OrmQ.objects.filter(lock__isnull=True).count(),
        'processing': OrmQ.objects.exclude(lock__isnull=True).count(),
        'successful': OrmQ.objects.filter(success=True).count(),
        'failed': OrmQ.objects.filter(success=False).count(),
        'total': OrmQ.objects.count(),
    }
    
    # Get recent tasks (last 24 hours)
    recent_cutoff = timezone.now() - timedelta(hours=24)
    stats['recent_total'] = OrmQ.objects.filter(
        started__gte=recent_cutoff
    ).count()
    
    return stats


def get_recent_tasks(limit=10):
    """
    Get recent tasks from the queue.
    
    Args:
        limit: Number of tasks to return
        
    Returns:
        QuerySet: Recent tasks ordered by started time
    """
    return OrmQ.objects.all().order_by('-started')[:limit]


def get_failed_tasks(limit=10):
    """
    Get recent failed tasks.
    
    Args:
        limit: Number of tasks to return
        
    Returns:
        QuerySet: Failed tasks ordered by started time
    """
    return OrmQ.objects.filter(success=False).order_by('-started')[:limit]


def clear_old_tasks(days=7):
    """
    Clear old completed tasks from the queue.
    
    Args:
        days: Number of days to keep tasks
        
    Returns:
        int: Number of tasks deleted
    """
    cutoff = timezone.now() - timedelta(days=days)
    deleted_count, _ = OrmQ.objects.filter(
        started__lt=cutoff,
        success__isnull=False,  # Only delete completed tasks
    ).delete()
    
    return deleted_count

