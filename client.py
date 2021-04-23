import socket
import packet
import time
import random
import threading


PACKET_SIZE = 256
ADDRESS = ""
PORT = 42069
send_delay = 0.01

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.setblocking(0)

class Value: value = None

def listener(client, container):
	while True:
		try:
			data = packet.decode(client.recv(PACKET_SIZE))
			print(int(time.time()*1000), "SERVER RESPONSE:", data)
			container.value = data
		except:
			pass
		
		
def sender(client, container):
	while True:
		if container.value:
			client.sendto(container.value, (ADDRESS, PORT))
			container.value = None
		else: time.sleep(send_delay)
		


print("started")

rx_container, tx_container = Value(), Value()
rx_task = threading.Thread(target=listener, args=(client, rx_container), daemon=True)
tx_task = threading.Thread(target=sender, args=(client, tx_container), daemon=True)
rx_task.start()
tx_task.start()

while True:

	data = {0:(random.randint(0,30),), 1:[random.uniform(-100,100) for i in range(3)], 2:[random.uniform(-100,100) for i in range(2)]}
	data = packet.encode(data)
	tx_container.value = data
		
	
	time.sleep(1)



