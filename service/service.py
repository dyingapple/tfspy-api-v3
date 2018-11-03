#!/usr/bin/python3
import os
import json
import uuid
import time
import logging
import argparse
from flask import Flask, jsonify, request, redirect
from werkzeug import secure_filename
from datetime import datetime

import gpu

# Global
app = Flask(__name__)

@app.route('/v1/tasks', methods=['POST'])
def taskin():
	#request.files








#----------------------------------------------------------
#|			Initialize			  |
#----------------------------------------------------------
if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description="Inference Service",
		epilog='Developed by Wei Cheng \'dyingapple\' Fang')
	parser.add_argument('--host',
		help="Host running IP, default=0.0.0.0",
		type=str,
		nargs=1,
		default='0.0.0.0')
	parser.add_argument('-p', '--port',
		help="Host running port, default=8500",
		type=str,
		nargs=1,
		default='8500')
	parser.add_argument('-f','--file',
		help="Config file saved location, default=config.txt",
		type=str,
		nargs=1,
		default='config.txt')
	parsed, unparsed = parser.parse_known_args()

    save_location = os.path.abspath(parsed.save[0])
	if not os.path.exists(save_location):
		os.makedirs(save_location)

	app.debug = True

	# Set Logs 
	formatter = logging.Formatter(
		"[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
	handler = logging.FileHandler('service.log', encoding='UTF-8')
	handler.setLevel(logging.DEBUG)
	handler.setFormatter(formatter)
	log = logging.getLogger('werkzeug')
	log.setLevel(logging.DEBUG)
	log.addHandler(handler)
	app.logger.addHandler(handler)

	app.secret_key = 'v3superkey'
	app.config['SESSION_TYPE'] = 'filesystem'

	app.run(host=parsed.host, port=parsed.port, debug=True)
