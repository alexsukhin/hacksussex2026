import requests

token = "8649843600:AAHgRy24e0TpCCMT6HkMGDijhPTjm4RIBS4"
chatID = "8717180588"
messageBody = "Hello World"

url =  f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chatID}&text={messageBody}"
r = requests.get(url)
print(r)

#https://api.telegram.org/bot8649843600:AAHgRy24e0TpCCMT6HkMGDijhPTjm4RIBS4/getUpdates