import re
import os
import click
import json
from general.output_formatting import OutputFormatting
from general.save_file import save_file
from converters.merge_cst_files import merge_cst_files
from converters.convert_to_json import convert_to_json
from converters.initial_convert_to_json import initial_convert_to_json
from parsers.parse_configuration_block import parse_configuration_block
from parsers.resolve_references import resolve_references
from general.load_state_file import load_state_file
from parsers.identify_resource_changes import identify_resource_changes
from handlers.error_handlers import ErrorHandlers
from deployments.resource_group import create_resource_group, remove_resource_group, update_resource_group
from deployments.storage_account import create_storage_account, remove_storage_account, update_storage_account

@click.command()
@click.argument('action', required=True)
def main(action):
    try:
        merged_cst_content = merge_cst_files()
        outputFormatting = OutputFormatting()

        if action == 'read':
            try:
                result_json = convert_to_json(merged_cst_content)
                config_match = re.search(r'configuration\s*{(.*?)}', merged_cst_content, re.DOTALL)

                if config_match:
                    config_block = config_match.group(1)
                    config_data = parse_configuration_block(config_block)
                    state_file_name = config_data.get("state_file_name", "default_state.cststate.lock")
                    lock_state_file_name = state_file_name + ".lock"
                else:
                    state_file_name = "default_state.cststate"
                    lock_state_file_name = "default_state.cststate.lock"

                with open(lock_state_file_name, "w") as state_file:
                    state_file.write(result_json)
                
                if not os.path.exists(state_file_name):
                    initial_result_json = initial_convert_to_json(merged_cst_content)
                    with open(state_file_name, "w") as state_file:
                        state_file.write(initial_result_json)

                print(outputFormatting.valid(f'Successfully initialized the Codestructure {lock_state_file_name}'))

                print(outputFormatting.info(f"Resolving references in file: {lock_state_file_name}"))
                resolved_config = resolve_references(lock_state_file_name)

                resolved_config_json = json.dumps(resolved_config, indent=4)

                with open(lock_state_file_name, "w") as state_file:
                    state_file.write(resolved_config_json)

                print(outputFormatting.valid(f'Successfully resolved the Codestructure {lock_state_file_name}'))

            except (IOError, json.JSONDecodeError, re.error) as e:
                print(outputFormatting.error(ErrorHandlers.handle_io_error(e)))

        elif action == 'plan':
            try:
                result_json = convert_to_json(merged_cst_content)
                config_match = re.search(r'configuration\s*{(.*?)}', merged_cst_content, re.DOTALL)

                if config_match:
                    config_block = config_match.group(1)
                    config_data = parse_configuration_block(config_block)
                    state_file_name = config_data.get("state_file_name", "default_state.cststate")
                    state_file_name = state_file_name
                else:
                    state_file_name = "default_state.cststate"

                initialized_state = state_file_name + ".lock"

                try:
                    state_data = load_state_file(state_file_name)
                    current_cst_data = load_state_file(initialized_state)

                    added_count, changed_count, removed_count, resource_changes = identify_resource_changes(current_cst_data, state_data)

                    if not resource_changes:
                        print(outputFormatting.valid("No resource changes found."))
                    else:
                        plan_file_name = state_file_name + ".plan"
                        with open(plan_file_name, "w") as json_file:
                            json.dump(resource_changes, json_file, indent=4)
                        print(outputFormatting.warning(f'Following resources are going to be changed:'))

                        if len(resource_changes["add"]) > 0:
                            print(outputFormatting.add(f'To add:'))
                        for resource in resource_changes["add"]:
                            print(f"{outputFormatting.add(f'')}{json.dumps(resource, indent=4)}")

                        if len(resource_changes["change"]) > 0:
                            print(outputFormatting.change(f'To change:'))
                        for resource in resource_changes["change"]:
                            print(f"{outputFormatting.change(f'')}{json.dumps(resource, indent=4)}")

                        if len(resource_changes["remove"]) > 0:
                            print(outputFormatting.remove(f'To remove:'))
                        for resource in resource_changes["remove"]:
                            print(f"{outputFormatting.remove(f'')}{json.dumps(resource, indent=4)}")


                    print(outputFormatting.info(f"{added_count} resources to be added, {changed_count} resources to be changed, {removed_count} resources to be removed."))

                except FileNotFoundError:
                    print(outputFormatting.error(f"State file not found. Ensure you have run 'codestructure read' before 'plan.'"))

            except (IOError, json.JSONDecodeError, re.error) as e:
                print(outputFormatting.error(f"Error during 'plan' action: {str(e)}"))
        
        elif action == 'deploy':
            try:
                result_json = convert_to_json(merged_cst_content)
                config_match = re.search(r'configuration\s*{(.*?)}', merged_cst_content, re.DOTALL)

                if config_match:
                    config_block = config_match.group(1)
                    config_data = parse_configuration_block(config_block)
                    subscription_id = config_data.get("subscription_id")
                    spn_object_id = config_data.get("spn_object_id")
                    spn_secret = config_data.get("spn_secret")
                    state_file_name = config_data.get("state_file_name")
                    tenant_id = config_data.get("tenant_id")
                    plan_file_name = state_file_name + ".plan"
                    lock_file_name = state_file_name + ".lock"
                else:
                    print(outputFormatting.error(f"Configuration block in state not found. Ensure you have run 'codestructure read' before 'deploy'."))

                plan_data = load_state_file(plan_file_name)
                state_file = load_state_file(state_file_name)

                add_resources = plan_data.get("add", [])
                change_resources = plan_data.get("change", [])
                remove_resources = plan_data.get("remove", [])

                while add_resources:
                    resource = add_resources[0]
                    resource_type = resource.get("resourceType")

                    try:
                        if resource_type == "resource_group":
                            deployment = create_resource_group(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                        elif resource_type == "storage_account":
                            deployment = create_storage_account(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                        else:
                            print(outputFormatting.error(f"Unsupported resource type: {resource_type}"))
                        
                        if deployment == "exists":
                            add_resources.pop(0)
                            break
                    except Exception as e:
                        print(outputFormatting.error(f"Failed to deploy resource: {str(e)}"))
                    else:
                        if deployment and deployment != "exists":
                            add_resources.pop(0)

                            state_file_resources = state_file.get("resources", [])
                            state_file_resources.append(resource)
                            state_file["resources"] = state_file_resources

                            save_file(plan_file_name, plan_data)
                            save_file(state_file_name, state_file)
                        else:
                            print(outputFormatting.error(f"State file hasn't been updated."))

                while remove_resources:
                    resource = remove_resources[0]
                    resource_type = resource.get("resourceType")

                    try:
                        if resource_type == "resource_group":
                            removal = remove_resource_group(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                        elif resource_type == "storage_account":
                            removal = remove_storage_account(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                        else:
                            print(outputFormatting.error(f"Unsupported resource type: {resource_type}"))
                    except Exception as e:
                        print(outputFormatting.error(f"Failed to remove resource: {str(e)}"))
                    else:
                        if removal:
                            remove_resources.pop(0)
                            
                            state_file_resources = state_file.get("resources", [])
                            state_file_resources.remove(resource)
                            state_file["resources"] = state_file_resources

                            save_file(plan_file_name, plan_data)
                            save_file(state_file_name, state_file)
                        else:
                            print(outputFormatting.error(f"State file hasn't been updated."))

                while change_resources:
                    resource = change_resources[0]
                    resource_type = resource.get("resourceType")
                    symbolic_link = resource.get("symbolicLink")
                    changed_properties = resource.get("changedProperties")
                    recreate_properties = ["name", "location"]

                    try:
                        recreate = False
                        for recreate_property in recreate_properties:
                            for changed_property in changed_properties:
                                if recreate_property in changed_property:
                                    recreate = True

                        if resource_type == "resource_group":
                                    
                            if recreate:
                                print(outputFormatting.warning(f"Crucial property has been changed - resource {resource_type}.{symbolic_link} is being recreated"))
                                removal = remove_resource_group(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                                if removal:
                                    deployment = create_resource_group(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                                    if deployment:
                                        update = True
                                    else:
                                        update, deployment = False, False
                                        break
                                else:
                                    update, deployment = False, False
                                    break
                            else:
                                print(outputFormatting.warning(f"Resource {resource_type}.{symbolic_link} is being updated"))
                                update = update_resource_group(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                                if update:
                                    deployment = True
                                else:
                                    update, deployment = False, False
                                    break

                        elif resource_type == "storage_account":

                            if recreate:
                                print(outputFormatting.warning(f"Crucial property has been changed - resource {resource_type}.{symbolic_link} is being recreated"))
                                removal = remove_storage_account(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                                if removal:
                                    deployment = create_storage_account(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                                    if deployment:
                                        update = True
                                    else:
                                        update, deployment = False, False
                                        break
                                else:
                                    update, deployment = False, False
                                    break
                            else:
                                print(outputFormatting.warning(f"Resource {resource_type}.{symbolic_link} is being updated"))
                                update = update_storage_account(subscription_id, spn_object_id, spn_secret, tenant_id, resource)
                                if update:
                                    deployment = True
                                else:
                                    update, deployment = False, False
                                    break

                        else:
                            print(outputFormatting.error(f"Unsupported resource type: {resource_type}"))
                    except Exception as e:
                        print(outputFormatting.error(f"Failed to update resource: {str(e)}"))
                    else:
                        if deployment and update:
                            change_resources.pop(0)

                            state_file_resources = state_file.get("resources", [])
                            matching_resource = next((r for r in state_file_resources if r.get("resourceType") == resource_type and r.get("symbolicLink") == symbolic_link), None)

                            if matching_resource:
                                resource.pop('changedProperties', None)
                                matching_resource.update(resource)

                            save_file(plan_file_name, plan_data)
                            save_file(state_file_name, state_file)
                        else:
                            print(outputFormatting.error(f"State file hasn't been updated."))
                            break


            except FileNotFoundError:
                    print(outputFormatting.error(f"State file not found. Ensure you have run 'codestructure read' before 'deploy.'"))
            
            os.remove(plan_file_name)
            os.remove(lock_file_name)
        
        else:
            print(outputFormatting.error(f"Unknown action. Try action 'help' to get more information about possible actions."))

    except Exception as e:
        print(outputFormatting.error(ErrorHandlers.handle_unexpected_error(e)))

if __name__ == '__main__':
    main()
