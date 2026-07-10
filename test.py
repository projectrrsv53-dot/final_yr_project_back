from transformers import AutoModel

print("loading wavlm")

model = AutoModel.from_pretrained(
    "microsoft/wavlm-base"
)

print("success")