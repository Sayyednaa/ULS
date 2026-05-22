# Production Deployment Guide: Django + PostgreSQL + Nginx + Gunicorn on Ubuntu 24.04 LTS

This guide outlines the step-by-step process to deploy the **Fleet & Logistics OS** on a clean **Ubuntu 24.04 LTS** VPS using **PostgreSQL** as the primary database, **Gunicorn** as the WSGI server, **Nginx** as the reverse proxy/static server, and **Let's Encrypt** for SSL.

---

## 📋 Table of Contents
1. [Prerequisites & System Setup](#1-prerequisites--system-setup)
2. [Database Setup (PostgreSQL)](#2-database-setup-postgresql)
3. [Project Directory & Permissions](#3-project-directory--permissions)
4. [Python Virtual Environment & Dependencies](#4-python-virtual-environment--dependencies)
5. [Production Configuration (.env)](#5-production-configuration-env)
6. [Database Migrations & Initial Seed](#6-database-migrations--initial-seed)
7. [Gunicorn Socket & Service Configuration](#7-gunicorn-socket--service-configuration)
8. [Nginx Reverse Proxy & Static Files Configuration](#8-nginx-reverse-proxy--static-files-configuration)
9. [SSL Certificate Installation (Let's Encrypt)](#9-ssl-certificate-installation-lets-encrypt)
10. [Updating the Application (CI/CD / Manual redeploys)](#10-updating-the-application-cicd--manual-redeploys)
11. [Monitoring & Troubleshooting](#11-monitoring--troubleshooting)

---

## 1. Prerequisites & System Setup

Connect to your VPS via SSH and update the system packages:
```bash
sudo apt update && sudo apt upgrade -y
```

Install system-level packages including Python 3, PostgreSQL, Nginx, Git, and Gunicorn dependencies:
```bash
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib libpq-dev nginx curl git certbot python3-certbot-nginx
```

---

## 2. Database Setup (PostgreSQL)

By default, PostgreSQL is started and enabled. Verify the status:
```bash
sudo systemctl status postgresql
```

1. Log into the PostgreSQL interactive shell as the admin `postgres` user:
   ```bash
   sudo -i -u postgres psql
   ```

2. Create the production database:
   ```sql
   CREATE DATABASE uls_prod;
   ```

3. Create the database user and assign a strong, secure password:
   ```sql
   CREATE USER uls_user WITH PASSWORD 'ChangeThisToASecurePassword123!';
   ```

4. Configure connection parameters for Django compatibility:
   ```sql
   ALTER ROLE uls_user SET client_encoding TO 'utf8';
   ALTER ROLE uls_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE uls_user SET timezone TO 'Asia/Dubai';
   ```

5. Grant all privileges on the database to the new user:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE uls_prod TO uls_user;
   ```

6. Exit the PostgreSQL interactive shell:
   ```sql
   \q
   ```
   ```bash
   exit
   ```

---

## 3. Project Directory & Permissions

For security, it is highly recommended to run the Django process under a dedicated user account rather than `root`.

1. Create a dedicated system user `django`:
   ```bash
   sudo adduser --system --group --home /var/www/uls django
   ```

2. Clone your repository into the app folder (or move your existing files here):
   ```bash
   sudo git clone https://github.com/your-username/ULS.git /var/www/uls/app
   ```
   *(Note: Ensure you replace `https://github.com/your-username/ULS.git` with your repository URL).*

3. Transfer directory ownership to the `django` user:
   ```bash
   sudo chown -R django:django /var/www/uls
   ```

---

## 4. Python Virtual Environment & Dependencies

Switch to the `django` user to set up Python and install the workspace dependencies:

1. Switch shell user:
   ```bash
   sudo -u django -i
   ```

2. Navigate to the application root directory:
   ```bash
   cd /var/www/uls/app
   ```

3. Initialize the Python virtual environment:
   ```bash
   python3 -m venv .venv
   ```

4. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

5. Upgrade pip and install all Python requirements:
   ```bash
   pip install --upgrade pip
   ```
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The `requirements.txt` file already includes `psycopg2` and `psycopg2-binary` for PostgreSQL integration).*

---

## 5. Production Configuration (.env)

While still logged in as the `django` user in `/var/www/uls/app`, create your production environment settings file:

1. Open `.env` for editing:
   ```bash
   nano .env
   ```

2. Add the following environment variables, ensuring to update the credentials, domains, and secrets:
   ```env
   DEBUG=False
   SECRET_KEY=django-secure-cryptographically-random-key-here-generate-with-openssl
   DATABASE_URL=postgres://uls_user:ChangeThisToASecurePassword123!@localhost:5432/uls_prod
   ALLOWED_HOSTS=unpredictedcode.com,www.unpredictedcode.com
   CSRF_TRUSTED_ORIGINS=https://unpredictedcode.com,https://www.unpredictedcode.com
   SECURE_SSL_REDIRECT=True
   ```
   > [!TIP]
   > You can generate a cryptographically secure `SECRET_KEY` using python:
   > ```bash
   > python3 -c "import secrets; print(secrets.token_urlsafe(50))"
   > ```

3. Save and close the file (`Ctrl+O`, `Enter`, `Ctrl+X`).

4. Restrict permissions to the `.env` file so only the `django` user can read it:
   ```bash
   chmod 600 .env
   ```

---

## 6. Database Migrations & Initial Seed

With your virtual environment activated, run the following setup commands:

1. Collect all static files for Nginx / WhiteNoise:
   ```bash
   python manage.py collectstatic --no-input
   ```

2. Execute database migrations:
   ```bash
   python manage.py migrate
   ```

3. Seed initial mockup data (creates portals, default roles, and configuration):
   ```bash
   python manage.py seed_data
   ```

4. Exit the `django` user session back to your admin user shell:
   ```bash
   exit
   ```

---

## 7. Gunicorn Socket & Service Configuration

We will use systemd to manage Gunicorn. It will auto-start Gunicorn on system boot and restart it if it crashes. Gunicorn will communicate with Nginx via a UNIX socket.

### A. Gunicorn Socket Configuration
1. Create the systemd socket file:
   ```bash
   sudo nano /etc/systemd/system/uls.socket
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=Gunicorn socket for Fleet & Logistics OS (ULS)

   [Socket]
   ListenStream=/run/uls.sock

   [Install]
   WantedBy=sockets.target
   ```

### B. Gunicorn Service Configuration
1. Create the systemd service file:
   ```bash
   sudo nano /etc/systemd/system/uls.service
   ```

2. Add the following configuration:
   ```ini
   [Unit]
   Description=Gunicorn daemon for Fleet & Logistics OS (ULS)
   Requires=uls.socket
   After=network.target

   [Service]
   User=django
   Group=www-data
   WorkingDirectory=/var/www/uls/app
   ExecStart=/var/www/uls/app/.venv/bin/gunicorn \
             --access-logfile - \
             --workers 3 \
             --bind unix:/run/uls.sock \
             fleetops.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

### C. Enable and Start Gunicorn
1. Reload systemd daemons:
   ```bash
   sudo systemctl daemon-reload
   ```

2. Start and enable the Gunicorn socket:
   ```bash
   sudo systemctl start uls.socket
   sudo systemctl enable uls.socket
   ```

3. Confirm that the socket file `/run/uls.sock` has been generated and Gunicorn is active:
   ```bash
   sudo systemctl status uls.socket
   ```

---

## 8. Nginx Reverse Proxy & Static Files Configuration

Nginx will face the public web. It will handle incoming HTTP/HTTPS connections, serve static and uploaded media files directly for high performance, and route app requests to the Gunicorn UNIX socket.

1. Create a new Nginx server configuration block:
   ```bash
   sudo nano /etc/nginx/sites-available/uls
   ```

2. Add the following content, replacing `unpredictedcode.com` and `www.unpredictedcode.com` with your production domains:
   ```nginx
   server {
       listen 80;
       server_name unpredictedcode.com www.unpredictedcode.com;

       # Disable client body size limits for uploads (e.g. driver dossiers/EXCEL imports)
       client_max_body_size 20M;

       # Nginx directly serves Static Files
       location /static/ {
           alias /var/www/uls/app/staticfiles/;
           expires 30d;
           add_header Cache-Control "public, no-transform";
       }

       # Nginx directly serves Media Uploads (safeguarded)
       location /media/ {
           alias /var/www/uls/app/media/;
           expires 30d;
           add_header Cache-Control "public, no-transform";
       }

       # Reverse proxy to Gunicorn socket
       location / {
           include proxy_params;
           proxy_pass http://unix:/run/uls.sock;
       }
   }
   ```

3. Enable the configuration by symlinking it into the active site directory:
   ```bash
   sudo ln -s /etc/nginx/sites-available/uls /etc/nginx/sites-enabled/
   ```

4. Test your Nginx configuration syntax:
   ```bash
   sudo nginx -t
   ```

5. Restart Nginx to apply configurations:
   ```bash
   sudo systemctl restart nginx
   ```

6. Grant Nginx read/execute permissions to the static and media files:
   ```bash
   sudo usermod -aG django www-data
   sudo chmod 710 /var/www/uls
   ```

---

## 9. SSL Certificate Installation (Let's Encrypt)

Secure the application with SSL using Let's Encrypt Certbot.

1. Execute the Certbot command for Nginx:
   ```bash
   sudo certbot --nginx -d unpredictedcode.com -d www.unpredictedcode.com
   ```

2. Follow the prompt questions (provide your admin email and agree to terms). Certbot will automatically verify ownership, generate certificates, and rewrite the Nginx server block to handle SSL redirection.

3. Verify that the automatic renewal cron job is configured correctly:
   ```bash
   sudo systemctl status certbot.timer
   ```

---

## 10. Updating the Application (CI/CD / Manual redeploys)

To push code updates from git to the server:

1. Switch to the `django` user and pull the latest codebase changes:
   ```bash
   sudo -u django -i
   cd /var/www/uls/app
   source .venv/bin/activate
   git pull origin main
   ```

2. Run migration checks and collect new static assets:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --no-input
   ```
   ```bash
   exit
   ```

3. Restart the WSGI process to load changes:
   ```bash
   sudo systemctl restart uls.service
   ```

4. Reload Nginx (only needed if configuration blocks were modified):
   ```bash
   sudo systemctl reload nginx
   ```

---

## 11. Monitoring & Troubleshooting

### Check application logs:
To view Gunicorn stdout/stderr stream (Django stack traces and requests):
```bash
sudo journalctl -u uls.service -f
```

### Check Nginx web server logs:
- Request logs: `sudo tail -f /var/log/nginx/access.log`
- Web server errors: `sudo tail -f /var/log/nginx/error.log`

### Resetting services:
```bash
sudo systemctl restart uls.service
sudo systemctl restart nginx
```
