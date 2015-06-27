# -*- coding: utf-8 -*-
'''
Created on 9/05/2014

@author: Alex Montes Barrios
'''

import os
import sys
import  xml.dom.minidom as minidom
import webbrowser

import xbmc
import xbmcplugin
import xbmcaddon
import xbmcgui
import xbmcStubs.menuManagement as menuManagement

import time
from functools import wraps
import urllib
import urllib2
import traceback

"""
http://r3---sn-ja5gvjv-jube.googlevideo.com/videoplayback?ip=190.143.51.163&key=yt5&mv=m&signature=44B92D31E67F3BF89C698251675E07EEB2608B57.817F3001565F1AF68612E5DC10940F56639FEE87&sparams=gcr,id,ip,ipbits,itag,ratebypass,source,upn,expire&mt=1401936352&mws=yes&ipbits=0&ratebypass=yes&gcr=co&itag=43&id=o-AOuBLanWVT3ruBZvcLnMuCMB5sEhx47x7ySEHHty2dZ0&upn=R9TIUhAB4w4&source=youtube&ms=au&fexp=903903,913434,923341,930008,932617,936207,945004&expire=1401957750&sver=3|User-Agent=Mozilla%2F5.0+%28Windows+NT+6.2%3B+Win64%3B+x64%3B+rv%3A16.0.1%29+Gecko%2F20121011+Firefox%2F16.0.1
"""


"""
http://r3---sn-ja5gvjv-jube.googlevideo.com/videoplayback?ip=190.143.51.163&key=yt5&mv=m&signature=E88C356E8CDD9BBC0B0027371D3A2407D1D365D0.09FF9733443C799A36520C9AEF606F1139A83A6E&sparams=id,ip,ipbits,itag,ratebypass,source,upn,expire&mt=1401936911&mws=yes&ipbits=0&ratebypass=yes&itag=22&&id=o-AILMUqoVgYTzXHPvhOFqBdulX0BYbiboKfO9t5bGGlBN&upn=WamPiK-XTLE&source=youtube&ms=au&fexp=913434,913564,923341,930008,931976,932617,938806&expire=1401958449&sver=3|User-Agent=Mozilla%2F5.0+%28Windows+NT+6.2%3B+Win64%3B+x64%3B+rv%3A16.0.1%29+Gecko%2F20121011+Firefox%2F16.0.1
"""
"""
http://r3---sn-ja5gvjv-jube.googlevideo.com/videoplayback?source=youtube&key=yt5&itag=22&ip=190.143.51.163&ratebypass=yes&ipbits=0&expire=1401958449&mws=yes&sver=3&upn=WamPiK-XTLE&id=o-AILMUqoVgYTzXHPvhOFqBdulX0BYbiboKfO9t5bGGlBN&sparams=id,ip,ipbits,itag,ratebypass,source,upn,expire&mt=1401936911&mv=m&ms=au&fexp=913434,913564,923341,930008,931976,932617,938806&signature=E88C356E8CDD9BBC0B0027371D3A2407D1D365D0.09FF9733443C799A36520C9AEF606F1139A83A6E|User-Agent=Mozilla%2F5.0+%28Windows+NT+6.2%3B+Win64%3B+x64%3B+rv%3A16.0.1%29+Gecko%2F20121011+Firefox%2F16.0.1
"""


def timethis(func):
    """
    Decorator that reports the execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start)
        if type(args[0]) == type('str'):
            print (args[0])
        else:
            print (args[0].get_full_url())
        return result
    return wrapper

urllib2.urlopen = timethis(urllib2.urlopen)
urllib.urlopen = timethis(urllib.urlopen)

ORIGINAL_PYTHONPATH = sys.path
base_addon = 'plugin://baseAddonMenus/'
menuObj = menuManagement.menuObject(base_addon)        

def getAvailableXbmcAddons():
    pathDir = xbmc.translatePath('special://home/addons')
    addons = [addon for addon in os.listdir(pathDir) if addon.startswith('plugin.video')]
    addonsAttr = {}
    for addonDir in addons:
        addonXmlFile = os.path.join(pathDir, addonDir, 'addon.xml')
        with open(addonXmlFile, 'r') as xmlFile:
            xmlContent = xmlFile.read()
        
        xmlDom = minidom.parseString(xmlContent)
        heading = xmlDom.getElementsByTagName('addon')
        heading = dict(heading[0].attributes.items())
        addonID = 'plugin://' + heading['id'] + '/'
        
        body = xmlDom.getElementsByTagName('extension')
        body = dict(body[0].attributes.items())
        
        heading.update(body)
        addonsAttr[addonID] = heading
    return addonsAttr

def getCompiledAddonSource(addonParam):
    addonId = addonParam['id']
    addonSourceFile = addonParam['library']
    if addonParam.get('dir', None):
        addonFile = os.path.join(addonParam['dir'], addonSourceFile)
    else:
        homeAddons = xbmc.translatePath('special://home/addons')
        addonFile = os.path.join(homeAddons, addonId, addonSourceFile)
    with open(addonFile, 'r') as f:
        addonSource = f.read()
    return compile(addonSource, addonFile, 'exec')

def getDependencies(AddonId, prevDep = []):
    if AddonId in prevDep: return prevDep
    pathToInc = xbmc.translatePath('special://home/addons' + '/' + AddonId)
    if not os.path.exists(pathToInc): return prevDep + [str(AddonId)]
    addonDep = xbmcaddon.Addon(AddonId).getAddonInfo('requires')
    if addonDep:
        for elem in addonDep:
            if elem.startswith('plugin.video'): continue
            prevDep = getDependencies(elem, prevDep)
    prevDep.append(str(AddonId))
    return prevDep


def setPythonPath(pluginID):
    pathToInc = str(xbmc.translatePath('special://home/addons' + '/' + pluginID))
    pyPathAdd = []
    if os.path.exists(pathToInc):
        pyPathAdd.append(pathToInc)
        
    addonDep = getDependencies(pluginID)

    for path in addonDep:
        if path.startswith('xbmc.'):
            pathToInc = str(xbmc.translatePath('special://Kodi' + '/system/python/lib'))
        else:
            pathToInc = '/' + path + ('' if path.startswith('script.') else '/resources') + '/lib' 
            pathToInc = str(xbmc.translatePath('special://home/addons' + pathToInc))
        if os.path.exists(pathToInc):
            pyPathAdd.append(pathToInc)
    sys.path = pyPathAdd + ORIGINAL_PYTHONPATH
    
def getAddonId(addonParam):
    limInf = len('plugin://')
    limSup = addonParam.find('/', limInf) + 1
    return addonParam[:limSup]

if __name__ == '__main__':
    argvIni = sys.argv
    sys.argv = [0,0,0]
    baseAddonDict = {'id':'baseAddonMenus', 
                     'library':'baseAddonMenus.py', 
                     'dir':'C:\\eclipse\\Workspace\\xbmc addon development\\src\\xbmcStubs\\'}
    addonAttr = getAvailableXbmcAddons()
    addonAttr[base_addon] = baseAddonDict
    addonID = ''
    url = base_addon
    menuSel = 0
    while True:
        if url.startswith('plugin://'):             # Plugin diferente
            pluginId, sep, urlArgs = url.partition('?')
            sys.argv[0], sys.argv[2] = str(pluginId), str(urlArgs)
            sys.argv[1] += 1 
            sys.argv[2] = str(sep) + sys.argv[2]
            actualID = getAddonId(sys.argv[0])
            if addonID != actualID:
                addonID = actualID
                addonParam = addonAttr[addonID]
                setPythonPath(addonParam['id'])
                sourceCode = getCompiledAddonSource(addonParam)
            try:
                exec(sourceCode)
            except:
                print('**** HA OCURRIDO UN ERROR ****')
                traceback.print_exc(file = sys.stderr)
                menuObj.displayMenu(0)
        else:                                       # Ejecución de media (archivo, etc, etc)
            urlLink, sep, userAgent = url.rpartition('|')
            webbrowser.open(urlLink)
            menuObj.displayMenu(0)
        menuSel, selObj = menuObj.getSelectionData()
        url = selObj[0]
        if menuSel == -1: break
    sys.argv = argvIni
    print('Program Terminated')    

    
