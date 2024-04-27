# TCP-Chatroom-and-Video-Streaming

## Tejas Mhaiskar
## Chat room and Video Streaming

### Demo Link : 
* **NOTE** : The **server.py Assignment** shown as video in the available video list is a video file in the same directory which was a failed screen recording done before.**
* **https://www.youtube.com/watch?v=sbe8RCJIf0I&t=171s**
* Use , headphones if possible , the audio from the mic recorded is not loud enough .


### File structure : 
* Place client.py , utils.py and server.py in the same directory .  
* Place all the videos in the same directory as client.py and server.py . The naming convention for videos is [video_name]_[resolution].mp4 . 
* popo and wildlife are two videos are already present and provided in the submission , you can add in more with the accepted format stated in the point before .

### Steps to run the code :
* Run server.py in a terminal
* Run as many client.py's in other terminals . 
* The instructions as enter username , choose the service etc are displayed on the terminal
* First it prompts to enter the username . It registers yourself to the server . 
* Then it asks for the service , enter 1 2 or 3 out of the available ones . 
    1. For chat , enter the username out of available users and then the message . To QUIT , enter the username as QUIT and it moves you back to the homepage .
    2. For streaming , select the index of the video and it streams in all the possible resolutions equally . 
    3. For QUIT , it disconnects you from the server and exits the code .

### Explanation for files :

#### client.py
* The required packages have been imported as socket , threading , cv2 and others
* Variables have been initialized . users is a dictionary storing username-public key pairs . videos_list is a list storing all the available video names retrived from the server . New rsa keys for the client are generated . Socket is initialized and connected to the server . Username input is taken . Username , client public key , server public key are exchanged . The client recieves  the initial dictionary of users and their public keys . 
* Now the code moves to line number 152 after all the defined functions . A recv_chat thread responsible for handling all the recieved data to the client is started . Inside a while loop , the client is given options out of the available services . 
* Threads used : 
    1. **send_chat thread** : Responsilble to send the chat messages if the client is using the chat services . Prints the instructions of chat room initially . Prints out the list of available users . Prompts the user to enter the username and the message . Sends the encrypted chat message to the server using the public key .
    2. **recv_chat thread** : Responsible to recieve all data frames . The name states its recieves chat , initially the function served that purpose only but slowly it evolved into a general recieving thread . It inherits some global variables which are relevant and can be seen in the code . Recieves the message(msg) out of which first 4 bytes indicate the type of the message . Header URIF corresponds to User Information , meaning updated dictionary for users is recieved . Header CHAT corresponds to a chat recieved from another user .It decrypts the message using rsa and the client's public key . If its success in decrypting , meaning the message is meant for the user and prints else ignores . Header STRM corresponds to a frame of video recieved . Header STLI corresponds to Stream List and gets the list of videos which are available at the server . Each header is handled according  to its methods . And can be seen in the code . 
    3. **stream thread** : This thread actually just takes in the name of the video user wants to stream and  sends it to the client . It also prints the list of available videos which is print before the input prompt .
* On exiting the app , os._exit(0) is used to terminate the process for the client .

#### server.py
* The required packages have been imported as socket , threading , cv2 and others
* Various initialisations as client dictionary , client sockets list , videos list is declatered . **For videos , they should be stored in the same directory as server.py and client.py. Also the name of the videos should be of the form [video_name]_[resolution].mp4** . Public key of the server is generated and exchanged with the client(Although server public key is not used anywhere ahead.) . 
* Now the code moves on the the line 189 with the function start() being called .
* The server establishes a connection with the client and then starts the thread handle_client for each of the clients . 
* The server recieves the headers and it handles the client accordingly . 
    1. **[CHAT]** : Header chat meaning it recieved a chat message from one of the clients . It broadcasts the message to all the clients using the client socket list .
    2. **[STREAM]** : This is responsible for streaming the video . Its sends the frames of the video . **Note : For example : If a video has 902 frames and 4 resolutions , 902/4 in integer comes out to be 225 but 2 frames still remain to be streamed . These number of frames are referred to as "remain" number of frames and are streamed first . i.e. 2 frames streamed of the first quality in the list and then 225 frames of each kind .** . Usually , the number of frames is much larger and number of available resolutions is not more than 5 or 6 . So these residual frames do not bring much change .
    3. **[DISCONNECT]** : Its disconnects the client from the server . The server removes its entry in the dictionary and sockets list . It is then broadcasted to every available client . The thread is exited using sys.exit() funciton . 
#### utils.py 
* This file contains , the rsa encryption and decryption functions . This is not much used in the code but used in some places . 
