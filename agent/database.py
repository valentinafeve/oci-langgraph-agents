import oracledb
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def __init__():
    pass

class DatabaseClient:
    def __init__(self):
        self.connection=oracledb.connect(
            config_dir=os.environ["DB_WALLET_LOCATION"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            dsn=os.environ["DB_DSN"],
            wallet_location=os.environ["DB_WALLET_LOCATION"],
            wallet_password=os.environ["DB_WALLET_PASSWORD"])

    def check_connection(self):
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM dual")
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            logger.exception(f"Error checking connection e:{e}")
            return False

    def execute_query(self, sql, params=None):
        try:
            conn = self.connection
            cursor = conn.cursor()
            cursor.execute(sql, params or {})
            
            if cursor.description is None:            
                conn.commit()
                return {"status": "success", "rows": 0}
            
            columns = [col[0].lower() for col in cursor.description]
            rows = [
                {
                    col: val.read() if isinstance(val, oracledb.LOB) else val
                    for col, val in zip(columns, row)
                } for row in cursor.fetchall()
            ]
            return rows
        except Exception as e:
            logger.exception(f"Error running query e:{e}")
            raise
