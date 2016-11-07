import IPAddressConverter

# minBin = ipToBin("208.65.153.0", 24)
# multipleOriginASCheck(minBin, 24, "17557", validPrefixesDict)
def multipleOriginASCheck(checkIP, prefixLength, originAS, validIPPrefixes):
     #checkIPBinをどんどん右から削っていき、これと一致するIPプリフィックスが辞書にあるか
    #同一のプリフィックスは他にあるか
    checkIPBin = IPAddressConverter.ipToBin(checkIP, prefixLength)
    if checkIP in validIPPrefixes:
        if validIPPrefixes[checkIP]["originAS"] != originAS: #オリジンASが違う!!
            #print("MOAS")
            if validIPPrefixes[checkIP]["prefixLength"] <= prefixLength: #プリフィックス値が大きい
                print("%s/%d of AS %s is Dangerousness of Hijacking of AS%s" % (checkIP, prefixLength, originAS, validIPPrefixes[checkIP]["originAS"]))
                return checkIP
            else: #同じオリジンASによるアナウンス(正常)
                return False
                #print("Valid Announce by Same Origin AS")
    #このプリフィックスを包含するプリフィックスはあるか
    for i in reversed(range(prefixLength)):#prefixLength = 24なら、23ビット目から
        if checkIPBin[i] == "1":
            inclusionIPBin = checkIPBin[:i] + "0" * (32 - i)
            inclusionIP = IPAddressConverter.binToIP(inclusionIPBin)
            #print(inclusionIP)
            if inclusionIP in validIPPrefixes:
                if validIPPrefixes[inclusionIP]["originAS"] != originAS: #オリジンASが違う!!
                    #print("MOAS")
                    if validIPPrefixes[inclusionIP]["prefixLength"] <= i:  # プリフィックス値が大きい
                        print("%s/%d of AS %s is Conflicting with %s/%d of AS" % (checkIP, prefixLength, originAS, inclusionIP, validIPPrefixes[inclusionIP]["prefixLength"]), validIPPrefixes[inclusionIP]["originAS"])
                        return inclusionIP
                else:  # 同じオリジンASによるアナウンス(正常)
                    return False
                    #print("Valid Announce by Same Origin AS")
        else:
            inclusionIPBin = checkIPBin[:i] + "0" * (32 - i)
            inclusionIP = IPAddressConverter.binToIP(inclusionIPBin)
            #print(inclusionIP)
            if inclusionIP in validIPPrefixes:
                if validIPPrefixes[inclusionIP]["originAS"] != originAS:  # オリジンASが違う!!
                    #print("MOAS")
                    if validIPPrefixes[inclusionIP]["prefixLength"] <= i:  # プリフィックス値が大きい
                        print("%s/%d of AS %s is Conflicting with %s/%d of AS" % (checkIP, prefixLength, originAS, inclusionIP, validIPPrefixes[inclusionIP]["prefixLength"]), validIPPrefixes[inclusionIP]["originAS"])
                        return inclusionIP
                else:  # 同じオリジンASによるアナウンス(正常)
                    return False
                    #print("Valid Announce by Same Origin AS")