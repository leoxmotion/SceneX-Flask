import os

class GeneralConfig(object):
    SECRET_KEY="HNp9P4LmQa7CEcpB9Fr7sW5DERLFzXIbLkpFJj2rFNf-Aw"
    PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
    PAYSTACK_PUBLIC_KEY = os.environ.get("PAYSTACK_PUBLIC_KEY")
    
class LiveConfig(GeneralConfig):
    SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root@localhost/scenedb'
    SQLALCHEMY_TRACK_MODIFICATIONS=False