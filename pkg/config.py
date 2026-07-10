import os

class GeneralConfig(object):
    SECRET_KEY="HNp9P4LmQa7CEcpB9Fr7sW5DERLFzXIbLkpFJj2rFNf-Aw"
    PAYSTACK_SECRET_KEY = os.environ.get("sk_test_937d94b9d037534a0187b6a3134bb3bf8190da2e")
    PAYSTACK_PUBLIC_KEY = os.environ.get("pk_test_6763004f5dabc995b404b1bdff4085d970e0ae91")
    
class LiveConfig(GeneralConfig):
    SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root@localhost/scenedb'
    SQLALCHEMY_TRACK_MODIFICATIONS=False