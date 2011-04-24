#
# written by Mike Borozdin
# @mikebz
#
# please keep the author's name in the code file if you are using
# this IP
# 
import json
from httplib import HTTPConnection
from pprint import pprint
import sys
import string
from array import array
from django.utils.encoding import smart_str, smart_unicode

api_key = "get this from factual.com"

'''
get the table data
'''
def get_table_data(table, search = ""):
	url = "http://api.factual.com"
	conn = HTTPConnection("api.factual.com")
	
	query = "/v2/tables/" + table + "/read?"
	if( search != "" ):
		query += "filters={\"$search\":\"" + search + "\"}&"		
	
	conn.request("GET", query + "api_key=" + api_key)
	
	resp = conn.getresponse()
	status = resp.status
	if status == 200 or status == 304:
		return resp.read()
		print result
	else:
		print 'Error status code: ', status
		
	return "";
	
def get_table_schema(table):
	url = "http://api.factual.com"
	conn = HTTPConnection("api.factual.com")
	conn.request("GET", "/v2/tables/" + table + "/schema?api_key=" + api_key)
	resp = conn.getresponse()
	status = resp.status
	if status == 200 or status == 304:
		return resp.read()
		print result
	else:
		print 'Error status code: ', status
		
	return "";	

def print_table(data, row_ids = [] ):
	
	#DEBUG
	#print 'in print_table'
	#pprint(row_ids)

	for row in data['response']['data']:
		
		for i in range( min(len(row), len(row_ids))):
			sys.stdout.write('-------------------------------')
		print ""
		
		for i in range(1, len(row) ): #there is a weird additional row
			cell = row[i]
			
 			# handle the case when only certain row ids
 			# were selected
 			# NOTE: adjusting for some additional row here.
 			if( len(row_ids) == 0 or (i-1) in row_ids):
	 			value = smart_str(cell)
 				if( len(value) > 30):
 					value = value[:26] + '...'
 				
 				sys.stdout.write( "|{0:29}".format(value))
 			# else:
 				# DEBUG
 				# sys.stdout.write( "|{0:30}".format('skipped cell'))
 		print "|"
 		
def print_table_list(data):
	for row in data['response']['data']:
 		print row[2]
 		
def handle_describe(x):
	tokens = x.split()
	if len( tokens ) < 2: 
		print 'you need to provide a table name'
		return
		
	result = get_table_data("hPMZ80", tokens[1])
	data = json.loads(result)
	if ( len(data['response']['data']) < 1 ):
 		print 'No table that matches your query'
 	else:
 		print 'Loading table data for: ' + tokens[1]
 		table_id = data['response']['data'][0][7]
 		result = get_table_schema(table_id)
 		schema_data = json.loads(result)
 		for field in schema_data['schema']['fields']:
 			print '.' + field['name'] + ' : ' + field['datatype']
 		#pprint(schema_data)
 		
def table_id_lookup(table_name):
	result = get_table_data("hPMZ80", table_name)
	data = json.loads(result)
	if ( len(data['response']['data']) < 1 ):
 		print 'No table that matches your query'
 		return ""
 	else:
 		table_id = data['response']['data'][0][7]
 		return table_id;

'''
this function will take a table and fields and return the columns for those ids
'''
def table_row_lookup(table_id, fields):
	
	#DEBUG
	#print 'in table_row_lookup'
	#pprint(fields)
	
	columns = []; #create an empty collection to append
	result = get_table_schema(table_id) #this returns a schema part of which is fields
 	schema_data = json.loads(result)
 	
 	i = 0
 	#
 	# for every field see if it's also in the "fields" paramter
 	# if it is then append it's index, if not then just move on.
 	for field in schema_data['schema']['fields']:
 	
 		#DEBUG
		#print 'field:'
		#pprint(field)
	
 		if field['name'] in fields:
 			columns.append(i)
 		i += 1
 	
 	#DEBUG
 	#print 'return'
 	#pprint (columns)
 	
 	return columns
 		
def handle_select(x):
	tokens = []
	
	# a little weird tokenizing to get rid of the separators
	for tok1 in x.split():
		for tok2 in tok1.split(','):
			tokens.append(tok2)
	
	#first ensure it looks like a real select
	if( tokens[0] != 'select'):
		print 'improper syntax: select statement is not starting with \"select...\"'
		return
	if not 'from' in tokens:
		print 'select statement needs to end with "from <table_name>"'
		return
	if tokens.index('from') == len(tokens) - 1:
		print 'select statement needs to end with "from <table_name>"'
		return
	if tokens.index('from') == 1:
		print 'please provide some fields to select or use "*"'
		return
	
	
	# lot's of assumptions here, but this is a hackathon after all
	table_name = tokens[len(tokens) - 1]
	fields = tokens[1 : -2]
	
	table_id = table_id_lookup( table_name )
	result = get_table_data( table_id )
	data = json.loads(result)
	
	# if there is a star we will just dump it all out.
	if( '*' in fields ):
 		print_table(data)
 		return
 	else:
 		row_ids = table_row_lookup(table_id, fields)
 		print_table(data, row_ids)

def print_help():
	print "Help is on the way!"
	print "Current commands: test, help, quit, tables, describe, select"
	

'''
The main function that parses user input
'''
if __name__ == "__main__":
	x = ""
 	while x != 'quit' and x != 'exit' and x != 'q':
		x = raw_input('factual command> ')
		x = x.lower().strip()
		
		if x == "test":
			result = get_table_data("GxpamT")
 			data = json.loads(result)
 			print_table(data)
 		
 		elif x == 'tables':
 			result = get_table_data("hPMZ80")
 			data = json.loads(result)
 			print_table_list(data)
 			
 		elif x.startswith('describe'):
 			handle_describe(x)
 			
 		elif x.startswith('select'):
 			handle_select(x)
 			
 		# all the quitting functions	
		elif x == "quit":
			print "exiting..."
		elif x == "q":
			print "exiting..."
		elif x == "exit":
			print "exiting..."
		else:
			print 'does not compute. type help or quit'
