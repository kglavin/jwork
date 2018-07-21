
import pytest
from spell import LCSObject, LCSMap, LCSMultiMap

st1 = 'daemon service x regen started'
s1 = st1.split()
st2 = 'daemon service y regen started'
s2 = st2.split()
st3 = 'daemon service x regen stopped'
s3 = st3.split()
st4 = 'daemon service y regen stopped'
s4 = st4.split()
st5 = 'daemon service x regen started error 0'
s5 = st5.split()
st6 = 'daemon service x regen stopped error 6'
s6 = st6.split()

sdiff = "this is a different log not the same as other log messages"
sdiff_list = sdiff.split()

print("lets start")
m=LCSMap()
mm=LCSMultiMap()

def test_create():
   r = m.getMatch(s1)
   assert r == None
   assert m.len() == 0

def test_add_s1():
   m.insert(s1)
   m.debug()
   assert m.len() == 1

def test_check_s1():
   r = m.getMatch(s1)
   assert r != None

def test_check_neg_s1():
   r = m.getMatch("this will fail".split())
   assert r == None

def test_add_s2():
    m.insert(sdiff_list)
    assert m.len() == 2

def test_check_s1_again():
   r = m.getMatch(s1)
   m.debug()
   assert r != None

def test_check_sdiff():
   r = m.getMatch(sdiff_list)
   assert r != None

def test_mm_add_s1():
   mm.insert('proj1', s1)
   
def test_mm_add_s2():
   mm.insert('proj1', s2)

def test_mm_add_proj2_s1():
   mm.insert('proj2', s1)
   
def test_mm_add_proj2_s2():
   mm.insert('proj1', s2)

def test_mm_match():
   a,_ = mm.getMatch('proj1',s1)
   assert a != None

def test_mm_match_variation():
   a,_ = mm.getMatch('proj1',s3)
   assert a != None

def test_mm_match_no_s():
   a,v = mm.getMatch('proj1',sdiff_list)
   assert a == None

def test_mm_match_wrong_key():
   a,v = mm.getMatch('projx',s1)
   assert a == None

   
def test_mm_match_proj2():
   a,v = mm.getMatch('proj2',s1)
   assert a != None

def test_mm_match_proj2_no_s():
   a,v = mm.getMatch('proj2',sdiff_list)
   assert a == None
   
