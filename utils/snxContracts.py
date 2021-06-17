import requests
import web3 as W3 
from itertools import cycle
from collections import defaultdict
from utils.discordBot import discordBot

class snxContracts(discordBot):
    
    def __init__(self,conf,resolver):
        
        super().__init__(conf=conf)

        self.infuraKeys = cycle(self.conf["infura"]["key"])
        self.resolver   = resolver        
        self.contracts  = defaultdict(dict)
        self.w3         = self.getW3()
                        
    def getContract(self,contractName):

        w3      = self.getW3()
        if contractName in self.contracts.keys():
            address = self.contracts[contractName]["address"]
            abi     = self.contracts[contractName]["abi"]

            return w3.eth.contract(address=address,
                                   abi=abi)        
        
        proxyResolverContract = w3.eth.contract(address=self.resolver["address"],
                                                abi=self.resolver["abi"])
        
        resolverAddress = proxyResolverContract.functions.target().call()
        resolverABI     = self.getABI(resolverAddress)  
        
        resolverContract = w3.eth.contract(address=resolverAddress,
                                           abi=resolverABI)

        contractNameHex = w3.toHex(text=contractName)
        address         = resolverContract.functions.getAddress(contractNameHex).call()
        abi             = self.getABI(address)
        
        self.contracts[contractName]["address"] = address
        self.contracts[contractName]["abi"]     = abi

        return w3.eth.contract(address=address,
                               abi=abi)
            
    def getABI(self,address):
        etherscanKey = self.conf["etherscan"]
        link = f'https://api.etherscan.io/api?module=contract&action=getabi&address={address}&apikey={etherscanKey}'
        return requests.get(link).json()["result"]
    
    def getW3(self):
        key = next(self.infuraKeys)
        key = self.conf["infura"]["http"] + key
        return W3.Web3(W3.HTTPProvider(key))
        
#%%        
if __name__ == '__main__':    
    contracts = snxContracts(conf,resolver)
    self = contracts