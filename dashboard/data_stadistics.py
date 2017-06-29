#!/usr/bin/python3
# -*- coding: utf-8 -*-
from datetime import datetime as dt
import numpy as np
import sqlite3
import os.path

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'databases')
global c, conn, db_path;
db_path = os.path.join(BASE_DIR, "wikis_db.sqlite")


'''
  Open and close ddbb
'''

def init_stadistics(db_name):
  db_path = os.path.join(BASE_DIR, db_name)
  conn = sqlite3.connect(db_path)
  c = conn.cursor()


def end_stadistics():
  conn.close();


'''
  Currently being used Statistics
'''


def get_name(wiki_id):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("select name from wikis where id = ?",(wiki_id,));
  result = c.fetchone();
  conn.close();
  return result[0]


def wiki_status(wiki):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month asc ",(wiki,))
  dates = c.fetchall()
  result ={}
  for date in dates:
    c.execute('''SELECT sum(creation) as pages,
              sum(case when creation = 0 then 1 else 0 end) editions,
              count(distinct(case when contributor_name <> 'Anonymous' then contributor_id else null end)) as logged_users,
              count(distinct(case when contributor_name = 'Anonymous' then contributor_id else null end)) as anonymous_users,
              avg(case when creation = 1  then null else revision_bytes end) avg_revision_bytes
          from revisions
          where month_group <= ? and page_ns = 0 and wiki_id = ?''',[date[0],wiki])
    result[dt.strptime(date[0],"%Y-%m-%d")] = c.fetchall()
  conn.close()
  return result


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


def get_classified_users(wiki_id):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month desc ",(wiki_id,))
  dates = c.fetchall()
  result ={}
  for date in dates:
    row = []
    c.execute('''SELECT count(contributor_id) editions, contributor_id
          from revisions
          where month_group = ? and page_ns = 0 and wiki_id = ?
          group by contributor_id
          having editions > 100''',[date[0],wiki_id])
    row.append(len(c.fetchall()))
    c.execute('''SELECT count(contributor_id) editions, contributor_id
          from revisions
          where month_group = ? and page_ns = 0 and wiki_id = ?
          group by contributor_id
          having editions > 5 and editions < 100''',[date[0],wiki_id])
    row.append(len(c.fetchall()))
    c.execute('''SELECT count(contributor_id) editions, contributor_id
          from revisions
          where month_group = ? and page_ns = 0 and wiki_id = ?
          group by contributor_id
          having editions < 5''',[date[0],wiki_id])
    row.append(len(c.fetchall()))
    result[date[0]] = row
  conn.close()
  return result


def get_average_page_size(wiki_id):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month desc ",(wiki_id,))
  dates = c.fetchall()
  result ={}
  for date in dates:
    c.execute('''SELECT page_id,
              max(revision_date),
              page_size,
              revision_id
           from revisions
            where month_group <= ? and page_ns = 0 and wiki_id = ?
            group by page_id
          ''',[date[0],wiki_id])
    fetch = np.array(c.fetchall(),dtype="object")
    result[date[0]] = np.mean(fetch[:,2])
  conn.close()
  return result


def monthly_avg_bytes(wiki_id):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute('''SELECT month_group, avg(case when creation = 1 then null else revision_bytes end) avg_revision_bytes
          from revisions
           where page_ns = 0 and wiki_id = ?
           group by month_group
           order by month_group asc''',(wiki_id,))
  result = c.fetchall()
  conn.close()
  return result


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


def get_edited_by_users(wiki_id):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month asc ",(wiki_id,))
  dates = c.fetchall()
  result ={}
  for date in dates:
    c.execute('''SELECT distinct(contributor_id), contributor_name from revisions where month_group = ? and page_ns = 0 and wiki_id = ?''',(date[0],wiki_id))
    users = c.fetchall()
    date_result = {}
    for user in users:
      u_result = []
      c.execute('''SELECT page_title
              from revisions
              where wiki_id = ? and month_group=? and contributor_id = ?''',(wiki_id,date[0],user[0]))
      for i in c.fetchall():
        u_result.append(i[0])
      if user[1] != 'Anonymous':
        date_result[user[1]] =tuple(u_result)
      else:
        date_result[user[0]] =tuple(u_result)
    result[dt.strptime(date[0],"%Y-%m-%d")]= date_result
  return result


'''
  Currently unused Statistics
'''


def ns_info(wiki_id):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("SELECT distinct(month_group) month from revisions where wiki_id=?  order by month desc ",(wiki_id,))
  dates = c.fetchall()
  result ={}
  for date in dates:
    c.execute(''' SELECT  page_ns,count(distinct(page_id))
            from revisions
            where month_group <= ? and wiki_id=?
            group by page_ns''',[date[0],wiki_id])
    result[dt.strptime(date[0],"%Y-%m-%d")] = c.fetchall()
  conn.close()
  return result


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


def pages_info(wiki_id):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("SELECT distinct(month_group) month from revisions where wiki_id=? and page_ns = 0 order by month desc ",(wiki_id,))
  dates = c.fetchall()
  result ={}
  for date in dates:
    c.execute('''SELECT   page_id,
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


def get_all_wikis():
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute("select id from wikis where name not like '%zelda%'");
  result = c.fetchall();
  conn.close();
  return result


def get_pages_editions(wiki_id):
  conn = sqlite3.connect(db_path)
  c = conn.cursor()
  c.execute(''' SELECT page_id,count(*) editions
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
  c.execute(''' SELECT contributor_id,count(*) editions
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
    c.execute('''SELECT count(contributor_id) editions, contributor_id
          from revisions
          where month_group = ? and page_ns = 0 and wiki_id = ?
          group by contributor_id
          having editions > 100''',[date[0],wiki_id])
    row.append(len(c.fetchall()))
    c.execute('''SELECT count(contributor_id) editions, contributor_id
          from revisions
          where month_group = ? and page_ns = 0 and wiki_id = ?
          group by contributor_id
          having editions > 5 and editions < 100''',[date[0],wiki_id])
    row.append(len(c.fetchall()))
    c.execute('''SELECT count(contributor_id) editions, contributor_id
          from revisions
          where month_group = ? and page_ns = 0 and wiki_id = ?
          group by contributor_id
          having editions < 5''',[date[0],wiki_id])
    row.append(len(c.fetchall()))
    result[date[0]] = row
  conn.close()
  return result


