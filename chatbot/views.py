import asyncio
import json

import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from my_settings import HUGGINGFACE_TOKEN

# # GGUF 모델 로드
# model_name = "Dongwookss/small_fut_final"
# token = HUGGINGFACE_TOKEN
# tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=token)
# model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=token)


# # 챗봇 응답 생성 함수
# def generate_response(input_text):
#     print(f"Generating response for input: {input_text}")  # 디버그 로그 추가
#     try:
#         inputs = tokenizer.encode(input_text, return_tensors="pt")
#         attention_mask = inputs.ne(tokenizer.pad_token_id).long()
#         outputs = model.generate(
#             inputs,
#             attention_mask=attention_mask,
#             max_length=100,
#             num_return_sequences=1,
#             pad_token_id=tokenizer.eos_token_id,
#         )
#         response = tokenizer.decode(outputs[0], skip_special_tokens=True)
#         print(f"Generated response: {response}")  # 디버그 로그 추가
#         return response
#     except Exception as e:
#         print(f"Error during response generation: {str(e)}")  # 에러 로그 추가
#         return "Error during response generation"
#
#
# # 챗봇 뷰
# def chatbot_view(request):
#     if request.method == "POST":
#         try:
#             import json
#
#             body_unicode = request.body.decode("utf-8")
#             print(f"Body Unicode: {body_unicode}")  # 디버그 로그 추가
#             body_data = json.loads(body_unicode)
#             print(f"Body Data: {body_data}")  # 디버그 로그 추가
#             input_text = body_data.get("input_text", "")
#             print(f"Input Text: {input_text}")  # 디버그 로그 추가
#             if not input_text:
#                 return JsonResponse({"error": "No input text provided"}, status=400)
#
#             response_text = generate_response(input_text)
#             print(f"Response Text: {response_text}")  # 디버그 로그 추가
#             return JsonResponse({"response": response_text})
#         except Exception as e:
#             import traceback
#
#             traceback.print_exc()
#             return JsonResponse({"error": str(e)}, status=400)
#     return render(request, "chatbot.html")


# # 챗봇 응답 생성 함수 (비동기)
# async def generate_response(input_text):
#     print(f"Generating response for input: {input_text}")
#     try:
#         inputs = tokenizer.encode(input_text, return_tensors="pt").to("cpu")
#         attention_mask = inputs.ne(tokenizer.pad_token_id).long().to("cpu")
#
#         outputs = await asyncio.to_thread(
#             model.generate,
#             inputs,
#             attention_mask=attention_mask,
#             max_length=100,
#             num_return_sequences=1,
#             pad_token_id=tokenizer.eos_token_id,
#         )
#
#         response = tokenizer.decode(outputs[0], skip_special_tokens=True)
#         print(f"Generated response: {response}")
#         return response
#     except Exception as e:
#         print(f"Error during response generation: {str(e)}")
#         return "Error during response generation"
#
#
# # 비동기 뷰
# @csrf_exempt
# async def chatbot_view(request):
#     if request.method == "POST":
#         try:
#             body_unicode = request.body.decode("utf-8")
#             print(f"Body Unicode: {body_unicode}")
#             body_data = json.loads(body_unicode)
#             print(f"Body Data: {body_data}")
#             input_text = body_data.get("input_text", "")
#             print(f"Input Text: {input_text}")
#             if not input_text:
#                 return JsonResponse({"error": "No input text provided"}, status=400)
#
#             response_text = await generate_response(input_text)
#             print(f"Response Text: {response_text}")
#             return JsonResponse({"response": response_text})
#         except Exception as e:
#             import traceback
#
#             traceback.print_exc()
#             return JsonResponse({"error": str(e)}, status=400)
#     return render(request, "chatbot.html")


def get_model_response(input_text):
    url = "http://127.0.0.1:8000/generate"  # FastAPI 서버의 IP 주소와 포트 사용
    headers = {"Content-Type": "application/json"}
    data = {"input_text": input_text}

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json().get("response")
    else:
        return "Error: Unable to get response"


def chatbot_view(request):
    if request.method == "POST":
        input_text = request.POST.get("input_text")
        response_text = get_model_response(input_text)
        return JsonResponse({"response": response_text})
    return render(request, "chatbot.html")
