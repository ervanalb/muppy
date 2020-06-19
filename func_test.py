import logging
import muppy
from muppy.func import FuncCore
import numpy as np
import random
import queue
import threading
import time

logging.basicConfig(level=logging.INFO)

def random_actions():
    actions = []
    for i in range(random.randint(10, 100)):
        t = random.randrange(240)
        a = random.choice([
            (0x80, None, None), # A
            (0x40, None, None), # B
            (0x20, None, None), # Z
            (0, random.randint(-128, 127), random.randint(-128, 127)), # Joystick
        ])
        actions.append((t, a))
    return actions

def merge(actions1, actions2):
    everything = actions1 + actions2
    if len(everything) > 400:
        return random.sample(everything, 400)
    return everything

def f(actions):
    inputs = [[0, 0, 0] for _ in range(240)]
    goal = np.array([77.0, -3045.0])

    for t, a in sorted(actions, key=lambda x: x[0]):
        # Press buttons
        inputs[t][0] |= a[0]
        if a[1] is not None or a[2] is not None:
            # Hold joystick
            for i in range(t, len(inputs)):
                inputs[i][1] = a[1]
                inputs[i][2] = a[2]

    results = worker.test("start.st", inputs=inputs, mem_addrs=[(0x80339E3C, "f"), (0x80339E44, "f")])
    results = np.array(results)
    dists = np.linalg.norm(results - goal, axis=1)
    return np.sum(dists)

def worker_thread():
    core = FuncCore("/home/eric/sm64.jp.z64")
    while True:
        action, data = incoming_q.get()
        if action == "SHUTDOWN":
            break
        elif action == "RUN":
            result = f(data)
            outgoing_q.put((data, result))
    core.close()

def shutdown():
    for _ in workers:
        incoming_queue.put(("SHUTDOWN", None))

    for w in workers:
        w.join()

def startup(n_workers):
    global workers
    global incoming_queue, outgoing_queue

    workers = []
    incoming_queue = queue.Queue()
    outgoing_queue = queue.Queue()

    for i in range(n_workers):
        t = threading.Thread(target=worker_thread, daemon=True)
        workers.append(t)
        t.start()
        time.sleep(3)

def request_work(data):
    global incoming_queue
    incoming_queue.put(("RUN", data))

def retrieve_work():
    global outgoing_queue
    return outgoing_queue.get()

def main():
    startup(3)
    try:
        for i in range(3):
            request_work(random_actions())

        for i in range(3):
            (actions, result) = retrieve_work()
            print(result)

    finally:
        shutdown()

if __name__ == "__main__":
    main()
