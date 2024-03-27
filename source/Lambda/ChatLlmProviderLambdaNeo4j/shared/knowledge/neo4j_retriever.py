#!/usr/bin/env python
import os
import time
from typing import Any, Dict, List, Optional, Sequence
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain.vectorstores import Neo4jVector
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores.neo4j_vector import SearchType
from utils.constants import METRICS_SERVICE_NAME, TRACE_ID_ENV_VAR
from utils.enum_types import CloudWatchNamespaces

logger = Logger(utc=True)
tracer = Tracer()
metrics = Metrics(namespace=CloudWatchNamespaces.AWS_NEO4J.value, service=METRICS_SERVICE_NAME)
from enum import Enum


class Neo4jCloudWatchMetrics(str, Enum):
    """Supported Cloudwatch Metrics"""

    NEO4J_QUERY = "NEO4JQueries"
    NEO4J_QUERY_PROCESSING_TIME = "NEO4JProcessingTime"
    NEO4J_FAILURES = "NEO4JFailures"


class CustomNeo4jRetriever(BaseRetriever):
    """
    Retrieves documents from an Neo4j index.

    Attributes:
        client (Any): Neo4j client
        index_name (str): Neo4j index name
        top_k (int): Number of documents to return
    """

    index_id: str
    #client: Any
    top_k: int
    return_source_documents: bool
    docsearch: Any

    def __init__(
        self,
        index_id: str,
        #client: Any,
        docsearch: Any,
        top_k: Optional[int] = 10,
        return_source_documents: Optional[bool] = False,
    ):
        super().__init__(
            index_id=index_id, top_k=top_k, return_source_documents=return_source_documents
        )  # Call the superclass constructor
        self.index_id = index_id
        self.top_k = top_k
        self.return_source_documents = return_source_documents
        #self.client = client
        self.docsearch = docsearch

    @tracer.capture_method(capture_response=True)
    @metrics.log_metrics
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """
        Run search on Neo4j index and get top k documents.
        Overrides the abstract method from BaseRetriever.

        Returns:
            List[Document]: List of Document objects.
        """
        with tracer.provider.in_subsegment("## neo4j_query") as subsegment:
            subsegment.put_annotation("service", "neo4j")
            subsegment.put_annotation("operation", "retrieve/query")
            metrics.add_metric(name=Neo4jCloudWatchMetrics.NEO4J_QUERY.value, unit=MetricUnit.Count, value=1)
            try:
                cleaned_docs = self._neo4j_query(query)
                documents = [Document(page_content=doc) for doc in cleaned_docs]
                return documents
            except Exception as e:
                logger.error(
                    f" query failed, returning empty docs. Query: {query}\nException: {e}",
                    xray_trace_id=os.environ[TRACE_ID_ENV_VAR],
                )
                metrics.add_metric(
                    name=Neo4jCloudWatchMetrics.NEO4J_FAILURES.value, unit=MetricUnit.Count, value=1
                )

            return []

    @tracer.capture_method(capture_response=True)
    def _neo4j_query(self, query: str):
        """
        Execute a query on the neo4j index 

        Args:
            query (str): Query to search for in the neo4j index

       
        """
        try:
            start_time = time.time()
            response = self.docsearch.similarity_search(query, k=1)
            end_time = time.time()
            metrics.add_metric(
                name=Neo4jCloudWatchMetrics.NEO4J_QUERY_PROCESSING_TIME.value,
                unit=MetricUnit.Seconds,
                value=(end_time - start_time),
            )

            cleaned_docs = self._get_clean_docs(response)
            for doc in cleaned_docs:
                print(doc)
            return cleaned_docs

        except Exception as e:
            logger.error(f"query failed: {e}")
            return []

    def _get_clean_docs(self, documents):
        cleaned_docs = []
    
        for document in documents:  # Assuming 'documents' is a list of Document objects
            content = document.page_content  # Directly use the content string
            if content:  # Ensure the content is not empty
                cleaned_docs.append(content)
    
        return cleaned_docs



