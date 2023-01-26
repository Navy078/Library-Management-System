from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher:

    @staticmethod 
    def get_hash(password):
        return pwd_cxt.hash(password)

    @staticmethod
    def verify_password(password, hashed_password):
        return pwd_cxt.verify(password, hashed_password)

