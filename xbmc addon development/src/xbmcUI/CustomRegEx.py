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
BLANKTEXT = r'(?P<BLANKTEXT>(?<=>)\W+(?=<))'
GENTEXT = r'(?P<GENTEXT>(?<=>)[^<]+(?=<))'
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

        print '*** *** ***'
        print tagRegex
        print string[:40]
        reg = re.compile(tagRegex, re.DOTALL)
        posIni = 0 
        while 1:
            match  = reg.search(string, posIni)
            print 'match', match
            if not match: return None
#             ATTR_PARAM = r'(?P<ATTR>(?<= )[^\s]+(?==))=(?P<PARAM>(?<==)\".+?\"(?=[ >]))'  
            ATTR_PARAM = r'(?P<ATTR>(?<= )[^\s]+(?==))=([\"\'])(?P<PARAM>(?<==[\"\']).*?)\2(?=[ >])'
            mgDict = dict((mg.group("ATTR"), mg) for mg in list(re.finditer(ATTR_PARAM, match.group("ATTR"))))
            print match.group("ATTR")
            print list(re.finditer(ATTR_PARAM, match.group("ATTR")))
            print mgDict
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

def compile(regexPattern, compFlags):
    match = re.search('\(\?#<TAG (?P<tag>[a-zA-Z][a-zA-Z\d]*)(?P<vars>[^>]*>)\)',regexPattern)
    if not match: return re.compile(regexPattern, compFlags)
    
    ATTR = r'(?P<ATTR>(?<= )[^\s]+(?==))'
    REQATTR = r'(?P<REQATTR>(?<= )[a-zA-Z][a-zA-Z\d]*(?= ))'
    VAR = r'(?P<VAR>(?<==)[a-zA-Z][a-zA-Z\d]*(?=[ >]))'
    PARAM = r'(?P<PARAM>(?<==)[\'\"][^\'\"]+[\'\"](?=[ >]))'
    EQ = r'(?P<EQ>=)'
    WS = r'(?P<WS>\s+)'
    END = r'(?P<END>>)'
    
    
    rootTag = match.group('tag')
    master_pat = re.compile('|'.join([ATTR, REQATTR, VAR, PARAM, EQ, WS, END]))
    scanner = master_pat.scanner(match.group('vars'))
    totLen = 0
    tags = {}
    varList = []
    for m in iter(scanner.match, None):
        sGroup = m.group()
        totLen += len(sGroup) 
        print m.lastgroup, m.group()
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
        if sGroup: tagDict[attrKey] = re.compile(sGroup[1:-1])
#         tagDict[attrKey] = sGroup[1:-1]

    if totLen != len(match.group('vars')): re.compile(r'(') # Eleva exepci�n, se puede mejorar
    print '****'
    print regexPattern
    print tags
    print varList
    return ExtRegexObject(regexPattern, compFlags, tags, varList)




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
    
    with open(r'c:/fileTest/htmlRegexTest.txt', 'r') as origF:
        equis = origF.read()
  
    import pprint
    reg = compile('(?#<TAG tr td.a.href=url td.a.*=label td[3].*=when td[4].*=quality>)', 0)
    ese = reg.findall(equis)
    pprint.pprint(ese)
    print len(ese)
# 
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