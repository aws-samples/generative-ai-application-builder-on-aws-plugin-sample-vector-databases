# Generative AI Application Builder on AWS Plugin for Vector Databases

This sample code explains how to add Neo4j for [Amazon Bedrock](https://aws.amazon.com/bedrock/knowledge-bases/) in the [Generative AI Application Builder on AWS](https://aws.amazon.com/solutions/implementations/generative-ai-application-builder-on-aws/) solution for Retrieval Augmented Generation (Retrieval Augmented Generation) use cases.

**_NOTE:_**
This is not a production-ready code base, but should rather be used for testing and proof of concepts.

## Pre-requisites

See the pre-requisites section in [README.md](https://github.com/aws-samples/generative-ai-application-builder-on-aws-plugin-sample-vector-databases?tab=readme-ov-file#pre-requisites)

A free instance can be created for neo4j AuraDB is available [here](https://neo4j.com/cloud/platform/aura-graph-database/?utm_medium=PaidSearch&utm_source=Google&utm_campaign=UCGenAIutm_content=AMS-Search-SEMBrand-UCGenAI-None-SEM-SEM-NonABM&utm_adgroup=genai-llm&utm_term=neo4j%20ai&gclid=Cj0KCQjwwMqvBhCtARIsAIXsZpaStf3cKwDB7CTKLjpuJRx80URq3WBweTCmU7-r2PsdshNi1o0Y8u0aAl2iEALw_wcB).

## Steps to integrate Neo4j for Retrieval Augmented Generation with Generative AI App builder on AWS.

**Step 1: Clone the repository.**

In the terminal, use the following AWS CLI command to create a secret in secrets manager. Provide the username, password within the strings.

```
aws secretsmanager create-secret --name 'Neo4j-secret' --secret-string '{"username":"", "password":""}'

```

**Step 2: Create initial resources through the publish script available inside source folder.**

```
cd source/publish_assets

chmod +x ./publish_neo4j.sh

./publish_neo4j.sh

```

This would help create the following:

- An SSM parameter for storing a string in the SSM Parameter Store.
- An S3 bucket created for storing the lambda function assets and layers.
- Logic to zip the contents of lambda function, layers and upload to the s3 bucket.

**Step 3:Ingest data into Neo4j.**

To use sample data to ingest in Neo4j using the following steps:

- Once you connect to the neo4j Aura instance, please run the following cypher queries. Each of these queries would create 1 node, will set 2 properties, and 1 label.

```
CREATE (p:Recs {title: "Amazon Q", description: 'Amazon Q is a fully managed, generative-AI powered assistant that you can configure to answer questions, provide summaries, generate content, and complete tasks based on data in your enterprise. Amazon Q provides immediate and relevant information to employees, and helps streamline tasks and accelerate problem solving.'})
```

```
CREATE (p:Recs {title: "Benefits of Amazon Q", description: 'Amazon Q generates comprehensive responses to natural language queries from users by analyzing information across all enterprise content that it has access to. It can avoid incorrect statements by confining its generated responses to existing enterprise data. Amazon Q also provides citations to the sources that it used to generate its response.Amazon Q undertakes the complex task of developing and managing machine learning infrastructure and models so that you can build your chat solution quickly. Amazon Q connects to your data and ingests it for processing using its pre-built connectors, document retrievers, document upload capabilities.Amazon Q provides you with the flexibility of choosing what sources should be used to respond to user queries. You can control whether the responses should only use your enterprise data, or use both enterprise data and model knowledge.'})

```

```
CREATE (p:Recs {title: "How Amazon Q works", description: "With Amazon Q, you can build an interactive chat application for your organization’s end users, using a combination of your enterprise data and large language model knowledge, or enterprise data only."}
)
```

```
CREATE (p:Recs {title: "Enhancing an Amazon Q application", description: "After you finish configuring your application, you can optionally choose to enhance it.You can choose from the following available enhancements:Document enrichment – Control document attribute ingestion and build customized data solutions.Guardrails – Customize blocked topics and choose the knowledge sources your web experience uses for responses.
Plugins – Enable your end users to perform specific tasks related to third-party services from within their web experience chat—like creating Jira tickets."})
```

**Step 4: Deploy the CloudFormation template `bedrock_neo4j.template`**

In the parameters,

1. Give the name of the `Neo4jLambdaBucket` the name of the newly created s3 bucket in your AWS account from step 2.

2. For `ExistingNeo4jHost` enter the Neo4j instance URI.

3. You can either create a new kendra index or provide an existing kendra index.

 **_NOTE:_**  Once deployed, In the parameter store, you can toggle between Kendra and Neo4j ("KnowledgeBaseType":"Neo4j") for the parameter to test the differences between Kendra and Neo4j.

## Testing

Once deployed, you can get the CloudFront UI URL from the "Outputs" tab of the CloudFormation stack. In the conversation interface, you can enter questions related to content in Neo4j and receive responses. For example, "What is amazon Q and how does it work?"

## Cleanup

- Delete the CloudFormation stacks

- Delete the S3 buckets

- Delete the created index

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
