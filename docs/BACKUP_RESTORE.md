# LibrarySphere — Backup & Restore Guide

## MySQL Backup

### Full Database Backup

```bash
mysqldump -u library_portal_user -p library_portal_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Backup with Compression

```bash
mysqldump -u library_portal_user -p library_portal_db | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz
```

### Backup Specific Tables

```bash
# Backup only catalogue data
mysqldump -u library_portal_user -p library_portal_db catalog_book catalog_author catalog_category catalog_bookcopy > catalog_backup.sql

# Backup only user/membership data
mysqldump -u library_portal_user -p library_portal_db auth_user accounts_userprofile > users_backup.sql
```

## MySQL Restore

### Restore from Full Backup

```bash
mysql -u library_portal_user -p library_portal_db < backup_20260808_120000.sql
```

### Restore from Compressed Backup

```bash
gunzip < backup_20260808_120000.sql.gz | mysql -u library_portal_user -p library_portal_db
```

## SQLite Backup (Development)

Simply copy the database file:

```bash
cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
```

Restore by replacing the file:

```bash
cp db_backup_20260808_120000.sqlite3 db.sqlite3
```

## E-Book Files Backup

Protected e-book PDFs are stored in the `protected_ebooks/` directory. Back up this directory along with the database:

```bash
tar -czf ebooks_backup_$(date +%Y%m%d_%H%M%S).tar.gz protected_ebooks/
```

Restore:

```bash
tar -xzf ebooks_backup_20260808_120000.tar.gz
```

## Media Files Backup

User-uploaded cover images and other media are in `media/`:

```bash
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

## Automated Backup Script

Create a `backup.sh` script:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Database
mysqldump -u library_portal_user -p library_portal_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# E-book files
tar -czf $BACKUP_DIR/ebooks_$DATE.tar.gz protected_ebooks/

# Media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz media/

echo "Backup completed: $DATE"
```

## Important Notes

- **Never include passwords** in backup scripts committed to version control.
- **Test your backups** regularly by restoring to a staging environment.
- **Keep backups off-site** (cloud storage, external drive).
- The `protected_ebooks/` directory contains access-controlled files — treat backups with the same security precautions.
