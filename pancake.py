import pyautogui as gui
from time import sleep
from tkinter import Tk
import numpy as np
from pancake_utils import *
#Initialise some globals
FROM_BOX = True
TO_BOX = False


"""START BOT:"""
#Assume we are in browser focus on Pancakeswap Exchange tab
if __name__ == '__main__':
    sleep(5)
    print(get_balance(FROM_BOX), get_balance(TO_BOX))
    # set_token_address(FROM_BOX, "Binance")
    # set_token_value(1000, FROM_BOX)