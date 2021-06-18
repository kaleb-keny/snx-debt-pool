from utils.snxContracts import snxContracts
import numpy as np
import time
import pandas as pd

class debtComp(snxContracts):
    def __init__(self,conf,resolver):
        
        super().__init__(conf=conf,
                         resolver=resolver)
            
    def startBot(self):
        while True:
            try:
                
                df = self.gatherData()            
                self.sendEmbed(title='Debt Pool Composition',
                               description='Please note that negative market cap numbers means that the hedge requires a short position.',
                               df=df)
                
                time.sleep(60*60)
                
            except KeyboardInterrupt:
                print("quitting")
                break
            
            except Exception as e:
                print(f"Exception seen {e}")
            
            
    
    
    def gatherData(self):
                                        
        df         = self.getSynthMarketCap()
        df.set_index(keys=['synth'],inplace=True)

        #remove short and borrows of eth
        multiETH   = self.getMultiCollateralIssuance(currencyKey='sETH')
        oldLoanETH = self.getOldLoansETH()
        wrapprETH  = self.getWrapprETH()
        df.loc['sETH','supply'] = df.loc['sETH','supply'] - multiETH - wrapprETH - oldLoanETH

        #remove short and borrows of btc
        multiBTC  = self.getMultiCollateralIssuance(currencyKey='sBTC')
        df.loc['sBTC','supply'] = df.loc['sBTC','supply'] - multiBTC

        #remove borrows of usd and wrappr sUSD
        multiUSD    =   self.getMultiCollateralIssuance(currencyKey='sUSD')
        oldLoanUSD  = self.getOldLoansUSD()
        wrapprUSD   = self.getWrapprUSD()
        df.loc['sUSD','supply'] = df.loc['sBTC','supply'] - multiUSD - wrapprUSD - oldLoanUSD
        
        #compute market cap
        df["market cap"]     = df["price"] * df["supply"]
        marketCapAbs = np.abs(df["market cap"]).sum()
        df["debt pool %"] = np.abs(df["market cap"] / marketCapAbs)
        otherDF = df[df["debt pool %"] < 0.05].sum()
        
        #update ETH to short ETH if it's negative
        if df.loc["sETH","market cap"] < 0:
            df.rename(index={'sETH':'Short sETH'},inplace=True)            

        #Group small things
        df = df[df["debt pool %"] >= 0.05]
        df.loc['other','market cap']  = otherDF["market cap"]
        df.loc['other','debt pool %'] = otherDF["debt pool %"]
        
        #other formatting
        df["synth"] = df.index
        df["market cap"]  = df["market cap"].astype(float)
        df["debt pool %"] = df["debt pool %"].astype(float)
        df["market cap (sUSD millions)"] = df["market cap"]
        df = df[['synth','market cap (sUSD millions)','debt pool %']]
        df.sort_values(by=['debt pool %'],inplace=True,ascending=False)

        return df
                
    def getSynthMarketCap(self):
        #get synth list
        snxContract       = self.getContract('Synthetix')
        synthListHex      = snxContract.functions.availableCurrencyKeys().call()
        synthList         = [synth.decode().replace('\x00','') for synth in synthListHex]
        synthDF           = pd.DataFrame(synthList,columns=['synth'])
        synthDF["supply"] = synthDF["synth"].apply(self.getSynthSupply)
        synthDF["price"]  = self.getSynthPrices(synthListHex)
        synthDF["price"]  = synthDF["price"]  / 1e18
        return synthDF
        
    def getSynthSupply(self,synth):
        if synth == 'sUSD':
            contract = self.getContract(contractName = 'ProxyERC20sUSD')
        else:
            contract = self.getContract(contractName = f'Proxy{synth}')

        return contract.functions.totalSupply().call() / 1e24

    def getSynthPrices(self,synthListHex):
        contract = self.getContract(contractName = 'ExchangeRates')
        return contract.functions.ratesForCurrencies(synthListHex).call()
    
    def getWrapprETH(self):
        contract = self.getContract(contractName = 'EtherWrapper')
        return contract.functions.sETHIssued().call() / 1e24
    
    def getWrapprUSD(self):
        contract = self.getContract(contractName = 'EtherWrapper')
        return contract.functions.sUSDIssued().call() / 1e24

    def getMultiCollateralIssuance(self,currencyKey):
        contract = self.getContract(contractName = 'CollateralManagerState')
        currency = self.w3.toHex(text=f'{currencyKey}')
        longs, shorts = contract.functions.totalIssuedSynths(currency).call()
        return (longs + shorts)/1e24
    
    def getOldLoansETH(self):
        contract = self.getContract(contractName = 'EtherCollateral')
        return contract.functions.totalIssuedSynths().call() / 1e24
        
    def getOldLoansUSD(self):
        contract = self.getContract(contractName = 'EtherCollateralsUSD')
        return contract.functions.totalIssuedSynths().call() / 1e24

                    

#%%
if __name__ == '__main__':
    debt = debtComp(conf=conf,resolver=resolver)
    self=debt