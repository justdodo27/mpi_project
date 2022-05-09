from typing import Dict
from mpi4py import MPI
from time import sleep, time
from random import randint

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

TAGS = {
    'reservation': 0,
    'landing': 1,
    'starting': 2,
    'respond': 3,
}

STATES = {
    'reserving': 0,
    'landing': 1,
    'starting': 2,
    'idle': 3,
}

SHIPS = [2,2]


class Plane():
    def __init__(self, rank: int):
        self.status = MPI.Status()
        self.rank = rank
        self.counter = 0
        self.state = STATES['reserving']
        self.desired_ship = randint(0, len(SHIPS)-1)
        self.reservation_list = set()
        self.airstrip_list = set()
        self.request_id = self.rank * 100

    def increment_counter(self) -> None:
        self.counter += 1
    
    def print_state(self) -> str:
        if self.state == 0:
            return f'reserving {self.desired_ship}'
        elif self.state == 1:
            return f'landing on {self.desired_ship}'
        elif self.state == 2:
            return f'starting from {self.desired_ship}'
        elif self.state == 3:
            return f'idle on {self.desired_ship}...'

    def calc_respond_value(self, recv_priority: int, source: int) -> int:
        if self.counter == recv_priority:
            if self.rank < source:
                return 1
            else:
                return 0
        elif self.counter < recv_priority:
            return 1
        elif self.counter > recv_priority:
            return 0

    def send_requests(self) -> None:
        if self.state == STATES['reserving']:
            tag = TAGS['reservation']
        elif self.state == STATES['landing']:
            tag = TAGS['landing']
        elif self.state == STATES['starting']:
            tag = TAGS['starting']
        for i in range(size):
            if i == rank: continue
            comm.isend({'id': self.request_id, 'priority': self.counter, 'ship': self.desired_ship}, dest=i, tag=tag)
    
    def receive_request(self, tag: int, source: int, data: Dict) -> None:
        if tag == TAGS['reservation']:
            if data['ship'] != self.desired_ship:
                respond_value = 0
            elif data['ship'] == self.desired_ship:
                if self.state == STATES['reserving']:
                    respond_value = self.calc_respond_value(data['priority'], source)
                else: # landing, idle, starting - means that place is taken
                    respond_value = 1
            comm.isend({'id': data['id'], 'priority': self.counter, 'respond_value': respond_value}, dest=source, tag=TAGS['respond'])
            if respond_value == 1:
                self.reservation_list.add((source, data['id']))
            # elif respond_value == 0 and source in self.airstrip_list:
            #     self.airstrip_list.remove(source)
        elif tag == TAGS['landing']:
            if data['ship'] != self.desired_ship:
                respond_value = 1
            elif data['ship'] == self.desired_ship:
                if self.state == STATES['landing']:
                    respond_value = self.calc_respond_value(data['priority'], source)
                elif self.state == STATES['idle']:
                    respond_value = 1
                elif self.state == STATES['starting']:
                    respond_value = 0
                elif self.state == STATES['reserving']:
                    respond_value = 1
            comm.isend({'id': data['id'], 'priority': self.counter, 'respond_value': respond_value}, dest=source, tag=TAGS['respond'])
            # if source in self.reservation_list:
            #     self.reservation_list.remove(source)
            if respond_value == 0:
                self.airstrip_list.add((source, data['id']))
            # elif respond_value == 1 and source in self.airstrip_list:
            #     self.airstrip_list.remove(source)
        elif tag == TAGS['starting']:
            if data['ship'] != self.desired_ship:
                respond_value = 1
            elif data['ship'] == self.desired_ship:
                if self.state == STATES['starting']:
                    respond_value = self.calc_respond_value(data['priority'], source)
                elif self.state == STATES['idle']:
                    respond_value = 1
                elif self.state == STATES['landing']:
                    respond_value = 1
                elif self.state == STATES['reserving']:
                    respond_value = 1
            comm.isend({'id': data['id'], 'priority': self.counter, 'respond_value': respond_value}, dest=source, tag=TAGS['respond'])
            # if source in self.reservation_list:
            #     self.reservation_list.remove(source)
            if respond_value == 0:
                self.airstrip_list.add((source, data['id']))
            # elif respond_value == 1 and source in self.airstrip_list:
            #     self.airstrip_list.remove(source)

    def wait_for_responds(self) -> None:
        responds_count = 0
        responds_value = 0
        while True:
            req = comm.irecv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
            data = req.wait(status=self.status)
            tag = self.status.Get_tag()
            source = self.status.Get_source()
            
            if tag == TAGS['respond']:
                if self.request_id == data['id']:
                    responds_count += 1
                    responds_value += data['respond_value']
            else:
                self.receive_request(tag, source, data)

            if responds_count >= size-1:
                if self.state == STATES['reserving'] and SHIPS[self.desired_ship] - responds_value > 0:
                    break
                elif self.state in [STATES['landing'], STATES['starting']] and responds_value == size-1:
                    break
        
    def idle(self, seconds: int) -> None:
        start_time = time()
        print(f"{self.rank} ({self.counter}): {self.print_state()}")
        while True:
            if comm.iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=self.status):
                req = comm.irecv(source=self.status.Get_source(), tag=self.status.Get_tag())
                data = req.wait(status=self.status)
                tag = self.status.Get_tag()
                source = self.status.Get_source()
                self.receive_request(tag, source, data)

            if time() - start_time >= seconds: break
        self.change_state()

    def send_reservation_responds(self) -> None:
        for source, id in self.reservation_list:
            print(f"{self.rank} ({self.counter}): send reservation free to {source}")
            comm.isend({'id': id, 'priority': self.counter, 'respond_value': -1}, dest=source, tag=TAGS['respond'])
        self.reservation_list.clear()

    def send_airstrip_responds(self) -> None:
        for source, id in self.airstrip_list:
            print(f"{self.rank} ({self.counter}): send airstrip free to {source}")
            comm.isend({'id': id, 'priority': self.counter, 'respond_value': 1}, dest=source, tag=TAGS['respond'])
        self.airstrip_list.clear()

    def change_state(self) -> None:
        if self.state == STATES['reserving']:
            self.state = STATES['landing']
        elif self.state == STATES['landing']:
            self.state = STATES['idle']
            self.send_airstrip_responds()
            self.idle(10)
        elif self.state == STATES['idle']:
            self.state = STATES['starting']
        elif self.state == STATES['starting']:
            self.desired_ship = randint(0, len(SHIPS)-1)
            self.state = STATES['reserving']
            self.send_reservation_responds()
            self.send_airstrip_responds()
        self.increment_counter()

    def run(self) -> None:
        while True:
            self.send_requests()
            self.wait_for_responds()
            self.request_id += 1
            self.change_state()
            sleep(1.5)
            print(f"{self.rank} ({self.counter}): {self.print_state()}")

plane = Plane(rank)

plane.run()