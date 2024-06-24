from azure.identity import DefaultAzureCredential
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.keyvault.models import VaultProperties, Sku, AccessPolicyEntry, Permissions, SecretPermissions, \
    KeyPermissions, CertificatePermissions, VaultCreateOrUpdateParameters
from azure.keyvault.secrets import SecretClient


subscription_id = '86c82398-3448-43c6-9f4b-954558c30c5a'
resource_group_name = 'Rohan-RG'
vault_name = 'rohanlab'
location = 'centralindia'  

credential = DefaultAzureCredential()

keyvault_client = KeyVaultManagementClient(credential, subscription_id)

properties = VaultProperties(
    sku=Sku(name='standard'),
    tenant_id=credential.get_token("https://management.azure.com/").tenant_id,
    access_policies=[
        AccessPolicyEntry(
            tenant_id=credential.get_token("https://management.azure.com/").tenant_id,
            object_id="your-object-id",  
            permissions=Permissions(
                secrets=[SecretPermissions.all],
                keys=[KeyPermissions.all],
                certificates=[CertificatePermissions.all]
            )
        )
    ]
)

create_params = VaultCreateOrUpdateParameters(
    location=location,
    properties=properties,
    tags={}
)

vault = keyvault_client.vaults.create_or_update(resource_group_name, vault_name, create_params)

print(f"Key Vault '{vault_name}' created successfully in resource group '{resource_group_name}'.")


vault_url = f"https://{vault_name}.vault.azure.net/"
secret_client = SecretClient(vault_url=vault_url, credential=credential)

secret_name = "ssecret_name"
secret_value = "secret_value"

secret_client.set_secret(secret_name, secret_value)

print(f"Secret '{secret_name}' stored in Key Vault '{vault_name}'")

# Example: Retrieve a secret from the Key Vault
retrieved_secret = secret_client.get_secret(secret_name)
print(f"Retrieved secret '{secret_name}': {retrieved_secret.value}")
