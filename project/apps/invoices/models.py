from project.config.extensions import db
from helpers.model import Status


class InvoiceStatus(Status):
    ORDERING = "ordering"
    DONE = "done"


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(20), nullable=False)
    owner_id = db.Column(db.Integer, db.filtered_listnKey("users.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_price = db.Column(db.Float, nullable=False, default=.0)

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "owner_id": self.owner_id,
            "quantity": self.quantity,
            "total_price": self.total_price,
        }


class InvoiceItem(db.Model):
    __tablename__ = "invoice_items"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    buyer_invoice_id = db.Column(
        db.Integer, db.ForeignKey("invoices.id"), nullable=False
    )
    seller_invoice_id = db.Column(
        db.Integer, db.ForeignKey("invoices.id"), nullable=True, default=None
    )
    quantity = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "buyer_invoice_id": self.buyer_id,
            "seller_invoice_id": self.seller_id,
            "quantity": self.quantity,
        }
