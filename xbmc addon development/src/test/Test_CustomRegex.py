# -*- coding: utf-8 -*-
'''
Created on 27/10/2015

@author: Alex Montes Barrios
'''

import sys
import pprint
import pytest
import re

import xbmcUI.CustomRegEx as CustomRegEx
import CustomRegEx

def ExtCompObjEquality(a , b):
    return (a.tags, a.varList) == (b.tags, b.varList)

@pytest.fixture
def htmlString():
    with open(r'c:/fileTest/extRegExTest.txt', 'r') as origF:
        equis = origF.read()
    return equis


class TestExtcompile:

    def test_ExtCompile(self):
        """
        Html tag m�nimo
        """
        requested = {'tagpholder': {}}
        assert CustomRegEx.compile('(?#<table>)', 0).tags == requested
        
    def test_namedvars(self):
        """
        <a href="http://uno.html">texto</a>
        Html tag con variables url y label a los que se asigna el valor del atributo href y 
        el texto respectivamente
        """
        actual = CustomRegEx.compile('(?#<a href=url *=label>)', 0)
        assert (actual.tagPattern, actual.tags, actual.varList) == ('a', {'tagpholder': {'*': '', 'href': ''}}, [['tagpholder.href', 'url'], ['tagpholder.*', 'label']])

    def test_namedvarswithpattern(self):
        """
        <a href="http://uno/dos/tres.html">texto</a>
        Html tag con variables url y label a los que se asigna el valor del atributo href y 
        el texto respectivamente ya que href cumple con el patrón "http://uno/.+?/tres.html"
        """
        actual = CustomRegEx.compile('(?#<a href="http://uno/.+?/tres.html" href=url *=label>)', 0)
        assert actual.varList == [['tagpholder.href', 'url'], ['tagpholder.*', 'label']]
        
    def test_implicitvars(self):
        """
        <a href="http://uno.html">texto</a>
        Html tag con variable implícita href y variable label que recoge el texto
        """
        actual = CustomRegEx.compile('(?#<a (href) *=label>)', 0)
        assert (actual.tagPattern, actual.tags, actual.varList) == ('a', {'tagpholder': {'*': '', 'href': ''}}, [['tagpholder.href', 'group1'], ['tagpholder.*', 'label']])
         
    def test_cleanvars(self):
        """
        <a href="http://uno.html">texto</a>
        Html tag con variable implícita href y variable label que recoge el texto una vez se
        eliminan los espacios en el prefijo y el sufijo. Es decir si a.* = \n\r \testo es lo que vale \t\n
        la notación &label& hace que en label se almacene "esto es lo que vale"
        """
        first = CustomRegEx.compile('(?#<a (href) *=label>)', 0)
        scnd  = CustomRegEx.compile('(?#<a (href) *=&label&>)', 0)
        assert first.tags['tagpholder']['*'] != scnd.tags['tagpholder']['*']

    def test_equivNotation(self):
        """
        Notación equivalente utilizando asociatividad que se expresa con las {}
        """
        first = CustomRegEx.compile('(?#<a href span{src=icon *=label} div.id>)',0)
        scnd  = CustomRegEx.compile('(?#<a href span.src=icon span.*=label div.id>)',0)
        assert ExtCompObjEquality(first , scnd)
        
    def test_equivNotationII(self):
        """
        Notación equivalente utilizando asociatividad cuando se tienen el mismo tag en 
        varios niveles 
        """
        first  = CustomRegEx.compile('(?#<table id td.*=grp1 td[2].b.*=grp2 td[2].a.href=grp2a td[2].a.src=grp2b td[3].*=grp3 td[4].*=grp4>)',0)
        scnd   = CustomRegEx.compile('(?#<table id td{1.*=grp1 2{b.*=grp2 a{href=grp2a src=grp2b}} 3.*=grp3 4.*=grp4}>)',0)
        assert ExtCompObjEquality(first , scnd)
        

    def test_tripleAsignation(self):
        """
        Notación equivalente utilizando doble asignación para declarar la variable y el parametro que
        se quiere
        """
        first  = CustomRegEx.compile('(?#<ese a.*="http//.+?/prueba" a.*=icon href=url>)', 0)
        scnd   = CustomRegEx.compile('(?#<ese a.*="http//.+?/prueba"=icon href=url>)', 0)
        assert ExtCompObjEquality(first , scnd)

    def test_raiseAsignationError(self):
            with pytest.raises(re.error):
                CustomRegEx.compile('(?#<TAG ese a{*=icon a.*="http//esto/es/prueba" href=url>)', 0)


class TestExtRegexParser:
    @pytest.mark.parametrize('cycle', [3, 2, 1])
    def test_getAttrDict0(self, cycle):
        htmlLst = ['<a', 'href2=eltiempo.com', 'href1', 'href0=\"eltiempo.com\"']
        htmlLst.append(htmlLst.pop(cycle))
        htmlStr = ' '.join(htmlLst) + '>'
        print htmlStr
        parser = CustomRegEx.ExtRegexParser()
        tag, attrD = parser.getAttrDict(htmlStr, offset = 18, noTag=False)
        htmlStr = 18*' ' + htmlStr 
        attrP = attrD.pop('*ParamPos*')
        assert tag == 'a', "El tag reportado no corresponde al tag real"
        assert len(attrD) == 3
        assert attrD['href0'] == "eltiempo.com", "Error valor de attributo normal"
        assert attrD['href1'] == "", "Error atributo sin valor"
        assert attrD['href2'] == "eltiempo.com", "Error valor de attributo sin comillas"
        getSlice = htmlStr.__getslice__
        print '***' + htmlStr + '***'
        for k in attrD:
            print k, attrD[k], getSlice(*attrP[k]), attrP[k]
        assert all([attrD[k] == getSlice(*attrP[k]) for k in attrD])
        
    @pytest.mark.parametrize('cycle', [4, 3, 2, 1])    
    def test_getAttrDict1(self, cycle):
        htmlLst = ['<a', 'href0="eltiempo.com"', 'href1="eltiempo.com\'', 'href2=\'eltiempo.com\'', 'href3=eltiempo.com']
        htmlLst.append(htmlLst.pop(cycle))
        htmlStr = ' '.join(htmlLst) + '>'
        print htmlStr
        parser = CustomRegEx.ExtRegexParser()
        tag, attrD = parser.getAttrDict(htmlStr, noTag = False)
        attrD.pop('*ParamPos*')
        assert sorted(attrD.keys()) == ['href%d' % k for k in range(4)], "Los attributos reportados no corresponde a los reales"
        assert set(attrD.values()) == set(["eltiempo.com"]), "Por lo menos el valor de un attributo reportado no corresponde al real"
        
    def test_getAttrDict2(self):
        htmlStr = """<a href0="el 'tiempo com" href1="el 'tiempo" com' href2='el 'tiempo' com' href3=''el tiempo' com' href4='el 'tiempo com''>"""
        parser = CustomRegEx.ExtRegexParser()
        attrD = parser.getAttrDict(htmlStr)
        assert attrD['href0'] == "el \'tiempo com", "Error comilla interior simple"
        assert attrD['href1'] == "el \'tiempo\" com", "Error comillas interiores mixtas"
        assert attrD['href2'] == "el \'tiempo\' com", "Error comillas interiores"
        assert attrD['href3'] == "\'el tiempo\' com", "Error comillas interiores ajustadas a la izquierda"
        assert attrD['href4'] == "el \'tiempo com\'", "Error comillas interiores ajustadas a la derecha"

class TestExtMatch:
    htmlStr = """
<span class="independiente">span0</span>
<script>
    <span class="bloque1">span1</span>
    <a href="http://www.eltiempo.com.co">El Tiempo</a>
    <span class="bloque1">span2</span>
</script>
<bloque>
    <span class="independiente">bloque1</span>
    <parent id="root">
    <hijo id="hijo1">primer hijo</hijo>
    <hijo id="hijo2" exp="hijo con varios comentarios">
         <h1>El primer comentario</h1>
         <h1>El segundo comentario</h1>
         <h1>El tercer comentario</h1>
    </hijo>
    <hijo id="hijo3">tercer hijo</hijo>
    </parent>
    <span class="independiente">bloque2</span>
</bloque>
<!--
    <span class="bloque2">span1</span>
    <a href="http://www.elheraldo.com.co">El Heraldo</a>
    <span class="bloque2">span2</span>
-->
<span class="independiente">span3</span>
        """

    def test_general(self):
        answer = CustomRegEx.findall('(?#<hijo id="hijo1" *=label>)', self.htmlStr)
        required = [('primer hijo', )]
        assert answer == required, 'Comentario y variable independiente'

        answer = CustomRegEx.findall('(?#<hijo id=varid *=label>)', self.htmlStr)
        required = [('hijo1', 'primer hijo'), ('hijo2', ''), ('hijo3', 'tercer hijo')]
        assert answer == required, 'Utilizando variables para distinguir casos'

        answer = CustomRegEx.findall('(?#<hijo id="hijo[13]"=varid *=label>)', self.htmlStr)
        required = [('hijo1', 'primer hijo'), ('hijo3', 'tercer hijo')]
        assert answer == required, 'Utilizando variables para distinguir casos'

        answer = CustomRegEx.findall('(?#<hijo exp *=label>)', self.htmlStr)
        required = [('', )]
        assert answer == required, 'Utilizando atributos requeridos (exp) para distinguir un caso'
        
        answer = CustomRegEx.findall('(?#<hijo exp .*>)', self.htmlStr)
        required = [('El primer comentario', 'El segundo comentario', 'El tercer comentario')]
        assert answer == required, 'Comentarios incluidos en tag'
        
        with pytest.raises(re.error):
            'Error porque no se pueden utilizar variables cuando se tiene ".*" como variable requerida'
            CustomRegEx.compile('(?#<span class=var1 .*>)')
        
        
    
    def test_tag(self):
        answer = CustomRegEx.findall('(?#<span|a *=label>)', self.htmlStr)
        required1 = [('span0', ), ('bloque1', ), ('bloque2', ), ('span3',)]
        assert answer == required1, 'Obtener texto de tags span o a'
        
        cmpobj = CustomRegEx.compile('(?#<(span|a) *=label>)')
        answer = cmpobj.groupindex.keys()
        required2 = ['__TAG__', 'label']
        assert answer == required2, 'Al encerrar el tagpattern entre paréntesis el nametag se almacena en la variable __TAG__ '
        
        answer = cmpobj.findall(self.htmlStr)
        required3 = [('span', 'span0'), ('span', 'bloque1'), ('span', 'bloque2'), ('span', 'span3')]
        assert answer == required3, 'El primer componente de los tuples que conforman answer corresponde al nametag'

        cmpobj = CustomRegEx.compile('(?#<span|a __TAG__=mi_nametag_var *=label>)')
        answer = cmpobj.groupindex.keys()
        required4 = ['mi_nametag_var', 'label']
        assert answer == required4, 'Al utilizar el atributo __TAG__ se puede asignar una variable que contendra el nametag de los tags que cumplen con el pattern buscado'

        answer = cmpobj.findall(self.htmlStr)
        assert answer == required3, 'El resultado es el mismo, cambia solo el nombre de la variable asociada al nametag'

        cmpobj = CustomRegEx.compile('(?#<__TAG__ *="[sb].+?"=label>)')
        answer = cmpobj.findall(self.htmlStr)
        assert answer == required1, 'Al utilizar __TAG__ como tag attribute se hace el tagpattern = "[a-zA-Z][^\s>]*", para con el primer resultado se asigna "[sb].+?" al *'
        
        cmpobj = CustomRegEx.compile('(?#<(__TAG__) *=".+?"=label>)')
        answer = cmpobj.groupindex.keys()
        assert answer == required2, 'Se puede utiliza (__TAG__) para guardar el nametag en la variable __TAG__'
        
        cmpobj = CustomRegEx.compile('(?#<__TAG__ __TAG__=mi_nametag_var *=".+?"=label>)')
        answer = cmpobj.groupindex.keys()
        assert answer == required4, 'Se puede utiliza __TAG__=nombrevar para guardar el nametag en una variable con nmbre propio'
        
        cmpobj = CustomRegEx.compile('(?#<__TAG__ __TAG__=mi_nametag_var *=label>)')
        answer = cmpobj.findall(self.htmlStr)
        required = [('span', 'span0'), ('script', ''), ('bloque', ''), ('span', 'span3')] 
        assert answer == required, 'Utilizando __TAG__ como tagpattern'
        
        cmpobj = CustomRegEx.compile('(?#<__TAG__ __TAG__="span|a"=mi_nametag_var *=label>)')
        answer = cmpobj.findall(self.htmlStr)
        assert answer == required3, 'Utilizando __TAG__="span|a"=mi_nametag_var se redefine el tagpattern a "span|a" y se asigna a la variable mi_nametag_var'
        
        with pytest.raises(re.error):
            'Entrega error porque se utiliza (__TAG__) como tagpattern y con __TAG__=mi_nametag_var se intenta asignarle a otra variable'
            CustomRegEx.compile('(?#<(__TAG__) __TAG__=mi_nametag_var *=label>)')
        
    def test_nzone(self):
        
        allspan = [('independiente', 'span0'),
                   ('bloque1', 'span1'), ('bloque1', 'span2'),                  #En script
                   ('independiente', 'bloque1'), ('independiente', 'bloque2'),  #En bloque
                   ('bloque2', 'span1'), ('bloque2', 'span2'),                  #En <!--
                   ('independiente', 'span3')]

        answer1 = CustomRegEx.findall('(?#<span class=test *=label>)', self.htmlStr)
        required = [lista for lista in allspan if lista[0] == 'independiente']
        assert answer1 == required, 'Por default se excluyen Los tags buscados en self.htmlStr contenidos en zonas <!--xxx--> y script'
        answer2 = CustomRegEx.findall('(?#<span class=test *=label __EZONE__="[!--|script]">)', self.htmlStr)
        assert answer1 == answer2, 'El resultado por default se obtiene haciendo __NZONE__="[!--|script]" '
        
        answer = CustomRegEx.findall('(?#<span class=test *=label __EZONE__="">)', self.htmlStr)
        assert answer == allspan, 'Para no tener zonas de exclusi.n se hace __EZONE__=""'
        
        answer = CustomRegEx.findall('(?#<span class=test *=label __EZONE__="[bloque]">)', self.htmlStr)
        required = [lista for lista in allspan if not lista[1].startswith('bloque')]
        assert answer == required, 'Se personaliza la zona de exclusi.n asignando a __NZONE__="xxx|zzz" donde xxx y zzz son tags'
        
        answer = CustomRegEx.findall('(?#<span class=test *=label __EZONE__="^[!--|script]">)', self.htmlStr)
        required = [lista for lista in allspan if lista[0].startswith('bloque')]
        assert answer == required, 'Para incluir solo tags buscados en las zonas xxx y zzz se debe hacer __NZONE__="^[xxx|zzz]'
                
        answer = CustomRegEx.findall('(?#<a href=url *=labe>)', self.htmlStr)
        required = []
        assert answer == required 

        answer = CustomRegEx.findall('(?#<a href=url *=label __EZONE__="^[script]">)', self.htmlStr)
        required = [('http://www.eltiempo.com.co', 'El Tiempo')]
        assert answer == required
        
        answer = CustomRegEx.findall('(?#<a href=url *=label __EZONE__="^[!--]">)', self.htmlStr)
        required = [('http://www.elheraldo.com.co', 'El Heraldo')]
        assert answer == required
        


def test_extSearch(htmlString):
    testPattern = CustomRegEx.compile('<ul class="links">.+?</ul><ZIN><a title="(?P<label>[^"]+)" href="(?P<url>[^"]+)">.+?</a>', re.DOTALL)
    match = testPattern.search(htmlString, 0)
    
'''
Para probar:   <tv default="true">-</tv>
'''    
    
