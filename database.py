from sqlalchemy import create_engine,inspect,text
from sqlalchemy.orm import sessionmaker, declarative_base


DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/fastapi_db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()

def sync_database():
    from models import User,Hoteldata,Tokengen
    models = [User,Hoteldata,Tokengen]
    inspector = inspect(engine)
    print(inspector)
    with engine.begin() as conn:
        for model in models:
            table_name = model.__tablename__
            # Check whether table exists
            if not inspector.has_table(table_name):
                model.__table__.create(bind=engine)
                print(f"Created table: {table_name}")
                continue
            # Database columns
            db_columns = {
                column["name"]: column
                for column in inspector.get_columns(table_name)
            }
            # Model columns
            model_columns = {
                column.name: column
                for column in model.__table__.columns
            }
            # --------------------------------
            # 1. ADD NEW COLUMNS
            # --------------------------------
            for column_name, column in model_columns.items():
                if column_name not in db_columns:
                    column_type = column.type.compile(
                        engine.dialect
                    )
                    conn.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            f"ADD COLUMN {column_name} "
                            f"{column_type}"
                        )
                    )
                    print(
                        f"Added column: {column_name}"
                    )
            # --------------------------------
            # 2. DELETE REMOVED COLUMNS
            # --------------------------------
            for column_name in db_columns:
                if column_name not in model_columns:
                    conn.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            f"DROP COLUMN {column_name}"
                        )
                    )
                    print(
                        f"Deleted column: {column_name}"
                    )