from discord import Webhook, RequestsWebhookAdapter,Embed

class discordBot():
    
    def __init__(self,conf):
        self.conf = conf
        self.hook = conf["discord"]


    def sendEmbed(self,description,df,title=None):
        
        webhook = Webhook.from_url(self.hook, adapter=RequestsWebhookAdapter())
        e = Embed(title=title, description=description)
                
        #shoot the synth
        valueString  = ''
        for value in df["synth"]:
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

#%%
if __name__ == '__main__':
    bot = discordBot(conf)
    