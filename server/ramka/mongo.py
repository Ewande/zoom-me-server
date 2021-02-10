import datetime as dt
import logging
from pathlib import Path
import re

import bcrypt
from pymongo import MongoClient

from ramka.config import cfg


log = logging.getLogger(__name__)


def get_mongo_client():
    return MongoClient(
        host=cfg.MONGODB_HOST,
        port=cfg.MONGODB_PORT)[cfg.MONGODB_DB]


def is_valid_frame(frame_id: str, password: str):
    password_hash = bcrypt.hashpw(password.encode(), cfg.SALT)
    return get_mongo_client()['frames'].find_one({
        '_id': frame_id,
        'password': password_hash
    }) is not None


def add_image_to_frame(frame_id: str, image: dict, sender: str, description: str):
    log.info(f'Adding to frame {frame_id}')
    upload_timestamp = dt.datetime.utcnow()
    ext = re.search(r'\/(\w+);', image['type']).group(1)
    ext = 'jpg' if ext == 'jpeg' else ext
    filepath = Path(cfg.IMAGES_DIR, frame_id)
    filepath.mkdir(parents=True, exist_ok=True)
    filepath /= f'{upload_timestamp:%Y-%m-%d_%H.%M.%S}.{ext}'
    log.info(f'Uploading file to {filepath}')
    filepath.write_bytes(image['content'])
    log.info(f'Saving to database')
    get_mongo_client()['frames'].update(
        {'_id': frame_id},
        {'$push': {
            'images': {
                'filepath': str(filepath),
                'sender': sender,
                'description': description,
                'timestamp': dt.datetime.utcnow().isoformat(timespec='seconds')
            }
        }}
    )


def get_images_since(frame_id: str, since: dt.datetime):
    return list(get_mongo_client()['frames'].aggregate([
        {'$match': {'_id': frame_id}},
        {'$project': {
            'images': {'$filter': {
                'input': '$images',
                'as': 'item',
                'cond': {'$gt': ['$$item.timestamp', since.isoformat()]}
            }}
        }}
    ]))[0]['images']


def get_image_full_path(frame_id: str, filename: str):
    return get_mongo_client()['frames'].find_one({
        '_id': frame_id,
        'images': {'$elemMatch': {
            'filepath': {'$regex': filename}
        }}
    }, {'images.$': 1})['images'][0]['filepath']
