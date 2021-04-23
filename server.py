import socket
import packet
import time
import subprocess
import threading

PACKET_SIZE = 256
PORT = 42069
PROTOCOL = "UDP" #can be UDP or TCP
PORT_DESCRIPTION = "my python server"


class Commands:

	def __init__(self, s):
		self.s = s
		self.help_message = "Type \"help\" for a list of commands."
		self.commands = {"help":self.help, "quit":self.quit, "ip":self.ip, "port":self.port,
						 "protocol":self.protocol}
		
	def is_command(self, command):
		return command in self.commands
		
	def run(self, command):
		split = command.split()

		if split and self.is_command(split[0].lower()):
			args = " ".join(split[1:])
			self.commands[split[0].lower()](args)
		else:
			print("Command not found. "+self.help_message)
	
	def help(self, command):
		"""Displays help message"""
		print("Available commands:\n\n"+"\n".join(f"{k}: {v.__doc__}" for k, v in self.commands.items())+"\n")
	
	def quit(self, args):
		"""Stop the server and exit"""
		self.s.stop_flag = True
		
	def ip(self, args):
		"""See the external IP address of the server"""
		print(self.s.external_ip)
		
	def port(self, args):
		"""See the port of the server"""
		print(self.s.port)
		
	def protocol(self, args):
		"""See the connection protocol of the server"""
		print(self.s.protocol)

	
class Server:

	def __init__(self, port, protocol, packet_size, description="", timeout=10):
	
		self.port = port
		self.protocol = protocol
		self.packet_size = packet_size
		self.description = description
		self.timeout = timeout
		self.stop_flag = False
	
		self.get_device_info()
		self.forward()
	
		self.history = []
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((self.local_ip, self.port))
		self.sock.setblocking(0)
		self.clients = {}
		
		
	def get_device_info(self):
		output = subprocess.check_output(["upnpc", "-s"]).decode("utf-8").split("\r\n")
		self.desc_url = [i.split()[-1] for i in output if "desc" in i.lower()][0]
		self.addresses = [i.split()[-1] for i in output if "address" in i.lower()]
		self.local_ip = self.addresses[0]
		self.external_ip = self.addresses[1]
		

	def forward(self):
		output = subprocess.call(["upnpc", "-u", self.desc_url, "-e", self.description,
		"-a", self.local_ip, str(self.port), str(self.port), self.protocol], stderr=subprocess.DEVNULL)
		
		
	def run_daemon(self):
	
		while not self.stop_flag:
		
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
					time.sleep(0.05)
				
		print("Server stopped")
		
	
	def run(self):
		
		threading.Thread(target=self.run_daemon, daemon=True).start()
		print(f"Server is running on port: {self.port} and external ip: {self.external_ip}")
		
		commands = Commands(self)
		print(commands.help_message)
		
		while not self.stop_flag:
			command = input(">> ")
			commands.run(command)
				




				
if __name__ == "__main__":
	s = Server(PORT, PROTOCOL, PACKET_SIZE, PORT_DESCRIPTION)
	s.run()
	
