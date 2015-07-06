# -*- coding: utf-8 -*-
'''
Created on 29/03/2015

@author: Alex Montes Barrios
'''
import os
import sys
import urllib
import urlparse
import shutil
import tempfile
import pickle
import thread
import re
import tkMessageBox
import webbrowser
import xml.dom.minidom as minidom
import logging
import Tkinter as tk
import tkFont
import traceback
import xbmcStubs.menuManagement as menuManagement
import xbmcStubs.collapsingFrame as collapsingFrame
import xbmcUI.SintaxEditor as SintaxEditor
from PIL import Image, ImageTk  # @UnresolvedImport
import KodiAddonImporter
xbmcStubsDir = r'C:\Users\Alex Montes Barrios\git\addonDevelopment\xbmc addon development\src\xbmcStubs'
addonRoot = r'C:\Users\Alex Montes Barrios\AppData\Roaming\Kodi\addons'
KodiAddonImporter.install_meta(xbmcStubsDir, hookId = 'xbmc_mock', atype = 'xbmc')
import xbmc, xbmcgui, xbmcaddon, xbmcplugin, xbmcvfs  # @UnresolvedImport


class newModules:
    def __init__(self, aDict):
        self.dict = aDict
        self._initKeys = aDict.keys()
    def clear(self):
        for key in self.dict.keys():
            if key in self._initKeys: continue
            self.dict.pop(key)
        pass
    def __getattr__(self, attr):
        return getattr(self.dict,attr)



class KodiFrontEnd(tk.Frame):
    def __init__(self, master = None, testAddonGen = None, fileGenerator = None):
        tk.Frame.__init__(self, master)
        self.testAddonGen = testAddonGen
        self.fileGenerator = fileGenerator
        self.message = tk.StringVar()
        self.kodiDirectory = []
        self.addonID = ''
        self.message.set('        ')
        self.optHistory = []
        self.prevPointer = 0
        self.urlParams = {}
        self.makeWidgets()
        self.setLogger()
        self.ORIGINAL_PYTHONPATH = sys.path
        self.mutex = thread.allocate_lock()
        self.thMutex = thread.allocate_lock()
        self.imgDir = {}
        self.testAddon = 'plugin.video.ted.talks'
        self.testRootDir = r'c:\users\Alex Montes Barrios\AppData\Roaming\Kodi\addons'
        self.redefineXbmcMethods()
        
        
    def initGlobals(self):
        theGlobals = {}
        exec 'import sys' in theGlobals
        theGlobals['sys'].argv = [0,0,0]
        exec 'import xbmc, xbmcgui, xbmcplugin' in theGlobals
        theGlobals["__name__"] = "__main__"
        self.theGlobals = theGlobals
            
    def redefineXbmcMethods(self):
        sys.modules['xbmc'].log = self.log
        sys.modules['xbmc'].translatePath = self.translatePath(sys.modules['xbmc'].translatePath, self.testAddon, self.testRootDir)
        sys.modules['xbmcplugin'].setResolvedUrl = self.setResolvedUrl
        sys.modules['xbmcplugin'].addDirectoryItem = self.addDirectoryItem
        sys.modules['xbmcplugin'].endOfDirectory = self.endOfDirectory

    def log(self, msg, level = 2):
        logLst = ['DEBUG', 'INFO', 'NOTICE', 'WARNING', 
               'ERROR', 'SEVERE', 'FATAL', 'NONE']
        msg = '{0:>9s}:{1}'.format(logLst[level], msg)
        self.logger.log(level+1, msg)
        
    def translatePath(self, func, addonId, baseDir):
        def wrapper(path):
            prefix = func('special://home/addons')
            result = func(path)
            if addon and addon in result:
                result = result.replace(prefix,rootDir)
            return result
        addon = addonId
        rootDir = baseDir 
        return wrapper
        
    def setResolvedUrl(self, handle, succeeded, listitem):
        if succeeded:
            url = listitem.getProperty('path')
            self.runAddon(url)

    def addDirectoryItem(self, handle, url, listitem, isFolder = False, totalItems = 0):
        kwargs = {'handle':handle, 'url':url, 'listitem':listitem, 'isFolder':isFolder, 'totalItems':totalItems}
        self.kodiDirectory.append(kwargs)
        
    def endOfDirectory(self, handle, succeeded = True, updateListing = False, cacheToDisc = True):
        if not succeeded: return
        options = list(self.kodiDirectory)
        self.kodiDirectory = [] 
        if self.prevPointer:
            head = {'handle':handle, 'url':'', 'listitem':xbmcgui.ListItem('..'), 'isFolder':True, 'totalItems': 0}
            options.insert(0, head)
        if updateListing: self.prevPointer -= 1
        self.optHistory[self.prevPointer][1] = pickle.dumps(options)
        self.fillListBox(options)        
        
    def select(self, index):
#         self.listbox.focus_set()
        self.listbox.activate(index)
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.see(index)
        self.handleList()
        
    def back_event(self, event):
        if self.listbox.get(0) == '..':
            self.select(0)
            self.executeOption()
            
    def home_event(self, event):
        self.select(0)
        return "break"
    
    def end_event(self, event):
        lsize = self.listbox.size()
        self.select(lsize - 1)
        return "break"    
    
    def right_event(self, event):
        self.sbar.focus_force()
        self.sbar.activate('slider')
        return "break"
        
    def up_event(self, event):
        selItem = self.listbox.index("active")
        lsize = self.listbox.size()
        self.select((selItem + lsize -1) % lsize)
        return "break"    

    def down_event(self, event):
        selItem = self.listbox.index("active")
        lsize = self.listbox.size()
        self.select((selItem + lsize + 1) % lsize)
        return "break"    

    def left_sbar(self, event):
        self.listbox.focus_force()
        
    def sbar_up_down(self, event, delta):
        index = self.listbox.curselection()
        yoffset = self.listbox.bbox(index)[1]
        self.listbox.yview_scroll(delta, 'pages')
        index = self.listbox.nearest(yoffset)
        self.select(index)
        
    def handleList(self, event = None):
        index = self.listbox.curselection()                # on list double-click
        self.runCommand(index)                             # and call action here
                                                           # or get(ACTIVE)
                                                           
    def setLogger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(xbmc.LOGDEBUG+1)
        ch = logging.StreamHandler(self.stEd)
        ch.setLevel(xbmc.LOGDEBUG+1)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
                      
    def runCommand(self, index):                       # redefine me lower
        def setWidgetImage(imgFileName, imgIndx, widget, size = None):
            if not imgFileName:
                self.imageVar[imgIndx] = None
                widget.config(image = None) 
                return 
            try:
                if not os.path.exists(imgFileName):
                    with self.mutex: imgFileName = self.imgDir[imgFileName]
            except:
                widget.config(image = None)
            else:
                im = Image.open(imgFileName)
                if not size: size = (widget.master.winfo_width(),widget.master.winfo_height())
                im.thumbnail(size, Image.ANTIALIAS)
                self.imageVar[imgIndx] = ImageTk.PhotoImage(im)
                widget.config(image = self.imageVar[imgIndx])
            
        label = self.listbox.get(index)                
        texto = 'You selected: \n' + label
        index = int(index[0])
        for key in sorted(self.options[index].keys()):
            texto = texto + '\n' + key + ' = \t' + str(self.options[index][key])
        self.message.set(texto)

        sizeX = max(40, self.icon.master.master.winfo_width()/2)
        sizeY = max(40, self.icon.master.master.winfo_height())
        size = (sizeX, sizeY)
        listitem = self.options[index]['listitem']
        filePtrs = [self.fanart, self.icon, self.thumbnail]
        for k, iProperty in enumerate(['fanart_image', 'iconImage', 'thumbnailImage']):
            fileName = listitem.getProperty(iProperty)
            setWidgetImage(fileName, k, filePtrs[k], size)
        
    def initFrameExec(self):
        self.initGlobals()
        self.message.set('        ')
        self.optHistory = []
        self.prevPointer = 0
        self.urlParams = {}
        self.optHistory = [[0, '']]
        self.setTestPlugin()
        self.kodiAddons()
        
    def setTestPlugin(self):
        if not all([self.testAddonGen, self.fileGenerator]):return
#         if self.testRootDir: shutil.rmtree(self.testRootDir)
        addonFiles = self.testAddonGen()[1:]
        self.testAddon = os.path.commonprefix([addonFiles[0][0],addonFiles[1][0]])[:-1]
        self.testRootDir = tempfile.mkdtemp()
        xbmc.translatePath = self.translatePath(xbmc.translatePath, self.testAddon, self.testRootDir)
        baseDirectory = self.testRootDir
        for elem in addonFiles:
            dstFile, mode, srcFile = elem[0], elem[1]['type'], elem[1]['source']
            dstFile = os.path.join(baseDirectory,dstFile)
            dstDirectory = os.path.split(dstFile)[0]
            if not os.path.exists(dstDirectory): os.makedirs(dstDirectory)
            if mode == 'file':
                shutil.copyfile(srcFile, dstFile)
            elif mode == 'genfile':
                srcFile = self.fileGenerator.getSource(srcFile)
                with open(dstFile,'w') as wfile:
                    wfile.write(srcFile)
        
        
    def kodiAddons(self):
        pathDir = xbmc.translatePath('special://home/addons')
        addons = [addon for addon in os.listdir(pathDir) if addon.startswith('plugin.video')]
        if self.testAddon and self.testAddon not in addons: addons.append(self.testAddon)
        for addonId in sorted(addons):
            kwargs = {'handle':0, 'isFolder':True, 'totalItems':0}
            addon = xbmcaddon.Addon(addonId)
            kwargs['url'] = 'plugin://' + addonId + '/?'
            name = addon.getAddonInfo('name')
            if addonId == self.testAddon: name = '[COLOR red]' + name + ' (test mode)[/COLOR]'
            listitem = xbmcgui.ListItem(label = name , iconImage = addon.getAddonInfo('icon'))
            listitem.setProperty('fanart_image', addon.getAddonInfo('fanart'))
            kwargs['listitem'] = listitem
            self.addDirectoryItem(**kwargs)
        self.endOfDirectory(handle = 0)

    def toHistory(self, index, option):
        pointer = self.prevPointer
        if index != self.optHistory[pointer][0] and option['listitem'].getLabel() != '..':
            self.optHistory[pointer][0] = index
            self.optHistory = self.optHistory[:pointer+1]
        if not option['isFolder']: return 0, ''
        if option['listitem'].getLabel() != '..':
            if pointer == len(self.optHistory)-1:
                self.optHistory.append([0, ''])
            self.prevPointer += 1
        else:
            self.prevPointer -= 1
        return self.optHistory[self.prevPointer]

    def executeOption(self, event = None):
        index = int(self.listbox.curselection()[0])              # on list double-click
        option = self.options[index]
        selItem, strDump = self.toHistory(index, option)
        if strDump == '':
            url = option['url']            
            self.runAddon(url)
        else:
            options = pickle.loads(strDump)
            self.fillListBox(options, selItem)
        
    def runAddon(self, url):
        urlScheme = urlparse.urlparse(url)
        if urlScheme.scheme == 'plugin':             # Plugin diferente
            pluginId, urlArgs = urllib.splitquery(url)
            self.theGlobals['sys'].argv[0] = pluginId
            self.theGlobals['sys'].argv[2] = '?' + (urlArgs or '')
            self.theGlobals['sys'].argv[1] += 1
            self.kodiDirectory = [] 
            actualID = urlScheme.netloc
            addonDir = xbmc.translatePath('special://home/addons/' + actualID)
            if self.addonID != actualID:
                self.addonID = actualID
                self.theGlobals['sys'].modules = newModules(self.theGlobals['sys'].modules)                
                self.sourceCode = self.getCompiledAddonSource(actualID)
            try:
                msg = self.theGlobals['sys'].argv[0] + urllib.unquote(self.theGlobals['sys'].argv[2])
                self.log(msg, xbmc.LOGNONE)
                KodiAddonImporter.install_meta(addonDir, addonRoot, hookId = 'kodi_imports', atype = 'kodi')
                KodiAddonImporter.get_initial_state() 
                exec(self.sourceCode, self.theGlobals)
                KodiAddonImporter.restore_initial_state()
                KodiAddonImporter.remove_meta('kodi_imports')
            except:
                self.logger.exception('')
        else:                                       # Ejecuci�n de media (archivo, etc, etc)
            urlLink, sep, userAgent = url.partition('|')
            self.log('Opening: ' + urlLink, xbmc.LOGNOTICE)
            webbrowser.open(urlLink)
        
    def getCompiledAddonSource(self, addonId):
        addon = xbmcaddon.Addon(addonId)
        path = addon.getAddonInfo('path')
        addonSourceFile = addon.getAddonInfo('library')
        addonFile = os.path.join(path, addonSourceFile)
        with open(addonFile, 'r') as f:
            addonSource = f.read()
        return compile(addonSource, addonFile, 'exec')
    
    def setPythonPath(self, addonId):
        dependencies = set()
        toProcess = [addonId]
        while toProcess:
            dependency = toProcess.pop(0)
            if dependency in dependencies: continue
            dependencies.add(dependency)
            if dependency.startswith('xbmc.'):continue
            addon = xbmcaddon.Addon(dependency)
            toProcess.extend(addon.getAddonInfo('requires'))
        dependencies.remove('xbmc.python')
        pyPathAdd = [str(xbmc.translatePath('special://Kodi/system/python/lib'))]
        pyPathAdd.append(xbmc.translatePath('/'.join(['special://home/addons',addonId])))
        for addon in sorted(dependencies):
            if addon.startswith('script.'):
                pathToInc = '/'.join(['special://home/addons',addon,'lib'])
            elif addon.startswith('plugin.'):
                if addonId not in addon: continue
                pathToInc = '/'.join(['special://home/addons',addon,'resources','lib'])
            else: continue
            pathToInc = xbmc.translatePath(pathToInc)
            if os.path.exists(pathToInc): pyPathAdd.append(pathToInc)
        return pyPathAdd
        
        
    def fillListBox(self, vrtFolder, selItem = 0):
        self.options = vrtFolder
        self.listbox.delete('0', 'end')
        imageList = []
        for pos, item in enumerate(vrtFolder):                              # add to listbox
            for iProperty in ['Fanart_Image', 'iconImage', 'thumbnailImage']:
                imgName = item['listitem'].getProperty(iProperty)
                if imgName: imageList.append(imgName)
            lcolor, itemLabel = self.formatLbxEntry(item['listitem'].getLabel())
            self.listbox.insert(pos, itemLabel)                      # or insert(END,label)
            if lcolor: self.listbox.itemconfig(pos, foreground = lcolor)
        with self.mutex: self.runThread = False
        self.thMutex.acquire()
        self.thMutex.release()
        self.runThread = True
        thread.start_new_thread(self.getVrtFolderImages, (imageList, self.mutex, self.thMutex))
        self.select(selItem)
        
    def formatLbxEntry(self, itemLabel):
        lcolor = None
        itemSettings = re.findall('\[COLOR (.+?)\](.+?)\[/COLOR\]', itemLabel)
        if itemSettings:
            lcolor, itemLabel = itemSettings[0]
        pattern = re.compile(r'\[(.+?)\](.+?)\[/\1\]')
        mFunc = {'UPPERCASE':'upper', 'LOWERCASE':'lower', 'CAPITALIZE':'capitalize', 'B':'encode', 'I':'encode'}
        while 1:
            match = pattern.search(itemLabel)
            if not match: break
            limI, limS = match.span()
            case = match.group(1)
            tagI, tagS = match.span(2)
            fmtText = getattr(itemLabel[tagI:tagS], mFunc[case])() 
            itemLabel = itemLabel[:limI] + fmtText +itemLabel[limS:]
        return lcolor, itemLabel.replace('[CR]', '\n')
        
    def getVrtFolderImages(self, imageList, mutex, thmutex):
        thmutex.acquire()
        k = 0
        while self.runThread and k < len(imageList):
            image = imageList[k]
            if not os.path.exists(image):
                with mutex: bFlag = self.imgDir.get(image,'') == ''
                if bFlag:
                    try:     
                        imgFileName = urllib.urlretrieve(image)[0]
                    except:
                        pass
                    else:
                        with mutex: self.imgDir[image] = imgFileName
            k += 1
        thmutex.release()
        
        
    def makeWidgets(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        allContainer = collapsingFrame.collapsingFrame(self,tk.HORIZONTAL)
        allContainer.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        bottomFrame = tk.Frame(allContainer.scndWidget, height = 200)
        bottomFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        bottomFrame.pack_propagate(flag = False)
        stEd = SintaxEditor.loggerWindow(bottomFrame)
        stEd.pack(fill = tk.BOTH)
        self.stEd = stEd
        topFrame = tk.Frame(allContainer.frstWidget)
        topFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        frame = tk.Frame(topFrame, relief = tk.SUNKEN)
        frame.pack(side = tk.LEFT, fill = tk.Y)
        sbar = tk.Scrollbar(frame, takefocus = 1, activebackground = 'blue',activerelief = tk.FLAT)
        listBox = tk.Listbox(frame, selectmode = 'SINGLE', width = 50, relief=tk.SUNKEN, font = self.customFont)
        sbar.config(command=listBox.yview)                    # xlink sbar and list
        listBox.config(yscrollcommand=sbar.set)               # move one moves other
        sbar.pack(side=tk.RIGHT, fill=tk.Y)                      # pack first=clip last
        sbar.bind('<Key-Left>', self.left_sbar)
        sbar.bind('<Key-Up>', lambda event, delta = -1: self.sbar_up_down(event, delta))
        sbar.bind('<Key-Down>', lambda event, delta = 1: self.sbar_up_down(event, delta))
        listBox.pack(side=tk.LEFT, fill=tk.BOTH)        # list clipped first
        listBox.bind('<<ListboxSelect>>', self.handleList)           # set event handler
        listBox.event_add('<<Execute Option>>','<Return>','<Double-Button-1>')
        listBox.bind('<<Execute Option>>', self.executeOption)
        listBox.bind('<Key-Up>', self.up_event)
        listBox.bind('<Key-Down>', self.down_event)
        listBox.bind('<Key-Home>', self.home_event)
        listBox.bind('<Key-End>', self.end_event)
        listBox.bind('<Key-Right>', self.right_event)
        listBox.bind('<BackSpace>', self.back_event)
        self.listbox = listBox
        self.sbar = sbar
        infoPane = collapsingFrame.collapsingFrame(topFrame, tk.HORIZONTAL)        
        infoPane.pack(side = tk.LEFT, fill = tk.BOTH, expand = tk.YES)
        infoPaneUp = tk.Frame(infoPane.frstWidget)
        infoPaneUp.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        fanart = tk.LabelFrame(infoPaneUp, text = 'Fanart')
        fanart.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        paneUpBottom = tk.Frame(infoPaneUp)
        paneUpBottom.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = tk.YES)
        icon = tk.LabelFrame(paneUpBottom, text = 'Icon')
        icon.pack(side = tk.LEFT, fill = tk.BOTH, expand = tk.YES)
        thumbnail = tk.LabelFrame(paneUpBottom, text = 'Thumbnail')
        thumbnail.pack(side = tk.LEFT, fill = tk.BOTH, expand = tk.YES)
        self.imageVar = [None, None, None]
        self.fanart = tk.Label(fanart, text = '', image = self.imageVar[0])
        self.fanart.pack()
        self.icon = tk.Label(icon, text = '', image = self.imageVar[1])
        self.icon.pack()
        self.thumbnail = tk.Label(thumbnail, text = '', image = self.imageVar[2])
        self.thumbnail.pack()
        labelPane = tk.Label(infoPane.scndWidget, textvariable = self.message, relief=tk.SUNKEN)
        labelPane.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = tk.YES)
        self.listbox.focus_force()

         
        
if __name__ == '__main__':
    root = tk.Tk()
    dummy = KodiFrontEnd(root)
    dummy.pack(fill = tk.BOTH, expand = tk.YES)
    dummy.initFrameExec()
    root.mainloop()
