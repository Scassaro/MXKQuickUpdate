import telnetlib
import paramiko
import time
MXKTelnet = telnetlib.Telnet(input("Enter the IP of your device: "))
VersionNumber = input("What version do you want to upgrade to?: ")
MXKTelnet.read_until(b"login:")
MXKTelnet.write(b"admin\n")
MXKTelnet.read_until(b"password:")
MXKTelnet.write(b"zhone\n")
MXKTelnet.read_until(b"zSH>")
MXKTelnet.write(b"dir\r")
time.sleep(1)
DirArray = (MXKTelnet.read_very_eager().decode('ascii')).split()
RTLUtilSSH = paramiko.SSHClient()
RTLUtilSSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
RTLUtilSSH.connect('10.57.99.101', '22', 'mhiggins', 'zhone123')
FlashString = ""
for i in range(len(DirArray) - 1):
    if ((DirArray[i].find(".bin") > -1) & (DirArray[i].find(".bin_") < 0) & (DirArray[i].find(".bin.") < 0) & (DirArray[i].find("rom.bin") < 0)):
        stdin,stdout,stderr = RTLUtilSSH.exec_command("cd /data/release/MXK_" + VersionNumber + "; find | grep " + DirArray[i])
        FilePathResponse = ''.join(stdout.readlines())
        FileDownloadString = "image download 10.57.99.101 /release/MXK_" + VersionNumber + FilePathResponse[1:].strip(('\n\r')) + " /card1/" + DirArray[i] + "\r"
        if(len(FileDownloadString) > 80):
            print(FileDownloadString)
            MXKTelnet.write(FileDownloadString.encode('ascii'))
            MXKTelnet.read_until(b"zSH>")
        if(DirArray[i].find("mxup") > -1 and DirArray[i].find("raw.bin") > -1):
            FlashString = "image flash /card1/mxup2tg8graw.bin 1 all\r"
if(FlashString != ""):
    MXKTelnet.write(FlashString.encode('ascii'))
    print(FlashString)
MXKTelnet.write(b"exit\r")
RTLUtilSSH.close()
MXKTelnet.close()
