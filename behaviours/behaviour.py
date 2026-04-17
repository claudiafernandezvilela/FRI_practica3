#
# Clase base para todos los comportamientos de la arquitectura subsumida.
# Hereda de Thread para permitir ejecución paralela.
#

from threading import Thread
import time

class Behaviour(Thread):
    def __init__(self, robot, supress_list, params, **kwargs):
        super().__init__(**kwargs)
        self.robot = robot
        self.__supress = False
        self.supress_list = supress_list
        self.params = params
        self.daemon = True  # El hilo se cierra automáticamente al acabar el programa

    def take_control(self):
        pass

    def action(self):
        pass

    def run(self):
        while not self.params["stop"]:
            while not self.take_control() and not self.params["stop"]:
                time.sleep(0.01)
            if not self.params["stop"]:
                self.action()

    @property
    def supress(self):
        return self.__supress

    @supress.setter
    def supress(self, state):
        self.__supress = state

    def set_stop(self):
        self.params["stop"] = True

    def stopped(self):
        return self.params["stop"]