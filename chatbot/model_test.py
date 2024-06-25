from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers import TextStreamer
import os
import torch

# GGUF 모델 로드
model_name = "Dongwookss/small_fut_final"
token = "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"  # 직접 토큰 입력


def load_model():
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=token)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        # model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=token)
        print("Model and tokenizer loaded successfully.")
        return model, tokenizer
    except Exception as e:
        print(f"Error during model loading: {str(e)}")
        return None, None


def set_p(input_text):

    PROMPT = """Below is an instruction that describes a task. Write a response that appropriately completes the request.
    제시하는 context에서만 대답하고 context에 없는 내용은 모르겠다고 대답해\
                 \n context : '아디오스 팀은 8명으로 구성되어있다. \n팀 안에 영상부서, 챗봇부서, 개발자부서가 있으며 총괄 팀장으로 서한울이 있어.\
                 \n 각 부서의 팀장으로 영상부서 팀장은 김성일, 챗봇부서 팀장은 신대근, 개발자부서 팀장은 정현수야. \
                 \n영상 부서에는 김성일,손명준,임경란이 있고, 개발자부서에는 정현수,서한울이 있어. \
                 \n챗봇부서에는 강동욱,강민지,신대근이 있고 풋풋이라는 제품을 만들고있어.
    """
    instruction = input_text
    # "아디오스 팀의 팀장이 누구야? 그리고 각 부서의 팀장은 누구야? 풋풋이 만드는 부서는? 그 부서에 포함된 사람은? 김성일이 어느 부서 팀장이야?"

    messages = [
        {"role": "system", "content": f"{PROMPT}"},
        {"role": "user", "content": f"{instruction}"},
    ]

    input_ids = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    return input_ids


# def generate_response(model, tokenizer, input_ids):
#     try:
#         # inputs = tokenizer.encode(input_text, return_tensors="pt")
#         # attention_mask = inputs.ne(tokenizer.pad_token_id).long()
#         print("Inputs and attention mask prepared.")  # 디버그 로그 추가
#
#         terminators = [
#             tokenizer.eos_token_id,
#             tokenizer.convert_tokens_to_ids("<|eot_id|>"),
#         ]
#
#         text_streamer = TextStreamer(tokenizer)
#
#         outputs = model.generate(
#             input_ids,
#             max_new_tokens=4096,
#             eos_token_id=terminators,
#             do_sample=True,
#             streamer=text_streamer,
#             temperature=0.6,
#             top_p=0.9,
#             repetition_penalty=1.1,
#             # inputs,
#             # attention_mask=attention_mask,
#             # max_length=100,
#             # num_return_sequences=1,
#             # pad_token_id=tokenizer.eos_token_id,
#             # do_sample=True,  # 샘플링을 활성화하여 실행 시간 단축
#             # temperature=0.7,  # 출력의 다양성을 제어
#         )
#         print("Model output generated.")  # 디버그 로그 추가
#
#         # response = tokenizer.decode(outputs[0], skip_special_tokens=True)
#         print(f"Generated response: {response}")
#         return outputs
#     except Exception as e:
#         print(f"Error during response generation: {str(e)}")
#         return "Error during response generation"


# 테스트
model, tokenizer = load_model()
if model and tokenizer:
    input_text = "아디오스팀의 챗봇부서에는 누구누구가 있어?"
    input_prompt = set_p(input_text)
    # response = generate_response(model, tokenizer, input_prompt)
    # print(f"Response: {response}")
    attention_mask = input_prompt.ne(tokenizer.pad_token_id).long()
    terminators = [
        tokenizer.eos_token_id,
        tokenizer.convert_tokens_to_ids("<|eot_id|>"),
    ]

    text_streamer = TextStreamer(tokenizer)
    _ = model.generate(
        input_prompt,
        max_new_tokens=4096,
        eos_token_id=terminators,
        do_sample=True,
        # max_length=50,
        num_return_sequences=1,
        streamer=text_streamer,
        temperature=0.7,
        attention_mask=attention_mask,
        top_k=50,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id,
        repetition_penalty=1.1,
    )
