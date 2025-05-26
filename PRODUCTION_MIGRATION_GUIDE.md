# 🚀 Production Migration Guide - User Preferences Feature

## ⚠️ IMPORTANT: Read Before Deploying

This guide ensures **zero data loss** when deploying the user preferences feature to production.

## 📋 Pre-Deployment Checklist

### 1. **Backup Your Database** 
```bash
# Create a backup before any migration
cp database.db database_backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. **Check Current Database State**
```bash
# Check if user_preferences table exists
sqlite3 database.db "SELECT name FROM sqlite_master WHERE type='table' AND name='user_preferences';"

# If it exists, check its schema
sqlite3 database.db "PRAGMA table_info(user_preferences);"
```

### 3. **Test Migration in Staging First**
- Deploy to a staging environment with a copy of production data
- Verify the migration works correctly
- Test all user preferences endpoints

## 🔄 Safe Migration Process

### Step 1: Stop the Application
```bash
# Stop your production server
sudo systemctl stop your-app-service
# or
pkill -f "python.*main"
```

### Step 2: Run Database Migration
```bash
cd /path/to/your/backend
alembic upgrade head
```

**What the migration does safely:**
- ✅ **If table doesn't exist**: Creates it fresh
- ✅ **If table has old schema** (`preferences` column): Migrates data to new `preferences_text` column
- ✅ **If table has new schema**: Does nothing (idempotent)
- ✅ **Preserves all existing user data**

### Step 3: Verify Migration Success
```bash
# Check table was created/updated correctly
sqlite3 database.db "PRAGMA table_info(user_preferences);"

# Should show columns: id, user_id, preferences_text, last_updated
```

### Step 4: Restart Application
```bash
# Start your production server
sudo systemctl start your-app-service
# or restart your container/process
```

### Step 5: Test Endpoints
```bash
# Test the endpoints work (replace with valid auth token)
curl -X GET "https://your-domain.com/users/me/preferences" \
  -H "Authorization: Bearer YOUR_VALID_TOKEN"

curl -X POST "https://your-domain.com/users/me/preferences" \
  -H "Authorization: Bearer YOUR_VALID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"preference": "Test preference"}'
```

## 🛡️ Migration Safety Features

Our migration is **production-safe** because it:

1. **Checks existing schema** before making changes
2. **Preserves all data** by copying from old to new columns
3. **Is idempotent** - can be run multiple times safely
4. **Handles all scenarios**:
   - Fresh installation (no table)
   - Existing table with old schema (`preferences` column)
   - Existing table with new schema (`preferences_text` column)

## 📊 Data Migration Details

If you have existing user preferences data:

```sql
-- Old schema (will be migrated FROM)
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    preferences TEXT NOT NULL,  -- OLD COLUMN
    last_updated DATETIME
);

-- New schema (will be migrated TO)
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    preferences_text TEXT NOT NULL,  -- NEW COLUMN
    last_updated DATETIME DEFAULT (CURRENT_TIMESTAMP)
);
```

**Migration process**:
1. Creates temporary table with new schema
2. Copies data: `preferences` → `preferences_text`
3. Drops old table
4. Renames new table

## 🔄 Rollback Plan

If something goes wrong:

### Option 1: Restore from Backup
```bash
# Stop application
sudo systemctl stop your-app-service

# Restore backup
cp database_backup_YYYYMMDD_HHMMSS.db database.db

# Restart application
sudo systemctl start your-app-service
```

### Option 2: Run Downgrade Migration
```bash
# This will drop the user_preferences table
alembic downgrade e8fe544ecdc2
```

## ✅ Success Indicators

After migration, you should see:

1. **No errors** in migration output
2. **Table exists** with correct schema:
   ```
   id|INTEGER|0||1
   user_id|INTEGER|1||0
   preferences_text|TEXT|1||0
   last_updated|DATETIME|1|(CURRENT_TIMESTAMP)|0
   ```
3. **API endpoints respond** without database errors
4. **All existing user data preserved** (if any existed)

## 🚨 Emergency Contacts

- **If migration fails**: Restore from backup immediately
- **If data is lost**: Contact your database administrator
- **If endpoints fail**: Check application logs for detailed errors

## 📝 Post-Migration Tasks

1. **Monitor application logs** for any database-related errors
2. **Test user preferences functionality** with real user accounts
3. **Verify resume generation** includes user preferences
4. **Update documentation** to reflect new feature availability

---

**Remember**: This migration is **safe and non-destructive**. It will preserve all existing user data while updating the schema to support the new user preferences feature. 