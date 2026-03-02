import multiprocessing as mp

def worker(id, num, child):
    print(f"Worker {id} is calculating")
    result = num**2
    child.send(result)
    child.close()

if __name__ == "__main__":
    processes = []
    pipes = []

    for i in range(5):
        parent, child = mp.Pipe()
        p = mp.Process(target=worker, args=(i, 100, child))
        processes.append(p)
        pipes.append(parent)

    for p in processes:
        p.start()

    for parent in pipes:
        ergebnis = parent.recv()
        print(ergebnis)
        parent.close()

    for p in processes:
        p.join()
