import socket

host = socket.gethostname()
ipAddress = socket.gethostbyname(host)
print("Host name: ", host)
print("IP Address: ", ipAddress)