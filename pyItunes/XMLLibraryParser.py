import re
class XMLLibraryParser:
  def __init__(self,xmlLibrary):
    f = open(xmlLibrary)
    s = f.read()
    lines = s.split("\n")
    self.dictionary = self.parser(lines)
    
  def getValue(self,restOfLine):
    value = re.sub("<.*?>","",restOfLine.replace('&#38;','&'))
    return unicode(value,"utf-8")

  def keyAndRestOfLine(self,line, search):
    rawkey = search.group(0)
    key = re.sub("</*key>","",rawkey)
    restOfLine = re.sub("<key>.*?</key>","",line).strip()
    return key,restOfLine

  def parser(self,lines):
    dicts = 0
    songs = {}
    inSong = False
    for line in lines:
      if '<dict>' in line:
        dicts += 1

      if '</dict>'in line:
        dicts -= 1
        inSong = False
        songs[songkey] = temp

      if dicts == 2:
        search = re.search('<key>(.*?)</key>',line)
        if search:
          rawkey = search.group(0)
          songkey = re.sub("</*key>","",rawkey)
          inSong = True
          temp = {}

      if dicts == 3:  
        search = re.search('<key>(.*?)</key>',line)
        if search:
          key,restOfLine = self.keyAndRestOfLine(line, search)
          temp[key] = self.getValue(restOfLine)

      if len(songs) > 0 and dicts < 2:
        return songs
    return songs
