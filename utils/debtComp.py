from utils.snxContracts import snxContracts
import numpy as np
import time
import pandas as pd
from collections import namedtuple
from scipy.optimize import minimize

class debtComp(snxContracts):
    def __init__(self,conf,resolver):
        
        super().__init__(conf=conf,
                         resolver=resolver)
        
        self.leverage = namedtuple(typename='lvg', 
                                   field_names=['synth',
                                                'leverage',
                                                'adjusted_debt_pool_percentage'])
        
    def startBot(self):
        while True:

            try:
                
                df = self.gatherData()                            
                dfLeveraged = self.getLeveragedAdjustedDF(df=df)
                                
                            
                self.sendStandard(title='Debt Pool Composition',
                                  description='Please note that negative market cap numbers means that the hedge requires a short position.',
                                  df=df)

                self.sendLeverage(title='Debt Pool Composition - Leverage Adjusted',
                                  description='The below weights on non-stable synths can be used to mirror to debt pool and hedge against a 20% swing in prices.',
                                  df=dfLeveraged)
            
                
                time.sleep(12*60*60)
                
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
        
        #update ETH to short ETH if it's negative
        if df.loc["sETH","cap"] < 0:
            df.rename(index={'sETH':'Short sETH'},inplace=True)            
        
        #other formatting
        df["synth"]       = df.index
        df.rename(columns={'supply':'units'},
                  inplace=True)
        df["cap"]  = df["cap"].astype(float)
        df["debt_pool_percentage"] = df["debt_pool_percentage"].astype(float)
        df.sort_values(by=['debt_pool_percentage'],inplace=True,ascending=False)

        return df
    
    
    def getLeveragedAdjustedDF(self,df):
        
        breakCounter = 1
        resultList   = list()
        
        #run on a number of shocks
        shockList = np.linspace(-0.2,0.2,20)
        
        #assume nothing changes
        df["shockedPrice"]  = df["price"]
        
        #save it in memory for the optimizer
        self.df = df.copy()
        
        for synth, data in df.iterrows():
            if not synth in ['sUSD','sEUR','other']:
                leverage = 0
                #shock the price
                for shock in shockList:
                    #get the leverage
                    result = minimize(fun=self.netDebt,
                                      args=[df,synth,shock],
                                      method='SLSQP',
                                      x0=1.1)
                    
                    leverage += result.x[0] / len(shockList)
                
                #save the result
                resultList.append(self.leverage(synth=synth,
                                                leverage=leverage,
                                                adjusted_debt_pool_percentage=data.debt_pool_percentage*leverage))
                
                breakCounter += 1
                    
                if breakCounter ==5 :
                    break
        return pd.DataFrame(resultList)

    def netDebt(self,leverage,args):
                
        df, synth,shock = args
        
        #update price of shocked synth
        df.loc[synth,"shockedPrice"] = df.loc[synth,"price"] * (1+shock)
        
        #get shocked new cap
        df["shockedCap"]             = df["units"] * df["shockedPrice"]
        
        #get shocked debt pool percentage (representing 1$ being invested) or a users' that mirrors debt pool synth
        df["shocked_user_synth"] = df["debt_pool_percentage"] * \
                                        df.apply(lambda x: x.shockedPrice / x.price if x.units > 0 else 2 - x.shockedPrice / x.price, axis=1) * \
                                            leverage

        #get user's shocked debt & synths
        debt  = df["shockedCap"].sum() / df["cap"].sum()
        synth = df["shocked_user_synth"].sum()
                
        return abs(synth - debt)
        
                            
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