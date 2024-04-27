import socket 
import utils
import rsa
import threading
import json
import sys
import cv2
import pickle
import numpy as np
import time
import os

# User dictionary 
users = {}

# Videos list 
videos_list = []

# name of the streaming video
video_to_stream = ""

# Generating private and public keys for the user
user_public_key , user_private_key = rsa.newkeys(1024)

# Initialisng server intials to connect to it
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 1234

# Initialising user socket
user_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)

# Connect to server 
user_socket.connect((SERVER , PORT))

# recieving the server public key
server_key = rsa.PublicKey.load_pkcs1(user_socket.recv(4096))

# Taking in the username of the user
name = str(input("Enter your username : "))
user_socket.send(name.encode())

#Recieve dummy msg 
msg = user_socket.recv(8192) 

# send the public key of the user
user_socket.send(user_public_key.save_pkcs1("PEM"))

# Recieve the initial dictionary 
data = user_socket.recv(16384).decode()
if data[:4] == 'URIF':
    # print("initial recieve")
    users = json.loads(data[4:])

sent = 0

def send_chat(user_socket):
    print("[WELCOME] This our chat room ,\nYou can send messages to available clients.\nEnter the name out of available users to send message to.\nEnter the message and there you go !\nTo quit chat room , enter user as QUIT. ")
    while True : 
        print("----------------")
        print("Available users : ")
        for keys , value in users.items():
            print(keys)
        print("----------------")
        partner = input("Enter the username you want to send message to : ")
        
        if(partner == "QUIT"):
            user_socket.send("QUIT".encode())
            break
        
        msg = input("Enter the message -> ")
        
        msg = f"{name} : " + msg
        partner_public_key = rsa.PublicKey.load_pkcs1(users[partner])
        msg = b"CHAT" + utils.rsa_encrypt(msg , partner_public_key)
        user_socket.send(msg)
    sys.exit()

def recv_chat(user_socket):
    while True:
        global users
        global videos_list
        global video_to_stream
        msg = user_socket.recv(1024)
        if msg[:4] == b'URIF':
            users = json.loads(msg[4:].decode())
            print("\n[NEW USER] A new user has joined the room.\n")
        elif msg[:4] == b"CHAT":
            text = msg[4:]
            try:
                text = utils.rsa_decrypt(text , user_private_key).strip()
                if text : 
                    print(f"\n[CHAT RECIEVED] {text}")
            except Exception as e : 
                print("")
        elif msg[:4] == b'STRM':
            # print("The message showing error is : ")
            # print(msg[4:8])
            frame_length = int.from_bytes(msg[4:8] , byteorder='big')
            # print(f"Total frames : {int(frame_length)}")

            killall = 0
            for i in range( 0 , int(frame_length)):
                frame_size_bytes = user_socket.recv(8)
                frame_size_bytes = int.from_bytes(frame_size_bytes , byteorder='big')
                # print(frame_size_bytes)

                frame_data = b""

                while len(frame_data) < frame_size_bytes:
                    chunk = user_socket.recv(min(frame_size_bytes-len(frame_data) , 8192))
                    if not chunk : 
                        break
                    frame_data += chunk
                # print(frame_data)
                if len(frame_data) == frame_size_bytes:
                    frame = cv2.imdecode(np.frombuffer(frame_data , dtype = np.uint8) , cv2.IMREAD_COLOR)
                    frame = cv2.resize(frame , (400 , 250))
                    cv2.imshow(f"Streaming : {video_to_stream}" , frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
            print("Stream ended")
            cv2.destroyAllWindows()
            sys.exit()
        elif msg[:4] == b'STLI':
            # print("Recieved header STLI")
            videos_list_length = int.from_bytes(msg[4:] , byteorder='big')
            videos_list = user_socket.recv(videos_list_length).decode()
            videos_list = json.loads(videos_list)
            # print("The available videos are : ")
            for i in range(len(videos_list)):
                print(f"{i+1}. {videos_list[i]}")
            # print("Done till here")

        else :
            print("Invalid argument")

def stream(user_socket):
    global videos_list 
    global video_to_stream
    # Send the video it wants to stream 
    # the bytes will be recieved in recv_chat thread as it is the only thread to recieve everything
    video_to_stream = int(input("Enter the index of the video you want to stream : "))
    video_to_stream = videos_list[video_to_stream-1]
    print(f"Video to stream : {video_to_stream}")
    user_socket.send(video_to_stream.encode())
    print("Stream starts shortly ...")
    pass
# Take in the servive it wants to use chat or stream
services = ['[CHAT]' , '[STREAM]' , '[DISCONNECT]']

threading.Thread(target = recv_chat , args = (user_socket,)).start()
while True : 
    print("[HOME PAGE] You are at home page , you can choose your service :)")
    service = input("Enter the number of the service you want to 1.[CHAT]  2.[STREAM] : 3.[QUIT]\n")
    service = services[int(service)-1]
    if service == '[CHAT]':
        user_socket.send("[CHAT]".encode())
        chat_thread = threading.Thread(target = send_chat , args = (user_socket,))
        chat_thread.start()
        chat_thread.join()
        pass
    elif service == '[STREAM]':
        # print("stream chosen")
        user_socket.send("[STREAM]".encode())
        stream_thread = threading.Thread(target = stream , args = (user_socket,))
        stream_thread.start()
        stream_thread.join()
        # while sent != 0:
        #   user_socket.send("OK".encode())
            # sent = 1
    elif service == '[DISCONNECT]':
        user_socket.send('[DISCONNECT]'.encode())
        # sys.exit()
        os._exit(0)
    else : 
        print("Enter a valid argument!")
        pass
