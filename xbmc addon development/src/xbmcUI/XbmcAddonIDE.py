# -*- coding: utf-8 -*-
'''
Created on 29/06/2014

@author: Alex Montes Barrios
'''
from xbmcStubs import collapsingFrame
from xbmcUI import KodiLog

"""
    return [[{"url":"http://played.to/5jhkm0lq5xge", "menu":"media"}, {"isFolder": False, "label": "Relatos Salvajes"}, None]]
"""

import sys
import os
import Tkinter as tk
import tkMessageBox
import tkFileDialog
import tkSimpleDialog
import ttk
import tkFont
import keyword
import pickle
import json
import re
import urllib
import urllib2
import urlparse
import webbrowser
import menuThreads
import addonSettCtrls
import xml.etree.ElementTree as ET
import shutil
import zipfile
import addonCoder
import treeExplorer
import FileGenerator
import SintaxEditor
import xmlFileWrapper
import KodiFrontEnd
from likeXbmc import translatePath
from ParseThreads import RegexpFrame, parseTree, EditTransaction, StatusBar, ScrolledList, addonFilesViewer
from ParseThreads import ScrolledList, NodeEditFrame
from OptionsWnd import AppSettingDialog, getScriptSettings, exportAddon, getAddonXmlFile
from likeXbmc import translatePath


class XbmcAddonIDE(tk.Toplevel):
    PERSPECTIVES = ['Site API', 'Addon']
    def __init__(self, theGlobals = None):
        tk.Toplevel.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.Close)
        self.perspectiveIndx = tk.StringVar(value = self.PERSPECTIVES[0])
        self.activeViewIndx = tk.StringVar()
        self.activeViewIndx.trace("w", self.setActiveView)
        self.leftPaneIndx = tk.IntVar(value = -1)
        self.leftPaneVisible = tk.BooleanVar()
        self.leftPaneVisible.trace("w", self.setLeftPaneVisibility)
        self.rightPaneIndx = tk.IntVar(value = -1)
#         self.rightPaneIndx.trace("w", self.setRightPane)
        self.xbmcThreads = menuThreads.menuThreads()
        self.addonSettings = xmlFileWrapper.xmlFileWrapper('addonIdeSettingFile.xml')
        self.coder = addonCoder.Addoncoder(self.xbmcThreads, self.addonSettings)
        self.fileGenerator = FileGenerator.FileGenerator(self.addonSettings, self.xbmcThreads, self.coder) 
        self.settings = {}
        self.setGUI()
        self.activeUrl.set('')
        self.newFile()
        self.currentFile = 'default.pck'
        self.title(self.currentFile)
        
    def initCoder(self, xbmcThreads, modSourceCode = None):
        addon_id = self.getAddonSettings('addon_id')
        self.coder = addonCoder.Addoncoder(xbmcThreads, addon_id)
        self.coder.modSourceCode = modSourceCode or {}

    def checkSaveFlag(self):
        fileName = self.title()
        if fileName.endswith('**'):
            fileName = os.path.basename(self.currentFile) if not self.currentFile else 'default.pck'
            ans = tkMessageBox.askyesno('Warning', 'Do you want to save the changes you made to ' + fileName)
            if ans: self.saveFile()
            else: self.setSaveFlag(False)
        
        
    def Close(self):
        self.checkSaveFlag()
        self.destroy()

    def setGUI(self):
        frame = tk.Frame(self)
        frame.pack(fill = tk.BOTH, expand = 1)
        
        menuFrame = tk.Frame(frame)
        menuFrame.pack(side=tk.TOP, fill = tk.X)
        self.menuBar = {}
        menuOp = ['File', 'Get', 'Set', 'View', 'Knoth', 'Coding', 'Tools']
        for elem in menuOp:
            menubutton = tk.Menubutton(menuFrame, text = elem, name = elem.lower())
            menubutton.pack(side=tk.LEFT)
            self.menuBar[elem] = tk.Menu(menubutton, tearoff=False)
        
        topPane = tk.Frame(menuFrame)
        topPane.pack(side = tk.RIGHT)
        
        self.activeKnot = tk.StringVar()
        self.activeUrl = tk.StringVar()
        self.message = tk.StringVar()
        self.statusBar = StatusBar(frame,[('ActiveKnot: ', self.activeKnot),
                                    ('KnotData ', self.message),
                                    ('ActiveUrl: ', self.activeUrl)
                                    ])
        self.statusBar.pack(side = tk.BOTTOM, fill = tk.X, expand = 0)
        
        
        m1 = tk.PanedWindow(frame, sashrelief = tk.SUNKEN, bd = 10)
        m1.pack(side = tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.vPaneWindow = m1
        self.setUpPaneCtrls()        

        label = tk.Label(topPane, text = 'Perspective: ', width = 13)
        label.pack(side=tk.LEFT)
        fileChsr = ttk.Combobox(topPane, textvariable = self.perspectiveIndx, value = self.PERSPECTIVES, name = 'combo')
        fileChsr.pack(side=tk.LEFT)
        cClass = fileChsr.__class__
        cClass.config(fileChsr, state = 'readonly', takefocus = 0)

        label = tk.Label(topPane, text = 'View: ', width = 13)
        label.pack(side=tk.LEFT)
        fileChsr = ttk.Combobox(topPane, textvariable = self.activeViewIndx, name = 'combo2')
        fileChsr.pack(side=tk.LEFT)
        cClass = fileChsr.__class__
        cClass.config(fileChsr, state = 'readonly', takefocus = 0)

        self.topPane = topPane
        def setPerspectiveViews(*args, **kwargs):
            perspIndx = self.PERSPECTIVES.index(self.perspectiveIndx.get())
            views = [view[0] for view in self.viewPanes[perspIndx]]
            self.topPane.children['combo2'].config(value = views)
            actView = self.actViewPane[perspIndx]
            self.activeViewIndx.set(views[actView])
            
        setPerspectiveViews()
        self.perspectiveIndx.trace('w', setPerspectiveViews)

        self.menuBuilder()
        
        for elem in menuOp:
            menubutton = menuFrame.children[elem.lower()]
            menubutton.config(menu=self.menuBar[elem])

    def setUpPaneCtrls(self):
        m1 = self.vPaneWindow
        self.parseTree = treeExplorer.ApiTree(m1, self.xbmcThreads)
        self.parseTree.setOnTreeSelProc(self.onTreeSel)
        self.parseTree.setPopUpMenu(self.popUpMenu)
        self.explorerTree = treeExplorer.treeExplorer(m1, self.addonSettings, self.fileGenerator)
        
        self.addonFilesViewer = addonFilesViewer(m1)
        self.addonFilesViewer.setHyperlinkManager(self.hyperLinkProcessor)
        self.explorerTree.setEditorWidget(self.addonFilesViewer)
        self.addonCtrlSett = addonSettCtrls.vertRadioMenu(master = m1)
        self.leftPnNames = ['parsetree', 'esplorertree']
        self.avLeftPanes = [self.parseTree, self.explorerTree, self.addonCtrlSett]
        self.leftPaneVisible.set(True)
        self.regexpEd = RegexpFrame(m1, self.xbmcThreads, self.message)
        self.regexpEd.setDropDownFiler(self.comboBoxFiler)
        self.regexpEd.setPopUpMenu(self.popUpWebMenu)
        self.testFrame = ScrolledList(m1, self.coder)
        self.codeFrame = SintaxEditor.CodeEditor(m1, self.xbmcThreads, self.coder)
        xbmcFileW = xmlFileWrapper.threadXmlFileWrapper('NodeSettingFile.xml', self.xbmcThreads)
        self.NodeFrame = xmlFileWrapper.settingsDisplay(master = m1, xmlFileW = xbmcFileW)
        self.NodeFrame.setNotifyChange(self.setSaveFlag)
        self.settingsPane = xmlFileWrapper.settingsDisplay(master = m1, xmlFileW = self.addonSettings)
        self.settingsPane.setNotifyChange(self.setSaveFlag)
        self.addonCtrlSett.setSettingsPane(self.settingsPane)
        self.kodiFrontEnd = KodiFrontEnd.KodiFrontEnd(m1, self.explorerTree.getAddonTemplate, self.fileGenerator)
        self.avRightPanes = [self.NodeFrame, self.testFrame, self.codeFrame, self.regexpEd, self.addonFilesViewer, self.settingsPane, self.kodiFrontEnd]
        self.viewPanes = []
        self.viewPanes.append([('Design', 0, 0), ('Test', 0, 1), ('Code', 0, 2), ('Regexp Editor', 0, 3)])
        self.viewPanes.append([('Settings', 2, 5),('Test', 0, 6), ('Addon Explorer', 1, 4)])
        self.actViewPane = len(self.viewPanes)*[0]
        
        
    def hyperLinkProcessor(self, texto):
        match = re.search('File "(?P<filename>[^"]+)", line (?P<lineno>[0-9]+)', texto)
        if not match:
            tkMessageBox.showinfo('Hyperlink Not Process', texto)                
        else:
            fileName = match.group('filename')
            lineNo = match.group('lineno')
            rootId = self.explorerTree.treeview.get_children()[0]  
            baseDirectory = translatePath('special://home/addons/')
            if not fileName.startswith(baseDirectory):
                return tkMessageBox.showerror('Hyperlink Not in actual addon', texto)
            nodeId = fileName[len(baseDirectory):].replace('\\', '/')
            if not fileName.startswith(os.path.join(baseDirectory, rootId)):
                nodeId = rootId + '/Dependencies/' + fileName[len(baseDirectory):].replace('\\', '/')
                if not self.explorerTree.treeview.exists(nodeId):
                    return tkMessageBox.showerror('Hyperlink Not Found', texto)
            self.explorerTree.treeview.set(nodeId, column = 'inspos', value = lineNo + '.0')
            self.explorerTree.onTreeSelection(nodeId)
            self.addonFilesViewer.focus_force()
                                
        
    def setActiveView(self, *args, **kwargs):
        refreshFlag = kwargs.get('refreshFlag', False)
        perspIndx = self.PERSPECTIVES.index(self.perspectiveIndx.get())
        activeView = [view[0] for view in self.viewPanes[perspIndx]].index(self.activeViewIndx.get())
        self.actViewPane[perspIndx] = activeView
        viewName, vwLeftPane, vwRightPane = self.viewPanes[perspIndx][activeView]
        leftPaneIndx = self.leftPaneIndx.get()
        if leftPaneIndx != vwLeftPane: 
            self.leftPaneIndx.set(vwLeftPane)
            self.setLeftPaneVisibility()
        if refreshFlag or leftPaneIndx != vwLeftPane: self.avLeftPanes[vwLeftPane].refreshPaneInfo()
        rightPaneIndx = self.rightPaneIndx.get()
        if rightPaneIndx != vwRightPane:
            self.rightPaneIndx.set(vwRightPane)
            self.setRightPane()
        if refreshFlag or rightPaneIndx != vwRightPane: self.avRightPanes[vwRightPane].initFrameExec()
        
    def setLeftPane(self, *args, **kwargs):
        viewTy = int(self.leftPaneIndx.get())
        panes = self.vPaneWindow.panes()
        pane2 = self.avLeftPanes[viewTy]
        if self.leftPaneVisible.get():
            if len(panes) > 1: self.vPaneWindow.forget(panes[1])
            self.vPaneWindow.add(pane2, after = panes[0])
        else:
            self.vPaneWindow.forget(panes[0])
            self.vPaneWindow.add(pane2)
#         if self.xbmcThreads.threadDef:self.initRightPane(param = False)
        
        
        
    def setRightPane(self, *args, **kwargs):
        viewTy = int(self.rightPaneIndx.get())
        panes = self.vPaneWindow.panes()
        pane2 = self.avRightPanes[viewTy]
        if self.leftPaneVisible.get():
            if len(panes) > 1: self.vPaneWindow.forget(panes[1])
            self.vPaneWindow.add(pane2, after = panes[0])
        else:
            self.vPaneWindow.forget(panes[0])
            self.vPaneWindow.add(pane2)
#         if self.xbmcThreads:self.initRightPane(param = False)

    def setLeftPaneVisibility(self, *args, **kwargs):
        nPane = self.leftPaneIndx.get()
        isVisible = self.leftPaneVisible.get()
        panes = self.vPaneWindow.panes()
        if not isVisible and len(panes) > 1:
            self.vPaneWindow.forget(panes[0])
        elif isVisible:
            pane2 = self.avLeftPanes[nPane]
            if len(panes) == 2: 
                self.vPaneWindow.forget(panes[0])
                self.vPaneWindow.add(pane2, before = panes[1])
            elif len(panes) == 1:
                self.vPaneWindow.add(pane2, before = panes[0])
            elif len(panes) == 0:
                self.vPaneWindow.add(pane2)
            
    def dummyCommand(self):
        tkMessageBox.showerror('Not implemented', 'Not yet available')

    def menuBuilder(self):
            
        self.menuBar['popup'] = tk.Menu(self, tearoff=False)

        menuOpt = []
        menuOpt.append(('cascade', 'Insert New', 0))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Set Regexp','Ctrl+G', 0, self.setRegexp))
        menuOpt.append(('command', 'Set NextRegexp','Ctrl+N', 0, self.setNextRegexp))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Rename','Ctrl+R', 0, self.renameKnot))
        menuOpt.append(('command', 'Delete','Ctrl+D', 0, self.deleteKnot))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Transform in a menu node','Ctrl+N', 0, self.makeMenuNode))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Edit','Ctrl+E', 0, self.editKnot))
        self.makeMenu('popup', menuOpt)    
        
        menuOpt = []
        menuOpt.append(('command', 'Source','Ctrl+B', 0, self.newSendOutput))
        menuOpt.append(('command', 'Output','Ctrl+A', 0, self.newReceiveInput))
        menuOpt.append(('command', 'Link','Ctrl+A', 0, self.newLink))        
        self.makeMenu('popup.Insert_New', menuOpt)
        
        self.menuBar['webpopup'] = tk.Menu(self, tearoff=False)

        menuOpt = []
        menuOpt.append(('command', 'Cut','', 2, self.dummyCommand))
        menuOpt.append(('command', 'Copy','', 0, self.dummyCommand))
        menuOpt.append(('command', 'Paste','', 0, self.dummyCommand))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Send UserForm','', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Encrypt Rijndael','', 0, self.dummyCommand))
        menuOpt.append(('command', 'Decrypt Rijndael','', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Unwise process','', 0, self.unwiseProcess))
        menuOpt.append(('command', 'Unwise variable','', 0, self.dummyCommand))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Detect packer','', 0, self.detectPacker))
        menuOpt.append(('command', 'Unpack','', 0, self.unPack))
        self.makeMenu('webpopup', menuOpt)    

        menuOpt = []
        menuOpt.append(('command', 'New','Ctrl+O', 0, self.newFile))        
        menuOpt.append(('command', 'Open','Ctrl+O', 0, self.__openFile))        
        menuOpt.append(('command', 'Save','Ctrl+S', 0, self.saveFile))
        menuOpt.append(('command', 'Save as','Ctrl+S', 0, self.saveAsFile))        
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Export to XBMC','Ctrl+x', 0, self.onXbmcExport))
        menuOpt.append(('command', 'MakeZip File','Ctrl+M', 0, self.onMakeZipFile))
        menuOpt.append(('separator',))
        menuOpt.append(('command', 'Close','Alt+Q', 0, self.Close))
        self.makeMenu('File', menuOpt)


        menuOpt = []
        menuOpt.append(('command', 'File','Ctrl+F', 0, self.importFile))
        menuOpt.append(('command', 'Url','Ctrl+U', 0, self.importUrl))
        menuOpt.append(('command', 'Clipboard','Ctrl+L', 0, self.regexpEd.pasteFromClipboard))
        menuOpt.append(('command', 'Selected Url','Ctrl+S', 0, self.selectedURL))
        menuOpt.append(('command', 'Selected Form','Ctrl+F', 0, self.selectedForm))
        self.makeMenu('Get', menuOpt)

        menuOpt = []
        menuOpt.append(('command', 'Set Url','Ctrl+U', 0, self.setUrl))
        menuOpt.append(('command', 'Set Regexp','Ctrl+R', 0, self.setRegexp))
        menuOpt.append(('command', 'Set Header Regexp','Ctrl+N', 0, lambda param = 'headregexp': self.setActNodeParam(param)))
        menuOpt.append(('command', 'Set NextRegexp','Ctrl+N', 0, lambda param = 'nextregexp': self.setActNodeParam(param)))        
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Edit','Ctrl+E', 0, self.editKnot))
        self.makeMenu('Set', menuOpt)
         
        menuOpt = []
        menuOpt.append(('command', 'New','Ctrl+S', 0, self.newParseKnot))
        menuOpt.append(('command', 'Set ActiveKnoth','Ctrl+A', 0, self.setActiveKnot))
        self.makeMenu('Knoth', menuOpt)

        menuOpt = []
        menuOpt.append(('checkbutton', 'ParseTree', self.leftPaneVisible,[False, True]))
        menuOpt.append(('separator',))            
        menuOpt.append(('radiobutton', self.perspectiveIndx,self.PERSPECTIVES))        
        menuOpt.append(('separator',))
        perspIndx = 0            
        menuOpt.append(('radiobutton', self.activeViewIndx,[view[0] for view in self.viewPanes[perspIndx]]))
        self.makeMenu('View', menuOpt)
        def miLambda():
            frstIndx, lstIndx = 5, tk.END
            self.menuBar['View'].delete(frstIndx, lstIndx)
            perspIndx = self.PERSPECTIVES.index(self.perspectiveIndx.get())
            for k, view in enumerate(self.viewPanes[perspIndx]):
                self.menuBar['View'].add_radiobutton(label = view[0], variable = self.activeViewIndx, value = k)

        self.menuBar['View'].config(postcommand = miLambda)
                                                           
        menuOpt = []
        menuOpt.append(('command', 'Addon','Ctrl+E', 0, lambda key = '2':self.codeAddon(key)))
        menuOpt.append(('command', 'DownThread','Ctrl+D', 0, self.codeDownThread))
        menuOpt.append(('command', 'ActiveKnot','Ctrl+R', 0, self.codeActiveKnot))
        menuOpt.append(('command', 'SaveCode','Ctrl+o', 0, self.saveCode))
        self.makeMenu('Coding', menuOpt)

        menuOpt = []
        menuOpt.append(('command', 'Regexp editor','Ctrl+R', 0, lambda key = '3':self.codeAddon(key)))
        menuOpt.append(('separator',))        
        menuOpt.append(('command', 'Detach Window','Ctrl+R', 0, self.detachWindow))        
        menuOpt.append(('separator',))        
        menuOpt.append(('command', 'Setting','Ctrl+S', 0, self.programSettingDialog))
        self.makeMenu('Tools', menuOpt)
        
    def detachWindow(self):
        actWin = self.activeViewIndx.get()
        wname, lwpane, rwpane = self.viewPanes[actWin]
        
    def detectPacker(self):
        content = self.regexpEd.getContent()
        from jsunpack import detect
        result = detect(content)
        if result:
            tkMessageBox.showinfo('Pack content', 'The content is packed')
        else:
            tkMessageBox.showerror('Pack content', 'The content is packed')
        
    def unPack(self):
        content = self.regexpEd.getContent()
        from jsunpack import unpack
        content = unpack(content)
        self.regexpEd.setContent(content, newUrl = False)
        
    def unwiseProcess(self):
        content = self.regexpEd.getContent()
        from unwise import unwise_process
        content = unwise_process(content)
        self.regexpEd.setContent(content, newUrl = False)

    def onMakeZipFile(self):
        D = os.path.normpath(self.getAddonSettings(srchSett = 'script_export'))
        zipFileName = tkFileDialog.asksaveasfilename(title = 'Zip File to create', initialdir=D, defaultextension='.zip', filetypes=[('Zip Files', '*.zip'), ('All Files', '*.*')])
        if zipFileName:
            self.onXbmcExport(zipFileName)
            # Este procedimiento se hce necesario para asegurar que en el android el archivo zip no tenga problemas
            with open(zipFileName, 'r+b') as f:   
                data = f.read()  
                pos = data.find('\x50\x4b\x05\x06') # End of central directory signature  
                if (pos > 0):  
                    f.seek(pos + 22)   # size of 'ZIP end of central directory record' 
                    f.truncate()  
              
    def getAddonSettings(self, srchSett = None):
        return self.addonSettings.getParam(srchSett)

    def onXbmcExport(self, name = None):
        errMsg = ''
        if name:
            zipFile = zipfile.ZipFile(name, 'w')
            copySrcFile = zipFile.write
            genFileFromStr = zipFile.writestr
        else:
            baseDirectory = translatePath('special://home/addons')
            copySrcFile = shutil.copyfile 
            
        addonFiles = self.listAddonFiles(name)
        for elem in addonFiles:
            dstFile, mode, srcFile = elem
            if not name:
                dstFile = translatePath('special://home/addons/' + dstFile)
                dstDirectory = os.path.split(dstFile)[0]
                if not os.path.exists(dstDirectory): os.makedirs(dstDirectory)
            try:
                if mode == 'f':
                    copySrcFile(srcFile, dstFile)
                elif mode == 's':
                    srcFile = self.fileGenerator.getSource(srcFile)
                    if name:
                        genFileFromStr(dstFile, srcFile)
                    else:
                        with open(dstFile,'w') as wfile:
                            wfile.write(srcFile)
            except:
                errFile = dstFile.rpartition('\\')[2]
                errMsg += errFile + '\n' 
        if name: zipFile.close()
        addonId = self.getAddonSettings('addon_id')
        addonName = self.getAddonSettings('addon_name')
        if errMsg:
            errMsg = 'During addon creation for ' + addonName + ' (' + addonId + ') , the following source files were not found: \n' + errMsg
            tkMessageBox.showerror('Addon creation', errMsg)
        else:
            errMsg = 'Addon for ' + addonName + ' (' + addonId + ') succesfully created'
            tkMessageBox.showinfo('Addon creation', errMsg)
        
        
    def listAddonFiles(self, name = None):
        fileList = self.explorerTree.getAddonTemplate()[1:]
        fileList = [(filePath, fileAttr['type'], fileAttr['source']) for filePath, fileAttr in fileList if 'Dependencies' not in filePath]
        addonListFiles = []
        for filePath, itype, source in fileList:
            itype = {'file':'f', 'genfile':'s'}[itype]
            if type == 's': source = self.fileGenerator.getSource(source)
            addonListFiles.append((filePath, itype, source))
        return addonListFiles
        
    def programSettingDialog(self):
        settingObj = AppSettingDialog(self, 'ideProgramSettings.xml', settings = self.settings, title = 'Test Window Case')
        self.settings = settingObj.result
        if settingObj.applySelected: self.setSaveFlag(True)

    def codeAddon(self,key):
        if self.rightPaneIndx.get() != key: return self.rightPaneIndx.set(key)
        execObj = self.xbmcThreads if key in ['0', '3'] else self.coder
        self.avRightPanes[int(key)].initFrameExec(execObj, param = True)

    def codeDownThread(self):
        if self.rightPaneIndx.get() != '2': return self.rightPaneIndx.set('2')
        threadId = self.xbmcThreads.threadDef
        self.codeFrame.setContentToNodeCode(threadId, incDownThread = True)        
        
    def saveCode(self):
        viewTy = int(self.rightPaneIndx.get())
        rPane = self.avRightPanes[viewTy]
        if isinstance(rPane, SintaxEditor.CodeEditor):
            widget = self.codeFrame
            partialMod = True
        elif isinstance(rPane, addonFilesViewer):
            widget = self.addonFilesViewer.sintaxEditor
            partialMod = False
        else:
            return
        modSource, contType, fileId = widget.getContent()
        if contType == 'genfile':
            self.fileGenerator.setSource(fileId, modSource, partialMod)
            if not partialMod:
                modSource = self.fileGenerator.getSource(fileId)
                widget.setContent((modSource, contType, fileId), '1.0')
            else:
                match = re.search('\W*<([^>]+)>\W*', modSource)
                if match:
                    nodeId = match.group(1)
                    if nodeId == self.xbmcThreads.threadDef and nodeId in self.coder.modSourceCode:
                        self.coder.modSourceCode.pop(nodeId)
                        self.xbmcThreads.unlockThread(nodeId)
                self.codeFrame.initFrameExec()
            self.setSaveFlag(True)
        if contType == 'file':
            if os.path.splitext(fileId)[1] in ['.py', '.txt', '.xml']:
                with open(fileId, 'w') as f:
                    f.write(modSource)
    
    def codeActiveKnot(self):
        if self.rightPaneIndx.get() != '2': return self.rightPaneIndx.set('2')
        threadId = self.xbmcThreads.threadDef
        self.codeFrame.setContentToNodeCode(threadId)
        
    def makeMenu(self, masterID, menuArrDesc):
        master = self.menuBar[masterID]
        for menuDesc in menuArrDesc:
            menuType = menuDesc[0]
            if menuType == 'command':
                menuType, mLabel, mAccelKey, mUnderline, mCommand =  menuDesc
                master.add(menuType,
                           label = '{:30s}'.format(mLabel),
                            accelerator = mAccelKey,
                            underline = mUnderline, 
                            command = mCommand)
            elif menuType == 'cascade':
                menuType, mLabel, mUnderline =  menuDesc
                menuLabel = masterID + '.' + mLabel.replace(' ','_')
                self.menuBar[menuLabel] = tk.Menu(master, tearoff = False)
                master.add('cascade',
                           label = '{:30s}'.format(mLabel),
                           underline = mUnderline,
                           menu = self.menuBar[menuLabel])
            elif menuType == 'radiobutton':
                menuType, radioVar, radioOps = menuDesc
                for k, elem in enumerate(radioOps):
                    master.add_radiobutton(label = elem, variable = radioVar, value = k) 
            elif menuType == 'checkbutton':
                menuType, checkLabel, checkVar, checkVals = menuDesc
                master.add_checkbutton(label=checkLabel, variable=checkVar, onvalue=checkVals[1], offvalue=checkVals[0])
            else:
                master.add('separator') 

    def makeMenuNode(self):
        knotId = self.getActiveKnot()
        if self.xbmcThreads.isthreadLocked(knotId):
            return tkMessageBox.showerror('Access Error', knotId + ' is a Code locked Node')
        parseKnotId = tkSimpleDialog.askstring('Create Menu Node', 'Menu ID to create:')
        if not parseKnotId:return
        lstChanged = []
        self.xbmcThreads.createThread('list', parseKnotId, parseKnotId)
        menuThread = self.xbmcThreads.threadDef
        url = self.xbmcThreads.getThreadParam(menuThread, 'url')
        regexp = self.xbmcThreads.getThreadParam(menuThread, 'regexp')
        compflags = eval(self.xbmcThreads.getThreadParam(menuThread, 'compflags'))
        submenus = self.testFrame.parseUrlContent(url, regexp, compflags)
        for k, elem in enumerate(submenus):
            menuName = elem['label']
            menuId = 'opc{:0>2d}_{:}'.format(k,menuThread.replace(' ', '_'))
            self.xbmcThreads.createThread('list', menuName, menuId)
            self.xbmcThreads.setNextThread(parseKnotId, menuId)
            self.xbmcThreads.setThreadParams(menuId, {'option':k})
            self.xbmcThreads.setNextThread(menuId, menuThread)
            lstChanged.append(menuThread + '_' + menuId + '_' + 'lnk')
        lstChanged = map(self.xbmcThreads.getDotPath, lstChanged)
        self.parseTree.refreshTreeInfo(parseKnotId, lstChanged = lstChanged)
        if lstChanged: self.setSaveFlag(True)



    def editKnot(self):
        knotId = self.getActiveKnot()
        if not knotId: return -1
        if self.xbmcThreads.isthreadLocked(knotId):
            return tkMessageBox.showerror('Access Error', knotId + ' is a Code locked Node')
        editDlg = EditTransaction(self, self.xbmcThreads)
        self.parseTree.refreshTreeInfo(lstChanged = editDlg.result)
        if editDlg.result: self.setSaveFlag(True)
            
    def getActiveKnot(self):
        return self.xbmcThreads.threadDef
    
    def initRightPane(self, param = False):
        viewTy = int(self.rightPaneIndx.get())
#         execObj = self.xbmcThreads if viewTy in [0,3] else self.coder
        self.avRightPanes[viewTy].initFrameExec()
            
    def setActiveKnot(self, activeKnotId = None):
        if not activeKnotId:
            activeKnotId = tkSimpleDialog.askstring('Set ActiveKnot', 'Enter the new ActiveKnot:')
        if activeKnotId:
            if self.xbmcThreads.getThreadAttr(activeKnotId, 'name') != -1 and self.getActiveKnot() != activeKnotId:
                self.xbmcThreads.threadDef = activeKnotId
                self.initRightPane(param = False)
                self.parseTree.setSelection(activeKnotId, absFlag = False)
                
    def onTreeSel(self, node = None):
        treeview = self.parseTree.treeview
        iid = treeview.focus()
        parent, sep, threadId = iid.rpartition('.')
        self.setActiveKnot(threadId)
        
    def comboBoxFiler(self):
        nodeLst = [elem for elem in self.xbmcThreads.getSameTypeNodes('media') if not elem.endswith('_lnk')]
        getRegEx = self.xbmcThreads.getThreadParam
        lista = [ '(?#<rexp-' + node + '>)'+ getRegEx(node, 'regexp') for node in nodeLst]
        lista.extend([ '(?#<rnxt-' + node + '>)'+ getRegEx(node, 'nextregexp') for node in nodeLst if getRegEx(node, 'nextregexp')])
        headLst = lambda node: [elem.split('<->') for elem in getRegEx(node, 'headregexp').split('<=>')]
        for node in nodeLst:
            if not getRegEx(node, 'headregexp'): continue
            lista.extend(['(?#<rhead-' + node + '-' + label + '>)' + regexp for label, regexp in headLst(node)])        
        return sorted(lista)
        
    def popUpMenu(self):
        popUpMenu = self.menuBar['popup']
        treeview = self.parseTree.treeview
        iid = treeview.focus()
        menuState = tk.DISABLED if iid == 'media' else tk.NORMAL 
        self.menuBar['popup.Insert_New'].entryconfigure(1, state= menuState)
        return popUpMenu
    
    def popUpWebMenu(self):
        return self.menuBar['webpopup']
    
    
    def setKnotParam(self, paramStr, paramValue):
        if not self.getActiveKnot(): return -1
        knotId = self.getActiveKnot()
        if self.xbmcThreads.isthreadLocked(knotId):
            return tkMessageBox.showerror('Access Error', knotId + ' is a Code locked Node')
        params = self.xbmcThreads.getThreadAttr(knotId, 'params')
        params[paramStr] = paramValue
        self.setSaveFlag(True)
        
    def setActNodeParam(self, param):
        if param == 'url':
            self.setKnotParam('url', self.regexpEd.getActiveUrl())
        elif param == 'nextregexp':
            self.setKnotParam('nextregexp', self.regexpEd.getRegexpPattern())
        elif param == 'headregexp':
            knotId = self.getActiveKnot()
            headRegExp = self.xbmcThreads.getThreadParam(knotId, 'headregexp') or ''
            headRegExp += ('<=>' if headRegExp else '') + 'headervar<->' + self.regexpEd.getRegexpPattern()
            self.setKnotParam('headregexp', headRegExp )
                
    def setUrl(self):
        self.setKnotParam('url', self.regexpEd.getActiveUrl())
        
    def setNextRegexp(self):
        self.setKnotParam('nextregexp', self.regexpEd.getRegexpPattern())
        
    def setRegexp(self):
        exitFlag = self.setKnotParam('regexp', self.regexpEd.getRegexpPattern())
        if exitFlag == 'ok': return
        self.setKnotParam('compflags', self.regexpEd.getCompFlags())
        
    def newSendOutput(self):
        refKnot = self.xbmcThreads.threadDef
        self.newParseKnot(refKnot, outputToRefKnoth = True)
        
    def newLink(self):
        parseKnotId = tkSimpleDialog.askstring('Create Link', 'ParseKnot ID to link:')
        if parseKnotId:
            self.xbmcThreads.setLinkTie(self.xbmcThreads.threadDef, parseKnotId)
            lnkNode = parseKnotId + '_' + self.xbmcThreads.threadDef +'_lnk'
            lstChanged = [self.xbmcThreads.getDotPath(lnkNode)]
            self.parseTree.refreshTreeInfo(self.xbmcThreads.threadDef, lstChanged = lstChanged)
            if lstChanged: self.setSaveFlag(True)
    def newReceiveInput(self):
        refKnot = self.xbmcThreads.threadDef
        self.newParseKnot(refKnot, outputToRefKnoth = False)
        
    def deleteKnot(self, threadId = None):
        if not threadId: threadId = self.xbmcThreads.threadDef
        lstChanged = [self.xbmcThreads.getDotPath(threadId)]
        if self.xbmcThreads.getThreadAttr(threadId, 'type') == 'thread':
            for lnkId in self.xbmcThreads.getLinks(threadId):
                toNode = self.xbmcThreads.getThreadAttr(lnkId, 'name')
                if self.xbmcThreads.getThreadAttr(toNode, 'type') == 'thread':continue
                lnkRev = self.xbmcThreads.getLinkId(threadId, toNode)
                lstChanged.append(self.xbmcThreads.getDotPath(lnkRev))
        lista = [elem for elem in self.xbmcThreads.getSameTypeNodes(threadId) if not elem.endswith('_lnk')]
        self.xbmcThreads.deleteNode(threadId)
        self.parseTree.refreshTreeInfo(lstChanged = lstChanged)
        self.coder.modifyCode('delete', *lista)
        if lstChanged: self.setSaveFlag(True)
        
    def renameKnot(self, threadId = None):
        if not threadId: threadId = self.xbmcThreads.threadDef
        if self.xbmcThreads.isthreadLocked(threadId):
            return tkMessageBox.showerror('Access Error', threadId + ' is a Code locked Node')
        newKnotId = tkSimpleDialog.askstring('Create new ParseKnotID', 'New ParseKnot ID to rename:')
        lstChanged = [self.xbmcThreads.getDotPath(threadId)]
        self.xbmcThreads.rename(threadId, newKnotId)
        lstChanged.append(self.xbmcThreads.getDotPath(newKnotId))
        self.parseTree.refreshTreeInfo(lstChanged = lstChanged)
        self.coder.modifyCode('rename', threadId, newKnotId)
        if lstChanged: self.setSaveFlag(True)
        
    def newParseKnot(self, refKnot = None, outputToRefKnoth = True):
        parseKnotId = tkSimpleDialog.askstring('Create ParseKnot', 'ParseKnot ID to create:')
        if not parseKnotId:return
        activeKnoth = self.xbmcThreads.threadDef
        knothType = self.xbmcThreads.getThreadAttr(activeKnoth, 'type')
        if self.xbmcThreads.createThread(iType = knothType, name = parseKnotId, menuId = parseKnotId) == -1: return
        if refKnot == None: refKnot = 'media' if knothType == 'thread' else 'rootmenu'
        lstChangedFlag = refKnot not in ['media', 'rootmenu']
        
        lstChanged = [] if lstChangedFlag else [self.xbmcThreads.getDotPath(parseKnotId)]
        self.xbmcThreads.threadDef = parseKnotId
        if knothType == 'list':
            if refKnot != 'rootmenu':
                if outputToRefKnoth:
                    lstChanged.append(self.xbmcThreads.getDotPath(activeKnoth))                    
                    if self.xbmcThreads.getThreadAttr(refKnot, 'up') != 'rootmenu':
                        refKnotUp = self.xbmcThreads.getThreadAttr(refKnot, 'up')
                        self.xbmcThreads.setNextThread(refKnotUp, parseKnotId)
                    self.xbmcThreads.setNextThread(parseKnotId, refKnot)
                    refKnot = parseKnotId
                else:
                    self.xbmcThreads.setNextThread(refKnot, parseKnotId)
                    activeKnoth = parseKnotId
        elif knothType == 'thread':
            self.setKnotParam('url', self.regexpEd.getActiveUrl())
            self.setRegexp()
            if refKnot != 'media':
                if outputToRefKnoth:
                    self.xbmcThreads.setNextThread(parseKnotId, refKnot)
                    activeKnoth = parseKnotId
                else:
                    lstChanged.append(self.xbmcThreads.getDotPath(activeKnoth))                    
                    if self.xbmcThreads.getThreadAttr(refKnot, 'up') != 'media':
                        refKnotUp = self.xbmcThreads.getThreadAttr(refKnot, 'up')
                        self.xbmcThreads.setNextThread(parseKnotId, refKnotUp)
                    self.xbmcThreads.setNextThread(refKnot, parseKnotId)
                    refKnot = parseKnotId
        if lstChangedFlag:
            lstChanged.append(self.xbmcThreads.getDotPath(activeKnoth))
        self.parseTree.refreshTreeInfo(parseKnotId, lstChanged = lstChanged)
        self.setSaveFlag(True)

    def setSaveFlag(self, state, lstChanged = None):
        suffix = '  **' if state else ''
        fileName = (self.currentFile if self.currentFile else 'default.pck') + suffix
        self.title(fileName)
        if lstChanged:
            self.parseTree.refreshTreeInfo(lstChanged = lstChanged)

                                
    def importFile(self):
        name = tkFileDialog.askopenfilename(filetypes=[('xml Files', '*.xml'),('Text Files', '*.txt'), ('All Files', '*.*')])
        if name:
            name = 'file:///' + name
            self.importUrl(name)
    
    def importUrl(self, urlToOpen = None, initialValue = None):
        if not urlToOpen:
            urlToOpen = tkSimpleDialog.askstring('Open URL', 'URL addres to parse:', initialvalue = initialValue or '')
        if urlToOpen:
            self.regexpEd.setActiveUrl(urlToOpen)

                
    def selectedURL(self):
        selRange = self.regexpEd.getSelRange()
        selUrl = self.regexpEd.getContent(*selRange)
        self.importUrl(selUrl)
        
    def selectedForm(self):
        selForm = self.regexpEd.getContent('1.0', 'end')
        if not (selForm[:5].lower() == '<form' and selForm[-8:-1].lower() == '</form>'):
            return tkMessageBox.showerror('Not Form', 'Zoom In to a <form.+?</form> pattern')
        selForm = '<form' + selForm[5:-8] + '</form>'
        activeUrl = self.regexpEd.getActiveUrl()
        formAttr = re.search('<form\s*([^>]+)>', selForm).group(1)
        formAttr = eval("dict(" + ",".join(formAttr.split()) + ")")
        method = '?' if formAttr.get("method",'GET') == 'GET' else '<post>'
        formUrl = formAttr.get('action', '') or activeUrl
        
        forInVars = re.findall(r'<input\s*(.+?)[/>]', selForm, re.IGNORECASE|re.DOTALL)
        urlVars = {}
        for inVar in forInVars:
            inVar = inVar.replace('class=', '_class=')
            inAttr = eval("dict(" + ",".join(inVar.split()) + ")")
            key = inAttr.get('name', None) or inAttr.get('id', None)
            if key:urlVars[key] = inAttr.get('value', '')
        methodData = urllib.urlencode(urlVars)
        selUrl = formUrl + method + methodData 
        self.importUrl(initialValue = selUrl)
         
    def newFile(self, fileName = '', threadData = None, modSourceCode = None , settings = None):
        self.checkSaveFlag()
        self.currentFile = fileName or 'default.pck'
        self.title(self.currentFile)
        threadData = threadData or self.initThreadData()                      
        self.xbmcThreads.setThreadData(*threadData)
        addonSettings = settings or {} 
        if addonSettings.has_key('reset'): addonSettings.pop('reset')
        self.addonSettings.setNonDefaultParams(addonSettings)
        
        self.coder.modSourceCode = modSourceCode or {}
        self.parseTree.setXbmcThread(self.xbmcThreads)
        
        self.explorerTree.refreshFlag = True
        self.setActiveView(refreshFlag = True)
        
             
    def saveFile(self):
        nameFile = self.currentFile
        self.saveAsFile(nameFile)
             
    def saveAsFile(self, nameFile = None):
        if not nameFile:
            name = tkFileDialog.asksaveasfilename(title = 'File Name to save', defaultextension='.pck',filetypes=[('pck Files', '*.pck'), ('All Files', '*.*')])
            if not name: return
        else:
            name = nameFile
        try:
            with open(name,'wb') as f:
                for objeto in [self.xbmcThreads.getThreadData(), self.addonSettings.getNonDefaultParams(), self.coder.modSourceCode]:
                    objStr = json.dumps(objeto)
                    f.write(objStr + '\n')

        except:
            tkMessageBox.showerror('Error', 'An error was found saving the file')
        else:
            self.currentFile = name if name.endswith('.pck') else name +  '.pck'
            self.setSaveFlag(False)
            

    def __openFile(self):
        self.checkSaveFlag()
        name = tkFileDialog.askopenfilename(filetypes=[('pck Files', '*.pck'), ('All Files', '*.*')])
        if name:
            try:
                with open(name,'rb') as f:
                    kodiThreadData = json.loads(f.readline())
                    settings = json.loads(f.readline())
                    modifiedCode = json.loads(f.readline())
            except IOError:
                tkMessageBox.showerror('Not a valid File', 'File not pck compliant ')
                return
            except ValueError:
                tkMessageBox.showerror('Not a valid File', 'An error has ocurred while reding the file ')
                return
            self.newFile(fileName = name, threadData = kodiThreadData, modSourceCode = modifiedCode, settings = settings )

    def initThreadData(self):
        xbmcMenu = menuThreads.menuThreads()
        params = {'url':'https://www.youtube.com/watch?v=Vw8ViaL7-m4', 'regexp':'onclick="location.href=\'(?P<videourl>.+?)\'"  value="Click Here to Play" />', 'compflags':'re.DOTALL'}
        xbmcMenu.setThreadParams('media', params)    

        xbmcMenu.lstChanged = []  # Se borra cualquier actualización del árbol 
                                  # porque este en este punto no existe
        return xbmcMenu.getThreadData()

            

if __name__ == "__main__":
    Root = tk.Tk()
    Root.withdraw()
    mainWin = XbmcAddonIDE()
    Root.mainloop()
