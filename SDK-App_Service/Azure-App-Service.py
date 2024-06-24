from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.web import WebSiteManagementClient
from azure.mgmt.web.models import Site, SkuDescription

SUBSCRIPTION_ID = '86c82398-3448-43c6-9f4b-954558c30c5a'
RESOURCE_GROUP_NAME = 'Rohan-RG'
LOCATION = 'centralindia'
APP_SERVICE_PLAN_NAME = 'lab-plan-Rohan'
WEB_APP_NAME = 'lab-app-Rohan'

credential = AzureCliCredential()
resource_client = ResourceManagementClient(credential, SUBSCRIPTION_ID)
web_client = WebSiteManagementClient(credential, SUBSCRIPTION_ID)

resource_client.resource_groups.create_or_update(
    RESOURCE_GROUP_NAME,
    {"location": LOCATION}
)

app_service_plan_async = web_client.app_service_plans.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    APP_SERVICE_PLAN_NAME,
    {
        "location": LOCATION,
        "reserved": False,  
        "sku": SkuDescription(
            name="B1",  
            tier="Basic",
            size="B1",
            family="B",
            capacity=1
        )
    }
)
app_service_plan = app_service_plan_async.result()
print(f"Created {APP_SERVICE_PLAN_NAME} App Service Plan successfully.")

web_app_async = web_client.web_apps.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    WEB_APP_NAME,
    Site(
        location=LOCATION,
        server_farm_id=app_service_plan.id
    )
)
web_app = web_app_async.result()
print(f" Created {WEB_APP_NAME}.")