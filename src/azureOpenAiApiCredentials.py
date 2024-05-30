import os
import dotenv


dotenv.load_dotenv()

azureOpenAiApiCredentials = {
    "GPT4TURBO": {
        "deployment_name": os.environ['AZUREOPENAIAPI_COMPLETION_GPT4TURBO_DEPLOYMENTNAME'],
        "azure_endpoint": os.environ['AZUREOPENAIAPI_COMPLETION_GPT4TURBO_ENDPOINT'],
        "api_key": os.environ['AZUREOPENAIAPI_COMPLETION_GPT4TURBO_KEY'],
        "api_version": os.environ['AZUREOPENAIAPI_COMPLETION_GPT4TURBO_VERSION']
    },
    "GPT35TURBO": {
        "deployment_name": os.environ['AZUREOPENAIAPI_COMPLETION_GPT35TURBO_DEPLOYMENTNAME'],
        "azure_endpoint": os.environ['AZUREOPENAIAPI_COMPLETION_GPT35TURBO_ENDPOINT'],
        "api_key": os.environ['AZUREOPENAIAPI_COMPLETION_GPT35TURBO_KEY'],
        "api_version": os.environ['AZUREOPENAIAPI_COMPLETION_GPT35TURBO_VERSION']
    },
    "GPT3516K": {
        "deployment_name": os.environ['AZUREOPENAIAPI_COMPLETION_GPT3516K_DEPLOYMENTNAME'],
        "azure_endpoint": os.environ['AZUREOPENAIAPI_COMPLETION_GPT3516K_ENDPOINT'],
        "api_key": os.environ['AZUREOPENAIAPI_COMPLETION_GPT3516K_KEY'],
        "api_version": os.environ['AZUREOPENAIAPI_COMPLETION_GPT3516K_VERSION']
    },
    "GPT4": {
        "deployment_name": os.environ['AZUREOPENAIAPI_COMPLETION_GPT4_DEPLOYMENTNAME'],
        "azure_endpoint": os.environ['AZUREOPENAIAPI_COMPLETION_GPT4_ENDPOINT'],
        "api_key": os.environ['AZUREOPENAIAPI_COMPLETION_GPT4_KEY'],
        "api_version": os.environ['AZUREOPENAIAPI_COMPLETION_GPT4_VERSION']
    }

}
