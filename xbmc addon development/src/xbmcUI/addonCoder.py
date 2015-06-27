'''
Created on 29/10/2014

@author: Alex Montes Barrios
'''

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

ntype = enum('ROOT', 'NOTIMPLEMENTED', 'ONECHILD', 'MENU', 'APIMENU', 'JOIN', 'MULTIPLEXOR','APICATEGORY', 'PAGE', 'SEARCH', 'MEDIA')

class CoderParser:
    def __init__(self):
        pass
        
    def handle(self, ntypeOp, *args):
        nTypeId = ntype.reverse_mapping[ntypeOp]
        return eval('self.handle_' + nTypeId.lower() + '(*args)')
    
    def handle_root(self):
        pass
    
    def handle_notimplemented(self, threadId):
        sourceCode = 'def ' + threadId + '():'
        sourceCode += '\n\treturn [[{}, {"label":"NotImplemented option"}, {}]]'
        return sourceCode
    
    def handle_onechild(self, nodeId, menuId, url, option):
        INDENT = '\n\t'        
        sourceCode = 'def ' + nodeId + '():'
        if url: sourceCode += INDENT + 'args["url"] = [' +  "'" + url + "'" + ']'
        if  option == None:                        
            sourceCode += INDENT + 'return ' + menuId + '()'
        else:
            sourceCode += INDENT + 'nextMenuArgs = ' + menuId + '()'+ '[' + str(option) + '][0]' 
            sourceCode += INDENT + 'nextMenu = nextMenuArgs.pop("menu")' 
            sourceCode += INDENT + 'args.update([(key,[value]) for key, value in nextMenuArgs.items()])'
            sourceCode += INDENT + 'methodToCall = globals()[nextMenu]'
            sourceCode += INDENT + 'return methodToCall()' 
        return sourceCode
    
    def handle_menu(self, nodeId, menuElem, menuIcons):
        INDENT = '\n\t'        
        sourceCode = 'def ' + nodeId + '():'
        sourceCode += '\n\tmenuContent = []'
        for elem in menuElem:
            paramDict, itemParam = elem
            if paramDict.has_key("nxtmenu"):
                nxtMenu = paramDict.pop("nxtmenu")
                sourceCode += INDENT + 'args["url"] = ["' + paramDict.pop("url") + '"]'
                sourceCode += INDENT + 'menuContent.extend(' + nxtMenu + '()' + ')'
            else:
                sourceCode += INDENT + 'menuContent.append([' + str(paramDict) + ', ' + str(itemParam) + ', None])'
        if menuIcons: 
            iconList = '["' + '", "'.join(menuIcons) + '"]'
            sourceCode += INDENT + 'iconList = ' + iconList
            sourceCode += INDENT + 'for k, icon in enumerate(iconList):'
            sourceCode += INDENT + '\t' + 'menuContent[k][1]["iconImage"] = os.path.join(_media, icon)'
        sourceCode += INDENT + 'return menuContent' 
        return sourceCode


    def handle_apimenu(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag):
        import re
        from basicFunc import INFOLABELS_KEYS
        INDENT = '\n\t'        
        sourceCode = 'def ' + nodeId + '():'
        if paramDict.get('url', None):paramDict.pop('url')
        sourceCode += '\n\t'+ 'url = args.get("url")[0]'
        suffix = ')'
        if menuId:
            if spanFlag:
                sourceCode += '\n\t'+ 'limInf, limSup = eval(args.get("span", ["(0,0)"])[0])'
                suffix = ', posIni = limInf, posFin = limSup)'
        spanFlag = False
        addonInfoFlag = paramDict.has_key('regexp') 
        if addonInfoFlag:
            regexp = paramDict.pop('regexp')
            spanFlag = regexp.find('?#<SPAN') != -1 
            regexp = regexp.replace("'", "\\'")    
            sep = "'"
            sourceCode += '\n\t'+ 'regexp = r' + sep + regexp + sep
            sourceCode += '\n\t'+ 'url, data = openUrl(url)'
            if paramDict.get('compflags', None):
                sourceCode += '\n\t'+ 'compflags = ' + paramDict.pop('compflags')
                sourceCode += '\n\t'+ 'subMenus = parseUrlContent(url, data, regexp, compflags' + suffix
            else:
                sourceCode += '\n\t'+ 'subMenus = parseUrlContent(url, data, regexp' + suffix
            addonInfoFlag = any(map(lambda x: x in INFOLABELS_KEYS, re.findall('\?P<([^>]+)>', regexp)))
            
        if spanFlag and regexp.find('?P<') == -1:
            sourceCode += '\n\t'+ "args['span'] = [str(subMenus[0]['span'])]"
            sourceCode += '\n\t'+ "return " +  str(paramDict['menu']) + "()"
            return sourceCode

        if menuIcons:
            iconList = '["' + '", "'.join(menuIcons) + '"]'
            sourceCode += '\n\t' + 'iconList = ' + iconList
            sourceCode += '\n\t' + 'kMax = min(len(subMenus), len(iconList))'
            sourceCode += '\n\t' + 'for k in range(kMax):'
            sourceCode += '\n\t\t' + 'subMenus[k]["iconImage"] = os.path.join(_media, iconList[k])'
        
        contextMenuFlag = paramDict.has_key('contextmenus')
        if contextMenuFlag:
            contextMenu = [tuple(elem.split(',')) for elem in paramDict.pop('contextmenus').split('|')]
            onlyContext = paramDict.pop('onlycontext') if paramDict.has_key('onlycontext') else False
            sourceCode += '\n\t'+ 'contextMenu = {"lista":' + str(contextMenu) + ', "replaceItems":' + str(onlyContext) + '}' 
            
        sourceCode += '\n\t'+ 'menuContent = []'
        sourceCode += '\n\t'+ 'for elem in subMenus:'
        sourceCode += '\n\t\t'+ 'itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])'
        isFolder = str(paramDict['menu'] != 'media') if paramDict.has_key('menu') else 'True'
        sourceCode += '\n\t\t'+ 'itemParam["isFolder"] = ' + isFolder
        sourceCode += '\n\t\t'+ 'otherParam = {}'
#         sourceCode += '\n\t\t'+ 'otherParam = None'
        if contextMenuFlag:
            sourceCode += '\n\t\t'+ 'otherParam["contextMenu"] = dict(contextMenu)'
        if addonInfoFlag:
            sourceCode += '\n\t\t'+ 'otherParam["addonInfo"] = dict([(key,elem.pop(key)) for key  in elem.keys() if key in INFOLABELS_KEYS])'
        sourceCode += '\n\t\t'+ 'paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])'            
        sourceCode += '\n\t\t'+ 'paramDict.update(' + str({ key:value for key, value in paramDict.items() if key not in ['header','headregexp','nextregexp', 'iconflag', 'iconimage']}) + ')'
#         sourceCode += '\n\t\t'+ 'paramDict = ' + str({ key:value for key, value in paramDict.items() if key not in ['nextregexp', 'iconflag', 'iconimage']})
        sourceCode += '\n\t\t'+ 'paramDict.update(elem)'
        if spanFlag: sourceCode += '\n\t\t'+ 'paramDict["url"] = url'
        sourceCode += '\n\t\t'+ 'menuContent.append([paramDict, itemParam, otherParam])'
        sourceCode += '\n\t'+ 'return menuContent'
        if searchFlag: sourceCode += ' or EMPTYCONTENT' 
        return sourceCode

    def handle_page(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag):
        sourceCode = self.handle_apimenu(nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag)

        headFlag = paramDict.has_key('headregexp')
        footFlag = paramDict.has_key('nextregexp')
        frstline, sourceCode, lstline = sourceCode.partition('\n\t'+ 'url = args.get("url")[0]')
        if headFlag:
            headregexp = paramDict.pop('headregexp')
            headmenu = [elem.split("<->") for elem in headregexp.split("<=>")]
            if len(headmenu) == 1 and len(headmenu[0]) == 1:
                sourceCode += '\n\t'+ 'headmenu = [[\'Header >>>\', \'' + headregexp + '\']]'
            else:
                sourceCode += '\n\t'+ 'headmenu = ' + str(headmenu)
        if footFlag:
            nextregexp = paramDict.pop('nextregexp')
            footmenu = [elem.split("<->") for elem in nextregexp.split("<=>")]
            if len(footmenu) == 1 and len(footmenu[0]) == 1:
                sourceCode += '\n\t'+ 'footmenu = [[\'Next Page >>>\', \'' + nextregexp + '\']]'
            else:
                sourceCode += '\n\t'+ 'footmenu = ' + str(footmenu)
        if headFlag and not footFlag:
            sourceCode += '\n\t'+ 'if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, headmenu)'        
        if not headFlag and footFlag:
            sourceCode += '\n\t'+ 'if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)'        
        if headFlag and footFlag:
            sourceCode += '\n\t'+ 'if args.has_key("section"):'
            sourceCode += '\n\t\t'+ 'fhmenu = headmenu if args["section"][0] == "header" else footmenu'
            sourceCode += '\n\t\t'+ 'url = processHeaderFooter(args.pop("section")[0], args, fhmenu)'

        sourceCode = frstline + sourceCode + lstline
        sourceCode, lsep, lstLine = sourceCode.rpartition('\n\t')

        if headFlag:
            sourceCode += '\n\t'+ 'menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent'
            
        if footFlag:            
            sourceCode += '\n\t'+ 'menuContent += getMenuHeaderFooter("footer", args, data, footmenu)'
            
        sourceCode += lsep + lstLine

        return sourceCode

    def handle_media(self, keySet, regexp, compflags):
        INDENT = '\n\t'
        mediacode  = 'def media():'
        mediacode += INDENT + 'import urlresolver'
        if 'url' in keySet:
            if len(keySet) > 1:
                mediacode += INDENT + 'if args.get("url", None):'
                INDENT += '\t'
            mediacode += INDENT + 'url = args.get("url")[0]'
            regexp = regexp.replace("'", "\\'")    
            sep = "'"
            mediacode += INDENT + 'regexp = ' + sep + regexp + sep
            mediacode += INDENT + 'url, data = openUrl(url)'
            mediacode += INDENT + 'compflags ='  + compflags
            mediacode += INDENT + 'subMenus = parseUrlContent(url, data, regexp, compflags )'
            if '(?P<videourl>' in regexp:
                mediacode += INDENT + 'videoUrl = subMenus[0]["videourl"]'
                mediacode += INDENT + 'url = urlresolver.HostedMediaFile(url = videoUrl).resolve()'
            elif '(?P<videoUrl>' in regexp:
                mediacode += INDENT + 'url = subMenus[0]["videoUrl"]'
        if 'videoUrl' in keySet:
            INDENT = '\n\t'
            if len(keySet) > 1:
                mediacode += INDENT + 'if args.get("videoUrl", None):'
                INDENT += '\t'
            mediacode += INDENT + 'videoUrl = args.get("videoUrl")[0]'
            mediacode += INDENT + 'url = urlresolver.HostedMediaFile(url=videoUrl).resolve()'
        if 'videoId' in keySet:
            INDENT = '\n\t'
            if len(keySet) > 1:
                mediacode += INDENT + 'if args.get("videoId", None):'
                INDENT += '\t'
            mediacode += INDENT + 'videoId = args.get("videoId")[0]'
            mediacode += INDENT + "videoHost = args.get('videoHost')[0]"
            mediacode += INDENT + 'url = urlresolver.HostedMediaFile(host=videoHost,media_id=videoId).resolve()'
            
        INDENT = '\n\t'
        
        mediacode += INDENT + 'li = xbmcgui.ListItem(path = url)'
        mediacode += INDENT + 'if args.get("icondef", None): li.setThumbnailImage(args["icondef"][0])'
        mediacode += INDENT + 'if args.get("labeldef", None): li.setLabel(args["labeldef"][0])'
        mediacode += INDENT + "li.setProperty('IsPlayable', 'true')"
        mediacode += INDENT + "li.setProperty('mimetype', 'video/x-msvideo')"
        mediacode += INDENT + "return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)"
        return mediacode    

    def handle_search(self, nodeId, menuId, addon_id, regexp, searchKeys):
        sourceCode = """
def <nodeId>():
    if args.has_key('searchkeys'):
        searchKeys = args.get('searchkeys')[0]
        searchKeys = searchKeys.split('+')
        menuContent = []
        for elem in searchKeys:
            searchLabel, searchId = map(lambda x: x.strip(), elem.split('*'))
            menuContent.append([{'searchid':searchId, 'menu': '<nodeId>'}, {'isFolder': True, 'label': '<nodeId> by ' + searchLabel}, None])            
        return menuContent
    import xml.etree.ElementTree as ET
    searchId     = args.get('searchid', ['all'])[0]
    savedsearch = xbmc.translatePath('special://profile')
    savedsearch = os.path.join(savedsearch, 'addon_data', '<addon_id>','savedsearch.xml')
    root = ET.parse(savedsearch).getroot() if os.path.exists(savedsearch) else ET.Element('searches')
        
    if not args.has_key("tosearch") and os.path.exists(savedsearch):
        existsSrch = root.findall("search")
        if searchId != "all":
            existsSrch = [elem for elem in existsSrch if elem.get("searchid") == searchId] 
        menuContent = [] 
        for elem in existsSrch:
           menuContent.append([{'menu':elem.get('menu'), 'url':elem.get('url')}, {'isFolder': True, 'label': elem.get('tosearch')}, None])
        if menuContent:
            menuContent.insert(0,[{'menu':'<nodeId>', 'tosearch':'==>', 'searchid':searchId}, {'isFolder': True, 'label': 'Search by ' + searchId}, None])
            return menuContent

    kb = xbmc.Keyboard("", "Search for " + searchId , False)
    kb.doModal()
    if not (kb.isConfirmed()):return EMPTYCONTENT
    srchLabel = kb.getText()
    toSearch = (searchId + "=" if searchId != 'all' else "") + urllib.quote_plus(srchLabel) 
    srchUrl = "<regexp>".replace("<search>", toSearch)
    existsSrch = [elem for elem in root.findall("search") if elem.get("url") == srchUrl]
    args["url"] = [srchUrl]    
    menuContent = <menuId>()
    if menuContent and not existsSrch:
        toInclude = ET.Element('search', url = srchUrl, tosearch = srchLabel, menu = "<menuId>", searchid = searchId)
        root.insert(0, toInclude)
        if not os.path.exists(os.path.dirname(savedsearch)):os.mkdir(os.path.dirname(savedsearch)) 
        ET.ElementTree(root).write(savedsearch)
    return menuContent
        """
        sourceCode = sourceCode.replace('<nodeId>',nodeId)
        sourceCode = sourceCode.replace('<addon_id>', addon_id)
        sourceCode = sourceCode.replace('<message>', nodeId.replace("_", ' '))
        sourceCode = sourceCode.replace('<regexp>', regexp)
        sourceCode = sourceCode.replace('<menuId>', menuId)
        return sourceCode.strip("\n ")

    def handle_apicategory(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict):
        discrim = paramDict.pop('discrim')
        menuDef = paramDict.pop("menu")        
        genFunc = self.handle_page if paramDict.has_key('nextregexp') else self.handle_apimenu 
        sourceCode = genFunc(nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag)
        urloutFlag = discrim.startswith('urlout')
        urlinFlag =  discrim.startswith('urlin')
        optlabelFlag = discrim.startswith('optlabel')
        optionFlag = discrim.startswith('option') or discrim.startswith('optnumber')

        oldCode = '\n\t'+ 'menuContent = []'
        newCode = '\n\t' + 'optionMenu = ' + str(discrimDict)
        if urlinFlag: newCode += '\n\t' + 'menu = getMenu(url, ' + '"' + menuDef + '"' + ', optionMenu)'
        else: newCode += '\n\t' + 'menuDef = ' + '"' + menuDef + '"'
        sourceCode = sourceCode.replace(oldCode, newCode + oldCode)
        
        oldCode = '\n\t'+ 'for elem in subMenus:'
        if optionFlag:
            newCode = '\n\t'+ 'for k, elem in enumerate(subMenus):'
            sourceCode = sourceCode.replace(oldCode, newCode)

        oldCode = '\n\t\t'+ 'itemParam["isFolder"] = True'
        newCode = ''
        if optionFlag: newCode = '\n\t\t'+ 'menu = optionMenu.get(str(k), menuDef)'
        if optlabelFlag: newCode = '\n\t\t'+ 'menu = optionMenu.get(itemParam["label"], menuDef)'
        if urloutFlag: newCode = '\n\t\t' + 'menu = getMenu(elem["url"], menuDef, optionMenu)'        
        if newCode:
            newCode += '\n\t\t'+ 'itemParam["isFolder"] = menu != "media"'
            sourceCode = sourceCode.replace(oldCode, newCode)
        
        oldCode = '\n\t\t'+ 'paramDict.update(elem)'
        newCode = ''
        if urlinFlag or urloutFlag or optionFlag or optlabelFlag: newCode = '\n\t\t' + 'paramDict["menu"] = menu'
        sourceCode = sourceCode.replace(oldCode, oldCode + newCode)
       
        return sourceCode

    def handle_multiplexor(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict):
        paramDict.pop('discrim')
        optionMenu = str(discrimDict)
        menuDef = paramDict.pop("menu")
        sep = "'"
        regexp = 'r' + sep + paramDict.pop('regexp').replace("'", "\\'") + sep    
        compflags = paramDict.get('compflags', '0')
        
        repDict = {'<nodeId>':nodeId, '<optionMenu>':optionMenu,'<menuDef>':menuDef,'<regexp>':regexp, '<compflags>':compflags, }
        
        sourceCode ="""
def <nodeId>():
    optionMenu = <optionMenu>
    menuDef = "<menuDef>"
    url = args.get("url")[0]
    regexp = <regexp>
    compflags = <compflags>
    urldata = openUrl(url, validate = False)[1]
    match = re.search(regexp, urldata, compflags)
    nxtmenu = getMenu(match.group(1), menuDef, optionMenu) if match else menuDef         
    return globals()[nxtmenu]()
        """
        for key, value in repDict.items():
            sourceCode = sourceCode.replace(key, value)
        return sourceCode.strip("\n ")

    def handle_join(self, nodeId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict):
        paramDict.pop('discrim')
        optionMenu = discrimDict.items()
        menuDef = paramDict.pop("menu")
        optionMenu.insert(0, ('-1', menuDef))
        sep = "'"
        regexp = 'r' + sep + paramDict.pop('regexp').replace("'", "\\'") + sep    
        compflags = paramDict.get('compflags', '0')
        repDict = {'<nodeId>':nodeId, '<optionMenu>':optionMenu,'<menuDef>':menuDef,'<regexp>':regexp, '<compflags>':compflags, }
        
        sourceCode ="""
def <nodeId>():
    menuContent = []
    <joincontent> 
    return menuContent
        """
        sourceCode = sourceCode.replace('<nodeId>', nodeId)
        optionMenu = sorted([(value,key) for value, key in optionMenu])
        for key, value in optionMenu:
            sourceCode = sourceCode.replace('<joincontent>', 'menuContent.extend(' + value + '())\n    <joincontent>')
        sourceCode = sourceCode.replace('\n    <joincontent>', '')
        return sourceCode.strip("\n ")


class Addoncoder:
    
    HEADER = '\nimport os, sys\nimport xbmcaddon\nimport xbmc\nimport xbmcplugin\nimport xbmcgui\nimport urlparse\nimport urllib\nimport re\n\n_settings = xbmcaddon.Addon()\n_path = xbmc.translatePath(_settings.getAddonInfo(\'path\')).decode(\'utf-8\')\n_lib = xbmc.translatePath(os.path.join(_path, \'resources\', \'lib\'))\n_media = xbmc.translatePath(os.path.join(_path, \'resources\', \'media\'))\nsys.path.append(_lib)\n\nEMPTYCONTENT = [[{}, {"isFolder": True, "label": ""}, None]]\n\nfrom basicFunc import openUrl, parseUrlContent, makeXbmcMenu, getMenu, getMenuHeaderFooter, processHeaderFooter, LISTITEM_KEYS, INFOLABELS_KEYS\n'
    FOOTER = '\nbase_url = sys.argv[0]\naddon_handle = int(sys.argv[1])\nargs = urlparse.parse_qs(sys.argv[2][1:])\nxbmcplugin.setContent(addon_handle, \'movies\')\n\nmenu = args.get(\'menu\', None)\n\nmenuFunc = menu[0] if menu else \'rootmenu\'\nmenuItems = eval(menuFunc + \'()\')\nif menuItems: makeXbmcMenu(addon_handle, base_url, menuItems)    \n'
    ERRORS = ''
    
    def __init__(self, addonADG, addonSettings):
        self.parser = CoderParser()
        self.addonADG = addonADG
        self.addonSettings = addonSettings
        self.modSourceCode = {}
        
    def addon_id(self):
        return self.addonSettings.getParam('addon_id')
        

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
            if nodeType == 'link':
                nodeId = self.addonADG.getThreadAttr(elem, 'name')
                nodeType = self.addonADG.getThreadAttr(nodeId, 'type')
            else:
                nodeId = elem
            if nodeType != "list": 
                params = self.addonADG.getThreadAttr(nodeId, 'params')
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
        node = self.addonADG.parseThreads[threadId]
        paramDict = dict(node['params'])
        paramDict['menu'] = node['up']
        regexp = paramDict.get('regexp', None)  # ** En proceso SEARCH
        if regexp and regexp.startswith('(?#<SEARCH>)'):
            regexp = regexp[len('(?#<SEARCH>)'):]
            menuId = node['up']
            searchKeys = paramDict.get('searchkeys', None)
            return self.parser.handle(ntype.SEARCH, threadId, menuId, self.addon_id(), regexp, searchKeys)
        
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
        
        discrim = self.addonADG.getThreadParam(threadId, 'discrim')    
        if discrim:
            disc = self.addonADG.getThreadParam(threadId, discrim)
            listaDisc = [(disc, threadId)] if disc else []
            listaMenu = [self.addonADG.getThreadAttr(elem, 'name') for elem in self.addonADG.getChildren(threadId) if self.addonADG.getThreadAttr(elem, 'type') == 'link']
            for elem in listaMenu:
                params = self.addonADG.parseThreads[elem]['params']
                listaDisc.extend([(disc, elem) for key, disc in params.items() if key.startswith(discrim)])
            discrimDict = dict(listaDisc)
            if not discrimDict:
                self.ERRORS += 'WARNING: ' + threadId + ' not define alternative menus'  + '\n'
            if discrim.startswith('urljoin'):
                return self.parser.handle(ntype.JOIN, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict)
            elif discrim.startswith('urldata'):
                return self.parser.handle(ntype.MULTIPLEXOR, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict)
            return self.parser.handle(ntype.APICATEGORY, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag, discrimDict)            
        if paramDict.has_key('nextregexp') or paramDict.has_key('headregexp'): return self.parser.handle(ntype.PAGE, threadId, menuId, paramDict, menuIcons, searchFlag, spanFlag)
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
    
        
    def saveCode(self, content, isPartialMod = False):
        import re
        if not isPartialMod:
#             for key in self.modSourceCode.keys():
#                 if self.addonADG.existsThread(key):
#                     params = self.addonADG.parseThreads[key]['params']
#                     if params.has_key('enabled'): params.pop('enabled')
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
            else:
                if params.has_key('enabled'): params.pop('enabled')
            pos = match.start(0)
            content = content[:pos] + placeHolder + content[match.end(0)-1:]
            pos += len(placeHolder) 
        if (not isPartialMod) and content.strip('\t\n\x0b\x0c\r '):
            self.modSourceCode['_codeframe_'] = content.strip('\t\n\x0b\x0c\r ') + '\n'
        
    
    

