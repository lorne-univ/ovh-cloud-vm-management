# A couple of tools to manage cloud ovh vm

## pip
pip install ovh
ovh==1.1.0

## Main program : csv-ovh-vm.py

For creating ovh cloud instance from a csv file.
The csv file exemple : 
```
Nom;Prénom;region;flavor;image;Adresse IP;instanceId
Nom1;prenom1;SBG5;d2-2;AlmaLinux 9;;
```
| Nom       | Prénom    | region | flavor | image     | Adresse IP    | instanceId                           |
|-----------|-----------|--------|--------|-----------|---------------|--------------------------------------|
| Nom1      | Prénom1   | SBG5   | d2-2   | Debian 10 |               |                                      |
| Nom2      | Prénom2   | GRA11  | d2-2   | AlmaLinux 9|              |                                      |      

It's possible to use Excel. Save file with CSV UTF-8 Format.
The expected format is a DOS/WINDOWS one with BOM character.

settings : OVH Token or credential.

Create the different token here : https://eu.api.ovh.com/createToken/index.cgi?GET=/*&PUT=/*&POST=/*&DELETE=/*

Settings can be set with program arguments or with environment variable.
APPLICATION_KEY=
APPLICATION_SECRET=
CONSUMER_KEY=
SERVICEID=

Exemple de commande :
```
python.exe .\csv-ovh-vm.py -f 'C:\Users\flore\OneDrive - Université Savoie Mont Blanc\Enseignements\Journée Immersion Lycéen\mars-2024.csv' --key 82c9614cbf98a9ae --secret dde64253988ad0d6d335f261bce84843 --cons 3a8b74c7c98ea651798c0be578ded153 -a create --service 81d63e9494aa4029866afdc3d5623c3d --ssh ovh-student
```

Check constant : DISABLE_INSTANCE_CREATION = False

## Secondary program : cloud-parameters-list.py
Use this to determine flavor, region, image...
