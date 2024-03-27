#!/usr/bin/env python
import os
import json
import boto3
import time
from opensearchpy import OpenSearch
from shared.knowledge.knowledge_base import KnowledgeBase
from shared.knowledge.opensearch_retriever import CustomOpenSearchRetriever
from utils.constants import DEFAULT_OPENSEARCH_NUMBER_OF_DOCS, DEFAULT_RETURN_SOURCE_DOCS, OPENSEARCH_INDEX_ID_ENV_VAR
from utils.enum_types import KnowledgeBaseTypes
from langchain_community.vectorstores import OpenSearchVectorSearch 
from typing import Any, Dict, List, Optional, Sequence
from langchain_community.embeddings import SagemakerEndpointEmbeddings
from langchain_community.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from aws_lambda_powertools import Logger, Metrics, Tracer
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from opensearchpy import exceptions as opensearch_exceptions
from enum import Enum

logger = Logger(utc=True)
tracer = Tracer()


logger = Logger(utc=True)
OPENSEARCH_TIMEOUT = 30
OPENSEARCH_PORT = 443
OPENSEARCH_INDEX_ID_ENV_VAR = "OPENSEARCH_INDEX_ID"
OPENSEARCH_HOST_ENV_VAR = "OPENSEARCH_HOST"
OPENSEARCH_AUTH_ENV_VAR = "OPENSEARCH_AUTH"
OPENSEARCH_SECRET_NAME_ENV_VAR = "OPENSEARCH_SECRET_NAME_ENV_VAR"
OPENSEARCH_USE_SSL = True
OPENSEARCH_VERIFY_CERTIFICATES = True
SAGEMAKER_EMBEDDING_ENDPOINT = "SAGEMAKER_EMBEDDING_ENDPOINT"

# Function to retrieve the secret from AWS Secrets Manager
def get_secret(secret_name):
    
    client = boto3.client(service_name='secretsmanager')
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        logger.error(f"Error retrieving secret: {e}")
        raise e

    if 'SecretString' in get_secret_value_response:
        return json.loads(get_secret_value_response['SecretString'])
    else:
        raise Exception("Secret not in string format")
        
class ContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: List[str], model_kwargs: Dict) -> bytes:
        
        input_str = json.dumps({"text_inputs": inputs, "normalize": False})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        embeddings = response_json["embedding"]
        if isinstance(embeddings, list):
            if len(embeddings) == 1:
                return [embeddings[0]]
            return embeddings
        else:
            raise KeyError("'embedding' key not found in the JSON response.")
        
class OpenSearchKnowledgeBase(KnowledgeBase):
    """
    OpenSearchKnowledgeBase adds context to the LLM memory using OpenSearch.

    Attributes:

        index_name (str): OpenSearch index name
        number_of_docs (int): Number of documents to query for [Optional]
        retriever (CustomOpenSearchRetriever): Custom OpenSearch retriever

    Methods:
        get_relevant_documents(query): Run search on OpenSearch index and get top k documents.
    """

    knowledge_base_type: KnowledgeBaseTypes = KnowledgeBaseTypes.OpenSearch.value

    def __init__(
        self,
        opensearch_knowledge_base_params: Optional[Dict[str, Any]] = {},
    ) -> None:
        self._check_env_variables()
        
        OPENSEARCH_HOST = os.environ.get(OPENSEARCH_HOST_ENV_VAR)
        # Retrieve the secret name from the environment variable
        secret_name = os.environ.get(OPENSEARCH_SECRET_NAME_ENV_VAR)
        if secret_name:
            secret = get_secret(secret_name)
            OPENSEARCH_AUTH = (secret['username'], secret['password'])
        else:
            raise ValueError("OpenSearch secret name not provided in environment variables")

        self.index_id = os.environ.get(OPENSEARCH_INDEX_ID_ENV_VAR)
        self.number_of_docs = opensearch_knowledge_base_params.get(
            "NumberOfDocs",
            DEFAULT_OPENSEARCH_NUMBER_OF_DOCS,
        )

        self.return_source_documents = opensearch_knowledge_base_params.get(
            "ReturnSourceDocs",
            DEFAULT_RETURN_SOURCE_DOCS,
        )
      
        # Initialize the ContentHandler
        content_handler = ContentHandler()
        
        self.embeddings = SagemakerEndpointEmbeddings(
                endpoint_name=os.environ.get(SAGEMAKER_EMBEDDING_ENDPOINT),
                region_name=os.environ['AWS_REGION'],
                content_handler=content_handler,
            )
        self.docsearch = OpenSearchVectorSearch(
                index_name=os.environ.get(OPENSEARCH_INDEX_ID_ENV_VAR),
                embedding_function=self.embeddings,  
                opensearch_url="https://" + OPENSEARCH_HOST + ":443",
                http_auth=OPENSEARCH_AUTH
            )
      
        self.retriever = CustomOpenSearchRetriever(
         index_id=self.index_id, top_k=self.number_of_docs, return_source_documents=self.return_source_documents,  docsearch=self.docsearch,embeddings=self.embeddings)
    def _check_env_variables(self) -> None:
        """
        Checks if the OpenSearch related environment variables exist.
        """
        missing_env_vars = []
        
        if not os.environ.get(OPENSEARCH_INDEX_ID_ENV_VAR):
            missing_env_vars.append(OPENSEARCH_INDEX_ID_ENV_VAR)
            
        if not os.environ.get(OPENSEARCH_HOST_ENV_VAR):
            missing_env_vars.append(OPENSEARCH_HOST_ENV_VAR)
        
        if not os.environ.get(OPENSEARCH_SECRET_NAME_ENV_VAR):
            missing_env_vars.append(OPENSEARCH_SECRET_NAME_ENV_VAR)
    
        if missing_env_vars:
            missing_vars = ", ".join(missing_env_vars)
            logger.error(f"Missing environment variables: {missing_vars}")
            raise ValueError(f"Missing environment variables: {missing_vars}")