-- Schema for DB Browser (SQLite)
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS attributes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  data_type TEXT NOT NULL DEFAULT 'text',
  is_required INTEGER DEFAULT 0,
  options TEXT
);

CREATE TABLE IF NOT EXISTS category_attributes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  category_id INTEGER NOT NULL,
  attribute_id INTEGER NOT NULL,
  UNIQUE(category_id, attribute_id),
  FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE,
  FOREIGN KEY(attribute_id) REFERENCES attributes(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  sku TEXT NOT NULL UNIQUE,
  description TEXT,
  price REAL DEFAULT 0,
  category_id INTEGER NOT NULL,
  created_at TEXT DEFAULT (datetime('now')),
  FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS product_attribute_values (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  attribute_id INTEGER NOT NULL,
  value TEXT,
  UNIQUE(product_id, attribute_id),
  FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
  FOREIGN KEY(attribute_id) REFERENCES attributes(id) ON DELETE CASCADE
);

-- Seed data for Dresses and Shoes
INSERT OR IGNORE INTO categories (id, name, description) VALUES
  (1, 'Dresses', 'All types of dresses'),
  (2, 'Shoes', 'Footwear');

-- Attributes examples
INSERT OR IGNORE INTO attributes (id, name, data_type, is_required, options) VALUES
  (1, 'Size', 'select', 1, 'XS,S,M,L,XL,XXL'),
  (2, 'Color', 'select', 0, 'Red,Blue,Green,Black,White'),
  (3, 'Material', 'text', 0, NULL),
  (4, 'OS', 'select', 1, 'Android,iOS'),
  (5, 'RAM', 'select', 1, '4GB,6GB,8GB,12GB'),
  (6, 'Battery Size', 'number', 0, NULL),
  (7, 'Dial Color', 'select', 0, 'Black,Blue,White,Gold,Silver'),
  (8, 'Dial Size', 'number', 0, NULL),
  (9, 'Strap Type', 'select', 0, 'Metal,Leather,Silicone,Fabric');

-- Map attributes to Dresses and Shoes
INSERT OR IGNORE INTO category_attributes (category_id, attribute_id) VALUES
  (1, 1), -- Size
  (1, 2), -- Color
  (1, 3), -- Material
  (2, 1), -- Size
  (2, 2); -- Color
