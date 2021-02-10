import base64
import datetime as dt
import logging

from pymongo.errors import DuplicateKeyError

from ramka.mongo import get_mongo_client


log = logging.getLogger(__name__)


class SessionProfile:
    def __init__(self, session_id: str):
        self.session_id = session_id
        try:
            self._start_new_session()
            log.info(f'Starting new sessions {session_id}')
        except DuplicateKeyError:
            log.info(f'Resuming session {session_id}')

    def _start_new_session(self):
        timestamp = dt.datetime.utcnow()
        get_mongo_client()['sessions'].insert({
            '_id': self.session_id,
            'timestamp': timestamp
        })

    def _get_session(self):
        return get_mongo_client()['sessions'].find_one({'_id': self.session_id})

    def get_target_frames(self):
        return self._get_session().get('frames', [])

    def get_image(self):
        return self._get_session().get('image')

    def get_formatted_image(self):
        image = self.get_image()
        if image is not None:
            return _to_img_src(image)

    def clear_image(self):
        get_mongo_client()['sessions'].update(
            {'_id': self.session_id},
            {'$unset': {'image': None}}
        )

    def add_target_frame(self, frame_id: int):
        get_mongo_client()['sessions'].update(
            {'_id': self.session_id},
            {'$push': {'frames': frame_id}}
        )

    def add_image(self, image_type: str, image: bytes):
        get_mongo_client()['sessions'].update(
            {'_id': self.session_id},
            {'$set': {
                'image': {
                    'type': image_type,
                    'content': image
                }
            }}
        )

    def add_image_description(self, description: str):
        get_mongo_client()['sessions'].update(
            {'_id': self.session_id},
            {'$set': {
                'image': {
                    'description': description
                }
            }}
        )


def _to_img_src(image):
    return f'{image["type"]},{base64.b64encode(image["content"]).decode("ascii")}'
