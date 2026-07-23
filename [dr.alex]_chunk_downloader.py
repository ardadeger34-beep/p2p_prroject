import json
import socket #for TCP connections.
import base64 #for decoding ,encoding stuff.
import datetime
import random #for generating a key for secure download.
import pyDes #for decryting.
import time  #for fixing timing issue

#function declerations.
def log_download(chunk_names, ip) : #download time.
    timestamp = datetime.datetime.now()
    with open("download_log.txt", "a") as log_file:
        log_file.write(str(timestamp) + " | " + chunk_names + " | " + ip + " | RECEIVED\n")

def view_contents() :
    with open("content_dictionary.json", "r") as opened_file: #open the file in read mode, and assign it to something to destroy it automaticly later.
        content_dictionary = json.load(opened_file)
        
    content_names = [] #holder for content names.

    for chunk_names in content_dictionary: #loop the chunk names to extract the content name.
        temp = chunk_names.split("_")

        if temp[0] not in content_names: #chechk if the name already exist because there is more than onne chunks.
            content_names.append(temp[0])

    print(content_names)

    return content_names # to reuse in download function, give user a list to pick from.
        

def download_content() :
    with open("content_dictionary.json", "r") as opened_file: #open the file in read mode, and assign it to something to destroy it automaticly later.
        content_dictionary = json.load(opened_file)

    content_names = view_contents() #catches the list.

    print("Pick one from above: ")
    temp = input("Enter your choice:") #get the file name from user.

    print("Pick one: Secure, Unsecure")
    temp1 = input("Please enter: ")

    if temp not in content_names : #check the content names for a match.
        print("File name not exists.")
        return
    
    else: #when match is found.

        if temp1 == "Secure" : #Check if they want secure or not.

            #generate a secret number to send a secure key.
            fix_modulus_number = 907
            fix_base_number = 7
            secret_rand_number = random.randint(2, fix_modulus_number-2)
            key = (fix_base_number**secret_rand_number)%fix_modulus_number

            for i in range(1, 4):
                chunk_names = temp + "_" + str(i) #recreate the chunk names to find them in dictionary.
                ip_list = content_dictionary[chunk_names] #get the related IP adresses from content_dict.

                for ip in ip_list:
                    try:
                        key_message = json.dumps({"key": str(key)}) #convert the key integer to a json to send.
                        connectoin_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM) #create a socket to communicate from. AF_INET = IPv4 , SOCK_STREAM = TCP
                        connectoin_socket.connect((ip, 6001)) # connect the port and IP adress. (ip , port)
                        connectoin_socket.send(key_message.encode('utf-8')) #encode it and sends the key.
                        key_response = connectoin_socket.recv(4096) #recv the key.

                        recv_key_message = json.loads(key_response.decode('utf-8')) # decodes the incoming json and decodes it.
                        recv_key = int(recv_key_message["key"]) # extracts the key from json file and converts to integer.
                        time.sleep(0.1) # to fix servers timing issue about recving the key. Gives time to server to handle key.

                        shared_key = (recv_key**secret_rand_number) % fix_modulus_number #compute to verify the key.

                        #Conversion to 8 bytes for Data Encryption Standart, as requierments mention. Key creation.
                        des_key_string = str(shared_key).zfill(8)[:8]
                        des_key_bytes = des_key_string.encode('utf-8')

                        request_message = {"requested secured content": chunk_names}
                        request = json.dumps(request_message)
                        connectoin_socket.send(request.encode('utf-8')) #sending the request.
                        print("Chunk request sent:", request)

                        connectoin_socket.settimeout(2.0) #timeout to break the loop otherwise it would go forever and ever.
                        enc_response = b""
                        while True: # if it is too big break
                            try:
                                part = connectoin_socket.recv(65536)# recieve the content
                                if not part:
                                    break
                                enc_response += part
                            except:
                                pass

                        response = json.loads(enc_response.decode('utf-8')) #conversion to string.
                        encrypted_bytes = base64.b64decode(response["encrypted chunk"]) #bes64 decodtion.
                        
                        content_bytes = pyDes.des(des_key_bytes, pyDes.ECB, pad=None, padmode=pyDes.PAD_PKCS5).decrypt(encrypted_bytes) #decryption proccess to get the actual download content.

                        with open(chunk_names, 'wb') as byte_file: #save chunks to a file
                            byte_file.write(content_bytes) # writes bytes to a file.

                        connectoin_socket.close() #close the socket.
                        log_download(chunk_names, ip) #get the logs.
                        break

                    except Exception as e:
                        print(chunk_names + " is not able to download from " + ip)
                        print("Error:", e)
                
                else :
                    print("Chunks" + chunk_names + "cannot be downloaded from the online peers.")

            with open(temp, 'wb') as final_file: #get it all the chunks together and make 1 final file that can be viewable.
                for i in range(1, 4):
                    chunk_name = temp + "_" + str(i)
                    with open(chunk_name, 'rb') as chunk_file:
                        final_file.write(chunk_file.read())

            print(temp + " Downloaded successfully.")

        #unsecure proccess.
        elif temp1 == "Unsecure" :
            for i in range(1, 4):
                chunk_names = temp + "_" + str(i) #recreate the chunk names to find them in dictionary.
                ip_list = content_dictionary[chunk_names] #get the related IP adresses from content_dict.

                connection_message = {"requested content": chunk_names} #create a json connectoin request to send via TCP.
                request = json.dumps(connection_message) # convert to json.

                for ip in ip_list: #traverse the ip_list.
                    try: #for the IPs that do not work.
                        connectoin_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM) #create a socket to communicate from. AF_INET = IPv4 , SOCK_STREAM = TCP
                        connectoin_socket.connect((ip, 6001)) # connect the port and IP adress. (ip , port)
                        connectoin_socket.send(request.encode('utf-8')) # send connection request. encode to convert string to byte.

                        connectoin_socket.settimeout(2.0) #timeout to break the loop otherwise it would go forever and ever.
                        response = b""
                        try:
                            while True: #if its too big do this.
                                part = connectoin_socket.recv(65536)#recieves the message
                                if not part:
                                    break
                                response += part
                        except:
                            pass

                        data = json.loads(response.decode('utf-8')) # extract the data and convert it to string from json.
                        data_bytes = base64.b64decode(data["data"]) # revert to bytes.

                        with open(chunk_names, 'wb') as byte_file: #save chunks to a file
                            byte_file.write(data_bytes) # writes bytes to a file.

                        connectoin_socket.close() #close the socket.
                        log_download(chunk_names, ip)
                        break

                    except Exception as e:
                        print(chunk_names + " is not able to download from " + ip)
                        print("Error:", e)
                
                else :
                    print("Chunks" + chunk_names + "cannot be downloaded from the online peers.")

            with open(temp, 'wb') as final_file: #get it all the chunks together and make 1 final file that can be viewable.
                for i in range(1, 4):
                    chunk_name = temp + "_" + str(i)
                    with open(chunk_name, 'rb') as chunk_file:
                        final_file.write(chunk_file.read())

            print(temp + " Downloaded successfully.")

        else: #failsafe
            print("Wrong entry , try again.")
            return

def view_history() :   
    try:
        with open("download_log.txt", "r") as f:
            print(f.read())

    except:
        print("No download history.")


while True:
    print("Pick one: View Contents,Download Content,History")
    choice = input("Enter your choice: ")

    #get user input and decide the action.
    if choice == "View Contents":
        view_contents()
    elif choice == "Download Content":
        download_content()
    elif choice == "History":
        view_history()