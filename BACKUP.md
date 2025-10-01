# Workshop Schedule Backup & Restore Guide

This guide explains how to backup and restore the workshop schedule data (`workshop_schedule.json`) for the FabricStudio Controller.

## Overview

The backup/restore system uses the application's API endpoints to safely backup and restore workshop schedule data. It works with both local and Docker deployments.

## Prerequisites

The backup script requires the following tools:
- `curl` - for API communication
- `jq` - for JSON processing

### Install on macOS:
```bash
brew install jq
```

### Install on Ubuntu/Debian:
```bash
sudo apt-get install jq curl
```

## Quick Start

### Create a Backup

```bash
./backup-restore-workshop.sh backup
```

Output:
```
═══════════════════════════════════════
   FabricStudio Workshop Backup
═══════════════════════════════════════

🔄 Connecting to API at http://localhost:8000...
📥 Downloading workshop schedule...
✅ Backup created successfully!
   File: ./backups/workshop_schedule_20251001_123220.json
   Size: 1234 bytes
   Entries: 5 workshops
```

### List Available Backups

```bash
./backup-restore-workshop.sh list
```

Output:
```
📋 Available backups in ./backups:

Backup File                              Size        Entries    Date
---------------------------------------- ----------  --------   -------------------
workshop_schedule_20251001_123220.json   1KB         5          2025-10-01 12:32:20
workshop_schedule_20251001_100000.json   0KB         0          2025-10-01 10:00:00

Total: 2 backup(s)
```

### Restore from a Specific Backup

```bash
./backup-restore-workshop.sh restore backups/workshop_schedule_20251001_123220.json
```

The script will ask for confirmation before restoring:
```
⚠️  This will replace the current workshop schedule with 5 entries
   from: workshop_schedule_20251001_123220.json

Continue? (y/N):
```

### Restore from Latest Backup

```bash
./backup-restore-workshop.sh latest
```

## Command Reference

### backup
Create a new backup of the current workshop schedule.

```bash
./backup-restore-workshop.sh backup
```

**How it works:**
1. Connects to the API at `/api/workshops`
2. Downloads the current workshop schedule
3. Saves to `./backups/workshop_schedule_YYYYMMDD_HHMMSS.json`
4. Automatically cleans up old backups (keeps last 30)

**Fallback:** If API is not accessible, attempts to copy directly from Docker container.

### restore
Restore workshop schedule from a specific backup file.

```bash
./backup-restore-workshop.sh restore <backup_file>
```

**Example:**
```bash
./backup-restore-workshop.sh restore backups/workshop_schedule_20251001_123220.json
```

**How it works:**
1. Reads the backup file
2. Validates JSON content
3. Asks for confirmation
4. Uploads to API at `/api/workshops`
5. Confirms successful restore

**Fallback:** If API is not accessible, attempts to copy directly to Docker container.

### latest
Restore from the most recent backup (shortcut for restore with automatic file selection).

```bash
./backup-restore-workshop.sh latest
```

### list
Display all available backups with details.

```bash
./backup-restore-workshop.sh list
```

Shows:
- Backup filename
- File size
- Number of workshop entries
- Creation date/time

## Environment Variables

### API_URL
Specify a custom API endpoint (default: `http://localhost:8000`)

```bash
# Backup from remote server
API_URL=http://192.168.1.100:8000 ./backup-restore-workshop.sh backup

# Restore to remote server
API_URL=http://server.example.com:8000 ./backup-restore-workshop.sh restore backups/file.json
```

### CONTAINER_NAME
Specify Docker container name (default: `fabricchanger-fabricstudio-1`)

```bash
CONTAINER_NAME=my-custom-container ./backup-restore-workshop.sh backup
```

## Automated Backups

### Daily Backup with Cron

Add to your crontab (`crontab -e`):

```bash
# Backup workshop schedule daily at 2 AM
0 2 * * * cd /path/to/FabricChanger && ./backup-restore-workshop.sh backup >> backups/backup.log 2>&1

# Backup every 6 hours
0 */6 * * * cd /path/to/FabricChanger && ./backup-restore-workshop.sh backup >> backups/backup.log 2>&1
```

### Backup Before Updates

Create a pre-update script:

```bash
#!/bin/bash
# pre-update.sh - Run before updating the application

echo "Creating backup before update..."
./backup-restore-workshop.sh backup

if [ $? -eq 0 ]; then
    echo "✅ Backup completed, safe to proceed with update"
    exit 0
else
    echo "❌ Backup failed, aborting update"
    exit 1
fi
```

## Backup Storage

### Local Backups
- **Location:** `./backups/` directory
- **Format:** `workshop_schedule_YYYYMMDD_HHMMSS.json`
- **Retention:** Last 30 backups (automatic cleanup)

### Backup to Cloud Storage

#### Amazon S3
```bash
./backup-restore-workshop.sh backup
aws s3 cp backups/ s3://my-bucket/fabricstudio-backups/ --recursive
```

#### Google Cloud Storage
```bash
./backup-restore-workshop.sh backup
gsutil -m cp -r backups/ gs://my-bucket/fabricstudio-backups/
```

#### Rsync to Remote Server
```bash
./backup-restore-workshop.sh backup
rsync -avz backups/ user@remote-server:/backups/fabricstudio/
```

## Disaster Recovery

### Scenario 1: Accidental Deletion

```bash
# List available backups
./backup-restore-workshop.sh list

# Restore from latest backup
./backup-restore-workshop.sh latest
```

### Scenario 2: Container Restart/Rebuild

If you're rebuilding a Docker container:

```bash
# Before rebuilding - create backup
./backup-restore-workshop.sh backup

# Rebuild container
docker-compose down
docker-compose build
docker-compose up -d

# After rebuild - restore data
./backup-restore-workshop.sh latest
```

### Scenario 3: Migration to New Server

On old server:
```bash
./backup-restore-workshop.sh backup
scp backups/workshop_schedule_*.json user@new-server:/tmp/
```

On new server:
```bash
./backup-restore-workshop.sh restore /tmp/workshop_schedule_*.json
```

## Backup File Format

Backup files are standard JSON arrays:

```json
[
  {
    "id": 1633024800000,
    "date": "2025-10-15",
    "workshopType": "FAZ Workshop",
    "vmCount": 5,
    "comment": "Training session for new team",
    "created": "2025-10-01T10:00:00.000Z"
  },
  {
    "id": 1633111200000,
    "date": "2025-10-20",
    "workshopType": "FAD/FWB Workshop",
    "vmCount": 3,
    "comment": "Customer demo",
    "created": "2025-10-01T11:00:00.000Z"
  }
]
```

You can manually edit backup files if needed, but ensure valid JSON format.

## Troubleshooting

### API Not Accessible

**Error:** `❌ API not accessible at http://localhost:8000`

**Solutions:**
1. Check if the application is running: `curl http://localhost:8000`
2. For Docker: `docker ps` to verify container is running
3. Check port number matches your configuration
4. Use `API_URL` environment variable for custom ports

**Fallback:** Script will automatically try Docker container method.

### Permission Denied

**Error:** Permission denied when running script

**Solution:**
```bash
chmod +x backup-restore-workshop.sh
```

### Missing jq Command

**Error:** `Required command not found: jq`

**Solution:**
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# CentOS/RHEL
sudo yum install jq
```

### Container Not Found

**Error:** `Container not accessible`

**Solutions:**
1. Check container name: `docker ps`
2. Set correct container name: `CONTAINER_NAME=your-container-name ./backup-restore-workshop.sh backup`

### Corrupted Backup

If a backup file appears corrupted:

```bash
# Validate JSON
jq '.' backups/workshop_schedule_20251001_123220.json

# If invalid, try an older backup
./backup-restore-workshop.sh list
./backup-restore-workshop.sh restore backups/workshop_schedule_OLDER_FILE.json
```

## Best Practices

1. **Regular Backups:** Schedule automatic backups at least daily
2. **Before Changes:** Always backup before major updates or configuration changes
3. **Test Restores:** Periodically test restore process to ensure backups are valid
4. **Off-site Storage:** Copy backups to cloud storage or remote server
5. **Retention Policy:** Keep backups for at least 30 days
6. **Version Control:** For critical changes, consider keeping additional backup copies
7. **Documentation:** Note what changes were made after each backup

## Security Considerations

- Backup files contain workshop schedule data (dates, comments, VM counts)
- Store backups in secure location with appropriate permissions
- Use HTTPS for remote API access in production
- Consider encryption for sensitive backup data
- Restrict access to backup directory

## Integration Examples

### Git Integration

```bash
#!/bin/bash
# backup-and-commit.sh - Backup and commit to git

./backup-restore-workshop.sh backup
git add backups/
git commit -m "Automated backup: $(date +%Y-%m-%d)"
git push origin main
```

### Webhook Notification

```bash
#!/bin/bash
# backup-with-notification.sh

./backup-restore-workshop.sh backup

if [ $? -eq 0 ]; then
    curl -X POST https://hooks.slack.com/your-webhook \
        -d '{"text":"Workshop backup completed successfully"}'
fi
```

### Docker Compose Hook

Add to your docker-compose.yml:

```yaml
services:
  backup:
    image: alpine
    volumes:
      - ./:/app
    command: sh -c "apk add --no-cache curl jq && cd /app && ./backup-restore-workshop.sh backup"
    depends_on:
      - fabricstudio
```

## Support

For issues or questions:
- Check this documentation first
- Review script output for error messages
- Verify API is accessible: `curl http://localhost:8000/api/workshops`
- Check container status: `docker ps`
- Review application logs: `docker logs <container_name>`

## License

This backup script is part of the FabricStudio Controller project.

