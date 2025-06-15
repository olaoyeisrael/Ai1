# from transformers import AutoTokenizer, AutoModel
# import torch

# # Load model & tokenizer
# model_name = "sentence-transformers/all-MiniLM-L6-v2"
# tokenizer = AutoTokenizer.from_pretrained(model_name)
# model = AutoModel.from_pretrained(model_name)

# def mean_pooling(model_output, attention_mask):
#     token_embeddings = model_output[0]
#     input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size())
#     return (token_embeddings * input_mask_expanded).sum(1) / input_mask_expanded.sum(1)

# def embed_chunks(texts: list[str]) -> list[list[float]]:
#     """Convert text chunks into dense vector embeddings"""
#     encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
#     with torch.no_grad():
#         model_output = model(**encoded_input)
#     pooled = mean_pooling(model_output, encoded_input['attention_mask'])
#     return pooled.tolist()

# def embed_query(query: str) -> list[float]:
#     return embed_chunks([query])[0]

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Your Together AI API Key
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# Together AI endpoint and model
TOGETHER_API_URL = "https://api.together.xyz/v1/embeddings"
TOGETHER_MODEL = "togethercomputer/m2-bert-80M-32k-retrieval"  # or replace with your preferred model


def embed_chunks(texts: list[str]) -> list[list[float]]:
    """
    Converts a list of text chunks into dense vector embeddings using Together AI API.
    """
    if not TOGETHER_API_KEY:
        raise EnvironmentError("TOGETHER_API_KEY not set in environment")

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": TOGETHER_MODEL,
        "input": texts
    }

    response = requests.post(TOGETHER_API_URL, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Embedding failed: {response.text}")

    return [item["embedding"] for item in response.json()["data"]]


def embed_query(query: str) -> list[float]:
    """
    Embeds a single query string and returns a single vector.
    """
    return embed_chunks([query])[0]