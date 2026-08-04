import os

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()


EMBEDDING_MODEL_NAME = "mixedbread-ai/mxbai-embed-large-v1"


def get_embedding_model() -> HuggingFaceEmbeddings:
    """
    Retorna o modelo responsável por gerar embeddings.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={
            "device": "cpu",
            "token": os.getenv("HF_TOKEN"),
        },
        encode_kwargs={"normalize_embeddings": True},
    )
