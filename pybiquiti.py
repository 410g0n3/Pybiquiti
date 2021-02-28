# Small ISP tool to automate Ubiquiti device configurations
# Autor: Vicente M - 410.g0n3
# Acknowledgment : https://twitter.com/fr33project

# Import libraries
import paramiko
import time
import sys
import subprocess
import os
from getpass import getpass
from io import open
import argparse

# Arguments to ssh connection
parse = argparse.ArgumentParser()
parse.add_argument("-H", "--host", help="IP del dispositivo a conectar")
parse.add_argument("-p", "--port", help="Puerto del dispositivo a conectar")
parse.add_argument("-u", "--user", help="Username para el inicio de sesión")
parse = parse.parse_args()

config_file = "WRITE HERE YOUR CONFIG FILE .TXT"

if __name__ == "__main__":
    
    
    # Open and read config file and parse it to array
    read_file = open (config_file,"r")
    config_ant = read_file.readlines()

    print("Write the PPPoE secret")
    secret=input()

    print("Write your SSID repeater")
    repeater = input()

    print("Write your device name")
    device_name = input()

    # Modify array with input names
    config_ant[120] = "ppp.1.name="+secret+"\n"
    config_ant[164] = "resolv.host.1.name="+device_name+"\n"
    config_ant[178] = "wpasupplicant.profile.1.network.1.ssid="+repeater+"\n"
    config_ant[193] = "wireless.1.ssid="+repeater+"\n"

    # Create and write new file with new parameters
    new_file = open("system.cfg", "w")
    new_file.writelines(config_ant)

    # Close files
    new_file.close()
    read_file.close()

    # Send file via console with SCP
    subprocess.run('scp .\system.cfg ubnt@192.168.1.20:/tmp/', shell=True)

    try:
        # Start Paramiko connection
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        PASS = getpass('ubnt@192.168.1.20 password: ')
        client.connect(hostname=parse.host, port=parse.port, username=parse.user, password=PASS)
        
        # Execute save and reboot comand
        stdin, stdout, stderr = client.exec_command("cfgmtd -w -p /etc/ && reboot")

        time.sleep(1)
        result = stdout.read().decode()
        result_error = stderr.read().decode()
        
        # Print values
        print(result)
        print(result_error)

        print("Closing ssh connection...")
        client.close()

        # Deleting known hosts file, to avoid problems with id_rsa of the ssh connection
        username = os.getenrv('username')
        os.remove('c:/Users/'+username+'/.ssh/known_hosts')

    except paramiko.ssh_exception.AuthenticationException as e:
        print('Write correct password')
