from robobopy.Robobo import Robobo
from behaviours.explore import Explore
from behaviours.detect_object import DetectObject
import time

def main():
    robobo = Robobo("localhost")
    robobo.connect()
    robobo.wait(1)

    robobo.startObjectRecognition()
    robobo.wait(0.5)

    robobo.moveTiltTo(120, 60)
    robobo.wait(1)

    params = {
        "stop": False,
        "detected_object": None,
        "objeto_cerca": False,
    }

    explore = Explore(robobo, [], params)
    detect  = DetectObject(robobo, [explore], params)

    threads = [explore, detect]
    for t in threads:
        t.start()

    # Parar cuando el objeto esté cerca
    while not params["stop"]:
        if params.get("objeto_cerca"):
            print("=== Objeto alcanzado. ===")
            params["stop"] = True
        time.sleep(0.1)

    for t in threads:
        t.join(timeout=2)

    robobo.stopMotors()
    robobo.stopObjectRecognition()
    robobo.disconnect()

if __name__ == "__main__":
    main()