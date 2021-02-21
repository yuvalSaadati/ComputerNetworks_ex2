import sys
import socket
import os


def send_message(file_name, conn, client_socket, client_address):
    message = "HTTP/1.1 "
    # index.html:
    if file_name == "/":
        if not os.path.isfile("files/index.html"):
            message += "404 Not Found\r\nConnection: close\r\n\r\n"
            client_socket.send(message.encode())
            return "close"
        message += "200 OK\r\nConnection: " + str(conn) + "\r\nContent-Length: "\
                   + str(os.stat("files/index.html").st_size) + "\r\n\r\n"
        message += open("files/index.html", "r").read()
        client_socket.send(message.encode())
        return conn
    # redirect:
    if file_name == "/redirect":
        message += "301 Moved Permanently\r\nConnection: close\r\nLocation: /result.html\r\n\r\n"
        client_socket.send(message.encode())
        return "close"

    # pictures, icons and regular files:
    if not os.path.isfile("files/" + file_name):
        message += "404 Not Found\r\nConnection: close\r\n\r\n"
        client_socket.send(message.encode())
        return "close"

    message += "200 OK\r\nConnection: " + str(conn) + "\r\nContent-Length: " \
               + str(os.stat("files/" + file_name).st_size) + "\r\n\r\n"
    message = message.encode()
    message += open("files/" + file_name, "rb").read()
    client_socket.send(message)
    return conn


def handle_request(client_socket, client_address, client_request):
    file_name = ""
    conn = ""
    lines = client_request.split("\r\n")
    for line in lines:
        if "GET" in line:
            file_name = line.split()[1]
        if "Connection:" in line:
            conn = line.split()[1]

    # check the case that the request is an empty request
    if file_name == "":
        return "close"

    return send_message(file_name, conn, client_socket, client_address)


def connect_with_server(server_port):
    # create a TCP socket.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(server_port)))
    server.listen(1)
    # start listening to clients.
    while True:
        client_socket, client_address = server.accept()
        client_socket.settimeout(1)
        data = ''
        conn = ''
        try:
            while True:
                if conn == "close":
                    break
                while "\r\n\r\n" not in data:
                    data += client_socket.recv(1024).decode()
                # at this moment 'data' contains a complete request from the client.
                while "\r\n\r\n" in data:
                    data, remainder = data.split("\r\n\r\n", 1)
                    print(data)
                    conn = handle_request(client_socket, client_address, data)
                    if conn == "close":
                        break
                    data = remainder
            client_socket.close()
        except socket.timeout:
            client_socket.close()


def main(server_port):
    connect_with_server(server_port)


if __name__ == "__main__":
    main(sys.argv[1])
