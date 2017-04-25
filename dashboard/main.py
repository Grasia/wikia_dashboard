from datetime import datetime as dt
from datetime import date  as d
import numpy as np 
import dataHandler as dh
from bokeh.plotting import figure, output_file,show,vplot,gridplot,ColumnDataSource,curdoc
from bokeh.models import LinearAxis, Range1d, HoverTool,CustomJS,Tabs,Panel
import pandas as pd
from bokeh.charts import Donut, Area, Bar, Scatter
from bokeh.models.widgets import Slider, Select ,DataTable, TableColumn,CheckboxGroup,Div
from bokeh.layouts import row,widgetbox,Column,layout
from six.moves import zip
from bokeh.palettes import small_palettes
from random import randint
import sys
from bokeh.charts.attributes import CatAttr
from bokeh.palettes import Paired9
from numpy import pi

WIDTH = 1300
HEIGHT = 300
NAMESPACES = {	-2:"Media",
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
def get_width(source):
    mindate = min(source.data['dates'])
    maxdate = max(source.data['dates'])
    return 0.8 * (maxdate-mindate).total_seconds()*1000 / len(source.data['dates'])
def banners_html(total_pages,total_editions,logged_users,anonymous_users):
	return '''
		<div  style ="width:23%; display :inline-block;border:1px solid blue; background-color: '''+ Paired9[1]+ ''' ; color  : white;text-align:center"> <h1>Content pages: '''+str(total_pages)+'''</h1></div>
				<div style ="width:23%;display:inline-block;background-color: '''+ Paired9[3]+ '''; color : white; text-align:center"> <h1>Editions: ''' +str(total_editions)+'''</h1></div>
				<div style ="width:23%;display:inline-block;background-color: '''+ Paired9[5]+ '''; color : white;text-align:center"> <h1> Logged users: '''+str(logged_users)+'''</h1></div>
				<div style ="width:23%;display:inline-block;background-color: '''+ Paired9[7]+ '''; color : white;text-align:center"> <h1> Anonymous users: '''+str(anonymous_users)+'''</h1></div>

'''
def banners_html_2(total_pages,total_editions,logged_users,days,active_users):
	days = 30 + days
	return '''
		<div  style ="width:23%; display :inline-block;border:1px solid blue; background-color: '''+ Paired9[2]+ ''' ; color  : white;text-align:center"> <h1>'''+str(round(total_pages/logged_users,2))+''' pages/logged user</h1></div>
				<div style ="width:23%;display:inline-block;background-color: '''+ Paired9[4]+ '''; color : white; text-align:center"> <h1>''' +str(round(total_editions/total_pages,2))+''' editions/page</h1></div>
				<div style ="width:23%;display:inline-block;background-color: '''+ Paired9[6]+ '''; color : white;text-align:center"> <h1>'''+str(round(total_editions/days,2))+''' editions/day</h1></div>
				<div style ="width:23%;display:inline-block;background-color: '''+ Paired9[8]+ '''; color : white;text-align:center"> <h1> Active users: '''+str(active_users)+'''</h1></div>

'''
def cb_callback(active):
	rootLayout = curdoc().get_model_by_name('graphs')
	children = rootLayout.children
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
	banners_div.text = banners_html(pages[new-1],editions[new-1],logged[new-1],anonymous[new-1])
	banners_div_2.text = banners_html_2(pages[new-1],editions[new-1],logged[new-1],(dates[new-1]-dates[0]).days,total_active_users[new-1])
	date_div.text = '<h1 style="text-align:center">'+time[new-1]+'<h1>'
	top_users_source.data = top_users_table_ds[dates[new-1]].data
	top_pages_source.data = top_pages_ds[dates[new-1]].data
	classified_users_source.data = classified_users_ds[dates[new-1]].data
	pages_ns_source.data = pages_ns_data_frames[dates[new-1]]




wiki_id = 1
curdoc().title = dh.get_name(wiki_id)


all_figures=[]
d= dh.wiki_status(wiki_id)
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
pages= [element[0][0] for element in darray[:,1]]
editions = [element[0][1] for element in darray[:,1]]
users = [element[0][2]+element[0][3] for element in darray[:,1]]
anonymous=[element[0][3] for element in darray[:,1]]
avg_edition_bytes = [element[0][4] for element in darray[:,1]]
logged = [element[0][2] for element in darray[:,1]]
editions_per_logged = [element[0][1]/element[0][2] for element in darray[:,1]]
pages_per_logged = [element[0][0]/element[0][2] for element in darray[:,1]]
editions_per_page = [element[0][1]/element[0][0] for element in darray[:,1]]
pages_per_user = [element[0][0]/(element[0][2]+element[0][3]) for element in darray[:,1]]
editions_per_user = [element[0][1]/(element[0][2]+element[0][3]) for element in darray[:,1]]
edited_pages = [element[1] for element in edited_pages]
pages_month = [el-pages[i-1] if i>0 else el for i,el in enumerate(pages)]
editions_month= [el-editions[i-1] if i>0 else el for i,el in enumerate(editions)]
logged_month= [el-logged[i-1] if i>0 else el for i,el in enumerate(logged)]
users_month= [el-users[i-1] if i>0 else el for i,el in enumerate(users)]
anonymous_month = [el-anonymous[i-1] if i>0 else el for i,el in enumerate(anonymous)]
editions_per_edited_page=[element/edited_pages[idx] for idx,element in enumerate(editions_month)]
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

wiki_status_source = ColumnDataSource(
		data=dict(
			pages = pages,
			editions = editions,
			users = users,
			dates = dates,
			time = time,
			editions_per_logged=editions_per_logged,
			pages_per_logged=pages_per_logged,
			editions_per_page = editions_per_page,
			logged = logged,
			anonymous = anonymous,
			pages_month = pages_month,
			editions_month = editions_month,
			logged_month=logged_month,
			users_month = users_month,
			anonymous_month	=anonymous_month,
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
pages_figure = figure(title = "Total pages",name ="Total pages",y_axis_label = "Pages",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
pages_figure.line('dates','pages',source=wiki_status_source,line_width=2.5,color =Paired9[0])
hover = pages_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Pages','@pages')
]

editions_figure = figure(title = "Total editions",name = "Total editions",y_axis_label = "Editions",height = HEIGHT, width =WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
editions_figure.line('dates','editions',source=wiki_status_source,line_width=2.5,color =Paired9[1])
hover = editions_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Editions','@editions')
]

users_figure = figure(title = "Total users",name = "Total users",y_axis_label = "Users",height = HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
users_figure.line('dates','users',source=wiki_status_source,line_width=2.5,color =Paired9[2])
hover = users_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Users','@users')
]

logged_figure = figure(title = "Total logged users",name ="Total logged users",y_axis_label = "Logged users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
logged_figure.line('dates','logged',source=wiki_status_source,line_width=2.5,color =Paired9[3])
hover = logged_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Logged Users','@logged')
]

anonymous_figure = figure(title = "Total anonymous",name ="Total anonymous users",y_axis_label = "Anonymous users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
anonymous_figure.line('dates','anonymous',source=wiki_status_source,line_width=2.5,color =Paired9[4])
hover = anonymous_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total Anonymous Users','@anonymous')
]

pages_month_figure = figure(title = "Monthly new pages",name ="Monthly new pages",y_axis_label = "New pages",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
pages_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'pages_month', source= wiki_status_source,color =Paired9[0])
hover = pages_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('New pages','@pages_month')
]

editions_month_figure = figure(title = "Monthly editions",name ="Monthly editions",y_axis_label = "Monthly editions",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
editions_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'editions_month', source= wiki_status_source,color =Paired9[1])
hover = editions_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Editions','@editions_month')
]

users_month_figure = figure(title = "Monthly new users",name ="Monthly new users",y_axis_label = "New users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
users_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'users_month', source= wiki_status_source,color =Paired9[2])
hover = users_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('New users','@users_month')
]

logged_month_figure = figure(title = "Monthly new logged users",name ="Monthly new logged users",y_axis_label = "New logged users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
logged_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'logged_month', source= wiki_status_source,color =Paired9[3])
hover = logged_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('New logged users','@logged_month')
]

anonymous_month_figure = figure(title = "Monthly new anonymous users",name ="Monthly new anonymous users",y_axis_label = "New anonymous users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
anonymous_month_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'anonymous_month', source= wiki_status_source,color =Paired9[4])
hover = anonymous_month_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('New anonymous users','@anonymous_month')
]

edited_pages_figure = figure(title = "Monthly edited pages",name ="Monthly edited pages",y_axis_label = "Edited pages",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
edited_pages_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'edited_pages', source= wiki_status_source,color =Paired9[8])
hover = edited_pages_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Edited pages','@edited_pages')
]

editions_per_edited_page_figure = figure(title = "Monthly editions per edited page",name ="Monthly editions per edited page",y_axis_label = "Editions per edited page",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
editions_per_edited_page_figure.line('dates','editions_per_edited_page',source=wiki_status_source,line_width=2.5,color =Paired9[7])
hover = editions_per_edited_page_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Editions','@editions_month'),
('Edited pages','@edited_pages'),
('Editions per edited page','@editions_per_edited_page')
]

editions_by_type_figure = figure(title = "Editions by author type",name ="Editions by author type",y_axis_label = "Editions",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
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
users_by_type_figure = figure(title = "Active users by type",name ="Active users by type",y_axis_label = "Active users",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
users_by_type_figure.vbar(x= 'dates',width = get_width(wiki_status_source), top='very_active_users',source= wiki_status_source,color =Paired9[1],legend="Very active: editions > 100")
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


editions_per_user_figure = figure(title = "Total editions per user",name ="Total editions per user",y_axis_label = "Total editions",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
editions_per_user_figure.line('dates','editions_per_user',source=wiki_status_source,line_width=2.5,color =Paired9[5])
hover = editions_per_user_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total editions per user','@editions_per_user')
]

pages_per_user_figure = figure(title = "Total pages per user",name ="Total pages per user",y_axis_label = "Pages per user",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
pages_per_user_figure.line('dates','editions_per_user',source=wiki_status_source,line_width=2.5,color =Paired9[6])
hover = pages_per_user_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total pages per user','@pages_per_user')
]

editions_per_page_figure = figure(title = "Total editions per page",name ="Total editions per page",y_axis_label = "Editions per page",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
editions_per_page_figure.line('dates','editions_per_page',source=wiki_status_source,line_width=2.5,color =Paired9[7])
hover = editions_per_page_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Total editions_per_page','@editions_per_page')
]

avg_size_figure = figure(title = "Average page size",name ="Average page size",y_axis_label = "Bytes",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
avg_size_figure.line('dates','avg_size',source=wiki_status_source,line_width=2.5,color =Paired9[0])
hover = avg_size_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Average page size','@avg_size')
]

avg_editions_figure = figure(title = "Average edition bytes",name ="Average edition bytes",y_axis_label = "Bytes",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
avg_editions_figure.line('dates','avg_edition_bytes',source=wiki_status_source,line_width=2.5,color =Paired9[4])
hover = avg_editions_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Average edition bytes','@avg_edition_bytes')
]

monthly_edition_bytes_figure = figure(title = "Monthly average edition bytes",name ="Monthly average edition bytes",y_axis_label = "Bytes",height =HEIGHT, width = WIDTH,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
monthly_edition_bytes_figure.line('dates','monthly_edition_bytes',source=wiki_status_source,line_width=2.5,color =Paired9[7])
hover = monthly_edition_bytes_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Date','@time'),
('Monthly average edition bytes','@monthly_edition_bytes')
]

all_figures.append(pages_figure)
all_figures.append(editions_figure)
all_figures.append(users_figure)
all_figures.append(logged_figure)
all_figures.append(anonymous_figure)
all_figures.append(pages_month_figure)
all_figures.append(editions_month_figure)
all_figures.append(users_month_figure)
all_figures.append(logged_month_figure)
all_figures.append(anonymous_month_figure)
all_figures.append(edited_pages_figure)
all_figures.append(pages_per_user_figure)
all_figures.append(editions_per_user_figure)
all_figures.append(editions_per_page_figure)
all_figures.append(editions_per_edited_page_figure)
all_figures.append(editions_by_type_figure)
all_figures.append(users_by_type_figure)
all_figures.append(avg_size_figure)
all_figures.append(avg_editions_figure)
all_figures.append(monthly_edition_bytes_figure)

for fig in all_figures:
	fig.x_range = all_figures[0].x_range
cbg_labels = [	"Total pages",
				"Total editions",
				"Total users",
				"Total logged users",
				"Total anonymous users",
				"Monthly new pages",
				"Monthly editions",
				"Monthly new users",
				"Monthly new logged users",
				"Monthly new anonymous users",
				"Monthly edited pages",
				"Total pages per user",
				"Total editions per user",
				"Total editions per page",
				"Monthly editions per edited page",
				"Editions by author type",
				"Active users by type",
				"Average page size",
				"Average edition bytes",
				"Monthly average edition bytes"]
cbg = CheckboxGroup(labels=cbg_labels,active=[0,1])



cbg.on_click(cb_callback)


time_slider = Slider(start=1, end= len(dates), value= len(dates), step = 1, title = "Months from creation",width=1680)
date_div = Div(text = '<h1 style="text-align:center">'+time[-1]+'<h1>',width=1700)
banners_div = Div(text = banners_html(pages[-1],editions[-1],logged[-1],anonymous[-1]),width=1700)
banners_div_2 = Div(text = banners_html_2(pages[-1],editions[-1],logged[-1],(dates[-1]-dates[0]).days,total_active_users[-1]),width=1700)
time_slider.on_change('value',slider_callback)

pages_by_ns  =  dh.ns_info(wiki_id)
data = sorted(pages_by_ns.items(), key = lambda x:x[0])
data = np.array(data, dtype = object)
ns_dates = data[:,0]
pages_ns_data_frames ={}
for date in pages_by_ns:
	pages_ns = sorted(pages_by_ns[date],key = lambda x:x[1],reverse = True)
	pages_ns_data_frames[date]={}
	pages_ns = np.array(pages_ns)
	sorted_pages = sorted(pages_ns[:,1],reverse = True)
	pages_ns_data_frames[date]['data']=list()
	for idx,element in enumerate(sorted_pages):
 		if idx <=5:
 			pages_ns_data_frames[date]['data'].append(element)
 		else:
 			pages_ns_data_frames[date]['data'][5] += element
	pages_ns_data_frames[date]['labels']= [NAMESPACES[element] for idx,element in enumerate(pages_ns[:,0]) if idx < 5]
	pages_ns_data_frames[date]['labels'].append("Other")
	total = sum(pages_ns_data_frames[date]['data'])
	pages_ns_data_frames[date]['percents'] = [(element * 100)/total for element in pages_ns_data_frames[date]['data']]
	pages_ns_data_frames[date]['percents_accumulated'] = [sum(pages_ns_data_frames[date]['percents'][:idx+1])/100 for idx,element in enumerate(pages_ns_data_frames[date]['percents'])]
	pages_ns_data_frames[date]['starts'] = [p*2*pi for p in pages_ns_data_frames[date]['percents_accumulated'][:-1]]
	pages_ns_data_frames[date]['ends'] = [p*2*pi for p in pages_ns_data_frames[date]['percents_accumulated'][1:]]
	pages_ns_data_frames[date]['ends'].insert(0,pages_ns_data_frames[date]['starts'][0])
	pages_ns_data_frames[date]['starts'].insert(0,0)
	pages_ns_data_frames[date]['colors'] =  ["red", "green", "blue", "orange", "yellow","purple"]
 

pages_ns_source = ColumnDataSource(data=pages_ns_data_frames[ns_dates[-1]])

pages_by_ns_figure = figure(title = "Pages by namespace",name ="Pages by namespace",tools="hover,pan,reset,save,wheel_zoom,box_zoom",height = 500,width = 500)
pages_by_ns_figure.wedge(x=0,y=0,radius=1,start_angle = "starts",end_angle="ends",color="colors",source=pages_ns_source)
hover = pages_by_ns_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Namespace','@labels'),
('Pages','@data')
]
pages_by_ns_figure.xaxis.visible = False
pages_by_ns_figure.yaxis.visible = False
pages_by_ns_figure.xgrid.grid_line_color = None
pages_by_ns_figure.ygrid.grid_line_color = None

top_users = dh.top_users(wiki_id)
sorted_top_users = sorted(top_users.items(),key = lambda x:x[0])
array_top_users = np.array(sorted_top_users,dtype="object")
top_users_table_ds=dict()
classified_users_ds = dict()
for top_row in array_top_users:
	data = dict()
	sorted_users = sorted(top_row[1],key = lambda x:x[2],reverse = True)
	data['users'] = [element[0] for idx,element in enumerate(sorted_users) if idx < 10]
	data['creations'] = [element[1] for idx,element in enumerate(sorted_users) if idx < 10]
	data['editions'] = [element[2] for idx,element in enumerate(sorted_users) if idx < 10]
	top_users_table_ds[top_row[0]] = ColumnDataSource(data = data)
	classified_users_data = [0,0,0]
	classified_users_size = [0,0,0]
	size = len(sorted_users)

	for idx,user in enumerate(sorted_users):
		percent = (idx+1)*100/size
		if idx <= 1:
			classified_users_data[0]+=user[2]
			classified_users_size[0]+=1

		elif idx <=10:
			classified_users_data[1]+=user[2]
			classified_users_size[1]+=1

		else:
			classified_users_data[2]+=user[2]
			classified_users_size[2]+=1
	classified_users_ds[top_row[0]] = ColumnDataSource(data=dict(
		values = classified_users_data,
		labels = ["Top 1%", "Middle 9%", "Bottom 90%"],
		color = [Paired9[1],Paired9[3],Paired9[7]],
		users = classified_users_size
		))
top_users_columns = [
			TableColumn(field="users",title="User"),
			TableColumn(field="creations",title="Creations"),
			TableColumn(field="editions",title="Editions")
	]
top_users_table = DataTable(source = top_users_table_ds[array_top_users[-1][0]], columns = top_users_columns,width = 800,height = 300)
top_users_source = top_users_table.source

classified_users_source = classified_users_ds[array_top_users[-1][0]]
classified_users_figure = figure(title = "Editions by classified users",name ="Editions by classified users",x_range = classified_users_source.data['labels'],y_axis_label = "Editions by grouped users",tools="hover,pan,reset,save,wheel_zoom,box_zoom",width=750,height = 300)
classified_users_figure.vbar(x="labels",top="values", width = 0.7, color = "color",source = classified_users_source)
hover = classified_users_figure.select(dict(type=HoverTool))
hover.tooltips = [
('Users','@users'),
('Editions','@values')
]
classified_users_figure.xgrid.grid_line_color = None


top_pages = dh.top_pages(wiki_id)
sorted_top_pages = sorted(top_pages.items(),key = lambda x:x[0])
array_top_pages = np.array(sorted_top_pages,dtype="object")
top_pages_ds=dict()
for top_row in array_top_pages:
	data = dict()
	data['page_id'] = [element[0] for element in top_row[1]]
	data['page_name'] = [element[1] for element in top_row[1]]
	data['page_creation'] = [element[2] for element in top_row[1]]
	data['page_editions'] = [element[3] for element in top_row[1]]
	data['page_contributors'] = [element[4] for element in top_row[1]]
	top_pages_ds[top_row[0]] = ColumnDataSource(data = data)


top_pages_columns = [
			TableColumn(field="page_id",title="ID"),
			TableColumn(field="page_name", title = "Name"),
			TableColumn(field="page_creation",title="Creation date"),
			TableColumn(field="page_editions",title="Editions"),
			TableColumn(field="page_contributors",title="Contributors"),
	]
top_pages_table = DataTable(source = top_pages_ds[array_top_pages[-1][0]], columns = top_pages_columns,width=1000,height = 300)
top_pages_source = top_pages_table.source














timelines = Column(all_figures[0],all_figures[1],name = "graphs")
main_tab_row = row(timelines,widgetbox(cbg))
main_tab = Panel(child = main_tab_row,title="Evolution")

other_row_1=row(top_users_table,classified_users_figure)
other_row_2=row(pages_by_ns_figure,top_pages_table)
other_layout = Column(	widgetbox(date_div),
						widgetbox(time_slider),
						widgetbox(banners_div),
						widgetbox(banners_div_2),
						other_row_1,
  						other_row_2)
other_tab = Panel(child = other_layout, title = "Snapshot")
curdoc().add_root(Tabs(tabs =[main_tab,other_tab]))



# dh.reset_db()
# wiki_id = dh.load_data("eszelda_pages_full.txt")
# print(wiki_id)
# dashboard(wiki_id)

# if __name__ == "__main__":
# 	if(sys.argv):
		
# 		dh.reset_db()
# 		wiki_id = dh.load_data(sys.argv[1])
# 		print(wiki_id)
# 		dashboard(wiki_id)
