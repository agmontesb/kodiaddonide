'''
Created on 19/03/2015

@author: Alex Montes Barrios
'''
import Tkinter as tk
import xml.etree.ElementTree as ET
import tkMessageBox
import json
import menuThreads
import ParseThreads
from OptionsWnd import scrolledFrame


class xmlFileWrapper():
    def __init__(self, xmlFile, nonDefaultValues = None):
        self.root = ET.parse(xmlFile).getroot()
        self.paneId = 'category'
        self.ver = 0
        self.refreshFlag = False
        self.setNonDefaultParams(nonDefaultValues)
        self.setActivePaneIndx()
        
    def getVer(self):
        return self.ver
    
    def setPaneId(self, paneId):
        self.paneId = paneId
        
    def setNonDefaultParams(self, nonDefSettings, refreshFlag = True):
        self.settings = nonDefSettings or {}
        self.refreshFlag = refreshFlag
        self.ver += 1
        
    def getNonDefaultParams(self):
        return self.settings

    def processChangedSettings(self, changedSettings):
        if changedSettings.has_key('reset'): changedSettings.pop('reset')
        self.settings.update(changedSettings)

    def getParam(self, srchSett = None):
        root = self.root
        if not srchSett:
            settings = {}
            for elem in root.findall('.//setting[@default]'):
                settings[elem.get('id')] = elem.get('default')
            settings.update(self.settings)
        else:
            if self.settings.has_key(srchSett): return self.settings[srchSett]
            srchStr = './/setting[@id="' + srchSett + '"]'
            settings = root.findall(srchStr)
            settings = settings[0].get('default') if settings else ''
        return settings
    
    def getActivePane(self):
        return self.root.findall(self.paneId)[self.actPaneIndx]        

    def setActivePaneIndx(self, index = 0):
        self.actPaneIndx = index
        
class threadXmlFileWrapper(xmlFileWrapper):
    def __init__(self, xmlFile, kodiThreads):
        xmlFileWrapper.__init__(self, xmlFile)
        self.kodiThreads = kodiThreads
        
    def getActivePane(self):
        threadId = self.kodiThreads.threadDef
        threadType = self.kodiThreads.getThreadAttr(threadId, 'type')
        srchStr = './/category[@label="' + threadType + '"]'
        threadPane = self.root.find(srchStr)
        settings = self.getNodeSettings(threadId, threadType, threadPane)
        self.setNonDefaultParams(settings, refreshFlag = False) 
        return threadPane
    
    def getNodeSettings(self, nodeId, nodeType, nodeConfigData):
        nodeDataIds = [key.get('id') for key in nodeConfigData.findall('setting') if key.get('id', None)]
        settings = dict(self.kodiThreads.parseThreads[nodeId])
        params = settings.pop('params')
        settings['nodeId'] = nodeId
        if settings.has_key('up'):
            baseNode = 'rootmenu' if nodeType == 'list' else 'media'
            lista = [elem for elem in self.kodiThreads.getSameTypeNodes(baseNode) if not elem.endswith('_lnk')]
            upMenu = '|'.join([settings['up']] + sorted(lista)) if nodeId != 'media' else ''
            settings['upmenu'] = upMenu
        other = set(params.keys()).difference(nodeDataIds)
        if len(other):
            params = dict(params)
            otherParameters = '|'.join([key + ',' + str(params.pop(key)) for key in other])
            settings['otherparameters'] = otherParameters
        settings.update(params)
        return settings
    
    def processChangedSettings(self, changedSettings):
        nodeId = self.settings['nodeId']
        nodeParams = self.kodiThreads.getThreadAttr(nodeId,'params')
        parameters = {}
        if changedSettings.has_key('otherparameters') or 'otherparameters' in changedSettings['reset']:
            if self.settings.has_key('otherparameters'):
                oldOther = [tuple(elem.split(',')) for elem in self.settings['otherparameters'].split('|')]
                for key, value in oldOther:
                    nodeParams.pop(key)
        for key in changedSettings.pop('reset'):
            self.settings.pop(key)
            if nodeParams.has_key(key): nodeParams.pop(key)
        if changedSettings.get('otherparameters', None):
            otherParameters = [tuple(elem.split(',')) for elem in changedSettings['otherparameters'].split('|')]
            parameters.update(otherParameters)
        for elem in  set(changedSettings.keys()).difference(['otherparameters', 'nodeId', 'upmenu', 'name']):
            parameters[elem] = changedSettings[elem]
        if parameters: nodeParams.update(parameters)

        nodeFlag = nodeId in ['media', 'rootmenu']
        if nodeFlag:
            for key in ['nodeId', 'name', 'upmenu']: 
                if changedSettings.has_key(key): changedSettings.pop(key)

        lstChanged = []
        if changedSettings.has_key('nodeId'):
            lstChanged.append(self.kodiThreads.getDotPath(self.settings['nodeId']))
            self.kodiThreads.rename(self.settings['nodeId'], changedSettings['nodeId'])
            lstChanged.append(self.kodiThreads.getDotPath(changedSettings['nodeId']))
            nodeId = changedSettings['nodeId']
        if changedSettings.has_key('name'):
            self.kodiThreads.parseThreads[nodeId]['name'] = changedSettings['name']
        if changedSettings.has_key('upmenu'):
            upmenu = changedSettings['upmenu'].partition('|')[0]
            if  upmenu != self.settings['up']:
                changedSettings['up'] = upmenu
                kType = self.kodiThreads.getThreadAttr(nodeId, 'type')
                threadIn = (upmenu, nodeId) if kType == 'list' else (nodeId, upmenu)
                lstChanged.append(self.kodiThreads.getDotPath(nodeId))
                self.kodiThreads.setNextThread(*threadIn)
                lstChanged.append(self.kodiThreads.getDotPath(nodeId))
        self.settings.update(changedSettings)
#         if self.notifyChangeTo: self.notifyChangeTo(True, lstChanged)



class settingsDisplay(tk.Frame):
    def __init__(self, master = None, xmlFileW = None):
        tk.Frame.__init__(self, master)
        self.setXmlFileW(xmlFileW)
        self.notifyChange = None
        self.topPane = None
        self.scrolled = None
        self.selPaneLabel = ''
        self.setGUI()
        
    def setXmlFileW(self, xmlFileW):
        self.xmlFileW = xmlFileW
        
    def setNotifyChange(self, notifyProcess):
        self.notifyChange = notifyProcess
        
    def setGUI(self):
        topPane = tk.Frame(self, height = 500, width = 500)
        topPane.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        topPane.grid_propagate(0)
        self.topPane = topPane
        bottomPane = tk.Frame(self, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        bottomPane.pack(side = tk.BOTTOM, fill = tk.X)
        for label in ['Apply', 'Discard']:
            boton = tk.Button(bottomPane, name = label.lower() , text = label, command = lambda action = label: self.onAction(action))
            boton.pack(side = tk.RIGHT)
        self.bottomPane = bottomPane
        
    def onAction(self, action, inChangedSettings = None):
        settings = self.xmlFileW.getNonDefaultParams()
        changedSettings = inChangedSettings or self.scrolled.getChangeSettings(settings)
        if action == 'Apply':
            self.xmlFileW.processChangedSettings(changedSettings)
            if self.notifyChange: self.notifyChange(True)
        if action == 'Discard':
            widgets = self.changedWidgets(changedSettings)
            map(lambda w: w.setValue(settings.get(w.id, w.default)), widgets)

    def initFrameExec(self):
        self.changesettings(saveChanges = False)

    def changesettings(self, selPaneIndx = 0, saveChanges = True):
        self.xmlFileW.setActivePaneIndx(selPaneIndx)
        if saveChanges and self.scrolled and not self.xmlFileW.refreshFlag:
            settings = self.xmlFileW.getNonDefaultParams()
            noDefault = self.scrolled.getChangeSettings(settings)
            widgets = self.changedWidgets(dict(noDefault))
            if widgets:
                oldBg = widgets[0].cget('bg')
                map(lambda w: w.config(bg='yellow'), widgets)
                message = 'Some <category> settings has been change, do you want to apply them?'
                message = message.replace('<category>', self.scrolled.category) 
                if tkMessageBox.askokcancel('Change Settings', message):
                    self.onAction('Apply', noDefault)
                map(lambda w: w.config(bg=oldBg), widgets)
        self.xmlFileW.refreshFlag = False
        selPane = self.xmlFileW.getActivePane()
        settings = self.xmlFileW.getNonDefaultParams()        
        if self.selPaneLabel != selPane.get('label'):
            if self.scrolled: self.scrolled.forget()
            self.scrolled = scrolledFrame(self.topPane, settings, selPane)
            self.selPaneLabel = selPane.get('label')
        else:
            self.scrolled.modifySettingsValues(settings)

    def changedWidgets(self, changedSettings):
        reset = changedSettings.pop('reset') + changedSettings.keys()
        filterFlag = lambda widget: (hasattr(widget, 'id') and (widget.id in reset))
        return self.scrolled.widgets(filterFlag)
    
