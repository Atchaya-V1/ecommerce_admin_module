from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    attributes = db.relationship(
        "CategoryAttribute", back_populates="category", cascade="all, delete-orphan"
    )
    products = db.relationship(
        "Product", back_populates="category", cascade="all, delete"
    )


class Attribute(db.Model):
    __tablename__ = "attributes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    data_type = db.Column(db.String(20), nullable=False, default="text")
    is_required = db.Column(db.Boolean, default=False)
    options = db.Column(db.Text)  # Comma-separated values for select/multiselect

    categories = db.relationship(
        "CategoryAttribute", back_populates="attribute", cascade="all, delete-orphan"
    )


class CategoryAttribute(db.Model):
    __tablename__ = "category_attributes"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    attribute_id = db.Column(db.Integer, db.ForeignKey("attributes.id"), nullable=False)

    category = db.relationship("Category", back_populates="attributes")
    attribute = db.relationship("Attribute", back_populates="categories")

    __table_args__ = (
        db.UniqueConstraint("category_id", "attribute_id", name="uq_category_attribute"),
    )


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category = db.relationship("Category", back_populates="products")
    attributes = db.relationship(
        "ProductAttributeValue", back_populates="product", cascade="all, delete-orphan"
    )


class ProductAttributeValue(db.Model):
    __tablename__ = "product_attribute_values"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    attribute_id = db.Column(db.Integer, db.ForeignKey("attributes.id"), nullable=False)
    value = db.Column(db.Text)

    product = db.relationship("Product", back_populates="attributes")
    attribute = db.relationship("Attribute")

    __table_args__ = (
        db.UniqueConstraint("product_id", "attribute_id", name="uq_product_attr"),
    )

    @staticmethod
    def normalize_value(raw_value, data_type):
        if raw_value is None:
            return None
        if data_type in ("number",):
            try:
                return str(int(float(raw_value)))
            except Exception:
                return "0"
        if data_type in ("decimal",):
            try:
                return f"{float(raw_value):.2f}"
            except Exception:
                return "0.00"
        if data_type in ("boolean",):
            return "1" if str(raw_value).lower() in ("1", "true", "yes", "on") else "0"
        if data_type in ("date",):
            return str(raw_value)
        if data_type in ("multiselect",):
            if isinstance(raw_value, list):
                return ",".join([str(x) for x in raw_value if str(x).strip() != ""])
            else:
                return ",".join(
                    [s.strip() for s in str(raw_value).split(",") if s.strip() != ""]
                )
        return str(raw_value)
