#!/usr/bin/env python
import os
import json
import boto3
from typing import Any, Dict,  Optional
from aws_lambda_powertools import Logger
from opensearchpy import OpenSearch
from shared.knowledge.knowledge_base import KnowledgeBase
from shared.knowledge.opensearch_retriever import CustomOpenSearchRetriever
from utils.constants import DEFAULT_OPENSEARCH_NUMBER_OF_DOCS, DEFAULT_RETURN_SOURCE_DOCS, OPENSEARCH_INDEX_ID_ENV_VAR
from utils.enum_types import KnowledgeBaseTypes

logger = Logger(utc=True)
OPENSEARCH_TIMEOUT = 30
OPENSEARCH_PORT = 443
OPENSEARCH_INDEX_ID_ENV_VAR = "OPENSEARCH_INDEX_ID"
OPENSEARCH_HOST_ENV_VAR = "OPENSEARCH_HOST"
OPENSEARCH_AUTH_ENV_VAR = "OPENSEARCH_AUTH"
OPENSEARCH_SECRET_NAME_ENV_VAR = "OPENSEARCH_SECRET_NAME_ENV_VAR"
OPENSEARCH_USE_SSL = True
OPENSEARCH_VERIFY_CERTIFICATES = True

# Function to retrieve the secret from AWS Secrets Manager
def get_secret(secret_name):
    
    client = boto3.client(service_name='secretsmanager')
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        logger.error(f"There is an Error retrieving the secret: {e}")
        raise e

    if 'SecretString' in get_secret_value_response:
        return json.loads(get_secret_value_response['SecretString'])
    else:
        raise Exception("The Secret is not in string format")
        
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
        
        self.client = OpenSearch(
            hosts=[
                {
                    "host": OPENSEARCH_HOST,
                    "port": OPENSEARCH_PORT,
                }
            ],
            http_auth=OPENSEARCH_AUTH,
            use_ssl=OPENSEARCH_USE_SSL,
            verify_certs=OPENSEARCH_VERIFY_CERTIFICATES,
            timeout=OPENSEARCH_TIMEOUT,
        )
      
        self.retriever = CustomOpenSearchRetriever(
            index_id=self.index_id, top_k=self.number_of_docs, return_source_documents=self.return_source_documents, client=self.client
        )
    
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