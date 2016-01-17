
def rootmenu():
    menuContent = []
    args["url"] = ["http://www.primewire.ag/"]
    menuContent.extend(nav_tabs())
    menuContent.append([{'menu': u'buscar', u'searchkeys': u'Title*search_keywords+Director*director+Starring*actor_name+Country*country'}, {'isFolder': True, 'label': u'Buscar'}, None])
    return menuContent

def buscar():
    if args.has_key('searchkeys'):
        searchKeys = args.get('searchkeys')[0]
        searchKeys = searchKeys.split('+')
        menuContent = []
        for elem in searchKeys:
            searchLabel, searchId = map(lambda x: x.strip(), elem.split('*'))
            menuContent.append([{'searchid':searchId, 'menu': 'buscar'}, {'isFolder': True, 'label': 'buscar by ' + searchLabel}, None])            
        return menuContent
    import xml.etree.ElementTree as ET
    searchId     = args.get('searchid', ['all'])[0]
    savedsearch = xbmc.translatePath('special://profile')
    savedsearch = os.path.join(savedsearch, 'addon_data', 'plugin.video.1channelide','savedsearch.xml')
    root = ET.parse(savedsearch).getroot() if os.path.exists(savedsearch) else ET.Element('searches')
        
    if not args.has_key("tosearch") and os.path.exists(savedsearch):
        existsSrch = root.findall("search")
        if searchId != "all":
            existsSrch = [elem for elem in existsSrch if elem.get("searchid") == searchId] 
        menuContent = [] 
        for elem in existsSrch:
           menuContent.append([{'menu':elem.get('menu'), 'url':elem.get('url')}, {'isFolder': True, 'label': elem.get('tosearch')}, None])
        if menuContent:
            menuContent.insert(0,[{'menu':'buscar', 'tosearch':'==>', 'searchid':searchId}, {'isFolder': True, 'label': 'Search by ' + searchId}, None])
            return menuContent

    kb = xbmc.Keyboard("", "Search for " + searchId , False)
    kb.doModal()
    if not (kb.isConfirmed()):return EMPTYCONTENT
    srchLabel = kb.getText()
    toSearch = (searchId + "=" if searchId != 'all' else "") + urllib.quote_plus(srchLabel) 
    srchUrl = "https://www.primewire.ag/?<search>&sort=release".replace("<search>", toSearch)
    existsSrch = [elem for elem in root.findall("search") if elem.get("url") == srchUrl]
    args["url"] = [srchUrl]    
    menuContent = pwire_copy()
    if menuContent and not existsSrch:
        toInclude = ET.Element('search', url = srchUrl, tosearch = srchLabel, menu = "pwire_copy", searchid = searchId)
        root.insert(0, toInclude)
        if not os.path.exists(os.path.dirname(savedsearch)):os.mkdir(os.path.dirname(savedsearch)) 
        ET.ElementTree(root).write(savedsearch)
    return menuContent

def pwire_copy():
    url = args.get("url")[0]
    footmenu = [['Next Page >>>', '</span> <a href="(?P<url>.+?)">']]
    if args.has_key("section"): url = processHeaderFooter(args.pop("section")[0], args, footmenu)
    regexp = r'<div class="index_item index_item_ie">\s*?<a href="(?P<url>.+?)" title="Watch (?P<label>.+?)"><img src="(?P<iconImage>.+?)" [^>]+>'
    url, data = openUrl(url)
    compflags = re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'': u'', 'menu': u'pagediscrim', u'icondefflag': 1, u'labeldefflag': 1})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent or EMPTYCONTENT

def pagediscrim():
    optionMenu = {u'TV Show': u'season'}
    menuDef = "listadded"
    url = args.get("url")[0]
    regexp = r'<title>[^<]+\((?P<discrim>.+?)\)[^<]+</title>'
    compflags = 0
    urldata = openUrl(url, validate = False)[1]
    match = re.search(regexp, urldata, compflags)
    nxtmenu = getMenu(match.group(1), menuDef, optionMenu) if match else menuDef         
    return globals()[nxtmenu]()

def nav_tabs():
    url = args.get("url")[0]
    regexp = r'<li class="[un]*pressed"><a href="(?P<url>[^"]+)" title="[WLP].+?">(?P<label>.+?)</a></li>'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    optionMenu = {u'3': u'playlist_list'}
    menuDef = "pwire_movies"
    menuContent = []
    for k, elem in enumerate(subMenus):
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        menu = optionMenu.get(str(k), menuDef)
        itemParam["isFolder"] = menu != "media"
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'plainnode': 1})
        paramDict.update(elem)
        paramDict["menu"] = menu
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def pwire_movies():
    url = args.get("url")[0]
    headmenu = [[u'Genre: ', u'<span>([^ ]+) [^>]+> <strong>[^<]+</strong></span>|<li><a href="(?P<url>[^"]+genre=[^&"]+)">(?P<label>.+?)</a></li>'], [u'Sort by: ', u'<span>[^>]+> <strong>([^<]+)</strong></span>|<li><a href="(?P<url>[^"]+&*sort=[^"]+)">(?P<label>.+?)</a></li>']]
    footmenu = [[u'Get Next Page >>>', u'<a href="(?P<url>[^"]+page[^"]+)">(?P<label>.+?)</a>']]
    if args.has_key("section"):
        fhmenu = headmenu if args["section"][0] == "header" else footmenu
        url = processHeaderFooter(args.pop("section")[0], args, fhmenu)
    regexp = r'<div class="index_item index_item_ie">\s*?<a href="(?P<url>.+?)" title="Watch (?P<label>.+?)"><img src="(?P<iconImage>.+?)" [^>]+>'
    url, data = openUrl(url)
    compflags = re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    optionMenu = {u'?tv': u'season'}
    menu = getMenu(url, "listadded", optionMenu)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'labeldefflag': 1, u'icondefflag': 1})
        paramDict.update(elem)
        paramDict["menu"] = menu
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def playlist_list():
    url = args.get("url")[0]
    headmenu = [[u'Sort by ', u'<span class="index_show_by_selected"><a [^>]+>(.+?)</a></span>|<span class="index_show_by_(?:not)*selected"><a href="(?P<url>.+?)">(?P<label>.+?)</a></span>']]
    footmenu = [['Next Page >>>', '</span> <a href="(?P<url>.+?)">(?P<label>.+?)<']]
    if args.has_key("section"):
        fhmenu = headmenu if args["section"][0] == "header" else footmenu
        url = processHeaderFooter(args.pop("section")[0], args, fhmenu)
    regexp = r'<td width="90">.+?src="(?P<iconImage>[^"]+)".+?<strong><a href="(?P<url>.+?)">(?P<label>.+?)</a>(?P<label1>.+?)</strong>'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'playlist_media', u'option': u'3'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    menuContent = getMenuHeaderFooter("header", args, data, headmenu) + menuContent
    menuContent += getMenuHeaderFooter("footer", args, data, footmenu)
    return menuContent

def playlist_media():
    url = args.get("url")[0]
    regexp = r'<img src="(?P<iconImage>[^"]+)".+?<a href="(?P<url>[^"]+)">(?P<label>[^<]+)</a> (?P<label1>\( [\d]+ \))'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    optionMenu = {u'/tv-': u'season'}
    menuDef = "listadded"
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        menu = getMenu(elem["url"], menuDef, optionMenu)
        itemParam["isFolder"] = menu != "media"
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'labeldefflag': 1, u'urlin': u'/tv-', u'icondefflag': 1})
        paramDict.update(elem)
        paramDict["menu"] = menu
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def season():
    url = args.get("url")[0]
    regexp = r'<h2>\W+<a data-id="\d+" class="season-toggle" href="(?P<url>.+?)">&#9658; (?P<label>.+?)<span'
    url, data = openUrl(url)
    compflags = 0
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'episode', u'urlin': u'?tv', u'urldata': u'TV Show', u'urlout': u'/tv-'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def episode():
    url = args.get("url")[0]
    regexp = r'<div class="tv_episode_item"> <a href="(?P<url>.+?)">(?P<label>E[0-9]+)\W+?<span class="tv_episode_name">(?P<label1>.+?)</span>'
    url, data = openUrl(url)
    compflags = re.DOTALL
    subMenus = parseUrlContent(url, data, regexp, compflags)
    contextMenu = {"lista":[(u'', u'')], "replaceItems":False}
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = True
        otherParam = {}
        otherParam["contextMenu"] = dict(contextMenu)
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({u'': u'', u'labeldefflag': 1, u'icondefflag': 1, 'menu': u'listadded'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def listadded():
    url = args.get("url")[0]
    regexp = r'<span class="movie_version_link">\s*?<a href="(?P<url>[^"]+?)".+?writeln\(\'(?P<label>.+?)\'\)'
    url, data = openUrl(url)
    compflags = re.DOTALL|re.IGNORECASE
    subMenus = parseUrlContent(url, data, regexp, compflags)
    menuContent = []
    for elem in subMenus:
        itemParam = dict([(key,elem.pop(key)) for key  in elem.keys() if key in LISTITEM_KEYS])
        itemParam["isFolder"] = False
        otherParam = {}
        paramDict = dict([(key, value[0]) for key, value in args.items() if hasattr(value, "__getitem__") and key not in ["header", "footer"]])
        paramDict.update({'menu': u'media'})
        paramDict.update(elem)
        menuContent.append([paramDict, itemParam, otherParam])
    return menuContent

def media():      # Modified code
    import urlresolver
    url = openUrl(args.get("url")[0], validate = True)
    if not url.startswith("http://www.primewire.ag"):
        regexp = r'http://(?P<videoHost>[^/]+)/(?P<videoId>[^.]+)'
        match = re.search(regexp, url)
        url = urlresolver.HostedMediaFile(host = match.group("videoHost"), media_id = match.group("videoId")).resolve()
    else:
        regexp = '<noframes>(?P<videourl>[^<]+)</noframes>'
        compflags =re.DOTALL
        url, data = openUrl(url)
        subMenus = parseUrlContent(url, data, regexp, compflags )
        videoUrl = subMenus[0]["videourl"]
        url = urlresolver.HostedMediaFile(url = videoUrl).resolve()
    li = xbmcgui.ListItem(path = url)
    if args.get("icondef", None): li.setThumbnailImage(args["icondef"][0])
    if args.get("labeldef", None): li.setLabel(args["labeldef"][0])
    li.setProperty('IsPlayable', 'true')
    li.setProperty('mimetype', 'video/x-msvideo')
    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)

