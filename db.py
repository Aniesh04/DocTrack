# from sqlalchemy import create_engine, Column, Integer, String, Float, Date
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# import pandas as pd
# import logging
# from sqlalchemy import text

# # Initialize logger
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)

# # Database setup (replace `sqlite:///data.db` with your database URI, e.g., for PostgreSQL)
# DATABASE_URL = "sqlite:///data.db"
# # DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
# engine = create_engine(DATABASE_URL)
# Base = declarative_base()
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Define a model for the database
# class DocumentRecord(Base):
#     __tablename__ = "document_records"

#     id = Column(Integer, primary_key=True, index=True)
#     document_name = Column(String, nullable=False)
#     expiration_date = Column(String, nullable=True)  # Store as string or ISO date
#     days_until_expiration = Column(Integer, nullable=True)
#     days_overdue = Column(Integer, nullable=True)
#     status = Column(String, nullable=False)

# # Create tables in the database
# Base.metadata.create_all(bind=engine)

# # Database helper functions
# class DatabaseHandler:
#     def __init__(self):
#         self.db = SessionLocal()

#     def insert_dataframe(self, df: pd.DataFrame):
#         """
#         Insert a Pandas DataFrame into the database.
#         """
#         try:
#             records = df.to_dict(orient="records")
#             for record in records:
#                 new_record = DocumentRecord(
#                     document_name=record.get("Document name", "NA"),
#                     expiration_date=record.get("Expiration/due date", "NA"),
#                     days_until_expiration=record.get("Days until expiration", None),
#                     days_overdue=record.get("Days overdue", None),
#                     status=record.get("Status", "NA"),
#                 )
#                 self.db.add(new_record)
#             self.db.commit()
#             logger.info("Data successfully inserted into the database.")
#             return {"success": "Data inserted successfully"}
#         except Exception as e:
#             self.db.rollback()
#             logger.error(f"Error inserting data into the database: {e}")
#             return {"error": str(e)}
#         finally:
#             self.db.close()

#     def get_all_records(self):
#         """
#         Retrieve all records from the database.
#         """
#         try:
#             records = self.db.query(DocumentRecord).all()
#             return [
#                 {
#                     "document_name": record.document_name,
#                     "expiration_date": record.expiration_date,
#                     "days_until_expiration": record.days_until_expiration,
#                     "days_overdue": record.days_overdue,
#                     "status": record.status,
#                 }
#                 for record in records
#             ]
#         except Exception as e:
#             logger.error(f"Error retrieving data from the database: {e}")
#             return {"error": str(e)}
#         finally:
#             self.db.close()
        
#     def update_records(self, df: pd.DataFrame):
#         """
#         Update the database records based on the modified DataFrame.
#         """
#         try:
#             records = df.to_dict(orient="records")
#             for record in records:
#                 db_record = (
#                     self.db.query(DocumentRecord)
#                     .filter(DocumentRecord.document_name == record.get("Document name"))
#                     .first()
#                 )
#                 if db_record:
#                     db_record.expiration_date = record.get("Expiration/due date", "NA")
#                     db_record.days_until_expiration = record.get(
#                         "Days until expiration", None
#                     )
#                     db_record.days_overdue = record.get("Days overdue", None)
#                     db_record.status = record.get("Status", "NA")

#             self.db.commit()
#             return {"success": "Records updated successfully"}
#         except Exception as e:
#             self.db.rollback()
#             logging.error(f"Error updating records in the database: {e}")
#             return {"error": str(e)}
#         finally:
#             self.db.close()
    
#     # def clear_all_records(self):
#     #     """
#     #     Clear all records from the database.
#     #     """
#     #     try:
#     #         self.db.query(DocumentRecord).delete()  # Deletes all rows in the table
#     #         self.db.commit()
#     #         logger.info("All records cleared from the database.")
#     #         return {"success": "All records cleared successfully"}
#     #     except Exception as e:
#     #         self.db.rollback()
#     #         logger.error(f"Error clearing records from the database: {e}")
#     #         return {"error": str(e)}
#     #     finally:
#     #         self.db.close()

#     def clear_all_records(self):
#         """
#         Clear all records from the database.
#         """
#         try:
#             # Use DELETE instead of TRUNCATE
#             self.db.execute(text("DELETE FROM document_records"))  # Replace with your actual table name
#             self.db.commit()
#             logger.info("All records cleared from the database.")
#             return {"success": "All records cleared successfully"}
#         except Exception as e:
#             self.db.rollback()
#             logger.error(f"Error clearing records from the database: {e}")
#             return {"error": str(e)}
#         finally:
#             self.db.close()

import sqlite3
import pandas as pd
import logging

# Initialize logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup (using sqlite3)
DATABASE_URL = "data.db"  # SQLite database file

# Database helper functions
class DatabaseHandler:
    def __init__(self):
        self.connection = sqlite3.connect(DATABASE_URL)
        self.cursor = self.connection.cursor()

    def insert_dataframe(self, df: pd.DataFrame):
        """
        Insert a Pandas DataFrame into the database.
        """
        try:
            # Creating the table if it doesn't exist
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_name TEXT NOT NULL,
                    expiration_date TEXT,
                    days_until_expiration INTEGER,
                    days_overdue INTEGER,
                    status TEXT NOT NULL
                )
            """)

            records = df.to_dict(orient="records")
            for record in records:
                self.cursor.execute("""
                    INSERT INTO document_records (document_name, expiration_date, days_until_expiration, days_overdue, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    record.get("Document name", "NA"),
                    record.get("Expiration/due date", "NA"),
                    record.get("Days until expiration", None),
                    record.get("Days overdue", None),
                    record.get("Status", "NA"),
                ))
            self.connection.commit()
            logger.info("Data successfully inserted into the database.")
            return {"success": "Data inserted successfully"}
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error inserting data into the database: {e}")
            return {"error": str(e)}

    def get_all_records(self):
        """
        Retrieve all records from the database.
        """
        try:
            self.cursor.execute("SELECT * FROM document_records")
            records = self.cursor.fetchall()
            return [
                {
                    "id": record[0],
                    "document_name": record[1],
                    "expiration_date": record[2],
                    "days_until_expiration": record[3],
                    "days_overdue": record[4],
                    "status": record[5],
                }
                for record in records
            ]
        except Exception as e:
            logger.error(f"Error retrieving data from the database: {e}")
            return {"error": str(e)}

    def update_records(self, df: pd.DataFrame):
        """
        Update the database records based on the modified DataFrame.
        """
        try:
            records = df.to_dict(orient="records")
            for record in records:
                self.cursor.execute("""
                    UPDATE document_records
                    SET expiration_date = ?, days_until_expiration = ?, days_overdue = ?, status = ?
                    WHERE document_name = ?
                """, (
                    record.get("Expiration/due date", "NA"),
                    record.get("Days until expiration", None),
                    record.get("Days overdue", None),
                    record.get("Status", "NA"),
                    record.get("Document name"),
                ))
            self.connection.commit()
            return {"success": "Records updated successfully"}
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error updating records in the database: {e}")
            return {"error": str(e)}

    def clear_all_records(self):
        """
        Clear all records from the database.
        """
        try:
            self.cursor.execute("DELETE FROM document_records")  # Deletes all rows in the table
            self.connection.commit()
            logger.info("All records cleared from the database.")
            return {"success": "All records cleared successfully"}
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Error clearing records from the database: {e}")
            return {"error": str(e)}

    def close_connection(self):
        """Close the database connection"""
        self.connection.close()

