from argparse import Namespace
import mcstatus
import threading

def generate_ip_strings(ip,mask):
    """Mask = {8,16,24,32} | 8 = ip + .{}.{}.{}"""

    mask = str(mask)
    return_list = []
    if "32" in mask:
        return_list.append(ip)
    elif "24" in mask:
        for i in range(0,256):
            return_list.append(f'{ip}.{i}')
    elif "16" in mask:
        for i in range(0,256):
            for j in range(0,256):
                return_list.append(f'{ip}.{i}.{j}')
    elif "8" in mask:
        for i in range(0,256):
            for j in range(0,256):
                for k in range(0,256):
                    return_list.append(f'{ip}.{i}.{j}.{k}')
    return return_list

def mc_status_java(ip):
    try:
        port = 25565
        status = mcstatus.JavaServer.lookup(f'{ip}:{port}')
        res = status.status()
        return res
    except:
        return None

def mc_status_bedrock(ip):
    try:
        port = 19132
        status = mcstatus.BedrockServer.lookup(f'{ip}:{port}')
        res = status.status()
        return res
    except:
        return None

def args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', help='IP to scan', required=True)
    parser.add_argument('-p', '--port', help='Port to scan', required=False)
    parser.add_argument('-m', '--mask', help='Mask to scan', required=True)
    parser.add_argument('-s', '--scan', help='Scan type | sync | async | compress | test', required=True)
    parser.add_argument('-t', '--threads', help='Number of threads to use', required=False)
    parser.add_argument('-v', '--verbose', help='Verbose', required=False, action='store_true')
    args = parser.parse_args()
    return args

def omni_mcstatus_request(ip):
    java = mc_status_java(ip)
    if java != None:
        return "JavaServer + |Players:{}|Latency:{}ms".format(java.players.sample,java.latency),None
    bedrock = mc_status_bedrock(ip)
    if bedrock != None:
        return None,"BedrockServer + |Players:{}|Latency:{}ms".format(bedrock.players.sample,bedrock.latency)
    return java,bedrock

def append_to_file(file_name,text):
    with open(file_name, 'a') as f:
        f.write(text)

def compress_all_txt_files_in_dir():
    import os
    text = {}
    for file in os.listdir():
        if file.endswith(".txt"):
            #open file with utf-8
            with open(file, 'r', encoding='utf-8') as f:
                text[file] = f.read()
            #delete file
            os.remove(file)
    #create new file
    with open("all.txt", 'w', encoding='utf-8') as f:
        for key in text:
            f.write(key+":"+text[key]+"\n")

def thread_function(ip_list,thread_id,verbose=0):
    print(f"Thread {thread_id} started on ip-s: {ip_list[0]} to {ip_list[-1]}")
    for ip in ip_list:
        if verbose != 0: print("\nIP: {}".format(ip))
        x = omni_mcstatus_request(ip)
        if x[0] != None:
            append_to_file(f"{thread_id}_thread.txt",f"{ip}|{x[0]} - JavaServer")
        if x[1] != None:
            append_to_file(f"{thread_id}_thread.txt",f"{ip}|{x[1]} - BedrockServer")
    print(f"Thread {thread_id} finished")

def main():
    arg = args()
    global_args = arg
    print(arg)
    if arg.scan == 'sync':
        list = generate_ip_strings(arg.ip,arg.mask)
        print("Synchronously scanning the following ip range :{} to {}".format(list[0],list[-1]))
        for ip in list:
            if arg.verbose != 0: print("\nIP: {}".format(ip))
            x = omni_mcstatus_request(ip)
            if x[0] != None:
                print(f"{ip}|{x[0]} - JavaServer")
            if x[1] != None:
                print(f"{ip}|{x[1]} - BedrockServer")
    elif arg.scan == 'async':
        list = generate_ip_strings(arg.ip,arg.mask)
        threads = []
        if arg.threads == None:
            arg.threads = 15
        avg_workload = round(len(list) / int(arg.threads))
        for i in range(int(arg.threads)+1):
            if i == int(arg.threads) - 1:
                threads.append(threading.Thread(target=thread_function, args=(list[i*avg_workload:],i,arg.verbose)))
            else:
                threads.append(threading.Thread(target=thread_function, args=(list[i*avg_workload:(i+1)*avg_workload],i,arg.verbose)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        print("Finished")
    elif arg.scan == "test":
        append_to_file("test.txt","test")
    elif arg.scan == "compress":
        compress_all_txt_files_in_dir()
    else:
        print('Invalid scan type')

main()