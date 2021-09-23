#!/system/bin/busybox sh

alias busybox=/system/bin/busybox

ZOOM_ID=$(cat /mnt/private/imei.txt | busybox tail -c -7)

SERVER_IP=<SERVER_IP>
SERVER_PORT=<SERVER_PORT>
PASSWORD=<PASSWORD>

LAST_TIMESTAMP_FILE=/data/local/last-timestamp

IMAGE_MAIN_DIR=/sdcard/DCIM/ZOOM.ME

while sleep 5; do
  TIMESTAMP=$(busybox date -u -Iseconds)
  sleep 1
  if test -f "$LAST_TIMESTAMP_FILE"; then
    LAST_TIMESTAMP=$(cat $LAST_TIMESTAMP_FILE)
  else
    LAST_TIMESTAMP='2000-01-01T00:00:00UTC'
  fi
  LAST_TIMESTAMP="${LAST_TIMESTAMP%UTC}"  # strip UTC
  #echo "LT=$LAST_TIMESTAMP"
  busybox wget -q -T 2 -O images.json "http://$ZOOM_ID:$PASSWORD@$SERVER_IP:$SERVER_PORT/image-ids?since=$LAST_TIMESTAMP"
  SERVER_OK="$?"
  RAW_TRANS=$(cat images.json | busybox sed -e 's/},{/\\\n/g' -e '$a\')
  echo "$RAW_TRANS" > images.json
  while IFS= read -r line <&3; do
      if [ "$line" = "[]" ]; then
          break
      fi
      ID=$(echo "$line" | grep -o '"id":"[^"]*' | busybox cut -d'"' -f4)
      COMMENT=$(echo "$line" | grep -o '"comment":"[^"]*' | busybox cut -d'"' -f4)
      SENDER=$(echo "$line" | grep -o '"sender":"[^"]*' | busybox cut -d'"' -f4)
      #echo "ID=$ID,COMMENT=$COMMENT,SENDER=$SENDER"
      if ! test -f "$IMAGE_MAIN_DIR/$ID"; then
          busybox wget -q -T 2 -P "$IMAGE_MAIN_DIR" "http://$ZOOM_ID:$PASSWORD@$SERVER_IP:$SERVER_PORT/image/$ID"
          SERVER_OK="$?"
      fi
  done 3< images.json
  if [ "$SERVER_OK" -eq 0 ]; then
      echo $TIMESTAMP > $LAST_TIMESTAMP_FILE
  fi
done
