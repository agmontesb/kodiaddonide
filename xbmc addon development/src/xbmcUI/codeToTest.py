import sys
import os

class KodiScriptImporter:

    KODI_STUBS = ''
    KODI_HOME = ''    
    archive = None
    prefix = ''
    path_cache = {}
    
    def __init__(self, pathprefix, kodi_stubs = None, kodi_home = None):
        self.pathprefix = pathprefix
        self.setPaths(kodi_stubs, kodi_home)
        self.path = filter(lambda x: x.startswith(pathprefix), os.listdir(self.KODI_HOME))
        stubs = ['xbmc', 'xbmcgui', 'xbmcaddon', 'xbmcplugin', 'xbmcvfs']
        criteria = all(map(lambda x: os.path.isfile(os.path.join(self.KODI_STUBS, x + '.py')), stubs)) and self.path 
        if not criteria: raise ImportError
        self.path_cache = dict((stub, os.path.join(self.KODI_STUBS, stub)) for stub in stubs)
                
        
        
    def setPaths(self, kodi_stubs, kodi_home):
        if sys.platform[:3] == 'win':
            baseDirectory = os.path.dirname(os.path.split(__file__)[0])
            self.KODI_STUBS = kodi_stubs or os.path.join(baseDirectory, 'xbmcStubs')    
            self.KODI_HOME= kodi_home or os.path.join(os.path.expandvars("$APPDATA"), "Kodi", "addons")
        

    def find_module(self, fullname, path = None):
        basename, sep, lastname = fullname.rpartition('.')
        if self.path_cache.has_key(fullname):
            testpath = self.path_cache.get(fullname)
        elif basename:
            basename = self.path_cache[basename]
            testpath = os.path.join(basename, lastname)
        else:
            for folder in self.path:
                testpath = os.path.join(self.KODI_HOME, folder, 'lib', lastname)
                if os.path.exists(testpath) or os.path.exists(testpath + '.py'): break
        criteria =  os.path.exists(testpath) or os.path.exists(testpath + '.py')
        if not criteria:
            print 'Not found: ', fullname 
            return None
        self.path_cache[fullname] = testpath
        print 'found:', fullname, ' at: ', testpath
        return None
        
    
    def get_code(self,fullname):
        pass
    
    def get_data(self, pathname):
        pass
    
    def get_filename(self, fullname):
        pass
    
    def get_source(self, fullname):
        pass
    
    def is_package(self, fullname):
        pass
    
    def load_module(self, fullname):
        pass
    
    def install(self, meta_path = True):
        if meta_path: 
            sys.meta_path.append(self)
        else:
            sys.path_hooks.append(KodiScriptImporter)
            sys.path.insert(0, self.pathprefix)

if __name__ == "__main__":
#     print os.getcwd()
#     print os.path.dirname(os.path.split(__file__)[0])
    
    importer = KodiScriptImporter('script.module')
    print importer.KODI_STUBS
    print importer.KODI_HOME
    importer.find_module('xbmc')
    importer.find_module('xbmcgui')
    importer.find_module('urlresolver')
    importer.find_module('urlresolver.plugins')
    importer.find_module('urlresolver.plugins.lib')
    importer.find_module('urlresolver')
    print importer.path_cache
    print importer.path
    
    print '============= final ============='
    