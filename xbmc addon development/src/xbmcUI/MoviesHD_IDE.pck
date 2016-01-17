["sortedlist", {"rootmenu_sortedlist_lnk": {"sibling": "search", "type": "link", "up": "sortedlist", "params": {}, "name": "rootmenu"}, "sortedlist_rootmenu_lnk": {"type": "link", "params": {"source": true}, "name": "sortedlist", "up": "rootmenu"}, "search": {"params": {"url": "http://movieshd.eu/?s=minions", "regexp": "(?#<SEARCH>)http://movieshd.eu/?<search>", "searchkeys": "Movies*s", "compflags": "0"}, "type": "thread", "name": "Search", "up": "sortedlist"}, "media": {"down": "sortedlist", "params": {"url": "http://movieshd.eu/HD-Stream1/watch-contact-1997-online.html", "regexp": "(?#<iframe src=url>)", "compflags": "re.DOTALL", "enabled": false}, "type": "thread", "name": "media"}, "rootmenu": {"down": "sortedlist_rootmenu_lnk", "params": {"discrim": "option"}, "type": "list", "name": "rootmenu"}, "years": {"sibling": "rootmenu_sortedlist_lnk", "type": "thread", "up": "sortedlist", "name": "Years", "params": {"url": "http://movieshd.eu/year", "regexp": "(?#<li img.src=iconImage a.href=url .span.*=label>)", "compflags": "0"}}, "sortedlist": {"down": "categories", "params": {"url": "http://movieshd.eu/?filtre=date&cat=0", "compflags": "re.DOTALL", "op_addonInfo": "movie*\\s*(?P<name>[^(]+?)\\s+\\((?P<year>\\d+)\\)", "headregexp": "Sort by: <->(?#<div class=\"filtre-container\" span.*=label>)|(?#<ul class=\"filtre-list\" .li<a.href=url a.*=label>*>)", "regexp": "(?#<li img.src=iconImage a.href=url .span.*=label>)", "contextmenus": "Movie Information,XBMC.Action(Info)", "nextregexp": "nextLink\":\"(?P<url>http[^\"]+)\""}, "type": "thread", "name": "All Movies", "up": "media"}, "categories": {"sibling": "years", "type": "thread", "up": "sortedlist", "name": "Categories", "params": {"url": "http://movieshd.eu/categories", "regexp": "(?#<li img.src=iconImage a{href=url span.*=label} span.*=label3>)", "compflags": "re.DOTALL"}}}]
{"addon_id": "plugin.video.movieshdide", "addon_requires": "xbmc.python,2.1.0,|script.module.urlresolver,2.4.0,|script.module.metahandler,2.9.0,", "addon_name": "Movies HD IDE", "addon_resources": "basicFunc.py,resources/lib,True,basicFunc.py|teleresolvers.py,resources/lib,True,teleresolvers.py|CustomRegEx.py,resources/lib,True,CustomRegEx.py", "addon_fanart": "C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.movieshd/fanart.jpg", "addon_icon": "C:/Users/Alex Montes Barrios/AppData/Roaming/Kodi/addons/plugin.video.movieshd/icon.png"}
{"media": "def media():\n    import teleresolvers\n    import CustomRegEx\n    url = args.get('url')[0]\n    pattern = r'(?#<iframe src=videoUrl>)'\n    content = openUrl(url)[1]\n    videoUrl = CustomRegEx.search(pattern, content).group('videoUrl')\n    host, media_id = re.search(r\"https://(.+?)\\..+?/embed/(.+?)/\", videoUrl).groups()\n    resolver = getattr(teleresolvers, host, None)\n    if not resolver: return\n    dialog = xbmcgui.Dialog()\n    try:\n        url = resolver(media_id)\n    except:\n        dialog.notification('Url error', 'It was imposible to parse url', xbmcgui.NOTIFICATION_INFO, 5000)\n    else:\n        dialog.notification('Url success', 'Url parsed', xbmcgui.NOTIFICATION_INFO, 5000)\n    \n    li = xbmcgui.ListItem(path = url)\n    if args.get(\"icondef\", None): li.setThumbnailImage(args[\"icondef\"][0])\n    if args.get(\"labeldef\", None): li.setLabel(args[\"labeldef\"][0])\n    li.setProperty('IsPlayable', 'true')\n    li.setProperty('mimetype', 'video/x-msvideo')\n    return xbmcplugin.setResolvedUrl(handle=addon_handle,succeeded=True,listitem=li)\n"}