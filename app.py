from flask import Flask, render_template, request, redirect, url_for, flash, jsonify


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    from models import db, Category, Attribute, CategoryAttribute, Product, ProductAttributeValue

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        stats = {
            "categories": Category.query.count(),
            "attributes": Attribute.query.count(),
            "products": Product.query.count(),
        }
        return render_template("index.html", stats=stats)

    # Categories
    @app.get("/categories")
    def list_categories():
        categories = Category.query.order_by(Category.name).all()
        return render_template("categories/list.html", categories=categories)

    @app.route("/categories/create", methods=["GET", "POST"])
    def create_category():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            is_active = request.form.get("is_active") == "on"

            if not name:
                flash("Category name is required", "danger")
                return redirect(url_for("create_category"))

            category = Category(name=name, description=description, is_active=is_active)
            db.session.add(category)
            db.session.commit()
            flash("Category created", "success")
            return redirect(url_for("list_categories"))

        return render_template("categories/form.html", category=None)

    @app.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
    def edit_category(category_id: int):
        category = Category.query.get_or_404(category_id)
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            is_active = request.form.get("is_active") == "on"

            if not name:
                flash("Category name is required", "danger")
                return redirect(url_for("edit_category", category_id=category_id))

            category.name = name
            category.description = description
            category.is_active = is_active
            db.session.commit()
            flash("Category updated", "success")
            return redirect(url_for("list_categories"))

        return render_template("categories/form.html", category=category)

    @app.post("/categories/<int:category_id>/delete")
    def delete_category(category_id: int):
        category = Category.query.get_or_404(category_id)
        if Product.query.filter_by(category_id=category.id).count() > 0:
            flash("Cannot delete category with products", "danger")
            return redirect(url_for("list_categories"))
        CategoryAttribute.query.filter_by(category_id=category.id).delete()
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted", "success")
        return redirect(url_for("list_categories"))

    # Attributes
    @app.get("/attributes")
    def list_attributes():
        attributes = Attribute.query.order_by(Attribute.name).all()
        return render_template("attributes/list.html", attributes=attributes)

    @app.route("/attributes/create", methods=["GET", "POST"])
    def create_attribute():
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            data_type = request.form.get("data_type", "text").strip()
            is_required = request.form.get("is_required") == "on"
            options = request.form.get("options", "").strip() or None

            if not name:
                flash("Attribute name is required", "danger")
                return redirect(url_for("create_attribute"))

            attr = Attribute(name=name, data_type=data_type, is_required=is_required, options=options)
            db.session.add(attr)
            db.session.commit()
            flash("Attribute created", "success")
            return redirect(url_for("list_attributes"))

        return render_template("attributes/form.html", attribute=None)

    @app.route("/attributes/<int:attribute_id>/edit", methods=["GET", "POST"])
    def edit_attribute(attribute_id: int):
        attribute = Attribute.query.get_or_404(attribute_id)
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            data_type = request.form.get("data_type", "text").strip()
            is_required = request.form.get("is_required") == "on"
            options = request.form.get("options", "").strip() or None

            if not name:
                flash("Attribute name is required", "danger")
                return redirect(url_for("edit_attribute", attribute_id=attribute_id))

            attribute.name = name
            attribute.data_type = data_type
            attribute.is_required = is_required
            attribute.options = options
            db.session.commit()
            flash("Attribute updated", "success")
            return redirect(url_for("list_attributes"))

        return render_template("attributes/form.html", attribute=attribute)

    @app.post("/attributes/<int:attribute_id>/delete")
    def delete_attribute(attribute_id: int):
        attribute = Attribute.query.get_or_404(attribute_id)
        CategoryAttribute.query.filter_by(attribute_id=attribute.id).delete()
        ProductAttributeValue.query.filter_by(attribute_id=attribute.id).delete()
        db.session.delete(attribute)
        db.session.commit()
        flash("Attribute deleted", "success")
        return redirect(url_for("list_attributes"))

    # Category-Attribute assignment
    @app.route("/categories/<int:category_id>/attributes", methods=["GET", "POST"])
    def manage_category_attributes(category_id: int):
        category = Category.query.get_or_404(category_id)
        all_attributes = Attribute.query.order_by(Attribute.name).all()
        if request.method == "POST":
            selected_ids = request.form.getlist("attribute_ids")
            selected_ids = {int(x) for x in selected_ids}

            existing_links = CategoryAttribute.query.filter_by(category_id=category.id).all()
            existing_ids = {link.attribute_id for link in existing_links}

            for link in existing_links:
                if link.attribute_id not in selected_ids:
                    db.session.delete(link)

            for attribute in all_attributes:
                if attribute.id in selected_ids and attribute.id not in existing_ids:
                    db.session.add(CategoryAttribute(category_id=category.id, attribute_id=attribute.id))

            db.session.commit()
            flash("Category attributes updated", "success")
            return redirect(url_for("list_categories"))

        assigned_ids = {a.attribute_id for a in CategoryAttribute.query.filter_by(category_id=category.id).all()}
        return render_template(
            "category_attributes/manage.html",
            category=category,
            all_attributes=all_attributes,
            assigned_ids=assigned_ids,
        )

    # Products
    @app.get("/products")
    def list_products():
        products = Product.query.order_by(Product.created_at.desc()).all()
        categories = {c.id: c for c in Category.query.all()}
        return render_template("products/list.html", products=products, categories=categories)

    @app.route("/products/create", methods=["GET", "POST"])
    def create_product():
        categories = Category.query.order_by(Category.name).all()
        if request.method == "POST":
            return _upsert_product()
        return render_template("products/form.html", product=None, categories=categories)

    @app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
    def edit_product(product_id: int):
        product = Product.query.get_or_404(product_id)
        categories = Category.query.order_by(Category.name).all()
        if request.method == "POST":
            return _upsert_product(product)

        values = ProductAttributeValue.query.filter_by(product_id=product.id).all()
        value_map = {v.attribute_id: v for v in values}
        return render_template(
            "products/form.html",
            product=product,
            categories=categories,
            value_map=value_map,
        )

    def _upsert_product(product=None):
        from models import db, Attribute, CategoryAttribute, ProductAttributeValue

        name = request.form.get("name", "").strip()
        sku = request.form.get("sku", "").strip()
        price = request.form.get("price", "0").strip()
        description = request.form.get("description", "").strip()
        category_id = int(request.form.get("category_id")) if request.form.get("category_id") else None

        if not name or not sku or category_id is None:
            flash("Name, SKU and Category are required", "danger")
            return redirect(request.referrer or url_for("list_products"))

        if product is None:
            product = Product(name=name, sku=sku, price=float(price or 0), description=description, category_id=category_id)
            db.session.add(product)
        else:
            product.name = name
            product.sku = sku
            product.price = float(price or 0)
            product.description = description
            product.category_id = category_id

        db.session.flush()

        assigned_attributes = CategoryAttribute.query.filter_by(category_id=category_id).all()
        assigned_attribute_ids = [a.attribute_id for a in assigned_attributes]
        attributes = Attribute.query.filter(Attribute.id.in_(assigned_attribute_ids)).all()

        existing_values = {v.attribute_id: v for v in ProductAttributeValue.query.filter_by(product_id=product.id).all()}

        for attr in attributes:
            form_key = f"attr_{attr.id}"
            raw_value = request.form.getlist(form_key) if attr.data_type == "multiselect" else request.form.get(form_key)
            if raw_value is None:
                continue

            value = ProductAttributeValue.normalize_value(raw_value, attr.data_type)
            pav = existing_values.get(attr.id)
            if pav is None:
                pav = ProductAttributeValue(product_id=product.id, attribute_id=attr.id, value=value)
                db.session.add(pav)
            else:
                pav.value = value

        for attr_id in list(existing_values.keys()):
            if attr_id not in assigned_attribute_ids:
                db.session.delete(existing_values[attr_id])

        db.session.commit()
        flash("Product saved", "success")
        return redirect(url_for("list_products"))

    @app.post("/products/<int:product_id>/delete")
    def delete_product(product_id: int):
        product = Product.query.get_or_404(product_id)
        ProductAttributeValue.query.filter_by(product_id=product.id).delete()
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted", "success")
        return redirect(url_for("list_products"))

    # API for dynamic attributes by category
    @app.get("/api/category/<int:category_id>/attributes")
    def api_category_attributes(category_id: int):
        from models import Attribute

        links = CategoryAttribute.query.filter_by(category_id=category_id).all()
        attribute_ids = [l.attribute_id for l in links]
        attrs = Attribute.query.filter(Attribute.id.in_(attribute_ids)).order_by(Attribute.name).all()
        data = [
            {
                "id": a.id,
                "name": a.name,
                "data_type": a.data_type,
                "is_required": a.is_required,
                "options": a.options,
            }
            for a in attrs
        ]
        return jsonify(data)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
