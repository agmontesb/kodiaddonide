'''
Created on 20/02/2015

@author: Alex Montes Barrios
'''
import os
import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
import tkSimpleDialog
import re
import xml.etree.ElementTree as ET
from xbmcStubs.xbmc import translatePath
import keyword
import FileGenerator
from SintaxEditor import PYTHONSINTAX, XMLSINTAX

SEP = '/'
IMAGEFILES = ['.bmp', '.dcx', '.eps', '.gif', '.im', '.jpg', '.jpeg', '.pcd', '.pcx', '.pdf', '.png', '.ppm', '.psd', '.tiff', '.xbm', '.xpm']

class FilteredTree(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.onTreeSelProc = None
        self.popUpMenu = None
        self.resetVariables()
        self.setGUI()
 
    def resetVariables(self):
        self._genFiles = None
        self.activeSel = None        
        self.editedContent = {}
        self.removedNodes = []
        self._activeNodes = []        
         
    def setGUI(self):
        self.srchVar = tk.StringVar()
        self.srchVar.trace('w', self.filterTree)
        entry = tk.Entry(self, textvariable = self.srchVar)
        entry.pack(side = tk.TOP, fill = tk.X)
        bottompane = tk.Frame(self)
        bottompane.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = 1)
         
        vscrollbar = tk.Scrollbar(bottompane)
        vscrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        hscrollbar = tk.Scrollbar(bottompane, orient = tk.HORIZONTAL)
        hscrollbar.pack(side = tk.BOTTOM, fill = tk.X)
         
#         treeview = ttk.Treeview(bottompane, show = 'tree', columns = ('type','editable', 'source', 'inspos'), displaycolumns = ())
        treeview = ttk.Treeview(bottompane, show = 'tree')
        treeview.pack(fill = tk.BOTH, expand = tk.YES)
        treeview.tag_configure('activeNode', background = 'light green')
        treeview.tag_configure('filterNode', foreground = 'red')
        treeview.event_add('<<myEvent>>','<Double-1>','<Return>')
        treeview.bind('<<myEvent>>', self.onTreeSelEvent)
        treeview.bind('<Button-3>',self.do_popup)
        treeview.column('#0', width = 400, stretch = False )
         
        treeview.config(xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=treeview.yview)
        hscrollbar.config(command=treeview.xview)
         
        self.treeview = treeview
#         self.actTreeSel = None
         
    def setOnTreeSelProc(self, onTreeSelProc):
        self.onTreeSelProc = onTreeSelProc
         
    def setPopUpMenu(self, popUpMenu):
        self.popUpMenu = popUpMenu
 
    def filterTree(self, *args, **kwargs):
        for node, parent, index in self.removedNodes:
            self.treeview.move(node, parent, index)
        srchTxt = self.srchVar.get()
        allNodes = self.getAllNodes()
        for nodeId, nodeText in allNodes: self.treeview.item(nodeId, open = False)
        for nodeId, nodeText in allNodes:
            fltrTest = self.treeview.item(nodeId, 'open') or nodeText.find(srchTxt) != -1
            self.treeview.item(nodeId, open = fltrTest)
            if fltrTest: self.treeview.see(nodeId)
 
        self.removedNodes = self.getCloseNodes()
        for node, parent, index in self.removedNodes:
            self.treeview.detach(node)
             
    def getAllNodes(self, nodeId = '', lista = None):
        lista = lista or []
        for node in self.treeview.get_children(nodeId):
            lista.append((node, self.treeview.item(node, 'text')))
            lista = self.getAllNodes(node, lista)
        return lista
 
    def getCloseNodes(self, nodeId = '', lista = None):
        lista = lista or []
        for node in self.treeview.get_children(nodeId):
            if not self.treeview.item(node, 'open'):
                parent = self.treeview.parent(node)
                index = self.treeview.get_children(parent).index(node) 
                lista.append((node, parent, index))
            else:
                lista = self.getCloseNodes(node, lista)
        return lista
 
    def onTreeSelEvent(self, event):
        if self.onTreeSelProc: self.onTreeSelProc(node = None)
         
    def do_popup(self, event):
        if self.popUpMenu: self.popUpMenu()
        
    def setActiveSel(self, newSel):
        if self.activeSel != newSel:
            if self.activeSel and self.treeview.exists(self.activeSel):
                iid = self.activeSel
                tags = self.treeview.item(iid, 'tags')
                tags = [tag for tag in tags if tag != 'activeNode']
                self.treeview.item(iid, tags = tags)
            
            iid = newSel
            tags = self.treeview.item(iid, 'tags')
            tags = list(tags).append('activeNode') if tags else ('activeNode',)
            self.treeview.item(iid, tags = tags)
            self.activeSel = iid      
        
        
         
class treeExplorer(FilteredTree):
    def __init__(self, master, addonSettings, fileGenerator):
        FilteredTree.__init__(self, master)
        self.setExplorerParam(addonSettings, fileGenerator)
        self.treeview.config(columns = ('type','editable', 'source', 'inspos'), displaycolumns = ())
        self.editorWidget = None
        self.setOnTreeSelProc(self.onTreeSelection)
        self.setPopUpMenu(self.treeExpPopUpMenu)
        self.menuBar = {}
         
    def setExplorerParam(self, addonSettings, fileGenerator):
        self.resetVariables()
        self._addonSettings = addonSettings
        self._genFiles = fileGenerator
        self.refreshFlag = True
        
    def getAddonTemplate(self):
        addonTemplate = self.getAddonStruct(self._addonSettings, self._genFiles)
        rootId = self._addonSettings.getParam('addon_id')
        addonTemplate[0] = rootId + SEP + addonTemplate[0].partition(SEP)[2]
        for elem in addonTemplate[1:]: elem[0] = rootId + SEP + elem[0]
        return addonTemplate
        
    def refreshPaneInfo(self):
        self.activeSel = None
        self.refreshFlag = False
        addonTemplate = self.getAddonTemplate()
        activeNode = addonTemplate[0]
        addonTemplate = addonTemplate[1:]   
        topLevelNodes = self.treeview.get_children()
        if topLevelNodes: self.treeview.delete(*topLevelNodes)
        rootId = activeNode.partition(SEP)[0]
        self.treeview.insert('', 'end', rootId, text = rootId, values = ('dir', True, '', ''))
 
        dependencyStr = rootId + SEP + 'Dependencies'
        notdep = [elem for elem in addonTemplate if not elem[0].startswith(dependencyStr)]
        notdep.append([dependencyStr, {'type':'requires', 'editable':False, 'source':''}])
        for elem in notdep:
            self.registerNode(elem[0], childName = True)
            if elem[1]['type'] == 'file' and not os.path.splitdrive(elem[1]['source'])[0]:
                elem[1]['source'] = os.path.join(os.getcwd(), elem[1]['source'])
            for dKey, dValue in elem[1].items():
                self.treeview.set(elem[0], column = dKey, value = dValue)
 
        dependencies = [elem for elem in addonTemplate if elem[0].startswith(dependencyStr)]                             
        for elem in dependencies:
            depIid = os.path.dirname(elem[0])
            if elem[1]['source'].startswith('xbmc'): continue
            self.onNewDependency(iid = depIid, newDependency = elem[1]['source'])
         
        self.treeview.set(rootId, column = 'type', value = 'root')
        self.onTreeSelection(node = activeNode)
 
    def getAddonStruct(self, addonSettings, fileGenerator):
        getData = lambda setting: [map(lambda x: x.strip(), elem.split(',')) for elem in setting.split('|')]
        getFileLoc = lambda fileLoc, fileName:os.path.join(os.path.normpath(fileLoc), fileName).replace(os.sep,'/').replace('./','')
        addonTemplate = [addonSettings.getParam("addon_id")]
        if not addonSettings.getParam('generatedFiles'):
            generatedFiles = fileGenerator.listFiles()
        else:
            generatedFiles = getData(addonSettings.getParam('generatedFiles'))
     
        for elem in generatedFiles:
            fileId, fileName, fileLoc, isEditable = elem
            fileLoc = getFileLoc(fileLoc,fileName)
            addonTemplate.append([fileLoc, {'type':'genfile', 'editable':isEditable, 'source':fileId, 'inspos':'1.0'}])
             
        for key, fileName in [('addon_icon', 'icon.png'), ('addon_fanart', 'fanart.jpg'), ('addon_license', 'licence.txt'), ('addon_changelog', 'changelog.txt')]:
            source = addonSettings.getParam(key)
            if source:
                addonTemplate.append([fileName, {'type':'file', 'editable':True, 'source':source}])
             
        resources = getData(addonSettings.getParam('addon_resources'))
        for elem in resources:
            fileName, fileLoc, isEditable, source = elem
            fileLoc = getFileLoc(fileLoc,fileName)
            isEditable = isEditable or 'True'
            source = source or fileName
            addonTemplate.append([fileLoc, {'type':'file', 'editable':isEditable, 'inspos':'1.0', 'source':source}])
     
        dependencies = getData(addonSettings.getParam('addon_requires'))
        for elem in dependencies:
            fileName, fileVer, fileOp = elem
            fileLoc = getFileLoc('Dependencies',fileName)
            addonTemplate.append([fileLoc, {'type':'depdir', 'editable':False, 'source':fileName, 'inspos':fileVer}])
     
        addonTemplate.insert(0,addonTemplate.pop(0) + "/" + addonTemplate[0][0])
        return addonTemplate
    
    def onTreeSelection(self, node = None):
        nodeId = node or self.treeview.focus()
        prevActiveNode = self.setActiveNode(nodeId)
        if self.treeview.set(prevActiveNode, column = 'type') in ['file', 'depfile']:
            insertIndx = self.editorWidget.textw.index('insert')
            self.treeview.set(prevActiveNode, column = 'inspos', value = insertIndx)
        if self.editorWidget.textw.edit_modified():
            self.editedContent[prevActiveNode] = self.editorWidget.textw.get('1.0','end')
        itype, isEditable, source, inspos = self.treeview.item(nodeId, 'values')        
        if itype == 'markpos':
            parent = self.treeview.parent(nodeId)
            if prevActiveNode != parent: 
                self.onTreeSelection(node = parent)
                self.setActiveNode(nodeId)
            self.editorWidget.setCursorAt(inspos)
        elif itype.endswith('file'):
            editedFlag = self.editedContent.has_key(nodeId)
            fileId = source                
            if editedFlag:
                content = self.editedContent.pop(nodeId)
                source = self._genFiles.getFileName(fileId)
                fileExt = (os.path.splitext(source)[1]).lower()
            elif itype == 'genfile':
#                 fileId = source
                source = self._genFiles.getFileName(fileId)
                content  = self._genFiles.getSource(fileId)
                fileExt = (os.path.splitext(source)[1]).lower()
            else:
                if not os.path.exists(source): return tkMessageBox.showerror('File not found', 'Check the file path')
                fileExt = (os.path.splitext(source)[1]).lower()
                if fileExt in IMAGEFILES:
                    try:
                        from PIL import ImageTk  # @UnresolvedImport
                    except:
                        return tkMessageBox.showerror('Dependencies not meet', 'For image viewing PIL is needed. Not found in your system ')
                    else:
                        self.image = ImageTk.PhotoImage(file = source)
                        content = self.image                                
                        inspos, editedFlag = 'end', False
                else:
                    with open(source, 'r') as f:
                        content = f.read()
            if fileExt in IMAGEFILES:
                fsintax = None
            elif fileExt == '.py' :
                fsintax = PYTHONSINTAX
            elif  fileExt == '.xml': fsintax = XMLSINTAX
            else:                    fsintax = None
            if fsintax == PYTHONSINTAX: self.fetchTextOutline(content, nodeId) 
            itype, source  
            self.editorWidget.setContent((content, itype, fileId), inspos, fsintax, eval(str(isEditable)))
            self.editorWidget.textw.edit_modified(editedFlag)

    def treeExpPopUpMenu(self):
        selNode = self.treeview.focus()
        if not selNode: selNode = ''
        itype = self.treeview.set(selNode, 'type')
        if itype == 'depfile': return False
        self.menuBar['popup'] = tk.Menu(self, tearoff=False)
        menuOpt = []
        menuOpt.append(('command', 'Rename','Ctrl+R', 0, self.onRename))
        if itype != 'root': menuOpt.append(('command', 'Delete','Ctrl+D', 0, self.onDelete))
        menuOpt.append(('separator',))            
        menuOpt.append(('command', 'Properties','Ctrl+P', 0, self.dummyCommand))
        if itype == 'depdir': 
            menuOpt = menuOpt[2:]
            menuOpt.insert(0,('command', 'Delete','Ctrl+D', 0, self.onDelDependency))
        if itype == 'requires':
            menuOpt.pop(1)
            menuOpt.insert(0,('command', 'New dependency','Ctrl+D', 0, self.onNewDependency))
            menuOpt.insert(1,('separator',))
        if itype not in ['genfile', 'file', 'requires', 'depdir']:
            menuOpt.insert(0,('cascade', 'Insert New', 0))
            menuOpt.insert(1,('separator',))
        self.makeMenu('popup', menuOpt)    
         
        if self.menuBar.get('popup' + SEP + 'Insert_New', None):    
            menuOpt = []
            menuOpt.append(('command', 'Genfile','Ctrl+B', 0, self.dummyCommand))
            menuOpt.append(('command', 'File','Ctrl+A', 0, self.onInsertFile))
            menuOpt.append(('command', 'Dir','Ctrl+A', 0, self.onInsertDir))        
            self.makeMenu('popup' + SEP + 'Insert_New', menuOpt)
        return True
         
    def do_popup(self, event):
        nodeId = self.treeview.identify_row(event.y)
        self.onTreeSelection(node = nodeId)
        self.popUpMenu()
        try:
            menu = self.menuBar['popup']
        except:
            pass
        else:
            menu.post(event.x_root, event.y_root)
            menu.grab_release()
            
    def dummyCommand(self):
        tkMessageBox.showerror('Not implemented', 'Not yet available')
         
    def setActiveNode(self, nodeId):
        self.treeview.see(nodeId)
        self.treeview.selection_set(nodeId)
        self.treeview.focus(nodeId)
        itype = self.treeview.set(nodeId, 'type')
#         activeNodes = self._activeNodes
        activeNode = self.activeSel
        if itype.endswith('file'):
            self.setActiveSel(nodeId)
#             for elem in activeNodes:
#                 nodeTags = [tag for tag in self.treeview.item(elem,'tags') if tag != 'activeNode']
#                 self.treeview.item(elem, tags = nodeTags) 
#             tags = self.treeview.item(nodeId,'tags')
#             nodeTags = list(tags).append('activeNode') if tags else ('activeNode',)
#             self.treeview.item(nodeId, tags = nodeTags)
#             self._activeNodes = [nodeId]
        return activeNode or ''
         
    def setEditorWidget(self, editorWidget):
        self.editorWidget = editorWidget 
         
    def registerNode(self, iid, childName = False):
        treeview = self.treeview
        if treeview.exists(iid): return
        iidPart = iid.rpartition(SEP)
        if len(iidPart[1]) and not treeview.exists(iidPart[0]):
            self.registerNode(iidPart[0], childName)
        nodeValues = self.treeview.item(iidPart[0], 'values')
        treeview.insert(iidPart[0], 'end',iid, values = nodeValues)
        if childName:
            treeview.item(iid, text = iidPart[2])
            
    def onDelDependency(self):
        iid = self.treeview.focus()
        self.modDependencies('delete', iid, None)
        self.treeview.delete(iid)
         
    def onNewDependency(self, iid = None, newDependency = None):
        iid = iid or self.treeview.focus() 
        addonsPath = translatePath('special://home/addons')
 
        if newDependency and os.path.exists(os.path.join(addonsPath, newDependency)):
            newDependency = os.path.join(addonsPath, newDependency)            
        elif newDependency:
            newDependency = tkFileDialog.askdirectory(title = newDependency + 'not found, please set new dependency', initialdir = addonsPath, mustexist=True)
        else:
            newDependency = tkFileDialog.askdirectory(title = 'New dependency', initialdir = addonsPath, mustexist=True)
        if newDependency:
            xmlfile = ET.parse(os.path.join(newDependency,'addon.xml')).getroot()
            addonVer = xmlfile.get('version')
            source = os.path.basename(newDependency)
            self.modDependencies('insert', source, addonVer)
            self.insertDirectory(iid, newDependency, values = ('depdir', False, source, addonVer), excludeext = ('.pyc', '.pyo'))
            
 
    def insertDirectory(self, dirParent = None, dirName = None, values = None, excludeext = None):
        if not dirName:
            dirName = tkFileDialog.askdirectory()
        dirName = os.path.normpath(dirName + os.sep)
        head, destino = os.path.split(dirName)
        idBaseDir = self.insertFolder(dirParent, destino)
        values = values or ()
        excludeext = excludeext or ()
        self.treeview.item(idBaseDir, values = values)
        itype, edit, source, inspos = values
        itype = 'depfile' if itype == 'depdir' else 'file'
        inspos = '1.0'
        lenDestino = len(dirName)
        for dirname, subshere, fileshere in os.walk(dirName):
            for fname in fileshere:
                if os.path.splitext(fname)[1] in excludeext:continue
                fname = os.path.join(dirname, fname)
                fnameNew = fname[lenDestino:]
                nodeName, extName = os.path.splitext(fnameNew)
                nodeId = idBaseDir + fnameNew.replace(os.sep, SEP)
                self.registerNode(nodeId, childName = True)
                self.treeview.item(nodeId, values = (itype, edit, fname, inspos))
                 
    def insertFolder(self, folderParent = None, folderName = None):
        parentId = folderParent or self.treeview.focus()
        if not folderName:
            folderName = tkSimpleDialog.askstring('Insert nuevo elemento', 'Nombre del nuevo elemento a incluir:')
        childId = parentId + SEP + folderName 
        self.registerNode(childId, childName = True)
        colValues = self.treeview.item(parentId, 'values')
        self.treeview.item(childId, values = colValues)
        self.treeview.item(parentId, open = True )  
        self.treeview.selection_set(childId)
        self.treeview.focus(childId)
        return childId
 
    def fetchTextOutline(self,text, moduleID):
        fileTree = self.getTextTree(text, prefix = moduleID)
        for child in fileTree:
            self.registerNode(child[0], child[1])
            self.treeview.set(child[0],column = 'type', value = 'markpos')
            self.treeview.set(child[0],column = 'source', value = (child[2],child[3]))
            self.treeview.set(child[0],column = 'inspos', value = '1.0 + %d chars' % child[2])
 
    def getTextTree(self, text, prefix = ''):    
        prefixID = ''
        fileTree = []
        tIter = re.finditer('^([ \t]*)(def|class)[ \t]+([^\(:)]*).*:', text, re.MULTILINE)
        for match in tIter:
            indent = (match.end(1) - match.start(1))/4 if match.group(1) else 0
            while prefixID.count(SEP) and indent <= prefixID.count(SEP)-1:
                prefixID = prefixID.rpartition(SEP)[0]
            prefixID = prefixID + SEP + match.group(2) + '('+match.group(3)+')'
            prefixMOD = prefix + prefixID if prefix else prefixID[1:]
            fileTree.append((prefixMOD, match.group(3), match.start(3), match.end(3)))
        return fileTree
 
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
                menuLabel = masterID + SEP + mLabel.replace(' ','_')
                self.menuBar[menuLabel] = tk.Menu(master, tearoff = False)
                master.add('cascade',
                           label = '{:30s}'.format(mLabel),
                           underline = mUnderline,
                           menu = self.menuBar[menuLabel])
            else:
                master.add('separator') 
 
    def onRename(self):
        iid = self.treeview.focus()
        oldName = self.treeview.item(iid, 'text')
        newName = tkSimpleDialog.askstring('Rename', 'Input new name for ' + oldName, initialvalue = oldName)
        if newName:
            self.modResources('rename', iid, None, None, newName)
            self.treeview.item(iid, text = newName)
     
    def onDelete(self):
        iid = self.treeview.focus()
        self.modResources('delete', iid, None, None, None)
        self.treeview.delete(iid)
        
    def modDependencies(self, modType, dependency, version):
        addonRequires = self._addonSettings.getParam('addon_requires')
        if modType == 'insert':
            pattern = '\|* *' + dependency + ',[^|]+'
            if not re.search(pattern, addonRequires):
                addonRequires = '|'.join([addonRequires,','.join([dependency, version, ''])])
        elif modType == 'delete':
            dependency = dependency.rpartition(SEP)[2]
            pattern = '\|* *' + dependency + ',[^|]+'
            toRep = re.compile(pattern)
            addonRequires = toRep.sub('', addonRequires)
        self._addonSettings.settings['addon_requires'] = addonRequires
        
        
    def modResources(self, modType, fileName, location, isEditable, fileSource):
        addonResources = self._addonSettings.getParam('addon_resources')
        if modType == 'insert':
            location = location.partition(SEP)[2]
            nFileSource = os.path.normpath(fileSource)
            if nFileSource.startswith(os.getcwd()): fileSource = fileSource[len(os.getcwd())+1:]
            addonResources = '|'.join([addonResources, ','.join([fileName, location, str(isEditable), fileSource])])
        elif modType == 'delete':
            fileName = fileName.rpartition(SEP)[2]
            pattern = '\|* *' + fileName + ',[^|]+'
            toRep = re.compile(pattern)
            addonResources = toRep.sub('', addonResources)
        elif modType == 'rename':
            fileName = fileName.rpartition(SEP)[2]
            addonResources = addonResources.replace(fileName + ',', fileSource + ',')
            pass
        self._addonSettings.settings['addon_resources'] = addonResources
        self._addonSettings.refreshFlag = True
 
    def onInsertFile(self):
        pathName = tkFileDialog.askopenfilenames(filetypes=[('python Files', '*.py'), ('xml Files', '*.xml'), ('Image Files', '*.jpg, *.png'), ('All Files', '*.*')])
        if pathName:
            location = self.treeview.focus()
            for fileSource in pathName:
                fileExt = os.path.splitext(fileSource)[1]
                fileName = os.path.basename(fileSource)
                isEditable = fileExt not in IMAGEFILES
                childId = SEP.join((location, fileName))
                self.modResources('insert', fileName, location, isEditable, fileSource)
                self.treeview.insert(location, 'end', iid = childId, text = fileName, values = ('file', isEditable, fileSource, '1.0' ))
 
    def onInsertDir(self):
        parent = self.treeview.focus()
        newDir = tkSimpleDialog.askstring('Insert directory', 'Input name for new directory')
        if newDir:
            childId = SEP.join((parent, newDir))
            newDirId = self.treeview.insert(parent, 'end', iid = childId,text = newDir, values = ('dir', True, '', ''))
            self.treeview.focus(newDirId)
        

class ApiTree(FilteredTree):
    def __init__(self, master, xbmcThread):
        FilteredTree.__init__(self, master)
        self.treeview.config(columns = ('name', ), displaycolumns = ())
        self.setXbmcThread(xbmcThread)
        self.popUpMenu = None
        
    def setXbmcThread(self, xbmcThread):
        self.xbmcThread = xbmcThread
        self.activeSel = None
        self.refreshFlag = True
        
    def refreshPaneInfo(self):
        if self.refreshFlag and self.xbmcThread:
            if self.treeview.exists('rootmenu'): self.treeview.delete('rootmenu')
            if self.treeview.exists('media'): self.treeview.delete('media')
            self.registerTreeNodes('rootmenu')
            self.registerTreeNodes('media')
        self.refreshFlag = False
        self.activeNode = None
        self.setActualKnot()
    
#     def getPopUpMenu(self, threadId = None):
#         popup = tk.Menu(self, tearoff = 0)
#         if threadId: popup.add_command(label = threadId)
#         popup.add_command(label = 'Set as ActiveKnot', command = self.onTreeSelProc)
#         popup.add_command(label = 'Previous')
#         popup.add_separator()
#         popup.add_command(label = 'Home')
#         return popup
    
    def do_popup(self, event):
        if not self.popUpMenu: return
        threadId = self.treeview.identify_row(event.y)
        self.xbmcThread.threadDef = threadId.rsplit('.', 1)[1] if threadId.find('.') != -1 else threadId
        self.setSelection(threadId)
        popup = self.popUpMenu()        
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()

    def setActualKnot(self):
        if not self.xbmcThread: return
        if self.xbmcThread.threadDef:
            iid = self.getAbsoluteId(self.xbmcThread.threadDef, absFlag = False)
            self.setActiveSel(iid)
        
    def refreshTreeInfo(self, activeThread = None, lstChanged = None):
        if not activeThread: activeThread = self.xbmcThread.threadDef
        if not lstChanged: return
        while lstChanged:
            threadId = lstChanged.pop()
#             if threadId.endswith('_lnk') and threadId.startswith('media'): continue 
            if self.treeview.exists(threadId): 
                self.delete(threadId)
            else:
                parentId, sep, threadId = threadId.rpartition('.') 
                self.registerTreeNodes(threadId)
                self.treeItemExpand(parentId, absFlag = True, flag = True)
        self.setSelection(activeThread, absFlag = False)
#         self.parseTree.setSelection(parseKnotId, absFlag = False)
    
    def getAbsoluteId(self, threadId, absFlag = True):
        return threadId if absFlag else self.xbmcThread.getDotPath(threadId)
    
    def registerTreeNodes(self, threadId = 'media'):
        threadKnots = self.xbmcThread.getSameTypeNodes(threadId)
        itemId = self.getAbsoluteId(self.xbmcThread.threadDef, absFlag = False)
        leaves = [itemId]
        for elem in threadKnots:
            if elem.endswith('_lnk') and not self.xbmcThread.getThreadParam(elem, 'source'): continue
            itemId = self.getAbsoluteId(elem, absFlag = False)
            itemParams = [itemId, {}]
            itemParams[1]['name'] = elem
            leaves.append(itemParams)
    
        for elem in leaves[1:]:
            self.registerNode(elem[0], childName = True)
            for dKey, dValue in elem[1].items():
                self.treeview.set(elem[0], column = dKey, value = dValue)
    
        selItem = leaves[0]
        if self.treeview.exists(selItem):
            while selItem.rpartition('.')[1]:
                self.treeview.item(selItem.rpartition('.')[0], open = True )
                selItem = selItem.rpartition('.')[0]
            self.treeview.selection_set(leaves[0])
            self.treeview.focus(leaves[0])

    def registerNode(self, iid, childName = False, absFlag = True):
        iid = self.getAbsoluteId(iid, absFlag)
        if self.treeview.exists(iid): return
        iidPart = iid.rpartition('.')
        if len(iidPart[1]) and not self.treeview.exists(iidPart[0]):
            self.registerNode(iidPart[0], childName)
        self.treeview.insert(iidPart[0], 'end',iid)
        if childName:
            self.treeview.item(iid, text = iidPart[2])
        
    def treeItemExpand(self, threadId, absFlag = True, flag = True):
        itemId = self.getAbsoluteId(threadId, absFlag)
        self.treeview.item(itemId, open = flag )  
        
    def delete(self, *items):
        items = [thread for thread in items if self.treeview.exists(thread)]
        if items: self.treeview.delete(*items)   
        
    def setSelection(self, threadId, absFlag = True):
        iid = self.getAbsoluteId(threadId, absFlag)
        self.setActualKnot()        
        self.treeview.focus(iid)
        self.treeview.selection_set(iid)
        
        
  
# class treeExplorer(tk.Frame):
#     def __init__(self, master, settings = None):
#         tk.Frame.__init__(self, master)
#         self.editorWidget = None
#         self.menuBar = {}
#         self.resetVariables()
#         self.setGUI()
#          
#     def resetVariables(self):
#         self._genFiles = None        
#         self.editedContent = {}
#         self.removedNodes = []
#         self._activeNodes = []        
#          
#          
#     def setGUI(self):
#         self.srchVar = tk.StringVar()
#         self.srchVar.trace('w', self.filterTree)
#         entry = tk.Entry(self, textvariable = self.srchVar)
#         entry.pack(side = tk.TOP, fill = tk.X)
#         bottompane = tk.Frame(self)
#         bottompane.pack(side = tk.BOTTOM, fill = tk.BOTH, expand = 1)
#          
#         vscrollbar = tk.Scrollbar(bottompane)
#         vscrollbar.pack(side = tk.RIGHT, fill = tk.Y)
#         hscrollbar = tk.Scrollbar(bottompane, orient = tk.HORIZONTAL)
#         hscrollbar.pack(side = tk.BOTTOM, fill = tk.X)
#          
#         treeview = ttk.Treeview(bottompane, show = 'tree', columns = ('type','editable', 'source', 'inspos'), displaycolumns = ())
#         treeview.pack(fill = tk.BOTH, expand = tk.YES)
#         treeview.tag_configure('activeNode', background = 'light green')
#         treeview.tag_configure('filterNode', foreground = 'red')
#         treeview.event_add('<<myEvent>>','<Double-1>','<Return>')
#         treeview.bind('<<myEvent>>', self.onTreeSelEvent)
#         treeview.bind('<Button-3>',self.do_popup)
#         treeview.column('#0', width = 400, stretch = False )
#          
#         treeview.config(xscrollcommand=hscrollbar.set, yscrollcommand=vscrollbar.set)
#         vscrollbar.config(command=treeview.yview)
#         hscrollbar.config(command=treeview.xview)
#          
#         self.treeview = treeview
#         self.actTreeSel = None
#         return
#          
#     def setExplorerParam(self, settings, objList):
#         self.resetVariables()
#         filegenerator = FileGenerator.FileGenerator(objList)
#         addonTemplate = self.getAddonStruct(settings, filegenerator)
#         rootId = addonTemplate[0].partition(SEP)[0]
#         for elem in addonTemplate[1:]: elem[0] = rootId + SEP + elem[0]
#         self._genFiles = filegenerator
#         self._addonTemplate = addonTemplate
#         self.refreshFlag = True      
#          
#          
#     def refreshPaneInfo(self):
#         activeNode = self._addonTemplate[0]
#         addonTemplate = list(self._addonTemplate[1:])   
#         topLevelNodes = self.treeview.get_children()
#         if topLevelNodes: self.treeview.delete(*topLevelNodes)
#         rootId = activeNode.partition(SEP)[0]
#         self.treeview.insert('', 'end', rootId, text = rootId, values = ('dir', True, '', ''))
#  
#         notdep = [elem for elem in addonTemplate if not elem[0].startswith('Dependencies')]
#         notdep.append(['Dependencies', {'type':'requires', 'editable':False, 'source':''}])
#         for elem in notdep:
#             self.registerNode(elem[0], childName = True)
#             if elem[1]['type'] == 'file' and not os.path.splitdrive(elem[1]['source'])[0]:
#                 elem[1]['source'] = os.path.join(os.getcwd(), elem[1]['source'])
#             for dKey, dValue in elem[1].items():
#                 self.treeview.set(elem[0], column = dKey, value = dValue)
#  
#         dependencies = [elem for elem in addonTemplate if elem[0].startswith('Dependencies')]                             
#         for elem in dependencies:
#             depIid = os.path.dirname(elem[0])
#             if elem[1]['source'].startswith('xbmc'): continue
#             self.onNewDependency(iid = depIid, newDependency = elem[1]['source'])
#          
#         self.treeview.set(rootId, column = 'type', value = 'root')
#         self.onTreeSelection(node = activeNode)
#  
#  
#     def getAddonStruct(self, addonSettings, fileGenerator):
#         getData = lambda setting: [map(lambda x: x.strip(), elem.split(',')) for elem in setting.split('|')]
#         addonTemplate = [addonSettings["addon_id"]]
#         if not addonSettings.has_key('generatedFiles'):
#             generatedFiles = fileGenerator.listFiles()
#         else:
#             generatedFiles = getData(addonSettings['generatedFiles'])
#      
#         for elem in generatedFiles:
#             fileId, fileName, fileLoc, isEditable = elem
#             addonTemplate.append([str(fileLoc + fileName), {'type':'genfile', 'editable':isEditable, 'source':fileId, 'inspos':'1.0'}])
#              
#         for key, fileName in [('addon_icon', 'icon.png'), ('addon_fanart', 'fanart.jpg'), ('addon_license', 'licence.txt'), ('addon_changelog', 'changelog.txt')]:
#             source = addonSettings[key]
#             if source:
#                 addonTemplate.append([fileName, {'type':'file', 'editable':True, 'source':source}])
#              
#         resources = getData(addonSettings['addon_resources'])
#         for elem in resources:
#             fileName, fileLoc, isEditable, source = elem
#             isEditable = isEditable or 'True'
#             source = source or fileName
#             addonTemplate.append([str(fileLoc + fileName), {'type':'file', 'editable':isEditable, 'inspos':'1.0', 'source':source}])
#      
#         dependencies = getData(addonSettings['addon_requires'])
#         for elem in dependencies:
#             fileName, fileVer, fileOp = elem
#             addonTemplate.append([str('Dependencies/' + fileName), {'type':'depdir', 'editable':False, 'source':fileName}])
#      
#         addonTemplate.insert(0,addonTemplate.pop(0) + "/" + addonTemplate[0][0])
#         return addonTemplate
#                  
#     def onTreeSelEvent(self, event):
#         return self.onTreeSelection(node = None)
#  
#     def onTreeSelection(self, node):
#         nodeId = node or self.treeview.focus()
#         prevActiveNode = self.setActiveNode(nodeId)
#         if self.treeview.set(prevActiveNode, column = 'type') in ['file', 'depfile']:
#             insertIndx = self.editorWidget.textw.index('insert')
#             self.treeview.set(prevActiveNode, column = 'inspos', value = insertIndx)
#         if self.editorWidget.textw.edit_modified():
#             self.editedContent[prevActiveNode] = self.editorWidget.textw.get('1.0','end')
#         itype, isEditable, source, inspos = self.treeview.item(nodeId, 'values')        
#         if itype == 'markpos':
#             parent = self.treeview.parent(nodeId)
#             if prevActiveNode != parent: 
#                 self.onTreeSelection(node = parent)
#                 self.setActiveNode(nodeId)
#             self.editorWidget.setCursorAt(inspos)
#         elif itype.endswith('file'):
#             editedFlag = self.editedContent.has_key(nodeId)                
#             if editedFlag:
#                 content = self.editedContent.pop(nodeId)
#             elif itype == 'genfile':
#                 fileId = source
#                 source = self._genFiles.getFileName(fileId)
#                 content  = self._genFiles.getSource(fileId)
#                 fileExt = (os.path.splitext(source)[1]).lower()
#             else:
#                 if not os.path.exists(source): return tkMessageBox.showerror('File not found', 'Check the file path')
#                 fileExt = (os.path.splitext(source)[1]).lower()
#                 if fileExt in IMAGEFILES:
#                     try:
#                         from PIL import ImageTk
#                     except:
#                         return tkMessageBox.showerror('Dependencies not meet', 'For image viewing PIL is needed. Not found in your system ')
#                     else:
#                         self.image = ImageTk.PhotoImage(file = source)
#                         content = self.image                                
#                         inspos, editedFlag = 'end', False
#                 else:
#                     with open(source, 'r') as f:
#                         content = f.read()
#             if fileExt in IMAGEFILES:
#                 fsintax = None
#             elif fileExt == '.py' :
#                 fsintax = PYTHONSINTAX
#             elif  fileExt == '.xml': fsintax = XMLSINTAX
#             else:                    fsintax = None
#             if fsintax == PYTHONSINTAX: self.fetchTextOutline(content, nodeId) 
#             self.editorWidget.setContent(content, inspos, fsintax, eval(str(isEditable)))
#             self.editorWidget.textw.edit_modified(editedFlag)
#              
#      
#          
#     def do_popup(self, event):
#         nodeId = self.treeview.identify_row(event.y)
#         self.onTreeSelection(node = nodeId)
#         self.popUpMenu()
#         try:
#             menu = self.menuBar['popup']
#         except:
#             pass
#         else:
#             menu.post(event.x_root, event.y_root)
#             menu.grab_release()
#                  
#     def dummyCommand(self):
#         tkMessageBox.showerror('Not implemented', 'Not yet available')
#          
#     def setActiveNode(self, nodeId):
#         self.treeview.see(nodeId)
#         self.treeview.selection_set(nodeId)
#         self.treeview.focus(nodeId)
#         itype = self.treeview.set(nodeId, 'type')
#         activeNodes = self._activeNodes
#         if itype.endswith('file'):
#             for elem in activeNodes:
#                 nodeTags = [tag for tag in self.treeview.item(elem,'tags') if tag != 'activeNode']
#                 self.treeview.item(elem, tags = nodeTags) 
#             tags = self.treeview.item(nodeId,'tags')
#             nodeTags = list(tags).append('activeNode') if tags else ('activeNode',)
#             self.treeview.item(nodeId, tags = nodeTags)
#             self._activeNodes = [nodeId]
#         return activeNodes[0] if activeNodes else ''
#          
#     def setEditorWidget(self, editorWidget):
#         self.editorWidget = editorWidget 
#          
#     def filterTree(self, *args, **kwargs):
#         for node, parent, index in self.removedNodes:
#             self.treeview.move(node, parent, index)
#         srchTxt = self.srchVar.get()
#         allNodes = self.getAllNodes()
#         for nodeId, nodeText in allNodes: self.treeview.item(nodeId, open = False)
#         for nodeId, nodeText in allNodes:
#             fltrTest = self.treeview.item(nodeId, 'open') or nodeText.find(srchTxt) != -1
#             self.treeview.item(nodeId, open = fltrTest)
#             if fltrTest: self.treeview.see(nodeId)
#  
#         self.removedNodes = self.getCloseNodes()
#         for node, parent, index in self.removedNodes:
#             self.treeview.detach(node)
#  
#     def getAllNodes(self, nodeId = '', lista = None):
#         lista = lista or []
#         for node in self.treeview.get_children(nodeId):
#             lista.append((node, self.treeview.item(node, 'text')))
#             lista = self.getAllNodes(node, lista)
#         return lista
#  
#     def registerNode(self, iid, childName = False):
#         treeview = self.treeview
#         if treeview.exists(iid): return
#         iidPart = iid.rpartition(SEP)
#         if len(iidPart[1]) and not treeview.exists(iidPart[0]):
#             self.registerNode(iidPart[0], childName)
#         nodeValues = self.treeview.item(iidPart[0], 'values')
#         treeview.insert(iidPart[0], 'end',iid, values = nodeValues)
#         if childName:
#             treeview.item(iid, text = iidPart[2])
#          
#     def onNewDependency(self, iid = None, newDependency = None):
#         iid = iid or self.treeview.focus() 
#         addonsPath = translatePath('special://home/addons')
#  
#         if newDependency and os.path.exists(os.path.join(addonsPath, newDependency)):
#             newDependency = os.path.join(addonsPath, newDependency)            
#         elif newDependency:
#             newDependency = tkFileDialog.askdirectory(title = newDependency + 'not found, please set new dependency', initialdir = addonsPath, mustexist=True)
#         else:
#             newDependency = tkFileDialog.askdirectory(title = 'New dependency', initialdir = addonsPath, mustexist=True)
#         if newDependency:
#             xmlfile = ET.parse(os.path.join(newDependency,'addon.xml')).getroot()
#             addonVer = xmlfile.get('version')
#             source = os.path.basename(newDependency)
#             self.insertDirectory(iid, newDependency, values = ('depdir', False, source, addonVer), excludeext = ('.pyc', '.pyo'))
#  
#     def insertDirectory(self, dirParent = None, dirName = None, values = None, excludeext = None):
#         if not dirName:
#             dirName = tkFileDialog.askdirectory()
#         dirName = os.path.normpath(dirName + os.sep)
#         head, destino = os.path.split(dirName)
#         idBaseDir = self.insertFolder(dirParent, destino)
#         values = values or ()
#         excludeext = excludeext or ()
#         self.treeview.item(idBaseDir, values = values)
#         itype, edit, source, inspos = values
#         itype = 'depfile' if itype == 'depdir' else 'file'
#         inspos = '1.0'
#         lenDestino = len(dirName)
#         for dirname, subshere, fileshere in os.walk(dirName):
#             for fname in fileshere:
#                 if os.path.splitext(fname)[1] in excludeext:continue
#                 fname = os.path.join(dirname, fname)
#                 fnameNew = fname[lenDestino:]
#                 nodeName, extName = os.path.splitext(fnameNew)
#                 nodeId = idBaseDir + fnameNew.replace(os.sep, SEP)
#                 self.registerNode(nodeId, childName = True)
#                 self.treeview.item(nodeId, values = (itype, edit, fname, inspos))
#                  
#     def insertFolder(self, folderParent = None, folderName = None):
#         parentId = folderParent or self.treeview.focus()
#         if not folderName:
#             folderName = tkSimpleDialog.askstring('Insert nuevo elemento', 'Nombre del nuevo elemento a incluir:')
#         childId = parentId + SEP + folderName 
#         self.registerNode(childId, childName = True)
#         colValues = self.treeview.item(parentId, 'values')
#         self.treeview.item(childId, values = colValues)
#         self.treeview.item(parentId, open = True )  
#         self.treeview.selection_set(childId)
#         self.treeview.focus(childId)
#         return childId
#  
#     def getCloseNodes(self, nodeId = '', lista = None):
#         lista = lista or []
#         for node in self.treeview.get_children(nodeId):
#             if not self.treeview.item(node, 'open'):
#                 parent = self.treeview.parent(node)
#                 index = self.treeview.get_children(parent).index(node) 
#                 lista.append((node, parent, index))
#             else:
#                 lista = self.getCloseNodes(node, lista)
#         return lista
#  
#     def fetchTextOutline(self,text, moduleID):
#         fileTree = self.getTextTree(text, prefix = moduleID)
#         for child in fileTree:
#             self.registerNode(child[0], child[1])
#             self.treeview.set(child[0],column = 'type', value = 'markpos')
#             self.treeview.set(child[0],column = 'source', value = (child[2],child[3]))
#             self.treeview.set(child[0],column = 'inspos', value = '1.0 + %d chars' % child[2])
#  
#     def getTextTree(self, text, prefix = ''):    
#         prefixID = ''
#         fileTree = []
#         tIter = re.finditer('^([ \t]*)(def|class)[ \t]+([^\(:)]*).*:', text, re.MULTILINE)
#         for match in tIter:
#             indent = (match.end(1) - match.start(1))/4 if match.group(1) else 0
#             while prefixID.count(SEP) and indent <= prefixID.count(SEP)-1:
#                 prefixID = prefixID.rpartition(SEP)[0]
#             prefixID = prefixID + SEP + match.group(2) + '('+match.group(3)+')'
#             prefixMOD = prefix + prefixID if prefix else prefixID[1:]
#             fileTree.append((prefixMOD, match.group(3), match.start(3), match.end(3)))
#         return fileTree
#  
#     def popUpMenu(self):
#         selNode = self.treeview.focus()
#         if not selNode: selNode = ''
#         itype = self.treeview.set(selNode, 'type')
#         if itype in ['depdir', 'depfile']: return False
#         self.menuBar['popup'] = tk.Menu(self, tearoff=False)
#         menuOpt = []
#         menuOpt.append(('command', 'Rename','Ctrl+R', 0, self.onRename))
#         if itype != 'root': menuOpt.append(('command', 'Delete','Ctrl+D', 0, self.onDelete))
#         menuOpt.append(('separator',))            
#         menuOpt.append(('command', 'Properties','Ctrl+P', 0, self.dummyCommand))
#         if itype == 'requires':
#             menuOpt.pop(1)
#             menuOpt.insert(0,('command', 'New dependency','Ctrl+D', 0, self.onNewDependency))
#             menuOpt.insert(1,('separator',))
#         if itype not in ['genfile', 'file', 'requires']:
#             menuOpt.insert(0,('cascade', 'Insert New', 0))
#             menuOpt.insert(1,('separator',))
#         self.makeMenu('popup', menuOpt)    
#          
#         if self.menuBar.get('popup' + SEP + 'Insert_New', None):    
#             menuOpt = []
#             menuOpt.append(('command', 'Genfile','Ctrl+B', 0, self.dummyCommand))
#             menuOpt.append(('command', 'File','Ctrl+A', 0, self.onInsertFile))
#             menuOpt.append(('command', 'Dir','Ctrl+A', 0, self.onInsertDir))        
#             self.makeMenu('popup' + SEP + 'Insert_New', menuOpt)
#         return True
#  
#     def makeMenu(self, masterID, menuArrDesc):
#         master = self.menuBar[masterID]
#         for menuDesc in menuArrDesc:
#             menuType = menuDesc[0]
#             if menuType == 'command':
#                 menuType, mLabel, mAccelKey, mUnderline, mCommand =  menuDesc
#                 master.add(menuType,
#                            label = '{:30s}'.format(mLabel),
#                             accelerator = mAccelKey,
#                             underline = mUnderline, 
#                             command = mCommand)
#             elif menuType == 'cascade':
#                 menuType, mLabel, mUnderline =  menuDesc
#                 menuLabel = masterID + SEP + mLabel.replace(' ','_')
#                 self.menuBar[menuLabel] = tk.Menu(master, tearoff = False)
#                 master.add('cascade',
#                            label = '{:30s}'.format(mLabel),
#                            underline = mUnderline,
#                            menu = self.menuBar[menuLabel])
#             else:
#                 master.add('separator') 
#  
#     def onRename(self):
#         iid = self.treeview.focus()
#         oldName = self.treeview.item(iid, 'text')
#         newName = tkSimpleDialog.askstring('Rename', 'Input new name for ' + oldName, initialvalue = oldName)
#         if newName:
#             self.treeview.item(iid, text = newName)
#      
#     def onDelete(self):
#         iid = self.treeview.focus()
#         self.treeview.delete(iid)
#  
#     def onInsertFile(self):
#         pathName = tkFileDialog.askopenfilenames(filetypes=[('python Files', '*.py'), ('xml Files', '*.xml'), ('Image Files', '*.jpg, *.png'), ('All Files', '*.*')])
#         if pathName:
#             iid = self.treeview.focus()
#             for elem in pathName.split(' '):
#                 fileExt = os.path.splitext(elem)[1]
#                 self.treeview.insert(iid, 'end', text = os.path.basename(elem), values = ('file', fileExt not in IMAGEFILES, elem, '1.0' ))
#  
#     def onInsertDir(self):
#         iid = self.treeview.focus()
#         newDir = tkSimpleDialog.askstring('Insert directory', 'Input name for new directory')
#         if newDir:
#             newDirId = self.treeview.insert(iid, 'end', text = newDir, values = ('dir', True, '', ''))
#             self.treeview.focus(newDirId)
#          
