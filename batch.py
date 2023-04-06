import subprocess
from os.path import join, split, getsize
from os import remove
from time import sleep
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
rasp_num="rasp1"    # rasberry pi num 설정해주세요


def file_rename(data_type):
    folder_path = result_dir    # result file path in local
    #file_list = os.listdir(folder_path)
    if data_type==1:    # monitored
        for file_name in range(1,101):
            try:
                old_file_name = str(file_name) + ".pcap"
                new_file_name = str(file_name) + "_" + str(instance) + "_" + rasp_num + ".pcap"    ######################################이거 instance $3d로 됤 수 있게 수정
                os.rename(old_file_name, new_file_name)
                old_wav_name = str(file_name) + ".wav"
                new_wav_name = str(file_name) + "_" + str(instance) + "_" + rasp_num + ".wav"
                os.rename(old_wav_name, new_wav_name)
            except:
                print("fail to change " + str(file_name))
    
    elif data_type==0:   # unmonitored
        for file_name in range(301,351):
            try:
                old_file_name = str(file_name) + ".pcap"
                new_file_name = str(file_name) + "_" + str(instance) + "_" + rasp_num + ".pcap"
                os.rename(old_file_name, new_file_name)
                old_wav_name = str(file_name) + ".wav"
                new_wav_name = str(file_name) + "_" + str(instance) + "_" + rasp_num + ".wav"
                os.rename(old_wav_name, new_wav_name)
            except:
                print("fail to change " + str(file_name))
    instance+=1


def do_send_server(batch_num):
    ''' make zip file '''
    file_path = result_dir
    owd = os.getcwd()
    os.chdir(file_path)
    zip_file = zipfile.ZipFile(join(file_path, "zipfile" + str(batch_num) + ".zip"), "w")
    for (path, dir, files) in os.walk(file_path):
        for file in files:
            zip_file.write(os.path.join(os.path.relpath(path, file_path), file),compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()
    sleep(1)

    ''' send to server '''
    _id = " "           # server ID     ############!!!!!!!!서버 아이디&비밀번호 github에 올리지 않게 주의!!!!!!!!############
    password = " "       # server password
    zfile = os.path.join(file_path, "zipfile" + str(batch_num) + ".zip")
    self.job.stampNum += 1
    cmd = f'sshpass -p "{password}" scp -o StrictHostKeyChecking=no {zfile} {_id}:/data/VFP/dataset_dir/result/{rasp_num}'  # 이 주소는 server 주소로 바꿔야해요
    zresult = subprocess.run(cmd, shell=True, text=True, check=True)
    print(zresult.returncode)

    ''' remove all file '''
    for files in os.listdir(file_path):
        path = os.path.join(file_path, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)
    os.chdir(owd)


for batch in range(4): 
    for set in range(28):
        ''' repeat 3 times for monitored commands -> call shell script for monitored record & rename all file '''
        for mon_repeat in range(3): 
            #os.system('bash record_mon.sh')
            cmd = 'bash record_mon.sh'
            zresult = subprocess.run(cmd, shell=True, text=True, check=True)
            file_rename(1)

        ''' repeat 1 time for unmonitored commands-> call shell script for unmonitored record & rename all file '''
        #os.system('bash record_unmon.sh')
        cmd = 'bash record_unmon.sh'
        zresult = subprocess.run(cmd, shell=True, text=True, check=True)
        file_rename(0)

    ''' make zip file & send to server -> remove all file in raspberry pi '''
    do_send_server(batch)
