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
        df.loc['sUSD','supply'] = df.loc['sUSD','supply'] - multiUSD - wrapprUSD - oldLoanUSD
        
        #compute market cap
        df["cap"]     = df["price"] * df["supply"]
        marketCapAbs = np.abs(df["cap"]).sum()
        df["debt_pool_percentage"] = np.abs(df["cap"] / marketCapAbs)
        otherDF = df[df["debt_pool_percentage"] < 0.05].sum()
        
        #update ETH to short ETH if it's negative
        if df.loc["sETH","cap"] < 0:
            df.rename(index={'sETH':'Short sETH'},inplace=True)            

        #Group small things
        df = df[df["debt_pool_percentage"] >= 0.05]
        df.loc['other','cap']                  = otherDF["cap"]
        df.loc['other','debt_pool_percentage'] = otherDF["debt_pool_percentage"]
        df.loc['other','debt_pool_percentage'] = otherDF["debt_pool_percentage"]
        df.loc['other','supply']               = 0
        
        #other formatting
        df["synth"]       = df.index
        df.rename(columns={'supply':'units'},
                  inplace=True)
        df["cap"]  = df["cap"].astype(float)
        df["debt_pool_percentage"] = df["debt_pool_percentage"].astype(float)
        df = df[['synth','units','cap','debt_pool_percentage']]
        df.sort_values(by=['debt_pool_percentage'],inplace=True,ascending=False)

        return df
                
    def getSynthMarketCap(self):
        #get synth list
        utilsContract     = self.getContract('SynthUtil')
        synthSupplyList   = utilsContract.functions.synthsTotalSupplies().call()
        synthDF           = pd.DataFrame(synthSupplyList).T
        synthDF.columns   = columns=['synthHex','supply','cap']
        synthDF["synth"]  = synthDF["synthHex"].str.decode('utf-8').str.replace('\x00','')
        synthDF           = synthDF.query("supply > 0").copy()
        synthDF["price"]  = synthDF["cap"] / synthDF["supply"]
        synthDF["cap"]    = synthDF["cap"] / 1e24
        synthDF["supply"] = synthDF["supply"] / 1e24
        return synthDF
            
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