import socket
import packet
import time
import subprocess
import threading

PACKET_SIZE = 256
PORT = 42069
PROTOCOL = "UDP" #can be UDP or TCP

	
class Server:

	def __init__(self, port, protocol, packet_size, description="", timeout=10):
	
		self.port = port
		self.protocol = protocol
		self.packet_size = packet_size
		self.timeout = timeout
		self.history = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.local_ip, self.port))
		self.sock.setblocking(0)
		self.clients = {}
		
		
	def run_daemon(self):
	
		while True:
		
			now = time.time()
			now_ms = int(now*1000)
			
			try:
			
				data, address = self.sock.recvfrom(self.packet_size)
				print(now_ms, "CLIENT:", address)
				self.clients[address] = now

				for address, last_time in self.clients.copy().items():
					self.sock.sendto(data, address)
				
			except:
			
				if int(now) % 10 == 0:
					for address, last_time in self.clients.copy().items():

						if now - last_time > self.timeout:
							del self.clients[address]
							print(now_ms, "DISCONNECTED:", address)

				if not self.clients:
					time.sleep(0.01)
				
		print("Server stopped")
		
	
	def run(self):
		
		threading.Thread(target=self.run_daemon, daemon=True).start()
		print(f"Server is running on port: {self.port} and external ip: {self.external_ip}")

	
if __name__ == "__main__":
	s = Server(PORT, PROTOCOL, PACKET_SIZE)
	s.run()
	
