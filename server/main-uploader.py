import base64
import logging
import uuid

import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
# import dash_table

from ramka.config import cfg
from ramka.mongo import is_valid_frame, add_image_to_frame
from ramka.session import SessionProfile
from ramka.util import get_warning, get_info, get_success


log = logging.getLogger(__name__)


app = dash.Dash(
    __name__,
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'],
    title='ZOOM.ME Uploader')


def get_layout():
    session_id = str(uuid.uuid1())

    return html.Div([
        dcc.Store(id='session-id', storage_type='session', data=session_id),
        html.Div([
            dcc.Input(
                id='frame-id',
                type='text',
                placeholder='Enter frame ID',
            ),
            dcc.Input(
                id='frame-password',
                type='password',
                placeholder='Enter frame password',
            ),
            html.Button('Add target frame', id='add-target-frame', n_clicks=0),
        ]),
        html.Div(id='frame-added-feedback'),
        html.Div(id='authorized-frames'),
        html.Hr(),
        dcc.Upload(
            id='add-new-image',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select an image')
            ]),
            style={
                'width': '50%',
                'height': '100px',
                'lineHeight': '100px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin-left': '25%',
                'margin-bottom': '10px'
            },
            # Allow multiple files to be uploaded
            # multiple=True
        ),
        # html.Div(id='uploaded-image'),
        html.Div(id='uploaded-image-block', children=[
            dbc.Row(
                html.Img(
                    id='uploaded-image',
                    style={'height': '200px'}
                )
            ),
            dbc.Row(
                dcc.Input(
                    id='image-description',
                    type='text',
                    placeholder='Enter a comment (optional)',
                )
            ),
        ]),
        html.Button('Upload', id='push-image-to-frames', n_clicks=0),
        html.Div(id='image-pushed-feedback'),
    ],
        style={
            'width': '50%',
            'textAlign': 'center',
            'margin-left': '25%'
        },
    )


app.layout = get_layout


@app.callback(
    Output('frame-added-feedback', 'children'),
    Output('frame-added-feedback', 'style'),
    Output('authorized-frames', 'children'),
    Output('frame-id', 'value'),
    Output('frame-password', 'value'),
    Input('add-target-frame', 'n_clicks'),
    State('frame-id', 'value'),
    State('frame-password', 'value'),
    State('session-id', 'data')
)
def update_target_frames(_, frame_id, frame_password, session_id):
    sp = SessionProfile(session_id)
    style = {}
    if frame_id is None or frame_password is None:
        feedback = '  '
    else:
        if frame_id in sp.get_target_frames():
            feedback = f'Frame {frame_id} already in the list'
        elif is_valid_frame(frame_id, frame_password):
            sp.add_target_frame(frame_id)
            feedback = f'Frame {frame_id} added successfully'
            frame_id, frame_password = '', ''
        else:
            feedback = f'Frame {frame_id} does not exist or the password is not valid'
            style = {'color': 'red'}
    frame_str = ', '.join([str(frame) for frame in sp.get_target_frames()]) or 'None'
    frames = 'IDs of approved frames: ' + frame_str
    # frames = dash_table.DataTable(
    #     data=[{'Approved frames': val} for val in sp.get_target_frames()],
    #     columns=[{'name': 'Approved frames', 'id': '1'}]
    # ),
    return feedback, style, frames, frame_id, frame_password


def add_new_image_to_session(contents, sp: SessionProfile):
    content_type, content_string = contents.split(',')

    if content_type.startswith('data:image'):
        decoded = base64.b64decode(content_string)
        sp.add_image(content_type, decoded)
        return get_info('')
    else:
        return get_warning('Incorrect file format')


@app.callback(
    Output('uploaded-image-block', 'style'),
    Output('uploaded-image', 'src'),
    Output('push-image-to-frames', 'style'),
    Output('image-description', 'value'),
    Output('image-pushed-feedback', 'children'),
    Output('image-pushed-feedback', 'style'),
    Input('add-new-image', 'contents'),
    Input('push-image-to-frames', 'n_clicks'),
    State('session-id', 'data'),
    State('image-description', 'value')
)
def update_uploaded_images(new_image, _, session_id, description):
    sp = SessionProfile(session_id)
    feedback = get_info('')

    ctx = dash.callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'add-new-image':
            feedback = add_new_image_to_session(new_image, sp)
        if trigger_id == 'push-image-to-frames':
            feedback = push_uploaded_image_to_frames(sp, description)
            description = ''

    image = sp.get_formatted_image()
    if image is not None:
        return (
            {'display': 'inline'},
            image,
            {'display': 'inline'},
            description,
            *feedback
        )
    else:
        return (
            {'display': 'none'},
            None,
            {'display': 'inline'},
            description,
            *feedback
        )


def push_uploaded_image_to_frames(sp: SessionProfile, description):
    frames = sp.get_target_frames()
    image = sp.get_image()
    if len(frames) == 0:
        return get_warning('No approved frames')
    elif image is None:
        return get_warning('No image to upload')
    else:
        log.info(f'Uploading image to {frames}')
        for frame_id in frames:
            add_image_to_frame(frame_id, image, 'PLC', description)
        sp.clear_image()
        return get_success('Image uploaded to the approved frames')


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=cfg.UPLOADER_PORT)
