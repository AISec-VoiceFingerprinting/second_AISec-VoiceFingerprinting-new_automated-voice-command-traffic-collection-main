import sys
import subprocess
from os.path import join, split, getsize
from os import remove
from pprint import pformat
from time import sleep, time
import random
import zipfile
import os
from pathlib import Path
import shutil


# 이거는 local 주소로 바꿔야해요
dataset_dir = "/data/VFP/dataset_dir/commands"      
mon_command_dir = "/data/VFP/dataset_dir/commands/input/monitored"    # monitored commands directory path
unmon_command_dir = "/data/VFP/dataset_dir/commands/input/unmonitored"     # monitored commands directory path
wake_word_dir = "/data/VFP/dataset_dir/commands/wake_words"     # wake word directory path
result_dir = "/data/VFP/dataset_dir/result"     #result directory path
 

instance=0
rasp_num="rasp1"

def file_rename(data_type):
    folder_path = result_dir    # result file path in local
    file_list = os.listdir(folder_path)
    if data_type==1:    # monitored
        for file_name in range(1,101):
            try:
                old_name = str(file_name) + ".pcap"
                new_name = str(file_name) + "_" + str(instance) + "_" + rasp_num + ".pcap"
                os.rename(old_name, new_name)
            except:
                print("fail to change " + file_name)
    
    elif data_type==0:   # unmonitored
        for file_name in range(101,151):
            try:
                old_name = str(file_name) + ".pcap"
                new_name = str(file_name) + "_" + str(instance) + "_" + rasp_num + ".pcap"
                os.rename(old_name, new_name)
            except:
                print("fail to change " + file_name)
    instance+=1


def do_send_server(batch_num):
     # make zip file
    file_path = result_dir
    owd = os.getcwd()
    os.chdir(file_path)
    zip_file = zipfile.ZipFile(join(file_path, "zipfile" + str(batch_num) + ".zip"), "w")
    for (path, dir, files) in os.walk(file_path):
        for file in files:
            zip_file.write(os.path.join(os.path.relpath(path, file_path), file),compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    sleep(1)

    # send to server
    _id = " "           # server ID
    password = " "       # server password
    zfile = os.path.join(file_path, "zipfile" + str(batch_num) + ".zip")
    self.job.stampNum += 1
    cmd = f'sshpass -p "{password}" scp -o StrictHostKeyChecking=no {zfile} {_id}:/data/VFP/dataset_dir/result/{rasp_num}'
    zresult = subprocess.run(cmd, shell=True, text=True, check=True)
    print(zresult.returncode)

    # remove all file

     




for batch in range(4): 
    for set in range(28):
        # repeat 3 times for monitored commands -> call shell script for monitored record
        for mon_repeat in range(3): 
            os.system('bash record_mon.sh')
            #rename all file 
            file_rename(1)
        # repeat 1 time for unmonitored commands-> call shell script for unmonitored record
        os.system('bash record_unmon.sh')
        #rename all file 
        file_rename(0)
    # make zip file & send to server -> remove all file in raspberry pi
    do_send_server(batch)
