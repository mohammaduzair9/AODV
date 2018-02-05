import subprocess, shlex

nodes = [("faryal", 1500),("emma",1501),("dawood", 1502),("charlie",1503),("bilal",1504),("ahmed",1505),("gul",1506)]

for i in range(0,7):
    cmd = "x-terminal-emulator -e 'python node.py " + nodes[i][0] + " localhost " + str(nodes[i][1]) + "'"
    process = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
