import argparse
from argparse import RawTextHelpFormatter
from utils.utility import parse_config
from utils.debtComp import debtComp

conf           = parse_config(r"config/conf.yaml")
resolver       = parse_config(r"config/proxyResolver.yaml")

#%%Arg Parse
if __name__ == '__main__':

    description = \
    '''
    launch debt comp
    '''
    
    parser = argparse.ArgumentParser(description=description,formatter_class=RawTextHelpFormatter)

    parser.add_argument("-t",
                        type=str,
                        required=True,
                        help="enter 'launch'"
                        )
 
    args = parser.parse_args()
    
    
    if args.t == 'launch':
        debt = debtComp(conf=conf,
                        resolver=resolver)
       
        debt.startBot()
            
    else:
        print("doing nothing wrong args")
