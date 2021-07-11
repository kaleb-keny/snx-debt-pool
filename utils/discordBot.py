from discord import Webhook, RequestsWebhookAdapter,Embed

class discordBot():
    
    def __init__(self,conf):
        self.conf = conf
        self.hook = conf["discord"]


    def sendStandard(self,description,df,title=None):

        #Group small things
        otherDF = df[df["debt_pool_percentage"] < 0.05].sum()
        df = df[df["debt_pool_percentage"] >= 0.05]
        df.loc['other','cap']                  = otherDF["cap"]
        df.loc['other','debt_pool_percentage'] = otherDF["debt_pool_percentage"]
        df.loc['other','debt_pool_percentage'] = otherDF["debt_pool_percentage"]
        df.loc['other','supply']               = 0
        df = df[['synth','units','cap','debt_pool_percentage']].copy()
        
        webhook = Webhook.from_url(self.hook, adapter=RequestsWebhookAdapter())
        e = Embed(title=title, description=description)
                
        #shoot the synth
        valueString  = ''
        for value in df.index:
            valueString =  valueString +  "\n" + value

        e.add_field(name="target \n synth",
                    value=valueString,
                    inline=True)

        #shoot the units and cap
        valueString  = ''
        for units, cap in zip(df["units"],df["cap"]):
            valueString =  valueString +  "\n" + str("{:,}".format(round(cap,2))) + "/" + str("{:,}".format(round(units,5))) 

        e.add_field(name="cap in dollars and units\n (millions)", 
                    value=valueString,
                    inline=True)
        
        #shoot the units and cap
        valueString  = ''
        for value in df["debt_pool_percentage"]:
            valueString =  valueString +  "\n" + str("{:.0%}".format(value))

        e.add_field(name="debt pool \n (%)", 
                    value=valueString,
                    inline=True)
    
        webhook.send(embed=e)

    def sendLeverage(self,description,df,title=None):
        
        #filter large synths
        df = df[df["adjusted_debt_pool_percentage"] > 0.05].copy()

        webhook = Webhook.from_url(self.hook, adapter=RequestsWebhookAdapter())
        e = Embed(title=title, description=description)
                
        #shoot the synth
        valueString  = ''
        for value in df["synth"]:
            valueString =  valueString +  "\n" + value

        e.add_field(name="target \n synth",
                    value=valueString,
                    inline=True)

        #shoot debt pool percentage
        valueString  = ''
        for value in df["adjusted_debt_pool_percentage"]:
            valueString =  valueString +  "\n" + str("{:.0%}".format(value))

        e.add_field(name="leverage adjusted weights \n (%)", 
                    value=valueString,
                    inline=True)
    
        webhook.send(embed=e)

#%%
if __name__ == '__main__':
    bot = discordBot(conf)
    