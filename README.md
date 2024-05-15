# Generative AI Application Builder on AWS Plugin for Vector Databases

This sample code explains how to add a Knowledge Base in addition to Amazon Kendra and Knowledge Bases for [Amazon Bedrock](https://aws.amazon.com/bedrock/knowledge-bases/) for the [Generative AI Application Builder on AWS](https://aws.amazon.com/solutions/implementations/generative-ai-application-builder-on-aws/) solution for Retrieval Augmented Generation (Retrieval Augmented Generation) use cases.

 **_NOTE:_**
This is not a production-ready code base, but should rather be used for testing and proof of concepts.

**Architecture Diagram:**
<img width="1174" alt="main-arch-diagram-v1" src="https://github.com/aws-samples/generative-ai-application-builder-on-aws-plugin-sample-vector-databases/assets/62153270/1c2f7f8b-907d-4974-a021-9b89311c9fab">


## Pre-requisites

Following are pre-requisites to build and deploy locally:

-   [Docker](https://www.docker.com/get-started/)
-   [Nodejs 20.x](https://nodejs.org/en)
-   [CDK v2.118.0](https://github.com/aws/aws-cdk)
-   [Python >= 3.11, <=3.12.1](https://www.python.org/)
    -   _Note: normal python installations should include support for `ensurepip` and `pip`; however, if running in an environment without these packages you will need to manually install them (e.g. a minimal docker image). See [pip's installation guide](https://pip.pypa.io/en/stable/installation/) for details._
-   [AWS CLI](https://aws.amazon.com/cli/)
-   [jq](https://jqlang.github.io/jq/)

**Note: Configure the AWS CLI with your AWS credentials or have them exported in the CLI terminal environment. In case the credentials are invalid or expired, running `cdk deploy` produces an error.**

**Also, if you have not run `cdk bootstrap` in this account and region, please follow the instructions [here](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) to execute cdk bootstrap as a one time process before proceeding with the below steps.**


## Steps to integrate a Knowledge Base for Retrieval Augmented Generation with Generative AI App builder on AWS.

The steps to ingest data into the Knowledge Base and deploy the stack for the text use case are under Instructions folder.

The currently supported knowledge base are:

1. Amazon OpenSearch Text Search
2. Amazon OpenSearch Embeddings Search
3. Neo4j Search

Choose the instructions for the Knowledge Base that you would like to use from the Instructions folder.

 **_NOTE:_** Once deployed and testing is complete, do not forget to cleanup resources so that no cost is incurred after testing.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

