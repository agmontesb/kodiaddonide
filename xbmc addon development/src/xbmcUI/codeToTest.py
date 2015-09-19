# -*- coding: utf-8 -*-
import sys
import os
import imp

class KodiScriptImporter:

    KODI_STUBS = ''
    KODI_HOME = ''
    KODI = ''    
    archive = None
    prefix = ''
    path_cache = {}
    
    def __init__(self, pathprefix, kodi = None, kodi_home = None):
        self.stack = []
        self.nullstack = set()
        self.path = None
        self.pathprefix = pathprefix
        self.setPaths(kodi, kodi_home)
        self.initPathCache(pathprefix)

    def setPaths(self, kodi, kodi_home):
        if sys.platform[:3] == 'win':
            baseDirectory = os.path.dirname(os.path.split(__file__)[0])
            self.KODI_STUBS = os.path.join(baseDirectory, 'xbmcStubs')
            self.KODI = kodi or os.path.join(os.path.expandvars("$PROGRAMFILES"), "Kodi", "addons")    
            self.KODI_HOME= kodi_home or os.path.join(os.path.expandvars("$APPDATA"), "Kodi", "addons")
        if not all(map(os.path.exists,[self.KODI, self.KODI_HOME])):
            print "kodi: " + self.KODI + ' or kodi_home: ' + self.KODI_HOME + "doesn't exits"
            raise ImportError 
                
    def initPathCache(self, pathprefix):
        def selFiles(xDir):
            basepaths = filter(lambda x: x.startswith(pathprefix), os.listdir(xDir))
            return [os.path.join(xDir, elem, 'lib') for elem in basepaths]
            
        stubs = ['xbmc', 'xbmcgui', 'xbmcaddon', 'xbmcplugin', 'xbmcvfs']
        self.path_cache = dict((stub, os.path.join(self.KODI_STUBS, stub)) for stub in stubs)

        basepaths = selFiles(self.KODI) + selFiles(self.KODI_HOME)
        if not basepaths: raise ImportError
        criteria = lambda x: os.path.splitext(x)[1] == '.py' or os.path.exists(os.path.join(x, '__init__.py'))
        for pathToProcess in sorted(basepaths):
            for elem in os.listdir(pathToProcess):
                elemPath = os.path.join(pathToProcess, elem)
                if not criteria(elemPath) or elem == '__init__.py': continue
                key = os.path.splitext(elem)[0]
                self.path_cache[key] =  self.path_cache.get(elem) or os.path.splitext(elemPath)[0]
        
    def find_module(self, fullname, path = None):
        basename, sep, lastname = fullname.rpartition('.')  # @UnusedVariable
        rootname = fullname.partition('.')[0]
        if not self.path_cache.has_key(rootname):
            if path and (path[0].startswith(self.KODI_HOME) or path[0].startswith(self.KODI)):
                testpath = os.path.join(path[0], lastname)
                criteria =  os.path.exists(testpath) or os.path.exists(testpath + '.py')
            else:
                return None
        elif self.path_cache.has_key(fullname):
            testpath = self.path_cache.get(fullname)
            criteria = True
        elif basename:
            criteria = self.path_cache.has_key(basename) 
            if criteria:
                basename = self.path_cache[basename]
                testpath = os.path.join(basename, lastname)
                criteria =  os.path.exists(testpath) or os.path.exists(testpath + '.py')
        if not criteria:
            print 'Not found: ' + fullname
            self.nullstack.add(fullname)
            return
        self.path_cache[fullname] = testpath
        print 'found:', fullname, ' at: ', testpath
        return self
        
    
    def get_code(self,fullname):
        src = self.get_source(fullname)
        code = compile(src, self.get_filename(fullname), 'exec')
        return code
    
    def get_data(self, pathname):
        try:
            u = open(pathname, 'rb')
            data = u.read()
            return data
        except:
            raise ImportError("Can't find %s" % pathname)
    
    def get_filename(self, fullname):
        scriptPath = self.path_cache[fullname]
        if self.is_package(fullname): return os.path.join(scriptPath, '__init__.py')
        return scriptPath + '.py'
    
    def get_source(self, fullname):
        filename = self.get_filename(fullname)
        return self.get_data(filename)
#         try:
#             u = open(filename, 'r')
#             source = u.read()
#             return source
#         except:
#             raise ImportError("Can't load %s" % filename)

    
    def is_package(self, fullname):
        fullpath = self.path_cache[fullname]
        return os.path.exists(os.path.join(fullpath, '__init__.py'))
    
    def load_module(self, fullname):
#         try:
#             mod = sys.modules[fullname]
#         except KeyError: pass
#         else:
#             print fullname, '  is in sys.modules not created'
#             return mod
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        self.stack.append(fullname)
#         mod = imp.new_module(fullname)
        mod.__file__ = self.get_filename(fullname)
        mod.__loader__ = self
        mod.__package__ = fullname.rpartition('.')[0]
        code = self.get_code(fullname)
        if self.is_package(fullname):
            mod.__package__ = fullname
            mod.__path__ = [self.path_cache[fullname]]
        try:
            exec(code, mod.__dict__)
        except:
            if self.stack[0] == fullname:
                print '***' + fullname + '*** Ha ocurrido un error, los siguientes módulos que fueron creados deben eliminarse: '
                print '\n'.join(sorted(self.stack))
            pass
        else:
#             sys.modules[fullname] = mod
            if self.stack[0] == fullname:
                print 'IMPORT ' + fullname + ' successful, los siguientes módulos fueron creados en el proceso : '
                print '\n'.join(sorted(self.stack))
                pass
        finally:
            if self.stack[0] == fullname:
                self.stack = []
                print '******los siguientes módulos dummy deben eliminarse : *****'
                toSave = []
                print '\n'.join(sorted(self.nullstack))
                while self.nullstack:
                    key = self.nullstack.pop()
                    if sys.modules.has_key(key) and not sys.modules[key]:
                        rootname = key.rpartition('.')[2]
                        if sys.modules.has_key(rootname) and hasattr(sys.modules[rootname], '__file__'):
                            filename = sys.modules[rootname].__file__
                            bFlag = filename.startswith(self.KODI_HOME) or filename.startswith(self.KODI)
                            bFlag = bFlag and not self.path_cache.has_key(rootname)
                            if bFlag:
                                toSave.append((rootname, sys.modules[rootname].__file__))                          
                        sys.modules.pop(key)
                if toSave:
                    print '******los siguientes módulos fueron reados por fuera  : *****'
                    for elem in sorted(toSave): print elem[0].ljust(15), elem[1]
                    pass
        return mod
    
    def install(self, meta_path = True):
        if meta_path: 
            sys.meta_path.append(self)
        else:
            def init(iself, path):
                if path == self.pathprefix:iself.path = None
                elif path.startswith(self.KODI_HOME) or path.startswith(self.KODI): iself.path = [path]
                else: raise ImportError
                    
            def find(iself, fullname, path = None):
                return self.find_module(fullname, iself.path)
            
            def getAttr(iself, attr):
                return getattr(self, attr)
            
            sys.path_hooks.append(type('trnClass', (), {'__init__':init, 'find_module':find, '__getattr__':getAttr}))
            sys.path.insert(0, self.pathprefix)
            
def trnClass(pathprefix):
    class pathImporter:
        importer = KodiScriptImporter(pathprefix)
        def __init__(self, path):
            bFlag1 = path == self.importer.pathprefix
            bFlag2 = path.startswith(self.importer.KODI_HOME) or path.startswith(self.importer.KODI)
            if not (bFlag1 or bFlag2):
                raise ImportError
            if bFlag1: self.path = None
            if bFlag2: self.path = path
            
        def find_module(self, fullname, path = None):
            return self.importer.find_module(fullname, self.path)
            
        def __getattr__(self, attr):
            return getattr(self.importer, attr)
    return pathImporter
    
if __name__ == "__main__":
#     print os.getcwd()
#     print os.path.dirname(os.path.split(__file__)[0])
#     genPathCache()

    meta_path = False
    importador = KodiScriptImporter('script.module')
    importador.install(meta_path)

#     myClass = trnClass('script.module')
#     sys.path_hooks.append(myClass)
#     sys.path.insert(0, 'script.module')
    


    import metahandler
#     import xbmc
#     import xbmcgui
#     import xbmcaddon
#     import BeautifulSoup
    import urlresolver  # @UnresolvedImport
    for k in [metahandler, urlresolver]:
        print '=============' + str(k) + '===================='
        print '\n'.join(sorted(k.__dict__.keys()))
        
        print '============= final ============='
        
    print urlresolver.resolve('https://www.youtube.com/watch?v=EiOglTERPEo')
    