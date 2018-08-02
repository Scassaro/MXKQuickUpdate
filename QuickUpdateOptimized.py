import telnetlib
import paramiko
import time

# Collect IP of MXK here and create telnet session
MXKTelnet = telnetlib.Telnet(input("Enter the IP of your device: "))
VersionNumber = input("What version do you want to upgrade to?: ")
MXKTelnet.read_until(b"login:")
MXKTelnet.write(b"admin\n")
MXKTelnet.read_until(b"password:")
MXKTelnet.write(b"zhone\n")
MXKTelnet.read_until(b"zSH>")
MXKTelnet.write(b"dir\r")

# The whole newline ("\n") vs carriage return ("\r") when sending the MXK commands is annoying, confusing, and not standard across any command. 
# If you're getting back junk or nothing at all, I just blast it with "\n\r" and that usually works.

time.sleep(1)

# This command reads the results of the dir command to determine what binaries are in your system.
# The .split() command breaks it up into an array for easier processing.
DirArray = (MXKTelnet.read_very_eager().decode('ascii')).split()

# Create SSH session for going to RTLUtil01 to get binaries.
RTLUtilSSH = paramiko.SSHClient()

# Dunno what this means, everyone on StackOverflow says its necessary or your SSH will get blocked.
RTLUtilSSH.set_missing_host_key_policy(paramiko.AutoAddPolicy())
RTLUtilSSH.connect('10.57.99.101', '22', 'mhiggins', 'zhone123')

FlashString = ""
for i in range(len(DirArray) - 1):

    # Basically I split the "dir" command into an array where every word is an array object.
    # Now I go through the array to find binaries, but not peoples special ones (.bin.backup or anything like that).
    # The last conditional catches any included ROM files. Possibly could kill a system in the ROM isn't ready to deploy.
    if ((DirArray[i].find(".bin") > -1) & (DirArray[i].find(".bin_") < 0) & (DirArray[i].find(".bin.") < 0) & (DirArray[i].find("rom.bin") < 0)):

        # Here's the hard part, a bit of background is that I found a daemon that Mike made that downloads every release build to RTLUtil01.
        # Basically it goes into RTLUtil01, "cd"s into whatever version number the user provides, and I save the LOCATION of the binary in there.
        stdin,stdout,stderr = RTLUtilSSH.exec_command("cd /data/release/MXK_" + VersionNumber + "; find | grep " + DirArray[i])
        FilePathResponse = ''.join(stdout.readlines())
        
        # Now I combine everything into a File Download command. There is some string manipulation required ([1:] is called slicing, its amazing for this kind of stuff).
        FileDownloadString = "image download 10.57.99.101 /release/MXK_" + VersionNumber + FilePathResponse[1:].strip(('\n\r')) + " /card1/" + DirArray[i] + "\r"

        # This is my hack to get around finding binaries in the MXK that don't exist on RTLUtil01.
        if(len(FileDownloadString) > 80):
            print(FileDownloadString)
            MXKTelnet.write(FileDownloadString.encode('ascii'))
            MXKTelnet.read_until(b"zSH>")

        # This is how I flash raw files. Still not 100% sure it works but close enough.
        if(DirArray[i].find("mxup") > -1 and DirArray[i].find("raw.bin") > -1):
            FlashString = "image flash /card1/" + DirArray[i] + " 1 all\r"
if(FlashString != ""):
    MXKTelnet.write(FlashString.encode('ascii'))
    time.sleep(2)
    MXKTelnet.write(b"yes\r")
    MXKTelnet.read_until(b"zSH>")
    print(FlashString)
time.sleep(1)
MXKTelnet.write(b"systemreboot\r\n")
time.sleep(1)
MXKTelnet.write(b"yes\r\n")
time.sleep(1)
MXKTelnet.write(b"no\r\n")
time.sleep(1)
MXKTelnet.write(b"yes\r\n")
time.sleep(1)
MXKTelnet.write(b"exit\r\n")
RTLUtilSSH.close()
MXKTelnet.close()
