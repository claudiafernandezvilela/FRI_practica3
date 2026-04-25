from robobopy.Robobo import Robobo
from behaviours.detect_tap import DetectTap
from behaviours.led_feedback import LedFeedback
from behaviours.explore import Explore
from behaviours.detect_object import DetectObject
from behaviours.find_container import FindContainer
from behaviours.push_to_zone import PushToZone
import cv2
from robobopy_videostream.RoboboVideo import RoboboVideo
import time
from robobopy.utils.LED import LED
from robobopy.utils.Color import Color

def main():
    robobo = Robobo("10.20.29.71")
    robobo.connect()
    robobo.wait(1)

    robobo.setStreamFps(20)
    robobo.startStream()
    robobo.wait(2)

    videoStream = RoboboVideo("10.20.29.71")
    videoStream.connect()
    robobo.wait(2)

    robobo.stopStream()
    robobo.wait(0.5)
    robobo.startCamera()
    robobo.wait(1)
    robobo.setStreamFps(20)
    robobo.startStream()
    robobo.wait(2)

    robobo.startObjectRecognition()
    robobo.wait(0.5)

    robobo.moveTiltTo(100, 60)
    robobo.wait(1)

    params = {
        "stop":             False,
        "detected_object":  None,
        "objeto_cerca":     False,
        "qr_centered":      False,
        "obj":              None,
        "depositados":      set(),
    }

    explore        = Explore(robobo, [], params)
    detect         = DetectObject(robobo, [explore], params)
    find_container = FindContainer(robobo, [explore, detect], params)
    push_to_zone   = PushToZone(robobo, [explore, detect, find_container], params)
    detect_tap    = DetectTap(robobo, [explore, detect, find_container, push_to_zone], params)
    led            = LedFeedback(robobo, [], params)  # sin supress_list, prioridad mínima

    threads = [explore, detect, find_container, push_to_zone, detect_tap, led]

    for t in threads:
        t.start()

    try:
        while not params["stop"]:
            try:
                frame = videoStream.getImage()
            except TypeError:
                time.sleep(0.1)
                continue

            if frame is None:
                time.sleep(0.1)
                continue

            cv2.imshow("Robobo Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                params["stop"] = True

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("=== Interrupción manual. Parando... ===")
        params["stop"] = True

    print("=== Misión completada. ===")

    for t in threads:
        t.join(timeout=2)

    robobo.stopMotors()
    robobo.stopObjectRecognition()
    robobo.stopStream()
    robobo.setLedColorTo(LED.All, Color.OFF)  # apagar LEDs al terminar
    cv2.destroyAllWindows()
    videoStream.disconnect()
    robobo.disconnect()

if __name__ == "__main__":
    main()