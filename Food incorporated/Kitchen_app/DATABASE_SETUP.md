# Database Setup Guide

This backend can connect to multiple types of databases. Follow the instructions below for your setup.

## Quick Start (Local Development)

The default configuration uses **SQLite**, which requires no setup:

```bash
python -m pip install -r requirements.txt
python server.py
```

The database file will be created automatically as `foodinc.db`.

---

## Database Options

### 1. SQLite (Default - Local Development)

**Pros:** No setup, file-based, perfect for testing  
**Cons:** Not suitable for production

**Configuration:**
```bash
# In .env
DATABASE_URL=sqlite:///foodinc.db
```

**No additional installation needed!**

---

### 2. PostgreSQL (Recommended for Production)

**Pros:** Reliable, scalable, great for multiple concurrent users  
**Cons:** Requires database server setup

**Installation:**

1. Install PostgreSQL on your system or use a hosted service (Heroku, AWS RDS, DigitalOcean, etc.)

2. Create a database:
```sql
CREATE DATABASE foodinc;
CREATE USER foodinc_user WITH PASSWORD 'your_secure_password';
ALTER ROLE foodinc_user SET client_encoding TO 'utf8';
ALTER ROLE foodinc_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE foodinc_user SET default_transaction_deferrable TO on;
ALTER ROLE foodinc_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE foodinc TO foodinc_user;
```

3. Update `.env`:
```bash
DATABASE_URL=postgresql://foodinc_user:your_secure_password@localhost:5432/foodinc
```

4. Install Python dependencies:
```bash
python -m pip install -r requirements.txt
python server.py
```

---

### 3. MySQL (Alternative)

**Pros:** Popular, widely supported  
**Cons:** Requires database server setup

**Installation:**

1. Install MySQL and create a database:
```sql
CREATE DATABASE foodinc;
CREATE USER 'foodinc_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON foodinc.* TO 'foodinc_user'@'localhost';
FLUSH PRIVILEGES;
```

2. Update `.env`:
```bash
DATABASE_URL=mysql+pymysql://foodinc_user:your_secure_password@localhost:3306/foodinc
```

3. Install Python dependencies:
```bash
python -m pip install -r requirements.txt
python server.py
```

---

## Deployment Configurations

### Heroku with PostgreSQL

1. Create a Heroku app:
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
```

2. Heroku automatically sets `DATABASE_URL`. Set other environment variables:
```bash
heroku config:set ALLOWED_ORIGINS="https://your-domain.com,https://menu.your-domain.com"
heroku config:set DEBUG=False
```

3. Push your code:
```bash
git push heroku main
```

### AWS RDS with PostgreSQL

1. Create RDS instance in AWS Console
2. Update `.env`:
```bash
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/foodinc
ALLOWED_ORIGINS=https://your-domain.com
```

### DigitalOcean Managed Database

1. Create a managed PostgreSQL database
2. Download the CA certificate from DigitalOcean
3. Update `.env`:
```bash
DATABASE_URL=postgresql://doadmin:password@db-host:25061/foodinc?sslmode=require
```

---

## CORS Configuration for Multiple Servers

By default, the server accepts connections from anywhere. For production, restrict to specific servers:

```bash
# Allow specific domains
ALLOWED_ORIGINS=https://menu.foodinc.com,https://kitchen.foodinc.com,https://admin.foodinc.com

# Or keep open during development
ALLOWED_ORIGINS=*
```

---

## Verifying Your Setup

Once configured, test the connection:

```bash
curl http://localhost:5000/health
```

Expected response:
```json
{"status": "healthy", "message": "Server is running"}
```

Get all tables:
```bash
curl http://localhost:5000/tables
```

---

## Troubleshooting

### "No module named 'flask_sqlalchemy'"
```bash
pip install flask-sqlalchemy python-dotenv
```

### "PostgreSQL connection refused"
- Check PostgreSQL is running
- Verify credentials and host in DATABASE_URL
- Ensure database exists

### "Table already exists"
- This is normal. The app won't reinitialize if data exists
- To reset: Delete `foodinc.db` (SQLite) or drop/recreate the database

### CORS errors in browser
- Check `ALLOWED_ORIGINS` includes your frontend domain
- For development, use `ALLOWED_ORIGINS=*`
