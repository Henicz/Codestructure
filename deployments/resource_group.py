import time
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import ResourceGroup
from general.output_formatting import OutputFormatting

outputFormatting = OutputFormatting()

def create_resource_group(subscription_id, spn_object_id, spn_secret, tenant_id, resource):
    credentials = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=spn_object_id,
        client_secret=spn_secret
    )

    resource_client = ResourceManagementClient(credentials, subscription_id)

    properties = resource.get("properties", {})
    resource_group_name = properties.get("name")
    location = properties.get("location")

    try:
        resource_group = resource_client.resource_groups.get(resource_group_name)

        print(outputFormatting.warning(f"Resource like '{resource_group_name}' already exists."))
        exists = "exists"
        return exists

    except Exception as e:
        if "ResourceGroupNotFound" in str(e):
            print(outputFormatting.info(f"Creating '{resource_group_name}'..."))
            resource_group_params = ResourceGroup(location=location)
            resource_client.resource_groups.create_or_update(resource_group_name, resource_group_params)

            print(outputFormatting.info(f"Resource '{resource_group_name}' creation in progress..."))

            print(outputFormatting.valid(f"Resource '{resource_group_name}' created successfully."))
            return True

        else:
            print(outputFormatting.error(f"Resource '{resource_group_name}' already exists or wrong parameter passed."))
            return False

def remove_resource_group(subscription_id, spn_object_id, spn_secret, tenant_id, resource):
    credentials = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=spn_object_id,
        client_secret=spn_secret
    )

    resource_client = ResourceManagementClient(credentials, subscription_id)

    properties = resource.get("properties", {})
    resource_group_name = properties.get("name")

    try:
        resource_group = resource_client.resource_groups.get(resource_group_name)

        if resource_group:
            print(outputFormatting.info(f"Deleting '{resource_group_name}'."))
            resource_client.resource_groups.begin_delete(resource_group_name)

            timer = 0
            while resource_group:
                time.sleep(5)
                timer += 5
                try:
                    print(outputFormatting.info(f"Deleting '{resource_group_name}'. Time elapsed: {timer} seconds."))
                    resource_group = resource_client.resource_groups.get(resource_group_name)
                except:
                    resource_group = None
                    print(outputFormatting.valid(f"Deleting '{resource_group_name}' was successfull. Time elapsed: {timer} seconds."))
                    return True

    except:
        print(outputFormatting.error(f"Error while deleting '{resource_group_name}'"))
        return False

def update_resource_group(subscription_id, spn_object_id, spn_secret, tenant_id, resource):
    credentials = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=spn_object_id,
        client_secret=spn_secret
    )
    resource_client = ResourceManagementClient(credentials, subscription_id)

    properties = resource.get("properties", {})
    resource_group_name = properties.get("name")
    location = properties.get("location")

    try:
        resource_group = resource_client.resource_groups.get(resource_group_name)

        update_params = ResourceGroup(
            location=location
        )

        resource_client.resource_groups.create_or_update(resource_group_name, update_params)
        print(outputFormatting.info(f"Resource '{resource_group_name}' update in progress..."))
        
        timer = 0
        while resource_group:
            time.sleep(5)
            timer += 5
            try:
                print(outputFormatting.info(f"Resource '{resource_group_name}' is being updated. Time elapsed: {timer} seconds."))
                resource_group = resource_client.resource_groups.get(resource_group_name)
            except:
                resource_group = None
                print(outputFormatting.valid(f"Resource '{resource_group_name}' updated successfully. Time elapsed: {timer} seconds."))
                return True

    except:
        print(outputFormatting.error(f"Error while updating '{resource_group_name}'"))
        return False