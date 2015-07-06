import os
import sys
import imp
import __future__
 
dataBank = {
            'installed_meta_cache' : {},
            'path_hook' : {},
            }
 
class XbmcModuleImportFinder(object):
    def __init__(self, xbmcStubsDir):
        self._loaders = {}
        self.addonRoot = xbmcStubsDir
              
    def isAbsolutePath(self, baseName):
        if not self.pathStack: return True
        path = os.path.join(self.pathStack[-1], baseName)
        return not (os.path.exists(path) or os.path.exists(path + '.py'))
  
    def getRootPath(self, path, baseName):
        if path and path[0] != self.addonRoot: return None 
        if baseName not in ['xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcplugin', 'xbmcvfs']: return None
        dPath = self.addonRoot
        testpath = os.path.join(dPath, baseName)
        if os.path.exists(testpath + '.py'): return dPath
        return None
      
    def find_module(self, fullname, path = None):
        parts = fullname.split('.')
        baseName = parts[-1]
        basePath = self.getRootPath(path, baseName)
        if not basePath: return None
          
        fullname = os.path.join(basePath, baseName + '.py')
        if os.path.exists(fullname):
            if basePath not in self._loaders:
                self._loaders[basePath] = AddonMetaImportLoader(basePath)
            return self._loaders[basePath]
        return None
      
    def invalidate_caches(self):
        pass
 
  
class KodiAddonImportFinder(object):
    def __init__(self, *arg, **kwargs):
        self.pathStack = []
        self._loaders = {}
        self.addonRoot = arg
        self.installedAddon = list(arg[:-1])
        addonRoot = arg[-1]
        addons = [addonId for addonId in os.listdir(addonRoot) if addonId.startswith('script.')]
        for addonId in addons:
            self.installedAddon.append(os.path.join(addonRoot, addonId,'lib'))
              
    def isAbsolutePath(self, baseName):
        if not self.pathStack: return True
        path = os.path.join(self.pathStack[-1], baseName)
        return not (os.path.exists(path) or os.path.exists(path + '.py'))
  
    def getRootPath(self, path, baseName):
        testPaths = []
        if path:
            if not path[0].startswith(self.addonRoot): return None
            testPaths.append(path[0])
        else:
            if self.pathStack: testPaths.append(self.pathStack[-1])
            testPaths.extend(self.installedAddon)
        for dPath in testPaths:
            testpath = os.path.join(dPath, baseName)
            if os.path.exists(testpath) or os.path.exists(testpath + '.py'): return dPath
        return None
     
    def normFullName(self, basePath, baseName):
        for base in self.addonRoot:
            if basePath.startswith(base): break
        os_sep = os.sep
        if base == self.addonRoot[-1]:
            posFin = basePath.find(os_sep + 'lib' + os.sep)
            if posFin == -1: posFin = len(basePath) - 5
            posFin += 5
            base = basePath[:posFin]
        suffix = basePath[len(base):].lstrip(os_sep)
        if suffix:return '.'.join([suffix.replace(os.sep,'.'),baseName])
        return baseName
      
    def find_module(self, fullname, path = None):
        parts = fullname.split('.')
        baseName = parts[-1]
        basePath = self.getRootPath(path, baseName)
        if not basePath: return None
 
#         fullname = self.normFullName(basePath, baseName)
        fullpath = os.path.join(basePath, baseName)
        if os.path.exists(fullpath):
            loader = AddonMetaImportLoader(fullpath, isPackage = True)
            try:
                self.pathStack.append(fullpath)
                mod = loader.load_module(fullname)
                self._loaders[fullpath] = AddonMetaImportLoader(fullpath)
            except ImportError:
                loader = None
            finally:
                self.pathStack.pop()
                if sys.meta_path[-1] != self:
                    indx = sys.meta_path.index(self)
                    sys.meta_path.append(sys.meta_path.pop(indx))
            return loader
          
        fullname = fullpath + '.py'
        if os.path.exists(fullname):
            if fullname not in self._loaders:
                self._loaders[fullname] = AddonMetaImportLoader(basePath)
            return self._loaders[fullname]
        return None
      
    def invalidate_caches(self):
        pass
  
  
class AddonMetaImportLoader(object):
    def __init__(self, addonPath, isPackage = False):
        self.addonPath = addonPath
        self._isPackage = isPackage
        self._source_cache = {}
        self.co_flags = 0
          
    def module_repr(self, module):
        return '<addonmodule %r from %r>' % (module.__name__, module.__file__)
      
    def load_module(self, fullname):
        try: return sys.modules[fullname]
        except KeyError: pass
#         print('in load_module before mod generation')
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = self.get_filename(fullname)
        mod.__loader__ = self
        mod.__package__ = fullname.rpartition('.')[0]
        code = self.get_code(fullname)
        if self.is_package(fullname):
#             print('setting __package__ and __path__')
#             print('apth =' + self.addonPath)
            mod.__package__ = fullname
            mod.__path__ = [self.addonPath]
        exec(code, mod.__dict__)
        return mod
      
    def get_code(self, fullname):
        src = self.get_source(fullname)
        code = compile(src, self.get_filename(fullname), 'exec', flags = self.co_flags)
        return code
      
    def get_data(self, path):
        pass
      
    def get_filename(self, fullname):
        if self.is_package(fullname): return os.path.join(self.addonPath, '__init__.py')
        return os.path.join(self.addonPath, fullname.split('.')[-1] + '.py')
      
    def get_source(self, fullname):
        filename = self.get_filename(fullname)
        if filename in self._source_cache:
            return self._source_cache[filename]
        try:
            u = open(filename, 'r')
            source = u.read()
            self._source_cache[filename] = source
            return source
        except:
            raise ImportError("Can't load %s" % filename)
      
    def is_package(self, fullname):
        return self._isPackage
      
def install_meta(*finderRoot, **kwargs):
    hookId = kwargs.get('hookId','hook')
    atype = kwargs.get('atype','kodi')
    if dataBank['installed_meta_cache'].has_key(hookId): remove_meta(hookId)
    if atype == 'kodi':finder = KodiAddonImportFinder(*finderRoot)
    if atype == 'xbmc': finder = XbmcModuleImportFinder(finderRoot[-1])
    dataBank['installed_meta_cache'][hookId] = finder
    sys.meta_path.append(finder)
         
def remove_meta(hookId):
    if not dataBank['installed_meta_cache'].has_key(hookId):return
    finder = dataBank['installed_meta_cache'].pop(hookId)
    sys.meta_path.remove(finder)
  
def get_initial_state():
    dataBank['initial_state'] = {}
    dataBank['initial_state']['python_path'] = sys.path[:]
    dataBank['initial_state']['sys_modules_keys'] = sys.modules.keys()
    dataBank['initial_state']['meta_path'] = sys.meta_path[:]
    dataBank['initial_state']['path_hooks'] = sys.path_hooks[:]
     
          
def restore_initial_state():
    if not dataBank.has_key('initial_state'): return
    initialState = dataBank.pop('initial_state')
    sys_modules_keys = initialState.pop('sys_modules_keys') 
    for key in sys.modules.keys():
        if key in sys_modules_keys : continue
        del sys.modules[key]
    sys.path = initialState.pop('python_path')
    sys.meta_path = initialState.pop('meta_path')
    sys.path_hooks = initialState.pop('path_hooks')
    sys.path_importer_cache.clear()
 
 
def select_Finder(hookId, xbmcStubsDir, addonRoot):    
    def finder(path):
        if xbmcStubsDir and path == xbmcStubsDir:
            return XbmcModuleImportFinder(path, isMetha = True)
        elif addonRoot and path == addonRoot:
            return KodiAddonImportFinder(path, isMetha = True)
    finder.__name__ = hookId
    return finder
     
     
def install_path_hook(hookId = 'hook', xbmcStubsDir = None, addonRoot = None):
    handle_path = select_Finder(hookId, xbmcStubsDir, addonRoot)
    dataBank['path_hook'][hookId] = handle_path 
    sys.path_hooks.append(handle_path)
    sys.path_importer_cache.clear()
     
def remove_path_hooks(hookId = None):
    if hookId and dataBank['path_hook'].get(hookId,None):
        hook = dataBank['path_hook'].pop(hookId)
        sys.path_hooks.remove(hook)
    else:
        for hookId in dataBank['path_hook'].keys():
            hook = dataBank['path_hook'].pop(hookId)
            sys.path_hooks.remove(hook)
    sys.path_importer_cache.clear()
     
     
     
     
def pyDevSetup():
    import os
    import sys
    xbmcRoot = r'C:\Users\Alex Montes Barrios\git\addonDevelopment\xbmc addon development\src\xbmcStubs'
    addonRoot = r'C:\Users\Alex Montes Barrios\AppData\Roaming\Kodi\addons'
    sys.path.insert(0, r'C:\Users\Alex Montes Barrios\git\addonDevelopment\xbmc addon development\src\xbmcUI')
    import KodiAddonImporter as kai
    kai.install_meta(xbmcRoot, addonRoot, hookId = 'pydev_hook', atype = 'kodi')
    import urlresolver
    
    
 
 
if __name__ == '__main__':
    sys.meta_path = []
    xbmcStubsDir = r'C:\Users\Alex Montes Barrios\git\addonDevelopment\xbmc addon development\src\xbmcStubs'
    addonRoot = r'C:\Users\Alex Montes Barrios\AppData\Roaming\Kodi\addons'
    addonDir = r'C:\Users\Alex Montes Barrios\AppData\Roaming\Kodi\addons\plugin.video.phstreams'
    install_meta(xbmcStubsDir, hookId = 'xbmc_hook', atype = 'xbmc')
    install_meta(addonDir, addonRoot, hookId = 'kodi_hook', atype = 'kodi')
    import xbmc
    import t0mm0.common
    import t0mm0
    import urlresolver
#     from resources.modules import main,resolvers    
# #     remove_meta()
    remove_path_hooks()
    print '\n'.join(sorted(dir(urlresolver)))
    print 'terminado normalmente'
    pass       
          





 
# import os
# import sys
# import imp
# import xml.etree.ElementTree as ET
#  
# dataBank = {
#             'installed_meta_cache' : None,
#             'python_path' : None,
#             'sys_modules_keys' : None }
#   
# class AddonMetaImportFinder(object):
#     def __init__(self, xbmcStubsDir, addonRoot):
#         self.pathStack = []
#         self._loaders = {}
#         self.installedAddon = [xbmcStubsDir]
#         addons = [addonId for addonId in os.listdir(addonRoot) if addonId.startswith('script.module')]
#         for addonId in addons:
#             self.installedAddon.append(os.path.join(addonRoot, addonId,'lib'))
#         self.addonRoot = addonRoot
#               
#     def isAbsolutePath(self, baseName):
#         if not self.pathStack: return True
#         path = os.path.join(self.pathStack[-1], baseName)
#         return not (os.path.exists(path) or os.path.exists(path + '.py'))
#   
#     def getRootPath(self, path, baseName):
#         testPaths = []
#         if path:
#             if not path[0].startswith(self.addonRoot): return None
#             testPaths.append(path[0])
#         else:
#             if self.pathStack: testPaths.append(self.pathStack[-1])
#             testPaths.extend(self.installedAddon)
#         for dPath in testPaths:
#             testpath = os.path.join(dPath, baseName)
#             if os.path.exists(testpath) or os.path.exists(testpath + '.py'): return dPath
#         return None
#       
#     def find_module(self, fullname, path = None):
#         parts = fullname.split('.')
#         baseName = parts[-1]
#         basePath = self.getRootPath(path, baseName)
#         if not basePath: return None
#           
#         fullpath = os.path.join(basePath, baseName)
#         if os.path.exists(fullpath):
#             loader = AddonMetaImportLoader(fullpath, isPackage = True)
#             try:
#                 self.pathStack.append(fullpath)
#                 loader.load_module(fullname)
#                 self._loaders[fullpath] = AddonMetaImportLoader(fullpath)
#             except ImportError:
#                 loader = None
#             finally:
#                 self.pathStack.pop()
#             return loader
#           
#         fullname = fullpath + '.py'
#         if os.path.exists(fullname):
#             if fullname not in self._loaders:
#                 self._loaders[fullname] = AddonMetaImportLoader(basePath)
#             return self._loaders[fullname]
#         return None
#       
#     def invalidate_caches(self):
#         pass
#   
#   
# class AddonMetaImportLoader(object):
#     def __init__(self, addonPath, isPackage = False):
#         self.addonPath = addonPath
#         self._isPackage = isPackage
#         self._source_cache = {}
#           
#     def module_repr(self, module):
#         return '<addonmodule %r from %r>' % (module.__name__, module.__file__)
#       
#     def load_module(self, fullname):
#         try:
#             return sys.modules[fullname]
#         except KeyError:
#             pass
#         mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
#         mod.__file__ = self.get_filename(fullname)
#         mod.__loader__ = self
#         mod.__package__ = fullname.rpartition('.')[0]
#         if self.is_package(fullname):
#             mod.__package__ = fullname
#             mod.__path__ = [self.addonPath]
#         code = self.get_code(fullname)
#         exec(code, mod.__dict__)
#         return mod
#       
#     def get_code(self, fullname):
#         src = self.get_source(fullname)
#         return compile(src, self.get_filename(fullname), 'exec')
#       
#     def get_data(self, path):
#         pass
#       
#     def get_filename(self, fullname):
#         if self.is_package(fullname): return os.path.join(self.addonPath, '__init__.py')
#         return os.path.join(self.addonPath, fullname.split('.')[-1] + '.py')
#       
#     def get_source(self, fullname):
#         filename = self.get_filename(fullname)
#         if filename in self._source_cache:
#             return self._source_cache[filename]
#         try:
#             u = open(filename, 'r')
#             source = u.read().decode('utf-8')
#             self._source_cache[filename] = source
#             return source
#         except:
#             raise ImportError("Can't load %s" % filename)
#       
#     def is_package(self, fullname):
#         return self._isPackage
#       
# kodiAddonFinder = None
#   
# def install_meta(xbmcStubsDir, addonRoot):
#     if dataBank.get('installed_meta_cache'): return
#     kodiAddonFinder = AddonMetaImportFinder(xbmcStubsDir, addonRoot)
#     dataBank['installed_meta_cache'] = kodiAddonFinder
#     dataBank['python_path'] = sys.path
#     dataBank['sys_modules_keys'] = sys.modules.keys() 
#     sys.meta_path.append(kodiAddonFinder)
#           
# def remove_meta():
#     if not dataBank.get('installed_meta_cache'): return
#     kodiAddonFinder = dataBank['installed_meta_cache'] 
#     sys.meta_path.remove(kodiAddonFinder)
#     for key in sys.modules.keys():
#         if key in dataBank['sys_modules_keys']: continue
#         del sys.modules[key]
#     sys.path = dataBank['python_path']
#     for key in dataBank: dataBank[key] = None
#       
# if __name__ == '__main__':
#     sys.meta_path = []
#     xbmcStubsDir = r'C:\Users\Alex Montes Barrios\git\addonDevelopment\xbmc addon development\src\xbmcStubs'
#     addonRoot = r'C:\Users\Alex Montes Barrios\AppData\Roaming\Kodi\addons'
#     install_meta(xbmcStubsDir, addonRoot)
#     import xbmc
#     import t0mm0
#     import t0mm0.common
#     import urlresolver
#     remove_meta()
#     pass       
           

