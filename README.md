# Goclever ZOOM.ME - custom toolkit

This custom toolkit includes:
- a simple FastAPI-based server to upload new photos and serve them to frames on demand
- a daemon that needs to be uploaded to your digital frame via USB

## Running the server
### Requirements
- docker
- docker-compose
### How to
1. Based on [config/.env.template](config/.env.template), create `.env.dev` file inside the `config` directory
   and set the required environment variables
2. From the main repo directory start the server with `make dev-up`. This will spin up 3 docker containers:
   - the uploader (web UI to upload photos)
   - the server (to pull photos from your frames)
   - a Mongo database to store the uploaded photos 
3. Register your frame on the server with
   - `SERVER_IP` - `localhost` if running locally, otherwise your external server IP
   - `SERVER_PORT` - 8000 by default
   - `FRAME_ID` - this should be the same ID as used in the original ZOOM.ME setup
   ```
   curl -X PUT '<SERVER_IP>:<SERVER_PORT>/frames?frame_id=<FRAME_ID>&password=<PASSWORD_OF_YOUR_CHOICE>'
   ```
4. Open `SERVER_IP` (or `localhost`) in your web browser to upload photos.
   Make sure your photos are not too big, there seems to be some size limits on the frame side.

## Connecting your frame to the server
### Requirements
- [Android Debug Bridge (adb) client](https://developer.android.com/studio/releases/platform-tools#downloads)
### How to
1. Connect your frame via USB (to reveal the USB port, press the back of your frame)
2. Edit [client/ramka-daemon.sh](client/ramka-daemon.sh), you need to hardcode these values in the file:
   - `SERVER_IP` - external server IP
   - `SERVER_PORT` - 8000 by default
   - `PASSWORD` - this should match the password you used to register your frame on the server
2. Run [deploy.sh](client/deploy.sh)