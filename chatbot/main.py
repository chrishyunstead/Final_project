# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
#
#
# app = FastAPI()
#
# model_name = "Dongwookss/small_fut_final"
# token = "hf_ZgYdnpMTuDbzFXNHH0gSKCEPuQccrJjrqQWa"  # 직접 토큰 입력
#
# device = "cuda" if torch.cuda.is_available() else "cpu"
#
# tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=token)
# model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=token).to(
#     device
# )
#
#
# class InputText(BaseModel):
#     input_text: str
#
#
# @app.post("/generate")
# async def generate(input_text: InputText):
#     print(f"Received request with input_text: {input_text.input_text}")
#     inputs = tokenizer.encode(input_text.input_text, return_tensors="pt").to(device)
#     attention_mask = inputs.ne(tokenizer.pad_token_id).long().to(device)
#
#     print("Generating response...")
#     outputs = model.generate(
#         inputs,
#         attention_mask=attention_mask,
#         max_length=100,
#         num_return_sequences=1,
#         pad_token_id=tokenizer.eos_token_id,
#         do_sample=True,
#         temperature=0.7,
#         top_k=50,
#         top_p=0.9,
#     )
#
#     response = tokenizer.decode(outputs[0], skip_special_tokens=True)
#     print(f"Generated response: {response}")
#     return {"response": response}
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)
