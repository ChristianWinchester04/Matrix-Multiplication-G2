#author: drew meketi
#i am the goat

import argparse
import os
import socket
import struct
import sys
import time
import numpy as np

# message types, anmd i think server must match these
JOB = 1     # server ->client: job id, A block, full B
RESULT = 2  # client -> server: job id, finished C block
DONE = 3    # server -> client: no more work, shut down

DTYPE = np.dtype("<i8")           # every matrix goes over the wire as little-endian int64
TYPE_FMT = struct.Struct("!B")    # 1 byte msg type
JOB_ID_FMT = struct.Struct("!I")  # 4 byte job id
SHAPE_FMT = struct.Struct("!II")  # rows, cols, should be 4 bytes each, and then sent before every matrix?

NAME = socket.gethostname()  # container id in docker


def log(msg):
    print(f"[client {NAME}] {msg}", flush=True)  # flush or docker logs holds onto it


def recv_exact(sock, n):
    buf = bytearray(n)
    view = memoryview(buf)
    got = 0
    while got < n:  # tcp hands data over in big ol chunks until its all done
        count = sock.recv_into(view[got:], n - got)
        if count == 0:  # 0 bytes equal closed
            raise ConnectionError(f"server stopped up mid-message big L (got {got} of {n} bytes)")
        got += count
    return buf
#dang bruh its just like networks class

def recv_matrix(sock):
    rows, cols = SHAPE_FMT.unpack(recv_exact(sock, SHAPE_FMT.size))
    data = recv_exact(sock, rows * cols * DTYPE.itemsize)
    return np.frombuffer(data, dtype=DTYPE).reshape(rows, cols)  # reads the bytes


def send_matrix(sock, matrix):
    matrix = np.ascontiguousarray(matrix, dtype=DTYPE)  # makes sure it's row-major and a good type
    sock.sendall(SHAPE_FMT.pack(*matrix.shape))
    sock.sendall(matrix.reshape(-1).view(np.uint8))  # sends


def handle_job(sock):
    (job_id,) = JOB_ID_FMT.unpack(recv_exact(sock, JOB_ID_FMT.size))
    a_block = recv_matrix(sock)
    b = recv_matrix(sock)
    log(f"job {job_id}: got A block {a_block.shape} and B {b.shape}")

    #todo might add error handle below idk
    #if a_block.shape[1] != b.shape[0]:
        #raise ValueError(f"job {job_id}: A block is {a_block.shape} but B is {b.shape}, the basic reqs of matmul is not fulfilled")

    start = time.perf_counter()
    c_block = a_block @ b  #actual work
    elapsed = time.perf_counter() - start
    log(f"job {job_id}: multiplied in {elapsed:.4f}s, sending back {c_block.shape}")

    sock.sendall(TYPE_FMT.pack(RESULT) + JOB_ID_FMT.pack(job_id))  # job id has to go back to server
    send_matrix(sock, c_block)


def connect(host, port, retries, delay):
    for attempt in range(1, retries + 1):
        try:
            sock = socket.create_connection((host, port))
            log(f"connected to {host}:{port}")
            return sock
        except OSError as e:  # depends_on only waits for the server container to start, not to be listening, so retry
            log(f"can't reach {host}:{port} yet ({e}), try {attempt}/{retries}")
            time.sleep(delay)
    raise ConnectionError(f"gave up on {host}:{port} after {retries} tries, is the server running on that port?")


def main():
    parser = argparse.ArgumentParser(description="matrix multiplication worker")
    parser.add_argument("--host", default=os.environ.get("SERVER_HOST", "server"))  # "server" is the compose service name
    parser.add_argument("--port", type=int, default=int(os.environ.get("SERVER_PORT", 5000)))
    parser.add_argument("--retries", type=int, default=30)
    parser.add_argument("--delay", type=float, default=1.0)  # however many seconds between connect attempts
    args = parser.parse_args()

    try:
        sock = connect(args.host, args.port, args.retries, args.delay)
    except ConnectionError as e:
        log(f"error: {e}")
        sys.exit(1)

    jobs_done = 0
    with sock:
        try:
            while True:  # keep taking jobs until server gives all clear
                (msg_type,) = TYPE_FMT.unpack(recv_exact(sock, TYPE_FMT.size))
                if msg_type == DONE:
                    break
                if msg_type != JOB:
                    raise ValueError(f"got unknown message type {msg_type}, server and client protocols probably don't match")
                handle_job(sock)
                jobs_done += 1
        except (OSError, ValueError) as e:  # OSError covers resets and hangups, ValueError covers bad data
            log(f"error: {e}")
            sys.exit(1)

    log(f"done, finished {jobs_done} job(s)")


if __name__ == "__main__":
    main()
