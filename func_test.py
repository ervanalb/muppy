import logging
import muppy
from muppy.func import FuncCore
import numpy as np
import random
import multiprocessing
import time

logging.basicConfig(level=logging.INFO)

def random_actions():
    actions = []
    for i in range(random.randint(0, 100)):
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
    everything = random.sample(actions1, len(actions1) // 2) + random.sample(actions2, len(actions2) // 2)
    if len(everything) > 400:
        return random.sample(everything, 400)
    return everything

def f(worker, actions):
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
        action, data = incoming_queue.get()
        if action == "SHUTDOWN":
            break
        elif action == "RUN":
            result = f(core, data)
            outgoing_queue.put((data, result))
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
    incoming_queue = multiprocessing.Queue()
    outgoing_queue = multiprocessing.Queue()

    for i in range(n_workers):
        t = multiprocessing.Process(target=worker_thread, daemon=True)
        workers.append(t)
        t.start()

def request_work(data):
    global incoming_queue
    incoming_queue.put(("RUN", data))

def retrieve_work():
    global outgoing_queue
    return outgoing_queue.get()

def main():
    N_WORKERS = 10
    POP_SIZE = 30
    SURVIVAL = 10
    OFFSPRING_RATIO = 0.8 # Sets ratio of offspring to random new members

    startup(N_WORKERS) # Simultaneous workers
    try:
        work = []
        for i in range(POP_SIZE): # Population size
            request_work(random_actions())

        while True:
            work.append(retrieve_work())

            # Only remember the top SURVIVAL members
            work = list(sorted(work, key=lambda x: x[1]))[0:SURVIVAL]

            print([x[1] for x in work])
            print("Best is:", work[0][0])

            if random.random() < OFFSPRING_RATIO and len(work) > 2:
                print("Add offspring")
                offspring = merge(*[x[0] for x in random.sample(work, 2)])
                request_work(offspring)
            else:
                print("Add new random")
                request_work(random_actions())

    finally:
        shutdown()

if __name__ == "__main__":
    main()
