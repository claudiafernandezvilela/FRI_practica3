#
# Comportamiento 2: DetectObject (prioridad 2)
#

from .behaviour import Behaviour
from robobopy.utils.IR import IR

MIN_CONFIDENCE = 0.5
IMAGE_CENTER_X = 160   # Centro horizontal de la imagen (320px / 2)
IR_GOAL        = 20    # Umbral para pasar a approach final
IR_CONTACT     = 100    # Umbral de contacto real con el objeto

# Parámetros PD
KP = 0.02
KD = 0.05

# Velocidad base de avance
BASE_SPEED = 10

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

class DetectObject(Behaviour):

    def __init__(self, robot, supress_list, params):
        super().__init__(robot, supress_list, params)
        self.last_error = 0

    def _read_object(self):
        obj = self.robot.readDetectedObject()
        if obj is not None and obj.label is not None and obj.confidence >= MIN_CONFIDENCE:
            return obj
        return None

    def _approach_final(self):
        """Avanza despacio hasta contacto real con el objeto."""
        print("      Modo approach final...")
        while not self.stopped():
            ir_front_c = self.robot.readIRSensor(IR.FrontC)
            ir_front_l = self.robot.readIRSensor(IR.FrontL)
            ir_front_r = self.robot.readIRSensor(IR.FrontR)
            ir_value = max(ir_front_c or 0, ir_front_l or 0, ir_front_r or 0)

            print(f"      approach_final IR={ir_value}")

            if ir_value >= IR_CONTACT:
                self.robot.stopMotors()
                self.params["objeto_cerca"] = True
                self.params["detected_object"] = self.params["obj"]
                print(f"      Contacto con objeto (IR={ir_value})")
                break

            self.robot.moveWheels(5, 5)
            self.robot.wait(0.1)

    def take_control(self):
        if self.supress:
            return False
        if self.params.get("objeto_cerca"):
            return False
        obj = self._read_object()
        if obj is None:
            return False
        self.params["obj"] = obj
        return True

    def action(self):
        # Guardia: si ya estamos cerca al entrar, no hacer nada
        if self.params.get("objeto_cerca"):
            return

        print(f"----> control: DetectObject ({self.params['obj'].label})")
        self.supress = False
        self.last_error = 0

        for bh in self.supress_list:
            bh.supress = True

        while not self.stopped():

            obj = self._read_object()

            # Si pierde el objeto, ceder control a Explore
            if obj is None:
                print("      Objeto perdido, cediendo control.")
                self.robot.stopMotors()
                break

            self.params["obj"] = obj
            ir_central = self.robot.readIRSensor(IR.FrontC)

            # Fase 2: ya está cerca, approach final
            if ir_central is not None and ir_central >= IR_GOAL:
                self.robot.stopMotors()
                self._approach_final()
                break

            # Fase 1: control PD para centrarse y avanzar

            # Detección dudosa con x=0: girar buscando el objeto
            if obj.x == 0:
                self.robot.moveWheels(BASE_SPEED, -BASE_SPEED)
                self.robot.wait(0.1)
                continue

            error      = IMAGE_CENTER_X - obj.x
            derivative = error - self.last_error
            correction = clamp((error * KP) + (derivative * KD), -BASE_SPEED, BASE_SPEED)
            self.last_error = error

            left_speed  = clamp(BASE_SPEED + correction, -BASE_SPEED, BASE_SPEED)
            right_speed = clamp(BASE_SPEED - correction, -BASE_SPEED, BASE_SPEED)

            print(f"      '{obj.label}' x={obj.x} IR={ir_central} "
                  f"err={error:.1f} corr={correction:.2f} "
                  f"L={left_speed:.1f} R={right_speed:.1f}")

            self.robot.moveWheels(int(right_speed), int(left_speed))
            self.robot.wait(0.1)

        for bh in self.supress_list:
            bh.supress = False