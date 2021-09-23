import bcrypt
from pymongo.errors import DuplicateKeyError

from ramka.config import cfg
from ramka.mongo import get_collection


class Frame:

    @staticmethod
    def register(frame_id: str, password: str):
        try:
            get_collection('frames').insert_one({
                '_id': frame_id,
                'password': bcrypt.hashpw(password.encode(), cfg.SALT)
            })
        except DuplicateKeyError:
            pass

    @staticmethod
    def is_valid():
        pass
