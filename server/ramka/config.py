import pydantic


class MainConfig(pydantic.BaseSettings):

    IMAGES_DIR: str
    SALT: bytes

    MONGODB_HOST: str = 'mongo'
    MONGODB_PORT: int = 27017
    MONGODB_DB: str = 'main'

    UPLOADER_PORT: int = 8050
    SERVER_PORT: int = 5000


cfg = MainConfig()
