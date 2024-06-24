from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku, Kind
from azure.core.exceptions import AzureError
import config 
import time

credential = DefaultAzureCredential()

storage_client = StorageManagementClient(credential, config.SUBSCRIPTION_ID)


def get_account_properties():
    try:
        account = storage_client.storage_accounts.get_properties(config.RESOURCE_GROUP_NAME, config.STORAGE_ACCOUNT_NAME)
        print(f'Storage account {config.STORAGE_ACCOUNT_NAME} properties:')
        print(f'Location: {account.location}')
        print(f'SKU: {account.sku.name}')
        print(f'Kind: {account.kind}')
        print(f'Access Tier: {account.access_tier}')
    except AzureError as e:
        print(f'Failed to retrieve properties for storage account {config.STORAGE_ACCOUNT_NAME}: {e}')




def remove_account():
    try:
        storage_client.storage_accounts.delete(
            config.RESOURCE_GROUP_NAME,
            config.STORAGE_ACCOUNT_NAME
        )
        print(f'Storage account {config.STORAGE_ACCOUNT_NAME} deleted successfully.')
    except AzureError as e:
        print(f'Failed to delete storage account {config.STORAGE_ACCOUNT_NAME}: {e}')



get_account_properties()
remove_account()
