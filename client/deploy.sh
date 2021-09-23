FRAME_DATA_DIR=/data/local
DAEMON=ramka-daemon.sh

cd $(dirname $0)

echo 'Uploading the daemon to your frame'
adb push "$DAEMON" "$FRAME_DATA_DIR"
echo 'Updating permissions'
adb shell "busybox chmod +x $FRAME_DATA_DIR/$DAEMON"

CMD="/system/bin/busybox sh $FRAME_DATA_DIR/$DAEMON > $FRAME_DATA_DIR/log.txt 2>&1"
IS_DEPLOYED=$(adb shell "cat /system/bin/preinstall.sh | grep '$CMD'")
if [ -z "$IS_DEPLOYED" ]; then
    echo 'Set up triggering at boot'
    adb shell 'mount -o remount,rw /system'
    adb shell "echo '$CMD' >> /system/bin/preinstall.sh"
    adb shell 'mount -o remount,ro /system'
else
    echo 'Boot trigger already set. Skipping'
fi
