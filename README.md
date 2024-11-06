# generative-ai-application-builder-on-aws-plugin-sample-vector-databases
This sample code explains how to add a Knowledgebase in addition to Amazon Kendra for the "Generative AI Application Builder on AWS" solution.
https://aws.amazon.com/solutions/implementations/generative-ai-application-builder-on-aws/

Note: This is not a production ready code base, but should rather be used for testing and proof of concepts.

If you find this GitHub repository useful, please consider giving it a free star ⭐ to show your appreciation and support for the project.

**Pre-requisites:**

Have the aws cli installed and python installed.

**Architecture Diagram:**
<img width="1174" alt="main-arch-diagram-v1" src="https://github.com/aws-samples/generative-ai-application-builder-on-aws-plugin-sample-vector-databases/assets/62153270/1c2f7f8b-907d-4974-a021-9b89311c9fab">


## Steps to integrate a Knowledgebase for Retrieval Augmented Generation with Generative AI App builder on AWS.

The steps to ingest data into the knowledgebase and deploy the stack for the text use case is under Instructions folder.

The currently supported knowledge base are 

1)Amazon Opensearch text search
2)Amazon OpenSearch embeddings search
3)Neo4j Search

Choose the instructions for the knowledgebase that you would like to use from the Instructions folder.

Note:Once deployed and testing is complete, do not forget to cleanup resources so that no cost is incurred after testing.


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

