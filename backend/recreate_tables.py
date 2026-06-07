"""
Recreate database tables with correct enum constraints.
WARNING: This will delete all existing data!
"""
from app.core.database import engine, Base
from app.models.user import User, Account, Order, Position, OrderType, OrderStatus

def recreate_tables():
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)

    print("Creating tables with corrected enum mappings...")
    Base.metadata.create_all(bind=engine)

    print("Done! Tables recreated successfully.")

if __name__ == "__main__":
    recreate_tables()
