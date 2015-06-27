'''
Created on 5/05/2015

@author: Alex Montes Barrios
'''
import Tkinter as tk
import Queue
import keyword
import tkFont
import ttk
import tkMessageBox
import HTMLParser
import urllib
import re
import os
import SintaxEditor
from likeXbmc import translatePath

class kodiLog(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.stopFlag = False
        self.activeCallBack = []        
        self.queue = Queue.Queue(maxsize=0)
        self.fileListProv = None
        self.isCoderSet = False
        self.setGUI()
        
    def setFileListProv(self, callBackFunction):
        self.fileListProv = callBackFunction
        
    def initFrameExec(self, coder, param = False):
        if param or not self.isCoderSet:
            self.coder = coder
            self.isCoderSet = True
            self.fillDropDownLst()
            self.fileChsr.current(0)
            self.sntxIndx.set(0)
        activeKnotId = self.coder.getActiveNode()
        srchStr = 'def ' + activeKnotId + '():'
        srchIndx = self.textw.search(srchStr, '1.0')
        if srchIndx:
            self.textw.mark_set('insert', srchIndx) 
            self.textw.see('insert')
            self.onUpRelease()
            self.textw.focus_set()
            
    def setGUI(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        topPane = tk.Frame(self)
        topPane.pack(side = tk.TOP, fill = tk.X)
        intVar = tk.IntVar()
        intVar.trace('w', self.changeDisplay)
        self.sntxIndx = intVar
        for k, elem in enumerate(['Errors/Warnings', 'Kodilog', 'xbmclogs.com']):
            boton = tk.Radiobutton(topPane, text = elem, width = 30, value = k, variable = intVar, indicatoron = 0)
            boton.pack(side = tk.LEFT)

        self.xbmclogComId = tk.StringVar()
        tk.Button(topPane, text = 'Get', command = self.getUrlLog).pack(side = tk.RIGHT)
        tk.Entry(topPane, textvariable = self.xbmclogComId).pack(side = tk.RIGHT)
        tk.Label(topPane, text = 'xbmclogId: ').pack(side = tk.RIGHT)

        self.sintaxEd = SintaxEditor.SintaxEditor(self)
        self.sintaxEd.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        self.setHyperlinkManager(self.click_hyperlink)
        self.sntxIndx.set(1)
        
    def setHyperlinkManager(self, hyperLinkManager):
        self.sintaxEd.setHyperlinkManager(hyperLinkManager)
        
    def getUrlLog(self):
        if self.sntxIndx.get() != 2: return
        logId = self.xbmclogComId.get()
        if logId:
            logUrl = 'http://xbmclogs.com/' + logId
            f = urllib.urlopen(logUrl)
            content = f.read().decode('utf-8')
            f.close()
            lines = map(lambda x:HTMLParser.HTMLParser().unescape(x), re.findall('middle">(.+?)</div', content))
            content = '\n'.join(lines)          #.replace('&nbsp;', '')
        else:
            logUrl, content = '', ''
        contentDesc = (content, 'filegen', logUrl)
        sintaxArray = self.errorSintax()
        self.sintaxEd.setContent(contentDesc,'1.0', sintaxArray, isEditable = False)
        
    
    def click_hyperlink(self, texto):
        tkMessageBox.showinfo('Hyperlink', texto)        
        return       
        
    def fillDropDownLst(self):
        dropDownContent = []
        if self.fileListProv:
            lista =  self.fileListProv()
            self.listaPy = [pFile for pFile in lista if pFile[0].endswith('.py')]
            dropDownContent = map(os.path.basename, [elem[0] for elem in self.listaPy])
        self.fileChsr.configure(values = dropDownContent)
        
    def errorSintax(self):
        toColor = [
                   ['errError', dict(background = 'red'), r'ERROR:',re.MULTILINE],
                   ['errWarning', dict(background = 'yellow'), r'WARNING:',re.MULTILINE],
                   ['hyper', dict(foreground="blue", underline=1), r'File "[^"]+", line [0-9]+, in [\w<>]+',re.MULTILINE],
                   ['hyper', dict(foreground="blue", underline=1), r'http:[^\n|]+',0]
                   ]
        return toColor
        
        
    def changeDisplay(self, *args, **kwargs):
        if self.sntxIndx.get() == 0:
            return
        elif self.sntxIndx.get() == 1:
            logfile = os.path.join(translatePath('special://logpath'), 'kodi.log')
            with open(logfile, 'r') as f:
                content = f.read()
            contentDesc = (content, 'file', logfile)
            sintaxArray = self.errorSintax()
            self.sintaxEd.setContent(contentDesc,'1.0', sintaxArray, isEditable = False)
        elif self.sntxIndx.get() == 2:
            self.getUrlLog()
            
        

        
    
if __name__ == '__main__':
    Root = tk.Tk()
    kodilog = kodiLog(Root)
    kodilog.pack(side =tk.TOP, fill = tk.BOTH, expand = tk.YES) 
    Root.mainloop()
    
         
