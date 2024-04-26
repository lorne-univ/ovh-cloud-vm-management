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

Exemples de commande :
```
#Creating vm from csv
python.exe .\csv-ovh-vm.py -f 'C:\Users\flo\mars-2024.csv' --key YYYYY --secret XXXXXX --cons WWWWW -a create --service ZZZZZ --ssh ovh-student

#Getting ip address and filling csv
python.exe .\csv-ovh-vm.py -f 'C:\Users\flo\mars-2024.csv' --key YYYYY --secret XXXXXX --cons WWWWW -a get_ip --service ZZZZZ --ssh ovh-student

#Delete vm
python.exe .\csv-ovh-vm.py -f 'C:\Users\flo\mars-2024.csv' --key YYYYY --secret XXXXXX --cons WWWWW -a delete --service ZZZZZ --ssh ovh-student
```

Check constant : DISABLE_INSTANCE_CREATION = False

## Secondary program : cloud-parameters-list.py
Use this to determine flavor, region, image...
