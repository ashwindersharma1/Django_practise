# Django-Q2 Setup and Usage Guide

This project uses `django-q2` for asynchronous task processing with a database backend. Django-Q2 is a maintained fork of django-q that supports Django 5.x.

**Important Note:** The package is installed as `django-q2`, but it uses `django_q` (not `django_q2`) as the import name in your code. This is why you'll see `from django_q import ...` in the code examples.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Start the queue cluster** (in a separate terminal):
   ```bash
   python manage.py qcluster
   ```
   
   **Important:** Keep this running! Tasks won't execute without it.

4. **Your Django app is ready!** Tasks will be automatically queued and processed.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

This will install `django-q2` which is compatible with Django 5.x.

2. Run migrations to create django-q2 tables:
```bash
python manage.py migrate
```

This creates the necessary database tables for the queue system.

## Running the Queue Cluster

The queue cluster processes background tasks. You **MUST** run it in a separate terminal/process for tasks to be processed:

### Windows (PowerShell or Command Prompt):
```bash
python manage.py qcluster
```

Or use the provided batch file:
```bash
.\run_qcluster.bat
```

### Linux/Mac:
```bash
python manage.py qcluster
```

Or use the provided shell script:
```bash
chmod +x run_qcluster.sh
./run_qcluster.sh
```

**Important:** 
- Keep this process running while your Django application is running
- The qcluster processes tasks from the database queue
- If qcluster is not running, tasks will be queued but not executed
- You can run multiple qcluster instances for load balancing

### Running in Production

For production, use a process manager like `supervisor`, `systemd`, or `pm2`:

#### Example Supervisor Configuration (`/etc/supervisor/conf.d/django-q2.conf`):
```ini
[program:django-q2]
command=/path/to/venv/bin/python /path/to/manage.py qcluster
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/django-q2.log
```

#### Example systemd Service (`/etc/systemd/system/django-q2.service`):
```ini
[Unit]
Description=Django-Q2 Queue Cluster
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python /path/to/manage.py qcluster
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable django-q2.service
sudo systemctl start django-q2.service
```

## Configuration

The django-q2 configuration is in `mysite/settings.py`. The app is already added to `INSTALLED_APPS` as `'django_q'` (the package name is `django-q2` but the import name is `django_q`):

```python
Q_CLUSTER = {
    'name': 'mysite_queue',
    'workers': 4,              # Number of worker processes
    'recycle': 500,            # Restart workers after N tasks
    'timeout': 60,             # Task timeout in seconds
    'retry': 120,              # Retry failed tasks after N seconds
    'queue_limit': 50,         # Max tasks in queue
    'bulk': 10,                # Process N tasks at once
    'orm': 'default',          # Use Django ORM (database backend)
    'sync': False,             # Set True for synchronous execution (testing)
    'max_attempts': 3,         # Maximum retry attempts
}
```

## Using Queues in Your Code

### Basic Usage

Import and use `async_task` to queue tasks:

```python
# Note: django-q2 package uses 'django_q' as the import name
from django_q.tasks import async_task
from admin_panel.tasks import process_campaign_statistics

# Queue a task
task_id = async_task(
    process_campaign_statistics,
    campaign_id=123,
    task_name='process_campaign_123',
)
```

### Available Tasks

All background tasks are defined in `admin_panel/tasks.py`:

- `process_campaign_statistics(campaign_id)` - Process campaign statistics
- `update_schedule_status(schedule_id, new_status)` - Update schedule status
- `bulk_update_radio_stations(station_ids, update_data)` - Bulk update stations
- `send_campaign_notification(campaign_id, notification_type)` - Send notifications
- `cleanup_old_schedules(days_old=30)` - Cleanup old schedules

### Checking Task Status

```python
# Note: django-q2 package uses 'django_q' as the import name
from django_q.models import OrmQ

# Get task by ID
task = OrmQ.objects.get(id=task_id)

# Check if task is complete
if task.success:
    result = task.result
    print(f"Task succeeded: {result}")
else:
    print(f"Task failed: {task.result}")
```

### Viewing Tasks in Admin

Django-Q provides an admin interface. Add to your admin:

```python
# In admin.py
# Note: django-q2 package uses 'django_q' as the import name
from django_q.admin import TaskAdmin
from django_q.models import OrmQ

admin.site.register(OrmQ, TaskAdmin)
```

## Scheduled Tasks

To schedule recurring tasks:

```python
# Note: django-q2 package uses 'django_q' as the import name
from django_q.tasks import schedule
from admin_panel.tasks import cleanup_old_schedules

schedule(
    'admin_panel.tasks.cleanup_old_schedules',
    30,  # days_old parameter
    schedule_type='D',  # Daily
    repeats=-1,  # Repeat indefinitely
)
```

Schedule types:
- `'I'` - Minutes
- `'H'` - Hours
- `'D'` - Days
- `'W'` - Weeks
- `'M'` - Months

## Monitoring

### View Queue Status

```python
# Note: django-q2 package uses 'django_q' as the import name
from django_q.models import OrmQ

# Count pending tasks
pending = OrmQ.objects.filter(lock__isnull=True).count()

# Count failed tasks
failed = OrmQ.objects.filter(success=False).count()

# Count successful tasks
successful = OrmQ.objects.filter(success=True).count()
```

### Django-Q2 Admin Interface

Access the admin interface at `/admin/django_q/` (if admin is enabled) to view:
- Task queue
- Task history
- Scheduled tasks
- Success/failure statistics

## Troubleshooting

### Tasks Not Processing

1. Ensure `qcluster` is running: `python manage.py qcluster`
2. Check database connection
3. Verify `Q_CLUSTER` settings in `settings.py`
4. Check logs for errors

### Tasks Failing

1. Check task logs in the database: `OrmQ.objects.filter(success=False)`
2. Review error messages in `task.result`
3. Ensure task functions handle exceptions properly
4. Check worker logs

### Performance Issues

- Adjust `workers` count in `Q_CLUSTER` settings
- Increase `timeout` for long-running tasks
- Adjust `bulk` size for batch processing
- Monitor database performance

## Best Practices

1. **Keep tasks idempotent** - Tasks should be safe to retry
2. **Handle exceptions** - Always catch and log errors in tasks
3. **Use meaningful task names** - Makes debugging easier
4. **Monitor queue size** - Prevent queue from growing too large
5. **Set appropriate timeouts** - Based on expected task duration
6. **Use database transactions carefully** - Tasks run in separate processes

## Example: Adding a New Task

1. Add function to `admin_panel/tasks.py`:

```python
def my_new_task(param1, param2):
    """Process something in the background."""
    try:
        # Your logic here
        result = do_something(param1, param2)
        return {'success': True, 'result': result}
    except Exception as e:
        logger.error(f"Error in my_new_task: {str(e)}")
        return {'success': False, 'error': str(e)}
```

2. Queue it from your view:

```python
# Note: django-q2 package uses 'django_q' as the import name
from django_q.tasks import async_task
from admin_panel.tasks import my_new_task

async_task(my_new_task, param1, param2, task_name='my_task')
```

## Security Notes

- Database credentials are stored in `settings.py` - use environment variables in production
- Tasks run with the same permissions as the Django process
- Ensure proper input validation in task functions
- Use parameterized queries to prevent SQL injection

