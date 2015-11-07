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
        first  = CustomRegEx.compile('(?#<table id td.*=grp1 td[2].a.href=grp2 td[3].*=grp3 td[4].*=grp4>)',0)
        scnd   = CustomRegEx.compile('(?#<table id td{1.*=grp1 2.a.href=grp2 3.*=grp3 4.*=grp4}>)',0)
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
                CustomRegEx.compile('(?#<TAG ese a.*=icon a.*="http//esto/es/prueba" href=url>)', 0)


def test_extSearch(htmlString):
    testPattern = CustomRegEx.compile('<ul class="links">.+?</ul><ZIN><a title="(?P<label>[^"]+)" href="(?P<url>[^"]+)">.+?</a>', re.DOTALL)
    match = testPattern.search(htmlString, 0)
    assert match
