import re

#Check if the string starts with "The" and ends with "Spain":

txt = "open localhost:3000"
if re.search("^open ([A-Z]|[a-z]|[0-9])*:[0-9]*$", txt):
  path = re.split('open ', txt)
  server = path[1].split(':')[0]
  port = path[1].split(':')[1]
  print(server)
  print(port)
else:
  print("No match")
