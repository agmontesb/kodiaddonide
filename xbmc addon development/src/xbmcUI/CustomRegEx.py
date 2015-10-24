# -*- coding: utf-8 -*-
'''
Created on 19/09/2015

@author: Alex Montes Barrios
'''
from collections import namedtuple
from operator import pos
import re
from timeit import template
import itertools

Token = namedtuple('Token', ['type', 'value'])

PREFIX = r'(?P<PREFIX>(?s).+(?=<!DOCTYPE))'
GENSELFTAG = r'(?P<GENSELFTAG><[a-zA-Z\d]+[^>]+/>)'
GENTAG = r'(?P<GENTAG><[a-zA-Z\d]+[^>]*>)'
DOCSTR =r'(?P<DOCSTR><![^>]*>)'
BLANKTEXT = r'(?P<BLANKTEXT>(?<=>)\W+(?=<[a-z/]))'
GENTEXT = r'(?P<GENTEXT>(?<=>).+?(?=<[a-z/]))'
ENDTAG = r'(?P<ENDTAG></[^>]+>)'
SUFFIX = r'(?P<SUFFIX>(?s)(?<=</html>).+)'


class filteredStr:
    def __init__(self, htmlString):
        self.htmlString = htmlString
        self.start = []
        self.end = []
        for match in re.finditer(r'<!--.+?-->|<script[^>]*>.*?</script>', htmlString, re.DOTALL):
            self.end.append(match.start())
            self.start.append(match.end())
            
        if self.end[0] == 0:
            self.end.pop(0)
        else:
            self.start.insert(0, 0)
            
        if self.start[-1] == len(htmlString):
            self.start.pop()
        else:
            self.end.append(len(htmlString))

        self.base = [0]
        for k in range(len(self.start)-1):
#             print k
#             print self.base[k] + self.end[k] - self.start[k], self.base
            self.base.append(self.base[k] + self.end[k] - self.start[k])

#         for k in range(len(self.start)):
#             print k, self.start[k], self.end[k], self.base[k]
            
            
    def __str__(self):
        return ''.join(list(map(lambda x,y: self.htmlString[x:y], self.start, self.end)))
    
    def __getitem__(self):
        pass
    
    def deTrnsSlice(self, trnIni, trnFin):
        trnFunc = lambda pos: sum(map(lambda x: x <= pos, self.base)) - 1
        indx = trnFunc(trnIni)
        posIni = trnIni + self.start[indx] - self.base[indx]
        indx = trnFunc(trnFin - 1)
        posFin = trnFin + self.start[indx] - self.base[indx]
        return (posIni, posFin)
    
    def transSlice(self, posIni, posFin):
        trnFunc = lambda pos: max(0, sum(map(lambda x: x <= pos, self.start)) - 1)
        indx = trnFunc(posIni)
        trnIni = self.base[indx] + min(self.end[indx], posIni) - self.start[indx]
        indx = trnFunc(posFin)
        trnFin = self.base[indx] + min(self.end[indx], posFin) - self.start[indx]
        return (trnIni, trnFin)

class ExtRegexObject:
    def __init__(self, pattern, compflags, tagPattern, tags, varList):
        self.pattern = pattern
        self.flags = compflags
        self.tagPattern = tagPattern
        self.tags = tags
        self.groupindex = {}
        for k, varTuple in enumerate(varList):
            self.groupindex[varTuple[1]] = k + 1
        self.varList = varList
        self.groups = len(varList)
        pass

    def search(self, origString, spos = -1, sendpos = -1):
        pos = spos if spos != -1 else 0
        endpos = sendpos if sendpos != -1 else len(origString)
        findTag = ExtRegexParser(self.varList, self.tags)
        rootTag = self.tags.keys()[0].partition('.')[0]
        diffSet = set(self.tags.get(rootTag,{}).keys()).difference(['*'])
        if diffSet:
            myfunc = lambda x: '<' + self.tagPattern + '\s[^>]*' + '=[^>]+'.join(x) + '=[^>]+[/]*>'
            SRCHTAG =  '|'.join(map(myfunc, itertools.permutations(diffSet,len(diffSet))))
        else:
            SRCHTAG = '<' + self.tagPattern + '(?:\s|>)'
        master_pat = re.compile(SRCHTAG, re.DOTALL)
        posIni = pos
        while 1:
            match = master_pat.search(origString[posIni:endpos])
            if not match: return None
            tagPos = match.start() + posIni
            if origString[posIni:tagPos].rfind('<!--') <= origString[posIni:tagPos].rfind('-->'): 
                varPos = findTag.initParse(origString[tagPos:], tagPos)
                if varPos: break
            posIni = match.end() + posIni
        return ExtMatchObject(self, origString, spos, sendpos, varPos)            

    def match(self, string, pos = -1, endpos = -1):
        m = self.search(string, pos, endpos)
        return m if m.start() == 0 else None

    def split(self, string, maxsplit = 0):
        answer = []
        lstPos = 0
        for k, match in enumerate(self.finditer(string)):
            if maxsplit and k + 1 > maxsplit: break
            posIni, posFin = match.span()
            answer.append(string[lstPos:posIni])
            lstPos = posFin
            if match.groups():answer.extend(match.groups())
        if lstPos != len(string): answer.append(string[lstPos:])
        return answer
    
    def findall(self, string, pos = -1, endpos = -1):
        answer = []
        for match in self.finditer(string, pos, endpos):
            answer.append(match.groups())
        return answer
    
    def finditer(self, string, pos = -1, endpos = -1):
        def iterTag():
            nPos = pos
            while 1:
                match = self.search(string, nPos, endpos)
                if not match: break
                yield match
                nPos = match.end()
        return iterTag()

    def sub(self, repl, string, count = 0):
        pass
    def subn(self, repl, string, count = 0):
        pass

class ExtMatchObject:
    def __init__(self, regexObject, htmlstring, pos, endpos, varPos):
        self.pos = pos
        self.enpos = endpos
        self.lastindex = 0
        self.lastgroup = 0
        self.re = regexObject
        self.string = htmlstring
        self.varpos = varPos
    
    def _varIndex(self, x):
        nPos = self.re.groupindex[x] if isinstance(x, basestring) else int(x)
        if nPos > len(self.varpos): raise Exception
        return nPos
    
    def expand(self, template):
        pass
    
    def group(self, *grouplist):
        if not grouplist: grouplist = [0]
        answer = []
        for group in grouplist:
            posIni, posFin = self.span(group)
            answer.append(self.string[posIni:posFin])
        return answer if len(answer) > 1 else answer[0]
    
    def groups(self, default = None):
        return tuple(self.string[tpl[0]:tpl[1]] for tpl in self.varpos[1:])
    
    def groupdict(self, default = None):
        keys = sorted(self.re.groupindex.keys(), lambda x, y: self.re.groupindex[x] - self.re.groupindex[y])
        values = self.groups()
        return dict(zip(keys, values))
    
    def start(self, group = 0):
        return self.span(group)[0] 
    
    def end(self, group = 0):   
        return self.span(group)[1] 
    
    def span(self, group = 0):
        nPos = self._varIndex(group)
        return self.varpos[nPos]
           
    
ATTRSEP = '.'
COMMSEP = '*'

"""
EJEMPLO DEL RESUULTADO DE COMPILAR LOS PATTERNS

++++++++++++++++++++
>>> req = compile(r'(?#<TAG a>)', 0)
>>> req.tags
{'a': {}}
>>> req.varList
[]

+++++++++++++++++++
(?#<TAG a href>)
****
(?#<TAG a href>)
{'a': {'href': ''}}
[]

+++++++++++++++++++
(?#<TAG a *>)
****
(?#<TAG a *>)
{'a': {'*': ''}}
[]


+++++++++++++++++++
(?#<TAG a href=url>)
****
(?#<TAG a href=url>)
{'a': {'href': ''}}
[['a.href', 'url']]

+++++++++++++++++++
(?#<TAG a href="/">)
****
(?#<TAG a href="/">)
{'a': {'href': <_sre.SRE_Pattern object at 0x03631CB8>}}
[]
a {'href': '/\\Z'}

"""

def ExtCompile(regexPattern, compFlags):
    """
    tr : TAG buscado
    td.width : Atributo "width" buscado en td
    td.div.class="playlist_thumb" : Atributo class de td.div con valor playlist_thumb 
    td.div.a.img.src=icon : Atributo "src" buscado y almacenado en variable "icon".  td.div.a.img = td..img
    td[2].div[2].*=hist : td[2] = Segundo tag td hijo de tr, td[2].div[2] = Segundo tag div de td[2], * = comentario
    td..a.href=url : td..a  es notación compacta de td.div.a
    
    >>> req = compile(r'(?#<TAG tr td.width div.class="playlist_thumb" td.div.a.img.src=icon td[2].div[2].*=hist td..a.href=url>)', 0)
    >>> req.tags.keys()
    ['tr.td[2].div[2]', 'tr.div', 'tr.td', 'tr', 'tr.td.div.a.img', 'tr.td..a']
    >>> req.varList
    [['tr.td.div.a.img.src', 'icon'], ['tr.td[2].div[2].*', 'hist'], ['tr.td..a.href', 'url']]
    
    >>> equis = compile('(?#<TAG ese a.*="http//esto/es/prueba"=icon href=url>)', 0)
    >>> equis.varList
    [['ese.a.*', 'icon'], ['ese.href', 'url']]
    >>> for tag in equis.tags:
    ...    print tag, [(key, equis.tags[tag][key].pattern) for key in equis.tags[tag] if equis.tags[tag][key]]
    ... 
    ese []
    ese.a [('*', 'http//esto/es/prueba\\\\Z')]
    
    >>> equis = compile('(?#<TAG a href span.src=icon span.*=label div.id>)',0)
    >>> equis.tags
    {'a': {'href': ''}, 'a.div': {'id': ''}, 'a.span': {'src': '', '*': ''}}
    >>> equis = compile('(?#<TAG a href span{src=icon *=label} div.id>)',0)
    >>> equis.tags
    {'a': {'href': ''}, 'a.div': {'id': ''}, 'a.span': {'src': '', '*': ''}}
    >>> equis = compile('(?#<TAG a href span{src=icon *=label div.id>}',0)
    Traceback (most recent call last):
      File "C:\Python27\lib\doctest.py", line 1315, in __run
        compileflags, 1) in test.globs
      File "<doctest __main__.compile[10]>", line 1, in <module>
        equis = compile('(?#<TAG a href span(src=icon *=label div.id>)',0)
      File "C:\\Users\\Alex Montes Barrios\\git\\addonDevelopment\\xbmc addon development\\src\\xbmcUI\\CustomRegEx.py", line 534, in compile
        raise re.error(v)
    error: unbalanced parenthesis
    
    """
    def storeAttrVarPair(varName, attrName):
        if attrName in attrSet:
            v = 'reassigment of attribute '+ attrName + ' to var ' + varName + '; was var ' + attrSet[attrName] 
            raise re.error(v)
        if varName in varSet:
            v = 'redefinition of group name '+ varName + ' as group ' + str(len(varList) + 1) + '; was group ' + str(varSet[varName])
            raise re.error(v)
        varList.append([attrName, varName])
        attrSet[attrName] = varName
        varSet[varName] = len(varList)
        pass
    
#     match = re.search('\(\?#<(?P<tagpattern>[a-zA-Z][a-zA-Z\d]*)(?P<vars>[^>]*>)\)',regexPattern)
    match = re.search('\(\?#<(?P<tagpattern>[a-zA-Z]\S*|_TAG_)(?P<vars>[^>]*>)\)',regexPattern)
    if not match: return re.compile(regexPattern, compFlags)
    
    ATTR        = r'(?P<ATTR>(?<=[{ ])\(*[a-z\d\*\.\[\]_-]+\)*(?==))'
    REQATTR     = r'(?P<REQATTR>(?<=[{ ])\(*[a-z\d\*\.\[\]_-]+\)*(?=[ >\)]))'
    VAR         = r'(?P<VAR>(?<==)[a-zA-Z][a-zA-Z\d]*(?=[ >}]))'
    STRPVAR     = r'(?P<STRPVAR>(?<==)&[a-zA-Z][a-zA-Z\d]*&(?=[ >}]))'
    PARAM       = r'(?P<PARAM>(?<==)[\'\"][^\'\"]+[\'\"](?=[ >=]))'
    TAGSUFFIX   = r'(?P<TAGSUFFIX>(?<=[ {])[a-z\d\*\.\[\]]+(?={))'
    OPENP       = r'(?P<OPENP>{)'
    CLOSEP      = r'(?P<CLOSEP>})'
    EQ          = r'(?P<EQ>=)'
    WS          = r'(?P<WS>\s+)'
    END         = r'(?P<END>>)'
    
    tagPattern = match.group('tagpattern')
    if tagPattern == '_TAG_': tagPattern = '[a-zA-Z][^\s>]*'
    rootTag = "tagpholder"
    rootTagStck = [rootTag]
    master_pat = re.compile('|'.join([TAGSUFFIX, ATTR, REQATTR, VAR, STRPVAR, PARAM, OPENP, CLOSEP, EQ, WS, END]))
    scanner = master_pat.scanner(match.group('vars'))
    totLen = 0
    varSet={}
    attrSet = {}
    tags = {rootTag:{}}
    varList = []
    for m in iter(scanner.match, None):
        sGroup = m.group()
        totLen += len(sGroup) 
#         print m.lastgroup, m.group()
        if m.lastgroup in ["ATTR", "REQATTR"]:
            if sGroup[0] == "(" and sGroup[-1] == ")":
                sGroup = sGroup[1:-1]
                varName = "group" + str(1 + len(varList))
#                 varList.append([, varName])
                attrName = rootTag + ATTRSEP + sGroup
                storeAttrVarPair(varName, attrName)
                pass
            elif (sGroup[0] == "(" and sGroup[-1] != ")") or (sGroup[0] != "(" and sGroup[-1] == ")"):
                v = 'unbalanced parenthesis'
                raise re.error(v)
            pathKey, sep, attrKey = sGroup.rpartition(ATTRSEP)
            pathKey = rootTag + ATTRSEP + pathKey if pathKey else rootTag
            tags.setdefault(pathKey, {})
            sGroup = ""
            
        if m.lastgroup in ["ATTR", "WS", "EQ", 'END']: continue

        if m.lastgroup == "TAGSUFFIX":
            pathKey = sGroup
            continue

        if m.lastgroup == "OPENP":
            rootTagStck.append(pathKey)
            rootTag = '.'.join(rootTagStck)
            continue

        if m.lastgroup == "CLOSEP": 
            rootTagStck.pop()
            rootTag = '.'.join(rootTagStck)
            continue
        
        if m.lastgroup in ["VAR", "STRPVAR"]:
            varName = sGroup if m.lastgroup == "VAR" else sGroup[1:-1]
            attrName = pathKey + ATTRSEP + attrKey
            storeAttrVarPair(varName, attrName)
            sGroup = "" if m.lastgroup == "VAR" else " \s*([ \S]*?)\s* "
        tagDict = tags[pathKey]
        if attrKey in tagDict and m.lastgroup != "VAR":
            v = 'reasociation of attribute '+ pathKey + ATTRSEP + attrKey 
            raise re.error(v)
        tagDict.setdefault(attrKey, '')
        if sGroup: tagDict[attrKey] = re.compile(sGroup[1:-1] + r'\Z')

    if totLen == len(match.group('vars')) and len(rootTagStck) > 1:
        v = 'unbalanced parenthesis'
        raise re.error(v)
        
    if totLen != len(match.group('vars')): 
        v = 'unable to process pattern from: ' + match.group('vars')[totLen:]
        raise re.error(v)
#     print '****'
#     print regexPattern
#     print tags
#     print varList
#     for tag in tags:
#         if not any(tags[tag].values()):continue
#         print tag, dict((key, value.pattern) for key, value in tags[tag].items() if value)
    return ExtRegexObject(regexPattern, compFlags, tagPattern, tags, varList)

class zinwrapper(ExtRegexObject):
    def __init__(self, pattern, compflags, spanRegexObj, srchRegexObj):
        try:
            tagPattern, tags, varList = srchRegexObj.tagPattern, srchRegexObj.tags, srchRegexObj.varList
        except:
            tagPattern, tags, varList = "", {}, []

        ExtRegexObject.__init__(self, pattern, compflags,tagPattern, tags, varList) 
        self.spanRegexObj = spanRegexObj
        self.srchRegexObj = srchRegexObj
        self.spanDelim = None
        self.matchParams = None 
        pass
    
    def findSpan(self, string, posIni, posFin):
        offset = posIni
        if isinstance(self.spanRegexObj, ExtRegexObject):
            string = string[posIni:posFin]
            posIni = offset + re.match(GENTAG, string).end()
            posFin = offset + re.search(ENDTAG+'\Z', string).start()
            return posIni, posFin
        else:
            return match.span()

    def delimiter(self, string, pos, endpos):
        if endpos == -1: endpos = len(string)
        if self.spanDelim == None:
            srchFunc = getattr(self.spanRegexObj, 'search')
            match = srchFunc(string, pos, endpos)
            if not match: return None
            self.spanDelim = self.findSpan(string, *match.span())
            self.matchParams = match.groupdict()
            return self.spanDelim
        limInf, limSup = self.spanDelim
        if limInf <= pos < limSup:
            return pos, min(limSup, endpos)
        self.spanDelim = None
        return self.delimiter(string, pos, endpos)

    def search(self, string, pos = 0, endpos = -1):
        spanDelim = self.delimiter(string, pos, endpos)
        if not spanDelim: return None
        posIni, posFin = spanDelim
        srchFunc = getattr(self.srchRegexObj, 'search')
        match = srchFunc(string, posIni, posFin)
        if match: return match
        self.spanDelim = None
        return self.search(string, posFin, endpos) 
    
#     def match(self, string, pos = 0, endpos = -1):
#         pass
#     
#     def findall(self, string, pos = 0, endpos = -1):
#         pass
#     
#     def finditer(self, string, pos = 0, endpos = -1):
#         pass
#     
#     def __getattr__(self, attrname):
#         return getattr(self.srchRegexObj, attrname)
    



def compile(regexPattern, compFlags):  
    spanRegexObj, srchRegexObj = regexPattern.rpartition('<ZIN>')[0:3:2]
    srchRegexObj = ExtCompile(srchRegexObj, compFlags)
    if not spanRegexObj: return srchRegexObj
    spanRegexObj = ExtCompile(spanRegexObj, compFlags)
    return zinwrapper(regexPattern, compFlags, spanRegexObj, srchRegexObj)
    




class ExtRegexParser:
    def __init__(self, varList, reqTags):
        self.TAGPATT = r'<(?P<TAG>[a-zA-Z\d]+)(?P<ATTR>[^>]*)(?:>|/>)'
        self.ATTR_PARAM = r'(?P<ATTR>(?<=\W)[^\s]+(?==))=([\"\'])(?P<PARAM>(?<==[\"\']).*?)\2(?=[\W>])'
        self.master_pat = re.compile('|'.join([GENSELFTAG, GENTAG, ENDTAG, BLANKTEXT, GENTEXT, DOCSTR, SUFFIX]))
        
        self.reqTags = dict(reqTags)
        self.varDict = {}
        for k, tagTple in enumerate(varList):
            key = tagTple[0]
            self.varDict[key] = k + 1
        self.varPos = (len(varList) + 1) * [0]
        
        self.totLen = 0
        pass
    
    def checkStartTag(self, data):
        tag = re.match(r'<([a-zA-Z\d]+)[\W >]', data).group(1)
#         if tag not in self.reqTags:return True
        if 'tagpholder' not in self.reqTags:return True
        reqTags = dict(self.reqTags['tagpholder'])
        if '*' in reqTags: reqTags.pop('*')
        tagAttr = self.getAttrDict(data, 0)
        return self.haveTagAllAttrReq('tagpholder', tagAttr, reqTags)

    def initParse(self, data, posIni):
        if not self.checkStartTag(data): return None
        tagList = self.feed(data)
        if not tagList: return None
        reqSet = set(self.reqTags.keys())        
        toProcess = self.setPathTag(tagList, reqSet = reqSet)
        if reqSet: return None

        self.varPos[0] = tagList[0][0]
        for k in toProcess:
            tag = tagList[k][1]
            tagAttr = self.getAllTagData(k, data, tagList)
            if not self.haveTagAllAttrReq(tag, tagAttr): return None
            self.storeReqVars(tag, tagAttr, self.reqTags[tag])
        return [self.trnCoord(elem, posIni) for elem in self.varPos]
        pass
    
    def htmlStruct(self, data, posIni):
        tagName = re.match(r'<([a-zA-Z\d]+)[\W >]', data).group(1)
        tagList = self.feed(data)
        self.setPathTag(tagList, rootName = tagName)
        answer = []
        for elem in tagList:
            tagPos, tagId = elem[:2]
            pos, endpos = tagPos
            if tagId[-1] != "*":
                endpos = data.find(">", pos) + 1
            answer.append((tagId, re.sub("[\t\n\r\f\v]", "", data[pos:endpos])))
        return answer
    
    def storeReqVars(self, tag, tagAttr, reqAttr):
        interSet = set(reqAttr.keys()).intersection(tagAttr.keys())
        if interSet: 
            paramPos = tagAttr.pop('*ParamPos*')
            for attr in interSet:
                fullAttr = tag + '.' + attr
                if fullAttr in self.varDict:
                    k = self.varDict[fullAttr]
                    if reqAttr[attr] and reqAttr[attr].groups:
                        m = reqAttr[attr].match(tagAttr[attr])
                        self.varPos[k] = self.trnCoord(m.span(1), paramPos[attr][0])
                    else:
                        self.varPos[k] = paramPos[attr]
        

    def haveTagAllAttrReq(self, tag, tagAttr, reqTags = -1):
        if reqTags == -1: reqTags = self.reqTags[tag]
        diffSet = set(reqTags.keys()).difference(tagAttr.keys())
        interSet = set(reqTags.keys()).intersection(tagAttr.keys())
        bFlag = diffSet or not all([reqTags[key].match(tagAttr[key]) for key in interSet if reqTags[key]])
        return not bFlag
    
    def getAllTagData(self, tagPos, data, tagList):
        posBeg, posEnd = tagList[tagPos][0]
        tagAttr = self.getAttrDict(data[posBeg:posEnd], posBeg)
        if tagList[tagPos][2]:
            n = tagList[tagPos][2]
            posBeg, posEnd = tagList[n][0]
            tagAttr['*'] = data[posBeg:posEnd]
            tagAttr['*ParamPos*']['*'] = tagList[n][0]
        return tagAttr
    
    def setPathTag(self, tagList, rootName = 'tagpholder', reqSet = -1):
        dadList = [-1]
        no_reqSetFlag = reqSet == -1
        for k in xrange(len(tagList) - 1):
            indx = k + 1
            while 1:
                if tagList[indx][0][1] < tagList[k][0][1]:
                    dadList.append(k)
                    if tagList[indx][1] == '*':tagList[k][2] = indx
                    break
                k = dadList[k]
                    
        packPath = lambda x, n:tagList[0][1] + '.' + '..'.join(x.partition('.')[2].split('.')[0:n:n-1])
        pathDict = {}
        toProcess = []
        tagList[0][1] = rootName
        if not no_reqSetFlag:
            if tagList[0][1] in reqSet:toProcess.append(0)
            reqSet.difference_update([tagList[0][1]])
            relPath = sorted([x for x in reqSet if x.find('..') != -1], cmp = lambda x,y: y.count('.') - x.count('.')) 
            efe = lambda x: not (pathTag.startswith(x.split('..')[0]) and pathTag.endswith(x.split('..')[1]))
            
        for k in xrange(1,len(tagList)):
            indx = dadList[k]
            pathTag = tagList[indx][1] + '.' + tagList[k][1]
            pathDict[pathTag] = pathDict.get(pathTag, 0) + 1
            if pathDict[pathTag] > 1: pathTag += '[' + str(pathDict[pathTag]) + ']'
            tagList[k][1] = pathTag
            if no_reqSetFlag:continue
#             packedPath = pathTag if pathTag.count('.') < 3 else packPath(pathTag, pathTag.count('.'))
            if pathTag in reqSet:
                reqSet.difference_update([pathTag])
                toProcess.append(k)
            elif relPath:
                rpos = list(itertools.takewhile(efe, relPath))
                rpos = len(rpos) + 1
                if rpos <= len(relPath):
                    toProcess.append((k, relPath[rpos - 1]))
                    reqSet.difference_update([relPath.pop(rpos - 1)])
            if not reqSet: break
        if no_reqSetFlag: return None
        for k in range(len(toProcess)):
            m = toProcess[k]
            if isinstance(m, int):continue
            toProcess[k] = m[0]
            tagList[m[0]][1] = m[1]
        return toProcess
    
    def getAttrDict(self, data, offset):
        """
        Recibe    : '<tag parameters>' o <tag parameters/>
        Entrega   : Dictionary con parameters value and en *ParamPos* diccionario de posiciones
         
        """
        match = re.match(r'<[a-zA-Z\d]+(.+?)[/]*>', data, re.DOTALL)
        if not match: return {'*ParamPos*':{}}
        offset += match.start(1) - 1
        data = ' ' + match.group(1) + ' '
        mgList = list(re.finditer(self.ATTR_PARAM, data, re.DOTALL)) 
        mgDict = dict((mg.group("ATTR"), mg.group("PARAM")) for mg in mgList)
        mgDict['*ParamPos*'] = dict((mg.group("ATTR"), self.trnCoord(mg.span("PARAM"), offset)) for mg in mgList)
        return mgDict

    def trnCoord(self, tupleIn, offset):
        return (tupleIn[0] + offset, tupleIn[1] + offset)

    def getTag(self, data):
        match = re.match(self.TAGPATT, data)
        return match.group('TAG') 
        pass

    def feed(self, data):
        tag = re.match(r'<([a-zA-Z\d]+).+?(>|/>)', data, re.DOTALL)
        if tag.group(2) == '>':
            pattern = '</' + tag.group(1) + '>'
            if not re.search(pattern, data): data = tag.group()
        scanner = self.master_pat.scanner(data)
        totLen = 0
        tagStack = []
        tagList = []
        stackPath = ''
        for m in iter(scanner.match, None):
            totLen += len(m.group())
            if m.lastgroup in ["GENSELFTAG", "GENTAG"]:
                tag = self.getTag(m.group())
                stackPath += '.' + tag 
                if m.lastgroup == "GENTAG" :
                    tagStack.append([tag, m.span()])
                else: 
                    tagList.append([m.span(), tag, None])
                    if not tagStack: return sorted(tagList)
                continue
            
            if m.lastgroup == "ENDTAG":
                tag = m.group()[2:-1]
                rootTag, sep = stackPath.rpartition('.' + tag)[:2]
                if sep:
                    stackPath = rootTag
                    while 1:
                        stckTag, stckTagSpan = tagStack.pop()
                        bFlag = tag == stckTag
                        if bFlag:
                            tagSpan = (stckTagSpan[0], m.end())
                        else:
                            tagSpan = stckTagSpan 
                        tagList.append([tagSpan, stckTag, None])
                        if bFlag: break
                    if not tagStack: return sorted(tagList)
                    continue

            if m.lastgroup == "GENTEXT":
                tagList.append([m.span(), '*', None])
                continue
            
            if m.lastgroup == "DOCSTR": 
                continue
                pass
            
            if m.lastgroup in ["BLANKTEXT", "SUFFIX"]:
                continue
                pass
        if totLen != len(data): raise Exception
        if tagStack:
            stckTag, stckTagSpan = tagStack[0]
            tagList = [[stckTagSpan, stckTag, None]]
        return tagList
        pass

    
if __name__ == "__main__":

    
#     testStr = ['<uno><dos><!--Comentario en <dos>--></dos><script f="uno">script en <uno></script></uno>', 
#                '<!--Comentario al inicio --><uno><dos><!--Comentario en el medio--></dos></uno><!--Comentario al final -->']
#     
#     for elem in testStr:
#         equis = filteredStr(elem)
#         print equis
# 
#     pattern = r'<dos>.*?</dos>'
#     match = re.search(pattern, testStr[0])
#     print 'original', match.start(), match.end(), match.group()
#     
#     equis = filteredStr(testStr[0])    #Aca debo resolver el problema que no ve silteredStr como una str
#     print 'start', equis.start
#     print 'end', equis.end
#     print 'base', equis.base
#     
#     print len(str(equis)), equis
#     match = re.search(pattern, str(equis))
#     print 'filtered', match.start(), match.end(), match.group()
#     print 'filterToOrig', match.start(), match.end(), equis.trnsSlice(match.start(), match.end())

#     with open(r'c:/fileTest/htmlRegexTest.txt', 'r') as origF:
#         ese = origF.read()
# 
#     equis = filteredStr(ese)
#     print 'start', equis.start
#     print 'end', equis.end
#     print 'base', equis.base
# 
#     with open(r'c:/fileTest/htmlRegexMod.txt', 'w') as origF:
#         origF.write(str(equis))

#     with open(r'c:/fileTest/htmlRegexMod.txt', 'r') as origF:
#
#     filteredEquis = filteredStr(equis)
#     print 'mod = 5649', filteredEquis.deTrnsSlice(5649, 5649)
#     print 'real = 10288', filteredEquis.transSlice(10288, 10288)


#     salida = ''
#     testHtmlPattern(equis,0)

#     compile('(?#<TAG table ID="2345" clase ref=url a.title=label>)', 0)
#     compile("(?#<TAG table ID='2345' clase ref=url a.title=label>)", 0)

#     modEquis = filteredStr(equis)
#     filteredEquis = str(modEquis)
# 
#     with open(r'c:/fileTest/NEWhtmlRegexMod.txt', 'w') as origF:
#         origF.write(str(filteredEquis))
    
#     with open(r'c:/fileTest/htmlRegexTest.txt', 'r') as origF:
#         equis = origF.read()
#     
#     import pprint
#     reg = compile('(?#<TAG tr td.a.href=url td.a.*=label td[3].*=when td[4].*=quality>)', 0)
#     ese = reg.findall(equis)
#     pprint.pprint(ese)
#     print len(ese)
# 

# 
#     with open(r'c:/fileTest/extRegExTest.txt', 'r') as origF:
#         equis = origF.read()
#     reg = compile(r'(?#<TAG li a.title=label a.href=url>)',0)
#     ese = reg.findall(equis)
#     print len(ese)




#     reg = compile('(?#<TAG a href=url target="_blank" *=label>)', 0)
#     match = reg.search(equis)
#     print match.groupdict()
#  
#     reg = compile('(?#<TAG td align="center" a.href=url a.style=label>)', 0)
#     print match.group()
#     print match.start(), match.end()
#     print match.span()
#      
#     print match.group('url')
#     print match.start('url'), match.end('url')
#     print match.span('url')
#     ese = reg.findall(equis)
#     print ese
#     print len(ese)
#     
#     
#     
#     
# #     for tag in ["uno", "uno.dos", "uno.dos[2]", "uno.dos[2].tres[6]"]:
# #         print tag, findPredecesor(tag)
# #         
# #     tag = "uno.dos[2].tres[6]"
# #     print '*****'
# #     while tag:
# #         print tag
# #         tag = findPredecesor(tag)
#     
#     
#   

    print '******* BEG ********' 
    testing = "<ZIN>"

    if testing == "<ZIN>":
        with open(r'c:/fileTest/extRegExTest.txt', 'r') as origF:
            equis = origF.read()
            
#         testPattern = compile('(?#<ul class="links">)<ZIN>(?#<a title=label href=url>)', 0)
        testPattern = compile('<ul class="links">.+?</ul><ZIN><a title="(?P<label>[^"]+)" href="(?P<url>[^"]+)">.+?</a>', re.DOTALL)
#         testPattern = compile('<ul class="links">.+?</ul><ZIN>(?#<a title=label href=url>)', re.DOTALL)                                
        pos = 0
        for k in range(59):        
            match = testPattern.search(equis, pos)
            print match.group()
            print match.groupdict()
            print match.span()
            pos = match.end()
        match = testPattern.search(equis, pos)
        print match.group()
        print match.groupdict()
        print match.span()

        pos = 0
        testPattern = compile('(?#<div class="tagindex" h4.*="A">)<ZIN><a title="(?P<label>[^"]+)" href="(?P<url>[^"]+)">.+?</a>', re.DOTALL)
        print '****   finditer   ****'
        for match in testPattern.finditer(equis, pos):
            print match.group()
            
        pos = 0
        import pprint
        pprint.pprint(testPattern.findall(equis, pos))

    if testing == "doctest":
        import doctest
        doctest.testmod(verbose=True)

    if testing == "regexparser":
        setupStrTest ="""
import CustomRegEx
with open(r'c:/fileTest/extRegExTest.txt', 'r') as origF:
    equis = origF.read()

reqTags = {'li': {}, 'li.a': {'title':'', 'href':''}}
varList = [('li.a.title', 'label'), ('li.a.href', 'url')]
dmy = CustomRegEx.ExtRegexParser(varList, reqTags)
ene = 0
"""
        execStr = """
varPos = dmy.initParse(equis[7958:], 7958)
posIni, posFin = varPos[1]
ene += 1
print '***', ene, '***   ', equis[7958:][posIni:posFin]
"""

#         import timeit
#         t = timeit.Timer(execStr, setupStrTest)
#         print t.repeat(3,2582)

        with open(r'c:/fileTest/extRegExTest.txt', 'r') as origF:
            equis = origF.read()
            
        reqTags = {'li': {}, 'li.a': {'title':'', 'href':''}}
        varList = [('li.a.title', 'label'), ('li.a.href', 'url')]
        dmy = ExtRegexParser(varList, reqTags)
        varPos = dmy.initParse(equis[7958:], 7958)
        for posIni, posFin in varPos:
            print equis[7958:][posIni:posFin]
    
#         with open(r'c:/fileTest/NEWhtmlRegexMod.txt', 'r') as origF:
#             equis = origF.read()
#          
#         reqTags = {'tr.td.a': {'target':re.compile('_blank' + r'\Z'), '*':'' }, 'tr.td.img': {'src':''}, 'tr.td[3]':{'*':''}, 'tr.td[4]':{'*':''} }
#         varList = [('tr.td.a.*', 'resolver'), ('tr.td.img.src', 'icon'), ('tr.td[3].*', 'when'), ('tr.td[4].*', 'who') ]
#      
#         dmy = newRegexParser(reqTags, varList)
#         varPos = dmy.initParse(equis[5059:], 5059)
#         for posIni, posFin in varPos:
#             print equis[5059:][posIni:posFin]



    
    if testing == "TIMETEST":
        setupStrBase ="""
import re
case = 'Base re'
with open(r'c:/fileTest/extRegExTest.txt', 'r') as origF:
    equis = origF.read()
reg = re.compile(r'<li><a title="(?P<label>[^"]+)" href="(?P<url>[^"]+)">')
"""
        setupStrTest ="""
import CustomRegEx
case = 'CustomRegEx'
with open(r'c:/fileTest/extRegExTest.txt', 'r') as origF:
    equis = origF.read()
reg = CustomRegEx.compile(r'(?#<TAG li a.title=label a.href=url>)',0)
"""
        execStr = """
answer = []
nPos = 0
while 1:
    match = reg.search(equis,nPos)
    if not match:break
    answer.append(match)
    nPos = match.end()
    #print equis[match.start(1):match.end(1)]
print '***', len(answer)
"""
        import timeit
        testResults = [['CustomRegEx '], 
                       ['Base Case re'],
                       ['Cociente    ']]

        t = timeit.Timer(execStr, setupStrBase)
        testResults[1].extend(t.repeat(10,2))

        print '****'

        t = timeit.Timer(execStr, setupStrTest)
        testResults[0].extend(t.repeat(10,2))
        
        testResults[2].extend([testResults[0][k]/testResults[1][k] for k in range(1,len(testResults[0]))])
        
        for k in range(len(testResults)):
            print testResults[k]

        """
['Base Case re', 0.017796395910653448, 0.06384938588563631, 0.006653778622702056]
['CustomRegEx' , 4.617611456204629,    4.556558026229592,   4.550929028689399]
['RegexParser',  1.5810683341039153,   1.3093148011828322,  1.2611394744304092]
['myHtmlParser', 0.5135678556911564,   0.48400788368354086, 0.5097856710838946]
"""

        """
['CustomRegEx', 3.990230601934045, 3.7897863415601707, 3.792617916522909]
[0.7224969933329516, 0.48941115421094017, 0.5274976987298665]
[1.8069470421520055, 1.378646867129761, 1.3666685989420442]
['CustomRegEx', 0.7102466933646595, 0.13496191555071946, 0.04810506642604018]
"""

    print '******* END ********'
