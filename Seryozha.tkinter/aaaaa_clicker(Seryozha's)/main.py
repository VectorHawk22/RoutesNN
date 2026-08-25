import tkinter as tk
from gui.allgui import ClickerGUI

def main():
    root = tk.Tk()
    app = ClickerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()