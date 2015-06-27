#! python3
import xbmc, xbmcaddon, xbmcgui, xbmcplugin, xbmcvfs
print(xbmc.CAPTURE_FLAG_CONTINUOUS, xbmcaddon.Addon('plugin.video.youtube').addonId)
input('presione enter para continuar')