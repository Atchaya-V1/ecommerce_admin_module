# Keyswecommerce Catalog Admin (Flask + SQLite)

A minimal internal tool to manage product categories, attributes, and products with category-specific attributes.

## Quickstart (Windows PowerShell)

```powershell
# From the project root (keyswecommerce)
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# (Optional) Initialize database from SQL schema
python - << 'PY'
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
print('Database initialized at catalog.db')
PY

# Or use DB Browser: open schema.sql and execute to create tables and seed data

# Run the dev server
$env:FLASK_APP = "app.py"
python app.py
```

Open `http://localhost:5000`.

## Managing Category-specific Attributes
- Create attributes with types like `text`, `number`, `decimal`, `boolean`, `date`, `select`, `multiselect`.
- Assign attributes to a category via `Categories → Manage`.
- While creating/editing a product, selecting a category will auto-load its attributes.

## Notes
- SQLite file is `catalog.db`. You can open it with DB Browser for SQLite.
- The schema in `schema.sql` mirrors the ORM models, so either approach works.
- To add new categories like smartphones or watches, create the category then assign attributes (e.g., OS/RAM/Battery for smartphones; Dial Color/Size/Strap for watches).
