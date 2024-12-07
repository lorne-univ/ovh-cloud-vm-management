import json
import ovh
from time import sleep
import csv
import logging
import sys
import argparse
import os
from tabulate import tabulate
import random
import unicodedata
from dotenv import load_dotenv

"""
For creating ovh cloud instance from a csv file.
csv file exemple : 
Nom;Prénom;region;flavor;image;Adresse IP;instanceId;hostname
1;Florent;SBG5;d2-2;AlmaLinux 9;;

In Excel save file as UTF8 csv

settings : OVH Token or credential.exit()
Create the different token here : https://eu.api.ovh.com/createToken/index.cgi?GET=/*&PUT=/*&POST=/*&DELETE=/*

Settings can be set with program arguments or with environment variable.
APPLICATION_KEY=
APPLICATION_SECRET=
CONSUMER_KEY=
SERVICEID=
"""
# To set a password on a VM
# ssh -i .ssh/ovh-student debian@91.134.19.153 "echo -e 'password\npassword' | sudo passwd debian"


settings = {
    "application_key": None,
    "application_secret": None,
    "consumer_key": None,
    "serviceId": None,
}

# client : ovh client use get_client() function to get a client
client = None
# Variable to test, disable instance creation
DISABLE_INSTANCE_CREATION = False


def remove_accent(chaine: str) -> str:
    nfkd_form = unicodedata.normalize("NFKD", chaine)
    chaine = nfkd_form.encode("ASCII", "ignore").decode("utf-8")
    return chaine


def create_instance(
    name: str,
    flavorId: str,
    imageId: str,
    region: str,
    sshKeyId: str,
    monthlyBilling: bool,
) -> str:
    """
    Parameters:
    -----------
    name: the name that will be given to the instance
    flavorId: flavor e.g 'd2-2' identifier depends on the region and flavor name use get_param_id('flavor', 'd2-2', 'SBG5')
    imageId : image e.g 'AlmaLinux 9' identifier depends on the region and image name use get_param_id('image', 'AlmaLinux 9', 'SBG5')
    region : datacenter name e.g SBG5, GRA11
    sshkeyId : the sshkeyidentifier. VM will be provisionned with an sshkey

    Returns
    ------
    str instanceId or FakeInstanceId if DISABLE_INSTANCE_CREATION =TRUE
    """
    client = get_client()
    logging.debug("Create instance {} {} {} {}".format(name, region, flavorId, imageId))
    # For testing it's possible to Disable Instance Creation
    if monthlyBilling:
        monthlyBilling = True
    else:
        monthlyBilling = False

    if not DISABLE_INSTANCE_CREATION:
        instance_infos = client.post(
            f"/cloud/project/{settings['serviceId']}/instance",
            name=name,
            flavorId=flavorId,
            imageId=imageId,
            region=region,
            monthlyBilling=monthlyBilling,
            sshKeyId=sshKeyId,
        )
        instance_infos = json.dumps(instance_infos, indent=4)
        instance_infos_decoded = json.loads(instance_infos)
        print(f"Instance {name} created. Instance_id {instance_infos_decoded['id']}")
        return instance_infos_decoded["id"]
    else:
        return f"Fake-Instance-ID-{random.randrange(0,1000)} "


def get_instance_status(client, serviceName, instanceId):

    path = f"/cloud/project/{serviceName}/instance/{instanceId}"
    instance = client.get(path)
    # print(instances)
    instance = json.loads(json.dumps(instance))
    return instance["status"]


def writecsv_instance_ip(csv_file):
    """
    Read the csv file, for each line with an instanceId value find the ip
    address and write it to the file.
    csv_file : file name
    """
    logging.debug("Find and write IP address in {}".format(csv_file))
    write_rows = []
    for row in read_csv(csv_file):
        instanceId = row["instanceId"]
        ip_address = get_instance_ip(instanceId)
        logging.debug("IP address for {} is {}".format(instanceId, ip_address))
        write_rows.append(
            {
                "Nom": row["Nom"],
                "Prénom": row["Prénom"],
                "region": row["region"],
                "flavor": row["flavor"],
                "image": row["image"],
                "instanceId": row["instanceId"],
                "Adresse IP": ip_address,
            }
        )
    write_csv(csv_file, write_rows)


def get_instance_ip(instanceId):
    """
    serviceName : id projet cloud : pour Com-Lycee : 81d63e9494aa4029866afdc3d5623c3d
    """
    client = get_client()
    path = f"/cloud/project/{settings['serviceId']}/instance/{instanceId}"
    ip_address = None
    i = 0
    while ip_address == None and i < 60:
        instance = json.loads(json.dumps(client.get(path)))
        try:
            ip_address = instance["ipAddresses"][0]["ip"]
        except IndexError:
            sleep(1)
            i += 1
        print(
            f"IP found in {i} second {instance['name']} {instance['id']} {ip_address}"
        )
    if ip_address is not None:
        return ip_address
    else:
        print(f"Instance : {instanceId} IP address not found")
        return None


def delete_instance(instanceId):
    logging.debug("Deleting instance {}".format(instanceId))
    client = get_client()
    path = f"/cloud/project/{settings['serviceId']}/instance/{instanceId}"
    client.delete(path)


def read_csv(filename):
    """
    Return each row of the csv as a dictionnary
    """
    try:
        with open(filename, "r", encoding="utf-8-sig") as monfile:
            myccsv = csv.DictReader(monfile, delimiter=";")
            for row in myccsv:
                try:
                    yield (row)
                except:
                    print("Closing file {}".format(filename))
                    monfile.close()
                    sys.exit(2)
    except FileNotFoundError:
        print(f"Can't open file {filename}")
        sys.exit(2)


def check_region(region):
    logging.info("Check region")
    regions = ["GRA", "GRA11", "RBX", "RBX-A", "SBG", "SBG5"]
    if region not in regions:
        return False, f"Your region : {region}. Available regions {regions}"
    else:
        return True, f"{region} in {regions}"


def check_flavor(flavor):
    logging.info("Check flavor")
    client = get_client()
    path = f"/cloud/project/{settings['serviceId']}/flavor"
    flavors = json.loads(json.dumps(client.get(path), indent=4))
    for flavor_available in flavors:
        if flavor in flavor_available["name"]:
            return True, f"{flavor} found in available flavors"

    return False, f"{flavor} not found in available flavors"


def check_instanceId(instanceId):
    """
    For creation instanceId must be null
    """
    logging.debug("Check InstanceId")
    if instanceId != "":
        return False, f"InstanceId : {instanceId} is not null."
    else:
        return True, f"InstanceId is null"


def check_image(image):
    """
    Check if image exists
    """
    logging.info("Check image")
    client = get_client()
    path = f"/cloud/project/{settings['serviceId']}/image"
    images = json.loads(json.dumps(client.get(path), indent=4))
    for image_available in images:
        if image in image_available["name"]:
            return True, f"{image} found in available images"

    return False, f"{image} not found in available images"


def csv_file_validation(fileName):
    """
    Function to validate the file format
    The csv file must contain three columns
    - Nom : name of the person
    - Prénom : first name
    - instanceId : empty columns
    - region
    - flavor
    - image
    - hostname
    """
    # List of all fields that must be presents
    # If the value is True, the fields must contains a value
    attended = {
        "Nom": {"notnull": False, "checkfunction": False},
        "Prénom": {"notnull": True, "checkfunction": False},
        "instanceId": {"notnull": False, "checkfunction": check_instanceId},
        "region": {"notnull": True, "checkfunction": check_region},
        "flavor": {"notnull": True, "checkfunction": check_flavor},
        "image": {"notnull": True, "checkfunction": check_image},
        "hostname": {"notnull": False, "checkfunction": False},
    }
    gen = read_csv(fileName)
    # For each row of the csv
    for i, row in enumerate(gen):
        for key in attended.keys():
            # Check if there is a key in row dictionnary
            if key in row:
                if attended[key]["notnull"]:
                    if not row.get(key):
                        print(
                            f"Line {i}. There isn't a value for the {key}. Row values :  {row.values()}"
                        )
                        gen.close()
                        sys.exit(2)
                if attended[key]["checkfunction"]:
                    # Call of the checkfunction with the value of the row or False
                    condition, reason = attended[key]["checkfunction"](
                        row.get(key, False)
                    )
                    if not condition:
                        print(f"Line {i}. {reason}")
                        gen.close()
                        sys.exit(2)
            else:
                print(
                    f"Line {i}. There isn't a {key} field. Row values :  {row.values()}"
                )
                gen.close()
                sys.exit(2)


def write_csv(filename, lines_dict):
    """
    filename : name of the file to write
    lines_dict : all the lines [{'Nom':'nom1', 'Prénom':'Prénom1', 'Adresse IP': '192.168.15.1', 'instanceId': 'instanceId1', 'hostname'},{'Nom':'nom2', 'Prénom':'Prénom2', 'Adresse IP': '192.168.15.1', 'instanceId': 'instanceId1'}]
    """
    fieldnames = [
        "Nom",
        "Prénom",
        "region",
        "flavor",
        "image",
        "Adresse IP",
        "instanceId",
        "hostname",
    ]
    with open(filename, "w", encoding="utf-8-sig", newline="") as monfile:
        myccsv = csv.DictWriter(monfile, delimiter=";", fieldnames=fieldnames)
        myccsv.writeheader()
        for row in lines_dict:
            myccsv.writerow(row)


def get_param_id(param_name: str, param: str, region: str) -> str:
    """
    To get flavor or image depending on the region
    param_name: string e.g 'flavor', 'image'
    param : value of the param, e.g 'd2-2' or 'AlmaLinux 9'
    region : datacenter e.g  'SBG5', 'GRA11'
    """
    logging.debug(
        "get_param_id. param_name : {}, param : {} ".format(param_name, param)
    )
    client = get_client()
    path = f"/cloud/project/{settings['serviceId']}/{param_name}"
    params = json.loads(json.dumps(client.get(path), indent=4))
    for param_available in params:
        if param == param_available["name"] and region == param_available["region"]:
            id = param_available["id"]
            logging.debug("{} {} {}".format(param_name, param, id))
            return id

    print(f"Can't find {param_name} ID for {param} and region {region} ")


def create_instances_from_csv(fileName, sshKeyId, monthlyBilling):
    """
    Create an instance for each users in the csv file.
    instance name will be the user firstname (Prénom) prefixed by pc-
    The instanceId column will be updated by the instanceId created

    client: ovh.Client instance
    serviceName : id of the cloud project
    fileName : path of the csv file
    The csv file must contains 3 columns :
    - Nom : name of the person
    - Prénom : first name
    - instanceId : empty columns
    - region
    - flavor
    - image
    """
    # List of rows to write in the csv file
    write_rows = []

    # Declare a generator
    csv_file_validation(fileName)
    gen = read_csv(fileName)
    for row in gen:
        prenom = row.get("Prénom").strip().lower()
        prenom = remove_accent(prenom)
        nom = row.get("Nom").strip().lower()
        logging.debug("Creating instance for {}".format(prenom))
        instanceId = create_instance(
            name="pc-" + prenom,
            flavorId=get_param_id("flavor", row["flavor"], row["region"]),
            imageId=get_param_id("image", row["image"], row["region"]),
            region=row["region"],
            sshKeyId=sshKeyId,
            monthlyBilling=monthlyBilling,
        )
        logging.debug(
            "Creating instance : {} {} {}".format(
                nom.capitalize(), prenom.capitalize(), instanceId
            )
        )

        write_rows.append(
            {
                "Nom": nom.capitalize(),
                "Prénom": prenom.capitalize(),
                "region": row["region"],
                "flavor": row["flavor"],
                "image": row["image"],
                "instanceId": instanceId,
                "Adresse IP": "",
                "hostname": "",
            }
        )
    write_csv(fileName, write_rows)


def check_serviceId():
    """
    Check if serviceId correspond to an existing service

    """
    client = get_client()
    path = "/cloud/project"
    services = json.loads(json.dumps(client.get(path), indent=4))
    for service in services:
        if service == settings["serviceId"]:
            return True
    print(f"No service found with serviceId : {settings['serviceId']}")
    return False


def delete_instance_from_csv(fileName):
    gen = read_csv(fileName)
    for row in gen:
        instanceId = row.get("instanceId", False)
        if instanceId:
            print(f"Delete instance {instanceId} in {fileName}")
            delete_instance(instanceId)


def list_ssh_key():
    client = get_client()
    path = f"/cloud/project/{settings['serviceId']}/sshkey"
    ssh_keys = json.loads(json.dumps(client.get(path), indent=4))
    print("Available ssh keys : ")
    data = []
    for key in ssh_keys:
        data.append([key["name"], key["id"]])
    print(tabulate(data, tablefmt="grid"))


def get_ssh_key_id(sshkey_name):
    client = get_client()
    path = f"/cloud/project/{settings['serviceId']}/sshkey"
    ssh_keys = json.loads(json.dumps(client.get(path), indent=4))
    ssh_key_id = ""
    for key in ssh_keys:
        if key["name"] == sshkey_name:
            ssh_key_id = key["id"]
            break
    if ssh_key_id != "":
        return ssh_key_id
    else:
        print(f"Can't find an ssh-key named {sshkey_name}")
        list_ssh_key()
        sys.exit(2)


def getArgs(argv=None):
    parser = argparse.ArgumentParser(
        prog="Cloud-Instance Management",
        description="""Manage ovh cloud instances from csv file.\n
        CSV File header : Nom;Prénom;region;flavor;image;Adresse IP;instanceId
        """,
        epilog="Thanks for using",
    )
    parser.add_argument("-f", dest="fileName", required=True, help="The csv filename")
    parser.add_argument(
        "--key",
        dest="application_key",
        help="The application key. https://eu.api.ovh.com/createToken/index.cgi?GET=/*&PUT=/*&POST=/*&DELETE=/*",
    )
    parser.add_argument(
        "--secret", dest="application_secret", help="The application secret "
    )
    parser.add_argument("--cons", dest="consumer_key", help="The consumer secret ")
    parser.add_argument(
        "-a",
        required=True,
        dest="action",
        choices=["create", "delete", "get_ip"],
        help="The action to perfom. action=c -> create instance, action=d -> delete instance, action=ip -> get ip addresses",
    )
    parser.add_argument(
        "--monthlyBilling",
        dest="monthlyBilling",
        default=False,
        choices=["True", "False"],
        help="If we pay for a month",
    )
    parser.add_argument(
        "--service",
        dest="serviceId",
        help="ServiceId the cloud ovh project number.",
    )
    parser.add_argument(
        "--ssh",
        required=True,
        dest="ssh_key",
        help="ssh key name that will be provisionned inside the vm.",
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        choices=["info", "debug", "none"],
        help="debug value, if not specified no debug",
    )
    return parser


def get_client():
    global client
    if client is None:
        client = ovh.Client(
            endpoint="ovh-eu",  # Endpoint of API OVH Europe (List of available endpoints)
            application_key=settings["application_key"],  # Application Key
            application_secret=settings["application_secret"],  # Application Secret
            consumer_key=settings["consumer_key"],  # Consumer Key
        )
    return client


if __name__ == "__main__":
    """
    Token creation page : https://eu.api.ovh.com/createToken/index.cgi?GET=/*&PUT=/*&POST=/*&DELETE=/*
    """
    args = vars(getArgs().parse_args())

    debug_value = args.get("debug", False)
    if debug_value == "debug":
        logging.basicConfig(level=logging.DEBUG)
    elif debug_value == "info":
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=None)

    """
    Settings can be passed with program argument or with 
    environment variable.
    """
    load_dotenv()
    for setting in settings:
        if args[setting]:
            settings[setting] = args[setting]
        elif os.environ.get(setting.upper()):
            settings[setting] = os.environ[setting]
            logging.debug("setting {} set in environment variable".format(setting))
        else:
            print(
                f"No value for {setting}. Enter one as argument or define one as environment variable : {setting.upper()}=."
            )
            sys.exit(2)

    client = get_client()

    if not check_serviceId():
        sys.exit(2)

    if args.get("monthlyBilling") == "true" or args.get("monthlyBilling") == "True":
        monthlyBilling = True
    else:
        monthlyBilling = False

    if args["action"] == "create":
        print("create")
        print(f"")
        sshKeyId = get_ssh_key_id(sshkey_name=args["ssh_key"])
        create_instances_from_csv(args["fileName"], sshKeyId, monthlyBilling)
    elif args["action"] == "delete":
        delete_instance_from_csv(args["fileName"])
    elif args["action"] == "get_ip":
        writecsv_instance_ip(args["fileName"])

    else:
        print("No action found")
