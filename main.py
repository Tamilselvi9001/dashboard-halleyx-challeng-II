from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import engine, get_db, Base
from models import Order, DashboardWidget
import json, uuid
from datetime import datetime

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NexDash API")

# Allow all origins (frontend HTML files)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════
# PYDANTIC SCHEMAS
# ═══════════════════════════════════════

class OrderCreate(BaseModel):
    first_name:   str
    last_name:    str
    email:        str
    phone:        Optional[str] = ""
    street:       Optional[str] = ""
    city:         Optional[str] = ""
    state:        Optional[str] = ""
    postal_code:  Optional[str] = ""
    country:      Optional[str] = ""
    product:      str
    quantity:     int = 1
    unit_price:   float = 0
    total_amount: float = 0
    status:       str = "Pending"
    created_by:   Optional[str] = ""

class OrderUpdate(BaseModel):
    first_name:   Optional[str] = None
    last_name:    Optional[str] = None
    email:        Optional[str] = None
    phone:        Optional[str] = None
    street:       Optional[str] = None
    city:         Optional[str] = None
    state:        Optional[str] = None
    postal_code:  Optional[str] = None
    country:      Optional[str] = None
    product:      Optional[str] = None
    quantity:     Optional[int] = None
    unit_price:   Optional[float] = None
    total_amount: Optional[float] = None
    status:       Optional[str] = None
    created_by:   Optional[str] = None

class WidgetSave(BaseModel):
    id:          str
    type:        str
    wtype:       str
    title:       str = "Untitled"
    x:           float = 0
    y:           float = 0
    card_w:      float = 300
    configured:  bool = False
    config_json: dict = {}

class DashboardSave(BaseModel):
    widgets: List[WidgetSave]


# ═══════════════════════════════════════
# HELPER — convert Order DB row to dict
# ═══════════════════════════════════════
def order_to_dict(o: Order) -> dict:
    return {
        "id":           o.id,
        "customerId":   o.customer_id,
        "firstName":    o.first_name,
        "lastName":     o.last_name,
        "email":        o.email,
        "phone":        o.phone,
        "street":       o.street,
        "city":         o.city,
        "state":        o.state,
        "postalCode":   o.postal_code,
        "country":      o.country,
        "product":      o.product,
        "quantity":     o.quantity,
        "unitPrice":    o.unit_price,
        "totalAmount":  o.total_amount,
        "status":       o.status,
        "createdBy":    o.created_by,
        "createdAt":    str(o.created_at) if o.created_at else "",
    }

def widget_to_dict(w: DashboardWidget) -> dict:
    cfg = {}
    try: cfg = json.loads(w.config_json or "{}")
    except: pass
    return {
        "id":         w.id,
        "type":       w.type,
        "wtype":      w.wtype,
        "title":      w.title,
        "x":          w.x,
        "y":          w.y,
        "cardW":      w.card_w,
        "configured": w.configured,
        **cfg
    }


# ═══════════════════════════════════════
# ROOT
# ═══════════════════════════════════════
@app.get("/")
def root():
    return {"message": "NexDash API is running!"}


# ═══════════════════════════════════════
# ORDERS ENDPOINTS
# ═══════════════════════════════════════

@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    orders = db.query(Order).all()
    return [order_to_dict(o) for o in orders]


@app.post("/orders", status_code=201)
def create_order(data: OrderCreate, db: Session = Depends(get_db)):
    # Auto-generate IDs
    count    = db.query(Order).count()
    order_id = f"ORD-{str(count + 1).zfill(4)}"
    cust_id  = f"CUST-{str(count + 1).zfill(4)}"

    order = Order(
        id           = order_id,
        customer_id  = cust_id,
        first_name   = data.first_name,
        last_name    = data.last_name,
        email        = data.email,
        phone        = data.phone,
        street       = data.street,
        city         = data.city,
        state        = data.state,
        postal_code  = data.postal_code,
        country      = data.country,
        product      = data.product,
        quantity     = data.quantity,
        unit_price   = data.unit_price,
        total_amount = data.total_amount,
        status       = data.status,
        created_by   = data.created_by,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order_to_dict(order)


@app.put("/orders/{order_id}")
def update_order(order_id: str, data: OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for field, value in data.dict(exclude_none=True).items():
        # Convert camelCase field names to snake_case
        snake = {
            "first_name":   "first_name",
            "last_name":    "last_name",
            "email":        "email",
            "phone":        "phone",
            "street":       "street",
            "city":         "city",
            "state":        "state",
            "postal_code":  "postal_code",
            "country":      "country",
            "product":      "product",
            "quantity":     "quantity",
            "unit_price":   "unit_price",
            "total_amount": "total_amount",
            "status":       "status",
            "created_by":   "created_by",
        }
        if field in snake:
            setattr(order, snake[field], value)
    db.commit()
    db.refresh(order)
    return order_to_dict(order)


@app.delete("/orders/{order_id}")
def delete_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    db.delete(order)
    db.commit()
    return {"message": f"Order {order_id} deleted"}


# ═══════════════════════════════════════
# DASHBOARD WIDGET ENDPOINTS
# ═══════════════════════════════════════

@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    widgets = db.query(DashboardWidget).all()
    return {
        "configured": len(widgets) > 0,
        "widgets":    [widget_to_dict(w) for w in widgets]
    }


@app.post("/dashboard")
def save_dashboard(data: DashboardSave, db: Session = Depends(get_db)):
    # Delete all existing widgets and replace with new ones
    db.query(DashboardWidget).delete()
    for w in data.widgets:
        # Separate known fields from extra config
        known_keys = {"id","type","wtype","title","x","y","cardW","card_w","configured","config_json"}
        extra = {k: v for k, v in w.config_json.items()}
        widget = DashboardWidget(
            id          = w.id,
            type        = w.type,
            wtype       = w.wtype,
            title       = w.title,
            x           = w.x,
            y           = w.y,
            card_w      = w.card_w,
            configured  = w.configured,
            config_json = json.dumps(extra)
        )
        db.add(widget)
    db.commit()
    return {"message": "Dashboard saved", "count": len(data.widgets)}


@app.delete("/dashboard/{widget_id}")
def delete_widget(widget_id: str, db: Session = Depends(get_db)):
    widget = db.query(DashboardWidget).filter(DashboardWidget.id == widget_id).first()
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    db.delete(widget)
    db.commit()
    return {"message": f"Widget {widget_id} deleted"}


# ═══════════════════════════════════════
# RUN
# ═══════════════════════════════════════
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
