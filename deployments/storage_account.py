import time
from azure.identity import ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku
from azure.mgmt.storage.models import StorageAccountUpdateParameters
from general.output_formatting import OutputFormatting

outputFormatting = OutputFormatting()

def create_storage_account(subscription_id, spn_object_id, spn_secret, tenant_id, resource):
    credentials = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=spn_object_id,
        client_secret=spn_secret
    )

    storage_client = StorageManagementClient(credentials, subscription_id)

    properties = resource.get("properties", {})

    storage_account_name = properties.get("name")
    location = properties.get("location")
    resource_group_name = properties.get("resource_group_name")
    sku = properties.get("sku")

    try:
        storage_account = storage_client.storage_accounts.get_properties(resource_group_name, storage_account_name)

        print(outputFormatting.warning(f"Resource like '{storage_account_name}' already exists."))
        exists = "exists"
        return exists
    
    except Exception as e:
        if "ResourceNotFound" in str(e):
            print(outputFormatting.info(f"Creating '{storage_account_name}'..."))

            create_params = StorageAccountCreateParameters(
                sku=Sku(name=sku),
                kind="StorageV2",
                location=location
            )

            operation = storage_client.storage_accounts.begin_create(resource_group_name, storage_account_name, create_params)
            timer = 0
            while operation.status() != 'Succeeded':
                time.sleep(5)
                timer += 5
                print(outputFormatting.info(f"Resource '{storage_account_name}' is being created. Time elapsed: {timer} seconds."))
                operation = storage_client.storage_accounts.begin_create(resource_group_name, storage_account_name, create_params)
                if operation.status() == 'Succeeded':
                    print(outputFormatting.valid(f"Resource '{storage_account_name}' created successfully. Time elapsed: {timer} seconds."))
                    return True
        else:
            print(f"Error while creating: '{storage_account_name}'")
            return False

def remove_storage_account(subscription_id, spn_object_id, spn_secret, tenant_id, resource):
    credentials = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=spn_object_id,
        client_secret=spn_secret
    )

    storage_client = StorageManagementClient(credentials, subscription_id)

    properties = resource.get("properties", {})

    storage_account_name = properties.get("name")
    resource_group_name = properties.get("resource_group_name")

    try:
        storage_account = storage_client.storage_accounts.get_properties(resource_group_name, storage_account_name)

        if storage_account:
            print(outputFormatting.info(f"Deleting '{storage_account_name}'."))
            storage_client.storage_accounts.delete(resource_group_name, storage_account_name)
            timer = 0
            while storage_account:
                time.sleep(5)
                timer += 5
                try:
                    print(outputFormatting.info(f"Deleting '{storage_account_name}'. Time elapsed: {timer} seconds."))
                    storage_account = storage_client.storage_accounts.get_properties(resource_group_name, storage_account_name)
                except:
                    storage_account = None
                    print(outputFormatting.valid(f"Removal of '{storage_account_name}' was successful. Time elapsed: {timer} seconds."))
                    return True
                timer += 5
                time.sleep(5)
    except:
        print(outputFormatting.error(f"Error deleting '{storage_account_name}'"))
        return False

def update_storage_account(subscription_id, spn_object_id, spn_secret, tenant_id, resource):
    credentials = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=spn_object_id,
        client_secret=spn_secret
    )

    storage_client = StorageManagementClient(credentials, subscription_id)

    properties = resource.get("properties", {})

    storage_account_name = properties.get("name")
    resource_group_name = properties.get("resource_group_name")
    prop_sku = properties.get("sku")
    prop_kind = properties.get("kind")

    try:
        storage_client.storage_accounts.get_properties(resource_group_name,storage_account_name)

        print(outputFormatting.info(f"Updating '{storage_account_name}'..."))
        update_params = StorageAccountUpdateParameters(
            sku= Sku(name=prop_sku, tier="Standard"),
            kind=prop_kind
        )

        update = storage_client.storage_accounts.update(resource_group_name, storage_account_name, update_params)

        print(outputFormatting.info(f"Resource '{storage_account_name}' update in progress..."))

        if update:
            print(outputFormatting.valid(f"Resource '{storage_account_name}' updated successfully."))
            return True

    except:
        print(outputFormatting.error(f"Error while updating '{storage_account_name}'"))
        return False