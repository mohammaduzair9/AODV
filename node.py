import sys, json, pickle
from socket import *
import os.path

#gobal parameters
my_ip = ""
my_seq_num = 1
broadcast_num = 1
my_port = 0
life_time = "undefined"
route_table = list()
neighbours = list()
route_entry = []
hop_count = 0
dest_id = ""
dest_seq_num = -1

#defining data_msg type arrays	
RREQ = []
RREP = []
RERR = []

#get name of neighbour from port
def get_neighbour_name(port):
	for x in neighbours.items():
		if (x[1][2] == port):
			return x[1]


# check if node exists in the route table
def exist_in_route_table(node):
	nodes = [route_entry[0][0] for route_entry in route_table]
	if (node in nodes):
		return True
	else: 	
		return False


# get the node in next hop from route table
def get_next_hop(node):
	for route_entry in route_table:
		if (route_entry[0][0] == node):
			return route_entry[1]


# get an entry from route table given node id
def get_route_entry(node_id):
	for route_entry in route_table:
		if (route_entry[0][0] == node_id):
			return route_entry



# print the route table
def print_route_table():
	print "-----------------------------------------------------------------------------------"
	print "|                                Route Table                                      |"
	print "-----------------------------------------------------------------------------------"
	print "|  Destination  | Next Hop | Hop Count | Life Time | Destination Sequence | Valid |"
	print "-----------------------------------------------------------------------------------"
	for x in xrange(0,len(route_table)):
		dest = route_table[x][0][0]
		n_h = route_table[x][1][0]
		h_c = route_table[x][2]
		l_t = route_table[x][3]
		dest_sequence = route_table[x][4]
		valid = route_table[x][5]

		row = "|  "+dest+"| ".rjust(15-len(dest))+n_h+"|   ".rjust(13-len(n_h))+str(h_c)+"| ".rjust(10-len(str(h_c)))+l_t+" | ".rjust(10-len(l_t))+"   "+str(dest_sequence)+"| ".rjust(20-len(str(dest_sequence)))+" "+str(valid)+"    |"
		print row
	print "-----------------------------------------------------------------------------------"





# main starts here
# required 4 arguments
if (len(sys.argv) != 4):
	print "syntax: python node.py [source name] [source ip] [source port]"
	exit(1)

my_id = sys.argv[1]
my_ip = sys.argv[2]
my_port = int(sys.argv[3])

# defining neighbours
if (my_id == "gul"):
	neighbours = {"faryal":["faryal","localhost",1500], "ahmed":["ahmed","localhost",1505]}
elif (my_id == "dawood"):
	neighbours = {"emma":["emma","localhost",1501], "charlie":["charlie","localhost",1503]}
elif (my_id == "ahmed"):
	neighbours = {"gul":["gul","localhost",1506], "bilal":["bilal","localhost",1504]}
elif (my_id == "emma"):
	neighbours = {"dawood":["dawood","localhost",1502], "faryal":["faryal","localhost",1500]}
elif (my_id == "faryal"):
	neighbours = {"emma":["emma","localhost",1501], "gul":["gul","localhost",1506]}
elif (my_id == "bilal"):
	neighbours = {"charlie":["charlie","localhost",1503], "ahmed":["ahmed","localhost",1505]}
elif (my_id == "charlie"):
	neighbours = {"dawood":["dawood","localhost",1502], "bilal":["bilal","localhost",1504]}

# printing source information
print "*************************************************"
print "****" ,my_id, "=>", my_ip,":",my_port
print "*************************************************"

print "*************************************************"
print "**** Neighbours: ",neighbours.keys()
print "*************************************************"

# opening source socket
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((my_ip, my_port))

# setting gul as the initial originator and all other as receivers
# 1 is originator 
# 2 is destination
if (my_id == "gul"):
	flag = "1"
else:
	flag = "2"

# saving routing table in pickle files
route_table_name = "table_" + my_id + ".pickle"

# restoring routing table from pickle
if os.path.isfile(route_table_name):
	#open the serialized file and load it to route_table
	with open(route_table_name, 'rb') as f:
		route_table = pickle.load(f)


#infinite loop 
while(1):
	# sending mode tasks
	if (flag == "1"):
		#dest_id = raw_input("Name of destination node: ")
		dest_id = "dawood"
		#dest_ip = #raw_input("IP Address of destination: ")
		dest_ip = "localhost"
		dest_port = raw_input("Port No of destination: ")
		
		#if the destination node is in the table then get it from the table
		if (exist_in_route_table(dest_id)):
			print "FOUND ::: Route to destination exists"
			print "SEND  ::: Sending data_msg to destination"
			
			originator = [my_id, my_ip, my_port]
			data_msg = "This is a data message from " + my_ip + ":::" + my_id + ":::" + my_port + "for " + destination + ""
			data = json.dumps(["DATA",originator,dest_id,data_msg])
			#print sock.sendto(data, tuple(get_next_hop(dest_id)[1:]))
			#sock.settimeout(3)
			# if (sock.sendto(data, tuple(get_next_hop(dest_id)[1:])) < 0):
			# 	for entry in xrange(0, len(route_table)):
			# 		print route_table[entry][1], get_next_hop(dest_id), route_table[entry][5]
			# 		if (route_table[entry][1] == get_next_hop(dest_id)):
			# 			route_table[entry][5] = 0
			sock.sendto(data, tuple(get_next_hop(dest_id)[1:]))
			print_route_table()
			# in receiving mode after sending the data or request			
			flag = "2"
		else:
			print "NOT FOUND ::: Route to destination does not exist"
			print "SEND	 ::: Broadcasting RREQ"
			
			for x in xrange(0,len(neighbours)):
				neighbour_node = neighbours.get(neighbours.keys()[x])
				RREQ = ["RREQ",[my_id,my_ip, my_port],my_seq_num, broadcast_num, [dest_id, dest_ip, dest_port], dest_seq_num, 0]
				RREQ = json.dumps(RREQ)
				sock.sendto(RREQ, (neighbour_node[1], neighbour_node[2]))	
				print "RREQ ::: TO ", neighbours.keys()[x] , ": FOR " , dest_id
				flag = "2"

	# receiving mode tasks
	elif (flag == "2"):
		while 1:
			#["RREQ",[src_id, src_ip, src_port], src_seq, src_brdcst, [dest_id, dest_ip, dest_port], dest_seq_num, hops]
			msg, sender_address = sock.recvfrom(4096)
			msg = json.loads(msg)
			#updateEntry = False
			#if it is RREQ packet
			print_route_table()
			if (msg[0] == "RREQ"):
				print "RREQ ::: FROM ", get_neighbour_name(sender_address[1])[0] 

				# if originator of RREQ is already in route table
				# if originator is receiving RREQ back to itself
				if (get_route_entry(msg[1][0]) is not None or msg[1][0] == my_id):
					print "DISCARD ::: RREQ Discarded"
				# if not in route table	
				# if not originator itself
				# add reverse entry in route table			
				else:
					if (msg[1][0]!=my_id):
						route_table.append([msg[1], get_neighbour_name(sender_address[1]), msg[6]+1, life_time,msg[5],1])
						#with open(route_table_name, 'wb') as f:
						#	pickle.dump(route_table, f)
					
					# if destination exists in route table
					if (exist_in_route_table(msg[4][0])):
						print "FOUND ::: Route to destination exists"
						route_entry = get_route_entry(msg[4][0])
						dest_seq_num = my_seq_num	#RFC3561: 6.6.2	
						RREP = ["RREP", route_entry[0], dest_seq_num, msg[1], route_entry[2], route_entry[3]]
						RREP = json.dumps(RREP)
						
						sock.sendto(RREP, tuple(get_next_hop(msg[1][0])[1:]))
						print "RREP ::: TO ", msg[1][0] , " FROM ", my_id
					
					# if routing entry is to be updated
					else:
						destination = msg[4][0]		
						# if destination is reached
						if (my_id == destination):
							print "FOUND ::: Destination found"
							dest_seq_num = msg[2]+1
							hop_count = 0
							RREP = ["RREP", [my_id, my_ip, my_port], dest_seq_num, msg[1], hop_count, "undefined"]
							
							# serialize the RREP list into json
							RREP = json.dumps(RREP)

							# send data to Next_hop that leads to destination
							sock.sendto(RREP, tuple(get_next_hop(msg[1][0])[1:]))
							print "RREP ::: TO ", get_next_hop(msg[1][0])[0] , " FROM ", my_id 
							
						else:
							print "NOT FOUND ::: Route to destination does not exist"
							
							# incrementing hop count
							msg[6] = msg[6]+1
							
							# broadcasting RREQ to neighbours
							for x in xrange(0,len(neighbours)):
								neighbour_node = neighbours.get(neighbours.keys()[x])
								RREQ = json.dumps(msg)
								
								#send data to neighbours
								sock.sendto(RREQ, (neighbour_node[1], neighbour_node[2]))	
								print "RREQ ::: TO ", neighbours.keys()[x] , ": FOR " , destination

			#if it is RREP packet
			elif(msg[0] == "RREP"):
				print msg
				print "RREP ::: FROM ", get_neighbour_name(sender_address[1])[0] , " TO ", my_id 
				
				#["RREP", [dest_id,dest_ip,dest_port], dest_seq_num, [src_id, src_ip, src_port], hop_count, life_time]
				if (exist_in_route_table(msg[1][0])):
					h_count = get_route_entry(msg[1][0])[2]
					if (h_count > msg[4]+1):
						route_table.remove(get_route_entry(msg[1][0]))
						route_table.append([msg[1], get_neighbour_name(sender_address[1]), msg[4]+1, life_time, msg[2],1])
				else:
					route_table.append([msg[1], get_neighbour_name(sender_address[1]), msg[4]+1, life_time, msg[2],1])
				
				#serializing routing table
				#with open(route_table_name, 'wb') as f:
				#	pickle.dump(route_table, f)
				
				#if RREP is reached at originator of RREQ: means route found.
				if (my_id == msg[3][0]):
					print "FOUND ::: Route found"
					print "SEND  ::: Sending data_msg to destination"
					originator = [my_id, my_ip, my_port]
					destination = dest_id
					data_msg = "This is a reply from " + my_ip + ":::" + my_id + ":::" + my_port 
					#serialize data list into json
					data = json.dumps(["DATA",originator,destination,data_msg])
					#send data to Next_hop that leads to destination
					# if (sock.sendto(data, tuple(get_next_hop(dest_id)[1:])) < 0):
					# 	for entry in xrange(0, len(route_table)):
					# 		if (route_table[entry][1] == get_next_hop(dest_id)):
					# 			route_table[entry][5] = 0
					sock.sendto(data, tuple(get_next_hop(dest_id)[1:]))
					print_route_table()
				else:
					#hop count incrementing
					msg[4] = msg[4]+1		
					#serializing msg into json
					RREP = json.dumps(msg)
					#send data to Next_hop that leads to destination
					sock.sendto(RREP, tuple(get_next_hop(msg[3][0])[1:]))
					print "RREP ::: FROM ", get_next_hop(msg[3][0])[0] , " TO ", my_id 
					
				
			#if it is DATA packet
			#data => ["DATA", [originator_id,originator_ip,originator_port], dest_id, data_msg]
			elif (msg[0] == "DATA"):
				#if data packet is received at destination
				if (msg[2] == my_id):
					#print msg
					print msg[3]
					originator = [my_id, my_ip, my_port]
					destination = msg[1][0]
					ddata_msg = "This is a reply from " + my_ip + ":::" + my_id + ":::" + my_port 
					#create reply msg and serialize into json
					data = json.dumps(["REPLYDATA",originator,destination,data_msg])
					#send data to Next_hop that leads to originator of data msg
					sock.sendto(data, tuple(get_next_hop(destination)[1:]))
				#if data packet is received at intermediate node (not at destination)
				else:
					if(exist_in_route_table(msg[2])):
						#print that forwarding data_msg to next hop
					 	print "[LOG] forwarding data_msg to", get_next_hop(msg[2])[0]
					 	#serialize the same msg into jso
					 	data = json.dumps(msg)
					 	#send the same msg to next hop that leads to destination
					 	sock.sendto(data, tuple(get_next_hop(msg[2])[1:]))
					else:
					 	# Generate a RERR message

			#if it is REPLYDATA packet
			elif (msg[0] == "REPLYDATA"):
				#if packet is received at destination
				if (msg[2] == my_id):
					print msg[3]
				#if packet is at intermediate node, forward it to next hop
				else:
					print "SEND ::: Forwarding data to", get_next_hop(msg[2])[0]
				 	data = json.dumps(msg)
				 	sock.sendto(data, tuple(get_next_hop(msg[2])[1:]))
		print_route_table()

	else:
		print "Invalid Input."


