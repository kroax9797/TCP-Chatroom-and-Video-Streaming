import socket
import utils
import rsa
import threading
import json
import sys
import cv2
import pickle
import os

# Dictionary to store clients 
# 'name' : public_key
client_dict = dict()

# Client sockets
client_sockets = []

# Video list : 
current_directory = os.getcwd()
files = os.listdir(current_directory)
videos = [file for file in files if file.endswith('.mp4')]
videos_unique = set()

for filename in videos : 
    video_name = filename.split('_')[0]
    videos_unique.add(video_name)

videos_unique = list(videos_unique)

# Generating rsa keys for the server
public_key , private_key = rsa.newkeys(1024)

# Initialising server socket addr and port
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 1234

# Initialising the server socket 
server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
server_socket.bind((SERVER , PORT))


def handle_client(conn):
    while True : 
        # Recieving the name and public_key of the user
        username = conn.recv(1024).decode().strip()
        conn.send("OK".encode())
        user_public_key = conn.recv(4096).decode()
        client_dict[username] = user_public_key
        print(f"[NEW USER {username}] Number of total connections : {len(client_dict)}")

        # Broadcast the client_dictionary
        users_info = json.dumps(client_dict)
        for c in client_sockets:
            c.send(("URIF" + users_info).encode())
        # print("USERS SENT")

        while True : 
            service = conn.recv(1024).decode()
            if(service == '[CHAT]'):
                print(f"Chat service used by the client {username}")
                while True : 
                    # Broadcasting recieved msg
                    msg = conn.recv(8192)
                    if(msg == b'QUIT'):
                        break
                    else: 
                        for c in client_sockets:
                            c.send(msg)
                        
            elif(service == '[STREAM]'):
                # Sending all the available video file names to the user : 
                videos_data = json.dumps(videos_unique)
                conn.send(b'STLI' + len(videos_data).to_bytes(4 , byteorder='big'))
                conn.send(videos_data.encode())
                # print(len(f"videos data length : {len(videos_data)}"))

                # Recieving the video to be streamed 
                video_to_play = conn.recv(1024).decode().strip()
                # print(f"Video to play : {video_to_play}")

                resolutions = []
                for item in videos:
                    if item.startswith(video_to_play):
                        resolutions.append(item)
                resolutions = sorted(resolutions)
                # print(f"List of videos :\n")
                # print(resolutions)
                num_resolution = int(len(resolutions))
                # print(f"Num resolutions : {num_resolution}")

                VIDEO_FILE_PATH = f'./{resolutions[0]}'
                cap = cv2.VideoCapture(VIDEO_FILE_PATH)
                limit = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                conn.send(b'STRM' + limit.to_bytes(4 , byteorder='big'))
                print(f"{username} is streaming {video_to_play}")
                # Streaming video to the user : 
                # for i in range(0 , limit):
                #     ret , frame = cap.read()
                #     if not ret : 
                #         break
                #     encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                #     result , encoded_frame = cv2.imencode('.jpg' , frame , encode_param)
                #     if not result : 
                #         continue 
                #     frame_size = len(encoded_frame)
                #     # print(frame_size)
                #     f = frame_size.to_bytes(8,byteorder='big')
                #     # print(f)
                #     conn.sendall(f)
                #     conn.sendall(encoded_frame)

                frame_number = 0
                hehe = 0
                frame_delta = int(limit/num_resolution)
                remain = limit%num_resolution
                # print(f"Remaining frames : {remain}")
                # print(f"frame delta : {frame_delta}")

                for residue in range(0 , remain):
                    VIDEO_FILE_PATH = resolutions[0]
                    cap = cv2.VideoCapture(VIDEO_FILE_PATH)
                    cap.set(cv2.CAP_PROP_POS_FRAMES , frame_number)
                    ret , frame = cap.read()
                    if not ret : 
                        break 
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                    result , encoded_frame = cv2.imencode('.jpg' , frame , encode_param)
                    if not result : 
                        continue 
                    frame_size = len(encoded_frame)
                    f = frame_size.to_bytes(8,byteorder='big')
                    conn.sendall(f)
                    conn.sendall(encoded_frame)
                    frame_delta += 1

                for VIDEO_FILE_PATH in resolutions:
                    print(f"Streaming {VIDEO_FILE_PATH} to {username}")
                    # print("inside for loop")
                    cap = cv2.VideoCapture(VIDEO_FILE_PATH)
                    cap.set(cv2.CAP_PROP_POS_FRAMES , frame_number)
                    # print("cap done")
                    for alpha in range(0 , frame_delta):
                        hehe += 1 
                        ret , frame = cap.read()
                        if not ret : 
                            break
                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
                        result , encoded_frame = cv2.imencode('.jpg' , frame , encode_param)
                        if not result : 
                            continue 
                        frame_size = len(encoded_frame)
                        f = frame_size.to_bytes(8,byteorder='big')
                        conn.sendall(f)
                        conn.sendall(encoded_frame)
                    frame_number += frame_delta
                    cap.release()
                print(f"Stream ended for {username}")

                # print(f"Frames send : {hehe}")

            elif(service == '[DISCONNECT]'):
                del(client_dict[username])
                client_sockets.remove(conn)
                users_info = json.dumps(client_dict)
                for c in client_sockets:
                    c.send(("URIF" + users_info).encode())
                print("[UPDATE] Dictionary has been updated and sent to all the available clients.")
                print(f"[DISCONNECTED {len(client_dict)}] '{username}' has been disconnected from the network.")
                sys.exit()
            else :
                print(f"Error in connection {username} , quitting...")
                sys.exit()
            # Take in the servive it wants to use


def start():
    server_socket.listen()
    print(f"[LISTENING] Server accepting clients on {SERVER}")
    while True :
        # Accepting a new client
        conn , addr = server_socket.accept()
        # Sending the public key of the server
        conn.send(public_key.save_pkcs1("PEM"))
        client_sockets.append(conn)
        
        threading.Thread(target=handle_client , args = (conn,)).start()
    pass

start()