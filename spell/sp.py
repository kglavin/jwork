
 
with open("testfiles/syslog.200", "r") as my_file:
  for line in my_file:
      line = line.replace("["," ").replace("]"," ").replace(":"," ").replace("("," ").replace(")"," ")
      s = line.split()
      print(s)


with open("testfiles/syslog", "r") as my_file:
  for line in my_file:
      s = line.replace("["," ").replace("]"," ").replace(":"," ").replace("("," ").replace(")"," ").split()
      print(s)
