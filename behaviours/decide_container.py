from .behaviour import Behaviour
from robobopy.utils.BlobColor import BlobColor
import time

class DecideContainer(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)

    def take_control(self):
        if self.supress:
            return False

        objeto_detectado = self.params.get("objeto_detectado", False)
        contenedor_decidido = self.params.get("contenedor_decidido", False)

        return objeto_detectado and not contenedor_decidido

    def action(self):
        print("----> control: Decidir Contenedor")
        self.supress = False

        for bh in self.supress_list:
            bh.supress = True

        color_objeto = self.params.get("objeto_color")

        # DECISIÓN SIN DICCIONARIOS
        if color_objeto == BlobColor.RED:
            self.params["contenedor"] = "organico"
            self.params["contenedor_decidido"] = True
            print("      Es orgánico")
            self.robot.sayText("Orgánico")

        elif color_objeto == BlobColor.GREEN:
            self.params["contenedor"] = "papel"
            self.params["contenedor_decidido"] = True
            print("      Es papel")
            self.robot.sayText("Papel")

        elif color_objeto == BlobColor.BLUE:
            self.params["contenedor"] = "plastico"
            self.params["contenedor_decidido"] = True
            print("      Es plástico")
            self.robot.sayText("Plástico")

        else:
            self.params["contenedor_decidido"] = False
            print("      Color no reconocido")

        time.sleep(0.05)

        for bh in self.supress_list:
            bh.supress = False