from database.connection import Base, engine
import models

def create_tables():
    print("Creating MediAssist AI database tables...")

    Base.metadata.create_all(bind=engine)

    print("Database tables created successfully!")

    print("\nTables available:")
    for table_name in Base.metadata.tables:
        print(f"- {table_name}")


if __name__ == "__main__":
    create_tables()