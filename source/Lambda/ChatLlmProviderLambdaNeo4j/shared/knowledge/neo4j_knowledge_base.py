#!/usr/bin/env python
import os
import json
import boto3
from typing import Any, Dict,  Optional
from aws_lambda_powertools import Logger
from shared.knowledge.knowledge_base import KnowledgeBase
from shared.knowledge.neo4j_retriever import CustomNeo4jRetriever
from utils.constants import DEFAULT_NEO4J_NUMBER_OF_DOCS, DEFAULT_RETURN_SOURCE_DOCS, NEO4J_INDEX_ID_ENV_VAR
from utils.enum_types import KnowledgeBaseTypes
from langchain.vectorstores import Neo4jVector
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores.neo4j_vector import SearchType

logger = Logger(utc=True)
NEO4J_TIMEOUT = 30
NEO4J_PORT = 443
NEO4J_INDEX_ID = "NEO4J_INDEX_ID"
NEO4J_URI = "NEO4J_URI"
NEO4J_AUTH_ENV_VAR = "NEO4J_AUTH"
NEO4J_SECRET_NAME_ENV_VAR = "NEO4J_SECRET_NAME_ENV_VAR"
NEO4J_USE_SSL = True
NEO4J_VERIFY_CERTIFICATES = True
NEO4J_NODE_LABEL="NEO4J_NODE_LABEL"
NEO4J_NODE_PROPERTY=["title", "description"]
NEO4J_EMBEDDING_NODE_PROPERTY="NEO4J_EMBEDDING_NODE_PROPERTY"
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
        
class Neo4jKnowledgeBase(KnowledgeBase):
    """
    Neo4jKnowledgeBase adds context to the LLM memory using NEO4J.

    Attributes:

        index_name (str): NEO4J index name
        number_of_docs (int): Number of documents to query for [Optional]
        retriever (CustomNeo4jRetriever): Custom NEO4J retriever

    Methods:
        get_relevant_documents(query): Run search on Neo4j index and get top k documents.
    """

    knowledge_base_type: KnowledgeBaseTypes = KnowledgeBaseTypes.Neo4j.value

    def __init__(
        self,
        neo4j_knowledge_base_params: Optional[Dict[str, Any]] = {},
    ) -> None:
        self._check_env_variables()
        
        
        # Retrieve the secret name from the environment variable
        secret_name = os.environ.get(NEO4J_SECRET_NAME_ENV_VAR)
        if secret_name:
            secret = get_secret(secret_name)
            NEO4J_USERNAME = (secret['username'])
            NEO4J_PASSWORD = (secret['password'])
        else:
            raise ValueError("NEO4J secret name not provided in environment variables")

        self.index_id = os.environ.get(NEO4J_INDEX_ID_ENV_VAR)
        self.number_of_docs = neo4j_knowledge_base_params.get(
            "NumberOfDocs",
            DEFAULT_NEO4J_NUMBER_OF_DOCS,
        )

        self.return_source_documents = neo4j_knowledge_base_params.get(
            "ReturnSourceDocs",
            DEFAULT_RETURN_SOURCE_DOCS,
        )

       
        bedrock = boto3.client('bedrock-runtime')
    
        EMBEDDING_MODEL = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=bedrock)
        
        self.docsearch = Neo4jVector.from_existing_graph(
        embedding=EMBEDDING_MODEL,
        url=os.environ.get(NEO4J_URI),
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        index_name=os.environ.get(NEO4J_INDEX_ID),
        node_label=os.environ.get(NEO4J_NODE_LABEL),
        text_node_properties=NEO4J_NODE_PROPERTY,
        embedding_node_property=os.environ.get(NEO4J_EMBEDDING_NODE_PROPERTY),
        )
        self.retriever = CustomNeo4jRetriever(
            index_id=self.index_id, top_k=self.number_of_docs, return_source_documents=self.return_source_documents, docsearch=self.docsearch
        )
    def _check_env_variables(self) -> None:
        """
        Checks if the Neo4j related environment variables exist.
        """
        missing_env_vars = []
        
        if not os.environ.get(NEO4J_INDEX_ID_ENV_VAR):
            missing_env_vars.append(NEO4J_INDEX_ID_ENV_VAR)
            
        if not os.environ.get(NEO4J_URI):
            missing_env_vars.append(NEO4J_URI)
        
        if not os.environ.get(NEO4J_SECRET_NAME_ENV_VAR):
            missing_env_vars.append(NEO4J_SECRET_NAME_ENV_VAR)
    
        if missing_env_vars:
            missing_vars = ", ".join(missing_env_vars)
            logger.error(f"Missing environment variables: {missing_vars}")
            raise ValueError(f"Missing environment variables: {missing_vars}")