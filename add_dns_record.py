#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import json
import ovh
from dotenv import load_dotenv
import os
import logging
from csv_ovh_vm import write_csv
from csv_ovh_vm import read_csv
from csv_ovh_vm import remove_accent

"""
ADD DNS RECORD IN ZONE - By default in zone 
"""


def add_dns_A_record(domain_zone, name, address, keys):
    """
    domain_zone: univ-lorawan.fr or univ-tri.fr
    name: name of the record florent for florent.univ-tri.fr
    address: ipv4 address for the record
    keys: {'application_key':value, 'application_secret': value, consumer_key:'value'}
    keys: {'application_key':value, 'application_secret': value, }
    """
    logging.info("add_dns_A_record {}.{} -> {} ".format(name, domain_zone, address))
    application_key = keys.get("application_key")
    application_secret = keys.get("application_secret")
    consumer_key = keys.get("consumer_key")

    # Creation Token : https://eu.api.ovh.com/createToken
    client = ovh.Client(
        endpoint="ovh-eu",  # Endpoint of API OVH Europe (List of available endpoints)
        application_key=application_key,  # Application Key
        application_secret=application_secret,  # Application Secret
        consumer_key=consumer_key,  # Consumer Key
    )

    result = client.post(
        f"/domain/zone/{domain_zone}/record",
        fieldType="A",
        subDomain=f"{name}",
        target=f"{address}",
    )

    print(
        f"Creating record {result.get('subDomain')}.{result.get('zone')}->{result.get('target')}"
    )
    result = client.post(f"/domain/zone/{domain_zone}/refresh")


def add_dns_A_record_csv(domain_zone, keys, csv_file):
    """
    ADD dns record for all row in csv_file

    """
    logging.debug("ADD dns from csv {}".format(csv_file))
    write_rows = []
    for row in read_csv(csv_file):
        ip_address = row.get("Adresse IP")
        prenom = row.get("Prénom").strip().lower()
        prenom = remove_accent(prenom)
        first_letter_nom = row.get("Nom").strip().lower()[0]
        if ip_address != None and prenom != None:
            add_dns_A_record(
                domain_zone,
                name=f"{prenom}-{first_letter_nom}",
                address=ip_address,
                keys=keys,
            )
            write_rows.append(
                {
                    "Nom": row["Nom"],
                    "Prénom": row["Prénom"],
                    "region": row["region"],
                    "flavor": row["flavor"],
                    "image": row["image"],
                    "instanceId": row["instanceId"],
                    "Adresse IP": row["Adresse IP"],
                    "hostname": f"{prenom}-{first_letter_nom}",
                }
            )
    write_csv(csv_file, write_rows)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    application_key = os.getenv("APPLICATION_KEY_DNS")
    application_secret = os.getenv("APPLICATION_SECRET_DNS")
    consumer_key = os.getenv("CONSUMER_KEY_DNS")
    keys = {
        "application_key": application_key,
        "application_secret": application_secret,
        "consumer_key": consumer_key,
    }
    # add_dns_A_record(
    #     "univ-lorawan.fr",
    #     "test4",
    #     "8.8.8.9",
    #     {
    #         "application_key": application_key,
    #         "application_secret": application_secret,
    #         "consumer_key": consumer_key,
    #     },
    # )
    add_dns_A_record_csv(
        "univ-lorawan.fr",
        keys,
        "C:\\Users\\flore\\OneDrive - Université Savoie Mont Blanc\\LoRaWAN\\Formations\\2024-12\\liste_candidats_decembre_2024.csv",
    )
