# MySQL Setup Required

Your MySQL server is installed at `/usr/local/mysql` (v8.0.45) but is **not currently running**.

Follow these steps to complete the project setup.

---

## Step 1 — Start MySQL Server

Open **System Preferences → MySQL** and click **Start MySQL Server**.

Or run from Terminal:

```bash
sudo /usr/local/mysql/support-files/mysql.server start
```

Verify it is running:

```bash
/usr/local/mysql/bin/mysqladmin -u root -p status
```

---

## Step 2 — Add MySQL to PATH (optional but recommended)

Add this line to your `~/.zshrc` so you can use `mysql` directly:

```bash
export PATH="/usr/local/mysql/bin:$PATH"
```

Then reload:

```bash
source ~/.zshrc
```

---

## Step 3 — Create the Database and User

Open **MySQL Workbench** or a terminal MySQL session:

```bash
/usr/local/mysql/bin/mysql -u root -p
```

Then run these SQL statements **exactly as shown**:

```sql
CREATE DATABASE IF NOT EXISTS library_portal_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'library_portal_user'@'127.0.0.1'
    IDENTIFIED BY 'y8D7XJLuBPYIR%y^*2pwGufp';

GRANT ALL PRIVILEGES ON library_portal_db.*
    TO 'library_portal_user'@'127.0.0.1';

FLUSH PRIVILEGES;
```

> **Note**: The password above matches the value stored in your `.env` file.
> If you change it here, update `.env` → `DB_PASSWORD` to match.

---

## Step 4 — Run Django Migrations

```bash
cd "/Users/sk/Documents/Public Library Membership Management and Book Reservation Tracking Portal"
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

---

## Step 5 — Create a Superuser (optional)

```bash
python manage.py createsuperuser
```

Then sign in at **http://127.0.0.1:8000/admin/**.
