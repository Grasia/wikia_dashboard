#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime as dt
from datetime import date as d
import argparse
import csv
import sqlite3
import os.path
import sys

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'databases')
if (not os.path.isdir(BASE_DIR)):
  os.mkdir(BASE_DIR)

Debug = True

PAGE_ID = 0
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
  reader = csv.reader(file,delimiter=';',quotechar='|')
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
    if Debug:
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


def grouping(data,size=1):
  for i in range(0,len(data)//size):
      yield sum([int(v) for v in data[i*size:(i+1)*size]])


def isActive(max_date,*args : object):
  result = []
  for date in args:
    delta = max_date - date
    result.append(delta.days < ACTIVITY_LIMIT)
  return result


def create_index_table(db_path):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute('CREATE TABLE wikis(id INTEGER PRIMARY KEY AUTOINCREMENT, name)');
  c.execute('CREATE TABLE revisions(id INTEGER PRIMARY KEY AUTOINCREMENT, wiki_id int, page_id int, page_title text, page_ns int, revision_id int, revision_date timestamp, contributor_id text, contributor_name text, page_size int, revision_bytes int, month_group timestamp, year_group timestamp, creation int)');
  conn.close();


def reset_db(db_path):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()

  c.execute('DROP TABLE IF EXISTS revisions')
  c.execute('''CREATE TABLE revisions
        (id INTEGER PRIMARY KEY AUTOINCREMENT,wiki_id int ,page_id int,page_title text,page_ns int,revision_id int, revision_date timestamp,contributor_id text, contributor_name text, page_size int,revision_bytes int, month_group timestamp,year_group timestamp,creation int)''')
  c.execute('DROP TABLE IF EXISTS wikis')
  c.execute('''CREATE TABLE wikis
        (id INTEGER PRIMARY KEY AUTOINCREMENT,name text)''')
  conn.close()


args_parser = argparse.ArgumentParser(description="Generate a SQLite database from a csv file of wiki revisions")
args_parser.add_argument("inputfile", nargs='?', help="The input csv file to get data from to insert into the database")
args_parser.add_argument("-r", "--reset", action='store_true', help="Delete all current data stored in database. Optionally, creates new database if used along with <inputfile> data.")
args_parser.add_argument("-db", "--database", default='wikis_db', help="Set database to store data into or to reset. Default is 'wikis_db'")
args = args_parser.parse_args()

if len(sys.argv) < 2:
  args_parser.print_help()


#if args.database:
  #db_name = args.database
#else:
  #db_name = "wikis_db.sqlite"

db_name = args.database + '.sqlite'
db_path = os.path.join(BASE_DIR, db_name)

if not os.path.isfile(db_path):
  create_index_table(db_path)

if args.reset:
  if os.path.isfile(db_path):
    reset_db(db_path)
    print('All data in %s has been deleted' % db_name)
  else:
    print('No database found to reset', file=sys.stderr)


if args.inputfile:
  if os.path.isfile(args.inputfile):
    load_data(args.inputfile)
  else:
    print('Input file <' + args.inputfile + '> not found', file=sys.stderr)
