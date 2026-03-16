import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(("", 50000))   # listen on all network interfaces
s.listen(4)

clients = []

def handle_client(comm, addr):
    print(f"{addr} connected")
    clients.append(comm)

    try:
        while True:
            data = comm.recv(1024)
            if not data:
                break

            print(f"{addr}: {data.decode()}")

            # send message to all clients
            for client in clients:
                if client != comm:
                    client.send(data)

    finally:
        print(f"{addr} disconnected")
        clients.remove(comm)
        comm.close()


try:
    while True:
        print("waiting for connection")
        comm, addr = s.accept()

        thread = threading.Thread(target=handle_client, args=(comm, addr))
        thread.start()

except:
    print("Something went wrong")

finally:
    s.close()
