import json
import ovh
from pprint import pprint
from dotenv import load_dotenv
import os

"""
This module is used to list
- region
- flavors (CPU/RAM/Discovery..)
- images
- ssh-keys
Modify main function to list what you want
"""


def list_my_regions(client, service):
    result = client.get(f"/cloud/project/{service['id']}/region")
    result_json = json.dumps(result, indent=4)
    result_decoded = json.loads(result_json)  # Transform json into python object
    for region in result_decoded:
        print(f"{region}")


def get_infos_region(client, service, region_name):
    result = client.get(f"/cloud/project/{service['id']}/region/{region_name}")
    result_json = json.dumps(result, indent=4)
    # result_decoded = json.loads(result_json)  # Transform json into python object
    print(f"{result_json}")


def list_flavors(client, service, name, region):
    result = client.get(f"/cloud/project/{service['id']}/flavor")
    result_json = json.dumps(result, indent=4)
    result_decoded = json.loads(result_json)  # Transform json into python object
    for flavor in result_decoded:
        if name in flavor["name"] and flavor["region"] == region:
            print(f"{flavor}")


def list_images(client, serviceName, image_name, region):
    """
    image_name: the beginning of the image name
    region : the region
    """
    images = client.get(f"/cloud/project/{serviceName['id']}/image")
    images_json = json.dumps(images, indent=4)
    images_decoded = json.loads(images_json)  # Transform json into python object
    for image in images_decoded:
        if image_name in image["name"] and image["region"] == region:
            print(f"{image}")


def list_ssh_key(client, serviceName):
    path = f"/cloud/project/{serviceName['id']}/sshkey"
    ssh_keys = json.loads(json.dumps(client.get(path), indent=4))
    for key in ssh_keys:
        print(f"{key['id']}  {key['name']}")


if __name__ == "__main__":
    load_dotenv()

    application_key = os.getenv("APPLICATION_KEY")
    application_secret = os.getenv("APPLICATION_SECRET")
    consumer_key = os.getenv("CONSUMER_KEY")
    service_id = os.getenv("SERVICEID")
    client = ovh.Client(
        endpoint="ovh-eu",  # Endpoint of API OVH Europe (List of available endpoints)
        application_key=application_key,  # Application Key
        application_secret=application_secret,  # Application Secret
        consumer_key=consumer_key,  # Consumer Key
    )
    serviceName = {"id": service_id, "name": "Com-Lycee"}
    # list_my_regions(client, serviceName)
    # get_infos_region(client, serviceName, "SBG5")
    # list_flavors(client, serviceName, "d2-2", "SBG5")
    list_images(client, serviceName, "Debian", "SBG5")
    # list_ssh_key(client, serviceName)
