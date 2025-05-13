import boto3
import os, json  
from langchain_aws import ChatBedrock
from models.llmProvider import LLMProvider

def run_bedrock(resume_text):    
    client = boto3.client('bedrock-runtime')
    response = client.invoke_model(
        modelId="anthropic.claude-v2",
        contentType="application/json",
        accept="application/json",
        body=json.dumps({"prompt": f"Extract relevant skills:\n\n{resume_text}", "max_tokens": 250})
    )
    return json.loads(response['body'].read().decode('utf-8'))

def get_bedrock_embedding(text):
    client = boto3.client('bedrock-runtime')
    response = client.invoke_model(
        modelId="amazon.titan-embed-text-v1",
        contentType="application/json",
        body=json.dumps({"inputText": text})
    )
    return json.loads(response['body'].read().decode("utf-8"))["embedding"]


class BedrockProvider(LLMProvider):
    def __init__(self, model_id="anthropic.claude-3-sonnet-20240229-v1:0", region_name="us-east-1", temperature=0):
        self.model_id = model_id
        self.region_name = region_name
        self.temperature = temperature
        
    def get_llm(self):
        # return BedrockChat(
        #     model_id=self.model_id,
        #     region_name=self.region_name,
        #     model_kwargs={"temperature": self.temperature}
        # )
        return ChatBedrock(
            model=self.model_id,
            region= os.environ['AWS_REGION'],
            momodel_kwargs={"temperature": self.temperature} 
        )