from time import sleep
from typing import Dict
from random import randint
import curses
import curses.panel
import threading
from config import *

import mpi4py
mpi4py.rc.initialize = False

from mpi4py import MPI

MPI.Init_thread(2)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

class Plane():
    def __init__(self, rank: int, stdscrn, win):
        self.status = MPI.Status()
        self.rank = rank
        self.counter = 0
        self.state = STATES['reserving']
        self.desired_ship = randint(0, len(SHIPS)-1)
        self.reservation_list = set()
        self.airstrip_list = set()
        self.request_id = self.rank * 100
        self.responds_count = 0
        self.responds_value = 0
        self.stdscr = stdscrn
        self.win = win

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

    def print(self, text: str) -> None:
        self.win.addstr(text)
        self.win.noutrefresh()
        curses.doupdate()
        self.stdscr.noutrefresh()
        curses.doupdate()

    def calc_respond_value(self, recv_priority: int, source: int, resource_type: str) -> int:
        if self.counter == recv_priority:
            if self.rank < source:
                if resource_type == 'SPOT': return RESPOND_NEG_RESERVATION
                elif resource_type == 'AIRSTRIP': return RESPOND_NEG_AIRSTRIP
            else:
                if resource_type == 'SPOT': return RESPOND_POS_RESERVATION 
                elif resource_type == 'AIRSTRIP': return RESPOND_POS_AIRSTRIP
        elif self.counter < recv_priority:
            if resource_type == 'SPOT': return RESPOND_NEG_RESERVATION 
            elif resource_type == 'AIRSTRIP': return RESPOND_NEG_AIRSTRIP
        elif self.counter > recv_priority:
            if resource_type == 'SPOT': return RESPOND_POS_RESERVATION 
            elif resource_type == 'AIRSTRIP': return RESPOND_POS_AIRSTRIP

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
                respond_value = RESPOND_POS_RESERVATION
            elif data['ship'] == self.desired_ship:
                if self.state == STATES['reserving']:
                    respond_value = self.calc_respond_value(data['priority'], source, resource_type='SPOT')
                else: # landing, idle, starting - means that place is taken
                    respond_value = RESPOND_NEG_RESERVATION

            comm.isend({'id': data['id'], 'priority': self.counter, 'respond_value': respond_value}, dest=source, tag=TAGS['respond'])
            
            if respond_value == RESPOND_NEG_RESERVATION:
                self.reservation_list.add((source, data['id']))

        elif tag == TAGS['landing']:
            if data['ship'] != self.desired_ship:
                respond_value = RESPOND_POS_AIRSTRIP
            elif data['ship'] == self.desired_ship:
                if self.state == STATES['landing']:
                    respond_value = self.calc_respond_value(data['priority'], source, resource_type='AIRSTRIP')
                elif self.state == STATES['idle']:
                    respond_value = RESPOND_POS_AIRSTRIP
                elif self.state == STATES['starting']:
                    respond_value = RESPOND_NEG_AIRSTRIP
                elif self.state == STATES['reserving']:
                    respond_value = RESPOND_POS_AIRSTRIP
            
            comm.isend({'id': data['id'], 'priority': self.counter, 'respond_value': respond_value}, dest=source, tag=TAGS['respond'])

            if respond_value == RESPOND_NEG_AIRSTRIP:
                self.airstrip_list.add((source, data['id']))
            
        elif tag == TAGS['starting']:
            if data['ship'] != self.desired_ship:
                respond_value = RESPOND_POS_AIRSTRIP
            elif data['ship'] == self.desired_ship:
                if self.state == STATES['starting']:
                    respond_value = self.calc_respond_value(data['priority'], source, resource_type='AIRSTRIP')
                elif self.state == STATES['idle']:
                    respond_value = RESPOND_POS_AIRSTRIP
                elif self.state == STATES['landing']:
                    respond_value = RESPOND_POS_AIRSTRIP
                elif self.state == STATES['reserving']:
                    respond_value = RESPOND_POS_AIRSTRIP

            comm.isend({'id': data['id'], 'priority': self.counter, 'respond_value': respond_value}, dest=source, tag=TAGS['respond'])
            
            if respond_value == RESPOND_NEG_AIRSTRIP:
                self.airstrip_list.add((source, data['id']))

    def wait_for_responds(self) -> None:
        while True:
            if self.responds_count >= size-1:
                if self.state == STATES['reserving'] and SHIPS[self.desired_ship] - self.responds_value > 0:
                    break
                elif self.state in [STATES['landing'], STATES['starting']] and self.responds_value == size-1:
                    break
        
    def idle(self, seconds: int) -> None:
        self.print(f"{self.rank} ({self.counter}): {self.print_state()}\n")
        sleep(seconds)
        self.change_state()

    def free_spot(self) -> None:
        for source, id in self.reservation_list:
            self.print(f"{self.rank} ({self.counter}): send res. free to {source}\n")
            comm.isend({'id': id, 'priority': self.counter, 'respond_value': FREE_RESERVATION}, dest=source, tag=TAGS['respond'])
        self.reservation_list.clear()

    def free_airstrip(self) -> None:
        for source, id in self.airstrip_list:
            self.print(f"{self.rank} ({self.counter}): send as. free to {source}\n")
            comm.isend({'id': id, 'priority': self.counter, 'respond_value': FREE_AIRSTRIP}, dest=source, tag=TAGS['respond'])
        self.airstrip_list.clear()

    def change_state(self) -> None:
        if self.state == STATES['reserving']:
            self.state = STATES['landing']
        elif self.state == STATES['landing']:
            sleep(LANDING_TIME)
            self.print(f"{self.rank} ({self.counter}): landed on {self.desired_ship}\n")
            self.state = STATES['idle']
            self.idle(IDLE_TIME)
        elif self.state == STATES['idle']:
            self.state = STATES['starting']
        elif self.state == STATES['starting']:
            sleep(STARTING_TIME)
            self.print(f"{self.rank} ({self.counter}): started from {self.desired_ship}\n")
            self.desired_ship = randint(0, len(SHIPS)-1)
            self.state = STATES['reserving']
            self.free_spot()
        self.increment_counter()

    def run(self) -> None:
        while True:
            self.send_requests()
            self.wait_for_responds()
            sleep(1.5)
            self.print(f"{self.rank} ({self.counter}): {self.print_state()}\n")
            self.request_id += 1
            self.change_state()

    def communicate(self) -> None:
        local_id = self.request_id
        while True:
            if self.state in (STATES['idle'], STATES['reserving']) and len(self.airstrip_list) > 0:
                self.free_airstrip()

            req = comm.irecv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
            data = req.wait(status=self.status)
            tag = self.status.Get_tag()
            source = self.status.Get_source()

            if local_id != self.request_id:
                self.responds_count = 0
                self.responds_value = 0
                local_id = self.request_id

            if tag == TAGS['respond']:
                if self.request_id == data['id']:
                    self.responds_count += 1
                    self.responds_value += data['respond_value']
            else:
                self.receive_request(tag, source, data)
        

def main(stdscr):
    curses.curs_set(0)  # cursor off.
    curses.noecho()
    curses.cbreak()
    
    scr_y = curses.LINES
    scr_x = curses.COLS

    win = curses.newwin(scr_y, scr_x // size, 0, (scr_x // size) * rank)
    win.scrollok(True)
    
    win.noutrefresh()
    stdscr.noutrefresh()
    curses.doupdate()

    plane = Plane(rank, stdscr, win)
    x = threading.Thread(target=plane.run)
    y = threading.Thread(target=plane.communicate)
    x.start()
    y.start()

if __name__ == '__main__':
    curses.wrapper(main)