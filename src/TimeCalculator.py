def timeAdd(inputTime, addendMin):
    inputDate = inputTime[:len(inputTime) - 4]
    inputMin = int(inputTime[len(inputTime) - 2:])  # 下2桁
    inputHour = int(inputTime[len(inputTime) - 4:len(inputTime) - 2])  # 下4桁〜下2桁
    min = inputMin + addendMin  # 時間繰り上げなしの分カウント
    if min > 59:
        currentMin = min % 60
        if currentMin < 10:
            strMin = "0" + str(currentMin)  # "00 ~ 09"
        else:
            strMin = str(currentMin)  # "10 ~ 59"
    else:
        strMin = str(min)
    hour = min // 60
    currentHour = inputHour + hour
    strHour = str(currentHour)
    result = inputDate + strHour + strMin
    return result