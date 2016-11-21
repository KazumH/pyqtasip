def timeAdd(inputTime, addendMin):
    inputDate = inputTime[:len(inputTime) - 4]
    inputMin = int(inputTime[len(inputTime) - 2:])  # 下2桁
    inputHour = int(inputTime[len(inputTime) - 4:len(inputTime) - 2])  # 下4桁〜下2桁
    min = inputMin + addendMin  # 時間繰り上げなしの分カウント
    hour = min // 60
    if min > 59:
        min = min % 60
    if min < 10:
        strMin = "0" + str(min)  # "00 ~ 09"
    else:
        strMin = str(min)  # "10 ~ 59"
    currentHour = inputHour + hour
    if currentHour < 10:
        strHour = "0" + str(currentHour)  # "00 ~ 09"
    else:
        strHour = str(currentHour)  # "10 ~ 23"
    result = inputDate + strHour + strMin
    return result