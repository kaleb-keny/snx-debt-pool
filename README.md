# SNX Debt Pool Composition
The repo contains the tools necessary to find the outstanding composition of the snx debt pool:

## Prerequisites

The code needs miniconda, as all packages were installed and tested on conda v4.9.2. Installation of miniconda can be done by running the following:

```
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -p $HOME/miniconda3
```

## Installing Environment

The enviroment files are available under env folder. Enviroment setup can be done with the one of the below actions:

```
conda env create --name debtPool --file=environment.yaml
```

## Conf File

Note the below conf file needs to be appended under config as conf.yaml, containing the following:
- a infura api key
- a etherscan api key
- a discord webhook api 

```
---
infura: 
    http:  "https://mainnet.infura.io/v3/"  
    key:  
        - "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    
etherscan: 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

discord: 'https://discord.com/api/webhooks/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```

## Running the model

To launch the programsimply run the following:

```
conda activate debtPool
python main.py -t launch
```

The debt pool composition will be sent to the webhook every hour.
