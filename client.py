import sys
import socket

if len(sys.argv)==3:
    while(1):
        print("Enter 1 to lookup")
        print("Enter 2 to insert")
        print("Enter 3 to Exit")
        choice  = input("Enter your choice :")
        if choice=='1':
            key = input("Input Key :")
            s = socket.socket()
            port = 12345
            s.connect(('127.0.0.1',port))
            msg = "LOOKUP "+key+" \r\n"
            s.send(msg.encode('utf-8'))
            receiveddata = s.recv(256)
            receiveddata = receiveddata.decode('utf-8')
            print(receiveddata)
            s.close()
        if choice=='2':
            key = input("Input Key :")
            value = input("Input Value :")
            s = socket.socket()
            port = 12345
            s.connect(('127.0.0.1', port))
            msg = "INSERT " + key + " " + value + " \r\n"
            s.send(msg.encode('utf-8'))
            receiveddata = s.recv(256)
            receiveddata = receiveddata.decode('utf-8')
            print(receiveddata)
            s.close()
        if choice =='3':
            break
else:
    print("insufficient or incorrect arguments")