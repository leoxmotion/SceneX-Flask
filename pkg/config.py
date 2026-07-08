class GeneralConfig(object):
    SECRET_KEY="HNp9P4LmQa7CEcpB9Fr7sW5DERLFzXIbLkpFJj2rFNf-Aw"
    
class LiveConfig(GeneralConfig):
    SQLALCHEMY_DATABASE_URI='mysql+mysqlconnector://root@localhost/scenedb'
    SQLALCHEMY_TRACK_MODIFICATIONS=False