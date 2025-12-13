# Technical Implementation Guide

## Overview

This document provides technical specifications and implementation guidelines for the Fabric Sense ERP system.

---

## Technology Stack

### Core Platform
- **Framework**: Frappe Framework (v14+)
- **ERP**: ERPNext (v14+)
- **Backend**: Python 3.10+
- **Frontend**: JavaScript (ES6+), jQuery
- **Database**: MariaDB 10.6+
- **Web Server**: Nginx
- **Application Server**: Gunicorn

### Development Tools
- **Version Control**: Git
- **Code Editor**: VS Code / PyCharm
- **Testing**: Frappe Test Framework
- **Documentation**: Markdown

---

## Project Structure

```
fabric_sense/
├── fabric_sense/
│   ├── __init__.py
│   ├── hooks.py                    # App hooks and event handlers
│   ├── patches.txt                 # Database patches
│   ├── modules.txt                 # Module list
│   ├── config/
│   │   ├── desktop.py             # Desktop icons
│   │   └── docs.py                # Documentation config
│   ├── fabric_sense/              # Main module
│   │   └── doctype/               # Custom DocTypes
│   │       ├── measurement_sheet/
│   │       ├── tailoring_sheet/
│   │       ├── tailoring_job_card/
│   │       └── curtain_pattern/
│   ├── api/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── measurement.py
│   │   ├── sales_order.py
│   │   └── notifications.py
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── calculations.py
│   │   ├── notifications.py
│   │   └── sku_generator.py
│   ├── templates/                 # Email/Print templates
│   │   ├── emails/
│   │   └── print_formats/
│   ├── public/                    # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── fixtures/                  # Initial data
│       ├── custom_field.json
│       └── workflow.json
├── docs/                          # Documentation
├── requirements.txt               # Python dependencies
└── setup.py                       # App setup
```

---

## Installation & Setup

### 1. Prerequisites

```bash
# Install Frappe Bench
pip install frappe-bench

# Create new bench
bench init frappe-bench --frappe-branch version-14
cd frappe-bench

# Install ERPNext
bench get-app erpnext --branch version-14
bench install-app erpnext
```

### 2. Install Fabric Sense App

```bash
# Get the app
bench get-app fabric_sense [git-url]

# Install on site
bench --site [site-name] install-app fabric_sense

# Run migrations
bench --site [site-name] migrate

# Clear cache
bench --site [site-name] clear-cache
```

### 3. Initial Configuration

```bash
# Create roles
bench --site [site-name] add-role "Salesperson"
bench --site [site-name] add-role "Manager"

# Import fixtures
bench --site [site-name] import-doc fixtures/custom_field.json
bench --site [site-name] import-doc fixtures/workflow.json

# Restart
bench restart
```

---

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   bench --site [site-name] migrate
   bench --site [site-name] clear-cache
   bench restart
   ```

2. **Permission Errors**
   ```bash
   bench --site [site-name] set-admin-password [password]
   bench --site [site-name] add-to-role [user] [role]
   ```

3. **Database Issues**
   ```bash
   bench --site [site-name] mariadb
   ```

---

## Best Practices

1. **Code Organization**
   - Keep business logic in Python controllers
   - Use utility functions for reusable code
   - Follow Frappe coding standards

2. **Documentation**
   - Document all custom functions
   - Add docstrings to classes and methods
   - Maintain updated README

3. **Version Control**
   - Use meaningful commit messages
   - Create feature branches
   - Review code before merging

4. **Testing**
   - Write unit tests for critical functions
   - Test workflows end-to-end
   - Perform load testing before production

---

## Resources

- [Frappe Framework Documentation](https://frappeframework.com/docs)
- [ERPNext Documentation](https://docs.erpnext.com)
- [Frappe Forum](https://discuss.erpnext.com)
- [GitHub Repository](https://github.com/frappe/frappe)

---

For questions or support, contact: info@yourcompany.com
