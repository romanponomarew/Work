import pygame
import simpy
from new_example3 import (PyGameEnvironment, FrameRenderer)
import time
import itertools
import random

def dim_color(color, percent):
    h, s, v, a = color.hsva
    result = pygame.Color(color.r, color.g, color.b, color.a)
    result.hsva = (h, s, v * percent, a)
    return result


BLACK = pygame.Color(0, 0, 0)
BLUE = pygame.Color(0, 0, 255)
RED = pygame.Color(255, 0, 0)
GREEN = pygame.Color(0, 255, 0)
YELLOW = pygame.Color(255, 255, 0)

T_INTER = [3000, 7000]            # Прибытие самолета каждые [min, max] секунд




class Airplane(object):
    """Описание методов самолета:
    1)перемещение на стоянку
    2)перемещение со стоянки на станцию тех.обслуживания
    3)перемещение со станции тех.обслуживания на взлетную полосу и вылет с аэропорта"""

    to_station1 = 0  # Отправился ли кто-то от парковки к стацнии тех.обслуживания1(=1 только пока в пути)
    to_station2 = 0  # Отправился ли кто-то от парковки к стацнии тех.обслуживания2(=1 только пока в пути)

    def __init__(self, env, name):
        IMG_size = 60
        self.image = pygame.image.load("airplane4.png")  # Загрузка в pygame картинки
        self.image = pygame.transform.scale(self.image, (IMG_size, IMG_size))  # Изменение размера картинки

        self.x = 0  # Изначальное положение центра картинки
        self.y = 0
        # self.image1 = self.image.get_rect(center =(self.x, self.y))
        self.env = env
        self.status_now = "" # "on_parking", "on_service_station", "moving" "stoyanka_to_station1" "stoyanka_to_station2"
        self.status = "arrived_on_airport"  # "on_parking", "on_service_station", "moving"
        self.name = name

        self.time_parking = 0  # Время прибытия на стоянку
        self.time_station = 0   # Время прибытия на станцию на ремонт
        self.time_leave = 0  # Самолет готов, покидает аэропорт
        #self.time_start = 0  # Начало отсчета времени пребывания самолтеа в аэропорту
        #self.time_end = 0   # Конец времени пребывания самолтеа в аэропорту
        self.time_result = 0  # Итоговое время пребывания самолета в аэропорту
        self.monitoring = ""  # Текущее событие самолета
        self.time_now = 0  # Время текущего события

        #self.image1 = self.image.get_rect()


    ###############################
    def arriving(self):
        """Прибытие самолета в аэропорт и перемещение на стоянку"""
        current_x_stoyanka = SCREEN_HEIGHT - 80  # Текущая координата Y для стоянки
        global stoyanka_counts
        global event, event_time
        # Движение по вертикали(Конечная координата зависит от того, сколько самолетов уже на стоянке):
        self.y += 5
        #self.bottom_y = self.y + IMG_size / 2
        if self.y >= current_x_stoyanka - 60 * stoyanka_counts:
            self.y = current_x_stoyanka - 60*stoyanka_counts
            # Движение по горизонтиали:
            self.x += 10
            # Удержание игрока в рамках окна
            if self.x > 56:
                self.x = 56
                self.status = "on_parking"
        # Увеличиваем количество самолетов на стоянке
        if self.status == "on_parking":
            stoyanka_counts = stoyanka_counts + 1
            self.time_parking = round(env.now/1000)
            self.monitoring = "Самолет1 на парковке"
            self.time_now = round(env.now/1000)
            event = f"Самолет{self.name} на парковке"
            event_time = round(env.now/1000)


    def go_to_service(self):
        """Перемещение самолета от стоянки на СВОБОДНУЮ станцию обслуживания"""
        # self.status = "moving"
        # self.status_prev = "on_parking"
        global stoyanka_counts
        #global service_airplanes1, service_airplanes2

        # Движение по горизонтиали:
        self.x += 3
        if self.x > 150 and self.x < 154:
            self.x = 150

        # Движение по вертикали(до станции обслуживания №1):
        self.y -= 10
        if self.y <= 280:
            self.y = 280
        #############################
        # # Движение по вертикали(до станции обслуживания №2):
        # self.y = self.y - 10
        # if self.y <= 465:
        #     self.y = 465
        ###############################

            # Движение по горизонтиали:
            if self.x == 150:
                self.x = self.x + 5
            if self.x >= 285:
                self.x = 285
                self.status = "on_service_station"
            # Увеличиваем количество самолетов на стоянке
            if self.status == "on_service_station":
                stoyanka_counts = stoyanka_counts - 1

    def go_to_service1(self):
        """Перемещение самолета от стоянки на СВОБОДНУЮ станцию обслуживания"""
        global stoyanka_counts
        global station1_status
        global stoyanka_to_station1
        global station1_repair
        global details_required1
        global event_time, event

        stoyanka_to_station1 = 1
        # Движение по горизонтиали:
        self.x += 3
        if self.x > 150 and self.x < 154:
            self.x = 150

        # Движение по вертикали(до станции обслуживания №1):
        self.y -= 10
        if self.y <= 280:
            self.y = 280
            # Движение по горизонтиали:
            if self.x == 150:
                self.x = self.x + 5
            if self.x >= 285:
                self.x = 285
                self.status = "on_service_station"

            # Увеличиваем количество самолетов на стоянке
            if self.status == "on_service_station":
                station1_status = 1
                stoyanka_to_station1 = 0
                self.status_now = "on_station1"
                Airplane.to_station1 = 0
                station1_repair = "repair"
                details_required1 = random.randint(10, 30)
                self.time_station = round(env.now/1000)
                self.monitoring = "Самолет1 на ремонте(1)"
                self.time_now = round(env.now / 1000)
                event = f"Самолет{self.name} на ремонте(1)"
                event_time = round(env.now / 1000)

    def go_to_service2(self):
        """Перемещение самолета от стоянки на СВОБОДНУЮ станцию обслуживания"""
        # self.status = "moving"
        # self.status_prev = "on_parking"
        global stoyanka_counts
        #global service_airplanes1, service_airplanes2
        global station2_status
        global stoyanka_to_station2
        global station2_repair
        global details_required2
        global event_time, event

        stoyanka_to_station2 = 1
        # Движение по горизонтиали:
        self.x += 3
        if self.x > 150 and self.x < 154:
            self.x = 150
        #############################
        # Движение по вертикали(до станции обслуживания №2):
        self.y = self.y - 10
        if self.y <= 465:
            self.y = 465
        ###############################
            # Движение по горизонтиали:
            if self.x == 150:
                self.x = self.x + 5
            if self.x >= 285:
                self.x = 285
                self.status = "on_service_station"


            # Увеличиваем количество самолетов на стоянке
            if self.status == "on_service_station":
                station2_status = 1
                stoyanka_to_station2 = 0  # Есть ли какой-нибудь самолет между стоянкой и станцией 2
                self.status_now = "on_station2"
                Airplane.to_station2 = 0
                station2_repair = "repair"
                details_required2 = random.randint(10, 30)
                self.time_station = round(env.now / 1000)
                self.monitoring = "Самолет1 на ремонте(2)"
                self.time_now = round(env.now / 1000)
                event = f"Самолет{self.name} на ремонте(2)"
                event_time = round(env.now / 1000)

    def leaving_airport(self):
        """Самолеты покидают аэропорт со станций обслуживания"""
        # Движение по горизонтиали:
        self.x += 2
        if self.x > 440 and self.y != 600: #and self.x < 154:
            self.x = 440
            # Движение по вертикали(до станции обслуживания №1):
            self.y += 3
            if self.y > 600:
                self.y = 600
        if self.x == 440 and self.y == 600:
            self.x += 3


    def run(self):
        global stoyanka_counts
        global station1_status
        global station2_status
        global details_required1, details_required2
        global event_time, event

        i = 1
        while True:
            # Прибытие самолета в аэропорт:
            if self.status == "arrived_on_airport":
                self.arriving()
            # Перемещение самолета со стоянки на станцию тех.обслуживания1:
            if self.status == "on_parking" and station1_status == 0 and Airplane.to_station1 == 0:
                if self.status_now != "to_station2":
                    self.status_now = "to_station1"
                    Airplane.to_station1 = 1
                if stoyanka_counts != 0:
                    stoyanka_counts -= 1
            # Перемещение самолета со стоянки на станцию тех.обслуживания2:
            if self.status == "on_parking" and station2_status == 0 and Airplane.to_station2 == 0:
                if self.status_now != "to_station1":
                    self.status_now = "to_station2"
                    Airplane.to_station2 = 1
                if stoyanka_counts != 0:
                    stoyanka_counts -= 1
            if self.status == "on_parking" and station1_status == 0 and Airplane.to_station1 == 1 and self.status_now == "to_station1":
                yield self.env.timeout(100)
                self.go_to_service1()
            if self.status == "on_parking" and station2_status == 0 and Airplane.to_station2 == 1 and self.status_now == "to_station2":
                yield self.env.timeout(100)
                self.go_to_service2()

            ##После ремонта(станция тех.обслуживания) самолет покидает аэропорт:
            if self.status == "on_service_station":
                if self.status_now == "on_station1" and station1_repair == "ready":
                    self.status_now = "from_station1"
                    station1_status = 0
                    details_required1 = 0

                if self.status_now == "on_station2" and station2_repair == "ready":
                    self.status_now = "from_station2"
                    station2_status = 0
                    details_required2 = 0

                if self.status == "on_service_station" and self.status_now == "from_station1":
                    self.leaving_airport()
                    if i < 2:
                        self.time_leave = round(env.now/1000)
                        i = 2
                        self.monitoring = "Самолет1 улетает"
                        self.time_now = round(env.now / 1000)
                        self.time_result = self.time_leave - self.time_parking
                        print(f"Общее время нахождения самолета{self.name} в аэропорту ={self.time_result}")
                        event = f"Самолет{self.name} улетает"
                        event_time = round(env.now / 1000)

                if self.status == "on_service_station" and self.status_now == "from_station2":
                    self.leaving_airport()
                    if i < 2:
                        self.time_leave = round(env.now/1000)
                        i = 2
                        self.monitoring = "Самолет1 улетает"
                        self.time_now = str(round(env.now / 1000))
                        self.time_result = self.time_leave - self.time_parking
                        print(f"Общее время нахождения самолета{self.name} в аэропорту ={self.time_result}")
                        event = f"Самолет{self.name} улетает"
                        event_time = round(env.now / 1000)

            yield self.env.timeout(20)

    def __call__(self, screen):
        # screen.blit(self.image, (self.x, self.y))  # Расположить картинку по координатам
        self.image1 = self.image.get_rect(topleft=(self.x, self.y))
        screen.blit(self.image, self.image1)



class Loader(object):
    """Экземпляр - команда грузчиков"""
    to_station1 = 0  # Отправился ли кто-то от склада к станции тех.обслуживания1(=1 только пока в пути)
    to_station2 = 0  # Отправился ли кто-то от склада к станции тех.обслуживания2(=1 только пока в пути)
    def __init__(self, env):
        self.IMG_size = 45
        self.image = pygame.image.load("loader.png")  # Загрузка в pygame картинки
        self.image = pygame.transform.scale(self.image, (self.IMG_size, self.IMG_size))  # Изменение размера картинки
        self.x = 650  # Изначальное положение центра картинки(На складе)
        self.y = 380
        # self.x = 400  # На станции 2
        # self.y = 410
        # self.x = 400  # На станции 1
        # self.y = 230
        self.env = env
        self.status_now = ""  # "on_parking", "on_service_station", "moving"
        self.status = "in_warehouse"  #"on_service_station", "moving"
        self.repair_time = random.randint(1200, 2000)
        self.warehose_status = "empty"  # "empty", "full"
        self.loader_details = 0  # Запчасти которые несет с собой грузчик от склада к станции


    def to_service_station1(self):
        global env
        global service_loaders1
        global station1_repair
        global repairing_1
        global WAREHOSE_STATION_SIZE2
        """Перемещение грузчиков от склада к станции тех.обслуживания №1"""
        self.x -= 3
        if self.x < 450 and self.y != 410 and self.y != 230:
            self.x = 450

            """К станции тех.обслуживания №1:"""
            self.y -= 2
            # self.x -= 2
            if self.y < 230:
                self.y = 230

        if self.y == 230 or self.y == 410:
            self.x -= 2
            if self.x < 400:
                self.x = 400
                self.status = "on_service_station1"
                self.image = pygame.image.load("loader_empty1.png")  # Загрузка в pygame картинки
                self.image = pygame.transform.scale(self.image,
                                                    (self.IMG_size, self.IMG_size))  # Изменение размера картинки
                service_loaders1 = 1
                Loader.to_station1 = 0
                repairing_1 = "now"
                #self.loader_details = 0
        yield self.env.timeout(10)  ###### Для того чтобы можно было вызвать как генератор


    def to_service_station2(self):
        global service_loaders2
        global station2_repair
        global repairing_2
        """Перемещение грузчиков от склада к станции тех.обслуживания №1"""
        self.x -= 3
        if self.x < 450 and self.y != 410 and self.y != 230:
            self.x = 450
            """К станции тех.обслуживания №2:"""
            self.y += 2
            if self.y > 410:
                self.y = 410

        if self.y == 230 or self.y == 410:
            self.x -= 2
            if self.x < 400:
                self.x = 400
                self.status = "on_service_station2"
                self.image = pygame.image.load("loader_empty1.png")  # Загрузка в pygame картинки
                self.image = pygame.transform.scale(self.image,
                                                    (self.IMG_size, self.IMG_size))  # Изменение размера картинки
                service_loaders2 = 1
                Loader.to_station2 = 0
                repairing_2 = "now"
                #self.loader_details = 0
        yield self.env.timeout(10)  ###### Для того чтобы можно было вызвать как генератор

    def to_warehouse(self):
        """Перемещение грузчиков от станции тех.обслуживания(1 или 2) к складу"""
        global warehouse_loaders
        self.x += 3
        if self.x > 450 and self.y != 380:
            self.x = 450
            """От станции тех.обслуживания №2:"""
            # self.y -= 2
            # if self.y < 380:
            #     self.y = 380
            """От станции тех.обслуживания №1:"""
            self.y += 2
            if self.y > 380:
                self.y = 380

        if self.y == 380:
            self.x += 2
            if self.x > 650:
                self.x = 650
                self.status = "in_warehouse"
                self.image = pygame.image.load("loader.png")  # Загрузка в pygame картинки
                self.image = pygame.transform.scale(self.image,
                                                    (self.IMG_size, self.IMG_size))  # Изменение размера картинки
                warehouse_loaders += 1
                self.warehose_status = "empty"
                #yield self.env.timeout(500)

    def run(self):
        global warehouse_loaders
        global service_loaders1, service_loaders2
        global repairing_1, repairing_2
        global station1_repair, station2_repair
        global WAREHOSE_STATION_SIZE2

        i1 = 0
        i2 = 0

        time_loading = random.randint(2000, 3500)
        while True:
            # Отправление грузчика с запчастями от склада к станции тех.обслуживания №1:
            if self.status == "in_warehouse" and service_loaders1 == 0 and Loader.to_station1 == 0 and station1_status == 1:
                if self.status_now != "to_station2":
                    self.status_now = "to_station1"
                    Loader.to_station1 = 1
                if warehouse_loaders != 0:
                    warehouse_loaders -= 1

            if self.status == "in_warehouse" and service_loaders1 == 0 and Loader.to_station1 == 1 \
                    and self.status_now == "to_station1" and station1_status == 1 and WAREHOSE_STATION_SIZE2 > details_required1:
                if self.warehose_status == "empty":
                    WAREHOSE_STATION_SIZE2 -= details_required1
                    self.loader_details = details_required1 #####
                    self.warehose_status = "full"
                #self.to_service_station1()

            if self.status == "in_warehouse" and service_loaders1 == 0 and Loader.to_station1 == 1 \
                    and self.status_now == "to_station1" and station1_status == 1 and self.loader_details != 0:
                yield env.process(self.to_service_station1())


####################
            # if self.warehose_status == "empty" and WAREHOSE_STATION_SIZE2 > details_required1 and details_required1!=0:
            #     WAREHOSE_STATION_SIZE2 -= details_required1
            #     self.warehose_status = "full"
            #
            # if self.status == "in_warehouse" and service_loaders1 == 0 and Loader.to_station1 == 1 \
            #         and self.status_now == "to_station1" and station1_status == 1 and self.warehose_status == "full":
            #     self.to_service_station1()
#######################



            # Отправление грузчика с запчастями от склада к станции тех.обслуживания №2:
            if self.status == "in_warehouse" and service_loaders2 == 0 and Loader.to_station2 == 0 and station2_status == 1 :
                if self.status_now != "to_station1":
                    self.status_now = "to_station2"
                    Loader.to_station2 = 1
                if warehouse_loaders != 0:
                    warehouse_loaders -= 1

            if self.status == "in_warehouse" and service_loaders2 == 0 and Loader.to_station2 == 1 \
                    and self.status_now == "to_station2" and station2_status == 1 and WAREHOSE_STATION_SIZE2 > details_required2:
                #yield self.env.timeout(100)
                #self.to_service_station2()
                if self.warehose_status == "empty":
                    WAREHOSE_STATION_SIZE2 -= details_required2
                    self.loader_details = details_required2
                    self.warehose_status = "full"

            if self.status == "in_warehouse" and service_loaders2 == 0 and Loader.to_station2 == 1 \
                    and self.status_now == "to_station2" and station2_status == 1 and self.loader_details != 0:
                yield env.process(self.to_service_station2())


#####################
            # if self.warehose_status == "empty" and WAREHOSE_STATION_SIZE2 > details_required2 and details_required2!=0:
            #     WAREHOSE_STATION_SIZE2 -= details_required2
            #     self.warehose_status = "full"
            #
            # if self.status == "in_warehouse" and service_loaders2 == 0 and Loader.to_station2 == 1 \
            #         and self.status_now == "to_station2" and station2_status == 1 and self.warehose_status == "full":
            #     #yield self.env.timeout(100)
            #     self.to_service_station2()
##########################

            if WAREHOSE_STATION_SIZE2 < details_required1 or WAREHOSE_STATION_SIZE2 < details_required2:
                # Ждем грузовик с новыми запчастями и пополняем запас склада
                #yield env.process(truck1.run())
                if truck1.status == "in_warehouse":
                    yield env.process(truck1.to_production())


                # Грузовик находится на производстве:
                if truck1.status == "on_production":
                    if truck1.loading_status == "now":
                        #yield truck1.env.timeout(time_loading)
                        yield env.process(truck1.loading())
                        truck1.loading_status = "done"
                    if truck1.loading_status == "done":
                        yield env.process(truck1.to_warehouse())
                        if truck1.y == 240 and truck1.x == 600:
                            WAREHOSE_STATION_SIZE2 = WAREHOSE_MAX

                #yield env.process(truck1.to_warehouse())
                # global iteration
                # iteration = 0



            if self.status == "on_service_station1" or self.status == "on_service_station2":

                self.status_now = "to_warehouse"
                # sick1 = "1"
                if repairing_1 == "now" and self.status == "on_service_station1":
                    yield self.env.timeout(self.repair_time)  # Время ремонта
                    repairing_1 = "done"
                    self.loader_details = 0  #####
                    station1_repair = "ready"

                if repairing_2 == "now" and self.status == "on_service_station2":
                    yield self.env.timeout(self.repair_time)  # Время ремонта
                    repairing_2 = "done"
                    self.loader_details = 0 #####
                    station2_repair = "ready"

                if self.status == "on_service_station1":
                    service_loaders1 = 0
                elif self.status == "on_service_station2":
                    service_loaders2 = 0
                self.to_warehouse()
            yield self.env.timeout(50)

    def __call__(self, screen):
        self.image1 = self.image.get_rect(topleft=(self.x, self.y))
        screen.blit(self.image, self.image1)  # Расположить картинку по координатам


class Truck(object):
    """Экземпляр - команда грузчиков"""
    def __init__(self, env):
        self.IMG_size = 70
        self.image = pygame.image.load("truck.png") # Загрузка в pygame картинки
        self.image = pygame.transform.scale(self.image, (self.IMG_size + 20, self.IMG_size))  # Изменение размера картинки
        self.x = 600  # Изначальное положение центра картинки(Склад)
        self.y = 240
        # self.x = 660  # На производстве
        # self.y = 50

        self.env = env
        self.status_prev = ""  # "on_parking", "on_service_station", "moving"
        self.status = "in_warehouse"  # "on_production"
        #self.status = "on_production"  # "on_production"
        self.loading_status = ""   # Загружается ли сейчас грузовик? ("now"/"done")

    def loading(self):
        yield self.env.timeout(1500)

    def to_production(self):
        """Перемещение грузовика от склада к производству/заводу"""
        global iteration
        global event_time, event
        self.y -= 3
        if self.y < 50:
            self.y = 50

            self.x += 2
            if self.x > 660:
                self.x = 660
                self.status = "on_production"
                self.image = pygame.image.load("truck.png")  # Загрузка в pygame картинки
                self.image = pygame.transform.scale(self.image,
                                                    (self.IMG_size + 20, self.IMG_size))  # Изменение размера картинки
                iteration += 1
                self.loading_status = "now"
                event = "Грузовик на заводе"
                event_time = round(env.now / 1000)

        yield self.env.timeout(10) ###### Для того чтобы можно было вызвать как генератор

    def to_warehouse(self):
        """Перемещение грузовика от завода к складу"""
        global iteration
        global WAREHOSE_STATION_SIZE2
        global event, event_time
        self.x -= 2
        if self.x < 600:
            self.x = 600

            self.y += 3
            if self.y > 240:
                self.y = 240
                self.status = "in_warehouse"
                self.image = pygame.image.load("truck.png")  # Загрузка в pygame картинки
                self.image = pygame.transform.scale(self.image, (self.IMG_size + 20, self.IMG_size))  # Изменение размера картинки
                iteration += 1
                event = "Грузовик на складе"
                event_time = round(env.now / 1000)
                #WAREHOSE_STATION_SIZE2 = WAREHOSE_MAX
        yield self.env.timeout(10)  ###### Для того чтобы можно было вызвать как генератор

    def run(self):
        """Данный метод НЕ ВЫЗЫВАЕТСЯ"""
        #iteration = 1
        global WAREHOSE_STATION_SIZE2
        time_loading = random.randint(2000, 3500)  # Время загрузки грузовика на производстве

        while iteration < 2:
            # Грузовик находится на складе:
            if self.status == "in_warehouse":
                self.to_production()
                #iteration = 2
            # Грузовик находится на производстве:
            if self.status == "on_production":
                if self.loading_status == "now":
                    yield self.env.timeout(time_loading)
                    self.loading_status = "done"
                if self.loading_status == "done":
                    self.to_warehouse()
                    if self.y == 240 and self.x == 600:
                        WAREHOSE_STATION_SIZE2 = WAREHOSE_MAX

            yield self.env.timeout(70)

            #iteration += 1

    def __call__(self, screen):
        self.image1 = self.image.get_rect(topleft=(self.x, self.y))
        screen.blit(self.image, self.image1)  # Расположить картинку по координатам



def airplane_generator(env, cars):
    """Генерируем новые самолеты, которые прибывают на обслуживание"""
    for i in itertools.count():
        yield env.timeout(random.randint(T_INTER[0], T_INTER[1]))
        if len(cars) != 0:
            a = cars.pop(0)
            renderer.add(a)
            env.process(a.run())

class Monitoring(object):
    """Класс для отображения текста и состояния переменных"""
    def __init__(self, stoyanka_counts):
        self.stoyanka_counts = stoyanka_counts
        self.font = pygame.font.Font(None, 20)

    def __call__(self, screen):
        # Отображение текста на экране:
        text = self.font.render("Кол-во самолетов: ", True, (0, 0, 255))
        loaders_count = self.font.render("Кол-во грузчиков: ", True, (0, 0, 255))
        details_count = self.font.render("Требуется деталей: ", True, (0, 0, 255))
        screen.blit(text, [10, 230])
        # Отображение кол-ва самолетов на стоянке:
        text1 = self.font.render(str(stoyanka_counts), True, (0, 0, 255))
        screen.blit(text1, [135, 230])
        # # Отображение кол-ва самолетов на станции тех.обслуживания №1:
        #text2 = self.font.render(str(service_airplanes1), True, (0, 0, 150))
        text2 = self.font.render(str(station1_status), True, (0, 0, 150))
        screen.blit(text2, [375, 215])
        screen.blit(text, [250, 215])
        # # Отображение кол-ва деталей на станции тех.обслуживания №1:
        #details_count = self.font.render("Кол-во деталей: ", True, (0, 0, 255))
        screen.blit(details_count, [240, 165])
        text_details = self.font.render(str(details_required1), True, (0, 0, 150))
        screen.blit(text_details, [375, 165])
        # # Отображение кол-ва самолетов на станции тех.обслуживания №2:
        #text3 = self.font.render(str(service_airplanes2), True, (0, 0, 50))
        text3 = self.font.render(str(station2_status), True, (0, 0, 50))
        screen.blit(text3, [375, 390])
        screen.blit(text, [250, 390])
        # # Отображение кол-ва деталей на станции тех.обслуживания №2:
        screen.blit(details_count, [240, 340])
        text_details = self.font.render(str(details_required2), True, (0, 0, 150))
        screen.blit(text_details, [375, 340])
        # # Отображение кол-ва команд грузчиков на складе:
        text4 = self.font.render(str(warehouse_loaders), True, (0, 0, 50))
        screen.blit(text4, [905, 300])
        screen.blit(loaders_count, [778, 300])
        # # # Отображение кол-ва деталей на складе:
        # text41 = self.font.render(str(warehose.level), True, (0, 0, 50))
        # screen.blit(text41, [960, 325])
        # details_warehose = self.font.render("Кол-во деталей на складе(можно убрать): ", True, (0, 0, 255))
        # screen.blit(details_warehose, [778, 325])
        # # Отображение кол-ва деталей на складе(2):
        text42 = self.font.render(str(WAREHOSE_STATION_SIZE2), True, (0, 0, 50))
        screen.blit(text42, [970, 325])
        details_warehose = self.font.render("Кол-во деталей на складе: ", True, (0, 0, 255))
        screen.blit(details_warehose, [778, 325])
        # # Отображение кол-ва команд механиков на станции тех.обслуживания №1:
        text5 = self.font.render(str(service_loaders1), True, (0, 0, 50))
        screen.blit(text5, [375, 190])
        screen.blit(loaders_count, [250, 190])
        # # Отображение кол-ва команд механиков на станции тех.обслуживания №2:
        text6 = self.font.render(str(service_loaders2), True, (0, 0, 50))
        screen.blit(text6, [375, 365])
        screen.blit(loaders_count, [250, 365])


class Monitoring1(object):
    """Класс для отображения ВСПОМОГАТЕЛЬНОГО текста и состояния переменных(ДЛЯ ОТЛАДКИ)"""
    def __init__(self):
        #self.stoyanka_counts = stoyanka_counts
        self.font = pygame.font.Font(None, 20)

    def __call__(self, screen):
        # Отображение текста на экране:
        text3 = self.font.render("Событие: ", True, (0, 0, 255))
        screen.blit(text3, [550, 440])
        text3 = self.font.render("Время: ", True, (0, 0, 255))
        screen.blit(text3, [650, 440])
        # Отображение Airplane.to_station1:
        text = self.font.render(str(event), True, (0, 0, 255))
        screen.blit(text, [550, 470])
        air_to_station1_mon = self.font.render(str(event_time), True, (0, 0, 255))
        screen.blit(air_to_station1_mon, [700, 470])
        # # # Отображение Airplane.to_station2:
        # text2 = self.font.render("Airplane.to_station2: ", True, (0, 0, 255))
        # screen.blit(text2, [550, 500])
        # air_to_station2_mon = self.font.render(str(Airplane.to_station2), True, (0, 0, 150))
        # screen.blit(air_to_station2_mon, [700, 500])
        # #screen.blit(text, [250, 215])
        # # Отображение Loadres.to_station1:
        # text3 = self.font.render("Loaders.to_station1: ", True, (0, 0, 255))
        # screen.blit(text3, [550, 530])
        # air_to_station1_mon = self.font.render(str(Loader.to_station1), True, (0, 0, 255))
        # screen.blit(air_to_station1_mon, [700, 530])
        # # Отображение Loadres.to_station2:
        # text4 = self.font.render("Loaders.to_station2: ", True, (0, 0, 255))
        # screen.blit(text4, [550, 560])
        # air_to_station1_mon = self.font.render(str(Loader.to_station2), True, (0, 0, 255))
        # screen.blit(air_to_station1_mon, [700, 560])
        # # Отображение iteration:
        # text5 = self.font.render("iteration: ", True, (0, 0, 255))
        # screen.blit(text5, [550, 590])
        # truck_iterarion = self.font.render(str(iteration), True, (0, 0, 255))
        # screen.blit(truck_iterarion, [700, 590])
        # Время в симуляции:
        text6 = self.font.render("Время симуляции: ", True, (0, 0, 255))
        screen.blit(text6, [550, 620])
        environment_time = self.font.render(str(round(env.now/1000)), True, (0, 0, 255))
        screen.blit(environment_time, [700, 620])

class Monitoring2(object):
    """Класс для отображения ВСПОМОГАТЕЛЬНОГО текста и состояния переменных(ДЛЯ ОТЛАДКИ)"""
    def __init__(self):
        #self.stoyanka_counts = stoyanka_counts
        self.font = pygame.font.Font(None, 20)

    def __call__(self, screen):
        # Отображение текста на экране:
        text3 = self.font.render("События: ", True, (0, 0, 255))
        screen.blit(text3, [800, 440])
        # Отображение текста на экране:
        text7 = self.font.render("Время: ", True, (0, 0, 255))
        screen.blit(text7, [930, 440])
        # Отображение Airplane.to_station1:
        text = self.font.render("Самолет1 прибыл на стоянку: ", True, (0, 0, 255))
        screen.blit(text, [750, 470])
        environment_time = self.font.render(str(airplane1.time_parking), True, (0, 0, 255))
        screen.blit(environment_time, [970, 470])
        # # Отображение Airplane.to_station2:
        text2 = self.font.render(str(airplane1.monitoring), True, (0, 0, 255))  # Отображение текущего события
        screen.blit(text2, [750, 500])
        environment_time1 = self.font.render(str(airplane1.time_now), True, (0, 0, 255))   # Отображение времени текущего события
        screen.blit(environment_time1, [970, 500])

        text3 = self.font.render("Самолет1 общее время: ", True, (0, 0, 255))
        screen.blit(text3, [750, 530])
        environment_time2 = self.font.render(str(airplane1.time_result), True, (0, 0, 255))
        screen.blit(environment_time2, [970, 530])
        # air_to_station1_mon = self.font.render(str(airplane1.time_leave), True, (0, 0, 255))
        # screen.blit(air_to_station1_mon, [900, 530])
        # Отображение Loadres.to_station2:
        text4 = self.font.render("Самолет2 прибыл на стоянку: ", True, (0, 0, 255))
        screen.blit(text4, [750, 560])
        air_to_station1_mon = self.font.render(str(airplane2.time_parking), True, (0, 0, 255))
        screen.blit(air_to_station1_mon, [9700, 560])
        # Отображение текущего события самолета2:
        text5 = self.font.render(str(airplane2.monitoring), True, (0, 0, 255))  # Отображение текущего события
        screen.blit(text5, [750, 590])
        environment_time3 = self.font.render(str(airplane2.time_now), True, (0, 0, 255))  # Отображение времени текущего события
        screen.blit(environment_time3, [970, 590])
        #############
        # Время в симуляции:
        # text6 = self.font.render("Время симуляции: ", True, (0, 0, 255))
        # screen.blit(text6, [750, 620])
        # environment_time = self.font.render(str(round(env.now/1000)), True, (0, 0, 255))
        # screen.blit(environment_time, [900, 620])

        text6 = self.font.render("Самолет2 общее время: ", True, (0, 0, 255))
        screen.blit(text6, [750, 620])
        environment_time4 = self.font.render(str(airplane2.time_result), True, (0, 0, 255))
        screen.blit(environment_time4, [970, 620])

###########################################################
def repair():
    """Ремонт самолета на станции тех.обслуживания"""
    time_repair = random.randint(3000, 7000)  # Время для ремонта
    # yield env.process(mechanic1.run())
    return time_repair



# def service_station_control(env, warehose):
#     """Периодически проверяем кол-во деталей на складе(%) и заказываем новые
#     детали, если значение ниже порогового"""
#     print("warehose.level=", warehose.level)
#     global iteration
#     while True:
#
#         warehose.get(45)    # Забрать 45 деталей со склада
#         print("warehose.level=", warehose.level)
#         print("warehose.capacity=", warehose.capacity)
#         if (warehose.level / warehose.capacity * 100 < THRESHOLD):
#
#             #iteration = 1  # Условие для запуска нового цикла грузовика
#
#             # Необходимо сделать заказ новых деталей!
#             print(f'Заказ грузовика с новыми деталями в {env.now} секунд')
#             print("-------")
#             # Ждем грузовик с новыми запчастями и пополняем запас склада
#             yield env.process(truck1.run())
#
#         yield env.timeout(10)  # Check every 10 seconds



###########################################################

"""Описание игры"""
pygame.init()

# Define constants for the screen width and height
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700

"""Вспомогательные переменные для отображения количества агентов, координат"""
############################################################
stoyanka_counts = 0     # Кол-во самолетов на стоянке
#service_airplanes1 = 0  # Кол-во самолетов на станции тех.обслуживания №1
#service_airplanes2 = 0  # Кол-во самолетов на станции тех.обслуживания №2
warehouse_loaders = 0   # Кол-во команд грузчиков на складе
service_loaders1 = 0    # Кол-во команд грузчиков на станции тех.обслуживания №1
service_loaders2 = 0    # Кол-во команд грузчиков на станции тех.обслуживания №2
WAREHOSE_STATION_SIZE = 50    # Максимальное(изначальное) количество деталей на складе
THRESHOLD = 20                 # Порог имеющихся деталей для заказа новых запчастей (в %)
number_station = 2
station1_status = 0     # Занята станция №1 или свободна(0/1)
stoyanka_to_station1 = 0  # Находится ли ктото в пути от стоянки к станции 1
station2_status = 0     # Занята станция №1 или свободна(0/1)
stoyanka_to_station2 = 0  # Находится ли ктото в пути от стоянки к станции 1

station1_repair = ""  # Статус ремонта самолета на ст.1 - "repair"/"ready"
station2_repair = ""  # Статус ремонта самолета на ст.2 - "repair"/"ready"

repairing_1 = ""  # Ведется ли сейчас ремонт на 1 станции? (now/done) - ожидание грузчиком и самолетом ремонта
repairing_2 = ""  # Ведется ли сейчас ремонт на 2 станции? (now/done) - ожидание грузчиком и самолетом ремонта

iteration = 0

details_required1 = 0  # Сколько деталей требуются для починки самолета на станции 1
details_required2 = 0  # Сколько деталей требуются для починки самолета на станции 2

WAREHOSE_MAX = 50
WAREHOSE_STATION_SIZE2 = WAREHOSE_MAX    # Максимальное(изначальное) количество деталей на складе

event = ""  # Глобальное событие в системе
event_time = 0  # Время глобального события


##############################################################

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

renderer = FrameRenderer(screen)

env = PyGameEnvironment(renderer, factor=0.001, strict=False)

renderer.add(Monitoring(stoyanka_counts))
# renderer.add(Monitoring(service_airplanes1))
# renderer.add(Monitoring(service_airplanes2))

renderer.add(Monitoring1())

renderer.add(Monitoring2())


airplane1 = Airplane(env, 1)
airplane2 = Airplane(env, 2)
airplane3 = Airplane(env, 3)
#####
airplane4 = Airplane(env, 4)
airplane5 = Airplane(env, 5)
##########
airplanes = [airplane1, airplane2, airplane3, airplane4, airplane5]

mechanic1 = Loader(env)
mechanic2 = Loader(env)
mechanic3 = Loader(env)
# mechanic3.x = 400  # На станции 1
# mechanic3.y = 230
# mechanic3.status = "on_service_station1"  # "on_service_station", "moving"

renderer.add(mechanic2)
env.process(mechanic2.run())
renderer.add(mechanic3)
env.process(mechanic3.run())

renderer.add(mechanic1)
env.process(mechanic1.run())

truck1 = Truck(env)
renderer.add(truck1)
#env.process(truck1.run())

service_station = simpy.Resource(env, number_station)  # Общий ресурс - станции обслуживания
warehose = simpy.Container(env, WAREHOSE_STATION_SIZE, init=WAREHOSE_STATION_SIZE)  # Склад(контейнер) - механики забирают детали, грузовик привозит новые

env.process(airplane_generator(env, airplanes))
#env.process(service_station_control(env, warehose))

# for airplane in airplanes:
#     print(f"Общее время нахождения самолета{airplane.name} в аэропорту = {airplane.time_result}")

env.run()


