import math,random
def generateOTP():
    digits = "123456789123456789"
    OTP = ""
    for i in range(6):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP