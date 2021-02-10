import datetime as dt
from pathlib import Path

from fastapi.security import HTTPBasicCredentials, HTTPBasic
from fastapi import FastAPI, Depends, status, HTTPException, Response
import uvicorn

from ramka.config import cfg
from ramka.mongo import is_valid_frame, get_images_since, get_image_full_path


app = FastAPI()


def authorize(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    if not is_valid_frame(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password.',
            headers={'WWW-Authenticate': 'Basic'},
        )
    return credentials.username


@app.get('/image-ids')
def get_image_ids(since: dt.datetime, frame_id: str = Depends(authorize)):
    images = get_images_since(frame_id, since) or []
    return [{
        'id': Path(image['filepath']).name,
        'comment': image['description'],
        'sender': image['sender']
    } for image in images]


@app.get('/image/{image_id}')
def get_image(image_id: str, frame_id: str = Depends(authorize)):
    image_path = get_image_full_path(frame_id, image_id)
    return Response(content=Path(image_path).read_bytes())


if __name__ == '__main__':
    uvicorn.run('main-server:app', host='0.0.0.0', port=cfg.SERVER_PORT)
