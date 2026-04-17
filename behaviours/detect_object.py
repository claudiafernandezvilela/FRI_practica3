#
# Comportamiento: Detectar Objeto (prioridad 2)
#

from .behaviour import Behaviour
from robobopy.utils.BlobColor import BlobColor
import time

# Tamaño mínimo del blob para considerarlo detectado
MIN_BLOB_SIZE = 2

# Colores que el robot debe detectar (objetos a clasificar)
OBJECT_COLORS = [BlobColor.RED, BlobColor.GREEN, BlobColor.BLUE]

class DetectObject(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def _get_detected_blob(self):
        for color in OBJECT_COLORS:
            blob = self.robot.readColorBlob(color)
            if blob is not None and blob.size > MIN_BLOB_SIZE:
                return color, blob
        return None, None

    def take_control(self):
        if self.supress:
            return False
        color, blob = self._get_detected_blob()
        return color is not None

    def action(self):
        print("----> control: Detectar Objeto")
        self.supress = False

        # Suprimir comportamientos de menor prioridad (Explorar)
        for bh in self.supress_list:
            bh.supress = True

        # Guardar el color detectado en params compartidos
        color, blob = self._get_detected_blob()
        if color is not None:
            params_key = _blob_color_to_str(color)
            self.params["objeto_detectado"] = True
            self.params["objeto_color"] = color
            self.params["objeto_color_str"] = params_key
            self.params["objeto_posx"] = blob.posx   # posición X del blob (0-100)
            print(f"      Objeto detectado: {params_key}, posX={blob.posx}")
        else:
            # Si ya no se ve el objeto, limpiar
            self.params["objeto_detectado"] = False
            self.params["objeto_color"] = None

        time.sleep(0.05)

        # Liberar supresión
        for bh in self.supress_list:
            bh.supress = False


def _blob_color_to_str(color):
    mapping = {
        BlobColor.RED:   "rojo",
        BlobColor.GREEN: "verde",
        BlobColor.BLUE:  "azul",
    }
    return mapping.get(color, "desconocido")