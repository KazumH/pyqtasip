def ipToBin(ip, prefixLength): # ip = "208.65.152.0", prefixLength = 22
    splittedIp = ip.split(".")
    minIPNum = 256 ** 3 * int(splittedIp[0]) + 256 ** 2 * int(splittedIp[1]) + 256 ** 1 * int(splittedIp[2]) + int(splittedIp[3])
    maxIPNum = minIPNum + (2 ** (32 - prefixLength) - 1)
    minIPBin = bin(minIPNum)
    maxIPBin = bin(maxIPNum)
    if len(minIPBin) < 34:
        headZeroes = "0" * (34 - len(minIPBin)) #"00"
        minIPBin = headZeroes + minIPBin[2:len(minIPBin)]
        binMaxIP = headZeroes + maxIPBin[2:len(maxIPBin)]
    else:
        minIPBin = minIPBin[2:len(minIPBin)]#'1101000001000001100110/0000000000'
        maxIPBin = maxIPBin[2:len(maxIPBin)]
    return minIPBin #32ビット

#バイナリ形式32ビットの値をIPアドレス表記へ
def binToIP(bin): #'11010000010000011001100000000000'
    firstOctet = int(bin[0:8], 2)
    secondOctet = int(bin[8:16], 2)
    thirdOctet = int(bin[16:24], 2)
    fourthOctet = int(bin[24:32], 2)
    ip = str(firstOctet) + "." + str(secondOctet) + "." + str(thirdOctet) + "." + str(fourthOctet)
    return ip #'208.65.152.0'