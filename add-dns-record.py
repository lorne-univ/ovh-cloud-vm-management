#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import json
import ovh
from dotenv import load_dotenv
import os

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

    # Pretty print
    print(json.dumps(result, indent=4))
    result = client.post(f"/domain/zone/{domain_zone}/refresh")
    print(json.dumps(result, indent=4))
