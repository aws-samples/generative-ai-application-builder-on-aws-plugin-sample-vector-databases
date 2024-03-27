#!/usr/bin/env python


import os
import time
from typing import Any, Dict, List, Optional, Sequence

from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from opensearchpy import exceptions as opensearch_exceptions
from utils.constants import METRICS_SERVICE_NAME, TRACE_ID_ENV_VAR
from utils.enum_types import CloudWatchNamespaces

logger = Logger(utc=True)
tracer = Tracer()
metrics = Metrics(namespace=CloudWatchNamespaces.AWS_OPENSEARCH.value, service=METRICS_SERVICE_NAME)
from enum import Enum


class OpenSearchCloudWatchMetrics(str, Enum):
    """Supported Cloudwatch Metrics"""

    OPENSEARCH_QUERY = "OpenSearchQueries"
    OPENSEARCH_QUERY_PROCESSING_TIME = "OpenSearchProcessingTime"
    OPENSEARCH_FAILURES = "OpenSearchFailures"


class CustomOpenSearchRetriever(BaseRetriever):
    """
    Retrieves documents from an OpenSearch index.

    Attributes:
        client (Any): OpenSearch client
        index_name (str): OpenSearch index name
        top_k (int): Number of documents to return
    """

    index_id: str
    client: Any
    top_k: int
    return_source_documents: bool

    def __init__(
        self,
        index_id: str,
        client: Any,
        top_k: Optional[int] = 10,
        return_source_documents: Optional[bool] = False,
    ):
        super().__init__(
            index_id=index_id, top_k=top_k, return_source_documents=return_source_documents
        )  # Call the superclass constructor
        self.index_id = index_id
        self.top_k = top_k
        self.return_source_documents = return_source_documents
        self.client = client

    @tracer.capture_method(capture_response=True)
    @metrics.log_metrics
    def _get_relevant_documents(self, query: str) -> List[Document]:
        """
        Run search on OpenSearch index and get top k documents.
        Overrides the abstract method from BaseRetriever.

        Returns:
            List[Document]: List of Document objects.
        """
        with tracer.provider.in_subsegment("## opensearch_query") as subsegment:
            subsegment.put_annotation("service", "opensearch")
            subsegment.put_annotation("operation", "retrieve/query")
            metrics.add_metric(name=OpenSearchCloudWatchMetrics.OPENSEARCH_QUERY.value, unit=MetricUnit.Count, value=1)
            try:
                cleaned_docs = self._opensearch_query(query)
                documents = [Document(page_content=doc) for doc in cleaned_docs]
                return documents
            except opensearch_exceptions.OpenSearchException as e:
                logger.error(
                    f"OpenSearch query failed, returning empty docs. Query: {query}\nException: {e}",
                    xray_trace_id=os.environ[TRACE_ID_ENV_VAR],
                )
                metrics.add_metric(
                    name=OpenSearchCloudWatchMetrics.OPENSEARCH_FAILURES.value, unit=MetricUnit.Count, value=1
                )

            return []

    @tracer.capture_method(capture_response=True)
    def _opensearch_query(self, query: str):
        """
        Execute a query on the OpenSearch index and return a list of ResultItem-like responses.

        Args:
            query (str): Query to search for in the OpenSearch index

        Returns:
            Sequence[ResultItem]: List of OpenSearch query response items
        """
        try:
            start_time = time.time()
            response = self.client.search(
                body={"size": self.top_k, "query": {"match": {"text": query}}, "_source": ["text"]},
                index=self.index_id,
            )
            end_time = time.time()
            metrics.add_metric(
                name=OpenSearchCloudWatchMetrics.OPENSEARCH_QUERY_PROCESSING_TIME.value,
                unit=MetricUnit.Seconds,
                value=(end_time - start_time),
            )

            cleaned_docs = self._get_clean_docs(response["hits"]["hits"])
            return cleaned_docs

        except opensearch_exceptions.OpenSearchException as e:
            logger.error(f"OpenSearch query failed: {e}")
            return []

    def _get_clean_docs(self, docs) -> Sequence[Dict[str, Any]]:
        """
        Parses and cleans the documents returned from OpenSearch, returning them in a Document-like format.

        Args:
            docs (Sequence[ResultItem]): List of OpenSearch query response items

        Returns:
            Sequence[Dict[str, Any]]: List of cleaned document objects
        """
        cleaned_docs = []
        for value in docs:
            cleaned_doc = value.get("_source", {}).get("text")
            cleaned_docs.append(cleaned_doc)
        return cleaned_docs

