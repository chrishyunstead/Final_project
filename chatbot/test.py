# import requests
#
# url = "https://09de-34-87-129-31.ngrok-free.app/query"
# payload = {"query": "풋살에 대해서 알려줘"}
# headers = {"Content-Type": "application/json"}
# response = requests.post(url, json=payload, headers=headers)
# print(response.json())

import requests

url = "http://43.200.89.250:8001/query"
payload = {"query": "풋살에 대해서 알려줘"}
headers = {"Content-Type": "application/json"}
response = requests.post(url, json=payload, headers=headers)
print(response.json())
