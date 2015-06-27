'''
Created on 18/05/2014

@author: Alex Montes Barrios
'''
"""
xbmcvfs Namespace Reference
Classes and functions to work with files and folders. 

Classes
class      File
class      Stat
 
Functions
def     copy
def     delete
def     rename
def     mkdir
def     mkdirs
def     rmdir
def     exists
def     listdir
"""

import os

#  
# Detailed Description
# 
# Classes and functions to work with files and folders.
#
#
# Function Documentation
#

def copy(source, destination):
    """        
    Copy file to destination, returns true/false.
    
    source: string - file to copy.
    destination: string - destination file
    
    Example:
        success = xbmcvfs.copy(source, destination)
    """
    import shutil
    try:
        shutil.copy(source, destination)
        return True
    except:
        return False
    
def delete(fileName):
    """    
    Deletes a file.
    
    fileName: string - file to delete
    
    Example:
        xbmcvfs.delete(file)
    """
    if os.path.isfile(fileName) and not os.path.isdir(fileName):
        return os.unlink(fileName)
    return False
    
    
def exists(path):
    """    
    Checks for a file or folder existance, mimics Pythons os.path.exists()
    
    path: string - file or folder
    
    Example:
        success = xbmcvfs.exists(path)
    """
    return os.path.exists(path)

def listdir(path):
    """    
    listdir(path) -- lists content of a folder.
    
    path        : folder
    
    example:
     - dirs, files = xbmcvfs.listdir(path)
    """
    pathContent = os.listdir(path)
    files = []
    dirs = []
    for elem in pathContent:
        if os.path.isdir(os.path.join(path,elem)):
            dirs.append(elem)
        else:
            files.append(elem)
    return (dirs, files)
    
def mkdir(path):
    """    
    Create a folder.
    
    path: folder
    
    Example:
        success = xbmcfvs.mkdir(path)
    """
    if os.path.exists(path): raise OSError
    os.mkdir(path)
    return os.path.exists(path)

def mkdirs(path):
    """    
    mkdirs(path)--Create folder(s) - it will create all folders in the path.
    
    path : folder
    
    example:
    
    - success = xbmcvfs.mkdirs(path)
    Create folder(s) - it will create all folders in the path.

    path: folder

    Example:
        success = xbmcfvs.mkdirs(path)
    """
    dirsToCreate = []
    basePath = path
    sep = os.path.sep
    while not os.path.exists(path):
        basePath, sep, leaf = basePath.rpartition(sep)
        dirsToCreate.append(leaf)
    for elem in dirsToCreate:
        basePath = basePath + sep + elem
        try:
            mkdir(basePath)
        except:
            raise OSError
    return True
             
        
    

def rename(fileName, newFileName):
    """        
    Renames a file, returns true/false.
    
    fileName: string - file to rename
    newFileName: string - new filename, including the full path
    
    Example:
        success = xbmcvfs.rename(file,newFileName)
    """
    return os.rename(fileName, newFileName)

def rmdir(path):
    """    
    Remove a folder.
    
    path: folder
    
    Example:
        success = xbmcfvs.rmdir(path)
    """
    try:
        os.rmdir(path)
        return True
    except:
        return False

#
# CLASSES
#

class File(object):
    """
    xbmcvfs.File Class Reference
    
    Public Member Functions
    def     __init__
    def     close
    def     read
    def     readBytes
    def     seek
    def     size
    def     write
    """

# Constructor & Destructor Documentation

    def __init__(self, filename, optype = None):
        """        
        'w' - opt open for write
        example:
         f = xbmcvfs.File(file, ['w'])
        """
        pass
    
#    Member Function Documentation
    
    def close(self):
        """    
        example:
         f = xbmcvfs.File(file)
         f.close()
        """
        pass
    
    def read(self, bytesToRead = None):
        """        
        bytes : how many bytes to read [opt]- if not set it will read the whole file
        example:
        f = xbmcvfs.File(file)
        b = f.read()
        f.close()
        """
        pass
    
    def readBytes(self, numbytes):
        """        
        readBytes(numbytes)
        
        numbytes : how many bytes to read [opt]- if not set it will read the whole file
        
        returns: bytearray
        
        example:
        f = xbmcvfs.File(file)
        b = f.read()
        f.close()
    """
    pass

def seek(self):
    """    
    FilePosition : position in the file
    Whence : where in a file to seek from[0 begining, 1 current , 2 end possition]
    example:
     f = xbmcvfs.File(file)
     result = f.seek(8129, 0)
     f.close()
    """
    pass

def size(self):
    """    
    example:
     f = xbmcvfs.File(file)
     s = f.size()
     f.close()
    """
    pass

def write(self, bufferToWrite):
    """        
    buffer : buffer to write to file
    example:
     f = xbmcvfs.File(file, 'w', True)
     result = f.write(buffer)
     f.close()
    """
    pass

class Stat(object):
    def __init__(self, path):
        """        
        Stat(path) -- get file or file system status.
        
        path        : file or folder
        
        example:
        - print xbmcvfs.Stat(path).st_mtime()
    """
    pass

#
# Member Function Documentation
#

def st_atime(self): pass    
def st_ctime(self): pass    
def st_gid(self): pass    
def st_ino(self): pass    
def st_mode(self): pass    
def st_mtime(self): pass    
def st_nlink(self): pass    
def st_size(self): pass    
def st_uid(self): pass    
