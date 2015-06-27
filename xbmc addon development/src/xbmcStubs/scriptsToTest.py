import os
import xbmcStubs.xbmc as xbmc
import xbmcStubs.xbmcvfs as xbmcvfs

def listFiles(filePath):
    dirs, files = xbmcvfs.listdir(filePath)
    for elem in files:
        front, ext =  os.path.splitext(elem)
        if ext == '.py':
            absPath = os.path.join(filePath, elem)
            with open(absPath, 'r') as fileObj:
                fileContent = fileObj.read()
            if fileContent.find('t0mm0.common.')!=-1:
                fileContent = fileContent.replace('t0mm0.common.', 'addon.common.')
                with open(absPath, 'w') as fileObj:
                    fileObj.write(fileContent)
                
    for elem in dirs:
        absPath = os.path.join(filePath,elem)
        listFiles(absPath)

addonId = 'script.module.urlresolver'
filePath = xbmc.translatePath('special://home/addons/' + addonId)
listFiles(filePath)




# import xbmcStubs.xbmc as xbmc
# import xbmcStubs.xbmcaddon as xbmcaddon
# import re
# 
# def getAttribIn(tagName, strIn):
#     tagRegex = '<' + tagName + '\s+([^>]+(?:"|\'))\s?/?>'
#     attRegex = """([^\s=]+)\s*=\s*(\'[^<\']*\'|"[^<"]*")"""
#     answer = []
#     tagList = re.findall(tagRegex, strIn)
#     for tagElem in tagList:
#         attrList = re.findall(attRegex, tagElem)
#         attrDict = {}
#         for attrElem in attrList:
#             attrDict[attrElem[0]] = attrElem[1][1:-1] 
#         answer.append(attrDict)
#     return answer
# 
# 
# addonId = 'plugin.video.projectfreetv'
# xmlPath = xbmc.translatePath('special://home/addons/' + addonId + '/resources/settings.xml')
# print(xmlPath)
# 
# with open(xmlPath,'r') as f:
#     xmlFile = f.read()
#     
# attrList = getAttribIn('setting', xmlFile)
# for elem in attrList:
#     print elem



# import sys
# # sys.modules.clear()
# class xbmcDict(dict):
#     def __init__(self, *args, **kwargs):
#         super(xbmcDict, self).__init__(*args, **kwargs)
#         self.init_keys = self.keys()
#         
#     def clear(self):
#         for key in self.keys():
#             if key not in self.init_keys: print self.pop(key)
#             
# 
# if __name__ == "__main__":
#     print len(sys.modules)
#     print type(sys.modules)
#     dictTuple = sys.modules.items()
#     xbmcInitModules = xbmcDict(dictTuple)
#     sys.modules['sys'].modules = xbmcInitModules
#     print type(sys.modules)
#     print sys.modules.get('xbmcStubs.xbmc', 'no existe')
#     import xbmcStubs.xbmc
#     import xbmcStubs.xbmcaddon
#     import xbmcStubs.xbmcgui
#     import xbmcStubs.xbmcplugin
#     print len(sys.modules['sys'].modules.keys())
#     print len(sys.modules.keys())
#     sys.modules['basura'] = 'esto es pura prueba'
#     print sys.modules.init_keys
#     print sys.modules.keys()
#     print xbmcStubs.xbmc.translatePath('special://home')
#     sys.modules.clear()
#     print 'final, final'
#     print sys.modules['__main__']
#     print len(sys.modules)
#     print type(sys.modules)
