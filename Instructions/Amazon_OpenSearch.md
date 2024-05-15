# Generative AI Application Builder on AWS Plugin for Vector Databases

This sample code explains how to add Amazon OpenSearch (text search and embeddings search) for [Amazon Bedrock](https://aws.amazon.com/bedrock/knowledge-bases/) in the [Generative AI Application Builder on AWS](https://aws.amazon.com/solutions/implementations/generative-ai-application-builder-on-aws/) solution for Retrieval Augmented Generation (Retrieval Augmented Generation) use cases.

 **_NOTE:_**
This is not a production-ready code base, but should rather be used for testing and proof of concepts.

## Pre-requisites
See the pre-requisites section in [README.md](https://github.com/aws-samples/generative-ai-application-builder-on-aws-plugin-sample-vector-databases?tab=readme-ov-file#pre-requisites)

**Architecture Diagram:**
<img width="1174" alt="" src="https://github.com/aws-samples/generative-ai-application-builder-on-aws-plugin-sample-vector-databases/assets/Amazon-OpenSearch-GAAB.png">


## Steps to integrate OpenSearch for RAG with Generative AI App builder on AWS.

**Step 1: Clone the repository.**

**Step 2: Create initial resources through the publish script available inside source folder.**

```
cd source/publish_assets
chmod +x ./publish_amazon_opensearch.sh
./publish_amazon_opensearch.sh

```

The `publish_amazon_opensearch.sh` script would help create the following:

- An SSM parameter for storing a string in the SSM Parameter Store.
- An S3 bucket created for storing the lambda function assets and layers.
- The lambda and lambda layer assets zipped and uploaded to the S3 bucket.

**Step 3: Deploy the CloudFormation stack**

From the deployment folder, create a CloudFormation stack using `provision_amazon_opensearch.yaml`. Name the CloudFormation stack as rag22. At the end of this deployment the following resources will be created:

- SageMaker endpoint to create an embeddings model to store the data in the OpenSearch cluster
- OpenSearch Service cluster
- SageMaker Notebook
- IAM roles

**Step 4:Ingest data into OpenSearch.**

- You can use your own data or use sample data using the following steps:

- Navigate to SageMaker in the console. Open the notebook instance `aws-llm-apps-blog` and run it with Jupyter. Choose conda_python3 for the kernel and "restart and run all cells" from the 'kernel' tab

- Path to follow is: llm-apps-workshop > blogs > opensearch-data-ingestion > 2_kb_to_vectordb_opensearch.ipynb

- Note: In the sagemaker notebook, make sure that the CloudFormation name parameter is the same as stack name created above.
  `CFN_STACK_NAME = ""`

- This notebook will ingest data from [SageMaker docs](https://sagemaker.readthedocs.io/en/stable/) into an OpenSearch Service index. It also creates embeddings. In the lambda provided, a text search is performed to retrieve the documents from OpenSearch, but since the embeddings are created you can create a similar function for document search using embeddings as well. For more information also refer [here](https://aws.amazon.com/solutions/guidance/chatbots-with-vector-databases-on-aws/).

**Step 5: Deploy the CloudFormation template `bedrock_amazon_opensearch.template` in the deployment folder**

In the parameters,

1. Give the name of the OpenSearchChatLambdaBucket the name of the newly created s3 bucket in your AWS account from step 2.

2. For `ExistingOpenSearchHost` and `OpenSearchSecret` enter the value of `OpenSearchDomainEndpoint` and `OpenSearchSecret` output values from the `provision_amazon_opensearch.yaml` stack deployment.

3. You can either create a new kendra index or provide an existing kendra index.

 **_NOTE:_** Once deployed, In the parameter store, you can toggle between Kendra and OpenSearch ("KnowledgeBaseType":"OpenSearch") for the parameter to test the differences between Kendra and Amazon OpenSearch.

## Testing

Once deployed, you can get the CloudFront UI URL from the "Outputs" tab of the CloudFormation stack. In the conversation interface, you can ask SageMaker related questions and receive responses. For example, "What is Sagemaker Model Monitor?"

## Cleanup

- Delete the CloudFormation stacks

- Delete the S3 buckets

- Delete the index created

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
