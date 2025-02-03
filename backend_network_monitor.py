import dpkt
import time
import threading
from collections import deque
from multiprocessing import shared_memory

class OptimizedNetworkMonitor:
    def __init__(self, config):
        self.config = config
        self.buffer_size = 10000
        self.packet_buffer = deque(maxlen=self.buffer_size)
        self.threat_index = {}
        self.throughput = 0
        self.lock = threading.Lock()
        
        self.shm = shared_memory.SharedMemory(
            name='network_monitor', 
            create=True,
            size=1024*1024
        )
    
    def start(self):
        from socket import socket, AF_PACKET, SOCK_RAW
        self.sock = socket(AF_PACKET, SOCK_RAW)
        self.sock.bind((self.config.interface, 0x0003))
        
        while True:
            try:
                packet = self.sock.recv(65535)
                self.process_packet(packet)
            except Exception as e:
                logging.error(f"Packet processing error: {str(e)}")
    
    def process_packet(self, packet):
        eth = dpkt.ethernet.Ethernet(packet)
        if not isinstance(eth.data, dpkt.ip.IP):
            return
        
        ip = eth.data
        with self.lock:
            self._update_threat_index(ip.src)
            self._calculate_throughput(len(packet))
    
    def _update_threat_index(self, ip):
        self.threat_index[ip] = self.threat_index.get(ip, 0) + 1
    
    def _calculate_throughput(self, packet_size):
        current_time = time.time()
        if not hasattr(self, 'last_throughput_time'):
            self.last_throughput_time = current_time
            self.bytes_count = 0
        
        self.bytes_count += packet_size
        if current_time - self.last_throughput_time >= 1:
            self.throughput = self.bytes_count / (current_time - self.last_throughput_time)
            self.bytes_count = 0
            self.last_throughput_time = current_time
