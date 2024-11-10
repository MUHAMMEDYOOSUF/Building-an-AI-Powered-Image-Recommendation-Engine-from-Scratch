# test.py
from fastapi import FastAPI
from pydantic import BaseModel
from langchain_experimental.open_clip import OpenCLIPEmbeddings
import torch

app = FastAPI()
print("start model loading")
# Load the OpenCLIP model
device = torch.device("cpu")
try:
    embedding_model = OpenCLIPEmbeddings(
    model_name="coca_ViT-L-14",
    checkpoint="/home/yoosuf/.cache/huggingface/hub/models--laion--mscoco_finetuned_CoCa-ViT-L-14-laion2B-s13B-b90k/snapshots/f895105fb18cf5ea3ba7a1172966e4cc0ad8d743/open_clip_pytorch_model.bin",
    pretrained=True,
    device=device,
    gradient_checkpointing=True
)
except Exception as e:
    print("error::",str(e))
print("model loaded")
class TextInput(BaseModel):
    text: str

@app.get("/embed")
async def embed_text(input: TextInput):
    embedding = embedding_model.embed(input.text)  # Use the appropriate embedding method
    return {"embedding": embedding.tolist()}  # Convert to list for JSON serialization
