from datetime import datetime as dt
from datetime import date  as d
import numpy as np
import sys,getopt
import dump_parser as wiki
import csv
import sqlite3



PAGE_ID = 0;
PAGE_NS = 1
REVISION_ID  = 2;
TIMESTAMP = 3;
CONTRIBUTOR_ID = 4;
CONTRIBUTOR_NAME = 5;
REVISION_BYTES = 6;
CSS_COLORS = ["Blue","DarkGreen","Crimson","Brown","CadetBlue","Chartreuse","Chocolate","Coral","CornflowerBlue","Crimson","DarkBlue","BlueViolet","DarkCyan","DarkGoldenRod","DarkGreen","DarkMagenta","DarkOliveGreen","Darkorange","DarkOrchid","DarkRed","DarkSalmon","DarkSeaGreen","DarkSlateBlue","DarkSlateGray","DarkSlateGrey","DarkTurquoise","DarkViolet","DeepPink","DeepSkyBlue","DimGray","DimGrey","DodgerBlue","FireBrick","FloralWhite","ForestGreen","Fuchsia","Gainsboro","GhostWhite","Gold","GoldenRod","Gray","Grey","Green","GreenYellow","HoneyDew","HotPink","IndianRed","Indigo","Ivory","Khaki","Lavender","LavenderBlush","LawnGreen","LemonChiffon","LightBlue","LightCoral","LightCyan","LightGoldenRodYellow","LightGray","LightGrey","LightGreen","LightPink","LightSalmon","LightSeaGreen","LightSkyBlue","LightSlateGray","LightSlateGrey","LightSteelBlue","LightYellow","Lime","LimeGreen","Linen","Magenta","Maroon","MediumAquaMarine","MediumBlue","MediumOrchid","MediumPurple","MediumSeaGreen","MediumSlateBlue","MediumSpringGreen","MediumTurquoise","MediumVioletRed","MidnightBlue","MintCream","MistyRose","Moccasin","NavajoWhite","Navy","OldLace","Olive","OliveDrab","Orange","OrangeRed","Orchid","PaleGoldenRod","PaleGreen","PaleTurquoise","PaleVioletRed","PapayaWhip","PeachPuff","Peru","Pink","Plum","PowderBlue","Purple","Red","RosyBrown","RoyalBlue","SaddleBrown","Salmon","SandyBrown","SeaGreen","SeaShell","Sienna","Silver","SkyBlue","SlateBlue","SlateGray","SlateGrey","Snow","SpringGreen","SteelBlue","Tan","Teal","Thistle","Tomato","Turquoise","Violet","Wheat","White","WhiteSmoke","Yellow","YellowGreen"]

LAST_RECORDED_DATE = dt.strptime("2013-11-01T12:00:00Z","%Y-%m-%dT%H:%M:%SZ")
USER_ID = 0;
LAST_REVISION = 1;
TOTAL_REVISIONS = 2;
TOTAL_BYTES = 3;
PATH = "D:/TFG/Python/"
HTML_OUTPUT_FILE = "D:/TFG/Python/"
ACTIVITY_LIMIT = 30



def count_entries(data,idx):
	dic={}
	for valor in data:
		key = valor[idx]
		if key in dic:
			dic[key]+=1
		else:
			dic[key] = 1
	return dic



def order_by_date(data_array,period = "day"):
	if period.lower() == "year":
		data_array[:,TIMESTAMP] = [ element.year for element in data_array[:,TIMESTAMP]]
	elif period.lower() == "month":
		data_array[:,TIMESTAMP] = [ dt(element.year,element.month,1) for element in data_array[:,TIMESTAMP]]

	date_sorted_data = sorted(data_array,key = lambda x:x[TIMESTAMP])
	date_sorted_data = np.array(date_sorted_data,dtype = object)
	return date_sorted_data



def normalize_data(data,idx):
	sigma = np.std(data[:,idx])
	data[:,idx] = [(d)/sum(data[:,idx]) for d in data[:,idx]]
	return data



def historical(data_array):
	sorted_counted_entries = order_by_date(data_array)
	result = [sorted_counted_entries[0]]
	for i in range(1,len(sorted_counted_entries)):
		result.append((sorted_counted_entries[i][0],sorted_counted_entries[i][1] + result[i-1][1]))
	a = np.array(result,dtype = object)
	return a



def load_data(data_file):
	file = open(data_file, encoding = 'utf-8')
	reader = csv.reader(file,delimiter=';')
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	print("Inserting wiki..")
	name = data_file[0:-15]
	c.execute("DELETE FROM wikis where name = ?",[name])
	c.execute("INSERT INTO wikis(name) values(?)",[name])
	c.execute("SELECT id from wikis where name =?",[name])
	wiki_id = c.fetchone()[0]
	#c.execute('DROP TABLE revisions')
	#c.execute('''CREATE TABLE revisionsa
	#			(wiki_id,page_id int,page_ns int,revision_id int, revision_date timestamp,contributor_id text, contributor_name text, revision_bytes int, month_group timestamp,year_group timestamp,creation number)''')
	print("Preparing data")
	data = [(wiki_id,int(row[PAGE_ID]),int(row[PAGE_NS]),int(row[REVISION_ID]),dt.strptime(row[TIMESTAMP],"%Y-%m-%dT%H:%M:%SZ"),row[CONTRIBUTOR_ID],row[CONTRIBUTOR_NAME],int(row[REVISION_BYTES])) for idx,row in enumerate(reader) if idx > 0]
	print("Inserting data...")
	c.executemany('INSERT INTO revisions(wiki_id,page_id,page_ns,revision_id,revision_date,contributor_id,contributor_name,revision_bytes,creation) VALUES(?,?,?,?,?,?,?,?,0)',data)
	c.execute("update revisions set month_group = date(revision_date,'start of month') where wiki_id =?",[wiki_id])
	c.execute("update revisions set year_group = date(revision_date,'start of year') where wiki_id =?",[wiki_id])
	print("Setting creations")
	c.execute("select id,page_id, min(revision_date) d from revisions where wiki_id =? group by page_id",[wiki_id] )
	result  = c.fetchall()
	c.executemany('UPDATE revisions SET creation = 1 where id = ? and page_id = ? and revision_date = ?',result)
	conn.commit()
	conn.close()
	print("Done!")
	return wiki_id


def historical_pages():
	conn = sqlite3.connect('wikis_db.sqlite')
	c = conn.cursor()
	c.execute('''
		select month_group,(select count(distinct(page_id)) 
		from revisions r1 
		where r1.month_group <= r.month_group) "pages" from revisions r 
		group by month_group''')
	r = c.fetchall()
	conn.close()
	return r



def load_all(args):
	for arg in args:
		yield load_data(arg)



def users_info(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month desc ",(wiki_id,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''SELECT contributor_name, MIN(revision_date) first,MAX(revision_date) as last,sum(creation) creations,sum(case when creation = 0 then 1 else 0 end) as editions
					from revisions
					where page_ns = 0 and month_group <= ?  and wiki_id = ?
					group by contributor_name
					having count(*) > 10
					order by creations,editions''',(date[0],wiki_id))
		result[date] = c.fetchall()
	conn.close()
	return result
	
def grouping(data,size=1):
	for i in range(0,len(data)//size):
			yield sum([int(v) for v in data[i*size:(i+1)*size]])


def ns_info(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=?  order by month desc ",(wiki_id,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''	SELECT 	page_ns,
							sum(creation) pages,
							sum(case when creation = 0 then 1 else 0 end) editions,
							count(distinct(contributor_id)) users,
							count(distinct(case when contributor_name <> 'Anonymous' then contributor_id else null end)) logged_users,
							count(distinct(case when contributor_name = 'Anonymous' then contributor_id else null end)) anonymous_users
						from revisions
						where month_group <= ? and wiki_id=?
						group by page_ns''',[date[0],wiki_id])
		result[date] = c.fetchall()
	conn.close()
	return result	
def pages_info(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month desc ",(wiki_id,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''SELECT 	page_id,
							MIN(revision_date) first,
							MAX(revision_date) as last,
							(count(*) - 1) revisions,
							count(distinct(contributor_id)) contributors,
							ROUND(AVG(revision_bytes),0) bytes
				from revisions
				where page_ns = 0 and month_group <= ?
				group by page_id''',date)
		result[date] = c.fetchall()
	conn.close()
	return result
def isActive(max_date,*args : object):
	result = []
	for date in args:
		delta = max_date - date
		result.append(delta.days < ACTIVITY_LIMIT)
	return result

def wiki_status(wiki):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month desc ",(wiki,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''SELECT	sum(creation) as pages,
							sum(case when creation = 0 then 1 else 0 end) editions,
							count(distinct(case when contributor_name <> 'Anonymous' then contributor_id else null end)) as logged_users,
							count(distinct(case when contributor_name = 'Anonymous' then contributor_id else null end)) as anonymous_users
					from revisions
					where month_group <= ? and page_ns = 0 and wiki_id = ?''',[date[0],wiki])
		result[date[0]] = c.fetchall()
	conn.close()
	return result

def create_index_table():
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute('CREATE TABLE wikis(id INTEGER PRIMARY KEY AUTOINCREMENT, name)');
	conn.close();

def get_all_wikis():
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute("select id from wikis where name not like '%zelda%'");
	result = c.fetchall();
	conn.close();
	return result
wikis = ["disney_pages_full.txt","enmarveldatabase_pages_full.txt","runescape_pages_full.txt","starwars_pages_full.txt","yugioh_pages_full.txt"]

def get_name(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute("select name from wikis where id = ?",(wiki_id,));
	result = c.fetchone();
	conn.close();
	return result[0]


def get_pages_editions(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute('''	SELECT page_id,count(*) editions
					from revisions
					where wiki_id = ? and page_ns = 0
					group by page_id
					order by editions desc''',(wiki_id,))
	result = c.fetchall()
	conn.close()
	return result

def get_users_editions(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute('''	SELECT contributor_id,count(*) editions
					from revisions
					where wiki_id = ? and page_ns = 0
					group by contributor_id
					order by editions desc''',(wiki_id,))
	result = c.fetchall()
	conn.close()
	return result

def get_classified_pages(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	result = []
	c.execute("""SELECT page_id,count(*) editions
				 from revisions
				 where page_ns = 0 and wiki_id = ?
				 group by page_id
				 having editions > 1000""",(wiki_id,))
	result.append(len(c.fetchall()))
	c.execute("""SELECT page_id,count(*) editions
				 from revisions
				 where page_ns = 0 and wiki_id = ?
				 group by page_id
				 having editions < 1000 and editions > 100""",(wiki_id,))
	result.append(len(c.fetchall()))	
	c.execute("""SELECT page_id,count(*) editions
				 from revisions
				 where page_ns = 0 and wiki_id = ?
				 group by page_id
				 having editions > 10 and editions < 100""",(wiki_id,))
	result.append(len(c.fetchall()))
	c.execute("""SELECT page_id,count(*) editions
				 from revisions
				 where page_ns = 0 and wiki_id = ?
				 group by page_id
				 having  editions < 10""",(wiki_id,))
	result.append(len(c.fetchall()))
	conn.close()
	return result


def get_classified_users(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month desc ",(wiki_id,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		row = []
		c.execute('''SELECT	count(contributor_id) editions, contributor_id
					from revisions
					where month_group = ? and page_ns = 0 and wiki_id = ?
					group by contributor_id
					having editions > 100''',[date[0],wiki_id])
		row.append(len(c.fetchall()))
		c.execute('''SELECT	count(contributor_id) editions, contributor_id
					from revisions
					where month_group = ? and page_ns = 0 and wiki_id = ?
					group by contributor_id
					having editions > 5 and editions < 100''',[date[0],wiki_id])
		row.append(len(c.fetchall()))
		c.execute('''SELECT	count(contributor_id) editions, contributor_id
					from revisions
					where month_group = ? and page_ns = 0 and wiki_id = ?
					group by contributor_id
					having editions < 5''',[date[0],wiki_id])
		row.append(len(c.fetchall()))
		result[date[0]] = row
	conn.close()
	return result

def reset_db():
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()

	c.execute('DROP TABLE IF EXISTS revisions')
	c.execute('''CREATE TABLE revisions
				(id INTEGER PRIMARY KEY AUTOINCREMENT,wiki_id int ,page_id int,page_ns int,revision_id int, revision_date timestamp,contributor_id text, contributor_name text, revision_bytes int, month_group timestamp,year_group timestamp,creation int)''')
	c.execute('DROP TABLE IF EXISTS wikis')
	c.execute('''CREATE TABLE wikis
				(id INTEGER PRIMARY KEY AUTOINCREMENT,name text)''')
	conn.close()

def top_users(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute('''SELECT contributor_name, sum(creation) creations,sum(case when creation = 0 then 1 else 0 end) as editions
					from revisions
					where wiki_id =? and contributor_name <> 'Anonymous'
					group by contributor_name
					order by editions desc
					limit 10''',(wiki_id,))
	result = c.fetchall()
	return result

def top_pages(wiki_id):
	conn = sqlite3.connect("wikis_db.sqlite")
	c = conn.cursor()
	c.execute('''SELECT page_id, count(*) as editions,count(distinct(contributor_id)) as contributors,MIN(revision_date) as created
					from revisions
					where wiki_id = ?
					group by page_id
					order by editions desc
					limit 10''',(wiki_id,))
	result = c.fetchall()
	return result
'''reset_db()
load_data("eszelda_pages_full.txt")'''
def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hi:o:l")
	except getopt.GetoptError:
		print('dataHandler.py -l <inputfile>')
		sys.exit(2)
	for opt, arg in opts:
		print(opt)
		print(arg)
		if opt == '-h':
			print('dataHandler.py -l <inputfile>')
			sys.exit()
		elif opt == "-l":
			load_data(arg)


