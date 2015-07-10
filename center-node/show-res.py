# -*- coding: utf-8 -*-
'''
This file is a part of disCalcPy .
homepage -> https://github.com/manageryzy/disCalcPy

MIT licenced!!!
'''

import Tkinter as tk

class ResApp:
    def __init__(self):
        self.mainWindow = tk.Tk()
        self.mainWindow.wm_title('结果监视')
        
        lable = tk.Label(self.mainWindow,text = '监视结果')
        lable.grid(row = 0,column = 0,columnspan = 2)
        
        button = tk.Button(self.mainWindow,text = '刷新',command = self.onRefresh)
        button.grid(row = 1,column = 0)
        
        button = tk.Button(self.mainWindow,text = '退出',command = self.onRefresh)
        button.grid(row = 2,column = 0)
        
        self.mainWindow.mainloop()

    def onRefresh(event):
        return


theApp = ResApp()
