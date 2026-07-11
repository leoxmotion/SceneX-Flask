import os

class GeneralConfig(object):
    SECRET_KEY = os.getenv("SECRET_KEY")
    PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
    PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY")
    
class LiveConfig(GeneralConfig):
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('MYSQLUSER')}:"
        f"{os.getenv('MYSQLPASSWORD')}@"
        f"{os.getenv('MYSQLHOST')}:"
        f"{os.getenv('MYSQLPORT')}/"
        f"{os.getenv('MYSQL_DATABASE')}"
)
    SQLALCHEMY_TRACK_MODIFICATIONS=False