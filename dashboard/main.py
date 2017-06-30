#!/usr/bin/python3
# -*- coding: utf-8 -*-

from datetime import datetime as dt
from datetime import date  as d
import numpy as np
import data_statistics as dh
from bokeh.plotting import figure, output_file,show,gridplot,ColumnDataSource,curdoc
from bokeh.models import LinearAxis, Range1d, HoverTool,CustomJS,Tabs,Panel,SingleIntervalTicker, LinearAxis
import pandas as pd
import math
from bkcharts import Donut, Area, Bar, Scatter, HeatMap
from bokeh.models.widgets import Slider, Button, Select ,DataTable, TableColumn,CheckboxGroup,Div
from bokeh.layouts import row,widgetbox,Column,layout
from six.moves import zip
from bokeh.palettes import small_palettes
from random import randint
import sys
from bokeh.palettes import Paired9,Reds5
from numpy import pi
import pickle
import os.path
import sys

# For production code:
# BOKEH_VALIDATE_DOC=false

import gc
import marshal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_DIR, "templates")
WIDTH = 1300
HEIGHT = 300
NAMESPACES = {  -2:"Media",
  -1:"Special",
  0:"Main content",
  1:"Talk",
  2:"User",
  3:"User talk",
  4:"Project",
  5:"Project talk",
  6:"File",
  7:"File talk",
  8:"MediaWiki",
  9:"MediaWiki talk",
  10:"Template",
  11:"Template talk",
  12:"Help",
  13:"Help Talk",
  14:"Category",
  15:"Category talk",
  110:"Forum",
  111:"Forum talk",
  500:"User blog",
  501:"User blog comments",
  502:"Blog",
  503:"Blog talk",
  1200:"Message Wall",
  1201:"Thread",
  1202:"Message Wall Greeting",
  2000: "Board",
  2001: "Board Thread",
  2002:"Topic"
}


def generate_users_bar(current_user_source):
  users_bar = Bar(current_user_source,values="editions",xlabel = None,ylabel = None,label="users",stack="edited",legend = None,title = "Editions for users",name ="Editions for users",tools = tools, width = 1000,height = 400)
  hover = users_bar.select(dict(type=HoverTool))
  hover.tooltips = [
  ('User','$x'),
  ('Page','@edited'),
  ('Editions','@height')]
  users_bar.background_fill_color = "#2f2f2f"
  users_bar.border_fill_color = "#2f2f2f"
  return users_bar
def generate_pages_bar(current_pages_source):
  pages_bar = Bar(current_pages_source,values="editions",label="edited",xlabel = None,ylabel = None, stack="users",legend = None,title = "Editions for pages",name ="Editions for pages",tools = tools, width = 600,height = 400)
  hover = pages_bar.select(dict(type=HoverTool))
  hover.tooltips = [
  ('Page','$x'),
  ('User','@users'),
  ('Editions','@height')
  ]
  pages_bar.background_fill_color = "#2f2f2f"
  pages_bar.border_fill_color = "#2f2f2f"
  return pages_bar
def generate_editors_df(hm_data):
  hm_df={}
  hm_df['users'] = []
  hm_df['edited'] = []
  hm_df['editions']= []
  result = {}
  for user in hm_data:
          elements = list(set(hm_data[user]))
          for page in elements:
                  hm_df['users'].append(str(user))
                  hm_df['edited'].append(str(page))
                  hm_df['editions'].append(hm_data[user].count(page))
  return hm_df


def get_width(source):
    mindate = min(source.data['dates'])
    maxdate = max(source.data['dates'])
    return 0.8 * (maxdate-mindate).total_seconds()*1000 / len(source.data['dates'])


def get_difference(current,last,idx):
  diff = round(current-last,2) if idx >0 else current
  if idx == 0 or diff > 0:
    arrow = '<img src="dashboard/static/up.png" style="vertical-align:middle" width = 20 height= 20 /> '
    value = '<span style = "color:#44dd34"> ' + str(abs(diff)) +' </span>'
  elif diff <0:
    arrow = '<img src="dashboard/static/down.png"  style="vertical-align:middle" width = 20 height= 20 /> '
    value = '<span style = "color:#e6286a"> ' + str(abs(diff)) +' </span>'
  else:
    arrow = '<img src="dashboard/static/equal.png"  style="vertical-align:middle" width = 20 height= 20 /> '
    value = '<span style = "color:#00a2ff"> ' + str(abs(diff)) +' </span>'
  return "("+arrow+value+")"


def banners_html(idx):
  total_pages = pages[idx]
  total_editions = editions[idx]
  logged_users = logged[idx]
  anonymous_users = anonymous[idx]
  days = (dates[idx]-dates[0]).days+30
  active_users =total_active_users[idx]
  td_style ='''"text-align:center;border: 1px solid white;font-size:1.5em; border-radius: 10px;padding: 10px 0px"'''
  image_style = '''"vertical-align:middle; margin-right: 5px;width:50px;height:50px"'''
  return '''
                  <table style = "width:100%">
                          <tr>
                          <td style='''+td_style+'''><img src="'''+"dashboard/static/pages.png"+'''"  style='''+image_style+'''/>'''+str(total_pages)+''' '''+get_difference(total_pages,pages[idx-1],idx)+''' </td>
                          <td style='''+td_style+'''><img src="'''+"dashboard/static/editions.png"+'''" style='''+image_style+''' />''' +str(total_editions)+''' '''+get_difference(total_editions,editions[idx-1],idx)+'''</td>
                          <td style='''+td_style+'''><img src="'''+"dashboard/static/logged_user.png"+'''"  style='''+image_style+''' />'''+str(logged_users)+''' '''+get_difference(logged_users,logged[idx-1],idx)+'''</td>
                          <td style='''+td_style+'''><img src="'''+"dashboard/static/anonym_user.png"+'''"  style='''+image_style+''' />'''+str(anonymous_users)+''' '''+get_difference(anonymous_users,anonymous[idx-1],idx)+'''</td>
                          </tr>
                          <tr>
                          <td style='''+ td_style +'''> Total pages / logged users: '''+ str(round(total_pages/logged_users,2)) +''' '''+get_difference(round(total_pages/logged_users,2),round(pages[idx-1]/logged[idx-1],2),idx)+ '''</td>
                          <td style='''+ td_style +'''> Total editions / total pages: ''' + str(round(total_editions/total_pages,2)) +''' '''+get_difference(round(total_editions/total_pages,2),round(editions[idx-1]/pages[idx-1],2),idx)+ '''</td>
                          <td style='''+ td_style +'''> Total editions / total days: '''+ str(round(total_editions/days,2)) + ''' '''+get_difference(round(total_editions/days,2),round(editions[idx-1]/((dates[idx-1]-dates[0]).days+30),2),idx)+'''</td>
                          <td style='''+ td_style +''' > Users who edited this month: '''+ str(active_users) + ''' '''+get_difference(total_active_users[idx],total_active_users[idx-1],idx)+'''</td>
                          </tr>
                  </table>
'''


def get_creation_date(creation_date,actual_date):
  diff = actual_date - creation_date
  days = diff.days + 30
  if days < 31:
          return str(days) + " days ago"
  elif days < 60:
          return str(int(round(days /7,0))) + " weeks ago"
  elif days < 365:
          return str(int(round(days / 30,0))) + " months ago"
  else:
          return str(int(round(days / 365,0))) + " years ago"


def cb_callback(active):
  active1 = cbg_pages.active
  active2 = [element + 4 for element in cbg_editions.active]
  active3=[element + 10 for element in cbg_users.active]
  active4=[element + 17 for element in cbg_ratios.active]
  active = active1 + active2 + active3 + active4
  rootLayout = curdoc().get_model_by_name('graphs')
  children = rootLayout.children
  if len(active) > 0:
          for i in range(0,len(all_figures)):
                  plt = curdoc().get_model_by_name(all_figures[i].name)
                  if i in active:
                          if not plt:
                                  children.insert(0,all_figures[i])
                  else:
                          if  plt:
                                  children.remove(plt)
          for fig in children:
                  fig.x_range = children[0].x_range


def slider_callback(attr,old,new):
  banners_div.text = banners_html(new-1)
  date_div.text = '<h1 style="text-align:center">'+time[new-1]+'<h1>'
  top_users_source.data = top_users_table_ds[dates[new-1]].data
  top_pages_source.data = top_pages_ds[dates[new-1]].data
  df = users_bar_data_frames[dates[new-1]]
  users_bar = generate_users_bar(df)
  u_rootLayout = curdoc().get_model_by_name('row1')
  u_children = u_rootLayout.children
  u_plt = curdoc().get_model_by_name('Editions for users')
  if u_plt in u_children:
          u_children.remove(u_plt)
  u_children.insert(1,users_bar)
  p_rootLayout = curdoc().get_model_by_name('row2')
  p_children = p_rootLayout.children
  pages_bar = generate_pages_bar(df)
  p_plt = curdoc().get_model_by_name('Editions for pages')
  if p_plt in p_children:
          p_children.remove(p_plt)
  p_children.insert(1,pages_bar)


def clear_callback():
  rootLayout = curdoc().get_model_by_name('graphs')
  cbg_users.active = []
  cbg_pages.active = []
  cbg_editions.active = []
  cbg_ratios.active = []


# Main starts here #
databases_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'databases')
db_name = sys.argv[1] + ".sqlite"
db_path = os.path.join(databases_dir, db_name)
print(db_path)
dh.init_statistics(db_path)

wiki_id = 1
curdoc().title = dh.get_name(wiki_id)
tools="hover,pan,reset,save,box_zoom,box_select,lasso_select"

all_figures=[]
if not os.path.isfile('wiki_status_source'):
  d = dh.wiki_status(wiki_id)
  dsorted = sorted(d.items(),key = lambda x:x[0])
  darray = np.array(dsorted,dtype="object")
  dates = darray[:,0]
  editions_by_type = dh.get_editions_by_author_type(wiki_id)
  edited_pages = dh.edited_pages(wiki_id)
  classified_active_users = dh.get_classified_users(wiki_id)
  classified_active_users = sorted(classified_active_users.items(),key = lambda x:x[0])
  classified_active_users =  np.array(classified_active_users,dtype="object")
  avg_page_size = dh.get_average_page_size(wiki_id)
  avg_page_size = sorted(avg_page_size.items(),key = lambda x:x[0])
  avg_page_size = np.array(avg_page_size,dtype="object")
  monthly_edition_bytes = dh.monthly_avg_bytes(wiki_id)
  pages = [element[0][0] for element in darray[:,1]]
  editions = [element[0][1] for element in darray[:,1]]
  users = [element[0][2]+element[0][3] for element in darray[:,1]]
  anonymous = [element[0][3] for element in darray[:,1]]
  avg_edition_bytes = [element[0][4] for element in darray[:,1]]
  logged = [element[0][2] for element in darray[:,1]]
  editions_per_logged = [element[0][1]/element[0][2] for element in darray[:,1]]
  pages_per_logged = [element[0][0]/element[0][2] for element in darray[:,1]]
  editions_per_page = [element[0][1]/element[0][0] for element in darray[:,1]]
  pages_per_user = [element[0][0]/(element[0][2]+element[0][3]) for element in darray[:,1]]
  editions_per_user = [element[0][1]/(element[0][2]+element[0][3]) for element in darray[:,1]]
  edited_pages = [element[1] for element in edited_pages]
  pages_month = [el-pages[i-1] if i>0 else el for i,el in enumerate(pages)]
  editions_month = [el-editions[i-1] if i>0 else el for i,el in enumerate(editions)]
  logged_month = [el-logged[i-1] if i>0 else el for i,el in enumerate(logged)]
  users_month = [el-users[i-1] if i>0 else el for i,el in enumerate(users)]
  anonymous_month = [el-anonymous[i-1] if i>0 else el for i,el in enumerate(anonymous)]
  editions_per_edited_page = [element/edited_pages[idx] for idx,element in enumerate(editions_month)]
  time = [element.strftime("%b %Y") for element in dates]
  logged_editions = [element[1] for element in editions_by_type]
  anonymous_editions = [element[2] for element in editions_by_type]
  other_users = [element[1][2] for element in classified_active_users]
  active_users = [element[1][1] for element in classified_active_users]
  very_active_users = [element[1][0] for element in classified_active_users]
  total_active_users = [element[1][1]+element[1][2]+element[1][0] for element in classified_active_users]
  middle_active_users = [element[1][1]+element[1][0] for element in classified_active_users]
  avg_size = avg_page_size[:,1]
  monthly_edition_bytes = [element[1] for element in monthly_edition_bytes]
  data = dict(
    pages = pages,
    editions = editions,
    users = users,
    dates = dates,
    time = time,
    editions_per_logged = editions_per_logged,
    pages_per_logged = pages_per_logged,
    editions_per_page = editions_per_page,
    logged = logged,
    anonymous = anonymous,
    pages_month = pages_month,
    editions_month = editions_month,
    logged_month = logged_month,
    users_month = users_month,
    anonymous_month = anonymous_month,
    editions_per_user = editions_per_user,
    pages_per_user = pages_per_user,
    edited_pages = edited_pages,
    editions_per_edited_page = editions_per_edited_page,
    logged_editions = logged_editions,
    anonymous_editions = anonymous_editions,
    other_users = other_users,
    active_users = active_users,
    very_active_users = very_active_users,
    total_active_users = total_active_users,
    middle_active_users = middle_active_users,
    avg_size = avg_size,
    avg_edition_bytes = avg_edition_bytes,
    monthly_edition_bytes = monthly_edition_bytes
  )
  wiki_status_source = ColumnDataSource(data=data)
  output = open(os.path.join(BASE_DIR,'wiki_status_source'),'wb')
  pickle.dump(data,output,protocol = 4)
  output.close()
else:
  inp = open(os.path.join(BASE_DIR,'wiki_status_source'),'rb')
  gc.disable()
  data = pickle.load(inp)
  gc.enable()
  pages = data["pages"]
  editions = data["editions"]
  users = data["users"]
  dates = data["dates"]
  time = data["time"]
  editions_per_logged = data["editions_per_logged"]
  pages_per_logged = data["pages_per_logged"]
  editions_per_page = data["editions_per_page"]
  logged = data["logged"]
  anonymous = data["anonymous"]
  pages_month = data["pages_month"]
  editions_month = data["editions_month"]
  logged_month = data["logged_month"]
  users_month = data["users_month"]
  anonymous_month = data["anonymous_month"]
  editions_per_user = data["editions_per_user"]
  pages_per_user = data["pages_per_user"]
  edited_pages = data["edited_pages"]
  editions_per_edited_page = data["editions_per_edited_page"]
  logged_editions = data["logged_editions"]
  anonymous_editions = data["anonymous_editions"]
  other_users = data["other_users"]
  active_users = data["active_users"]
  very_active_users = data["very_active_users"]
  total_active_users = data["total_active_users"]
  middle_active_users = data["middle_active_users"]
  avg_size = data["avg_size"]
  avg_edition_bytes = data["avg_edition_bytes"]
  monthly_edition_bytes = data["monthly_edition_bytes"]
  wiki_status_source = ColumnDataSource(data=data)
  inp.close()

wiki_status_source = ColumnDataSource(
  data=dict(
    pages = pages,
    editions = editions,
    users = users,
    dates = dates,
    time = time,
    editions_per_logged = editions_per_logged,
    pages_per_logged = pages_per_logged,
    editions_per_page = editions_per_page,
    logged = logged,
    anonymous = anonymous,
    pages_month = pages_month,
    editions_month = editions_month,
    logged_month = logged_month,
    users_month = users_month,
    anonymous_month = anonymous_month,
    editions_per_user = editions_per_user,
    pages_per_user = pages_per_user,
    edited_pages = edited_pages,
    editions_per_edited_page = editions_per_edited_page,
    logged_editions = logged_editions,
    anonymous_editions = anonymous_editions,
    other_users = other_users,
    active_users = active_users,
    very_active_users = very_active_users,
    total_active_users = total_active_users,
    middle_active_users = middle_active_users,
    avg_size = avg_size,
    avg_edition_bytes = avg_edition_bytes,
    monthly_edition_bytes = monthly_edition_bytes
))

if not os.path.isfile('top_users'):
  top_users = dh.top_users(wiki_id)
  sorted_top_users = sorted(top_users.items(),key = lambda x:x[0])
  array_top_users = np.array(sorted_top_users,dtype="object")
  output = open(os.path.join(BASE_DIR,'array_top_users'),'wb')
  pickle.dump(array_top_users,output,protocol = 4)
  output.close()
  top_users_table_ds=dict()
  top_users_data=dict()
  for top_row in array_top_users:
          data = dict()
          sorted_users = sorted(top_row[1],key = lambda x:x[2],reverse = True)
          data['users'] = [element[0] for idx,element in enumerate(sorted_users) if idx < 10]
          data['creations'] = [element[1] for idx,element in enumerate(sorted_users) if idx < 10]
          data['editions'] = [element[2] for idx,element in enumerate(sorted_users) if idx < 10]
          top_users_table_ds[top_row[0]] = ColumnDataSource(data = data)
          top_users_data[top_row[0]] = data
          size = len(sorted_users)
  output = open(os.path.join(BASE_DIR,'top_users'),'wb')
  pickle.dump(top_users_data,output,protocol = 4)
  output.close()
else:
  inp = open(os.path.join(BASE_DIR,'top_users'),'rb')
  gc.disable()
  top_users_data = pickle.load(inp)
  top_users_table_ds = {}
  for element in top_users_data:
          top_users_table_ds[element] =  ColumnDataSource(data = top_users_data[element])
  inp.close()
  inp = open(os.path.join(BASE_DIR,'array_top_users'),'rb')
  array_top_users = pickle.load(inp)
  array_top_users = np.array(array_top_users,dtype="object")
  gc.enable()
  inp.close()

pages_figure = figure(title = "Total pages",name ="Total pages",y_axis_label = "Pages",height = HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
pages_figure.line('dates','pages',source=wiki_status_source,line_width=2.5,color =Paired9[3])
hover = pages_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Pages','@pages')
]

editions_figure = figure(title = "Total editions",name = "Total editions",y_axis_label = "Editions",height = HEIGHT, width =WIDTH,x_axis_type = "datetime",tools = tools)
editions_figure.line('dates','editions',source=wiki_status_source,line_width=2.5,color =Paired9[5])
hover = editions_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Editions','@editions')
]

users_figure = figure(title = "Total users",name = "Total users",y_axis_label = "Users",height = HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
users_figure.line('dates','users',source=wiki_status_source,line_width=2.5,color =Paired9[1])
hover = users_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Users','@users')
]

logged_figure = figure(title = "Total logged users",name ="Total logged users",y_axis_label = "Logged users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
logged_figure.line('dates','logged',source=wiki_status_source,line_width=2.5,color =Paired9[1])
hover = logged_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Logged Users','@logged')
]

anonymous_figure = figure(title = "Total anonymous",name ="Total anonymous users",y_axis_label = "Anonymous users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
anonymous_figure.line('dates','anonymous',source=wiki_status_source,line_width=2.5,color =Paired9[1])
hover = anonymous_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Anonymous Users','@anonymous')
]

pages_month_figure = figure(title = "Monthly new pages",name ="Monthly new pages",y_axis_label = "New pages",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
pages_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'pages_month', source= wiki_status_source,color =Paired9[2])
hover = pages_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('New pages','@pages_month')
]

editions_month_figure = figure(title = "Monthly editions",name ="Monthly editions",y_axis_label = "Monthly editions",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
editions_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'editions_month', source= wiki_status_source,color =Paired9[4])
hover = editions_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Editions','@editions_month')
]

users_month_figure = figure(title = "Monthly new users",name ="Monthly new users",y_axis_label = "New users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
users_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'users_month', source= wiki_status_source,color =Paired9[0])
hover = users_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('New users','@users_month')
]

logged_month_figure = figure(title = "Monthly new logged users",name ="Monthly new logged users",y_axis_label = "New logged users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
logged_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'logged_month', source= wiki_status_source,color =Paired9[0])
hover = logged_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('New logged users','@logged_month')
]

anonymous_month_figure = figure(title = "Monthly new anonymous users",name ="Monthly new anonymous users",y_axis_label = "New anonymous users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
anonymous_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'anonymous_month', source= wiki_status_source,color =Paired9[0])
hover = anonymous_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('New anonymous users','@anonymous_month')
]

edited_pages_figure = figure(title = "Monthly edited pages",name ="Monthly edited pages",y_axis_label = "Edited pages",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
edited_pages_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'edited_pages', source= wiki_status_source,color =Paired9[2])
hover = edited_pages_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Edited pages','@edited_pages')
]

editions_per_edited_page_figure = figure(title = "Monthly editions per edited page",name ="Monthly editions per edited page",y_axis_label = "Editions per edited page",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
editions_per_edited_page_figure.line('dates','editions_per_edited_page',source=wiki_status_source,line_width=2.5,color =Paired9[4])
hover = editions_per_edited_page_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Editions','@editions_month'),
('Edited pages','@edited_pages'),
('Editions per edited page','@editions_per_edited_page')
]

editions_by_type_figure = figure(title = "Editions by author type",name ="Editions by author type",y_axis_label = "Editions",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
editions_by_type_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'editions_month',bottom = 'anonymous_editions', source= wiki_status_source,color =Paired9[2],legend = "Editions by logged users")
editions_by_type_figure.vbar(x= 'dates',width = get_width(wiki_status_source), top='anonymous_editions',source= wiki_status_source,color =Paired9[4],legend ="Editions by anonymous users")
hover = editions_by_type_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Editions by logged users','@logged_editions'),
('Editions by anonymous users','@anonymous_editions'),
('Total editions','@editions_month')
]
editions_by_type_figure.legend.location="top_left"
users_by_type_figure = figure(title = "Active users by type",name ="Active users by type",y_axis_label = "Active users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
users_by_type_figure.vbar(x= 'dates',width = get_width(wiki_status_source), top='very_active_users',source= wiki_status_source,color =Paired9[0],legend="Very active: editions > 100")
users_by_type_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'middle_active_users',bottom = 'very_active_users', source= wiki_status_source,color =Paired9[2],legend = "Active: 100>editions>5")
users_by_type_figure.vbar(x= 'dates',width = get_width(wiki_status_source), top = 'total_active_users',bottom='middle_active_users',source= wiki_status_source,color =Paired9[4],legend= "Other: editions < 5")
hover = users_by_type_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Very active users','@very_active_users'),
('Active users','@active_users'),
('Other users','@other_users'),
('Total contributors this month','@total_active_users')
]
users_by_type_figure.legend.location="top_left"


editions_per_user_figure = figure(title = "Total editions per user",name ="Total editions per user",y_axis_label = "Total editions",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
editions_per_user_figure.line('dates','editions_per_user',source=wiki_status_source,line_width=2.5,color =Paired9[5])
hover = editions_per_user_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total editions per user','@editions_per_user')
]

pages_per_user_figure = figure(title = "Total pages per user",name ="Total pages per user",y_axis_label = "Pages per user",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
pages_per_user_figure.line('dates','pages_per_user',source=wiki_status_source,line_width=2.5,color =Paired9[3])
hover = pages_per_user_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total pages per user','@pages_per_user')
]

editions_per_page_figure = figure(title = "Total editions per page",name ="Total editions per page",y_axis_label = "Editions per page",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
editions_per_page_figure.line('dates','editions_per_page',source=wiki_status_source,line_width=2.5,color =Paired9[5])
hover = editions_per_page_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total editions_per_page','@editions_per_page')
]

avg_size_figure = figure(title = "Average page size",name ="Average page size",y_axis_label = "Bytes",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
avg_size_figure.line('dates','avg_size',source=wiki_status_source,line_width=2.5,color =Paired9[7])
hover = avg_size_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Average page size','@avg_size')
]

avg_editions_figure = figure(title = "Average edition bytes",name ="Average edition bytes",y_axis_label = "Bytes",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
avg_editions_figure.line('dates','avg_edition_bytes',source=wiki_status_source,line_width=2.5,color =Paired9[7])
hover = avg_editions_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Average edition bytes','@avg_edition_bytes')
]

monthly_edition_bytes_figure = figure(title = "Monthly average edition bytes",name ="Monthly average edition bytes",y_axis_label = "Bytes",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools = tools)
monthly_edition_bytes_figure.line('dates','monthly_edition_bytes',source=wiki_status_source,line_width=2.5,color =Paired9[7])
hover = monthly_edition_bytes_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Monthly average edition bytes','@monthly_edition_bytes')
]

all_figures.append(pages_figure)
all_figures.append(pages_month_figure)
all_figures.append(pages_per_user_figure)
all_figures.append(edited_pages_figure)

all_figures.append(editions_figure)
all_figures.append(editions_month_figure)
all_figures.append(editions_per_user_figure)
all_figures.append(editions_per_page_figure)
all_figures.append(editions_per_edited_page_figure)
all_figures.append(editions_by_type_figure)


all_figures.append(users_figure)
all_figures.append(logged_figure)
all_figures.append(anonymous_figure)
all_figures.append(users_month_figure)
all_figures.append(logged_month_figure)
all_figures.append(anonymous_month_figure)
all_figures.append(users_by_type_figure)

all_figures.append(avg_size_figure)
all_figures.append(avg_editions_figure)
all_figures.append(monthly_edition_bytes_figure)

for fig in all_figures:
        fig.x_range = all_figures[0].x_range
cbg_labels = [  "Total",
                "New",
                "Total per user",
                "Edited (monthly)",

                "Total",
                "Monthly",
                "Total per user",
                "Total per page",
                "Monthly per edited page",
                "By contributor type",

                "Total",
                "Total logged",
                "Total anonymous",
                "New",
                "New logged",
                "New anoymous",
                "Classified (monthly)",

                "Page average",
                "Edition average (total)",
                "Edition average (monthly)"]

pages_div = Div(text = '<h1 id="pages_title"> Pages <h1>', css_classes=['pages_div','panel_div'])
editions_div = Div(text = '<h1 id="editions_title"> Editions <h1>', css_classes=['editions_div','panel_div'])
users_div = Div(text = '<h1 id="users_title"> Users <h1>', css_classes=['users_div','panel_div'])
size_div = Div(text = '<h1 id="size_title"> Size <h1>', css_classes=['size_div','panel_div'])

cbg_pages = CheckboxGroup(labels=cbg_labels[0:4],active=[0], css_classes =['pages_checks'])
cbg_editions =CheckboxGroup(labels=cbg_labels[4:10],active=[0], css_classes =['edition_checks'])
cbg_users = CheckboxGroup(labels=cbg_labels[10:17],active=[], css_classes =['users_checks'])
cbg_ratios=CheckboxGroup(labels=cbg_labels[17:20],active=[], css_classes =['other_checks'])

cbg_pages.on_click(cb_callback)
cbg_editions.on_click(cb_callback)
cbg_users.on_click(cb_callback)
cbg_ratios.on_click(cb_callback)

#cbg.on_click(cb_callback)
sizing_mode = "fixed"
time_slider = Slider(start=1, end= len(dates), value= len(dates), step = 1, title = "Months from creation",width=1580)
date_div = Div(text = '<h1 style="text-align:center"> Stats until:'+time[-1]+'<h1>',width=1600)
banners_div = Div(text = banners_html(len(dates)-1),width=1600)
time_slider.on_change('value',slider_callback)


top_users_columns = [
  TableColumn(field="users",title="User"),
  TableColumn(field="editions",title="Editions"),
  TableColumn(field="creations",title="Creations")]

date = dates[-1]
top_users_table = DataTable(source = top_users_table_ds[date],
                                                        columns = top_users_columns,
                                                        width = 500,height = 300,
                                                        row_headers=False)
top_users_source = top_users_table.source


top_pages = dh.top_pages(wiki_id)
sorted_top_pages = sorted(top_pages.items(),key = lambda x:x[0])
array_top_pages = np.array(sorted_top_pages,dtype="object")
top_pages_ds=dict()
for top_row in array_top_pages:
  data = dict()
  data['page_id'] = [element[0] for element in top_row[1]]
  data['page_name'] = [element[1] for element in top_row[1]]
  data['page_creation'] = [get_creation_date(dt.strptime(element[2],'%Y-%m-%d %H:%M:%S'),top_row[0]) for element in top_row[1]]
  data['page_editions'] = [element[3] for element in top_row[1]]
  data['page_contributors'] = [element[4] for element in top_row[1]]
  top_pages_ds[top_row[0]] = ColumnDataSource(data = data)

top_pages_columns = [
  TableColumn(field="page_id",title="ID"),
  TableColumn(field="page_name", title = "Name"),
  TableColumn(field="page_editions",title="Editions"),
  TableColumn(field="page_creation",title="Creation date"),
  TableColumn(field="page_contributors",title="Contributors"),
  ]
top_users_div = Div(text='<h3 style="text-align:center"> Top Users </h3>',width = 600)
top_pages_div = Div(text='<h3 style="text-align:center"> Top Pages </h3>',width = 1000)

top_pages_table = DataTable(source = top_pages_ds[array_top_pages[-1][0]], columns = top_pages_columns,width=1000,height = 300,row_headers=False)
top_pages_source = top_pages_table.source

clear_btn = Button(label="Clear",button_type=None,css_classes=['clear'])
clear_btn.on_click(clear_callback)


edited_by_users = dh.get_edited_by_users(wiki_id)
edited_sources = {}
users_bar_data_frames = {}
for d in dates:
  users_bar_data_frames[d]=generate_editors_df(edited_by_users[d])
current_u_source = users_bar_data_frames[dates[-1]]
users_bar = generate_users_bar(current_u_source)
pages_bar = generate_pages_bar(current_u_source)

dh.end_statistics()

'''
users_bar = figure(title = "Editions for users", y_range = edited_source.data['users'],name ="Editions for users",tools = tools, width = 1000,height = 400)
users_bar.hbar(y = 'users',height = 0.3,right='editions',stacked='edited',source = edited_source)
users_bar.xgrid.grid_line_color = None
users_bar.ygrid.grid_line_color = None
hover = users_bar.select(dict(type=HoverTool))
hover.tooltips = [
('User','@users'),
('Editions this month','@editions')
]
'''
'''
ticker = SingleIntervalTicker(interval=1, num_minor_ticks=0)
xaxis = LinearAxis(ticker=ticker)
hm.add_layout(xaxis, 'below')
'''

timelines = Column(all_figures[0],all_figures[4],name = "graphs")
cbg_widgetbox = widgetbox(Div(text = "Please select the charts you wish to see..."),pages_div,cbg_pages,editions_div,cbg_editions,users_div,cbg_users,size_div,cbg_ratios,clear_btn,width = 300)
main_tab_row= row(cbg_widgetbox,timelines)
main_tab = Panel(child = main_tab_row,title="Evolution")
top_users_col = Column(top_users_div,top_users_table)
top_pages_col = Column(top_pages_div,top_pages_table)

other_row_1=row(top_users_col,users_bar,name='row1')
other_row_2=row(top_pages_col,pages_bar,name='row2')
other_layout = Column(  widgetbox(date_div),
                        widgetbox(time_slider),
                        widgetbox(banners_div),
                        other_row_1,
                        other_row_2,
                        sizing_mode = sizing_mode)
other_tab = Panel(child = other_layout, title = "Statistics")
curdoc().add_root(Tabs(tabs=[main_tab,other_tab]))
