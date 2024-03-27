# generative-ai-application-builder-on-aws-plugin-sample-vector-databases
This sample code explains how to add  a knowledgebase in addition to Amazon Kendra for the "generative ai application builder on aws" solution.
https://aws.amazon.com/solutions/implementations/generative-ai-application-builder-on-aws/

Note: This is not a production ready code base, but should rather be used for testing and proof of concepts.

**Pre-requisites:**

Have the aws cli installed and python installed.


## Steps to integrate a Knowledgebase for Retrieval Augmented Generation with Generative AI App builder on AWS.

The steps to ingest data into the knowledgebase and deploy the stack for the text use case is under Instructions folder.

The currently supported knowledge base are 

1)Amazon Opensearch text search
2)Amazon OpenSearch embeddings search
3)Neo4j Search

Choose the instructions for the knowledgebase that you would like to use.

Note:Once deployed and testing is complete, do not forget to cleanup resources so that no cost is incurred after testing.


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

