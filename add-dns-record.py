#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
import json
import ovh
from dotenv import load_dotenv
import os


load_dotenv()

application_key = os.getenv("APPLICATION_KEY")
application_secret = os.getenv("APPLICATION_SECRET")
consumer_key = os.getenv("CONSUMER_KEY")

# Creation Token : https://eu.api.ovh.com/createToken
client = ovh.Client(
    endpoint="ovh-eu",  # Endpoint of API OVH Europe (List of available endpoints)
    application_key=application_key,  # Application Key
    application_secret=application_secret,  # Application Secret
    consumer_key=consumer_key,  # Consumer Key
)


result = client.post(
    "/domain/zone/usmb-tri.fr/record",
    fieldType="A",
    subDomain="test6",
    target="101.101.101.4",
)

# Pretty print
print(json.dumps(result, indent=4))
result = client.post("/domain/zone/usmb-tri.fr/refresh")
print(json.dumps(result, indent=4))
