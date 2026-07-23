import socket 
import json   
import time   
import os  


BROADCAST_IP = "192.168.71.255"
UDP_PORT = 6000
ANNOUNCE_INTERVAL_SEC = 8


username = input("Please enter your username:") 
filename = input("Enter the name of the file you want to share:") 

def split_file(filename, chunk_dir="chunks"):
       os.makedirs(chunk_dir, exist_ok=True) 
    
       with open(filename, "rb") as f: 
        data = f.read() 
      
        total = len(data) 
        first = total // 3
        second = total // 3 
        third = total - first - second
       
       
       base_name = os.path.splitext(os.path.basename(filename))[0]
       chunk_names = [] 
       offset = 0  

       for i, size in enumerate([first, second, third], start=1): 
           part = data[offset : offset + size]
           offset = offset + size

           chunk_name = f"{base_name}_{i}"
           out_path = os.path.join(chunk_dir, chunk_name) 

           with open(out_path, "wb") as out: 
            out.write(part)

           chunk_names.append(chunk_name) 
       return chunk_names
       
def build_announce_payload(username, chunk_names):
    message = {"username": username, "chunks": chunk_names}
    return json.dumps(message, ensure_ascii=False).encode("utf-8")







chunk_names = split_file(filename)
for f in os.listdir("chunks"):
    if f not in chunk_names:
        chunk_names.append(f)
print(f"3 parts were created: {chunk_names}")
print("UDP announcements begin (stop by Ctrl+C)...")

with open("local_username.txt", "w", encoding="utf-8") as f:
    f.write(username)

payload = build_announce_payload(username, chunk_names)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", 0))
target = (BROADCAST_IP, UDP_PORT)
while True:
    sock.sendto(payload, target)
    print("announcement sent:", payload.decode("utf-8"))
    time.sleep(ANNOUNCE_INTERVAL_SEC)
