# InSync Setup and Configuration Guide

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Initial Setup](#initial-setup)
4. [Account Configuration](#account-configuration)
5. [Folder Sync Configuration](#folder-sync-configuration)
6. [Troubleshooting](#troubleshooting)
7. [Management Scripts](#management-scripts)
8. [Best Practices](#best-practices)
9. [Common Issues and Solutions](#common-issues-and-solutions)

## Overview

InSync is a powerful tool for syncing Google Drive, OneDrive, and Dropbox accounts to local filesystems. This guide covers setting up InSync on Ubuntu servers for bidirectional sync between local folders and cloud storage.

### Key Features
- Bidirectional sync between local and cloud storage
- Selective folder synchronization
- Command-line interface for headless servers
- Real-time file monitoring and syncing
- Conflict resolution

## Installation

### Method 1: Direct .deb Installation (Recommended)

```bash
# Download the latest InSync .deb file
wget https://d2v3c0y4nuqndt.cloudfront.net/insync_3.8.7.50404-focal_amd64.deb

# Install it
sudo dpkg -i insync_3.8.7.50404-focal_amd64.deb

# Fix any dependency issues
sudo apt --fix-broken install
```

### Method 2: Repository Installation (Alternative)

```bash
# Remove any existing InSync installations
sudo apt remove insync
sudo rm -f /etc/apt/sources.list.d/insync.list
sudo apt-key del A684470CACCAF35C 2>/dev/null || true

# Download and add the new GPG key
wget -qO - https://d2v3c0y4nuqndt.cloudfront.net/insync.key | sudo gpg --dearmor -o /usr/share/keyrings/insync-archive-keyring.gpg

# Add the repository
echo "deb [signed-by=/usr/share/keyrings/insync-archive-keyring.gpg] https://d2v3c0y4nuqndt.cloudfront.net/ubuntu $(lsb_release -cs) non-free contrib" | sudo tee /etc/apt/sources.list.d/insync.list

# Update and install
sudo apt update
sudo apt install insync
```

### Verify Installation

```bash
# Check InSync version
insync-headless version

# Check if InSync is working
insync-headless status
```

## Initial Setup

### Start InSync Daemon

```bash
# Start InSync daemon
insync-headless start

# Check if it's running
insync-headless status
```

### Available Commands

```bash
# List all available commands
insync-headless --help

# Main commands:
# - account: Manage accounts
# - selective-sync: Configure folder sync
# - status: Check sync status
# - start: Start daemon
# - quit: Stop daemon
# - pause/resume: Control syncing
```

## Account Configuration

### Add Google Drive Account

```bash
# Generate auth URL
insync-headless account add --cloud gd

# This will output a URL like:
# https://connect.insynchq.com/auth?cloud=gd&state=...
```

### Complete Authentication

1. **Copy the URL** from the command output
2. **Open the URL** in a web browser
3. **Sign in** with your Google account
4. **Copy the auth code** from the page
5. **Use the auth code immediately** (they expire quickly):

```bash
# Replace YOUR_AUTH_CODE with the actual code
insync-headless account add --cloud gd --auth-code "YOUR_AUTH_CODE"
```

### Verify Account Addition

```bash
# List all accounts
insync-headless account list

# Expected output:
# noreply@example.com (Google Drive)
```

## Folder Sync Configuration

### Open Selective Sync Interface

```bash
# Open selective sync for your account
insync-headless selective-sync --account noreply@example.com --cloud gd
```

### Understanding the Interface

The selective sync interface shows:
- **Global options** at the top
- **Folder hierarchy** from your Google Drive
- **Checkboxes** `[X]` for selected folders
- **Navigation controls** at the bottom

### Global Sync Options

- `[X] Sync new children of partially-synced folders automatically`
  - Automatically syncs new subfolders in partially synced folders
- `[ ] Sync new top-level cloud items automatically`
  - Automatically syncs new top-level items in Google Drive

### Configuring Folder Sync

1. **Navigate to target folder** using arrow keys
2. **Select folder** by pressing SPACE to toggle `[X]`
3. **Set custom location** (if needed):
   - Highlight the folder
   - Press **Ctrl+S** (^S: Sync folder to custom location...)
   - Enter local path (e.g., `/root/Zumud/Applications`)
4. **Save configuration** by pressing OK

### Sync Direction

InSync typically defaults to **bidirectional sync**:
- Local changes → sync to Google Drive
- Google Drive changes → sync to local

This is usually the desired behavior for most use cases.

## Troubleshooting

### Check Sync Status

```bash
# Basic status
insync-headless status

# Detailed status with file information
insync-headless status --verbose

# Check for errors
insync-headless error list
```

### Common Status Messages

- **SYNCED**: All files are synchronized
- **SYNCING**: Files are currently being synced
- **PAUSED**: Sync is paused
- **ERROR**: There are sync errors

### Check InSync Logs

```bash
# Check InSync application logs
tail -f ~/.config/Insync/logs/insync.log

# Check system logs
journalctl -u insync -f

# Check for InSync processes
ps aux | grep insync
```

### Verify File Locations

```bash
# Check InSync's default sync location
ls -la /root/Insync-headless/noreply@example.com/Google\ Drive/

# Check your custom sync location
ls -la /root/Zumud/Applications/

# Check Google Drive via rclone (if configured)
rclone ls gdrive:Applications/
```

### Force Sync Refresh

```bash
# Pause and resume to force refresh
insync-headless pause
sleep 2
insync-headless resume

# Check status again
insync-headless status
```

## Management Scripts

### Comprehensive Management Script

```bash
cat > /root/insync_management.sh << 'EOF'
#!/bin/bash

LOG_FILE="/root/insync_sync.log"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to check if InSync is running
check_insync_status() {
    if insync-headless status >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start InSync if not running
start_insync() {
    if ! check_insync_status; then
        log_message "Starting InSync daemon..."
        insync-headless start
        sleep 5
    fi
}

# Function to show detailed status
show_status() {
    echo "=== InSync Status ==="
    insync-headless status
    
    echo -e "\n=== Account List ==="
    insync-headless account list
    
    echo -e "\n=== Error List ==="
    insync-headless error list
    
    echo -e "\n=== Process Status ==="
    ps aux | grep insync | grep -v grep
}

# Function to open selective sync
open_selective_sync() {
    echo "Opening selective sync interface..."
    insync-headless selective-sync --account noreply@example.com --cloud gd
}

# Function to pause/resume sync
pause_sync() {
    log_message "Pausing InSync sync..."
    insync-headless pause
}

resume_sync() {
    log_message "Resuming InSync sync..."
    insync-headless resume
}

# Function to test sync
test_sync() {
    log_message "Testing sync functionality..."
    
    # Create test file
    TEST_FILE="/root/Zumud/Applications/insync_test_$(date +%s).txt"
    echo "Test file created at $(date)" > "$TEST_FILE"
    
    echo "Created test file: $TEST_FILE"
    echo "Check Google Drive in 30 seconds to see if it syncs..."
    
    sleep 30
    
    # Check if file exists in Google Drive (via rclone if available)
    if command -v rclone &> /dev/null; then
        echo "Checking Google Drive for test file..."
        rclone ls gdrive:Applications/ | grep insync_test
    fi
}

# Function to show logs
show_logs() {
    echo "=== Recent InSync Logs ==="
    tail -20 ~/.config/Insync/logs/insync.log 2>/dev/null || echo "No logs found"
    
    echo -e "\n=== Recent Application Logs ==="
    tail -20 "$LOG_FILE"
}

# Main script logic
case "$1" in
    "start")
        start_insync
        ;;
    "status")
        show_status
        ;;
    "selective-sync")
        open_selective_sync
        ;;
    "pause")
        pause_sync
        ;;
    "resume")
        resume_sync
        ;;
    "test")
        test_sync
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        insync-headless quit
        ;;
    "restart")
        insync-headless quit
        sleep 3
        insync-headless start
        ;;
    *)
        echo "Usage: $0 {start|status|selective-sync|pause|resume|test|logs|stop|restart}"
        echo "  start          - Start InSync daemon"
        echo "  status         - Show detailed InSync status"
        echo "  selective-sync - Open selective sync interface"
        echo "  pause          - Pause syncing"
        echo "  resume         - Resume syncing"
        echo "  test           - Test sync functionality"
        echo "  logs           - Show recent logs"
        echo "  stop           - Stop InSync daemon"
        echo "  restart        - Restart InSync daemon"
        exit 1
        ;;
esac
EOF

chmod +x /root/insync_management.sh
```

### Automated Sync Service

```bash
# Create systemd service for automated monitoring
cat > /etc/systemd/system/insync-monitor.service << 'EOF'
[Unit]
Description=InSync Monitor Service
After=network.target

[Service]
Type=oneshot
ExecStart=/root/insync_management.sh status
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/insync-monitor.timer << 'EOF'
[Unit]
Description=Monitor InSync every 10 minutes
Requires=insync-monitor.service

[Timer]
OnCalendar=*:0/10
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable the monitor
systemctl daemon-reload
systemctl enable insync-monitor.timer
systemctl start insync-monitor.timer
```

## Best Practices

### 1. Authentication
- **Use auth codes immediately** - they expire within minutes
- **Keep InSync running** - don't stop the daemon unnecessarily
- **Monitor logs regularly** - check for errors and issues

### 2. Folder Configuration
- **Use selective sync** - only sync necessary folders
- **Set custom paths** - ensure folders sync to desired locations
- **Test sync functionality** - verify bidirectional sync works

### 3. Monitoring
- **Regular status checks** - monitor sync health
- **Error monitoring** - address sync errors promptly
- **Log monitoring** - track sync activity and issues

### 4. Performance
- **Limit concurrent syncs** - avoid overwhelming the system
- **Monitor disk space** - ensure adequate storage
- **Regular maintenance** - restart InSync periodically

## Common Issues and Solutions

### Issue 1: Auth Code Invalid
**Problem**: `Auth code received is invalid`
**Solution**: 
- Auth codes expire quickly (5-10 minutes)
- Generate a new auth code immediately
- Use the code right away

### Issue 2: Nothing Syncing
**Problem**: Status shows "SYNCED" but files don't sync
**Solutions**:
- Check if folders are properly selected in selective sync
- Verify custom paths are set correctly
- Check InSync logs for errors
- Restart InSync daemon

### Issue 3: Permission Errors
**Problem**: Cannot access sync directories
**Solution**:
- Check file permissions on sync directories
- Ensure InSync has read/write access
- Fix ownership issues if necessary

### Issue 4: Sync Conflicts
**Problem**: Files not syncing due to conflicts
**Solution**:
- Check `insync-headless error list`
- Resolve conflicts manually
- Use conflict resolution options in InSync

### Issue 5: InSync Not Starting
**Problem**: Daemon fails to start
**Solution**:
- Check system resources (memory, disk space)
- Verify InSync installation
- Check system logs for errors
- Reinstall InSync if necessary

### Issue 6: Slow Sync Performance
**Problem**: Sync is very slow
**Solution**:
- Check network connectivity
- Monitor system resources
- Consider pausing other sync operations
- Restart InSync daemon

## Testing Sync Functionality

### Create Test Script

```bash
cat > /root/test_insync_sync.sh << 'EOF'
#!/bin/bash

echo "=== InSync Sync Test ==="
echo "Date: $(date)"

# Test 1: Check InSync status
echo -e "\n1. Checking InSync status..."
insync-headless status

# Test 2: Create test file locally
echo -e "\n2. Creating test file locally..."
TEST_FILE="/root/Zumud/Applications/insync_test_$(date +%s).txt"
echo "Test file created at $(date)" > "$TEST_FILE"
echo "Created: $TEST_FILE"

# Test 3: Wait for sync
echo -e "\n3. Waiting 30 seconds for sync..."
sleep 30

# Test 4: Check if file synced to Google Drive
echo -e "\n4. Checking Google Drive for test file..."
if command -v rclone &> /dev/null; then
    rclone ls gdrive:Applications/ | grep insync_test
else
    echo "rclone not available - check Google Drive manually"
fi

# Test 5: Check InSync logs
echo -e "\n5. Recent InSync logs:"
tail -5 ~/.config/Insync/logs/insync.log 2>/dev/null || echo "No logs found"

echo -e "\n=== Test Complete ==="
EOF

chmod +x /root/test_insync_sync.sh
```

### Run Tests

```bash
# Run comprehensive test
/root/test_insync_sync.sh

# Test specific functionality
/root/insync_management.sh test
```

## Conclusion

This guide provides a comprehensive approach to setting up and managing InSync for Google Drive synchronization. The key to successful InSync deployment is:

1. **Proper installation** and authentication
2. **Correct folder configuration** using selective sync
3. **Regular monitoring** and maintenance
4. **Quick troubleshooting** when issues arise

For production use, consider implementing the management scripts and automated monitoring to ensure reliable sync operations.

---

**Last Updated**: August 2025
**Version**: 1.0
**Tested On**: Ubuntu 22.04 LTS 