import json 
import time 
import socket 
import os 
import threading 


IP_TO_USERNAME_FILE = "ip_to_username.json"
USERNAME_TO_IP_FILE = "username_to_ip.json"
CONTENT_DICT_FILE = "content_dictionary.json"


UDP_PORT = 6000
CONTENT_WIPE_INTERVAL_SEC = 60 
RECENT_PEER_TIMEOUT = 120 


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("",UDP_PORT))

print(f"UDP is being listened to: port {UDP_PORT}")


ip_to_username = {}
username_to_ip = {}
content_to_users = {}
ip_last_seen = {} 




def save_json(path, data):
    tmp = path + ".tmp" 
    with open(tmp, "w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    os.replace(tmp, path)


def wipe_content_dictionary():
    while True:
        time.sleep(CONTENT_WIPE_INTERVAL_SEC)
        content_to_users.clear()
        save_json(CONTENT_DICT_FILE, content_to_users)
        print("[Content Discovery] content_dictionary cleared.")

threading.Thread(target=wipe_content_dictionary, daemon=True).start()



while True: 
    data, addr = sock.recvfrom(65535)
    print(f"[A packet arrived from the network.!] From: {addr}")
    message = data.decode('utf-8')
    sender_ip = addr[0]
       

    try:
        obj = json.loads(message)
    except json.JSONDecodeError: 
        print("Invalid JSON, skipped.")
        continue

    username = obj.get("username")
    chunks = obj.get("chunks")

    if not isinstance(username, str) or not isinstance(chunks, list):
        print("Username or chunks are incorrect, skipped.")
        continue

    ip_to_username[sender_ip] = username 
    username_to_ip[username] = sender_ip 
    
    ip_last_seen[sender_ip] = time.monotonic()

    now = time.monotonic()
    for ip in list(ip_last_seen.keys()):
        if now - ip_last_seen[ip] > RECENT_PEER_TIMEOUT:   
            ip_to_username.pop(ip, None)
            ip_last_seen.pop(ip, None)

    
    for chunk in chunks:
        if not isinstance(chunk, str):  
            continue
            
        content_to_users.setdefault(chunk, [])
        if sender_ip not in content_to_users.setdefault(chunk, []):
            content_to_users[chunk].append(sender_ip)
    chunk_list = ", ".join(chunks)

    
    save_json(IP_TO_USERNAME_FILE, ip_to_username)
    save_json(USERNAME_TO_IP_FILE, username_to_ip)
    save_json(CONTENT_DICT_FILE, content_to_users)
    
    print(f"{username} : {chunk_list}")
