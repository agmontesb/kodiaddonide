
def rootmenu():
    menuContent = []
    menuContent.append([{'menu': u'mmoviesStrm'}, {'isFolder': True, 'label': u'movies_strm'}, None])
    menuContent.append([{'menu': u'tv_series'}, {'isFolder': True, 'label': u'tv_series'}, None])
    return menuContent

def mmoviesStrm():
    menuContent = []
    menuContent.append([{u'url': u'http://www.free-tv-video-online.me/movies/', 'menu': u'AtoZ'}, {'isFolder': True, 'label': u'A-Z'}, None])
    menuContent.append([{u'url': u'http://projectfreetv.so/movies/', 'menu': 'latest'}, {'isFolder': True, 'label': u'latest'}, None])
    menuContent.append([{u'url': u'http://projectfreetv.so/movies/', 'menu': u'genre'}, {'isFolder': True, 'label': u'genre'}, None])
    menuContent.append([{u'url': u'http://projectfreetv.so/movies/', 'menu': u'years'}, {'isFolder': True, 'label': u'years'}, None])
    return menuContent

def tv_series():
    menuContent = []
    menuContent.append([{u'url': u'http://projectfreetv.so/calendar/', 'menu': u'calendar'}, {'isFolder': True, 'label': u'calendar'}, None])
    menuContent.append([{u'url': u'http://projectfreetv.so/watch-tv-series/', 'menu': u'series_A_Z'}, {'isFolder': True, 'label': u'series_A_Z'}, None])
    return menuContent

def series_A_Z():
    url = args.get("url")[0]
    regexp = r'(?#<SPAN>)<h4 id="[^"]+">(?P<label>.+?)</h4>.+?</div>'
    url, data = openUrl(url)
    compflags = re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'series_list'})
        paramDict.update(elem)
        paramDict["url"] = url
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def series_list():
    url = args.get("url")[0]
    limInf, limSup = eval(args.get("span", ["(0,0)"])[0])
    regexp = r'<li><a title="(?P<label>[^"]+)" href="(?P<url>[^"]+)">'
    url, data = openUrl(url)
    compflags = re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags, posIni = limInf, posFin = limSup)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'seasons'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def seasons():
    url = args.get("url")[0]
    regexp = r'<li class="[^"]+"><a href="(?P<url>[^"]+)" >(?P<label>.+?)</a>(?P<label1>.+?)</li>'
    url, data = openUrl(url)
    compflags = re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'episode_list'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def episode_list():
    url = args.get("url")[0]
    regexp = r'<div align="left">.+?<a href="(?P<url>[^"]+)">(?P<label>.+?)</a>'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'resolvers'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def calendar():
    url = args.get("url")[0]
    regexp = r'(?#<SPAN>)<div class=\'column5\'><h4 class=\'[^\']{0,}\'>(?P<label>.+?)</h4>.+?</ul></div></div>'
    url, data = openUrl(url)
    compflags = re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'day_list'})
        paramDict.update(elem)
        paramDict["url"] = url
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def day_list():
    url = args.get("url")[0]
    limInf, limSup = eval(args.get("span", ["(0,0)"])[0])
    regexp = r'<a href=\'(?P<url>[^\']+)\'>(?P<label>.+?)</a>'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags, posIni = limInf, posFin = limSup)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'resolvers'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def AtoZ():
    url = args.get("url")[0]
    regexp = r'<a class="char" href="(?P<url>browse/.+?.html)">(?P<label>[#A-Z])</a>'
    url, data = openUrl(url)
    compflags = 0
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': u'movies'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def years():
    url = args.get("url")[0]
    regexp = r'<a .+?href="(?P<url>.+?\d{4})".+?<b>(?P<label>.+?)</b>'
    url, data = openUrl(url)
    compflags = re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': 'latest'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def genre():
    url = args.get("url")[0]
    regexp = r'<a .+?href="(?P<url>.+?/)".+?<b>(?P<label>.+?)</b>'
    url, data = openUrl(url)
    compflags = 0
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': 'latest'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def latest():
    url = args.get("url")[0]
    footmenu = [['Next Page >>>', '</span></li><li><a rel='nofollow' href='(?P<url>[^']+)' class='inactive'>(?P<label>[^<]+)</a>']]
    if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)
    regexp = r'<div class="post excerpt ">\W+<a href="(?P<url>[^"]+)" title="(?P<label>[^"]+)".+?<img  src="(?P<iconImage>[^"]+)"'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'az'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def az():
    url = args.get("url")[0]
    regexp = r'(?#<SPAN>)<a name="(?P<label>[#A-Z])">.+?(<td colspan="2">|<!-- Start of the latest link tables -->)'
    url, data = openUrl(url)
    compflags = re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': u'movies'})
        paramDict.update(elem)
        paramDict["url"] = url
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def movies():
    url = args.get("url")[0]
    limInf, limSup = eval(args.get("span", ["(0,0)"])[0])
    regexp = r'<a href="(?P<url>[^>]+?)"><b>(?P<label>.+?)</b></a>'
    url, data = openUrl(url)
    compflags = 0
    subMenus = parseUrlContent(url, data, regexp, compflags, posIni = limInf, posFin = limSup)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': u'resolvers'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def resolvers():
    url = args.get("url")[0]
    regexp = r'<td><a href="(?P<url>[^"]+)" target="_blank" rel="nofollow"><img src="(?P<thumbnailImage>[^"]+)" width="16" height="16"> &nbsp;(?P<label>[^<]+)</a>'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'menu': u'media'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def media():
    import urlresolver
    url = args.get("url")[0]
    regexp = '<a rel="nofollow" href="(?P<videourl>[^"]+)">'
    url, data = openUrl(url)
    compflags =re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags )
    videoUrl = subMenus[0]["videourl"]
    url = urlresolver.HostedMediaFile(url = videoUrl).resolve()
    li = xbmcgui.ListItem(path = url)
    if args.get("icondef", None): li.setThumbnailImage(args["icondef"][0])
    if args.get("labeldef", None): li.setLabel(args["labeldef"][0])
    li.setProperty('IsPlayable', 'true')
    li.setProperty('mimetype', 'video/x-msvideo')
    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)
