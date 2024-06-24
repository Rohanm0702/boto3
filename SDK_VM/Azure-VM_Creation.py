import asyncio
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.core.exceptions import HttpResponseError

async def create_resources():
    credential = AzureCliCredential()
    subscription_id = '86c82398-3448-43c6-9f4b-954558c30c5a'

    # Resource Management Client
    resource_client = ResourceManagementClient(credential, subscription_id)
    resource_group_name = 'Rohan-RG'
    location = 'centralindia'
    resource_group_params = {'location': location}
    
    try:
        # Create or update resource group (synchronous operation)
        resource_group = resource_client.resource_groups.create_or_update(resource_group_name, resource_group_params)

        # Network Management Client
        network_client = NetworkManagementClient(credential, subscription_id)

        vnet_name = 'RohanVnet'
        subnet_name = 'RohanSubnet'
        vnet_params = {'location': location, 'address_space': {'address_prefixes': ['10.0.0.0/16']}}
        poller = network_client.virtual_networks.begin_create_or_update(resource_group_name, vnet_name, vnet_params)
        vnet_result = poller.result()
        
        subnet_params = {'address_prefix': '10.0.1.0/24'}
        poller = network_client.subnets.begin_create_or_update(resource_group_name, vnet_name, subnet_name, subnet_params)
        subnet_result = poller.result()

        ip_name = 'RohanPublicIP'
        ip_params = {'location': location, 'public_ip_allocation_method': 'Dynamic'}
        poller = network_client.public_ip_addresses.begin_create_or_update(resource_group_name, ip_name, ip_params)
        public_ip = poller.result()

        nic_name = 'RohanNIC'
        nic_params = {
            'location': location,
            'ip_configurations': [{
                'name': 'myIPConfig',
                'subnet': {'id': subnet_result.id},
                'public_ip_address': {'id': public_ip.id}
            }]
        }
        poller = network_client.network_interfaces.begin_create_or_update(resource_group_name, nic_name, nic_params)
        network_interface = poller.result()

        # Compute Management Client
        compute_client = ComputeManagementClient(credential, subscription_id)
        vm_name = 'RohanVM'
        vm_params = {
            'location': location,
            'hardware_profile': {'vm_size': 'Standard_B1s'},
            'storage_profile': {
                'image_reference': {
                    'publisher': 'Canonical',
                    'offer': 'UbuntuServer',
                    'sku': '18.04-LTS',
                    'version': 'latest'
                },
                'os_disk': {
                    'create_option': 'FromImage',
                    'managed_disk': {
                        'storage_account_type': 'Standard_LRS'
                    }
                }
            },
            'os_profile': {
                'computer_name': vm_name,
                'admin_username': 'azureuser',
                'admin_password': 'Password@123'
            },
            'network_profile': {
                'network_interfaces': [{'id': network_interface.id}]
            }
        }
        poller = compute_client.virtual_machines.begin_create_or_update(resource_group_name, vm_name, vm_params)
        print(f"Azure resources created successfully!")

    except HttpResponseError as e:
        print(f"Failed to create Azure resources: {str(e)}")

def main():
    asyncio.run(create_resources())

if __name__ == "__main__":
    main()
