#!/bin/bash

trap "clean_exit" SIGINT
clean_exit() {
  echo -e "\nStopping capture and exiting safely\n"
  sudo pkill -2 tcpdump
  exit 1
}

rasp_num=1

#voices=(what_do_you_know_about_sports whats_the_high_today whats_the_price_of_bitcoin when_did_Snapchat_go_public)  #617로 변경 -> 1~617까지 돌게
voices=618


# Prompt for data directory paths (이거는 local 주소로 바꿔야해요)
datadirname="/data/VFP/dataset_dir/commands"
dataset_dir=$datadirname
commanddirname="/data/VFP/dataset_dir/commands/input/unmonitored"
command_dir=$commanddirname
wakeworddirname="/data/VFP/dataset_dir/commands/wake_words"
wake_word_dir=$wakeworddirname
resultdirname="/data/VFP/dataset_dir/result"
result_dir=$resultdirname

PS3="Select the command&wakeword subdirectory to use"
command_subdirs=$command_dir/*
wake_word_file=$wake_word_dir/*



# For each voice
for voice in ${voices}; do
  # For each command subdirectory
  for result_dir in ${result_dir[@]}; do
    sudo rm "$result_dir/${voice}_out"* # Delete stale output files of current voice in current command subdirectory
    variant=1 # Reset voice variant counter of current voice

    # For each variant file of current voice in current command subdirectory
    for variant_file in $command_subdir/${voice}; do
      # Start the capture
      echo -e "\nCapturing $command_subdir/${voice}$(printf '%03d' $variant).pcap\n"
      sudo tcpdump -U -i wlan0 -w $command_subdir/${voice}_$(printf "%03d" $variant)_${rasp_num}.pcap &
      paplay $wake_word_file
      variant_file=${variant_file}.wav
      paplay $variant_file

      # If the capture times out (no response heard after 60 seconds), then redo the capture
      while ! timeout --foreground 60s sox -d $command_subdir/${voice}_$(printf "%03d" $variant)_${rasp_num}.wav silence 1 0.1 5% 1 3.0 5%; do
        echo -e "while"
        # Clean up from failed capture
        sudo pkill -2 tcpdump
        sudo rm "$result_dir/${voice}$(printf "%03d" $variant)"*

        # Start the redo capture
        echo -e "\nCapturing $command_subdir/${voice}$(printf '%03d' $variant).pcap\n"
        sudo tcpdump -U -i wlan0 -w $command_subdir/${voice}_$(printf "%03d" $variant)_${rasp_num}.pcap &
        paplay $wake_word_file
        paplay $variant_file
      done

      sleep 2
      sudo pkill -2 tcpdump
      ((variant++))
    done

    sudo chown $USER:$USER "$command_subdir/"* # Fix ownership of files
  done
 ({voice++})
done