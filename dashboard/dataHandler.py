from datetime import datetime as dt
from datetime import date  as d
import numpy as np
import sys,getopt
import dump_parser as wiki
import csv
import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "wikis_db.sqlite")


PAGE_ID = 0;
PAGE_TITLE = 1
PAGE_NS = 2
REVISION_ID  = 3;
TIMESTAMP = 4;
CONTRIBUTOR_ID = 5;
CONTRIBUTOR_NAME = 6;
REVISION_BYTES = 7;
CSS_COLORS = ["Blue","DarkGreen","Crimson","Brown","CadetBlue","Chartreuse","Chocolate","Coral","CornflowerBlue","Crimson","DarkBlue","BlueViolet","DarkCyan","DarkGoldenRod","DarkGreen","DarkMagenta","DarkOliveGreen","Darkorange","DarkOrchid","DarkRed","DarkSalmon","DarkSeaGreen","DarkSlateBlue","DarkSlateGray","DarkSlateGrey","DarkTurquoise","DarkViolet","DeepPink","DeepSkyBlue","DimGray","DimGrey","DodgerBlue","FireBrick","FloralWhite","ForestGreen","Fuchsia","Gainsboro","GhostWhite","Gold","GoldenRod","Gray","Grey","Green","GreenYellow","HoneyDew","HotPink","IndianRed","Indigo","Ivory","Khaki","Lavender","LavenderBlush","LawnGreen","LemonChiffon","LightBlue","LightCoral","LightCyan","LightGoldenRodYellow","LightGray","LightGrey","LightGreen","LightPink","LightSalmon","LightSeaGreen","LightSkyBlue","LightSlateGray","LightSlateGrey","LightSteelBlue","LightYellow","Lime","LimeGreen","Linen","Magenta","Maroon","MediumAquaMarine","MediumBlue","MediumOrchid","MediumPurple","MediumSeaGreen","MediumSlateBlue","MediumSpringGreen","MediumTurquoise","MediumVioletRed","MidnightBlue","MintCream","MistyRose","Moccasin","NavajoWhite","Navy","OldLace","Olive","OliveDrab","Orange","OrangeRed","Orchid","PaleGoldenRod","PaleGreen","PaleTurquoise","PaleVioletRed","PapayaWhip","PeachPuff","Peru","Pink","Plum","PowderBlue","Purple","Red","RosyBrown","RoyalBlue","SaddleBrown","Salmon","SandyBrown","SeaGreen","SeaShell","Sienna","Silver","SkyBlue","SlateBlue","SlateGray","SlateGrey","Snow","SpringGreen","SteelBlue","Tan","Teal","Thistle","Tomato","Turquoise","Violet","Wheat","White","WhiteSmoke","Yellow","YellowGreen"]

LAST_RECORDED_DATE = dt.strptime("2013-11-01T12:00:00Z","%Y-%m-%dT%H:%M:%SZ")
USER_ID = 0;
LAST_REVISION = 1;
TOTAL_REVISIONS = 2;
TOTAL_BYTES = 3;
ACTIVITY_LIMIT = 30




def load_data(data_file):
	file = open(data_file, encoding = 'utf-8')
	reader = csv.reader(file,delimiter=';')
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	data = [row for row in reader]
	name = data[1][0]
	print("Inserting wiki "+name)
	c.execute("DELETE FROM wikis where name = ?",[name])
	c.execute("INSERT INTO wikis(name) values(?)",[name])
	c.execute("SELECT id from wikis where name =?",[name])
	wiki_id = c.fetchone()[0]
	print("Preparing data")
	data = [(wiki_id,int(row[PAGE_ID]),row[PAGE_TITLE],int(row[PAGE_NS]),int(row[REVISION_ID]),dt.strptime(row[TIMESTAMP],"%Y-%m-%dT%H:%M:%SZ"),row[CONTRIBUTOR_ID],row[CONTRIBUTOR_NAME],int(row[REVISION_BYTES])) for row in data[2:-1]]
	print("Inserting data...")
	c.executemany('INSERT INTO revisions(wiki_id,page_id,page_title,page_ns,revision_id,revision_date,contributor_id,contributor_name,page_size,creation) VALUES(?,?,?,?,?,?,?,?,?,0)',data)
	c.execute("update revisions set month_group = date(revision_date,'start of month') where wiki_id =?",[wiki_id])
	c.execute("update revisions set year_group = date(revision_date,'start of year') where wiki_id =?",[wiki_id])
	print("Setting creations")
	c.execute("select id,page_id, min(revision_date) d from revisions where wiki_id =? group by page_id",[wiki_id] )
	result  = c.fetchall()
	c.executemany('UPDATE revisions SET creation = 1 where id = ? and page_id = ? and revision_date = ?',result)
	c.execute("select distinct(page_id) from revisions where wiki_id = ?",[wiki_id])
	for page in c.fetchall():
		page = page[0]
		print("Setting revision bytes for page " + str(page))
		c.execute("select id,revision_id,page_size,revision_date from revisions where page_id = ? and wiki_id = ? order by revision_date asc",(page,wiki_id))
		revisions = c.fetchall()
		r_bytes = []
		for i in reversed(range(0,len(revisions))):
			r_bytes.insert(0,(abs(revisions[i][2]-revisions[i-1][2]),revisions[i][0]))
		c.executemany("update revisions set revision_bytes = ? where id = ?",r_bytes)
	conn.commit()
	conn.close()
	print("Done!")
	return wiki_id


def load_all(args):
	for arg in args:
		yield load_data(arg)



def users_info(wiki_id):
	conn = sqlite3.connect(db_path)
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
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=?  order by month desc ",(wiki_id,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''	SELECT 	page_ns,count(distinct(page_id))
						from revisions
						where month_group <= ? and wiki_id=?
						group by page_ns''',[date[0],wiki_id])
		result[dt.strptime(date[0],"%Y-%m-%d")] = c.fetchall()
	conn.close()
	return result	
def pages_info(wiki_id):
	conn = sqlite3.connect(db_path)
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
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month asc ",(wiki,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''SELECT	sum(creation) as pages,
							sum(case when creation = 0 then 1 else 0 end) editions,
							count(distinct(case when contributor_name <> 'Anonymous' then contributor_id else null end)) as logged_users,
							count(distinct(case when contributor_name = 'Anonymous' then contributor_id else null end)) as anonymous_users,
							avg(case when creation = 1  then null else revision_bytes end) avg_revision_bytes
					from revisions
					where month_group <= ? and page_ns = 0 and wiki_id = ?''',[date[0],wiki])
		result[dt.strptime(date[0],"%Y-%m-%d")] = c.fetchall()
	conn.close()
	return result
def monthly_avg_bytes(wiki_id):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute('''SELECT	month_group, avg(case when creation = 1 then null else revision_bytes end) avg_revision_bytes
					from revisions
					 where page_ns = 0 and wiki_id = ?
					 group by month_group
					 order by month_group asc''',(wiki_id,))
	result = c.fetchall()
	conn.close()
	return result

def create_index_table():
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute('CREATE TABLE wikis(id INTEGER PRIMARY KEY AUTOINCREMENT, name)');
	conn.close();

def get_all_wikis():
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("select id from wikis where name not like '%zelda%'");
	result = c.fetchall();
	conn.close();
	return result

def get_name(wiki_id):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("select name from wikis where id = ?",(wiki_id,));
	result = c.fetchone();
	conn.close();
	return result[0]


def get_pages_editions(wiki_id):
	conn = sqlite3.connect(db_path)
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
	conn = sqlite3.connect(db_path)
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
	conn = sqlite3.connect(db_path)
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
	conn = sqlite3.connect(db_path)
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
	conn = sqlite3.connect(db_path)
	c = conn.cursor()

	c.execute('DROP TABLE IF EXISTS revisions')
	c.execute('''CREATE TABLE revisions
				(id INTEGER PRIMARY KEY AUTOINCREMENT,wiki_id int ,page_id int,page_title text,page_ns int,revision_id int, revision_date timestamp,contributor_id text, contributor_name text, page_size int,revision_bytes int, month_group timestamp,year_group timestamp,creation int)''')
	c.execute('DROP TABLE IF EXISTS wikis')
	c.execute('''CREATE TABLE wikis
				(id INTEGER PRIMARY KEY AUTOINCREMENT,name text)''')
	conn.close()

def top_users(wiki_id):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month asc ",(wiki_id,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''SELECT contributor_name, sum(creation) creations,sum(case when creation = 0 then 1 else 0 end) as editions
						from revisions
						where wiki_id =? and contributor_name <> 'Anonymous' and contributor_name <> 'Wikia' and month_group <=?
						group by contributor_name
						order by editions desc''',(wiki_id,date[0]))
		result[dt.strptime(date[0],"%Y-%m-%d")] = c.fetchall()
	return result

def top_pages(wiki_id):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month asc ",(wiki_id,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''SELECT page_id,page_title, MIN(revision_date)  as created,count(*) as editions,count(distinct(contributor_id)) as contributors
						from revisions
						where wiki_id = ? and month_group <=?
						group by page_id
						order by editions desc
						limit 10''',(wiki_id,date[0]))
		result[dt.strptime(date[0],"%Y-%m-%d")]= c.fetchall()
	return result
def edited_pages(wiki_id):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute('''SELECT month_group,COUNT(DISTINCT(PAGE_ID))
				FROM REVISIONS
				WHERE wiki_id = ? and page_ns = 0 and creation = 0
				group by month_group
				order by month_group asc''',(wiki_id,))
	result = c.fetchall()
	return result

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

		

def get_editions_by_author_type(wiki_id):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute('''SELECT month_group,
				(select count(*) from revisions r1 where r1.wiki_id = ? and r1.month_group = r.month_group and r1.page_ns = 0 and r1.contributor_name <> 'Anonymous' and creation = 0) logged,
				(select count(*) from revisions r1 where r1.wiki_id = ? and r1.month_group = r.month_group and r1.page_ns = 0 and r1.contributor_name = 'Anonymous' and creation = 0) anonymous
				from revisions r
				where r.page_ns = 0 and r.wiki_id = ?
			group by month_group
			order by month_group asc''',[wiki_id,wiki_id,wiki_id])
	result = c.fetchall()
	return result

def get_average_page_size(wiki_id):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month desc ",(wiki_id,))
	dates = c.fetchall()
	result ={}
	for date in dates:
		c.execute('''SELECT	page_id,
							max(revision_date),
							revision_bytes,
							revision_id
					 from revisions
				    where month_group <= ? and page_ns = 0 and wiki_id = ?
				    group by page_id
					''',[date[0],wiki_id])
		fetch = np.array(c.fetchall(),dtype="object")
		result[date[0]] = np.mean(fetch[:,2])
	conn.close()
	return result

if __name__ == "__main__":
	if(sys.argv):
		print("Loading file " + sys.argv[1])
		reset_db()
		load_data(sys.argv[1])