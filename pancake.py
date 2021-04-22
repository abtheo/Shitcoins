import pyautogui as gui
from time import sleep
from tkinter import Tk
import numpy as np

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

def get_balance(from_box):
    """Get the current balance 
    by copying the correct box on Pancakeswap
    
        Params:
            [boolean] from_box: 
                -True to select From balance,
                -False to select To balance
    """
    if from_box:
        #From box / balance
        gui.click(x=922, y=454)
    else:
        #To box / exchange rate
        gui.click(x=922, y=608)

    sleep(0.5)
    copy_to_clipboard()
    return np.float(Tk().clipboard_get())

def set_token_value(from_box):
    if from_box:
        #From box / balance
        gui.click(x=922, y=454)
    else:
        #To box / exchange rate
        gui.click(x=922, y=608)
    
def set_token_address(from_box, address):
    if from_box:
        #From box / balance
        gui.click(x=922, y=454)
    else:
        #To box / exchange rate
        gui.click(x=922, y=608)
    



"""START BOT:"""
#Assume we are in browser focus on Pancakeswap Exchange tab
if __name__ == '__main__':
    sleep(5)
    print(get_balance(True), to_balance(False))

