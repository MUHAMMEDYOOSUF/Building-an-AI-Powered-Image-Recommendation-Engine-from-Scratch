import os
from PIL import Image
import torch
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
from langchain_chroma import Chroma
from langchain_experimental.open_clip import OpenCLIPEmbeddings
from transformers import BitsAndBytesConfig
from langchain_community.embeddings import HuggingFaceBgeEmbeddings

# Call the function to clear the CPU cache

class ImageSearch:
    def __init__(self, collection_name="img_collection", persist_directory="./image_simi_db", device='cuda'):
        
        device = torch.device("cpu")
        print("started loading embedding")
        try:
            self.embedding_model = OpenCLIPEmbeddings(
            model_name="coca_ViT-L-14",
            checkpoint="/home/yoosuf/.cache/huggingface/hub/models--laion--mscoco_finetuned_CoCa-ViT-L-14-laion2B-s13B-b90k/snapshots/f895105fb18cf5ea3ba7a1172966e4cc0ad8d743/open_clip_pytorch_model.bin",
            pretrained=True,
            device=device,
            gradient_checkpointing=True
        )
            # self.embedding_model = OpenCLIPEmbeddings(
            #     model_name="coca_ViT-B-32",
            #     checkpoint="/home/yoosuf/.cache/huggingface/hub/models--laion--mscoco_finetuned_CoCa-ViT-B-32-laion2B-s13B-b90k/snapshots/ef0732eb039c932624eb8b867c82ab2311001b09/open_clip_pytorch_model.bin",
            #     pretrained=True,
            #     device=device,
            #     gradient_checkpointing=True
            # )
        except Exception as e:
            print("error::",str(e))
        print("loaded embedding model")
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_model,
            persist_directory=persist_directory
        )
 
        

    def search_by_image(self, uri, k=5):
        similar_images=None
        try:
            similar_images = self.vector_store.similarity_search_by_image(uri=uri, k=k)
        except Exception as e:
            print(e)
        return self.get_images(similar_images)

    def search_by_query(self, query):
        # First retriever with similarity_score_threshold
        chroma_retreiver = self.vector_store.as_retriever(
            search_type="similarity_score_threshold", 
            search_kwargs={"k": 5, "score_threshold": 0.1}
        )
        similar_images = chroma_retreiver.invoke(query)
        
        # If no results, fallback to other methods
        if not similar_images:
            chroma_retreiver = self.vector_store.as_retriever(
                search_type="mmr", 
                search_kwargs={'k': 5, 'fetch_k': 50}
            )
            similar_images = chroma_retreiver.invoke(query)
        
        if not similar_images:
            chroma_retreiver = self.vector_store.as_retriever(
                search_type="mmr", 
                search_kwargs={'k': 5, 'lambda_mult': 0.25}
            )
            similar_images = chroma_retreiver.invoke(query)
        
        return self.get_images(similar_images)

    def base64_string_to_image(self, base64_string):
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data))

    def get_images(self, images):
        image_results = []
        for i in images:
            output_image = self.base64_string_to_image(i.page_content)
            meta_df = pd.DataFrame(i.metadata.items(), columns=['Spec', 'Values']).set_index('Spec')
            meta_df = meta_df.drop("ImageURL", errors='ignore')  # Exclude ImageURL
            image_results.append((output_image, meta_df))
        return image_results


# dd=ImageSearch()
