import asyncio

import azure.core.pipeline.transport
import azure.core.credentials as credentials
import azure.ai.inference.aio as inference

async def run():
    transport = azure.core.pipeline.transport.AioHttpTransport()
    async with inference.ChatCompletionsClient(
        endpoint='https://mistral-large-ajmih-serverless.eastus2.inference.ai.azure.com',
        credential=credentials.AzureKeyCredential("baQKPcIbIX1TW55l3IyfZBCKJdecumPC"),
        #transport=transport
    ) as client:
        async with client.with_defaults(seed=12) as defaulted_client:
            try:
                print("inner")
                model_info=await defaulted_client.get_model_info()
                print(model_info)
            except Exception as e:
                print(e)
        try:
            print("outer")
            model_info=await client.get_model_info()
            print(model_info)
        except Exception as e:
            print(e)
                
asyncio.run(run())