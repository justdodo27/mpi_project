from mpi4py import MPI
from time import sleep, time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    status = MPI.Status()
    sleep(6)
    while True:
        if comm.iprobe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status):
            req = comm.irecv(source=status.Get_source(), tag=status.Get_tag())
            data = req.wait()
            print(f"Got data {data}")
else:
    comm.isend("XD", dest=0, tag=0)