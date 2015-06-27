# -*- coding: utf-8 -*-
'''
Created on 27/06/2014

@author: Alex Montes Barrios
'''
import os
import Tkinter as tk
import tkSimpleDialog
import tkMessageBox
import menuThreads
import thread
import ttk
import tkFont
import urllib
import urllib2
import httplib
import tkMessageBox
import urlparse
import re
import Queue
import xml.etree.ElementTree as ET
import time
import addonCoder
from likeXbmc import translatePath
from OptionsWnd import scrolledFrame
from urllib import urlencode


"a simple customizable scrolled listbox component"

class RegexpBar(tk.Frame):
    def __init__(self, master, messageVar):
        tk.Frame.__init__(self, master)
        self.dropDownFiler = None
        self.textWidget = None
        self.actMatchIndx = 0

        self.queue = Queue.Queue(maxsize=0)
        self.activeCallBack = []
        self.threadFlag = 'stop'
        
        self.messageVar = messageVar
        self.setGUI()

    def setTextWidget(self, tWidget):
        self.textWidget = tWidget

    def setDropDownFiler(self, callbckFunc):
        self.dropDownFiler = callbckFunc 
        
    def setGUI(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        
        frame1 = tk.Frame(self)
        frame1.pack(fill = tk.X)
        self.butKeyMaker = tk.Button(frame1, text = "ZoomIn", command = self.zoomInOut)        
        self.butKeyMaker.pack(side = tk.LEFT)
        self.regexPattern = tk.StringVar()
        self.regexPattern.trace("w", self.getPatternMatch)
        self.entry = ttk.Combobox(frame1, font = self.customFont, textvariable = self.regexPattern)
        self.entry.configure(postcommand = self.fillDropDownLst)
        self.entry.pack(side=tk.LEFT, fill = tk.X, expand = 1 )
        
        self.entry.event_add('<<re_escape>>','<Control-E>','<Control-e>')
        self.entry.bind('<<re_escape>>', self.selPasteWithReEscape)
        self.entry.bind('<Return>', lambda event: self.extreme('<<'))
        
        self.matchLabel = tk.Label(frame1, font = self.customFont, text = "")
        self.matchLabel.pack(side = tk.LEFT)
        
        self.butLast = tk.Button(frame1, state = tk.DISABLED, font = self.customFont, text = "L", command = lambda: self.extreme('>>'))
        self.butLast.pack(side = tk.RIGHT)
        self.butNext = tk.Button(frame1, state = tk.DISABLED, font = self.customFont, text = ">", command = self.nextMatch)
        self.butNext.pack(side = tk.RIGHT)
        self.butPrev = tk.Button(frame1, state = tk.DISABLED, font = self.customFont, text = "<", command = self.prevMatch)
        self.butPrev.pack(side = tk.RIGHT)
        self.butFirst = tk.Button(frame1, state = tk.DISABLED, font = self.customFont, text = "F", command = lambda: self.extreme('<<'))
        self.butFirst.pack(side = tk.RIGHT)
        
        frame15 = tk.Frame(self)
        frame15.pack(fill = tk.X)
        label = tk.Label(frame15, text = "Compilation Flags:", font = self.customFont)
        label.pack(side = tk.LEFT)

        self.chkVar = {}
        chkTxt = ['UNICODE', 'DOTALL', 'IGNORECASE', 'LOCALE', 'MULTILINE']
        for elem in chkTxt:
            self.chkVar[elem] = tk.IntVar()
            chkbutt = tk.Checkbutton(frame15, text = elem, variable = self.chkVar[elem], font = self.customFont, command = self.getPatternMatch )
            chkbutt.pack(side = tk.LEFT)

        frame3 = tk.Frame(self)
        frame3.pack(fill = tk.X)
        cmbbxValues = ['[^X]+', '.+?', r'\w+', r'\W+?', r'(?P=<keyName>)']
        self.cmbbxPattern = ttk.Combobox(frame3, font = self.customFont, values = cmbbxValues)
        self.cmbbxPattern.pack(side=tk.LEFT, fill = tk.X )
        cmbbxIntVar = tk.IntVar()
#         cmbbxIntVar.trace('w', self.reggexpVar)
        self.cmbbxIntVar = cmbbxIntVar
        for k, elem in enumerate(['Pattern', 'Key']):
            boton = tk.Radiobutton(frame3, text = elem, width = 15, value = k, variable = cmbbxIntVar)
            boton.pack(side = tk.LEFT)
        cmbbxIntVar = 0
        
        cmbbxValues = ['url', 'label', 'iconImage', 'thumbnailImage', 'SPAN', 'SEARCH', 'NXTPOSINI']
        self.cmbbxKey = ttk.Combobox(frame3, font = self.customFont, values = cmbbxValues)
        self.cmbbxKey.pack(side=tk.LEFT, fill = tk.X )

        boton = tk.Button(frame3, font = self.customFont, text = "Apply", command = self.keyMaker)
        boton.pack(side = tk.LEFT)
        
    def setZoomManager(self, callBackFunc):
        self.zoomManager = callBackFunc
        
    def setZoomType(self, zoomType):
        self.butKeyMaker.config(text = zoomType)
        
    def zoomInOut(self):
        if self.zoomManager:
            btnText = self.butKeyMaker.cget('text')
            retValue = self.zoomManager(btnText)
            if retValue:
                indx = 1 - ['ZoomIn', 'ZoomOut'].index(btnText) 
                self.setZoomType(['ZoomIn', 'ZoomOut'][indx])

    def selPasteWithReEscape(self, event = None):
        textw = self.entry
        text = textw.selection_get(selection = 'CLIPBOARD')
        try:
            if text:
                if textw.select_present():
                    textw.delete('sel.first', 'sel.last')
                text = ''.join([(re.escape(elem) if elem in '()?.*{}[]+\\' else elem) for elem in text])
                textw.insert('insert', text)
        except tk.TclError:
            pass
        return 'break'


    def fillDropDownLst(self):
        if self.dropDownFiler:
            theValues = self.dropDownFiler()
        else:
            theValues =  ['uno', 'dos', 'tres']
        self.entry.configure(values = theValues)

    def extreme(self, widgetText):
        if widgetText == '>>':
            self.textWidget.mark_set('insert', '1.0')
            self.getMatchTag(False)            
        elif widgetText == '<<':
            self.textWidget.mark_set('insert', 'end')
            self.getMatchTag(True)
        
    def keyMaker(self):
        tagName = self.cmbbxKey.get()
        tagPattern = self.cmbbxPattern.get()
        entryTxt = self.regexPattern.get()
        if tagName in ['SPAN', 'NXTPOSINI']:
            entryTxt = '(?#<' + tagName +'>)' + entryTxt
        elif self.entry.select_present():
            selText = self.entry.selection_get()
            posIni = entryTxt.find(selText)
            posFin = posIni + len(selText)
            if tagPattern == '[^X]+': tagPattern = tagPattern.replace('^X', '^' + entryTxt[posFin])
            if tagPattern == r'(?P=<keyName>)': tagReplace = tagPattern.replace('<keyName>', tagName)
            elif tagName == 'SEARCH':
                entryTxt = '(?#<SEARCH>)' + entryTxt
                tagReplace = '<search>'
                posIni += len('(?#<SEARCH>)')
                posFin += len('(?#<SEARCH>)')
            elif self.cmbbxIntVar.get() == 1:
                tagReplace = '(?P<' + tagName +'>' + tagPattern + ')'
            elif self.cmbbxIntVar.get() == 0:
                tagReplace = tagPattern
            entryTxt = entryTxt[:posIni] + tagReplace + entryTxt[posFin:] 
            posFin = posIni + len(tagReplace)
            self.entry.select_range(posIni, posFin)
            self.entry.icursor(posFin)
        self.regexPattern.set(entryTxt)


    def actMatch(self, selTag):
        content = self.textWidget.get(*selTag)
        pattern = self.getRegexpPattern()
        compflags = eval(self.getCompFlags())
        fieldList = re.findall('\?P<([^>]+)>', pattern)
        match = re.search(pattern, content, flags = compflags)
        gDict = match.groupdict()
        matchStr = '   '.join([key + '=' + gDict.get(key,'') for key in fieldList])
        self.messageVar.set(matchStr)

    def getRegexpPattern(self):
        return self.regexPattern.get()

    def getCompFlags(self):
        compflags = ['re.' + key for key in self.chkVar.keys() if self.chkVar[key].get()]
        return '|'.join(compflags) if compflags else '0' 

    def setRegexpPattern(self, regexp):
        self.regexPattern.set(regexp)
        
    def setCompFlags(self, compflags):
        keyFlags = compflags.replace('re.', '').split('|') if compflags else []
        for key in self.chkVar.keys():
            flag = True if key in keyFlags else False 
            self.chkVar[key].set(flag)

    def nextMatch(self):
        self.getMatchTag(nextMatch = True)

    def prevMatch(self):
        self.getMatchTag(nextMatch = False)

    def getMatchTag(self, nextMatch = True):
        seekFunc = self.textWidget.tag_nextrange if nextMatch else self.textWidget.tag_prevrange
        tag_names = self.textWidget.tag_names('insert')
        if ('evenMatch' in tag_names) or ('oddMatch' in tag_names) :
            nxtTag = 'evenMatch' if 'oddMatch' in tag_names else 'oddMatch'
            iniPos = 'insert + 1 char' if nextMatch else 'insert - 1 char'
            selTag = seekFunc(nxtTag, iniPos)
        else:
            selOdd = seekFunc('oddMatch', 'insert')
            selEven = seekFunc('evenMatch', 'insert')
            if selEven != selOdd:
                if selOdd == tuple(): selTag = selEven
                elif selEven == tuple(): selTag = selOdd
                elif map(int, selOdd[0].split('.')) < map(int, selEven[0].split('.')): selTag = selOdd if nextMatch else selEven
                else: selTag = selEven if nextMatch else selOdd
            else:
                selTag = tuple()            
        oddMatchs = self.textWidget.tag_ranges('oddMatch')
        evenMatchs = self.textWidget.tag_ranges('evenMatch')
        eotags = []
        if evenMatchs:
            for ene in range(len(evenMatchs)/2):
                eotags.extend([oddMatchs[2*ene], oddMatchs[2*ene + 1]])
                eotags.extend([evenMatchs[2*ene], evenMatchs[2*ene + 1]])
            if len(oddMatchs) > len(evenMatchs):
                eotags.extend([oddMatchs[-2], oddMatchs[-1]])
        else:
            eotags = oddMatchs
        matchTags = map(str,eotags)
        nMatchs = len(matchTags)/2
        if selTag != tuple():
            nPos = [valor for k, valor in enumerate(matchTags) if not k%2].index(selTag[0]) + 1
        else:
            nPos = 1 if nextMatch else nMatchs
            selTag = (matchTags[0], matchTags[1]) if nextMatch else (matchTags[-2], matchTags[-1])
        matchStr = ' '  + str(nPos) + ' de ' + str(nMatchs)
        self.actMatchIndx = nPos

        self.textWidget.tag_remove('actMatch', '1.0', 'end')
        self.textWidget.tag_add('actMatch', *selTag)
        self.textWidget.mark_set('insert', selTag[0])
        self.textWidget.see(selTag[1 if nextMatch else 0])            
        self.matchLabel.config(text=matchStr, bg = 'SystemButtonFace')
        self.actMatch(selTag)
        
    def getPatternMatch(self, *dummy):
        if self.entry.current() != -1:
            pattern = self.regexPattern.get() 
            if pattern.startswith('(?#<'):
                posFin = pattern.find(')') + 1
                self.regexPattern.set(pattern[posFin:])
        self.formatContent()
            
    def formatContent(self, index1 = '1.0', index2 = 'end'):
        while self.activeCallBack:
            idAfter = self.activeCallBack.pop()
            self.after_cancel(idAfter)
        if self.threadFlag == 'run':
            self.threadFlag = 'stop'
            if self.t.isAlive():
                self.t.join(10)

        regexPattern =self.regexPattern.get()
        compileOp = self.chkVar
        matchLabel = self.matchLabel
                    
        opFlag = {'UNICODE':re.UNICODE, 'DOTALL':re.DOTALL, 'IGNORECASE':re.IGNORECASE, 'LOCALE':re.LOCALE, 'MULTILINE':re.MULTILINE}
        compFlags = reduce(lambda x,y: x|y,[opFlag[key]*compileOp[key].get() for key in compileOp.keys()],0)
        content = self.textWidget.get(index1, index2)
        baseIndex = self.textWidget.index(index1)

        self.removeTags('1.0', 'end')
        
        yesCompFlag = len(regexPattern) > 0
        try:
            reg = re.compile(regexPattern, compFlags)
        except:
            yesCompFlag = False

        if not yesCompFlag:
            matchLabel.config(text = '', bg = 'SystemButtonFace')
            return None
        
        if self.threadFlag == 'stop':
            self.threadFlag = 'run'
            from threading import Thread
            self.t = Thread(name="searchThread", target=self.lengthProcess, args=(reg, content, baseIndex))
            self.t.start()
            self.activeCallBack.append(self.after(100, self.updateGUI))
    
    def lengthProcess(self, reg, content, baseIndex):
        self.queue.queue.clear()
        k = 0
        pos = 0
        while self.threadFlag == 'run':
            match = reg.search(content, pos)
            if not match: break
            k += 1
            pos = match.end(0)
            self.queue.put([k, (match, baseIndex)])
        if k == 0:
            self.queue.put([-1, (None, baseIndex)])
        self.threadFlag = 'stop'
        return
    
    def removeTags(self, tagIni, tagFin):
        tagColor = ['evenMatch', 'oddMatch', 'matchTag', 'actMatch', 'group', 'hyper']
        for match in tagColor:
            self.textWidget.tag_remove(match, tagIni, tagFin)
            
    def setTag(self, tag, baseIndex, match, grpIndx):
        tagIni = baseIndex + ' + %d chars'%match.start(grpIndx)
        tagFin = baseIndex + ' + %d chars'%match.end(grpIndx)
        try:
            self.textWidget.tag_add(tag, tagIni, tagFin)
        except:
            print 'exception: ' + tag + ' tagIni: ' + tagIni + ' tagFin: ' + tagFin
        for key in match.groupdict().keys():
            tagIni = baseIndex + ' + %d chars'%match.start(key)
            tagFin = baseIndex + ' + %d chars'%match.end(key)
            self.textWidget.tag_add('group', tagIni, tagFin)
        urlkeys = [key for key in match.groupdict().keys() if key.lower().endswith('url')] 
        for key in urlkeys:
            tagIni = baseIndex + ' + %d chars'%match.start(key)
            tagFin = baseIndex + ' + %d chars'%match.end(key)
            self.textWidget.tag_add('hyper', tagIni, tagFin)
            

    def updateGUI(self):
        nProcess = 100
        k = 0
        while k != -1 and nProcess and not self.queue.empty():
            k, args = self.queue.get()
            if k != -1:
                match, baseIndex = args
                nProcess -= 1
                tagColor = ['evenMatch', 'oddMatch']
                matchColor = tagColor[k%2]
                self.setTag(matchColor, baseIndex, match, 0)
                self.setTag('matchTag', baseIndex, match, 0)                    
                if k > 1:
                    matchStr = ' '  + str(self.actMatchIndx) + ' de ' + str(k)
                    self.matchLabel.config(text = matchStr)
                    self.matchLabel.update()
                    continue
                self.actMatchIndx = 1
                self.matchLabel.config(text = ' 1 de 1', bg = 'SystemButtonFace')
                self.setTag('actMatch', baseIndex, match, 0)                
                btState = tk.NORMAL
            else:
                self.actMatchIndx = 0
                self.matchLabel.config(text = ' 0 de 0', bg = 'red')
                btState =  tk.DISABLED
    
            for button in [self.butFirst, self.butLast, self.butNext, self.butPrev]:
                button.config(state=btState)
     
        if not self.queue.empty(): self.activeCallBack.append(self.after(100, self.updateGUI))
        


class NavigationBar(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.urlContent = None        
        self.mutex = thread.allocate_lock()        
        self.activeUrl = tk.StringVar()
        self.upHistory = []
        self.downHistory = []
        self.cookies={}
        self.makeWidgets()

    def makeWidgets(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        urlFrame = self
        self.prevUrl = tk.Button(urlFrame, state = tk.DISABLED, font = self.customFont, text = "<", command = self.prevButton)
        self.prevUrl.pack(side = tk.LEFT)
        self.nextUrl = tk.Button(urlFrame, state = tk.DISABLED, font = self.customFont, text = ">", command = self.nxtButton)
        self.nextUrl.pack(side = tk.LEFT)
        labelUrl = tk.Label(urlFrame, text = "Actual URL:", width = 11, justify = tk.LEFT)
        labelUrl.pack(side = tk.LEFT)
        self.labelUrl = labelUrl
        entryUrl = tk.Entry(urlFrame, textvariable = self.activeUrl, font = self.customFont)
        entryUrl.pack(side=tk.LEFT, fill = tk.X, expand = 1 )
        entryUrl.bind('<Return>', self.returnKey)
        
    def setActiveUrl(self, url):
        activeUrl = self.normUrl(self.activeUrl.get())
        url = urlparse.urljoin(activeUrl, url)
        self.activeUrl.set(self.unNormUrl(url))
        self.returnKey()
            
    def getActiveUrl(self):
        return self.normUrl(self.activeUrl.get())
    
    def nxtButton(self, *args, **kwargs):
        if not len(self.upHistory): return 
        self.prevUrl.config(state = tk.NORMAL)
        self.downHistory.append(self.upHistory.pop())
        if len(self.upHistory) == 1:
            self.nextUrl.config(state = tk.DISABLED)
        self.setActiveUrl(self.upHistory[-1])
        
    def prevButton(self, *args, **kwargs):
        self.nextUrl.config(state = tk.NORMAL)
        self.upHistory.append(self.downHistory.pop())
        if not len(self.downHistory):
            self.prevUrl.config(state = tk.DISABLED)
        self.setActiveUrl(self.upHistory[-1])            

    def returnKey(self, *args, **kwargs):
        url = self.getActiveUrl()
        if not url: return
        if not self.upHistory:
            self.upHistory.append(url.partition('<post>')[0])
        elif url != self.upHistory[-1]:
            if len(self.upHistory) == 1:
                self.downHistory.append(self.upHistory.pop())
                self.prevUrl.config(state = tk.NORMAL)
            else:
                self.upHistory = []
            self.upHistory.append(url.partition('<post>')[0])

        thId = thread.start_new_thread(self.importUrl, (url, self.mutex))
        self.colorAnimation()
         
    def colorAnimation(self, *args, **kwargs):
        with self.mutex:
            bFlag = not self.urlContent 
        if bFlag:
            colorPalette = ['-  -  -  -', '\\  /  \\  /', '/  \\  /  \\']            
            actColor = self.labelUrl.cget('text')
            try:
                indx = (colorPalette.index(actColor) + 1) % (len(colorPalette))
            except:
                indx = 0
            self.labelUrl.config(text = colorPalette[indx])
            self.labelUrl.after(100, self.colorAnimation)
        else:
            if isinstance(self.urlContent, Exception):
                tkMessageBox.showerror('Error', self.urlContent)
                self.urlContent = ''
            self.urlContentProcessor(self.urlContent)
            self.urlContent = None
            self.labelUrl.config(text = 'Actual URL:')
        
    def setUrlContentProcessor(self, processor):
        self._urlContentProcessor = processor
        
    def urlContentProcessor(self, data):
        if self._urlContentProcessor: return self._urlContentProcessor(data)
        pass

    def normUrl(self, url):
        if not url.partition('//')[1]: url = 'http://' + url
        return url
    
    def unNormUrl(self, url):
        urlParts = url.partition('//') 
        if urlParts[1] and urlParts[0] == 'http:': url = urlParts[2]
        return url

    def importUrl(self, urlToOpen, mutex):
        urlToOpen = self.normUrl(urlToOpen)
        data = self.openUrl(urlToOpen)
        if isinstance(data, basestring):
            for match in re.finditer("\$\.cookie\('([^']+)',\s*'([^']+)",data):
                key,value = match.groups()
                self.cookies[key]=value
            self.cookies["url_referer"] = urlToOpen.partition('<post>')[0]
        with mutex:
            self.urlContent = data

    def openUrl(self, urlToOpen):
    # 31-08-04
    #v1.0.0 
    
    # cookie_example.py
    # An example showing the usage of cookielib (New to Python 2.4) and ClientCookie
    
    # Copyright Michael Foord
    # You are free to modify, use and relicense this code.
    # No warranty express or implied for the accuracy, fitness to purpose or otherwise for this code....
    # Use at your own risk !!!
    
    # If you have any bug reports, questions or suggestions please contact me.
    # If you would like to be notified of bugfixes/updates then please contact me and I'll add you to my mailing list.
    # E-mail michael AT foord DOT me DOT uk
    # Maintained at www.voidspace.org.uk/atlantibots/pythonutils.html
    
        COOKIEFILE = 'cookies.lwp'          # the path and filename that you want to use to save your cookies in
        import os.path
        
        cj = None
        cookielib = None
        
        try:                                    # Let's see if cookielib is available
            import cookielib            
        except ImportError:
            import urllib2
            urlopen = urllib2.urlopen
            Request = urllib2.Request
        else:
            import urllib2    
            urlopen = urllib2.urlopen
            cj = cookielib.LWPCookieJar()       # This is a subclass of FileCookieJar that has useful load and save methods
            Request = urllib2.Request
        
        ####################################################
        # We've now imported the relevant library - whichever library is being used urlopen is bound to the right function for retrieving URLs
        # Request is bound to the right function for creating Request objects
        # Let's load the cookies, if they exist. 
            
        if cj != None:                                  # now we have to install our CookieJar so that it is used as the default CookieProcessor in the default opener handler
            if os.path.isfile(COOKIEFILE):
                cj.load(COOKIEFILE)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
        
        REQUEST_HEADERS = [
            ["User-Agent" , "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"],
            ["Accept","text/html, application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"],
            ["Accept-Encoding","gzip,deflate,sdch"],
            ["Accept-Language" , "es-ES,es;q=0.8,en;q=0.6"],
            ["Cache-Control" , "max-age=0"],
            ["Connection" , "keep-alive"],
            ["Cookie" , "JSESSIONID=FB0417F4DE0E0ED245C58A1129C409A9.tomcatM1p6101"],
        ]
        
        referer = 'http://www.peliculaspepito.com/'
        if self.downHistory:
            referer = self.downHistory[-1]
        REQUEST_HEADERS.append(["Referer" , referer])

        sep = '<post>'
        urlToOpen, sep, postData = urlToOpen.partition(sep)
        
        headers = {}
        for elem in REQUEST_HEADERS:
            headers[elem[0]] = elem[1]
        if self.cookies and self.cookies.pop("url_referer") == urlToOpen:
            headers["Cookie"] = urllib.urlencode(self.cookies) 
        
        try:
            req = Request(urlToOpen, postData or None, headers)            
            url = urlopen(req)
        except Exception as e:
#             tkMessageBox.showerror('URL not Found', urlToOpen)
            data = e
        else:
            self.activeUrl.set(self.unNormUrl(url.geturl()))
            data = url.read()
            if url.info().get('Content-Encoding') == 'gzip':
                import StringIO
                compressedstream = StringIO.StringIO(data)
                import gzip
                gzipper = gzip.GzipFile(fileobj=compressedstream)
                data = gzipper.read()
                gzipper.close()
            url.close()
            
        if cj != None:
            urlParse = urlparse.urlparse(urlToOpen)
#             cj.save(COOKIEFILE, ignore_discard=True, ignore_expires=True)                     # save the cookies again
            cj.save(COOKIEFILE)                     # save the cookies again                
        return data
    
    def getReguestAndUrlOpen(self):
    # 31-08-04
    #v1.0.0 
    
    # cookie_example.py
    # An example showing the usage of cookielib (New to Python 2.4) and ClientCookie
    
    # Copyright Michael Foord
    # You are free to modify, use and relicense this code.
    # No warranty express or implied for the accuracy, fitness to purpose or otherwise for this code....
    # Use at your own risk !!!
    
    # If you have any bug reports, questions or suggestions please contact me.
    # If you would like to be notified of bugfixes/updates then please contact me and I'll add you to my mailing list.
    # E-mail michael AT foord DOT me DOT uk
    # Maintained at www.voidspace.org.uk/atlantibots/pythonutils.html
    
        COOKIEFILE = 'cookies.lwp'          # the path and filename that you want to use to save your cookies in
        import os.path
        
        cj = None
        cookielib = None
        
        try:                                    # Let's see if cookielib is available
            import cookielib            
        except ImportError:
            import urllib2
            urlopen = urllib2.urlopen
            Request = urllib2.Request
        else:
            import urllib2    
            urlopen = urllib2.urlopen
            cj = cookielib.LWPCookieJar()       # This is a subclass of FileCookieJar that has useful load and save methods
            Request = urllib2.Request
        
        ####################################################
        # We've now imported the relevant library - whichever library is being used urlopen is bound to the right function for retrieving URLs
        # Request is bound to the right function for creating Request objects
        # Let's load the cookies, if they exist. 
            
        if cj != None:                                  # now we have to install our CookieJar so that it is used as the default CookieProcessor in the default opener handler
            if os.path.isfile(COOKIEFILE):
                cj.load(COOKIEFILE)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            urllib2.install_opener(opener)
        
        # If one of the cookie libraries is available, any call to urlopen will handle cookies using the CookieJar instance we've created
        # (Note that if we are using ClientCookie we haven't explicitly imported urllib2)
        # as an example :
        
        theurl = 'http://www.diy.co.uk'         # an example url that sets a cookie, try different urls here and see the cookie collection you can make !
        txdata = None                                                                           # if we were making a POST type request, we could encode a dictionary of values here - using urllib.urlencode
        txheaders =  {'User-agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}          # fake a user agent, some websites (like google) don't like automated exploration
        
        try:
            req = Request(theurl, txdata, txheaders)            # create a request object
            handle = urlopen(req)                               # and open it to return a handle on the url
        except IOError, e:
            mess = 'We failed to open "%s".' % theurl
            if hasattr(e, 'code'):
                mess += '\nWe failed with error code - %s.' % e.code
                tkMessageBox.showerror('Error message', mess)
        else:
            mess = 'Here are the headers of the page :'
            mess += '\n' +  handle.info()                             # handle.read() returns the page, handle.geturl() returns the true url of the page fetched (in case urlopen has followed any redirects, which it sometimes does)
        
        print
        if cj == None:
            tkMessageBox.showerror('Error message', "We don't have a cookie library available - sorry.\nI can't show you any cookies.")
        else:
            cj.save(COOKIEFILE)                     # save the cookies again        
                                
class ScrolledList(tk.Frame):
    def __init__(self, master, threadSource = None):
        tk.Frame.__init__(self, master)
        self.message = tk.StringVar()
        self.threadSource = threadSource or self.menuSampleTest()
        self.message.set('        ')
        self.optHistory = []
        self.prevPointer = 0
        self.urlParams = {}
        self.makeWidgets()

    def menuSampleTest(self):
        xbmcMenu = menuThreads.menuThreads()
        params = {'url':'http://www.movie25.com', 'regexp':'<li><a href=\"(?P<url>.+?)\" title=\"(?P<label>.+?)\">'}
        xbmcMenu.createThread('thread', 'Movies', 'movies', params = params)    
        params = {'url':'http://www.movie25.com/new-releases/', 'regexp':'<h1><a href="(?P<url>.+?)".+?>\s*(?P<label>.+?)\s*</a></h1>', 'compflags':'re.DOTALL', 'nextregexp':"</font>&nbsp;<a href='(?P<url>.+?)'"}
        xbmcMenu.createThread('thread', 'List', 'list', params = params)    
        params = {'url':'http://www.movie25.com/murder-on-the-home-front-2013-47092.html', 'regexp':'<li class="link_name">\s*(?P<label>.+?)\s*</li>.+?<span><a href="(?P<url>.+?)"', 'compflags':'re.DOTALL'}
        xbmcMenu.createThread('thread', 'UrlResolvers', 'urlresolvers', params = params)    
        params = {'url':'http://www.movie25.tw/watch-school-dance-2014-48108-1171666.html', 'regexp':'onclick="location.href=\'(?P<url>.+?)\'"  value="Click Here to Play" />', 'compflags':'re.DOTALL'}
        xbmcMenu.setThreadParams('media', params)    
        
        xbmcMenu.setNextThread('movies', 'list')
        xbmcMenu.setNextThread('list', 'urlresolvers')
        xbmcMenu.setNextThread('urlresolvers', 'media')
        return xbmcMenu

    def select(self, index):
        self.listbox.focus_set()
        self.listbox.activate(index)
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(index)
        self.listbox.see(index)

    def up_event(self, event):
        selItem = self.listbox.index("active")
        if selItem == 0:
            selItem = self.listbox.size() - 1
        else:
            selItem -= 1
        self.select(selItem) 
        return "break"    

    def down_event(self, event):
        selItem = self.listbox.index("active")
        if selItem == self.listbox.size() - 1:
            selItem = 0
        else:
            selItem += 1
        self.select(selItem)
        return "break"    

    def handleList(self, event):
        index = self.listbox.curselection()                # on list double-click
        self.runCommand(index)                             # and call action here
                                                           # or get(ACTIVE)
    def makeWidgets(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        globFrame = tk.Frame(self)
        globFrame.pack(fill = tk.BOTH, expand = tk.YES)
        frame = tk.Frame(globFrame, relief = tk.SUNKEN)
        frame.pack(side = tk.LEFT, fill = tk.Y)
        sbar = tk.Scrollbar(frame)
        listBox = tk.Listbox(frame, selectmode = 'SINGLE', width = 50, relief=tk.SUNKEN, font = self.customFont)
        sbar.config(command=listBox.yview)                    # xlink sbar and list
        listBox.config(yscrollcommand=sbar.set)               # move one moves other
        sbar.pack(side=tk.RIGHT, fill=tk.Y)                      # pack first=clip last
        listBox.pack(side=tk.LEFT, fill=tk.BOTH)        # list clipped first
        listBox.bind('<<ListboxSelect>>', self.handleList)           # set event handler
        listBox.event_add('<<Execute Option>>','<Return>','<Double-Button-1>')
        listBox.bind('<<Execute Option>>', self.executeOption)
        listBox.bind('<Key-Up>', self.up_event)
        listBox.bind('<Key-Down>', self.down_event)
        self.listbox = listBox        
        
        labelPane = tk.Label(globFrame, textvariable = self.message, relief=tk.SUNKEN)
        labelPane.pack(side = tk.LEFT, fill = tk.BOTH, expand = tk.YES)

    def runCommand(self, index):                       # redefine me lower
        label = self.listbox.get(index)                # fetch selection text
        texto = 'You selected: \n' + label
        index = int(index[0])
        for key in sorted(self.options[index].keys()):
            texto = texto + '\n' + key + ' = \t' + str(self.options[index][key])
        self.message.set(texto)
        
    def initGlobals(self):
        theGlobals = {}
        exec 'import os' in theGlobals
        exec 'import urllib' in theGlobals
        exec 'import re' in theGlobals
        exec 'from basicFunc import openUrl, parseUrlContent, getMenu' in theGlobals
        exec 'from basicFunc import getMenuHeaderFooter, processHeaderFooter'  in theGlobals
        exec 'from basicFunc import LISTITEM_KEYS, INFOLABELS_KEYS' in theGlobals
#         theGlobals['getMenu'] = self.getMenu
#         theGlobals['parseUrlContent'] = self.parseUrlContent
        theGlobals['args'] = {}
        siteAPI = ''
        siteAPI += self.threadSource.scriptSource('rootmenu')
        siteAPI += self.threadSource.scriptSource('media', reverse = True)
        with open('siteAPI.py', 'w') as f:
            f.write(siteAPI)
        siteApiSrc = compile(siteAPI, 'siteAPI.py', 'exec')
        exec siteApiSrc in theGlobals
        self.theGlobals = theGlobals
        
    def initFrameExec(self):
#         self.threadSource = threadSource
        knotId = self.threadSource.threadDef
        self.initGlobals()
        option = {'menu':knotId, 'label':knotId, 'isFolder':True}
        if self.threadSource.getThreadAttr(knotId, 'type') == 'thread':
            url = self.threadSource.getThreadParam(knotId, 'url')
            option['url'] = [ url ]
            self.theGlobals['args'] = {'url':option['url']}
        self.message.set('        ')
        self.optHistory = []
        self.prevPointer = 0
        self.urlParams = {}
        self.optHistory = [[0, option]]
        self.fillListBox(knotId)


    def executeOption(self, event = None):
        index = int(self.listbox.curselection()[0])              # on list double-click
        option = self.options[index]
        pointer = self.prevPointer
        if option['label'] == "NotImplemented option": return
        if option['label'] != '..':
            if index != self.optHistory[pointer][0]:
                self.optHistory[pointer][0] = index
                self.optHistory = self.optHistory[:pointer+1]
            if pointer == len(self.optHistory)-1:
                self.optHistory.append([0, {}])
                self.optHistory[-1][1].update(option)
            pointer += 1
        else:
            pointer -= 1
        self.prevPointer = pointer
        selItem = self.optHistory[pointer][0]
        if option['isFolder']:
            knotId = option.pop('menu')
            self.theGlobals['args'] = option
            self.fillListBox(knotId, selItem)
        
    def fillListBox(self, threadKnot, selItem = 0):
        fillFunc = 'menuContent = ' + threadKnot + '()'
        if threadKnot != 'media':
            exec fillFunc in self.theGlobals
            menuContent = self.theGlobals.pop('menuContent')
        else:
            menuContent = []
        options = []
        for elem in menuContent:
            for key in elem[0].keys():
                if key != 'menu':
                    elem[0][key] = [str(elem[0][key])]
            options.append(elem[0])
            options[-1].update(elem[1])

        if threadKnot == 'media':
            if options:
                options[0]['label'] = 'url media'
            else:
                options.append({'label':'url media'})
  
        if self.prevPointer:
            head = {}
            pointer = self.prevPointer - 1
            head.update(self.optHistory[pointer][1])
            head['label'] = '..'
            options.insert(0, head)
        self.options = options 
        self.listbox.delete('0', 'end')
        for pos, item in enumerate(options):                              # add to listbox
            self.listbox.insert(pos, item['label'])                        # or insert(END,label)
        self.select(selItem) 
          
#     def openUrl(self, urlToOpen, validate = False):
#         headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
#         req = urllib2.Request(urlToOpen, None, headers)
#         try:
#             url = urllib2.urlopen(req)
#         except:
#             print('URL not Found: ', urlToOpen)
#             data = None
#         else:
#             if validate:
#                 data = url.geturl()
#             else:
#                 data = url.geturl(), url.read()
#             url.close()
#         return data
#     
#     def getMenu(self, url, menudef, optionMenu):
#         for key, value, in optionMenu.items():
#             if url.find(key) != -1: return value
#         return menudef
#     
#             
#     def parseUrlContent(self, url, regexp, compFlags = None, posIni = 0, posFin = 0):
#         url, data = self.openUrl(url)
#         scopeFlag = regexp.find('?#<SPAN') != -1
#         compFlags = compFlags if compFlags else 0
#         pattern = re.compile(regexp, flags = compFlags)
#         matchs = []
#         while 1:
#             match = pattern.search(data, posIni)
#             if not match: break
#             if posFin != 0 and  match.start(0) > posFin: break
#             matchDict = match.groupdict()
#             if scopeFlag:
#                 matchDict['span'] = (match.start(0), match.end(0))
#             # En este punto se normalizan los key de matchDict para que no tengan
#             # numeros al comienzo o al final
#             for elem in sorted(matchDict.keys()):
#                 if len(elem) != len(elem.strip('1234567890')):
#                     value = matchDict.pop(elem)
#                     if value:
#                         key = elem.strip('1234567890')
#                         if matchDict.get(key, None): value = matchDict[key] + ' ' + value
#                         matchDict[key] = value                
#             nxtposini = 'nxtposini' if matchDict.has_key('nxtposini') else 0
#             if nxtposini != 0: matchDict.pop(nxtposini)
#             posIni = match.end(nxtposini)
#             matchs.append(matchDict)
#         for key in ['url', 'videourl']:
#             if regexp.find('(?P<' + key) != -1:
#                 for elem in matchs:
#                     elem[key] = urlparse.urljoin(url, elem[key])
#         return matchs


#     def normUrl(self, urlBase, urlList):
#         import urlparse    
#         for k in range(len(urlList)):
#             url = urlparse.urljoin(urlBase,urlList[k]['url'])
#             urlList[k]['url'] = url
#         return urlList
            
        

class StatusBar(tk.Frame):
    def __init__(self, master, statusList):
        tk.Frame.__init__(self, master)
        self.setGUI(statusList)
        
    def setGUI(self, statusList):
        frame = tk.Frame(self, bd = 5)
        frame.pack(side = tk.TOP, fill = tk.X)
        label = tk.Label(frame, text = statusList[0][0], bd = 3)
        label.pack(side = tk.LEFT)
        label = tk.Label(frame, textvariable = statusList[0][1], bd = 3, relief = tk.SUNKEN, height = 1)
        label.pack(side = tk.LEFT)
        label = tk.Label(frame, text = statusList[1][0], bd = 3)
        label.pack(side = tk.LEFT)
        label = tk.Label(frame, textvariable = statusList[1][1], bd = 3, relief = tk.SUNKEN, height = 1)
        label.pack(side=tk.LEFT, fill = tk.X, expand = 1)
        label = tk.Label(frame, textvariable = statusList[2][1], bd = 3, relief = tk.SUNKEN, height = 1)
        label.pack(side = tk.RIGHT, fill = tk.X, expand = 1)
        label = tk.Label(frame, text = statusList[2][0], bd = 3)
        label.pack(side = tk.RIGHT)

        
class PythonEditor(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        self.prompt =''
        self.cellInput = ''
        self.hyperlinkManager = None

        scrollbar = tk.Scrollbar(self)
        scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
                
        textw = tk.Text(self, font = self.customFont, tabs=('1.5c'))
        textw.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=textw.yview)
        
        self.textw = textw 
        textw.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        textw.see('end')
        textw.event_add('<<CursorlineOff>>','<Up>','<Down>','<Next>','<Prior>','<Button-1>')
        textw.event_add('<<CursorlineOn>>','<KeyRelease-Up>','<KeyRelease-Down>','<KeyRelease-Next>','<KeyRelease-Prior>','<ButtonRelease-1>')
        textw.event_add('<<CopyEvent>>','<Control-C>','<Control-c>')
        textw.event_add('<<PasteEvent>>','<Control-V>','<Control-v>')
        textw.event_add('<<CutEvent>>','<Control-X>','<Control-x>')
        textw.event_add('<<SelAllEvent>>','<Control-A>','<Control-a>')
        
        textw.tag_configure('cursorLine', background = 'alice blue')
        textw.tag_configure('evenMatch', background = 'yellow')
        textw.tag_configure('oddMatch', background = 'red')
        textw.tag_configure('actMatch', background = 'light green')
        textw.tag_configure('group', foreground = 'blue')

        textw.tag_configure("hyper", foreground="blue", underline=1)
        textw.tag_bind("hyper", "<Enter>", self._enter)
        textw.tag_bind("hyper", "<Leave>", self._leave)
        textw.tag_bind("hyper", "<Button-1>", self._click)        
        
        
        
        self.dispPrompt()
        textw.bind('<<CopyEvent>>', self.selCopy)
        textw.bind('<<PasteEvent>>', self.selPaste)
        textw.bind('<<CutEvent>>', self.selCut)
        textw.bind('<<SelAllEvent>>',self.selAll)
        textw.bind('<<CursorlineOff>>', self.onUpPress)        
        textw.bind('<<CursorlineOn>>', self.onUpRelease)
        
    def _enter(self, event):
        self.textw.config(cursor="hand2")

    def _leave(self, event):
        self.textw.config(cursor="")

    def _click(self, event):
        for tag in self.textw.tag_names(tk.CURRENT):
            if tag == "hyper":
                tagRange = self.textw.tag_prevrange(tag, tk.CURRENT)
                texto = self.textw.get(*tagRange)
                self.processHyperlink(texto)
                return       
    def setHyperlinkManager(self, callbackFunction):
        self.hyperlinkManager = callbackFunction
        
    def processHyperlink(self, texto):
        if self.hyperlinkManager:
            self.hyperlinkManager(texto)
        
    def onUpPress(self, event = None):
        textw = self.textw
        textw.tag_remove('cursorLine', '1.0', 'end')
        
    def onUpRelease(self, event = None):
        textw = self.textw
        if textw.tag_ranges('sel'): return
        textw.tag_add('cursorLine', 'insert linestart', 'insert lineend + 1 chars')
        
    def getSelRange(self, tagName = 'sel'):
        textw = self.textw
        try:
            return textw.tag_ranges(tagName)
        except tk.TclError:
            return None
    
    def colorMatch(self, baseIndex, match, matchColor, frstMatch = False):
        tagIni = baseIndex + ' + %d chars'%match.start(0)
        tagFin = baseIndex + ' + %d chars'%match.end(0)
        try:
            self.textw.tag_add(matchColor, tagIni, tagFin)
        except:
            print 'exception: ' + matchColor + ' tagIni: ' + tagIni + ' tagFin: ' + tagFin
        self.textw.tag_add('matchTag', tagIni, tagFin)
        if frstMatch:
            self.textw.tag_add('actMatch', tagIni, tagFin) 
#             self.textw.mark_set('insert', tagIni)
#             self.textw.see('insert')
        return
        
        
    def getContent(self, posIni = '1.0', posFin = 'end'):
        textw = self.textw
        return textw.get(posIni, posFin)
    
    def setContent(self,text):
        self.textw.delete('1.0','end')
        if text: 
            self.textw.insert('1.0',text)
        
    def selDel(self, event = None):
        textw = self.textw
        selRange = self.getSelRange()
        if selRange: textw.delete(*selRange)
        
    def selPaste(self, event = None):
        textw = self.textw
        try:
            text = textw.selection_get(selection = 'CLIPBOARD')
            textw.insert('insert', text)
        except tk.TclError:
            pass
        
    def selCopy(self, event = None):
        textw = self.textw
        selRange = self.getSelRange()
        if selRange:
            text = textw.get(*selRange)
            textw.clipboard_clear()
            textw.clipboard_append(text)
        return selRange

    def selCut(self, event = None):
        textw = self.textw
        selRange = self.selCopy()
        if selRange: textw.delete(*selRange)

    def selAll(self, event = None):
        textw = self.textw
        textw.tag_add('sel', '1.0', 'end')
        
    def setCustomFont(self, tFamily = "Consolas", tSize = 18):
        self.customFont.configure(family = tFamily, size = tSize)

    def dispPrompt(self):
        self.textw.insert('insert', self.prompt)
        self.textw.insert('insert', self.cellInput)

    def isIndentModeOn(self):
        return len(self.cellInput) > 0

    def setNextIndentation(self,expr):
        if len(expr):
            nTabs = len(expr) - len(expr.lstrip('\t'))
            if expr[-1] == ':': nTabs += 1
            self.cellInput = nTabs * '\t'
        else:
            self.cellInput = ''
        
    def setKeyHandler(self, objInst):
        self.textw.bind('<Key>', objInst.keyHandler)


class RegexpFrame(tk.Frame):
    def __init__(self, master, xbmcThreads, messageVar):
        tk.Frame.__init__(self, master)
        self.xbmcThreads = xbmcThreads
        self.dropDownFiler = None
        self.popUpMenu = None

        self.queue = Queue.Queue(maxsize=0)
        self.activeCallBack = []
        self.threadFlag = 'stop'
        
        self.messageVar = messageVar
        self.setGUI()
        
    def initFrameExec(self):
        xbmcThreads = self.xbmcThreads
        activeKnotId = xbmcThreads.threadDef
        if xbmcThreads.getThreadAttr(activeKnotId, 'type') != 'thread': return
        urlToOpen = xbmcThreads.getThreadParam(activeKnotId, 'url')
        self.setActiveUrl(urlToOpen)
        compFlags = xbmcThreads.getThreadParam(activeKnotId, 'compflags')
        self.setCompFlags(compFlags)
        regexp = xbmcThreads.getThreadParam(activeKnotId, 'regexp')
        self.setRegexpPattern(regexp)
        
    def setGUI(self):
        self.customFont = tkFont.Font(family = 'Consolas', size = 18)
        
        self.urlFrame = NavigationBar(self)
        self.urlFrame.pack(fill = tk.X)
        self.urlFrame.setUrlContentProcessor(self.setContent)
        
        self.regexpFrame = RegexpBar(self, self.messageVar)
        self.regexpFrame.pack(fill = tk.X)
        self.regexpFrame.setDropDownFiler(self.fillDropDownLst)
        self.regexpFrame.setZoomManager(self.zoom)
        
        
        frame2 = tk.Frame(self)
        frame2.pack(fill = tk.BOTH, expand = 1)
        self.txtEditor = PythonEditor(frame2)
        self.txtEditor.setKeyHandler(self) 
        self.txtEditor.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
        self.txtEditor.setHyperlinkManager(self.setActiveUrl)        
        self.regexpFrame.setTextWidget(self.txtEditor.textw)
        self.txtEditor.textw.bind('<Button-3>',self.do_popup)
        
    def zoom(self, btnText):
        if btnText == 'ZoomIn':
            selRange = self.txtEditor.getSelRange() or self.txtEditor.getSelRange('actMatch') 
            if not selRange: return False
            texto = self.txtEditor.getContent(*selRange)
            self.setContent(texto, False)
        else:
            self.urlFrame.returnKey()
        return True
        
    def setDropDownFiler(self, callbckFunc):
        self.regexpFrame.setDropDownFiler(callbckFunc) 
                
    def fillDropDownLst(self):
        if self.dropDownFiler:
            theValues = self.dropDownFiler()
        else:
            theValues =  ['uno', 'dos', 'tres']
        self.entry.configure(values = theValues)
        
    def do_popup(self, event):
        if not self.popUpMenu: return
        popup = self.popUpMenu()        
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()
            
    def setPopUpMenu(self, popUpMenu):
        self.popUpMenu = popUpMenu
        
        

    def getMatchTag(self, nextMatch = True):
        seekFunc = self.txtEditor.textw.tag_nextrange if nextMatch else self.txtEditor.textw.tag_prevrange
        tag_names = self.txtEditor.textw.tag_names('insert')
        if ('evenMatch' in tag_names) or ('oddMatch' in tag_names) :
            nxtTag = 'evenMatch' if 'oddMatch' in tag_names else 'oddMatch'
            iniPos = 'insert + 1 char' if nextMatch else 'insert - 1 char'
            selTag = seekFunc(nxtTag, iniPos)
        else:
            selOdd = seekFunc('oddMatch', 'insert')
            selEven = seekFunc('evenMatch', 'insert')
            if selEven != selOdd:
                if selOdd == tuple(): selTag = selEven
                elif selEven == tuple(): selTag = selOdd
                elif map(int, selOdd[0].split('.')) < map(int, selEven[0].split('.')): selTag = selOdd if nextMatch else selEven
                else: selTag = selEven if nextMatch else selOdd
            else:
                selTag = tuple()            
        oddMatchs = self.txtEditor.textw.tag_ranges('oddMatch')
        evenMatchs = self.txtEditor.textw.tag_ranges('evenMatch')
        eotags = []
        if evenMatchs:
            for ene in range(len(evenMatchs)/2):
                eotags.extend([oddMatchs[2*ene], oddMatchs[2*ene + 1]])
                eotags.extend([evenMatchs[2*ene], evenMatchs[2*ene + 1]])
            if len(oddMatchs) > len(evenMatchs):
                eotags.extend([oddMatchs[-2], oddMatchs[-1]])
        else:
            eotags = oddMatchs
        matchTags = map(str,eotags)
        nMatchs = len(matchTags)/2
        if selTag != tuple():
            nPos = [valor for k, valor in enumerate(matchTags) if not k%2].index(selTag[0]) + 1
        else:
            nPos = 1 if nextMatch else nMatchs
            selTag = (matchTags[0], matchTags[1]) if nextMatch else (matchTags[-2], matchTags[-1])
        matchStr = ' '  + str(nPos) + ' de ' + str(nMatchs)

        self.txtEditor.textw.tag_remove('actMatch', '1.0', 'end')
        self.txtEditor.textw.tag_add('actMatch', *selTag)
        self.txtEditor.textw.mark_set('insert', selTag[0])
        self.txtEditor.textw.see(selTag[1 if nextMatch else 0])            
        self.matchLabel.config(text=matchStr, bg = 'SystemButtonFace')
        self.actMatch(selTag)
        
    def keyHandler(self,event):
        textw =  event.widget
        if textw == self.txtEditor.textw and event.keysym not in  ['Left', 'Right', 'Up','Down','Next','Prior','Button-1']:
            return "break"

    def getSelRange(self):
        return self.txtEditor.getSelRange()

    def setContent(self, data, newUrl = True):
        if newUrl: self.regexpFrame.setZoomType('ZoomIn')
        self.txtEditor.setContent(data)
        self.regexpFrame.getPatternMatch()
        
    def pasteFromClipboard(self, event = None):
        textw = self.txtEditor.textw
        try:
            data = textw.selection_get(selection = 'CLIPBOARD')
            self.setContent(data)
        except tk.TclError:
            pass

    def getContent(self, posIni = '1.0', posFin = 'end'):
        return self.txtEditor.getContent(posIni, posFin)
            
    def getRegexpPattern(self):
        return self.regexpFrame.getRegexpPattern()

    def getCompFlags(self):
        return self.regexpFrame.getCompFlags()
    
    def setRegexpPattern(self, regexp):
        self.regexpFrame.setRegexpPattern(regexp)
        
    def setCompFlags(self, compflags):
        self.regexpFrame.setCompFlags(compflags)            
            
            
    def setActiveUrl(self, url):
        self.urlFrame.setActiveUrl(url)
        
    def getActiveUrl(self):
        return self.urlFrame.getActiveUrl()
        
class NodeEditFrame(tk.Frame):
    def __init__(self, master = None, xmlFile = 'NodeSettingFile.xml', dheight = 600, dwidth = 400):
        tk.Frame.__init__(self, master, height = dheight, width = dwidth)
        self.root = ET.parse(xmlFile).getroot()
        self.rightPane = None
        self.settings = None
        self.setGUI()
        self.notifyChangeTo = None
        
    def setNotifyChange(self, notifyto):
        self.notifyChangeTo = notifyto
        
    def setGUI(self):
        bottomPane = tk.Frame(self, relief = tk.RIDGE, bd = 5, bg = 'white', padx = 3, pady = 3)
        bottomPane.pack(side = tk.BOTTOM, fill = tk.X)
        for label in ['Discard', 'Apply']:
            boton = tk.Button(bottomPane, name = label.lower() , text = label, width = 20, command = lambda action = label.lower(): self.onAction(action))
            boton.pack(side = tk.RIGHT)
        label = tk.Label(bottomPane, name = 'message', text = '')
        label.pack(side = tk.LEFT, fill = tk.X, expand = 1)
        self.bottomPane = bottomPane
            
    def onAction(self, action):
        toProcess = self.rightPane.getChangeSettings(dict(self.settings))
        if action == 'apply':
            self.processChangedSettings(toProcess)
        elif action == 'discard':
            if not toProcess: return
            reset = toProcess.pop('reset')
            toProcess.update([(key, 1) for key in reset])
            filterFlag = lambda widget: (hasattr(widget, 'id') and toProcess.has_key(widget.id)) 
            widgets = [(widget.id, widget) for child, widget in self.rightPane.frame.children.items() if filterFlag(widget)]
            for key, widget in widgets:
                if self.settings.has_key(key):
                    widget.setValue(self.settings[key])
                else:
                    widget.setValue(widget.default)
        
    def processChangedSettings(self, changedSettings):
        if not changedSettings: return
        nodeId = self.settings['nodeId']
        nodeParams = self.xbmcThreads.getThreadAttr(nodeId,'params')
        parameters = {}
        
        if changedSettings.has_key('otherparameters') or 'otherparameters' in changedSettings['reset']:
            if self.settings.has_key('otherparameters'):
                oldOther = [tuple(elem.split(',')) for elem in self.settings['otherparameters'].split('|')]
                for key, value in oldOther:
                    nodeParams.pop(key)
        for key in changedSettings.pop('reset'):
            self.settings.pop(key)
            if nodeParams.has_key(key): nodeParams.pop(key)
        if changedSettings.get('otherparameters', None):
#             if self.settings.has_key('otherparameters'):
#                 oldOther = [tuple(elem.split(',')) for elem in self.settings['otherparameters'].split('|')]
#                 for key, value in oldOther:
#                     nodeParams.pop(key)
            otherParameters = [tuple(elem.split(',')) for elem in changedSettings['otherparameters'].split('|')]
            parameters.update(otherParameters)
        for elem in  set(changedSettings.keys()).difference(['otherparameters', 'nodeId', 'upmenu', 'name']):
            parameters[elem] = changedSettings[elem]
        if parameters: nodeParams.update(parameters)

        nodeFlag = nodeId in ['media', 'rootmenu']
        if nodeFlag:
            for key in ['nodeId', 'name', 'upmenu']: 
                if changedSettings.has_key(key): changedSettings.pop('nodeId')

        lstChanged = []
        if changedSettings.has_key('nodeId'):
            lstChanged.append(self.xbmcThreads.getDotPath(self.settings['nodeId']))
            self.xbmcThreads.rename(self.settings['nodeId'], changedSettings['nodeId'])
            lstChanged.append(self.xbmcThreads.getDotPath(changedSettings['nodeId']))
            nodeId = changedSettings['nodeId']
        if changedSettings.has_key('name'):
            self.xbmcThreads.parseThreads[nodeId]['name'] = changedSettings['name']
        if changedSettings.has_key('upmenu') and changedSettings['upmenu'] != self.settings['up']:
            upmenu = changedSettings['upmenu']
            kType = self.xbmcThreads.getThreadAttr(nodeId, 'type')
            threadIn = (upmenu, nodeId) if kType == 'list' else (nodeId, upmenu)
            lstChanged.append(self.xbmcThreads.getDotPath(nodeId))
            self.xbmcThreads.setNextThread(*threadIn)
            lstChanged.append(self.xbmcThreads.getDotPath(nodeId))
        self.settings.update(changedSettings)
        if self.notifyChangeTo: self.notifyChangeTo(True, lstChanged)

    def initFrameExec(self, xbmcThreads, param = False):
        self.xbmcThreads = xbmcThreads
        if self.rightPane: self.rightPane.forget()
        activeNodeId = xbmcThreads.threadDef
        nodeType = self.xbmcThreads.getThreadAttr(activeNodeId, 'type')
        srchStr = './/category[@label="' + nodeType + '"]'
        nodeConfigData = self.root.findall(srchStr)
        if not nodeConfigData: return
        nodeConfigData = nodeConfigData[0]
        settings = self.getNodeSettings(activeNodeId, nodeType, nodeConfigData)
        self.settings = settings
        self.rightPane = scrolledFrame(self, settings, nodeConfigData)
        self.rightPane.pack(side = tk.TOP, fill = tk.BOTH, expand = 1)
        btnState = self.xbmcThreads.getThreadParam(activeNodeId, 'enabled') == None
        message = '' if btnState else 'Code Locked'
        btnState = tk.NORMAL if btnState else tk.DISABLED
        self.bottomPane.children['apply'].configure(state = btnState)
        self.bottomPane.children['discard'].configure(state = btnState)
        self.bottomPane.children['message'].configure(text = message)
        
        
    def getNodeSettings(self, nodeId, nodeType, nodeConfigData):
        nodeDataIds = [key.get('id') for key in nodeConfigData.findall('setting') if key.get('id', None)]
        settings = dict(self.xbmcThreads.parseThreads[nodeId])
        params = settings.pop('params')
        settings['nodeId'] = nodeId
        if settings.has_key('up'):
            upMenu = ''
            if nodeType == 'list':
                lista = [elem for elem in self.xbmcThreads.getSameTypeNodes('rootmenu') if not elem.endswith('_lnk')]
                upMenu = '|'.join(sorted(lista))
            elif nodeType == 'thread':
                upMenu = '|'.join(sorted(self.xbmcThreads.getSameTypeNodes('media'))) if nodeId != 'media' else '' 
            upMenu = settings['up'] + '|' + upMenu
            settings['upmenu'] = upMenu
        other = set(params.keys()).difference(nodeDataIds)
        if len(other):
            params = dict(params)
            otherParameters = '|'.join([key + ', ' + str(params.pop(key)) for key in other])
            settings['otherparameters'] = otherParameters
        settings.update(params)
        return settings
        
        
        
# import keyword
# class CodeFrame(tk.Frame):
#     def __init__(self, master):
#         tk.Frame.__init__(self, master)
#         self.stopFlag = False
#         self.activeCallBack = []        
#         self.queue = Queue.Queue(maxsize=0)
#         self.fileListProv = None
#         self.isCoderSet = False
#         self.sintaxForColor = [self.pythonSintax, self.errorSintax, self.errorSintax]
#         self.setGUI()
#         
#     def setFileListProv(self, callBackFunction):
#         self.fileListProv = callBackFunction
#         
#     def initFrameExec(self, coder, param = False):
#         if param or not self.isCoderSet:
#             self.coder = coder
#             self.isCoderSet = True
#             self.fillDropDownLst()
#             self.fileChsr.current(0)
#             self.sntxIndx.set(0)
#         activeKnotId = self.coder.getActiveNode()
#         srchStr = 'def ' + activeKnotId + '():'
#         srchIndx = self.textw.search(srchStr, '1.0')
#         if srchIndx:
#             self.textw.mark_set('insert', srchIndx) 
#             self.textw.see('insert')
#             self.onUpRelease()
#             self.textw.focus_set()
#             
#     def setContentToNodeCode(self, nodeId, incDownThread = False):
#         if incDownThread:
#             codeStr = self.coder.scriptSource(nodeId)
#         else:
#             codeStr = self.coder.knothCode(nodeId)
#         self.setContent(codeStr)
#             
# 
#     def pasteFromClipboard(self, event = None):
#         textw = self.textw
#         try:
#             data = textw.selection_get(selection = 'CLIPBOARD')
#             self.setContent(data)
#         except tk.TclError:
#             pass
#         self.formatContent()
# 
#     def setGUI(self):
#         self.customFont = tkFont.Font(family = 'Consolas', size = 18)
# 
#         topPane = tk.Frame(self)
#         topPane.pack(side = tk.TOP, fill = tk.X)
#         intVar = tk.IntVar()
#         intVar.trace('w', self.changeDisplay)
#         self.sntxIndx = intVar
#         for k, elem in enumerate(['Code', 'Errors/Warnings', 'xbmclog']):
#             boton = tk.Radiobutton(topPane, text = elem, width = 30, value = k, variable = intVar, indicatoron = 0)
#             boton.pack(side = tk.LEFT)
#         intVar = 0
#         
#         self.pythonFile = tk.StringVar()
#         self.pythonFile.trace("w", self.getPythonFile)
#         self.fileChsr = ttk.Combobox(topPane, textvariable = self.pythonFile)
#         self.fileChsr.configure(postcommand = self.fillDropDownLst)
#         self.fileChsr.pack(side=tk.RIGHT)
#         
#         self.prompt =''
#         self.cellInput = ''
# 
#         scrollbar = tk.Scrollbar(self)
#         scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
#         
#         textw = tk.Text(self, font = self.customFont, tabs=('1.5c'))
#         textw.pack(side = tk.LEFT, fill = tk.BOTH, expand = 1)
#         textw.config(yscrollcommand=scrollbar.set)
#         scrollbar.config(command=textw.yview)
# 
#         self.textw = textw
#         textw.see('end')
#         textw.event_add('<<Copy>>','<Control-C>','<Control-c>')
#         textw.event_add('<<Paste>>','<Control-V>','<Control-v>')
#         textw.event_add('<<Cut>>','<Control-X>','<Control-x>')
#         textw.event_add('<<Selall>>','<Control-A>','<Control-a>')
#         textw.event_add('<<CursorlineOff>>','<Up>','<Down>','<Next>','<Prior>','<Button-1>')
#         textw.event_add('<<CursorlineOn>>','<KeyRelease-Up>','<KeyRelease-Down>','<KeyRelease-Next>','<KeyRelease-Prior>','<ButtonRelease-1>')
#         textw.tag_configure('pythonNumber', foreground = 'IndianRed')
#         textw.tag_configure('pythonFunction', font = ('Consolas', 18, 'bold'))
#         textw.tag_configure('pythonKwd', foreground = 'blue')
#         textw.tag_configure('pythonMultilineString', foreground = 'lime green')
#         textw.tag_configure('pythonString', foreground = 'lime green')
#         textw.tag_configure('pythonComment', foreground = 'red')
#         textw.tag_configure('pythonTag')
#         textw.tag_configure('cursorLine', background = 'alice blue')
#         
#         textw.tag_configure('errError', background = 'red')
#         textw.tag_configure('errWarning', background = 'yellow')
#         
#         textw.tag_config("hyper", foreground="blue", underline=1)
#         textw.tag_bind("hyper", "<Enter>", self._enter)
#         textw.tag_bind("hyper", "<Leave>", self._leave)
#         textw.tag_bind("hyper", "<Button-1>", self._click)        
#         
#         
# 
#         self.dispPrompt()
#         textw.bind('<Key>', self.keyHandler)
#         textw.bind('<<Copy>>', self.selCopy)
#         textw.bind('<<Paste>>', self.selPaste)
#         textw.bind('<<Cut>>', self.selCut)
#         textw.bind('<<Selall>>',self.selAll)
#         textw.bind('<<CursorlineOff>>', self.onUpPress)        
#         textw.bind('<<CursorlineOn>>', self.onUpRelease)
#         
#     def _enter(self, event):
#         self.textw.config(cursor="hand2")
# 
#     def _leave(self, event):
#         self.textw.config(cursor="")
# 
#     def _click(self, event):
#         for tag in self.textw.tag_names(tk.CURRENT):
#             if tag == "hyper":
#                 tagRange = self.textw.tag_prevrange(tag, tk.CURRENT)
#                 texto = self.textw.get(*tagRange)
#                 result = re.match('File "(?P<filename>[^"]+)", line (?P<line>[0-9]+), in (?P<function>[\w<>]+)', texto)
#                 filename = result.groupdict()['filename']
#                 filename = os.path.basename(filename)
#                 line = result.groupdict()['line'] + '.0'
#                 self.sntxIndx.set(0)
#                 self.pythonFile.set(filename)
#                 self.textw.mark_set('insert', line) 
#                 self.textw.see('insert')
#                 self.onUpRelease()
#                 self.textw.focus_set()
#                 return       
#         
#         
#     def getPythonFile(self, *args, **kwargs):
#         selection = self.fileChsr.current()
#         content = ''
#         if selection != -1:
#             fileOut, fileType, fileSrc = self.listaPy[selection]
#             if fileType == 's':
#                 content = fileSrc
#             elif fileType == 'f':
#                 with open(fileSrc, 'r') as f:
#                     content = f.read()
#         return content
# #         self.__setContent__(content)
# 
#             
#     
#     def fillDropDownLst(self):
#         dropDownContent = []
#         if self.fileListProv:
#             lista =  self.fileListProv()
#             self.listaPy = [pFile for pFile in lista if pFile[0].endswith('.py')]
#             dropDownContent = map(os.path.basename, [elem[0] for elem in self.listaPy])
#         self.fileChsr.configure(values = dropDownContent)
#         
#     def onUpPress(self, event = None):
#         textw = self.textw
#         textw.tag_remove('cursorLine', '1.0', 'end')
#         
#     def onUpRelease(self, event = None):
#         textw = self.textw
#         if textw.tag_ranges('sel'): return
#         textw.tag_add('cursorLine', 'insert linestart', 'insert lineend + 1 chars')
#         
#     def getSelRange(self):
#         textw = self.textw
#         try:
#             return textw.tag_ranges('sel')
#         except tk.TclError:
#             return None
#         
#     def longProcess(self, baseIndex, content):
#         toColor = self.setRegexPattern()
#         pos = 0
#         anchor = baseIndex
#         while self.stopFlag:
#             matchs = [reg.search(content, pos) for tag, reg in toColor]
#             if not any(matchs): 
#                 break
#             match, k = min([(match.start(0), k) for k, match in enumerate(matchs) if match])
#             tagIni = baseIndex + ' + %d chars'%matchs[k].start(0)
#             tagFin = baseIndex + ' + %d chars'%matchs[k].end(0)
#             self.queue.put((toColor[k][0], anchor, tagIni, tagFin))
#             anchor = tagFin
#             pos = matchs[k].end(0)
#         self.stopFlag = False
#             
#     def queueConsumer(self):
#         nProcess = 100
#         while nProcess and not self.queue.empty():
#             tagTxt, anchor, tagStart, tagEnd = self.queue.get()
#             for tag in [tagname for tagname in self.textw.tag_names() if tagname.startswith('python')]:
#                 self.textw.tag_remove(tag, anchor, tagEnd)
#             self.textw.tag_add(tagTxt, tagStart, tagEnd)
#             if tagTxt != 'pythonFunction': self.textw.tag_add('pythonTag', tagStart)
#             self.textw.update()
#             nProcess -= 1 
#         if not self.queue.empty(): self.activeCallBack.append(self.after(50, self.queueConsumer))
#         
#     def setRegexPattern(self):
#         sntxIndx = self.sntxIndx.get()
#         return self.sintaxForColor[sntxIndx]()
# 
#     def errorSintax(self):
#         basePath = re.escape(os.path.dirname(self.listaPy[0][0]))
#         toColor = []
#         toColor.append(('errError', r'ERROR:'))
#         toColor.append(('errWarning',r'WARNING:'))
#         toColor.append(('hyper', 'File "' + basePath + '[^"]+", line [0-9]+, in [\w<>]+'))
#         for k in range(len(toColor)):
#             tag, regexp = toColor[k]
#             flags = 0
#             toColor[k] = (tag, re.compile(regexp, flags))
#         return toColor
#         
#     def pythonSintax(self):
#         toColor = []
#         toColor.append(('pythonNumber', r'(\d+[.]*)+'))
#         toColor.append(('pythonFunction',r'(?<=def)\s+(\b.+?\b)'))
#         toColor.append(('pythonFunction',r'(?<=class)\s+(\b.+?\b)'))
#         toColor.append(('pythonKwd',r'\b(' + '|'.join(keyword.kwlist + ['True', 'False', 'None']) + r')\b')) 
#         toColor.append(('pythonComment', r'#.*$'))
#         toColor.append(('pythonMultilineString', r'(\"\"\"|\'\'\').*?\1|(\"\"\"|\'\'\').+'))
#         toColor.append(('pythonString', r'(?<!\\)(\'|\").*?((?<!\\)\1|$)'))
#         
#         for k in range(len(toColor)):
#             tag, regexp = toColor[k]
#             flags = re.MULTILINE if tag != 'pythonMultilineString' else re.DOTALL
#             toColor[k] = (tag, re.compile(regexp, flags))
#             
#         return toColor  
#         
# 
#     def formatContent(self,index1 = '1.0', index2 = 'end'):
#         while self.activeCallBack:
#             idAfter = self.activeCallBack.pop()
#             self.after_cancel(idAfter)
#         self.queue.queue.clear()
#         if self.stopFlag:
#             self.stopFlag = False
#             if self.t.isAlive(): self.t.join(10)
#         textw = self.textw
#         content = textw.get(index1, index2)
# 
#         baseIndex = textw.index(index1)
#         
#         
#         if not self.stopFlag:
#             self.stopFlag = True
#             from threading import Thread
#             self.t = Thread(name="regexpThread", target=self.longProcess, args=(baseIndex, content))
#             self.t.start()
#             self.activeCallBack.append(self.after(50, self.queueConsumer))
#         
#     def getContent(self):
#         textw = self.textw
#         content = textw.get('1.0','end')
#         indx = self.fileChsr.current()
#         if indx == -1: return content, 'o', 'custom.py'
#         if self.listaPy[indx][1] == 's':
#             return (content, self.listaPy[indx][1], self.pythonFile.get())
#         elif self.listaPy[indx][1] == 'f':
#             return (content, self.listaPy[indx][1], self.listaPy[indx][2])
#         
#     def setContent(self, text):
#         self.pythonFile.set('custom.py')
#         self.__setContent__(text)
#         
#     def __setContent__(self,text):
#         self.textw.delete('1.0','end')
#         self.textw.insert('1.0',text)
#         self.formatContent()
#         
#     def selDel(self, event = None):
#         textw = self.textw
#         selRange = self.getSelRange()
#         if selRange: textw.delete(*selRange)
#         
#     def selPaste(self, event = None):
#         textw = self.textw
#         try:
#             text = textw.selection_get(selection = 'CLIPBOARD')
#             baseIndex = textw.index('insert')
#             textw.insert('insert', text)
#         except tk.TclError:
#             pass
#         self.formatContent(baseIndex, 'end')
#         return 'break'
#         
#     def selCopy(self, event = None):
#         textw = self.textw
#         selRange = self.getSelRange()
#         if selRange:
#             text = textw.get(*selRange)
#             textw.clipboard_clear()
#             textw.clipboard_append(text)
#         return selRange
# 
#     def selCut(self, event = None):
#         textw = self.textw
#         selRange = self.selCopy()
#         if selRange: textw.delete(*selRange)
# 
#     def changeDisplay(self, *args, **kwargs):
#         if self.sntxIndx.get() == 0:
#             content = self.getPythonFile()
#         elif self.sntxIndx.get() == 1:
#             content = self.coder.ERRORS
#         elif self.sntxIndx.get() == 2:
#             logfile = os.path.join(translatePath('special://logpath'), 'kodi.log')
#             with open(logfile, 'r') as f:
#                 content = f.read()
#         self.__setContent__(content)
# 
#     def selAll(self, event = None):
#         textw = self.textw
#         textw.tag_add('sel', '1.0', 'end')
#         
#     def setCustomFont(self, tFamily = "Consolas", tSize = 18):
#         self.customFont.configure(family = tFamily, size = tSize)
# 
#     def dispPrompt(self):
#         self.textw.insert('insert', self.prompt)
#         self.textw.insert('insert', self.cellInput)
# 
#     def isIndentModeOn(self):
#         return len(self.cellInput) > 0
# 
#     def setNextIndentation(self,expr):
#         if len(expr):
#             nTabs = len(expr) - len(expr.lstrip('\t'))
#             if expr[-1] == ':': nTabs += 1
#             self.cellInput = nTabs * '\t'
#         else:
#             self.cellInput = ''
# 
#     def keyHandler(self,event):
#         textw =  event.widget
#         selRange = self.getSelRange()
#         if event.keysym == 'Return':
#             if selRange: textw.delete(*selRange)
#             strInst = textw.get('insert linestart', 'insert lineend')
#             self.setNextIndentation(strInst) 
#             textw.insert('insert', '\n')
#             self.dispPrompt()
#         elif event.keysym == 'BackSpace':
#             if not selRange: selRange = ("%s-1c" % tk.INSERT,)
#             textw.delete(*selRange)
#         elif  event.keysym == 'Delete':
#             if not selRange: selRange = ("%s" % tk.INSERT,)
#             textw.delete(*selRange)
#         elif len(event.char) == 1:
#             if selRange: textw.delete(*selRange)
#             textw.insert('insert', event.char)
#         else:
#             return
# 
#         frstIndx = textw.tag_prevrange('pythonTag', 'insert')
#         frstIndx = frstIndx[0] if frstIndx else '1.0'
#         self.formatContent(frstIndx, 'end')
#         return "break"

import xbmcStubs.collapsingFrame as collapsingFrame
import KodiLog
import SintaxEditor
class addonFilesViewer(collapsingFrame.collapsingFrame):
    def __init__(self, master):
        collapsingFrame.collapsingFrame.__init__(self, master, tk.HORIZONTAL, buttConf = 'mRM')
        self.pack_propagate(flag = False)
        
        self.sintaxEditor = SintaxEditor.SintaxEditor(self.frstWidget)
        self.sintaxEditor.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        self.textw = self.sintaxEditor.textw

        self.kodiFrame = KodiLog.kodiLog(self.scndWidget)
        self.kodiFrame.config(height = 200)
        self.kodiFrame.pack(side = tk.TOP, fill = tk.BOTH, expand = tk.YES)
        self.kodiFrame.pack_propagate(flag = False)
#         self.collapseCommand(0)

    
    def setHyperlinkManager(self, hyperLinkProcessor):
        self.kodiFrame.setHyperlinkManager(hyperLinkProcessor)

    def initFrameExec(self):
        pass
    
    def __getattr__(self, attr):
        if attr != 'sintaxEditor': return getattr(self.sintaxEditor, attr)
        else:  raise AttributeError, attr
        
            


class parseTree(tk.Frame):
    def __init__(self, master, xbmcThread):
        tk.Frame.__init__(self, master)
        self.setXbmcThread(xbmcThread)
        self.popUpMenu = None
        self.setGUI()
        
    def setXbmcThread(self, xbmcThread):
        self.xbmcThread = xbmcThread
        self.refreshFlag = True
        
    def setGUI(self):
        treeview = ttk.Treeview(self, show = 'tree', columns = ('name', ), displaycolumns = ())
        treeview.pack(fill = tk.BOTH, expand = tk.YES)
        treeview.event_add('<<myEvent>>','<Double-1>','<Return>')
        treeview.bind('<Button-3>',self.do_popup)
        treeview.tag_configure('activeThread', background = 'light green')
        self.treeview = treeview
        self.actTreeSel = None
        
    def refreshPaneInfo(self):
        if self.refreshFlag and self.xbmcThread:
            if self.treeview.exists('rootmenu'): self.treeview.delete('rootmenu')
            if self.treeview.exists('media'): self.treeview.delete('media')
            self.registerTreeNodes('rootmenu')
            self.registerTreeNodes('media')
        self.refreshFlag = False
        self.activeNode = None
        self.setActualKnot()
    
    def getPopUpMenu(self, threadId = None):
        popup = tk.Menu(self, tearoff = 0)
        if threadId: popup.add_command(label = threadId)
        popup.add_command(label = 'Set as ActiveKnot', command = self.onTreeSelProc)
        popup.add_command(label = 'Previous')
        popup.add_separator()
        popup.add_command(label = 'Home')
        return popup
    
    def do_popup(self, event):
        if not self.popUpMenu: return
        threadId = self.treeview.identify_row(event.y)
        self.xbmcThread.threadDef = threadId.rsplit('.', 1)[1] if threadId.find('.') != -1 else threadId
        self.setSelection(threadId)
        popup = self.popUpMenu()        
        try:
            popup.post(event.x_root, event.y_root)
        finally:
            popup.grab_release()

            
    def setPopUpMenu(self, popUpMenu):
        self.popUpMenu = popUpMenu

    def setOnTreeSelProc(self, onTreeSelProc):
        self.onTreeSelProc = onTreeSelProc 
        self.treeview.bind('<<myEvent>>', self.onTreeSelProc)
        
    def setActualKnot(self):
        if not self.xbmcThread: return
        if self.xbmcThread.existsThread(self.activeNode) and self.activeNode != self.xbmcThread.threadDef:
            iid = self.getAbsoluteId(self.activeNode, absFlag = False)
            tags = self.treeview.item(iid, 'tags')
            tags = [tag for tag in tags if tag != 'activeThread']
            self.treeview.item(iid, tags = tags)
            
        if self.xbmcThread.threadDef:
            iid = self.getAbsoluteId(self.xbmcThread.threadDef, absFlag = False)
            tags = self.treeview.item(iid, 'tags')
            tags = list(tags).append('activeThread') if tags else ('activeThread',)
            self.treeview.item(iid, tags = tags)
            self.activeNode = self.xbmcThread.threadDef      
        
    def refreshTreeInfo(self, activeThread = None, lstChanged = None):
        if not activeThread: activeThread = self.xbmcThread.threadDef
        if not lstChanged: return
        while lstChanged:
            threadId = lstChanged.pop()
#             if threadId.endswith('_lnk') and threadId.startswith('media'): continue 
            if self.treeview.exists(threadId): 
                self.delete(threadId)
            else:
                parentId, sep, threadId = threadId.rpartition('.') 
                self.registerTreeNodes(threadId)
                self.treeItemExpand(parentId, absFlag = True, flag = True)
        self.setSelection(activeThread, absFlag = False)
#         self.parseTree.setSelection(parseKnotId, absFlag = False)
        

    
    def getAbsoluteId(self, threadId, absFlag = True):
        return threadId if absFlag else self.xbmcThread.getDotPath(threadId)
    
    def registerTreeNodes(self, threadId = 'media'):
        threadKnots = self.xbmcThread.getSameTypeNodes(threadId)
        itemId = self.getAbsoluteId(self.xbmcThread.threadDef, absFlag = False)
        leaves = [itemId]
        for elem in threadKnots:
            if elem.endswith('_lnk') and not self.xbmcThread.getThreadParam(elem, 'source'): continue
            itemId = self.getAbsoluteId(elem, absFlag = False)
            itemParams = [itemId, {}]
            itemParams[1]['name'] = elem
            leaves.append(itemParams)
    
        for elem in leaves[1:]:
            self.registerNode(elem[0], childName = True)
            for dKey, dValue in elem[1].items():
                self.treeview.set(elem[0], column = dKey, value = dValue)
    
        selItem = leaves[0]
        if self.treeview.exists(selItem):
            while selItem.rpartition('.')[1]:
                self.treeview.item(selItem.rpartition('.')[0], open = True )
                selItem = selItem.rpartition('.')[0]
            self.treeview.selection_set(leaves[0])
            self.treeview.focus(leaves[0])

    def registerNode(self, iid, childName = False, absFlag = True):
        iid = self.getAbsoluteId(iid, absFlag)
        if self.treeview.exists(iid): return
        iidPart = iid.rpartition('.')
        if len(iidPart[1]) and not self.treeview.exists(iidPart[0]):
            self.registerNode(iidPart[0], childName)
        self.treeview.insert(iidPart[0], 'end',iid)
        if childName:
            self.treeview.item(iid, text = iidPart[2])
        
    def treeItemExpand(self, threadId, absFlag = True, flag = True):
        itemId = self.getAbsoluteId(threadId, absFlag)
        self.treeview.item(itemId, open = flag )  
        
    def delete(self, *items):
        items = [thread for thread in items if self.treeview.exists(thread)]
        if items: self.treeview.delete(*items)   
        
    def setSelection(self, threadId, absFlag = True):
        iid = self.getAbsoluteId(threadId, absFlag)
        self.setActualKnot()        
        self.treeview.focus(iid)
        self.treeview.selection_set(iid)

        
class EditTransaction(tkSimpleDialog.Dialog):

    def __init__(self, master, xbmcMenu):
        self.xbmcMenu = xbmcMenu
        self.index = xbmcMenu.threadDef
        self.setFocus = None
        self.tr = tk.StringVar()
        self.tr.trace('w', self.setDlgVars)

        self.comVar = {}
        self.keyNames = ['name', 'up']
        if xbmcMenu.getThreadAttr(xbmcMenu.threadDef, 'type') == 'thread':
            self.keyNames.extend(['url', 'regexp', 'compflags', 'nextregexp']) 
        for key in self.keyNames:
            self.comVar[key] = tk.StringVar()
        return tkSimpleDialog.Dialog.__init__(self, master, 'Edit Parse Knot')
        
    def setDlgVars(self, *args, **kwargs):
        threadId = self.tr.get()
        kType = self.xbmcMenu.getThreadAttr(self.xbmcMenu.threadDef, 'type')
        if kType == 'thread':
            params = self.xbmcMenu.getThreadAttr(threadId,'params')
            for key in self.keyNames:
                if params.get(key,None): 
                    self.comVar[key].set(params[key])
                else:
                    self.comVar[key].set('')
        self.comVar['name'].set(self.xbmcMenu.getThreadAttr(threadId,'name'))
        if self.xbmcMenu.getThreadAttr(threadId,'up'):
            self.comVar['up'].set(self.xbmcMenu.getThreadAttr(threadId,'up'))

    def body(self, master):
        master.config(relief=tk.GROOVE, bd=4)
        self.tr.set(self.index)
        kType = self.xbmcMenu.getThreadAttr(self.xbmcMenu.threadDef, 'type')
        if self.tr:
            lista = self.xbmcMenu.listKnots(knothType = kType)
            listKnots = ttk.Combobox(master, textvariable=self.tr)
            listKnots['values'] = tuple(sorted(lista))
            listKnots.configure(width=45)
            listKnots.pack(side=tk.TOP, pady=10)

        self.topGrid = tk.Frame(master)
        self.topGrid.pack(side=tk.TOP, padx=10, pady=10)
        self.topGrid.grid_columnconfigure(0, pad=20)
        
        for pos, key in enumerate(self.keyNames):
            if key == 'up': continue
            tk.Label(self.topGrid, text=key).grid(column=0, row=pos)
            ce = tk.Entry(self.topGrid, textvariable=self.comVar[key], width=45)
            ce.grid(column=1, row=pos)
            
        # Send Output To:
        texto = 'Send Output To:' if kType == 'thread' else 'Get Input From:' 
        pos = len(self.keyNames) + 2
        tk.Label(self.topGrid, text=texto).grid(column=0, row=pos)
        listKnots = ttk.Combobox(self.topGrid, textvariable=self.comVar['up'])        
        listKnots.configure(width=45)
        listKnots.grid(column=1, row=pos)

        lista = self.xbmcMenu.listKnots(knothType = kType)
        listKnots['values'] = tuple(sorted(lista))


    def apply(self):
        if self.tr.get() == self.comVar['up'].get(): return
        threadId = self.tr.get()
        for key in self.keyNames:
            if key == 'up': continue
            if self.xbmcMenu.getThreadAttr(threadId, key):
                self.xbmcMenu.parseThreads[threadId][key] = self.comVar[key].get()
            else:
                params = self.xbmcMenu.getThreadAttr(threadId, 'params')
                params[key] = self.comVar[key].get()
        if  self.comVar['up'].get() != self.xbmcMenu.getThreadAttr(threadId, 'up'):
            kType = self.xbmcMenu.getThreadAttr(threadId, 'type')
            toThread = self.comVar['up'].get()
            threadIn = (toThread, threadId) if kType == 'list' else (threadId, toThread)
            self.result = [self.xbmcMenu.getDotPath(threadId)]
            self.xbmcMenu.setNextThread(*threadIn)
            self.result.append(self.xbmcMenu.getDotPath(threadId))
        parseThread = self.xbmcMenu.parseThreads[threadId]
        for key in parseThread.keys():
            if parseThread[key] == '': parseThread.pop(key)
        params = self.xbmcMenu.getThreadAttr(threadId, 'params')
        for key in params.keys():
            if params[key] == '': params.pop(key)
        self.xbmcMenu.threadDef = threadId
            

class ParseThreads(tk.Toplevel):
    def __init__(self, xbmcMenu):
        tk.Toplevel.__init__(self)
        self.protocol('WM_DELETE_WINDOW', self.Close)
        self.setGUI(xbmcMenu)

    def Close(self):
        self.destroy()

    def setGUI(self, xbmcMenu):
        frame = tk.Frame(self)
        frame.pack(fill = tk.BOTH, expand = 1)
        
        uno = tk.StringVar()
        uno.set('Este es el campo 1')
        dos = tk.StringVar()
        dos.set('Segundo mensaje')
        tres = tk.StringVar()
        tres.set('No hay dos sin tres')
        self.statusBar = StatusBar(frame,[('uno: ', uno),
                                    ('dos: ', dos),
                                    ('tres: ', tres)
                                    ])
        self.statusBar.pack(side = tk.BOTTOM, fill = tk.X, expand = 1)
        
        options = (('Lumberjack-%s' % x) for  x in range(20))  # or map/lambda, [...]
        
        m1 = tk.PanedWindow(frame, sashrelief = tk.SUNKEN, bd = 10)
        m1.pack(side = tk.TOP, fill=tk.BOTH, expand=tk.YES)
#         self.leftPane = RegexpFrame(m1)
        self.leftPane = ScrolledList(m1, None) 
        self.leftPane.pack(fill = tk.X, expand=tk.YES)
        self.leftPaneFlag = True
        m1.add(self.leftPane)
        self.button = tk.Button(m1, text = "Run", command = self.toggleLeftPane)
        m1.add(self.button)
        self.m1 = m1
        self.xbmcMenu = xbmcMenu
        
        

    def toggleLeftPane(self, *args, **kwargs):
        self.m1.forget(self.leftPane)
        if not self.leftPaneFlag:
            self.m1.paneconfigure(self.leftPane, before = self.button )
        self.leftPaneFlag = not self.leftPaneFlag

if __name__ == "__main__":
    
    xbmcMenu = menuThreads.menuThreads()
    xbmcMenu.createThread('list', 'rootMenu', 'rootmenu')
    xbmcMenu.createThread('thread', 'Ultimos Cap�tulos', 'lchapter', params = {'url':'http://www.seriales.us', 'regexp':'<li><a href=\"([#].+?)\" title=\".+?\">(.+?)</a>'})
    xbmcMenu.createThread('thread', 'Ultimas Series Agregadas', 'lseries', params = {'url':'http://www.seriales.us', 'regexp':'<div class=\"bl\"> <a href=\"(.+?)\" title=\"(.+?)\">'})
    xbmcMenu.createThread('thread', 'Genero', 'genero', params = {'url':'http://www.seriales.us', 'regexp':'^<li><a href=\"(.+?)\" class=\"let\">(.+?)</a></li>', 'compflags':'re.MULTILINE'})
    xbmcMenu.createThread('thread', 'Lista Completa de Series', 'all', params = {'url':'http://www.seriales.us', 'regexp':'<li class=\".+?\"><a href=\"(.+?)\" title=\".+?\">(.+?)</a>'})    
    xbmcMenu.createThread('thread', 'A-Z', 'a_z', params = {'url':'http://www.seriales.us', 'regexp': '<li><a href=\"(.+?)\" class=\"let\">[#A-Z]</a></li>'})
    xbmcMenu.createThread('thread', 'Buscar', 'buscar', params = {'url':'http://www.seriales.us'})
    xbmcMenu.createThread('thread', 'Temporadas', 'temporadas', params = {'regexp' : '<div class=\"bl\"> <a href=\"(.+?)\" title=\"(.+?)\">'})
    xbmcMenu.createThread('thread', 'Cap�tulos', 'capitulos', params = {'regexp' : "<li class=\'lcc\'><a href=\'(.+?)\' class=\'lcc\'>(.+?)</a>"})
    xbmcMenu.createThread('thread', 'Resolvers', 'resolvers', params = {'regexp' : '<li><a href=\"([#].+?)\" title=\".+?\">(.+?)</a>'})
    xbmcMenu.createThread('thread', 'Media', 'media')
    
    xbmcMenu.setNextThread('all', 'temporadas')
    xbmcMenu.setNextThread('temporadas', 'capitulos')
    xbmcMenu.setNextThread('capitulos', 'resolvers')
    xbmcMenu.setNextThread('resolvers', 'media')
  
    xbmcMenu.setNextThread('lseries', 'capitulos')
    xbmcMenu.setNextThread('lchapter', 'resolvers')
    xbmcMenu.setNextThread('genero', 'temporadas')
    xbmcMenu.setNextThread('a_z', 'temporadas')
    xbmcMenu.setNextThread('buscar', 'temporadas')
    
    
    Root = tk.Tk()
    Root.withdraw()
    ParseThreads(xbmcMenu)
    Root.mainloop()




