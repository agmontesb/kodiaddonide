'''
Created on 30/12/2014

@author: Alex Montes Barrios
'''
import sys
import re
import xml.etree.ElementTree as ET
from xbmcUI.addonCoder import CoderParser, ntype

class FileGenerator:
    def __init__(self, addonSettings, addonThreads, addonCoder):
        self._fileGenerators = {}
        fileObjets = sys.modules[__name__].__dict__
        fileClass = [fileGen for fileGen in fileObjets.keys() if fileGen.startswith('addonFile_')]
        for fileGen in fileClass:
            fileObj = fileObjets[fileGen](addonSettings, addonThreads, addonCoder)
            self.addFile(fileObj)
    
    def listFiles(self):
        return [ value.getFileMetaData() for value in self._fileGenerators.values()]
    
    def addFile(self, fileObject):
        fileId = fileObject.getFileMetaData()[0]
        self._fileGenerators[fileId] = fileObject

    def getSource(self, fileId):
        fileGen = self._fileGenerators[fileId]        
        return fileGen.getSource()
    
    def setSource(self, fileId, modSource, isPartialMod = False):
        fileGen = self._fileGenerators[fileId]
        fileGen.setSource(modSource, isPartialMod)
        
    def getFileName(self, fileId):
        return self._fileGenerators[fileId].getFileMetaData()[1]


class addonFile_apimodule:
    def __init__(self, addonSettings, addonThreads, addonCoder):
        self.addonSettings = addonSettings
        self.addonThreads = addonThreads
        self.addonCoder = addonCoder
        self._fileId = 'addon_module'
        self._location = ""
        self._isEditable = True
        
    def getFileMetaData(self):
        fileName = self.addonSettings.getParam('addon_module')
        return (self._fileId, fileName, self._location, self._isEditable)
    
    def getSource(self):
        return self.addonCoder.addonScripSource()
    
    def setSource(self, content, isPartialMod = False):
        self.addonCoder.saveCode(content, isPartialMod)
        


class InitModule:
    HEADER = '\nimport os, sys\nimport xbmcaddon\nimport xbmc\nimport xbmcplugin\nimport xbmcgui\nimport urlparse\nimport urllib\nimport re\n\n_settings = xbmcaddon.Addon()\n_path = xbmc.translatePath(_settings.getAddonInfo(\'path\')).decode(\'utf-8\')\n_lib = xbmc.translatePath(os.path.join(_path, \'resources\', \'lib\'))\n_media = xbmc.translatePath(os.path.join(_path, \'resources\', \'media\'))\nsys.path.append(_lib)\n\nEMPTYCONTENT = [[{}, {"isFolder": True, "label": ""}, None]]\n\nfrom basicFunc import openUrl, parseUrlContent, makeXbmcMenu, getMenu, LISTITEM_KEYS, INFOLABELS_KEYS\n'
    FOOTER = '\nbase_url = sys.argv[0]\naddon_handle = int(sys.argv[1])\nargs = urlparse.parse_qs(sys.argv[2][1:])\nxbmcplugin.setContent(addon_handle, \'movies\')\n\nmenu = args.get(\'menu\', None)\n\nmenuFunc = menu[0] if menu else \'rootmenu\'\nmenuItems = eval(menuFunc + \'()\')\nif menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)    \n'
    ERRORS = ''
    
    def __init__(self, addon_id, fileName, addonADG, modSourceCode = None):
        self._fileId = addon_id
        self._fileName = fileName
        self._location = ""
        self._isEditable = True
        self.parser = CoderParser()
        self.addonADG = addonADG
        self.addon_id = addon_id
        self.modSourceCode = modSourceCode or {}
        
    def getFileMetaData(self):
        return (self._fileId, self._fileName, self._location, self._isEditable)
    
    def getSource(self):
        return self.addonScripSource()
    
    def setSource(self, content, isPartialMod = False):
        self.saveCode(content, isPartialMod)
    

    def __getattr__(self, name):
        return getattr(self.addonADG, name)
        
    def getActiveNode(self):
        return self.addonADG.threadDef
    
    def addonScripSource(self):
        self.ERRORS = ''
        if self.modSourceCode.has_key('_codeframe_'): 
            codeStr = self.modSourceCode['_codeframe_']
            codeStr = codeStr.replace('<header>', self.HEADER)
            codeStr = codeStr.replace('<footer>', self.FOOTER)
            pos = 0
            for nodeId, isReverse in [('rootmenu', False), ('media', True)]:
                fncList = self.addonADG.getSameTypeNodes(nodeId)
                if isReverse: fncList = list(reversed(fncList))
                for node in fncList:
                    if node.endswith('_lnk'): continue
                    placeHolder = '<' + node + '>'
                    nodeCode = self.knothCode(node)
                    posIni = codeStr.find(placeHolder)
                    if posIni != -1:
                        codeStr = codeStr.replace(placeHolder, nodeCode)
                        pos = posIni + len(nodeCode + '\n')
                    else:
                        codeStr = codeStr[:pos]+ '\n' + nodeCode + '\n' + codeStr[pos:]
                        pos += len('\n' + nodeCode + '\n') 
        else:
            codeStr  = self.HEADER
            codeStr += self.scriptSource('rootmenu')
            codeStr += self.scriptSource('media', reverse = True)
            codeStr += self.FOOTER
        self.ERRORS = self.ERRORS or 'no ERRORS, no WARNINGS'
        return codeStr
    
    def scriptSource(self, threadId, reverse = False):
        fncList = self.addonADG.getSameTypeNodes(threadId)
        if reverse: fncList = list(reversed(fncList))
        sourceCode = ''
        for node in fncList:
            if self.addonADG.getThreadAttr(node, 'type') == 'link': continue
            sourceCode += '\n' + self.knothCode(node) + '\n'
        return sourceCode
    
    def knothCode(self, node):
        if self.modSourceCode.has_key(node): 
            return self.modSourceCode[node].replace(node + '():', node + '():' + '      # Modified code') 
        sourceCode = ''
        threadType = self.addonADG.getThreadAttr(node, 'type')
        if threadType != -1:
            if threadType == 'list':
                sourceCode = self.listSource(node)
            elif threadType == 'thread':
                sourceCode = self.threadSource(node)
            else:
                pass
        return sourceCode.expandtabs(4)
        
            
    def listSource(self, threadId):
        children = self.addonADG.getChildren(threadId)
        if threadId != 'rootmenu' and not children:
            self.ERRORS += 'WARNING: ' + threadId + ' not implemented' + '\n'                
            return self.parser.handle(ntype.NOTIMPLEMENTED, threadId)
        
        if threadId == 'rootmenu':
            testFunc = lambda x: self.addonADG.getThreadParam(x, 'source')
            fncList = [elem for elem in self.addonADG.getSameTypeNodes('media')  if not elem.endswith("_lnk")]
            for node in fncList:
                dwnNode = self.addonADG.getThreadAttr(node, 'down')
                if not dwnNode or  all(map(testFunc, self.addonADG.getChildren(node))):
                    children.append(node)
        if len(children) == 1 and (threadId == 'rootmenu' or self.addonADG.getThreadAttr(children[0], 'type') == 'link'):
            nodeId = children[0] if self.addonADG.getThreadAttr(children[0], 'type') != 'link' else self.addonADG.getThreadAttr(children[0], 'name') 
            url = self.addonADG.getThreadParam(nodeId, 'url')
            option = self.addonADG.getThreadParam(threadId,'option')
            return self.parser.handle(ntype.ONECHILD, threadId, nodeId, url, option)
            
        menuElem=[]
        for elem in children:
            paramDict = {}
            nodeType = self.addonADG.getThreadAttr(elem, 'type')
            nodeId = elem if nodeType != "link" else self.addonADG.getThreadAttr(elem, 'name')
            if nodeType != "list": 
                params = self.addonADG.getThreadAttr(elem, 'params')
                paramDict.update({key:value for key, value in params.items() if key in ['url', 'searchkeys']})
                if paramDict.has_key('searchkeys'): paramDict.pop('url')
                if params.get("plainnode"):
                    paramDict["nxtmenu"] = nodeId 
            paramDict['menu'] = nodeId
            node = self.addonADG.parseThreads[nodeId]
            itemParam = {'isFolder':True}
            itemParam['label'] = node['name']
            menuElem.append((paramDict, itemParam))
        menuIcons = None
        if self.addonADG.getThreadParam(threadId, 'iconflag'):
            params = self.addonADG.getThreadAttr(threadId, 'params')
            iconList = [icon.strip() for icon in params['iconimage'].split(',')]
            kMax = min(len(menuElem), len(iconList))
            if kMax != len(menuElem): self.ERRORS += '\n' + 'WARNING: in ' + threadId + ' not enough icons were provided'
            menuIcons = iconList[:kMax]
        return self.parser.handle(ntype.MENU, threadId, menuElem, menuIcons)
    
    def getMediaCode(self):
        keyValues = set(['url', 'videoUrl', 'videoId'])
        def getRegexKey(regexp, keySet):
            posFin = 0
            while True:
                posIni = regexp.find('(?P<', posFin)
                if posIni == -1: break
                posIni += len('(?P<')
                posFin = regexp.find('>', posIni)
                if posFin == -1: break
                keySet.add(regexp[posIni:posFin])
            return keySet.intersection(keyValues)
                
        lista = [(elem, self.addonADG.getThreadParam(elem, 'regexp')) for elem in self.addonADG.getChildren('media') if self.addonADG.getThreadAttr(elem, 'type') == 'thread']
        keySet = set()
        for elem in lista:
            keyElem = getRegexKey(elem[1], set())
            if keyElem:
                keySet.update(keyElem)
            else:
                self.ERRORS += 'ERROR: ' + elem[0] + ' not send any of ' + str(keyValues) + ' to media'  + '\n'
            
        regexp = self.addonADG.getThreadParam('media', 'regexp')
        compflags = self.addonADG.getThreadParam('media', 'compflags')
        return self.parser.handle(ntype.MEDIA, keySet, regexp, compflags)


    def threadSource(self, threadId):
        if threadId == 'media': return self.getMediaCode() 
#         nodeId = self.addonADG.getThreadAttr(threadId, 'up')
        node = self.addonADG.parseThreads[threadId]
        paramDict = dict(node['params'])
        paramDict['menu'] = node['up']
        regexp = paramDict.get('regexp', None)  # ** En proceso SEARCH
        if regexp and regexp.startswith('(?#<SEARCH>)'):
            regexp = regexp[len('(?#<SEARCH>)'):]
            menuId = node['up']
            searchKeys = paramDict.get('searchkeys', None)
            return self.parser.handle(ntype.SEARCH, threadId, menuId, self.addon_id, regexp, searchKeys)
        
        searchFlag = False
        spanFlag = False
        menuId = self.addonADG.getThreadAttr(threadId, 'down')
        if menuId:
            lista = [self.addonADG.getThreadParam(elem, 'regexp') for elem in self.addonADG.getChildren(threadId) if self.addonADG.getThreadAttr(elem, 'type') == 'thread']
            spanFlag = any(map(lambda x: x.find('?#<SPAN') != -1, lista))
            searchFlag = any(map(lambda x: x.find('?#<SEARCH>') != -1, lista))

        menuIcons = None
        if not self.addonADG.getThreadParam(threadId, 'nextregexp') and self.addonADG.getThreadParam(threadId, 'iconflag'):
            menuIcons = [icon.strip() for icon in self.addonADG.getThreadParam(threadId, 'iconimage').split(',')]
            
        if self.addonADG.getThreadParam(threadId, 'discrim'):
            discrim = self.addonADG.getThreadParam(threadId, 'discrim')
            listaMenu = [self.addonADG.getThreadAttr(elem, 'name') for elem in self.addonADG.getChildren(threadId) if self.addonADG.getThreadAttr(elem, 'type') == 'link']
            listaDisc = []
            for elem in listaMenu:
                params = self.addonADG.parseThreads[elem]['params']
                listaDisc.extend([(disc, elem) for key, disc in params.items() if key.startswith(discrim)])
            discrimDict = dict(listaDisc)
            if not discrimDict:
                self.ERRORS += 'WARNING: ' + threadId + ' not define alternative menus'  + '\n'
            if self.addonADG.getThreadParam(threadId, 'discrim').startswith('urldata'):
                return self.parser.handle(ntype.MULTIPLEXOR, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict)
            return self.parser.handle(ntype.APICATEGORY, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict)            
        if paramDict.has_key('nextregexp'): return self.parser.handle(ntype.PAGE, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag)
        return self.parser.handle(ntype.APIMENU, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag)
    
    def modifyCode(self, modType, *args):
        if modType == 'delete':
            for node in args:
                if self.modSourceCode.has_key(node): self.modSourceCode.pop(node)
                if self.modSourceCode.has_key('_codeframe_'):
                    codeStr = self.modSourceCode['_codeframe_']
                    self.modSourceCode['_codeframe_'] = codeStr.replace('<' + node + '>', '# Deleted node ' + node)
        elif modType == 'rename':
            oldName, newName = args[0:2]
            if self.modSourceCode.has_key(oldName): self.modSourceCode[newName] = self.modSourceCode.pop(oldName)
            if self.modSourceCode.has_key('_codeframe_'):
                codeStr = self.modSourceCode['_codeframe_']
                self.modSourceCode['_codeframe_'] = codeStr.replace('<' + oldName + '>', '<' + newName + '>')
    
        
    def saveCode(self, content):
        import re
        for key in self.modSourceCode.keys():
            if self.addonADG.existsThread(key):
                params = self.addonADG.parseThreads[key]['params']
                if params.has_key('enabled'): params.pop('enabled')
        self.modSourceCode = {}
        if content.startswith(self.HEADER): content = '<header>' + content[len(self.HEADER):] 
        if content.endswith(self.FOOTER): content = content[: -len(self.FOOTER)] + '<footer>'        
        pos = 0
        reg = re.compile('def (?P<name>[^\(]+?)\([^\)]*?\):(?:.+?)\n {4}return (?P<return>.+?)\n', re.DOTALL)
        while 1:
            match = reg.search(content, pos)
            if not match: break
            knotId = match.group(1)
            genCode = self.knothCode(knotId)
            pos = match.end(0)
            if not genCode: continue
            placeHolder = '<' + knotId + '>'
            params = self.addonADG.parseThreads[knotId]['params'] 
            if genCode != match.group(0)[:-1]:
                nodeCode = match.group(0).replace('      # Modified code', '')
                self.modSourceCode[knotId] = nodeCode
                params['enabled'] = False
            pos = match.start(0)
            content = content[:pos] + placeHolder + content[match.end(0)-1:]
            pos += len(placeHolder) 
        if content.strip('\t\n\x0b\x0c\r '):
            self.modSourceCode['_codeframe_'] = content.strip('\t\n\x0b\x0c\r ') + '\n'
    
    
    
    
    
    
class addonFile_addonXmlFile:
    def __init__(self, addonSettings, addonThreads, addonCoder):
        self._fileId = 'addon_xml'
        self._fileName = 'addon.xml'
        self._location = ""
        self._isEditable = False
        self.settings = addonSettings
        
    def getFileMetaData(self):
        return (self._fileId, self._fileName, self._location, self._isEditable)
    
    def getSource(self):
        allSettings = self.settings.getParam()
        return self.getAddonXmlFile(r'C:\eclipse\Workspace\xbmc addon development\src\xbmcUI\addonXmlTemplate.xml', allSettings)
    
    def getAddonXmlFile(self, xmlTemplate, settings):
        with open(xmlTemplate, 'r') as f:
            xmlTemplate = f.read()
        regexPatterns = ['"(.+?)"', '>([^<\W]+)<']       # [attribute, value]
        for regexPattern in regexPatterns:
            pos = 0
            reg = re.compile(regexPattern)
            while True:
                match = reg.search(xmlTemplate, pos)
                if not match: break
                key = match.group(1)                  #reemplazar verdadero codigo
                if settings.has_key(key):
                    posINI = match.start(0) + 1
                    posFIN = match.end(0) - 1
                    value = settings[key]
                    xmlTemplate = xmlTemplate[:posINI] + value + xmlTemplate[posFIN:]
                    pos = posINI + len(value) + 1
                else:
                    pos = match.end(0)
                    
        # Sesion requires
        regexPattern = "<requires>(.+?)\s*</requires>"
        pos = 0
        reg = re.compile(regexPattern, re.DOTALL)
        match = reg.search(xmlTemplate, pos)
        posINI = match.start(1)
        posFIN = match.end(1)
        template = match.group(1)
        lista = [elem.split(',') for elem in settings['addon_requires'].split('|')]
    
        for k, elem in enumerate(lista):
            if len(elem) < 3 or elem[2] == '': lista[k] = elem[:2] + ['false']
            lista[k] = template.format(*lista[k]).replace('optional="false"','')
        template = ''.join(lista)
        xmlTemplate = xmlTemplate[:posINI] + template + xmlTemplate[posFIN:]
        
        # Sesion provides
        attIds = ['addon_video', 'addon_music', 'addon_picture', 'addon_program']
        attlabel = ['video', 'music', 'picture', 'program']
        template = ''
        for k, attId in enumerate(attIds):
            if settings.get(attId) == 'true':
                template += attlabel[k] + ' '
        regexPattern = "<provides>(.+?)</provides>"
        pos = 0
        reg = re.compile(regexPattern, re.DOTALL)
        match = reg.search(xmlTemplate, pos)
        posINI = match.start(1)
        posFIN = match.end(1)
        xmlTemplate = xmlTemplate[:posINI] + template.strip() + xmlTemplate[posFIN:]
        return xmlTemplate
    
    def setSource(self):
        pass
    
    
