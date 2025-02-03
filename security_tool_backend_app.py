#!/usr/bin/env python3
import os
import sys
import json
import logging
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
from werkzeug.serving import WSGIRequestHandler
import psutil

executor = ThreadPoolExecutor(max_workers=psutil.cpu_count(logical=False))

class HighPerformanceSecurityDashboard:
    def __init__(self, usb_path):
        self.usb_path = usb_path
        self.app = Flask(__name__, static_folder=None)
        CORS(self.app, resources={r"/*": {"origins": "*"}})
        
        self.app.config.update({
            'JSONIFY_PRETTYPRINT_REGULAR': False,
            'SEND_FILE_MAX_AGE_DEFAULT': 3600
        })
        
        self.config = SecurityConfig.load()
        self.network_monitor = OptimizedNetworkMonitor(self.config)
        self.ml_detector = AsyncMLDetector(self.config)
        
        self._configure_logging()
        self._setup_routes()
        self._start_background_services()
    
    def _configure_logging(self):
        logging.basicConfig(
            filename=os.path.join(self.usb_path, 'security_tool', 'logs', 'app.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        logging.getLogger().addHandler(logging.StreamHandler())
    
    def _setup_routes(self):
        @self.app.route('/')
        def serve_frontend():
            return send_from_directory(
                os.path.join(self.usb_path, 'security_tool', 'frontend'), 
                'index.html'
            )
        
        @self.app.route('/api/network/stats')
        def get_network_stats():
            return jsonify({
                'throughput': self.network_monitor.throughput,
                'connections': self.network_monitor.active_connections,
                'threats': self.network_monitor.threat_index
            })
        
        @self.app.route('/api/anomalies')
        def get_anomalies():
            return jsonify(self.ml_detector.get_latest_anomalies())
    
    def _start_background_services(self):
        executor.submit(self.network_monitor.start)
        executor.submit(self.ml_detector.process_queue)
    
    def run(self):
        WSGIRequestHandler.protocol_version = "HTTP/1.1"
        from waitress import serve
        serve(self.app, host='0.0.0.0', port=8000, threads=8)

if __name__ == "__main__":
    app = HighPerformanceSecurityDashboard(os.getcwd())
    app.run()
