# CS620-A2
Youtube link for demo :

[ScreenCast of demo](https://www.youtube.com/watch?v=iMEgMrZbH2A&feature=youtu.be)

Distributed Dictionary Implementation using chord DHT

Team members:
	-Abhishek Singh 18305R010
	-Debashish Deka 173050055

Explnation:
  
	- There are separate modules for network send/recv functionalities. We are using TCP, therefore to handle the byte oriented nature of TCP, network module's read and sends in loop untill all the bytes are written.

	- RPC across different processes is simulated using message passing method to the server of each participating node.
	- For hashing we have used md5. hashlib.md5(str.encode())
Requirements : 

    System Requirement:
        - Linux Kernel 2.6 or higher
        - python3
    
    Dependency Package: (use sudo apt-get to install the dependencies)
        - python3-pip
        
Steps to setup the project environment:
       
       - 1. Run script.py  : will launch 4 gnome terminals. (check the script.py for hardcoded server ports)
       - 2. Run client.py ip port  : ip and port of any of DHT nodes.
       - 3. Input word-meaning and ouput meaning for word using client console.
