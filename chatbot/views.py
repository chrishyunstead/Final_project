import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse


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


# 이걸로
# def chat_view(request):
#     if request.method == "POST":
#         message = request.POST.get(
#             "message"
#         )  # 사용자의 질문을 받아옵니다.(질문형태 str일 경우)
#
#         # <AWS_EC2_PUBLIC_IP> : aws ip주소 적고
#         # 8000번은 fastapi 지정한 포트번호
#         response = requests.post(
#             "http://43.200.89.250:8001/query", data={"message": message}
#         )  # FastAPI 서버에 문자열 형태로 질문을 전송합니다.
#         return JsonResponse(
#             response.json()
#         )  # FastAPI 서버에서 받은 JSON 응답을 사용자에게 반환합니다.
#     return render(request, "chatbot.html")  # GET 요청인 경우, 챗봇 폼을 렌더링합니다.


def chatbot(request):
    message = ""
    response_data = {}
    chat_history = request.session.get("chat_history", [])

    if request.method == "POST":
        message = request.POST.get(
            "message"
        )  # 사용자의 질문을 받아옵니다.(질문형태 str일 경우)

        try:
            response = requests.post(
                "http://43.200.89.250:8080/query", json={"query": message}
            )  # FastAPI 서버에 JSON 형태로 질문을 전송합니다.
            response_data = response.json()  # JSON 응답을 파싱합니다.

            # 응답에서 "Answer:" 부분만 추출
            if "response" in response_data:
                answer_start = response_data["response"].split("Answer:")
                if len(answer_start) > 1:
                    response_data["response"] = answer_start[-1]
                else:
                    response_data["response"] = "답변을 찾을 수 없습니다."

            # 세션에 질문과 답변을 저장
            chat_history.append(
                {"question": message, "answer": response_data["response"]}
            )
            request.session["chat_history"] = chat_history
            request.session.modified = True

        except requests.exceptions.RequestException as e:
            response_data = {
                "error": str(e)
            }  # 요청이 실패한 경우 에러 메시지를 반환합니다.

    # 세션 데이터를 초기화하는 로직 추가
    elif request.method == "GET" and "reset" in request.GET:
        request.session["chat_history"] = []
        return redirect(
            "chatbot:chatbot"
        )  # 채팅 페이지로 리다이렉트하여 초기화된 상태를 보여줍니다.

    return render(
        request,
        "chatbot.html",
        {"response": response_data, "message": message, "chat_history": chat_history},
    )  # GET 또는 POST 요청인 경우, 챗봇 폼을 렌더링하고 응답을 전달합니다.


# import requests
# url = '주소:포트번호/query'
# payload = {'query': 사용자가 입력한 query를 str형태로 입력받아융}
# headers = {'Content-Type': 'application/json'}
# response = requests.post(url, json=payload, headers=headers)
# response.json() # 모델 응답 결과
