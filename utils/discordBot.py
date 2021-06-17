from discord import Webhook, RequestsWebhookAdapter,Embed

class discordBot():
    
    def __init__(self,conf):
        self.conf = conf
        self.hook = conf["discord"]


    def sendEmbed(self,description,df,title=None):
        
        webhook = Webhook.from_url(self.hook, adapter=RequestsWebhookAdapter())
        e = Embed(title=title, description=description)
        
        for fieldName in df.columns:

            valueString  = ''

            for value in df[fieldName]:
                
                if type(value) is float:
                    
                    if fieldName == 'debt pool %':

                        valueString =  valueString +  "\n" + str("{:.0%}".format(value))
                    
                    else:
                    
                        valueString =  valueString +  "\n" + str("{:,}".format(round(value,2)))
                
                else:
                    valueString =  valueString +  "\n" + value

            e.add_field(name=fieldName, 
                        value=valueString,
                        inline=True)

        
        webhook.send(embed=e)

#%%
if __name__ == '__main__':
    bot = discordBot(conf)
    