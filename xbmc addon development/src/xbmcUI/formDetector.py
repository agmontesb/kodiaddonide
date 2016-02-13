import Tkinter as tk
import urlparse
from OptionsWnd import scrolledFrame, AppSettingDialog
import basicFunc
import re
import operator
import pprint
import CustomRegEx
import collections
getAttrDict = CustomRegEx.ExtRegexParser.getAttrDict


def escapeXml(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').encode('utf-8')
def unescapeXml(s): return s.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').decode('utf-8')


def getFormData(comPattern, content, posini):
    if not isinstance(comPattern, CustomRegEx.ExtRegexObject): raise TypeError('Expecting an CustomRegEx.ExtRegexObject')
    match = comPattern.search(content, posini)
    if not match: return None
    posfin = match.end()
    formHtml = match.group()
    formAttr = getAttrDict(formHtml, 0, noTag=False)[1]
    formAttr.pop('*ParamPos*')
    formFields = collections.OrderedDict()
    if formAttr and formAttr.has_key('id'):
        formId = formAttr['id']
        pattern = r'''\$\(['"]<input/>['"]\)\.attr\(\{(?P<input_attr>[^}]+)\}\)\.prependTo\(['"]#%s['"]\)''' % formId
        prependVars = re.findall(pattern, content)
        for avar in prependVars:
            avar = avar.replace(': ', ':').replace(',', '').replace(':', '=')
            avar = '<input ' + avar + ' prepend="">'
            attr = getAttrDict(avar, 0, noTag=True)
            name = attr['name']
            formFields[name] = attr
    pattern = r'(?#<form<__TAG__="input|select|textarea"=tag name=name>*>)'
    for m in CustomRegEx.finditer(pattern, formHtml):
        # tag, name = map(operator.methodcaller('lower'),m.groups())
        tag, name = m.groups()
        p1, p2 = m.span()
        attr = getAttrDict(m.group(), 0, noTag=True)
        attr.pop('*ParamPos*')
        if formFields.get(name, None):
            if 'value' in attr and formFields[name].has_key('value'):
                value = formFields[name]['value']
                if isinstance(value, basestring):
                    value = [value]
                value.append(attr['value'])
                formFields[name]['value'] = value
        else:
            formFields[name] = attr
            if attr.has_key('list'):
                pattern = r'(?#<datalist id="%s"<value=value>*>)' % attr['list']
                attr['value'] = CustomRegEx.findall(pattern, formHtml)
                pass
            elif tag == 'select':
                pattern = r'(?#<option value=value *=&lvalue&>)'
                match = CustomRegEx.findall(pattern, formHtml[p1:p2])
                # attr['value'] = map(operator.itemgetter(0), match)
                # attr['lvalue'] = map(operator.itemgetter(1), match)
                attr['value'], attr['lvalue'] = match.groups()
                pattern = r'(?#<option value=value>)'
                attr['value'] = CustomRegEx.findall(pattern, formHtml[p1:p2])

                pattern = r'(?#<option value=value selected>)'
                try:
                    attr['default'] = CustomRegEx.findall(pattern, formHtml[p1:p2])[0]
                except:
                    attr['default'] = ''
                pass
            elif tag == 'textarea':
                attr['value'] = attr.get('*', '')
                continue
                pass

    return posfin, formAttr, formFields

def getFormXmlStr(content):
    form_xml ='<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<settings>\n'
    pattern = r'(?#<form>)'
    comPattern = CustomRegEx.compile(pattern)
    k = 0
    posIni = 0
    while True:
        formData = getFormData(comPattern, content, posIni)
        if not formData: break
        posIni, formAttr, formFields = formData
        formAttr = dict([(key, escapeXml(value)) for key, value in formAttr.items()])
        form_xml += '\t<category label="Form %s">\n' % (k + 1)
        if formAttr:
            form_xml += '\t\t<setting type="lsep" label ="Form attributes"/>\n'
            for name, value in sorted(formAttr.items()):
                form_xml += '\t\t<setting id="fa_{0}" type="text" label="{0}" default="{1}" enable="false"/>\n'.format(name, value)
        bFlag = 0
        for key in formFields:
            if formFields[key].has_key('prepend'):
                if bFlag == 0:
                    bFlag = 1
                    form_xml += '\t\t<setting type="lsep" label ="Form Prepend Vars"/>\n'
            else:
                if bFlag < 2:
                    bFlag = 2
                    form_xml += '\t\t<setting type="lsep" label ="Form Vars"/>\n'
            if isinstance(formFields[key].get('value', ''), basestring):
                formFields[key].update([(fkey, escapeXml(formFields[key][fkey])) for fkey in ['name', 'value', 'checked'] if formFields[key].has_key(fkey)])
                atype = formFields[key].get('type', '')
                if atype == 'hidden':
                    felem = '<setting id="{name}" type="text" label="{name}" default="{value}" enable="false"/>\n'
                    pass
                elif atype in ['radio', 'checkbox']:
                    formFields[key]['checked'] = 'true' if formFields[key].has_key('checked') else 'false'
                    felem = '<setting id="{name}" type="bool" label ="{name}" default="{checked}"/>\n'
                    pass
                elif atype == 'text':
                    formFields[key]['value'] = formFields[key].get('value', '')
                    felem = '<setting id="{name}" type="text" label="{name}" default="{value}"/>\n'
                elif atype == 'submit':
                    felem = '<setting type="lsep" label ="{value}" noline="true"/>\n'
                elif atype == 'file':
                    formFields[key]['defaultValue'] = formFields[key].get('defaultValue', '')
                    felem = '<setting id="if_{name}" type="file" label="{name}" default="{defaultValue}"/>'
                else:
                    formFields[key]['value'] = formFields[key].get('value', '')
                    felem = '<setting id="{name}" type="text" label="{name}" default="{value}"/>\n'
            else:
                toEscape = ['name', 'value', 'default']
                formFields[key]['value'] = '|'.join(formFields[key]['value'])
                if formFields[key].has_key('lvalue'):
                    formFields[key]['lvalue'] = '|'.join(formFields[key]['lvalue'])
                    toEscape.append('lvalue')
                formFields[key]['default'] = formFields[key].get('default', '')
                formFields[key].update([(fkey, escapeXml(formFields[key][fkey])) for fkey in toEscape])
                if formFields[key].has_key('lvalue'):
                    felem = '<setting id="{name}" type="drpdwnlst" label="{name}" lvalues="{lvalue}" values="{value}" default="{default}"/>\n'
                else:
                    felem = '<setting id="{name}" type="labelenum" label="{name}" lvalues="{value}" default="{default}"/>\n'
            form_xml += '\t\t' + felem.format(**formFields[key])
        form_xml += '\t</category>\n'
        k += 1
    form_xml += '</settings>\n'
    return form_xml

def getCurlCommand(baseUrlStr, formAttr, formFields, otherOptions = ''):
    if formAttr.has_key('action'):
        baseUrlStr = urlparse.urljoin(baseUrlStr, formAttr['action'])
    if formAttr.get('method', 'POST').upper() != 'POST':
        otherOptions += ' --get'
        pass
    datafrm = '--data-urlencode "%s=%s"'
    if formAttr.get('enctype', '').lower() == 'multipart/form-data':
        datafrm = '--form "%s=%s"'
        pass
    postData = ' '.join(datafrm % (item[0], item[1].encode('utf-8')) for item in formFields)
    return 'curl "{0}" {1} {2} --compressed'.format(baseUrlStr, postData, otherOptions)

if __name__ == '__main__':
    baseUrl = 'https://lastpass.com/?ac=1&lpnorefresh=1'
    content = basicFunc.openUrl(baseUrl)[1]

    Root = tk.Tk()
    form_xml = getFormXmlStr(content)
    print(form_xml)
    browser = AppSettingDialog(Root, form_xml, isFile = False, settings = {}, title = 'Form Detector In Develovment', dheight = 600, dwidth = 800)
    print('***Result***')
    pprint.pprint(browser.result)
    print('***AllSettings***')
    pprint.pprint(browser.allSettings)
    if browser.allSettings:
        formAttr = dict([(key[3:], value) for key, value in browser.allSettings if key.startswith('fa_')])
        formFields = [item for item in browser.allSettings if not item[0].startswith('fa_')]
        pprint.pprint(formAttr)
        pprint.pprint(formFields)
        print getCurlCommand(baseUrl, formAttr, formFields)

    Root.mainloop()





