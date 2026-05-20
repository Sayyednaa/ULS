# SAYYEDNAA LOGISTICS — Phase 1 Showcase

A complete, fully functional fleet management web application built with **pure Django** — no external database, no React, no REST API.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup database with sample data
python manage.py migrate
python manage.py seed_data

# 3. Run the server
python manage.py runserver

# 4. Open http://localhost:8000
```

## 🔑 Demo Accounts

| Role     | Username                         | Password    | Name             |
|----------|----------------------------------|-------------|------------------|
| Admin    | admin@sayyednaalogistics.com    | admin123    | Omar Al-Rashidi  |
| Manager  | manager@sayyednaalogistics.com  | manager123  | Sara Al-Mutairi  |
| Employee | employee@sayyednaalogistics.com | employee123 | Khalid Al-Enezi  |
| Driver   | driver@sayyednaalogistics.com   | driver123   | Ahmed Hassan     |

## 📋 Features

- **4-Role Access Control** — Admin, Manager, Employee, Driver portals
- **Driver Management** — Full CRUD with document expiry tracking
- **Invoice System** — Monthly entries, archiving, Excel export
- **Deduction Center** — Track driver and employee deductions
- **Salary Slips** — Print-friendly salary slip generation
- **Notifications** — Real-time notification system with badges
- **Messaging** — Internal messaging with attachments
- **Dashboard Charts** — Revenue, orders, and distribution charts
- **Task Management** — Personal task lists for all users
- **Contact Directory** — Team member cards with quick actions
- **Dark Theme** — Premium dark UI with orange accent

## 🛠️ Tech Stack

- **Python 3.12 + Django 5.x** — MVT pattern
- **SQLite** — Zero-config database
- **Tailwind CSS v4** — Via CDN
- **Alpine.js** — Lightweight interactivity
- **Chart.js** — Dashboard charts
- **openpyxl** — Excel export
