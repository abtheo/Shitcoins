import pyautogui as gui
from time import sleep
from tkinter import Tk
import numpy as np

#Initialise some globals
bnb_address = "0xB8c77482e45F1F44dE1745F52C74426C631bDD52"
FROM_BOX = True
TO_BOX = False

def copy_to_clipboard(all=True):
    """Copy the current selection to the clipboard
    
        Params:
            [boolean] all: True to select all first (Ctrl+A)
    """
    gui.keyDown("ctrl")
    if all:
        gui.press("a")
    gui.press("c")
    gui.keyUp("ctrl")

def select_box(from_box):
    if from_box:
        #From box / balance
        gui.click(x=922, y=454)
    else:
        #To box / exchange rate
        gui.click(x=922, y=608)

def get_balance(from_box):
    """Get the current balance 
    by copying the correct box on Pancakeswap
    
        Params:
            [boolean] from_box: 
                -True to select From balance,
                -False to select To balance
    """
    select_box(from_box)
    sleep(0.5)
    copy_to_clipboard()
    return np.float(Tk().clipboard_get())

def set_token_value(from_box, value):
    select_box(from_box)
    gui.write(value)
    
def set_token_address(from_box, address):
    if from_box:
        #From box / balance
        gui.click(x=1240, y=454)
    else:
        #To box / exchange rate
        gui.click(x=1240, y=608)
    
    sleep(0.6)
    #Click Address box
    gui.click(x=890, y=280)
    #Fill contract address
    gui.write(address)


"""START BOT:"""
#Assume we are in browser focus on Pancakeswap Exchange tab
if __name__ == '__main__':
    sleep(5)
    print(get_balance(FROM_BOX), to_balance(TO_BOX))
    set_token_address(FROM_BOX, bnb_address)
    set_token_value(1000, FROM_BOX)