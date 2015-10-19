
def rootmenu():
    args["url"] = ['http://www.tube8.com']
    return Content()

def Content():
    url = args.get("url")[0]
    regexp = r'<li [^>v]*>\W+<a href="(?P<url>[^"]+)">(?P<label>[^<]+)</a>'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'listaVideos'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def listaVideos():
    url = args.get("url")[0]
    headmenu = [[u'Categories: ', u'(?#<SPAN>)(?s)<div class="selected-filter sortBtn" id="categoriesBtn">\\W+<div class="arrow"></div>\\W+(?P<label>[^<]+)</div>.+?</ul>|<li><a href="(?P<url>[^"]+)" >(?P<label>[^<]+)</a></li>'], [u'Sort By: ', u'(?#<SPAN>)(?s)</div>\\W+(?P<label>[^<]+)</div>\\W+<ul [^>]*id="sortByList"[^>]*>.+?</ul>|<li><a href="(?P<url>[^"]+)" >(?P<label>[^<]+)</a></li>'], [u'Time Added: ', u'(?#<SPAN>)(?s)</div>\\W+(?P<label>[^<]+)</div>\\W+<ul [^>]*id="timeAddedList"[^>]*>.+?</ul>|<li><a href="(?P<url>[^"]+)" >(?P<label>[^<]+)</a></li>'], [u'Duration: ', u'(?#<SPAN>)(?s)</div>\\W+(?P<label>[^<]+)</div>\\W+<ul [^>]*id="durationList"[^>]*>.+?</ul>|<li><a href="(?P<url>[^"]+)" >(?P<label>[^<]+)</a></li>']]
    footmenu = [['Next Page >>>', '</span></b>\W+</li>\W+<li>\W+<b><a href="(?P<url>[^"]+)">']]
    if args.has_key("section"):
        fhmenu = headmenu if args["section"][0] == "header" else footmenu
        url = processHeaderFooter(args.pop("section")[0], args, fhmenu)
    regexp = r'<img class="videoThumbs.+?src="(?P<iconImage>[^"]+)".+?<a href="(?P<videoUrl>[^"]+)" title="(?P<label>[^"]+)">(?P=label)</a>'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'': u'', 'menu': u'media'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def media():      # Modified code
    import sesame
    url = args.get("videoUrl", None)[0]
    regexp = '"video_title":"(?P<videotitle>.+?)",.+?,"video_url":"(?P<encvideourl>.+?)"'
    compflags = re.DOTALL
    url, data = openUrl(url)
    subMenus = parseUrlContent(url, data, regexp, compflags )
    videoTitle = subMenus[0]['videotitle']
    videoUrl = subMenus[0]['encvideourl'].replace('\/', '/')
    url = sesame.decrypt(videoUrl, videoTitle, 256)

    li = xbmcgui.ListItem(path = url)
    li.setProperty('IsPlayable', 'true')
    li.setProperty('mimetype', 'video/x-msvideo')
    return xbmcplugin.setResolvedUrl(handle     = addon_handle, succeeded=True, listitem=li)

