import sys
import os
import xbmc
import xml.etree.ElementTree as ET
import  xml.dom.minidom as minidom
import re

class Addon(object):
    def __new__(cls, *args, **kwargs):
        if args:
            addonId = args[0]
        else:
            posIni = len('plugin://')
            posFin = sys.argv[0].find('/', posIni)
            addonId = sys.argv[0][posIni:posFin]
            addonId = kwargs.get('id',addonId)
        pathDir = xbmc.translatePath('special://home/addons/' + addonId)
        addonXmlFile = os.path.join(pathDir, 'addon.xml')
        if  not os.path.exists(addonXmlFile): return False
        inst = object.__new__(cls, *args, **kwargs)
        return inst
    
    def __init__(self, *args, **kwargs):
        """
        --Creates a newAddon class.
        addonId : [opt] string - id of the addon as specified in addon.xml
        *Note, specifying the addon id is not needed.
        Important however is that the addon folder has the same name as the addon id provided in addon.xml.
        You can optionally specify the addon id from another installed addon to retrieve settings from it.
        example:
            - self.Addon = xbmcaddon.Addon()
            - self.Addon =xbmcaddon.Addon ('script.foo.bar')
        """
        if args:
            self.addonId = args[0]
        else:
            posIni = len('plugin://')
            posFin = sys.argv[0].find('/', posIni)
            addonId = sys.argv[0][posIni:posFin]
            self.addonId = kwargs.get('id',None) or addonId
    
    def getAddonInfo(self, infoId):
        """
         --Returns the value of an addon property as a string.
        infoId : string - id of the property that the module needs to access.
        *Note, choices are (author, changelog, description, disclaimer, fanart. icon, id, name, path profile, stars, summary, type, version)
        example:
            - version = self.Addon.getAddonInfo('version')
        """
        infoId = infoId.lower()
        pathDir = xbmc.translatePath('special://home/addons/' + self.addonId)
        if not os.path.exists(pathDir):
            xbmc.log('The path ' + pathDir + 'for addon ' + self.addonId + 'dosen\'t exists', xbmc.LOGFATAL)
            return ''
        if infoId in ['changelog', 'fanart', 'icon', 'path', 'profile']:
            if infoId == 'changelog': return os.path.join(pathDir, 'changelog.txt')
            elif infoId == 'fanart':  return os.path.join(pathDir, 'fanart.jpg')
            elif infoId == 'icon': return os.path.join(pathDir, 'icon.png')
            elif infoId == 'path': return pathDir
            elif infoId == 'profile': return 'special://profile/addon_data/' + self.addonId + '/'
        
        if infoId == 'author': infoId = 'provider-name'
        addonXmlFile = os.path.join(pathDir, 'addon.xml')
        if  not os.path.exists(addonXmlFile): return None
        attributes = ['id', 'version', 'name', 'provider-name']
        metadata = ['summary', 'description', 'disclaimer', 'platform', 
                    'supportedcontent', 'language', 'license', 'forum', 
                    'website', 'source', 'email']
        with open(addonXmlFile, 'r') as xmlFile:
            xmlContent = xmlFile.read()
        xmlDom = minidom.parseString(xmlContent)
        if infoId in attributes:
            heading = xmlDom.getElementsByTagName('addon')
            heading = dict(heading[0].attributes.items())
            return heading.get(infoId, None)
        elif infoId in ['type', 'library']:
            if infoId == 'type': infoId = 'point'
            heading = xmlDom.getElementsByTagName('extension')
            heading = dict(heading[0].attributes.items())
            return heading.get(infoId, None)
        elif infoId in metadata:
            metadataInfo = xmlDom.getElementsByTagName(infoId)
            if metadataInfo:
                return metadataInfo[0].childNodes[0].data
            return None
        elif infoId == 'requires':
            requiresInfo = xmlDom.getElementsByTagName('import')
            modList = []
            if requiresInfo:
                for modToImport in requiresInfo:
                    modAttr = dict(modToImport.attributes.items())
                    modList.append(modAttr['addon'])
            return modList

    def getLocalizedString(self, stringId):
        """
        --Returns an addon's localized 'unicode string'.
        stringId : integer - id# for string you want to localize.
        example:
            - locstr = self.Addon.getLocalizedString(32000)
        """
        langPath = 'special://home/addons/' + self.addonId + '/resources/language/English/strings.xml' 
        langPath = xbmc.translatePath(langPath)
        if os.path.exists(langPath):
            with open(langPath, 'r') as langFile:
                langStr = langFile.read()
            strToSearch = '<string id="' + str(int(stringId)) + '">'
            limInf = langStr.find(strToSearch)
            if limInf == -1: return ''
            limInf += len(strToSearch)
            limSup = langStr.find('</string>', limInf)
            return langStr[limInf:limSup]
        return ''
    
    def getSetting(self, stringId):
        """
        --Returns the value of a setting as a unicode string.
        stringId : string - id of the setting that the module needs to access.
        example:
            - apikey = self.Addon.getSetting('apikey')
        """
        def getStringId(xmlFile, stringId, settingAttr):
            if not os.path.exists(settingXmlFile): return ''
            with open(xmlFile, 'r') as f: xmlData = f.read()
            tagRegex = '<' + 'setting id="{0}"\s+([^>]+(?:"|\'))\s?/?>'.format(stringId)
            match = re.search(tagRegex, xmlData)
            if not match: return ''
            attrib = match.group(1)
            attRegex = """([^\s=]+)\s*=\s*(\'[^<\']*\'|"[^<"]*")"""
            attr = dict((elem[0], elem[1][1:-1]) for elem in re.findall(attRegex,attrib))
            return attr.get(settingAttr, '')
            
        settingXmlFile = xbmc.translatePath('special://profile/addon_data/' + self.addonId + '/settings.xml')
        answer = getStringId(settingXmlFile, stringId, 'value')
        settingXmlFile = xbmc.translatePath('special://home/addons/' + self.addonId + '/resources/settings.xml') 
        if not answer: answer = getStringId(settingXmlFile, stringId, 'default')
        return answer
        
    
    def openSettings(self):
        """
        --Opens this scripts settings dialog.
        example:
            - self.Settings.openSettings()
        """
        pass

    def setSetting(self,settingId, value):
        """
        --Sets a script setting.
        addonId : string - id of the setting that the module needs to access. value : string or unicode - value of the setting.
        *Note, You can use the above as keywords for arguments.
        example:
            - self.Settings.setSetting(id='username', value='teamxbmc')
        """
        settingXmlFile = xbmc.translatePath('special://profile/addon_data/' + self.addonId + '/settings.xml')
        tree = ET.parse(settingXmlFile)
        root = tree.getroot()
        srchStr = './/setting[@id="' + settingId + '"]'
        root.find(srchStr).set('value', str(value))
        tree.write(settingXmlFile, method = 'xml')
        pass