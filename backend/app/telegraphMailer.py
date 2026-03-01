import requests
<<<<<<< HEAD
=======
#https://api.telegram.org/bot8649843600:AAHgRy24e0TpCCMT6HkMGDijhPTjm4RIBS4/getUpdates]#
>>>>>>> c66ee5c9336598f0f6a2b967331c356df91fe4ee

#token = "8649843600:AAHgRy24e0TpCCMT6HkMGDijhPTjm4RIBS4"
#chatID = "8717180588"
#messageBody = "Hello World"

url =  f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatID}&text={messageBody}"
r = requests.get(url)
print(r)


def sendUpdate():
    token = "8649843600:AAHgRy24e0TpCCMT6HkMGDijhPTjm4RIBS4"
    chatID = "8717180588"
    messageBody = "Hello World"
    url =  f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatID}&text={messageBody}"
    cropsWatered = True

    if cropsWatered:
        messageBody = '''
        **IRRIGATION UPDATE **
Hi, 
Your crops were watered.

_GreenField_
    
'''

    else:
        messageBody = '''**IRRIGATION UPDATE **
Hi, 
There has been no change to you crops. 

_GreenField_
    
'''

    url =  f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatID}&text={messageBody}"
    r = requests.get(url)
    print(r)

