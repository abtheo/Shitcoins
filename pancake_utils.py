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
    return np.float64(Tk().clipboard_get())

def set_token_value(from_box, value):
    """Get the token value in the correct box on Pancakeswap
        Params:
            [boolean] from_box: 
                -True to select From balance,
                -False to select To balance
    """
    select_box(from_box)
    gui.hotkey('ctrl', 'a', 'del')
    gui.write(str(value))
    
def set_token_address(from_box, address):
    """Sets the token address in the correct box on Pancakeswap
        Params:
            [boolean] from_box: 
                -True to select From balance,
                -False to select To balance
            [string] address:
                - 'Binance' - BNB coin
                - Else: Valid token address
    """
    if from_box:
        #From box / balance
        gui.click(x=1240, y=454)
    else:
        #To box / exchange rate
        gui.click(x=1240, y=608)
    
    sleep(0.6)
    #Click Address box
    gui.click(x=890, y=280)
    sleep(1.5)
    #Fill contract address
    if address == "Binance":
        gui.click(x=822, y=400)
    else:
        gui.write(address)
    sleep(0.5)
    