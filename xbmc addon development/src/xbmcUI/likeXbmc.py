'''
Created on 13/10/2014

@author: Alex Montes Barrios
'''

import sys, os

def translatePath(path):
    """
    --Returns the translated path.
 
    path : string or unicode - Path to format
 
    *Note, Only useful if you are coding for both Linux and Windows.
    e.g. Converts 'special://masterprofile/script_data' -> '/home/user/XBMC/UserData/script_data' on Linux.
 
    example:
        - fpath = xbmc.translatePath('special://masterprofile/script_data')
    """
    specialProtocol = {
                       'special://temp':'special://home/temp',
                       'special://masterprofile':'special://home/userdata',
                       'special://profile':'special://masterprofile',
                       'special://userdata':'special://masterprofile',
                       'special://database':'special://masterprofile/Database',
                       'special://thumbnails':'special://masterprofile/Thumbnails',
                       'special://musicplaylists':'special://profile/playlists/music',
                       'special://videoplaylists':'special://profile/playlists/video',
                       'special://logpath':'special://home'
                       }
    
    if sys.platform[:3] == 'win':
        specialProtocol['special://Kodi'] = 'C:\\Program Files\\Kodi'
        homePath = 'C:\\Users\\$USERNAME\\AppData\\Roaming\\Kodi'
        homePath = os.path.expandvars(homePath)
        specialProtocol['special://home'] = homePath
    SPECIAL = 'special://'
    pathToTranslate = path if path.find('/', len(SPECIAL)) != -1 else path + '/'
    while pathToTranslate.startswith(SPECIAL):
        keyLen = pathToTranslate.find('/',len(SPECIAL))
        key = pathToTranslate[:keyLen]
        specialPath = specialProtocol.get(key, None)
        if not specialPath: raise LookupError(key +' no se encuentra definido en el XBMC')
        pathToTranslate = specialPath + pathToTranslate[keyLen:]
    return pathToTranslate.replace('/','\\')
