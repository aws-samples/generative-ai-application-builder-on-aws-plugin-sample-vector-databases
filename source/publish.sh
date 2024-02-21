
#!/bin/bash

# JSON data to be stored as a Secure String in SSM
json_data='{"UseCaseName":"berock-wrag-salone","ConversationMemoryType":"DynamoDB","KnowledgeBaseType":"OpenSearch","KnowledgeBaseParams":{"NumberOfDocs":1,"ReturnSourceDocs":false},"LlmParams":{"ModelProvider":"Bedrock","ModelId":"amazon.titan-tg1-large","ModelParams":{},"PromptTemplate":"","Streaming":true,"Verbose":false,"Temperature":0.1,"RAGEnabled":true},"IsInternalUser":"true"}'

# SSM parameter name
parameter_name="/gaab-ai/use-case-config/87654321"

# Store JSON data in SSM as a Secure String
aws ssm put-parameter --name "$parameter_name" --value "$json_data" --type "String" --overwrite

echo "Parameter command has been excecuted. Please make sure that the parameter has been uploaded successfully"

#install opensearch-py 

pip3 install opensearch-py --target ./ChatLlmProviderLambdaLayer/python/


# This function return a random number. We are doing this so that we can concatenate the random number to the string gaabopensearch$result
function myfunc()
{
    local  myresult=$RANDOM$RANDOM$RANDOM
    echo "$myresult"
}
result=$(myfunc)   # or result=`myfunc`
echo $result
#making a bucket with a unique name

echo $(aws s3 mb s3://gaabopensearch$result)


#installing zip
sudo yum install zip

#zipping ChatLlmProviderLambda and uploading it to the newly created bucket
cd source
cd ChatLlmProviderLambda
zip -r ChatLlmProviderLambda.zip *
aws s3 cp ChatLlmProviderLambda.zip s3://gaabopensearch$result
cd ..
#zipping ChatLlmProviderLambdaLayer and uploading it to the newly created bucket
cd ChatLlmProviderLambdaLayer
zip -r ChatLlmProviderLambdaLayer.zip *
aws s3 cp ChatLlmProviderLambdaLayer.zip s3://gaabopensearch$result
cd ..

echo "This is the bucket that was created. It now holds the zip file for lambda package and layers. Please note it for usage with cloudformation template for the following parameters. "
