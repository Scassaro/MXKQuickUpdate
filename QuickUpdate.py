import time
import telnetlib
import paramiko
import sys

def telnetToMXKAndLogin():
    
    MXKTelnet = telnetlib.Telnet(input("Enter the IP of your device: "))
    MXKTelnet.read_until(b"login:")
    MXKTelnet.write(b"admin\r")
    MXKTelnet.read_until(b"password:")
    MXKTelnet.write(b"zhone\r")
    return MXKTelnet

def findBins(MXKTelnet):

    MXKTelnet.read_until(b"zSH>")
    MXKTelnet.write(b"dir\r")
    time.sleep(1)
    DirString = MXKTelnet.read_very_eager().decode('ascii')
    DirArray = DirString.split()
    BinArray = []
    for i in range(len(DirArray) - 1):
        if ((DirArray[i].find(".bin") > -1) & (DirArray[i].find(".bin_") < 0) & (DirArray[i].find(".bin.") < 0)):
            BinArray.append(DirArray[i])
    return BinArray

#def sshToRTLUtil():
    
    #ssh = paramiko.SSHClient()
    #ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #ssh.connect('10.57.99.101', '22', 'mhiggins', 'zhone123')
    #return ssh

def fileDownload(MXKTelnet, BinArray):

    MXKTelnet.write(b"\r")
    time.sleep(1)
    MXKTelnet.read_until(b"zSH>")
    VersionNumber = input("What version do you want to upgrade to?: ")
    #RTLUtilSSH = sshToRTLUtil()
    RTLUtilSSH = paramiko.SSHClient()
    RTLUtilSSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    RTLUtilSSH.connect('10.57.99.101', '22', 'mhiggins', 'zhone123')
    FlashString = ""
    for i in range(len(BinArray)):
        if(BinArray[i].find("mxup") != -1 and BinArray[i].find("raw.bin") != -1):
            FlashString = "image flash /card1/" + BinArray[i] + " 1"
            FlashStringAll = FlashString + " all"
        FileDownloadString = "image download 10.57.99.101 /release/MXK_" + VersionNumber
        GetPathSSHCommand = "cd /data/release/MXK_" + VersionNumber + "; find | grep "
        stdin,stdout,stderr = RTLUtilSSH.exec_command(GetPathSSHCommand + BinArray[i])
        FilePath = stdout.readlines()
        FilePathResponse = ''.join(FilePath)
        FileDownloadString += FilePathResponse[1:].strip(('\n\r')) + " /card1/" + BinArray[i] + "\r"
        if(len(FileDownloadString) > 80):
            #DownloadBytes = FileDownloadString.encode('ascii')
            MXKTelnet.write(FileDownloadString.encode('ascii'))
            MXKTelnet.read_until(b"zSH>")
    if(FlashString != ""):
        #print("flashing")
        MXKTelnet.write(FlashStringAll.encode('ascii'))
        MXKTelnet.write(FlashString.encode('ascii'))
    return
    
def main():
    
    MXKTelnet = telnetToMXKAndLogin()
    Reboot = input("Would you like to reboot after download (y/n)?: ")
    BinArray = findBins(MXKTelnet)
    if(BinArray == []):
        print("No bin files found for this load. You may have typed the new version wrong. Please try again.")
    else:
        fileDownload(MXKTelnet, BinArray)
    if(Reboot == "y"):
        MXKTelnet.write(b"systemreboot\r")
        time.sleep(1)
        MXKTelnet.write(b"y\r")
        time.sleep(1)
        MXKTelnet.write(b"n\r")
        time.sleep(1)
        MXKTelnet.write(b"y\r")
        time.sleep(1)
    MXKTelnet.write(b"exit\r")
    MXKTelnet.close()
             
main()
