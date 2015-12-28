# -*- coding: UTF-8 -*-
# *  GNU General Public License for more details.
# *
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *
# *  based on https://gitorious.org/iptv-pl-dla-openpli/ urlresolver
# */
from StringIO import StringIO
import json
import re
import CustomRegEx
import string
import urlparse
import basicFunc
import base64
import urllib
import operator as op

MOBILE_BROWSER = "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"
DESKTOP_BROWSER = "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"

def fromJscriptToPython(strvar):
    n = 0
    while 1:
        m = re.search(r'[;{}]', strvar)
        if not m:break
        if m.group() == '{':
            n += 1
            strvar = strvar[:m.start()] + '\n' + n*'\t' + strvar[m.end():]
        elif m.group() == '}':
            n -=1
        else:
            strvar = strvar[:m.start()] + '\n' + strvar[m.end():]
    return strvar            
strvar = """eval(function(p,a,c,k,e,d){e=function(c){return c.toString(36)};if(!\'\'.replace(/^/,String)){while(c--){d[c.toString(a)]=k[c]||c.toString(a)}k=[function(e){return d[e]}];e=function(){return\'\\\\w+\'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp(\'\\\\b\'+e(c)+\'\\\\b\',\'g\'),k[c])}}return p}(\'$("4").5("3","2://0.1.6.7/c/d.b?a=8&9=e");\',15,15,\'aa6|cdn|http|src|video|attr|vizplay|org|9VECn4qJ9eja2lxhz5ynjQ|hash|st|mp4|v|4da9d8f843be8468108d62cb506cc286|JLTFS3sQtGbdyTgq4hJSLA\'.split(\'|\'),0,{}))"""




def unescStr(encStr):
    dec = 'ABCDEF'
    enc = set(re.findall(r'[A-Z]', encStr))
    head = ''.join(sorted(enc.difference(dec)))
    tail = ''.join(sorted(enc.intersection(dec)))
    enc = head + tail
    dec = dec[:len(enc)]
    ttable = string.maketrans(enc, dec)
    return urllib.unquote(encStr.translate(ttable))

def intBaseN(value, base, strVal = ''):
    assert 1 < base <= 64, 'Base must be 1 < base <= 64 '
    strVal = strVal or '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    string = ''
    while value:
        string = strVal[value%base]
        value = value/base
    return string


def baseNtoInt(string, base, strVal = ''):
    assert 1 < base <= 64, 'Base must be 1 < base <= 64 '
    strVal = strVal or '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    value = 0
    pot = 1
    for k in range(len(string)-1, -1, -1):
        value += pot*strVal.index(string[k])
        pot *= base
    return value


def videomega(videoId, encHeaders = ''):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyz'
    url = 'http://videomega.tv/cdn.php?ref=%s' % (videoId)
    if encHeaders: url = url + encHeaders
    content = basicFunc.openUrl(url)[1]
    pattern = "\(\'(?P<patron>\$.+?;)\'.+?\'(?P<lista>.+?)\'"
    m = re.search(pattern, content)
    patron, lista = m.groups()
    lista = lista.split('|')
    repFunc = lambda x: lista[strVal.index(x.group())] or x.group()
    content = re.sub(r'\b\w+\b', repFunc, patron)
    m = re.search('\"(http.+?)\"', content)
    urlStr = m.group(1)
    return urlStr
    
    

def netu(videoId, encHeaders = ''):
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Content-Type': 'text/html; charset=utf-8'}
    player_url = "http://hqq.tv/player/embed_player.php?vid=%s&autoplay=no" % videoId
    data = basicFunc.openUrl(player_url, False)[1]
    b64enc = re.search('base64([^\"]+)', data, re.DOTALL)
    b64dec = b64enc and base64.decodestring(b64enc.group(1))
    enc = b64dec and re.search("\'([^']+)\'", b64dec).group(1)
    if not enc: return ''
    escape = re.search("var _escape=\'([^\']+)", base64.decodestring(enc[::-1])).group(1)
    escape = escape.replace('%', '\\').decode('unicode-escape')
    data = re.findall('<input name="([^"]+?)" [^>]+? value="([^"]*?)">', escape)
    post_data = dict(data)
    totUrl = player_url + '<post>' + urllib.urlencode(post_data)
    data = basicFunc.openUrl(totUrl, False)[1]
    data = re.sub('unescape\("([%0-9a-z]+)"\)', lambda x: urlparse.unquote(x.group(1)), data)
    vid_server = re.search(r'var\s*vid_server\s*=\s*"([^"]*?)"', data)
    vid_link = re.search(r'var\s*vid_link\s*=\s*"([^"]*?)"', data)
    at = re.search(r'var\s*at\s*=\s*"([^"]*?)"', data)
    if not (vid_server and vid_link and at): return ''
    get_data = {'server': vid_server.group(1),
                'link': vid_link.group(1),
                'at': at.group(1),
                'b': '1',
                'adb': '0/',
                'vid':videoId
                }
    totUrl = "http://hqq.tv/player/get_md5.php?" + urllib.urlencode(get_data)
    data = basicFunc.openUrl(totUrl, False)[1]
    data = json.load(StringIO(data))                
    if 'file' not in data: return ''
    dec_a = 'GLMNZoItVyxpRmzuD7WvQne0b='
    dec_b = '26ik8XJBasdHwfT3lc5Yg149UA'
    t1 = string.maketrans(dec_a + dec_b, dec_b + dec_a)
    encUrlStr = str(data['file']).translate(t1)
    urlStr = base64.decodestring(encUrlStr) + '='
    return urlStr

def powvideo(videoId, encHeaders = ''):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    urlStr  = 'http://powvideo.net/iframe-%s-607x360.html' % videoId
    headers = {'Referer':'http://powvideo.net/preview-%s-607x360.html' % videoId}
    urlStr += '<headers>' + urllib.urlencode(headers)
    content = basicFunc.openUrl(urlStr)[1]
    pattern = r"}\((?P<tupla>.+?\))\)\)"
    m = re.search(pattern, content)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])  
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base] 
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    pattern = r"(?P<url>http:[^']+\.m3u8)"
    m = re.search(pattern, patron)
    urlStr = m.group(1)
    return urlStr
    
def gamovideo(videoId, encHeaders = ''):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    headers = {'User-Agent':MOBILE_BROWSER}
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://gamovideo.com/embed-%s-607x360.html<headers>%s' % (videoId, encodeHeaders)
    pattern = r"}\((?P<tupla>.+?\))\)\)"
    content = basicFunc.openUrl(urlStr)[1]
    m = re.search(pattern, content)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])  
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base]
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    pattern = r'file:"(?P<url>http:[^"]+\.mp4)"'
    m = re.search(pattern, patron)
    urlStr = m.group(1) + '|' + MOBILE_BROWSER
    return urlStr

def up2stream(videoId, encHeaders = ''):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    urlStr = 'http://up2stream.com/cdn.php?ref=%s&width=607&height=360&hd=1' % videoId
    content = basicFunc.openUrl(urlStr)[1]
    pattern = r"}\((?P<tupla>\'.+?\)),0,{}"
    m = re.search(pattern, content)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])  
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base]
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    pattern = r'"(http[^"]+)"'
    m = re.search(pattern, patron)
    urlStr = m.group(1)
    return urlStr
    
def transOpenload(videoId, encHeaders = ''):
    '''
    headers = 'Host=openload.co&Cookie=_cfduid%3Dde5a492a69408b66def0def4cd9bc1efe1448464548'
    urlStr = 'https://openload.co/embed/%s/<headers>%s' % (videoId, headers)
    content = basicFunc.openUrl(urlStr)[1]    
    pattern = r'<script>\s+(j.+?)\n'
    m = re.search(pattern, content)
    if not m: return None
    mgrp = m.group(1).split(';', 4)
    
    eval(function(p,a,c,k,e,d){e=function(c){return (c<a?:e(parseInt(c/a)))+((c=c%a)>35?String[fromCharCode](c+29):c.toString(36))};if(![replace](/^/,String)){while(c--){d[e(c)]=k[c]||e(c)};k=[function(e){return d[e]}];e=function(){return \\w+};c=1;};while(c--){if(k[c]){p=p[replace]( new RegExp(\\b+e(c)+\\b,g),k[c])}};return p;}(_0xa98d[0],52,52,||function|return|if|30|replace|while|String|videooverlay||window||||target||playerClicked|title|event||RegExp|fromCharCode|eval|161||xa1|new|xff|logocontainer|hasClass|SubsExisting|undefined|popAdsLoaded|token|adblock|_VideoLoaded|get|reward|9000|typeof|hide|logobrandOutsideplayer|split|id|body|attr|var|ready|document|click|setTimeout[split](|),0,{}));
    eval(function(p,a,c,k,e,d){e=function(c){return(c<a?\'\':e(c/a))+String.fromCharCode(c%a+161)};if(!\'\'.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return\'\\[\\xa1-\\xff]+\'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp(e(c),\'g\'),k[c])}}return p}(\'\xb0 \xa6=0;$(\xb2).\xb3(\xa5(){$("\xac").\xb1(\xa5(\xa1){\xa4($(\xa1.\xa3).\xa7("\xae")||$(\xa1.\xa3).\xa7("\xaa")||$(\xa1.\xa3).\xa7("\xa8")||$(\xa1.\xa3).\xaf(\\\'\xad\\\')=="\xa9"){\xa4(\xa2.\xab){$("#\xa9,.\xa8,.\xaa").\xbe()}}\xa4(\xa6==0){\xb4(\xa5(){\xa4(\xbb \xa2.\xbc=="\xbd"){$.\xba("/\xb9/"+\xb5+"?\xb6="+(((!\xa2.\xab)||\xa2.\xb7)?\\\'1\\\':\\\'0\\\'))}},\xb8);\xa6+=1}})});\',30,30,\'event|window|target|if|function|playerClicked|hasClass|title|videooverlay|logocontainer|popAdsLoaded|body|id|logobrandOutsideplayer|attr|var|click|document|ready|setTimeout|token|adblock|_VideoLoaded|9000|reward|get|typeof|SubsExisting|undefined|hide\'.split(\'|\'),0,{}))
    
    'window.vr="https://openload.co/stream/EzDsB4C1Lk8~1450220365~186.86.0.0~i7bmnc1W?mime=true";window.vt="video/mp4";'
    'window.vr="https://openload.co/stream/EzDsB4C1Lk8~1450266406~186.86.0.0~wM74UYlh?mime=true";window.vt="video/mp4"
1: "f"
_: Function()
c: "c"
constructor: """
o: "o"
return: "\"
ﾟΘﾟ: "_"         F
ﾟΘﾟﾉ: "b"        C
ﾟωﾟﾉ: "a"        W
ﾟДﾟﾉ: "e"        E
ﾟｰﾟﾉ: "d"
    
    
    '''
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'    
    tTokens = {'(j+"")':'"[object object]"', '(![]+"")': '"false"', '(j[j]+"")': '"undefined"', '({}+"")': '"[object object]"', '(!""+"")': '"true"', '((!j)+"")': '"false"'}
    
    content = """return p}(function(z){var a="0%3B%7C%5Z%5B%3Z0%3B%7Z3%3Y%2Z%2Z0%2A%24%24%24%24%3Y%28%21%5Z%5B%2Z%22%22%29%5Z0%5B%2A2%24%3Y%2Z%2Z0%2A%241%241%3Y%28%21%5Z%5B%2Z%22%22%29%5Z0%5B%2A1%241%3Y%2Z%2Z0%2A%241%24%24%3Y%28%7Z%7B%2Z%22%22%29%5Z0%5B%2A%24%241%24%3Y%280%5Z0%5B%2Z%22%22%29%5Z0%5B%2A1%24%24%3Y%2Z%2Z0%2A%24%24%241%3Y%28%21%22%22%2Z%22%22%29%5Z0%5B%2A%242%3Y%2Z%2Z0%2A%241%24%3Y%2Z%2Z0%2A%24%242%3Y%28%7Z%7B%2Z%22%22%29%5Z0%5B%2A%24%241%3Y%2Z%2Z0%2A%24%24%24%3Y%2Z%2Z0%2A%243%3Y%2Z%2Z0%2A%242%24%3Y%2Z%2Z0%7B%3Z0.%241%3B%280.%241%3B0%2Z%22%22%29%5Z0.%241%24%5B%2Z%280.1%24%3B0.%241%5Z0.2%24%5B%29%2Z%280.%24%24%3B%280.%24%2Z%22%22%29%5Z0.2%24%5B%29%2Z%28%28%210%29%2Z%22%22%29%5Z0.1%24%24%5B%2Z%280.2%3B0.%241%5Z0.%24%241%5B%29%2Z%280.%24%3B%28%21%22%22%2Z%22%22%29%5Z0.2%24%5B%29%2Z%280.1%3B%28%21%22%22%2Z%22%22%29%5Z0.1%241%5B%29%2Z0.%241%5Z0.%241%24%5B%2Z0.2%2Z0.1%24%2Z0.%24%3Z0.%24%24%3B0.%24%2Z%28%21%22%22%2Z%22%22%29%5Z0.1%24%24%5B%2Z0.2%2Z0.1%2Z0.%24%2Z0.%24%24%3Z0.%24%3B%280.3%29%5Z0.%241%5B%5Z0.%241%5B%3Z0.%24%280.%24%280.%24%24%2Z%22%5A%22%22%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%24%241%2Z0.%24%24%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.2%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.%24%241%2Z0.%24%241%24%2Z0.1%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%24%241%2Z0.%24%24%24%2Z%22.%22%2Z0.2%2Z0.1%24%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.1%24%24%2Z0.%24%24%241%2Z%22%5A%5A%22%2Z0.2%24%2Z0.%241%24%2Z0.%24%241%2Z%22%3B%5A%5A%5A%22%22%2Z0.3%2Z0.%242%24%2Z0.%24%24%24%2Z0.2%24%2Z0.2%24%2Z0.%24%242%2Z0.%24%24%24%2Z0.%241%24%24%2Z0.%24%241%2Z0.%24%242%2Z0.%243%2Z0.%243%2Z0.%241%241%2Z0.%24%241%2Z0.3%2Z0.%24%241%2Z%22%5A%5A%5A%22%3Z%22%2Z%22%5A%22%22%29%28%29%29%28%29%3Z";return decodeURIComponent(a.replace(/[a-zA-Z]/g,function(c){return String.fromCharCode((c<="Z"?90:122)>=(c=c.charCodeAt(0)+z)?c:c-26);}));}(2),4,4,('j^_^__^___'+'').split("^"),0,{}))"""
    pattern = r'p}\((.+?),0,{}\)\)'
    m = re.search(pattern, content)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])
    m = re.search(r'a="(?P<grp1>[^"]+)".+?}\((?P<grp>\d+)\)',patron)
    patron, k = m.group(1), int(m.group(2))
    lsup = 90
    mf = lambda x: chr(ord(x.group(1)) + k if ord(x.group(1)) + k <= lsup else (ord(x.group(1)) + k - 26) )
    patron = re.sub(r'([A-Z])', mf, patron)
    lsup = 122
    patron = re.sub(r'([a-z])', mf, patron)
    patron = urllib.unquote(patron)
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base]
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    
#     m = """y=~[];y={___:++y,$$$$:(![]+"")[y],__$:++y,$_$_:(![]+"")[y],_$_:++y,$_$$:({}+"")[y],$$_$:(y[y]+"")[y],_$$:++y,$$$_:(!""+"")[y],$__:++y,$_$:++y,$$__:({}+"")[y],$$_:++y,$$$:++y,$___:++y,$__$:++y};y.$_=(y.$_=y+"")[y.$_$]+(y._$=y.$_[y.__$])+(y.$$=(y.$+"")[y.__$])+((!y)+"")[y._$$]+(y.__=y.$_[y.$$_])+(y.$=(!""+"")[y.__$])+(y._=(!""+"")[y._$_])+y.$_[y.$_$]+y.__+y._$+y.$;y.$$=y.$+(!""+"")[y._$$]+y.__+y._+y.$+y.$$;y.$=(y.___)[y.$_][y.$_];y.$(y.$(y.$$+"\""+"\\"+y.__$+y.$_$+y.__$+y.$$$$+"("+y.__+"\\"+y.__$+y.$$$+y.__$+"\\"+y.__$+y.$$_+y.___+y.$$$_+y._$+y.$$$$+"\\"+y.$__+y.___+y.$_$_+y.$$_$+y.$_$$+(![]+"")[y._$_]+y._$+y.$$__+"\\"+y.__$+y.$_$+y._$$+"\\"+y.$__+y.___+"==\\"+y.$__+y.___+"\\\""+y._+"\\"+y.__$+y.$_$+y.$$_+y.$$_$+y.$$$_+y.$$$$+"\\"+y.__$+y.$_$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.$$$_+y.$$_$+"\\\"){\\"+y.__$+y.$$_+y._$$+y.$$$_+y.__+"\\"+y.__$+y.__$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.__+y.$$$_+"\\"+y.__$+y.$$_+y._$_+"\\"+y.__$+y.$$_+y.$$_+y.$_$_+(![]+"")[y._$_]+"("+y.$$$$+y._+"\\"+y.__$+y.$_$+y.$$_+y.$$__+y.__+"\\"+y.__$+y.$_$+y.__$+y._$+"\\"+y.__$+y.$_$+y.$$_+"(){\\"+y.__$+y.$$_+y.$$$+"\\"+y.__$+y.$_$+y.__$+"\\"+y.__$+y.$_$+y.$$_+y.$$_$+y._$+"\\"+y.__$+y.$$_+y.$$$+".\\"+y.__$+y.$$_+y.___+y._$+"\\"+y.__$+y.$$_+y.___+"\\"+y.__$+y.___+y.__$+y.$$_$+"\\"+y.__$+y.$$_+y._$$+"\\"+y.__$+y.__$+y.$__+y._$+y.$_$_+y.$$_$+y.$$$_+y.$$_$+"="+y.$$$$+y.$_$_+(![]+"")[y._$_]+"\\"+y.__$+y.$$_+y._$$+y.$$$_+"},"+y.$$_+y.___+y.___+");}"+"\"")())();"""
#     m = """j=~[];j={___:++j,$$$$:(![]+"")[j],__$:++j,$_$_:(![]+"")[j],_$_:++j,$_$$:({}+"")[j],$$_$:(j[j]+"")[j],_$$:++j,$$$_:(!""+"")[j],$__:++j,$_$:++j,$$__:({}+"")[j],$$_:++j,$$$:++j,$___:++j,$__$:++j};j.$_=(j.$_=j+"")[j.$_$]+(j._$=j.$_[j.__$])+(j.$$=(j.$+"")[j.__$])+((!j)+"")[j._$$]+(j.__=j.$_[j.$$_])+(j.$=(!""+"")[j.__$])+(j._=(!""+"")[j._$_])+j.$_[j.$_$]+j.__+j._$+j.$;j.$$=j.$+(!""+"")[j._$$]+j.__+j._+j.$+j.$$;j.$=(j.___)[j.$_][j.$_];j.$(j.$(j.$$+"\""+j.$$_$+j._$+j.$$__+j._+"\\"+j.__$+j.$_$+j.$_$+j.$$$_+"\\"+j.__$+j.$_$+j.$$_+j.__+".\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$$_+j._$_+"\\"+j.__$+j.$_$+j.__$+j.__+j.$$$_+"('<"+j.$$_$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$_+j.$$_+"\\"+j.$__+j.___+"\\"+j.__$+j.$_$+j.__$+j.$$_$+"=\\\""+j._$+(![]+"")[j._$_]+j.$_$$+j.$_$_+"\\"+j.__$+j.$_$+j.$$_+"\\"+j.__$+j.$_$+j.$$_+j.$$$_+"\\"+j.__$+j.$$_+j._$_+"\\\"\\"+j.$__+j.___+"\\"+j.__$+j.$$_+j._$$+j.__+"\\"+j.__$+j.$$$+j.__$+(![]+"")[j._$_]+j.$$$_+"=\\\""+j.$$_$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$_+j._$$+"\\"+j.__$+j.$$_+j.___+(![]+"")[j._$_]+j.$_$_+"\\"+j.__$+j.$$$+j.__$+":\\"+j.__$+j.$_$+j.$$_+j._$+"\\"+j.__$+j.$_$+j.$$_+j.$$$_+";\\"+j.__$+j.$_$+j.___+j.$$$_+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$__+j.$$$+"\\"+j.__$+j.$_$+j.___+j.__+":"+j.___+";\\"+j.__$+j.$$_+j.___+j._$+"\\"+j.__$+j.$$_+j._$$+"\\"+j.__$+j.$_$+j.__$+j.__+"\\"+j.__$+j.$_$+j.__$+j._$+"\\"+j.__$+j.$_$+j.$$_+":"+j.$$$$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$$+j.___+j.$$$_+j.$$_$+";\\\"></"+j.$$_$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$_+j.$$_+"><"+(![]+"")[j._$_]+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$_$+j.$$_+"\\"+j.__$+j.$_$+j._$$+"\\"+j.$__+j.___+j._$+"\\"+j.__$+j.$_$+j.$$_+j.$$$_+"\\"+j.__$+j.$$_+j._$_+"\\"+j.__$+j.$$_+j._$_+j._$+"\\"+j.__$+j.$$_+j._$_+"=\\\"\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$_$+j.$$_+j.$$_$+j._$+"\\"+j.__$+j.$$_+j.$$$+"._\\"+j.__$+j._$_+j.$$_+"\\"+j.__$+j.$_$+j.__$+j.$$$_+j._$+"\\"+j.__$+j.__$+j.$__+j._$+j.$_$_+j.$$_$+j.$$$_+j.$$_$+"="+j.__+"\\"+j.__$+j.$$_+j._$_+j._+j.$$$_+"\\\"\\"+j.$__+j.___+"\\"+j.__$+j.$$_+j._$_+j.$$$_+(![]+"")[j._$_]+"=\\\"\\"+j.__$+j.$$_+j._$$+j.__+"\\"+j.__$+j.$$$+j.__$+(![]+"")[j._$_]+j.$$$_+"\\"+j.__$+j.$$_+j._$$+"\\"+j.__$+j.$_$+j.___+j.$$$_+j.$$$_+j.__+"\\\"\\"+j.$__+j.___+"\\"+j.__$+j.$_$+j.___+"\\"+j.__$+j.$$_+j._$_+j.$$$_+j.$$$$+"=\\\"//"+j.__$+j.$__$+j.$___+j.$$_+j.$_$_+j.$__+j.$__+j.$_$$+j.__$+j._$_+j.$$$_+"."+j.$$__+j._$+"\\"+j.__$+j.$_$+j.$_$+"/\\"+j.__$+j.___+j.__$+j.$$_$+"\\"+j.__$+j.$$_+j.$$_+j.$$$_+"\\"+j.__$+j.$$_+j._$_+j.__+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$$_+j._$$+j.$$$_+"\\"+j.__$+j.$_$+j.$_$+j.$$$_+"\\"+j.__$+j.$_$+j.$$_+j.__+"."+j.$$__+"\\"+j.__$+j.$$_+j._$$+"\\"+j.__$+j.$$_+j._$$+"\\\">');$("+j.$$_$+j._$+j.$$__+j._+"\\"+j.__$+j.$_$+j.$_$+j.$$$_+"\\"+j.__$+j.$_$+j.$$_+j.__+").\\"+j.__$+j.$$_+j._$_+j.$$$_+j.$_$_+j.$$_$+"\\"+j.__$+j.$$$+j.__$+"("+j.$$$$+j._+"\\"+j.__$+j.$_$+j.$$_+j.$$__+j.__+"\\"+j.__$+j.$_$+j.__$+j._$+"\\"+j.__$+j.$_$+j.$$_+"(){\\"+j.__$+j.$_$+j.__$+j.$$$$+"($(\\\"#"+j._$+(![]+"")[j._$_]+j.$_$$+j.$_$_+"\\"+j.__$+j.$_$+j.$$_+"\\"+j.__$+j.$_$+j.$$_+j.$$$_+"\\"+j.__$+j.$$_+j._$_+"\\\").\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$_$+j.__$+j.$$_$+j.__+"\\"+j.__$+j.$_$+j.___+"()!="+j.__$+j.___+j.___+"){\\"+j.__$+j.$$_+j.$$$+"\\"+j.__$+j.$_$+j.__$+"\\"+j.__$+j.$_$+j.$$_+j.$$_$+j._$+"\\"+j.__$+j.$$_+j.$$$+"._\\"+j.__$+j._$_+j.$$_+"\\"+j.__$+j.$_$+j.__$+j.$$_$+j.$$$_+j._$+"\\"+j.__$+j.__$+j.$__+j._$+j.$_$_+j.$$_$+j.$$$_+j.$$_$+"="+j.__+"\\"+j.__$+j.$$_+j._$_+j._+j.$$$_+";}});"+"\"")())();"""
    m = patron
    if m[0] != 'j': m = m.replace(m[0], 'j')
    diffTokens = set(re.findall(r'\([^$=+]+\+""\)',m)).difference(tTokens.keys())
    assert not diffTokens, 'Tokens no definidos ' + str(diffTokens)
    mgrp = []
    while m:
        match = re.match(r'j[.$_]*=', m)
        if not match: 
            mgrp.append(m)
            break
        code, m = m.partition(';')[0:3:2]
        mgrp.append(code)
        
    mdict = mgrp[1]
    pairs = re.findall(r'(?<=[,{])(?P<key>[_$]+):(?P<value>[^,]+)(?=[,}])', mdict)
    k = -1
    tdict = {}
    for key, value in pairs:
        if value == '++j':
            k +=  1
            tdict[key] = k
        elif value.endswith('[j]'):
            value = re.sub(r'\([^$=+]+\+""\)', lambda x: tTokens.get(x.group(),'"None"'), value)
            assert '"None"' not in value, 'tToken no identificado'
            value = value.replace('[j]', '[k]')
            tdict[key] = eval(value)
    
    for instruction in mgrp[2:]:
        stck = [instruction]
        while 1:
            key = ''
            code = stck.pop(0)
            match = re.match('j\.([$_]+)=', code)
            if match:
                key = match.group(1)
                value = code[match.end():]
                if not tTokens.has_key('(' + value + ')'):
                    prev = []
                    for m in re.finditer(r'(?<=\+)\([^=+]+=.+?\)(?=\+)|(?<=\A)\([^=+]+=[^)]+?\)(?=[+\[])', value):
                        prev.append([m.span(),m.group()[1:].split('=',1)[0],m.group()[1:-1]])
                    if prev:
                        for k in range(len(prev)-1, -1, -1):
                            span, tag, nxtCode = prev[k]
                            value = value[:span[0]] + tag + value[span[1]:]
                            prev[k] = nxtCode
                        prev.append(match.group() + value)
                        stck = prev + stck
                        continue
                    else:
                        code = value
                else:
                    tdict[key] = tTokens['(' + value + ')'][1:-1]
                    continue
            code = re.sub(r'\([^$=+]+\+""\)', lambda x: tTokens.get(x.group(),'"None"'), code)
            code = re.sub(r'j\.([$_]+)(?=\[)', lambda x: '"' + str(tdict.get(x.group(1), 'undefined')) + '"',code)
            code = re.sub(r'j\.([$_]+)', lambda x: str(tdict.get(x.group(1), 'undefined')),code)
            code = code.replace('(undefined+"")', '"undefined"')
            code = re.sub(r'"([\[\] a-z]+)"\[(\d+)\]', lambda x:op.itemgetter(int(x.group(2)))(x.group(1)), code)
            code = re.sub(r'(?<=\+)"(.+?)"(?=\+)', lambda x: x.group(1), code)
            code = code.replace('+', '')
            if key:
                tdict[key] = 'function' if code.startswith('(0)') else code
            if not stck: break
    
    code = code.replace('\\\\\\', '\\').replace('\\\\', '\\')
    code = code.decode('unicode-escape')
    code = code.replace('"""','"')
    pass
    
def openload(videoId, encHeaders = ''):
    headers = {'User-Agent':MOBILE_BROWSER}
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'https://openload.co/embed/%s/<headers>%s' % (videoId, encodeHeaders)
    content = basicFunc.openUrl(urlStr)[1]    
    varTags = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    pattern = r'(?#<video script.*=puzzle>)'
    puzzle = CustomRegEx.findall(pattern, content)[0][0]
    vars = sorted(set(re.findall(r'\(([^=)(]+)\) *=', puzzle)))
    keys1 = re.findall(r', *(?P<key>[^: ]+) *:', puzzle)
    keys2 = re.findall(r"\(ﾟДﾟ\) *\[[^']+\] *=", puzzle)
    keys = sorted(set(keys1 + keys2))
    totVars = vars + keys
    for k in range(len(vars)):
        puzzle = puzzle.replace(vars[k], varTags[k])
    for k in range(len(keys)):
        puzzle = puzzle.replace(keys[k], varTags[-k - 1])
#     puzzle = puzzle.replace('\xef\xbe\x89'.decode('utf-8'), '').replace(' ','')
    puzzle = re.sub(r'[ \x80-\xff]','',puzzle)
    pat_dicId = r'\(([A-Z])\)={'
    m = re.search(pat_dicId, puzzle)
    assert m, 'No se encontro Id del diccionario'
    dicId = m.group(1)
#     pat_obj = r"\(\(%s\)\+\\'_\\'\)" % dicId
    dic_pat1 = r"\(\(%s\)\+\'_\'\)" % dicId
    dic_pat2 = r"\(%s\+([^+)]+)\)" % dicId
    dic_pat3 = r"\(%s\)\.(.+?)\b" % dicId
    dic_pat4 = r"(?<=[{,])([^: ]+)(?=:)"
    
    puzzle = re.sub(dic_pat1, "'[object object]_'", puzzle)
    puzzle = re.sub(dic_pat2, lambda x: "('[object object]'+str(%s))" % x.group(1), puzzle)
    puzzle = re.sub(dic_pat3, lambda x: "(%s)['%s']" % (dicId, x.group(1)), puzzle)
    puzzle = re.sub(dic_pat4, lambda x: "'%s'" % x.group(1), puzzle)

    pat_str1 = r"\((\(.+?\)|[A-Z])\+\'_\'\)"
    pat_str2 = r"\([^()]+\)\[[A-Z]\]\[[A-Z]\]"
    puzzle = re.sub(pat_str1, lambda x: "(str(%s)+'_')" % x.group(1), puzzle)
    puzzle = re.sub(pat_str2, "'function'", puzzle)

    codeGlb = {}    
    code = puzzle.split(';')
    code.pop()
    code[0] = code[0][:2] + "'undefined'"
    for k, linea in enumerate(code[:-1]):
        try:
            exec(linea, codeGlb)
        except:
            print 'Linea %s con errores ' % k, linea
            code[k] = linea.split('=')[0] + '=' + "'\\\\'"
            print 'Se corrige como ', code[k]
            exec(code[k], codeGlb)
    
    linea = code[-1]
    linea = re.sub(r"\(([A-Z]+)\)", lambda x: x.group(1), linea)
    linea = re.sub(r"\([oc]\^_\^o\)", lambda x: "%s" % eval(x.group(), codeGlb), linea)
    while re.search(r"\([^)\]'\[(]+\)", linea):        
        linea = re.sub(r"\([^)\]'\[(]+\)", lambda x: "%s" % eval(x.group(), codeGlb), linea)
    linea = re.sub(r"[A-Z](?=[^\]\[])", lambda x: "%s" % eval(x.group(), codeGlb), linea)
    linea = re.sub(r"E\[[\'_A-Z]+\]", lambda x: "%s" % eval(x.group(), codeGlb), linea)
    linea = linea.replace('+', '')
    linea = linea.decode('unicode-escape')
    m = re.search(r'http.+?true', linea)
    urlStr = '%s|%s' % (m.group(),encodeHeaders)
    return urlStr
    
def thevideo(videoId, encHeaders = ''):
    headers = {'User-Agent':DESKTOP_BROWSER, 
               'Referer': 'http://thevideo.me/%s' % videoId}
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://thevideo.me/%s<headers>%s' % (videoId, encodeHeaders)
    content = basicFunc.openUrl(urlStr)[1]
    pattern = r'''name: '(?P<var1>[^']+)', value: '(?P<var2>[^']+)' \}\).prependTo\(\"#veriform\"\)'''
    formVars = CustomRegEx.findall(pattern, content)
    pattern = r"(?#<form .input<name=var1 value=var2>*>)"
    formVars.extend(CustomRegEx.findall(pattern, content))   
    pattern = r"\$\.cookie\(\'(?P<var1>[^']+)\', \'(?P<var2>[^']+)\'"
    cookieval = CustomRegEx.findall(pattern, content)
    qte = urllib.quote
    postdata = '&'.join(map(lambda x: '='.join(x),[(var1, qte(var2) if var2 else '') for var1, var2 in formVars]))
    headers['Cookie'] = '; '.join(map(lambda x: '='.join(x),cookieval))
    encodeHeaders = urllib.urlencode(headers)
    urlStr = 'http://thevideo.me/%s<post>%s<headers>%s' % (videoId, postdata, encodeHeaders)
    content = basicFunc.openUrl(urlStr)[1]
    pattern = r"label: '(?P<res>[^']+)', file: '(?P<url>[^']+)'"
    sources = CustomRegEx.findall(pattern, content)
    res, href = sources.pop()
    return href
    pass

def vidzi(videoId, encHeaders = ''):
    strVal = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    headers = {'User-Agent':MOBILE_BROWSER}
    encodeHeaders = urllib.urlencode(headers) 
    url = 'http://vidzi.tv/%s.html<headers>%s' % (videoId, encodeHeaders)
    content = basicFunc.openUrl(url)[1]
    pattern = r"(?#<script *='eval.+?'=pack>)"
    packed = CustomRegEx.search(pattern, content).group('pack')
    pattern = "}\((?P<tupla>\'.+?\))(?:,0,{})*\)"
    m = re.search(pattern, packed)
    mgrp = m.group(1).rsplit(',', 3)
    patron, base, nTags, lista = mgrp[0], int(mgrp[1]), int(mgrp[2]), eval(mgrp[3])  
    while nTags:
        nTags -= 1
        tag = strVal[nTags] if nTags < base else strVal[nTags/base] + strVal[nTags%base]
        patron = re.sub('\\b' + tag + '\\b', lista[nTags] or tag, patron)
    pattern = 'file:"([^"]+(?:mp4|ed=))"'
    sources = CustomRegEx.findall(pattern,patron)
    return sources.pop()



if __name__ == "__main__":
    headers = {'Referer': 'http://www.novelashdgratis.tv/'}
    urllib.urlencode(headers)
    resp = vidzi('exrexy8vni9q')
#     resp = thevideo('tv1j6shq1imt')
#     resp = videomega('tBmn3h4X3AA3X4h3nmBt', '<headers>' + urllib.urlencode(headers))
#     resp = up2stream('tBmn3h4X3AA3X4h3nmBt')
#     resp = gamovideo('o7vz5mb3kvls')
#     resp = netu('D5RM53HN4X3M')
#     resp = powvideo('x5gab53lm207')
#    https://openload.co/embed/EzDsB4C1Lk8/
#     resp = openload('EzDsB4C1Lk8')

    pass