# generative-ai-application-builder-on-aws-plugin-sample-vector-databases
This sample code explains how to add Amazon OpenSearch (text search and embeddings search) as a knowledgebase for the "generative ai application builder on aws" solution.
https://aws.amazon.com/solutions/implementations/generative-ai-application-builder-on-aws/

**Pre-requisites:**

Have the aws cli installed and python installed.


## Steps to integrate OpenSearch for Retrieval Augmented Generation with Generative AI App builder on AWS.

**Step 1: Clone the repository.**

**Step 2: Create initial resources through the publish script available inside source folder.**


```
cd source/publishAssets

chmod +x ./publish_Amazon_OpenSearch.sh

./publish_Amazon_OpenSearch.sh

```
This would help create the following:
-  An SSM parameter for storing a string in the SSM Parameter Store.
-  An S3 bucket created for storing the lambda function assets and layers.
-  Logic to zip the contents of lambda function, layers and upload to the s3 bucket. 

**Step 3: Deploy the cloudformtaion stack**

From the deployment folder, create a cloudformation stack using provision_Amazon_OpenSearch.yaml. Name the cloudformation stack as rag22. At the end of this deployment the following resources will be created.

- SageMaker endpoint for the embedding mdodel
- OpenSearch Service cluster
- SageMaker Notebook
- IAM roles

**Step 4:Ingest data into OpenSearch.**

- You can use your own data or use sample data using the following steps:

- Navigate to SageMaker in the console. Open the notebook instance "aws-llm-apps-blog" and run it with Jupyter. Choose conda_python3 for the kernel and "restart and run all cells" from the 'kernel' tab

- Path to follow is: llm-apps-workshop->blogs->opensearch-data-ingestion->2_kb_to_vectordb_opensearch.ipynb

- note: In the sagemaker notebook, make sure that the cloudformation name parameter is the same as stack name created above.
CFN_STACK_NAME = ""

- This notebook will ingest data from SageMaker docs (https://sagemaker.readthedocs.io/en/stable/) into an OpenSearch Service index. It also creates embeddings. In the lambda provided, a text search is performed to retrieve the documents from OpenSearch, but since the embeddings are created you can create a similar function for document search using embeddings as well. For more information also refer to https://aws.amazon.com/solutions/guidance/chatbots-with-vector-databases-on-aws/


**Step 5: Deploy the cloudformation template bedrock_Amazon_OpenSearch.template in the deployment folder..**

In the parameters,

1. Give the name of the OpenSearchChatLambdaBucket the name of the newly created s3 bucket in your AWS account from step 2.

2. For ExistingOpenSearchHost and OpenSearchSecret enter the value of OpenSearchDomainEndpoint and OpenSearchSecret output values from the provision_Amazon_OpenSearch.yaml stack deployment.

3. You can either create a new kendra index or provide an existing kendra index. 

note: Once deployed, In the parameter store, you can toggle between Kendra and OpenSearch ("KnowledgeBaseType":"OpenSearch") for the parameter to test the differences between Kendra and Amazon OpenSearch. 

## Testing
Once deployed, you can get the UI url from the "Outputs" tab of the cloudformation stack. In the conversation interface, you can enter sagemaker related questions and receive responses. For example, "What is Sagemaker Model Monitor?"

## Cleanup

- Delete the cloudformation stacks

- Delete the s3 buckets and the index created.


## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

