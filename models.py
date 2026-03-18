from sqlalchemy import Column, String, Float, Integer, Boolean, Text, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid

def gen_id():
    return str(uuid.uuid4())[:8].upper()

class Order(Base):
    __tablename__ = "orders"

    id            = Column(String, primary_key=True, default=lambda: f"ORD-{gen_id()}")
    customer_id   = Column(String, default=lambda: f"CUST-{gen_id()}")
    first_name    = Column(String, nullable=False)
    last_name     = Column(String, nullable=False)
    email         = Column(String, nullable=False)
    phone         = Column(String)
    street        = Column(String)
    city          = Column(String)
    state         = Column(String)
    postal_code   = Column(String)
    country       = Column(String)
    product       = Column(String, nullable=False)
    quantity      = Column(Integer, default=1)
    unit_price    = Column(Float, default=0)
    total_amount  = Column(Float, default=0)
    status        = Column(String, default="Pending")
    created_by    = Column(String)
    created_at    = Column(DateTime, server_default=func.now())


class DashboardWidget(Base):
    __tablename__ = "dashboard_widgets"

    id           = Column(String, primary_key=True)
    type         = Column(String)       # "Bar Chart", "KPI Value" etc.
    wtype        = Column(String)       # "bar-chart", "kpi" etc.
    title        = Column(String, default="Untitled")
    x            = Column(Float, default=0)
    y            = Column(Float, default=0)
    card_w       = Column(Float, default=300)
    configured   = Column(Boolean, default=False)
    config_json  = Column(Text, default="{}")  # stores all extra config as JSON
