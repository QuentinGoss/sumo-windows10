#!flask/bin/python

import sys

from flask import Flask, render_template, request, redirect, Response
import random, json

app = Flask(__name__, template_folder='template')

@app.route('/')
def output():
	# serve index template
	return render_template('index.html', name='Joe')

@app.route('/receiver', methods = ['POST'])
def worker():
	# read json + reply
	data = request.get_data()
	result = ''
	print(data)
	'''
	for item in data:
		# loop over every row
		result += str(item['make']) + '\n'
	'''
	return result

if __name__ == '__main__':
	# run!
	app.run()