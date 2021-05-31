# Chord DHT

[Original Repo](https://github.com/ddeka0/Chord-DHT.git) by Abhishek Singh and Debashish Deka

Distributed Dictionary Implementation using chord DHT

Explanation:
  
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

       - 1. Create Root node, run `python3 chord.py <RootNodePort>` and keep terminal open
       - 2. Add other nodes to Root node to form the chord. Run `python3 chord.py <NodePort> <RootNodePort>` in another terminal
       - 3. Run `python3 client.py <NodeIP> <NodePort>`  : NodeIP default is 127.0.0.1 and NodePort of any DHT nodes (including root node).
       - 4. Input word-meaning and output meaning for word using client console.
