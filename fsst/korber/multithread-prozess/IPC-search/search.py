import multiprocessing as mp

def split_list(original_list, num_sublists):
    n = len(original_list)
    k, remainder = divmod(n, num_sublists)  

    result = []
    start = 0
    for i in range(num_sublists):
        end = start + k + (1 if i < remainder else 0)
        result.append(original_list[start:end])
        start = end
    return result



def worker(id,usrword,sublist, child):
    print(f"Worker {id} is searching")
    result=sublist.count(usrword)
    child.send(result)
    child.close()


if __name__ == "__main__":
    processes = []
    pipes = []
    ges=0
    with open('text.txt', 'r') as file:
        a = file.read()

    words= a.split()
# print(words)

    uword= input("word to search for: ")
    unum= int(input("how many processes? "))

    sublists = split_list(words, unum)
# print(sublists)

    for i in range(unum):
        parent, child = mp.Pipe()
        p = mp.Process(target=worker, args=(i,uword,sublists[i], child))
        processes.append(p)
        pipes.append(parent)

    for p in processes:
        p.start()

    for parent in pipes:
        ergebnis = parent.recv()
        ges+=ergebnis

        # print(ergebnis)
        parent.close()

    for p in processes:
        p.join()

    print(f"Das wort '{uword}' wurde {ges} mal gefunden")
