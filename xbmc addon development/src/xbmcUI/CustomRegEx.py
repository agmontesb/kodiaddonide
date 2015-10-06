# -*- coding: utf-8 -*-
'''
Created on 19/09/2015

@author: Alex Montes Barrios
'''
import re
from collections import namedtuple
from timeit import template
from operator import pos
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
    def __init__(self, pattern, compflags, tags, varList):
        self.pattern = pattern
        self.flags = compflags
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
        findTag = ExtRegexParser(self.tags, self.varList)
        rootTag = self.tags.keys()[0].partition('.')[0]
        diffSet = set(self.tags.get(rootTag,{}).keys()).difference(['*'])
        if diffSet:
            SRCHTAG =  r'(?P<SRCHTAG><{0} [^>]*{1}=[^>]+>)'.format(rootTag, diffSet.pop())
        else:
            SRCHTAG = r'(?P<SRCHTAG><{0}(?:>| [^>]+>))'.format(rootTag)
        COMMENT = r'(?P<COMMENT><!--.+?-->)'
        GENTAG  = r'(?P<GENTAG>[\W]*<.+?(?=<{0}|<!--))'.format(rootTag)
        BLANKTEXT = r'(?P<BLANKTEXT>(?<=>)\W+(?=<))'
        LEFTOVER = r'(?P<LEFTOVER>.+?</html>.+?)'
        
        master_pat = re.compile('|'.join([BLANKTEXT, COMMENT, SRCHTAG, GENTAG, LEFTOVER]), re.DOTALL)
        posIni = origString.find('<', pos)
        while 1:
            scanner = master_pat.scanner(origString[posIni:])
            for m in iter(scanner.match, None):
                if m.lastgroup == 'SRCHTAG': break
            if not m or m.lastgroup != 'SRCHTAG': return None
            tagPos = m.start() + posIni
            varPos = findTag.initParse(origString[tagPos:], tagPos)
            if varPos: break
            posIni = origString.find('<', m.end() + posIni)
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



class ExtRegexObjectOLD:
    def __init__(self, pattern, compflags, tags, varList):
        self.pattern = pattern
        self.flags = compflags
        self.tags = tags
        self.groupindex = {}
        for k, varTuple in enumerate(varList):
            self.groupindex[varTuple[1]] = k + 1
        self.varList = dict(varList)
        self.groups = len(varList)
        pass
    
    def htmlLex(self, string, tag, addComment = False):
        SRCHTAG = r'(?P<SRCHTAG><{0}[^>]*>)'.format(tag)
        SRCHSELFTAG = r'(?P<SRCHSELFTAG><{0}[^>]*/>)'.format(tag)
        SRCHEND = r'(?P<SRCHEND></{0}>)'.format(tag)
        master_pat = re.compile('|'.join([SRCHSELFTAG, SRCHTAG, GENSELFTAG, GENTAG, BLANKTEXT, GENTEXT, SRCHEND, ENDTAG, DOCSTR, SUFFIX]))
        
        bFlag = False
        answer = []
        stack = []
        lstPop = None
        scanner = master_pat.scanner(string)
        for m in iter(scanner.match, None):
            if m.lastgroup == 'SRCHSELFTAG':
                lstPop = m
                break
            if bFlag and m.lastgroup == 'GENTEXT':
                answer.append([m.group(), m.span()])
            if m.lastgroup not in ['SRCHTAG', 'SRCHEND']: continue
            if m.lastgroup == 'SRCHTAG':
                if not stack: bFlag = addComment
                stack.append(m)
            if m.lastgroup == 'SRCHEND':
                lstPop = stack.pop()
            if not stack: break
        
        if m and lstPop: 
            answer.insert(0, [tag, (lstPop.start(), m.end()), (lstPop.end(), m.start())])            
            return answer
        elif not lstPop and m:
            answer.insert(0, [tag, (m.start(), m.end()), (0, 0)])
        elif not lstPop and not m and stack[0]:
            answer.insert(0, [tag, (stack[0].start(), stack[0].end()), (0, 0)])
        else: 
            answer = None
        return answer

    def findTag(self, string, tag, reqAttr, offset):
        transCoord = lambda x: (offset + x[0], offset + x[1])
        diffSet = set(reqAttr.keys()).difference(['*'])
#         fmtStr = r'<{0}(?P<ATTR>(?:>| [^>]+>))' if not diffSet else r'<{0}(?P<ATTR> [^>]+>)'
#         tagRegex = fmtStr.format(tag)
        if diffSet:
            tagRegex =  r'<{0}(?P<ATTR> [^>]*{1}=[^>]+>)'.format(tag, diffSet.pop())
        else:
            tagRegex = r'<{0}(?P<ATTR>(?:>| [^>]+>))'.format(tag)

#         print '*** *** ***'
#         print tagRegex
#         print string[:40]
        reg = re.compile(tagRegex, re.DOTALL)
        posIni = 0 
        while 1:
            match  = reg.search(string, posIni)
#             print 'match', match
            if not match: return None
#             ATTR_PARAM = r'(?P<ATTR>(?<= )[^\s]+(?==))=(?P<PARAM>(?<==)\".+?\"(?=[ >]))'  
            ATTR_PARAM = r'(?P<ATTR>(?<= )[^\s]+(?==))=([\"\'])(?P<PARAM>(?<==[\"\']).*?)\2(?=[ >])'
            mgDict = dict((mg.group("ATTR"), mg) for mg in list(re.finditer(ATTR_PARAM, match.group("ATTR"))))
#             print match.group("ATTR")
#             print list(re.finditer(ATTR_PARAM, match.group("ATTR")))
#             print mgDict
            diffSet = set(reqAttr.keys()).difference(mgDict.keys())
            interSet = set(reqAttr.keys()).intersection(mgDict.keys())
#             if diffSet.issubset(['*']) and all([reqAttr[key] == mgDict[key].group("PARAM") for key in interSet if reqAttr[key]]):
            if diffSet.issubset(['*']) and all([reqAttr[key].match(mgDict[key].group("PARAM")) for key in interSet if reqAttr[key]]):
                commFlag = '*' in diffSet
                result = self.htmlLex(string[match.start():], tag, commFlag)
                if not commFlag: break
                if commFlag and len(result) == 2:
                    if not reqAttr['*'] or reqAttr['*'].match(result[1][0]):
                        result[1][0] = '*'
                        break
            posIni = match.end()                
        if not result: return None
        offset += match.start()
        toReturn = [(result[0][0], (transCoord(result[0][1]), transCoord(result[0][2])))]
        if commFlag: toReturn.append((result[1][0], transCoord(result[1][1])))
        offset += match.start('ATTR') - match.start()
        for key in mgDict:
            toReturn.append((key, transCoord(mgDict[key].span("PARAM"))))
        return toReturn
        pass
    
    def search(self, origString, spos = -1, sendpos = -1):
        def findPredecesor(tag, parent = False):
            sep = "[" if not parent and tag[-1] == "]" else ATTRSEP
            rootTag, num = tag[:-1].rpartition(sep)[0:3:2]
            if sep == "[" and int(num) > 2: rootTag += "[" + str(int(num) - 1) + "]"
            return rootTag
        
        def getBoundary(tag):
            parent = findPredecesor(tag, parent = True)
            if not parent: return None
            posIni, posFin = tagBoundary[parent][1]
            if tag[-1] == "]":
                predecesor = findPredecesor(tag)
                posIni = tagBoundary[predecesor][0][1]
            return posIni, posFin                
            
        pos = spos if spos != -1 else 0
        endpos = sendpos if sendpos != -1 else len(origString)

        modString = filteredStr(origString)
        pos, endpos = modString.transSlice(pos, endpos)
        string = modString.__str__()
        varPos = []
        pathTagsCollection = sorted(self.tags.keys())
        ene = len(pathTagsCollection)
        for tag in pathTagsCollection[:ene]:
            while 1:
                tag = findPredecesor(tag)
                if not tag or tag in pathTagsCollection: break
                pathTagsCollection.append(tag)
        pathTagsCollection.sort()
        rootTag = pathTagsCollection[0]
        cycleFlag = True
        while 1:
            varPos = []            
            tagBoundary = {}
            for pathtag in pathTagsCollection:
                posIni, posFin = getBoundary(pathtag) or (pos, endpos)
                tag = pathtag.rpartition(ATTRSEP)[2].partition("[")[0]
                reqAttr = self.tags.get(pathtag, {})
#                 print '***' + pathtag + '***'
#                 print   string[posIni:posIni + 80]
                attrPos = self.findTag(string[posIni:posFin], tag, reqAttr, posIni)
                if pathtag == rootTag and not attrPos: return None
                cycleFlag = not attrPos
                if cycleFlag: break
                tagBoundary[pathtag] = attrPos.pop(0)[1]
                for attr, pos in [elem for elem in attrPos if (pathtag + ATTRSEP + elem[0]) in self.varList]:
                    var = self.varList[pathtag + ATTRSEP + attr]
                    varPos.append((self.groupindex[var], pos))
            if not cycleFlag: break
            pos = tagBoundary[rootTag][0][1]
        varPos.insert(0, (0, tagBoundary[rootTag][0]))
        varPos = [modString.deTrnsSlice(*elem[1]) for elem in sorted(varPos)]
        return ExtMatchObject(self, modString.htmlString, spos, sendpos, varPos)
    
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

def compile(regexPattern, compFlags):
    """
    tr : TAG buscado
    td.width : Atributo "width" buscado en td
    td.div.class="playlist_thumb" : Atributo class de td.div con valor playlist_thumb 
    td.div.a.img.src=icon : Atributo "src" buscado y almacenado en variable "icon".  td.div.a.img = td..img
    td[2].div[2].*=hist : td[2] = Segundo tag td hijo de tr, td[2].div[2] = Segundo tag div de td[2], * = comentario
    td..a.href=url : td..a  es notación compacta de td.div.a
    
    >>> req = compile(r'(?#<TAG tr td.width div.class="playlist_thumb" td.div.a.img.src=icon td[2].div[2].*=hist td..a.href=url>)', 0)
    >>> req.varList
    [['tr.td.div.a.img.src', 'icon'], ['tr.td[2].div[2].*', 'hist'], ['tr.td..a.href', 'url']]
    >>> req.tags
    {'tr.td[2].div[2]': {'*': ''}, 'tr.div': {'class': <_sre.SRE_Pattern object at 0x024903C8>}, 'tr.td': {'width': ''}, 'tr': {}, 'tr.td.div.a.img': {'src': ''}, 'tr.td..a': {'href': ''}}
    """
    match = re.search('\(\?#<TAG (?P<tag>[a-zA-Z][a-zA-Z\d]*)(?P<vars>[^>]*>)\)',regexPattern)
    if not match: return re.compile(regexPattern, compFlags)
    
    ATTR = r'(?P<ATTR>(?<= )[^\s]+(?==))'
#     REQATTR = r'(?P<REQATTR>(?<= )(?:[a-zA-Z]|\*)[a-zA-Z\d]*(?=[ >]))'
    REQATTR = r'(?P<REQATTR>(?<= )[^\s]+(?=[ >]))'
    VAR = r'(?P<VAR>(?<==)[a-zA-Z][a-zA-Z\d]*(?=[ >]))'
    PARAM = r'(?P<PARAM>(?<==)[\'\"][^\'\"]+[\'\"](?=[ >]))'
    EQ = r'(?P<EQ>=)'
    WS = r'(?P<WS>\s+)'
    END = r'(?P<END>>)'
    
    
    rootTag = match.group('tag')
    master_pat = re.compile('|'.join([ATTR, REQATTR, VAR, PARAM, EQ, WS, END]))
    scanner = master_pat.scanner(match.group('vars'))
    totLen = 0
    tags = {rootTag:{}}
    varList = []
    for m in iter(scanner.match, None):
        sGroup = m.group()
        totLen += len(sGroup) 
#         print m.lastgroup, m.group()
        if m.lastgroup in ["ATTR", "REQATTR"]:
            pathKey, sep, attrKey = sGroup.rpartition(ATTRSEP)
            pathKey = rootTag + ATTRSEP + pathKey if pathKey else rootTag
            sGroup = ""
        if m.lastgroup in ["ATTR", "WS", "EQ", 'END']: continue
        if m.lastgroup == "VAR": 
            varList.append([pathKey + ATTRSEP + attrKey, sGroup])
            sGroup = ""
        tagDict = tags.setdefault(pathKey, {})
        tagDict.setdefault(attrKey, '')
        if sGroup: tagDict[attrKey] = re.compile(sGroup[1:-1] + r'\Z')
#         tagDict[attrKey] = sGroup[1:-1]

    if totLen != len(match.group('vars')): re.compile(r'(') # Eleva exepci�n, se puede mejorar
#     print '****'
#     print regexPattern
#     print tags
#     print varList
#     for tag in tags:
#         if not any(tags[tag].values()):continue
#         print tag, dict((key, value.pattern) for key, value in tags[tag].items() if value)
    return ExtRegexObject(regexPattern, compFlags, tags, varList)


class ExtRegexParser:
    def __init__(self, reqTags, varList):
        self.TAGPATT = r'<(?P<TAG>[a-zA-Z\d]+)(?P<ATTR>[^>]*)(?:>|/>)'
        self.ATTR_PARAM = r'(?P<ATTR>(?<= )[^\s]+(?==))=([\"\'])(?P<PARAM>(?<==[\"\']).*?)\2(?=[ >])'
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
        tag = re.match(r'<([a-zA-Z\d]+)[ >]', data).group(1)
        if tag not in self.reqTags:return True
        reqTags = dict(self.reqTags[tag])
        if '*' in reqTags: reqTags.pop('*')
        tagAttr = self.getAttrDict(data, 0)
        return self.haveTagAllAttrReq(tag, tagAttr, reqTags)

    def initParse(self, data, posIni):
        if not self.checkStartTag(data): return None
        tagList = self.feed(data)
        if not tagList: return None
        reqSet = set(self.reqTags.keys())        
        toProcess = self.setPathTag(reqSet, tagList)
        if reqSet: return None

        self.varPos[0] = tagList[0][0]
        for k in toProcess:
            tag = tagList[k][1]
            tagAttr = self.getAllTagData(k, data, tagList)
            if not self.haveTagAllAttrReq(tag, tagAttr): return None
            self.storeReqVars(tag, tagAttr, self.reqTags[tag])
        return [self.trnCoord(elem, posIni) for elem in self.varPos]
        pass
    
    def storeReqVars(self, tag, tagAttr, reqAttr):
        interSet = set(reqAttr.keys()).intersection(tagAttr.keys())
        if interSet: 
            paramPos = tagAttr.pop('*ParamPos*')
            for attr in interSet:
                fullAttr = tag + '.' + attr
                if fullAttr in self.varDict:
                    k = self.varDict[fullAttr]
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
    
    def setPathTag(self, reqSet, tagList):
        dadList = [-1]
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
        if tagList[0][1] in reqSet:toProcess.append(0)
        reqSet.difference_update([tagList[0][1]])
        for k in xrange(1,len(tagList)):
            indx = dadList[k]
            pathTag = tagList[indx][1] + '.' + tagList[k][1]
            pathDict[pathTag] = pathDict.get(pathTag, 0) + 1
            if pathDict[pathTag] > 1: pathTag += '[' + str(pathDict[pathTag]) + ']'
            tagList[k][1] = pathTag
            packedPath = pathTag if pathTag.count('.') < 3 else packPath(pathTag, pathTag.count('.'))
            if pathTag in reqSet:
                reqSet.difference_update([pathTag])
                toProcess.append(k)
            elif pathTag != packedPath and packedPath in reqSet:
                reqSet.difference_update([packedPath])
                toProcess.append(-k)
            if not reqSet: break
        for k in range(len(toProcess)):
            m = toProcess[k]
            if m >= 0 : continue
            toProcess[k] = -m
            pathTag = tagList[-m][1]
            tagList[-m][1] = packPath(pathTag, pathTag.count('.')) 
        return toProcess
    
    def getAttrDict(self, data, offset):
        """
        Recibe    : '<tag parameters>' o <tag parameters/>
        Entrega   : Dictionary con parameters value and en *ParamPos* diccionario de posiciones
         
        """
        match = re.match(r'<[a-zA-Z\d]+ (.+?)[/]*>', data)
        if not match: return {'*ParamPos*':{}}
        offset += match.start(1) - 1
        data = ' ' + match.group(1) + ' '
        mgList = list(re.finditer(self.ATTR_PARAM, data)) 
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
                if m.lastgroup == "GENTAG" :tagStack.append([tag, m.span()])
                else: tagList.append([m.span(), tag, None])
                continue
                pass
            
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
                pass
            
            if m.lastgroup in ["BLANKTEXT", "SUFFIX"]:
                pass
    
        if totLen != len(data): raise Exception
        pass


class myHTMLParser(object):
    def __init__(self):
        self.TAGPATT = r'<(?P<TAG>[a-zA-Z\d]+)(?P<ATTR>[^>]*)(?:>|/>)'
        self.ATTR_PARAM = r'(?P<ATTR>(?<= )[^\s]+(?==))=([\"\'])(?P<PARAM>(?<==[\"\']).*?)\2(?=[ >])'
        self.master_pat = re.compile('|'.join([GENSELFTAG, GENTAG, BLANKTEXT, GENTEXT, ENDTAG, DOCSTR, SUFFIX]))
        self.breakFlag = False 
        self._totLen = 0
        self._starttag_text = ''
        pass
    
    def getTag(self, data):
        match = re.match(self.TAGPATT, data)
        return match.group('TAG') 
        pass
    
    def feed(self, data):
        scanner = self.master_pat.scanner(data)
        self._totLen = 0
        for m in iter(scanner.match, None):
            if m.lastgroup == "GENSELFTAG":
                self._starttag_text = m.group()
                tag = self.getTag(m.group())
                self.handle_startendtag(tag, {})
            elif m.lastgroup == "GENTAG":
                self._starttag_text = m.group()
                tag = self.getTag(m.group())
                self.handle_starttag(tag, {})
            elif m.lastgroup == "ENDTAG":
                tag = m.group()[2:-1]
                self.handle_endtag(tag)
            elif m.lastgroup == "GENTEXT":
                self.handle_data(m.group())
            elif m.lastgroup == "DOCSTR":
                decl = m.group()[2:-1]
                self.handle_decl(decl)
            elif m.lastgroup in ["BLANKTEXT", "SUFFIX"]:
                self.unknown_decl(m.group())
                
            self._totLen += len(m.group())
            if self.breakFlag: break
        if not self.breakFlag and self.getpos() != len(data): raise Exception
        pass

    def getpos(self):
        return self._totLen
        
    def close(self):
        self.breakFlag = True
        pass
    
    def reset(self):
        pass
    def get_starttag_text(self):
        return self._starttag_text
    
    def handle_starttag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        pass
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_data(self, data):
        pass
    def handle_entity_ref(self, name):
        pass
    def handle_charref(self, name):
        pass
    def handle_comment(self, data):
        pass
    def handle_decl(self, decl):
        pass
    def handle_pi(self, data):
        pass
    def unknown_decl(self, data):
        pass
    
  
class newRegexParser(myHTMLParser):
    def __init__(self, reqTags, varList):
        myHTMLParser.__init__(self)
        self.reqTags = dict(reqTags)
        self.varDict = {}
        for k, tagTple in enumerate(varList):
            key = tagTple[0]
            self.varDict[key] = k + 1
        self.varPos = (len(varList) + 1) * [0]
        
        self.lines = [0, 0]
        self.totLen = 0
        self.tagStack = []
        self.tagList = []
        self.stackPath = ''
        self.posIni = 0
        self.posFin = 0
        pass
    
    def checkStartTag(self, data):
        tag = re.match(r'<([a-zA-Z\d]+)[ >]', data).group(1)
        if tag not in self.reqTags:return True
        reqTags = self.reqTags.pop(tag)
        if '*' in reqTags: self.reqTags[tag] = {'*':reqTags.pop('*')}
        tagAttr = self.getAttrDict(data, 0)
        bFlag = self.haveTagAllAttrReq(tag, tagAttr, reqTags)
        if not bFlag: return False
        self.storeReqVars(tag, tagAttr, reqTags)
        return True

    def initParse(self, data, posIni):
        if not self.checkStartTag(data): return None
#         self.storeLineOffsets(data)
        self.feed(data)
#         return self.tagList
        tagList = self.tagList
        if not tagList: return None
        reqSet = set(self.reqTags.keys())        
        toProcess = self.setPathTag(reqSet)
        if reqSet: return None

        self.varPos[0] = self.tagList[0][0]
        for k in toProcess:
            tag = tagList[k][1]
            tagAttr = self.getAllTagData(k,data)
            if not self.haveTagAllAttrReq(tag, tagAttr): return None
            self.storeReqVars(tag, tagAttr, self.reqTags[tag])
        return list(self.varPos)
        pass
    
    def initParseOLD(self, data, posIni):
        if not self.checkStartTag(data): return None        
        tagSpan = lambda x: tagList[x][0][1]
        self.feed(data)
        tagList = self.tagList
        if not tagList: return None
        dadList = [-1]
        for k in xrange(len(tagList) - 1):
            indx = k + 1
            while 1:
                if tagSpan(indx) < tagSpan(k):
                    dadList.append(k)
                    if tagList[indx][1] == '*':tagList[k][2] = indx
                    break
                else:
                    k = dadList[k]
                    
        pathDict = {}
        toProcess = []
        reqSet = set(self.reqTags.keys())
        if tagList[0][1] in reqSet:toProcess.append(0)
        reqSet.difference_update(tagList[0][1])
        self.varPos[0] = tagList[0][0]
        for k in xrange(1,len(tagList)):
            indx = dadList[k]
            pathTag = tagList[indx][1] + '.' + tagList[k][1]
            pathDict[pathTag] = pathDict.get(pathTag, 0) + 1
            if pathDict[pathTag] > 1: pathTag += '[' + str(pathDict[pathTag]) + ']'
            tagList[k][1] = pathTag
            if pathTag in reqSet:
                reqSet.difference_update([pathTag])
                toProcess.append(k)
            if not reqSet: break

        for k in toProcess:
            tag = tagList[k][1] 
            posBeg, posEnd = tagList[k][0]
            tagAttr = self.getAttrDict(data[posBeg:posEnd], posBeg)
            if tagList[k][2]:
                n = tagList[k][2]
                posBeg, posEnd = tagList[n][0]
                tagAttr['*'] = data[posBeg:posEnd]
                tagAttr['*ParamPos*']['*'] = tagList[n][0]
            reqTags = self.reqTags[tag]
            diffSet = set(reqTags.keys()).difference(tagAttr.keys())
            interSet = set(reqTags.keys()).intersection(tagAttr.keys())
            if not diffSet and all([reqTags[key].match(tagAttr[key]) for key in interSet if reqTags[key]]):
                if not interSet: continue
                paramPos = tagAttr.pop('*ParamPos*')
                for attr in interSet:
                    fullAttr = tag + '.' + attr
                    if fullAttr in self.varDict:
                        k = self.varDict[fullAttr]
                        self.varPos[k] = paramPos[attr]
            else:
                return None
        return list(self.varPos)
        pass
    
    
    def storeReqVars(self, tag, tagAttr, reqAttr):
        interSet = set(reqAttr.keys()).intersection(tagAttr.keys())
        if interSet: 
            paramPos = tagAttr.pop('*ParamPos*')
            for attr in interSet:
                fullAttr = tag + '.' + attr
                if fullAttr in self.varDict:
                    k = self.varDict[fullAttr]
                    self.varPos[k] = paramPos[attr]
        

    def haveTagAllAttrReq(self, tag, tagAttr, reqTags = -1):
        if reqTags == -1: reqTags = self.reqTags[tag]
        diffSet = set(reqTags.keys()).difference(tagAttr.keys())
        interSet = set(reqTags.keys()).intersection(tagAttr.keys())
        bFlag = diffSet or not all([reqTags[key].match(tagAttr[key]) for key in interSet if reqTags[key]])
        return not bFlag
    
    def getAllTagData(self, tagPos, data):
        posBeg, posEnd = self.tagList[tagPos][0]
        tagAttr = self.getAttrDict(data[posBeg:posEnd], posBeg)
        if self.tagList[tagPos][2]:
            n = self.tagList[tagPos][2]
            posBeg, posEnd = self.tagList[n][0]
            tagAttr['*'] = data[posBeg:posEnd]
            tagAttr['*ParamPos*']['*'] = self.tagList[n][0]
        return tagAttr
    
    def setPathTag(self, reqSet):
        tagList = self.tagList
        dadList = [-1]
        for k in xrange(len(tagList) - 1):
            indx = k + 1
            while 1:
                if tagList[indx][0][1] < tagList[k][0][1]:
                    dadList.append(k)
                    if tagList[indx][1] == '*':tagList[k][2] = indx
                    break
                k = dadList[k]
                    
        pathDict = {}
        toProcess = []
        if tagList[0][1] in reqSet:toProcess.append(0)
        reqSet.difference_update([tagList[0][1]])
        for k in xrange(1,len(tagList)):
            indx = dadList[k]
            pathTag = tagList[indx][1] + '.' + tagList[k][1]
            pathDict[pathTag] = pathDict.get(pathTag, 0) + 1
            if pathDict[pathTag] > 1: pathTag += '[' + str(pathDict[pathTag]) + ']'
            tagList[k][1] = pathTag
            if pathTag in reqSet:
                reqSet.difference_update([pathTag])
                toProcess.append(k)
            if not reqSet: break
        return toProcess
    
    def getAttrDict(self, data, offset):
        """
        Recibe    : '<tag parameters>' o <tag parameters/>
        Entrega   : Dictionary con parameters value and en *ParamPos* diccionario de posiciones
         
        """
        match = re.match(r'<[a-zA-Z\d]+ (.+?)[/]*>', data)
        if not match: return {'*ParamPos*':{}}
        offset += match.start(1) - 1
        data = ' ' + match.group(1) + ' '
        mgList = list(re.finditer(self.ATTR_PARAM, data)) 
        mgDict = dict((mg.group("ATTR"), mg.group("PARAM")) for mg in mgList)
        mgDict['*ParamPos*'] = dict((mg.group("ATTR"), self.trnCoord(mg.span("PARAM"), offset)) for mg in mgList)
        return mgDict

    def trnCoord(self, tupleIn, offset):
        return (tupleIn[0] + offset, tupleIn[1] + offset)
    
    def close(self):
        myHTMLParser.close(self)
        self.tagList.sort()
    
    def handle_starttag(self, tag, attrs):
        posIni = self.getpos()
        posFin = posIni + len(self.get_starttag_text())
        self.stackPath += '.' + tag
        span = (posIni, posFin) 
        self.tagStack.append([tag, span])
        
    def handle_startendtag(self, tag, attrs):
        posIni = self.getpos()
        posFin = posIni + len(self.get_starttag_text())
        self.stackPath += '.' + tag
        span = (posIni, posFin) 
        self.tagList.append([span, tag, None])
        
    def handle_endtag(self, tag):
        posIni = self.getpos()
        posFin = posIni + len(tag) + len('</>')
        rootTag, sep = self.stackPath.rpartition('.' + tag)[:2]
        if sep:
            self.stackPath = rootTag
            while 1:
                stckTag, stckTagSpan = self.tagStack.pop()
                bFlag = tag == stckTag
                if bFlag:
                    tagSpan = (stckTagSpan[0], posFin)
                else:
                    tagSpan = stckTagSpan 
                self.tagList.append([tagSpan, stckTag, None])
                if bFlag: break
        if not self.tagStack: self.close()
        
    def handle_data(self, data):
        posIni = self.getpos()
        posFin = posIni + len(data)
        span = (posIni, posFin) 
        self.tagList.append([span, '*', None])

    
class regexParser:
    def __init__(self, reqTags, varList):
        self.TAGPATT = r'<(?P<TAG>[a-zA-Z\d]+)(?P<ATTR>[^>]*)(?:>|/>)'
        self.ATTR_PARAM = r'(?P<ATTR>(?<= )[^\s]+(?==))=([\"\'])(?P<PARAM>(?<==[\"\']).*?)\2(?=[ >])'
        self.master_pat = re.compile('|'.join([GENSELFTAG, GENTAG, BLANKTEXT, GENTEXT, ENDTAG, DOCSTR, SUFFIX]))
        
        self.reqTags = reqTags
        self.varDict = {}
        for k, tagTple in enumerate(varList):
            key = tagTple[0]
            self.varDict[key] = k + 1
        self.varPos = (len(varList) + 1) * [0]
        self.varList = varList
        pass
    
    def initParse(self, data, posIni):
        tagSpan = lambda x: tagList[x][0][1]
        tagList = self.feed(data)
        if not tagList: return None
        dadList = [-1]
        for k in xrange(len(tagList) - 1):
            indx = k + 1
            while 1:
                if tagSpan(indx) < tagSpan(k):
                    dadList.append(k)
                    if tagList[indx][1] == '*':tagList[k][2] = indx
                    break
                else:
                    k = dadList[k]
                    
        pathDict = {}
        toProcess = []
        reqSet = set(self.reqTags.keys())
        if tagList[0][1] in reqSet:toProcess.append(0)
        reqSet.difference_update(tagList[0][1])
        self.varPos[0] = tagList[0][0]
        for k in xrange(1,len(tagList)):
            indx = dadList[k]
            pathTag = tagList[indx][1] + '.' + tagList[k][1]
            pathDict[pathTag] = pathDict.get(pathTag, 0) + 1
            if pathDict[pathTag] > 1: pathTag += '[' + str(pathDict[pathTag]) + ']'
            tagList[k][1] = pathTag
            if pathTag in reqSet:
                reqSet.difference_update([pathTag])
                toProcess.append(k)
            if not reqSet: break

        for k in toProcess:
            tag = tagList[k][1] 
            posBeg, posEnd = tagList[k][0]
            tagAttr = self.getAttrDict(data[posBeg:posEnd], posBeg)
            if tagList[k][2]:
                n = tagList[k][2]
                posBeg, posEnd = tagList[n][0]
                tagAttr['*'] = data[posBeg:posEnd]
                tagAttr['*ParamPos*']['*'] = tagList[n][0]
            reqTags = self.reqTags[tag]
            diffSet = set(reqTags.keys()).difference(tagAttr.keys())
            interSet = set(reqTags.keys()).intersection(tagAttr.keys())
            if not diffSet and all([reqTags[key].match(tagAttr[key]) for key in interSet if reqTags[key]]):
                if not interSet: continue
                paramPos = tagAttr.pop('*ParamPos*')
                for attr in interSet:
                    fullAttr = tag + '.' + attr
                    if fullAttr in self.varDict:
                        k = self.varDict[fullAttr]
                        self.varPos[k] = paramPos[attr]
            else:
                return None
        return list(self.varPos)
        pass
    
    def getTag(self, data):
        match = re.match(self.TAGPATT, data)
        return match.group('TAG') 
        pass

    def getAttrDict(self, data, offset):
        """
        Recibe    : '<tag parameters>' o <tag parameters/>
        Entrega   : Dictionary con parameters value and en *ParamPos* diccionario de posiciones
         
        """
        match = re.match(r'<[a-zA-Z\d]+ (.+?)[/]*>', data)
        if not match: return {}
        offset += match.start(1) - 1
        data = ' ' + match.group(1) + ' '
        mgList = list(re.finditer(self.ATTR_PARAM, data)) 
        mgDict = dict((mg.group("ATTR"), mg.group("PARAM")) for mg in mgList)
        mgDict['*ParamPos*'] = dict((mg.group("ATTR"), self.trnCoord(mg.span("PARAM"), offset)) for mg in mgList)
        return mgDict

    def trnCoord(self, tupleIn, offset):
        return (tupleIn[0] + offset, tupleIn[1] + offset)

    def feed(self, data):
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
                if m.lastgroup == "GENTAG" :tagStack.append([tag, m.span()])
                else: tagList.append([m.span(), tag, None])
                continue
                pass
            
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
                pass
            
            if m.lastgroup == "DOCSTR":
                pass
            
            if m.lastgroup in ["BLANKTEXT", "SUFFIX"]:
                pass
    
        if totLen != len(data): raise Exception
        pass

    
    
    def handle_starttag(self, tag, attrs):
        pass
    def handle_endtag(self, tag):
        pass
    def handle_startendtag(self, tag, attrs):
        pass
    def handle_data(self, data):
        pass
    
            
    



def testHtmlPattern(fileName, compFlags):
    INDENT = '  '
    indentPos = -1
    master_pat = re.compile('|'.join([GENTAG, GENSELFTAG, BLANKTEXT, GENTEXT, ENDTAG, DOCSTR, SUFFIX]))
    
    stack = []
    scanner = master_pat.scanner(fileName)
    totLen = 0
    for m in iter(scanner.match, None):
        if m.lastgroup == ['BLANKTEXT', 'SUFFIX']: continue
        if m.lastgroup == 'ENDTAG':
            indentPos -= 1
        else:
            indentPos += 1
        
        if m.lastgroup == 'GENTAG':
            match = re.match(r'<(?P<TAG>[a-zA-Z\d]+)[^>]*>', m.group())
            stack.append(match.group('TAG'))
        if m.lastgroup == 'ENDTAG':
            match = re.match(r'</(?P<TAG>[^>]+)>', m.group())
            bFlag = stack and match.group('TAG') in stack
            if bFlag:
                while stack[-1] != match.group('TAG'):
                    print '--- ' + m.lastgroup + ' --- ' + str(indentPos) + ' *** '  + '</' + stack.pop() + '>'
                    indentPos -= 1                    
                stack.pop()
            else:
                print '<<<<<****>>>>>'
            
        print '*** ' + m.lastgroup + ' *** ' + str(indentPos) + ' *** '  + m.group()
        if m.lastgroup == 'GENSELFTAG':
            indentPos -= 1
        totLen += len(m.group()) 
    
    if totLen != len(fileName): 
        print 'file procesado hasta pos '  + str(totLen)
        print fileName[totLen:totLen+60]
#         raise re.error

    
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
    testing = "doctest"    

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
dmy = CustomRegEx.ExtRegexParser(reqTags, varList)
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
        dmy = ExtRegexParser(reqTags, varList)
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
