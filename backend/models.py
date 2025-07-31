from sqlalchemy import Table, Column, Integer, String
from db import metadata

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("token", String, index=True),
    Column("status", String),
)
