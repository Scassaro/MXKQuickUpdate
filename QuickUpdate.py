import time
import telnetlib

def telnetToMXKAndLogin():
    
    host = input("Enter the IP of your device: ")
    tn = telnetlib.Telnet(host)
    tn.read_until(b"login:")
    tn.write(b"admin\r")
    tn.read_until(b"password:")
    tn.write(b"zhone\r")
    return tn

def findBins(tn):

    tn.read_until(b"zSH>")
    tn.write(b"dir\r")
    time.sleep(1)
    DirString = tn.read_very_eager().decode('ascii')
    DirArray = DirString.split()
    BinArray = []
    for i in range(len(DirArray) - 1):
        if ((DirArray[i].find(".bin") > -1) & (DirArray[i].find(".bin_") < 0) & (DirArray[i].find(".bin.") < 0)):
            BinArray.append(DirArray[i])
    return BinArray

def fileDownload(tn, BinArray):

    tn.write(b"\r")
    time.sleep(1)
    tn.read_until(b"zSH>")
    versionNumber = input("What version do you want to upgrade to?: ")
    for i in range(len(BinArray) - 1):
        CamelCaseTempString = versionNumber + "/mxk"
        if(len(BinArray[i]) == 9):
            CamelCaseTempString += "Mc/"
        elif(len(BinArray[i]) == 10):
            CamelCaseTempString += "ROM/"
        elif(len(BinArray[i]) == 12):
            CamelCaseTempString += "McROM/"
        elif(len(BinArray[i]) == 13):
            CamelCaseTempString += "LcAeTg/"
        elif(BinArray[i][3] == "f"):
            CamelCaseTempString += "FcAe/"
        elif(BinArray[i][5] == "g"):
            CamelCaseTempString += "LcGp/"
        else:
            CamelCaseTempString += "LcAe/"
        WriteString = "image download 10.57.99.101 /release/MXK_" + CamelCaseTempString + BinArray[i] + " /card1/" + BinArray[i] + "\r"
        WriteBytes = WriteString.encode('ascii')
        print(WriteBytes)
        tn.write(WriteBytes)
        tn.read_until(b"zSH>")
    return
    
def main():
    
    tn = telnetToMXKAndLogin()
    Reboot = input("Would you like to reboot after download (y/n)?: ")
    BinArray = findBins(tn)
    fileDownload(tn, BinArray)
    if(Reboot == "y"):
        tn.write(b"systemreboot\r")
        time.sleep(1)
        tn.write(b"y\r")
        time.sleep(1)
        tn.write(b"n\r")
        time.sleep(1)
        tn.write(b"y\r")
        time.sleep(1)
    tn.write(b"exit\r")
    tn.close()
             
main()
