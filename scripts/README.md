# Scripts

Utility scripts for database initialization and management.

## Available Scripts

### `create_superuser.py`
Creates an admin/super_user account for the application.

**Usage:**
```bash
cd epet-backend
python scripts/create_superuser.py
```

### `init_sample_data.py`
Initializes the database with sample products and categories.

**Usage:**
```bash
python scripts/init_sample_data.py
```

### `init_subcategories.py`
Initializes subcategories for the store.

**Usage:**
```bash
python scripts/init_subcategories.py
```

### `update_categories.py`
Updates existing categories in the database.

**Usage:**
```bash
python scripts/update_categories.py
```

### `update_user_status.py`
Updates user account status (active/inactive/banned).

**Usage:**
```bash
python scripts/update_user_status.py
```

### `test_admin.py`
Tests admin authentication and permissions.

**Usage:**
```bash
python scripts/test_admin.py
```

## Notes

- Make sure MongoDB is running before executing any scripts
- Ensure your `.env` file is properly configured
- Run these scripts from the `epet-backend` directory
