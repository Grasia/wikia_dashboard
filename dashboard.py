from datetime import datetime as dt
from datetime import date  as d
import numpy as np 
import dataHandler as dh
from bokeh.plotting import figure, output_file,show,vplot,gridplot,ColumnDataSource
from bokeh.models import LinearAxis, Range1d, HoverTool,CustomJS,Tabs,Panel
import pandas as pd
from bokeh.charts import Donut, Area, Bar, Scatter
from bokeh.models.widgets import Slider, Select ,DataTable, TableColumn
from bokeh.layouts import row,widgetbox,Column
from six.moves import zip
from bokeh.palettes import small_palettes
from random import randint
import sys
from bokeh.charts.attributes import CatAttr


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
def dashboard(wiki_id):
	d= dh.wiki_status(wiki_id)
	dsorted = sorted(d.items(),key = lambda x:x[0])
	darray = np.array(dsorted,dtype="object")
	dates = [dt.strptime(element,"%Y-%m-%d") for element in darray[:,0]]
	pages= [element[0][0] for element in darray[:,1]]
	editions = [element[0][1] for element in darray[:,1]]
	users = [element[0][2]+element[0][3] for element in darray[:,1]]
	logged = [element[0][2] for element in darray[:,1]]
	editions_per_logged = [element[0][1]/element[0][2] for element in darray[:,1]]
	pages_per_logged = [element[0][0]/element[0][2] for element in darray[:,1]]
	editions_per_page = [element[0][1]/element[0][0] for element in darray[:,1]]
	wiki_status_source = ColumnDataSource(
			data=dict(
				pages = pages,
				editions = editions,
				users = users,
				dates = dates,
				time = darray[:,0],
				editions_per_logged=editions_per_logged,
				pages_per_logged=pages_per_logged,
				editions_per_page = editions_per_page,
				)
		)
	pages_figure = figure(title = "Total pages",height = 300, width = 1000,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
	pages_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'pages', source= wiki_status_source,color="Green")
	hover = pages_figure.select(dict(type=HoverTool))
	hover.tooltips = [
	('Date','@time'),
	('Total Pages','@pages')
	]

	editions_figure = figure(title = "Total editions",height = 300, width =500,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
	editions_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'editions', source= wiki_status_source)
	hover = editions_figure.select(dict(type=HoverTool))
	hover.tooltips = [
	('Date','@time'),
	('Total Editions','@editions')
	]

	users_figure = figure(title = "Total users",height = 300, width = 500,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
	users_figure.vbar(x= 'dates',width = get_width(wiki_status_source),top = 'users', source= wiki_status_source,color="Red")
	hover = users_figure.select(dict(type=HoverTool))
	hover.tooltips = [
	('Date','@time'),
	('Total Users','@users')
	]


	editions_figure.x_range = pages_figure.x_range
	users_figure.x_range = pages_figure.x_range


	row1 = row(users_figure,editions_figure,width = 1000)
	col1 = Column(row1,pages_figure)
	main_tab = Panel(child = col1,title="Index")


	data = dh.get_classified_users(wiki_id)
	df={}
	df['values']=[]
	df['stack'] = []
	df['labels']=[]
	for element in data.items():
		df['values'].append(element[1][0])
		df['stack'].append("Very Active")
		df['labels'].append(element[0])
		df['values'].append(element[1][1])
		df['stack'].append("Active")
		df['labels'].append(element[0])
		df['values'].append(element[1][2])
		df['stack'].append("Other")
		df['labels'].append(element[0])
	p = Bar(df,height = 300, width = 700,values='values',label='labels',stack='stack',tools="pan,reset,save,wheel_zoom,box_zoom",xscale="datetime",ylabel = "Users",xlabel = "Date")
	

	top_users = dh.top_users(wiki_id)
	sorted_top = sorted(top_users,key = lambda x:x[2], reverse = True)
	array_top = np.array(sorted_top,dtype="object")
	user_names = array_top[:,0]
	user_creations = array_top[:,1]
	user_editions = array_top[:,2]

	top_users_source = ColumnDataSource(data = dict(
		users = user_names,
		creations = user_creations,
		editions = user_editions


			))
	columns = [
			TableColumn(field="users",title="User"),
			TableColumn(field="creations",title="Creations"),
			TableColumn(field="editions",title="Editions")
	]
	users_table = widgetbox(DataTable(height = 300,source = top_users_source, columns = columns,width = 700))

	user_ratios = figure(width = 1400, height= 300,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
	user_ratios.line(x="dates",y='editions_per_logged',source = wiki_status_source, color = "DarkGreen",legend="Editions per logged user",line_width=4)
	user_ratios.line(x='dates',y='pages_per_logged',source = wiki_status_source,color="Red",legend="Pages per logged user",line_width=4)
	hover = user_ratios.select(dict(type=HoverTool))
	hover.tooltips = [
	('Date','@time'),
	('Editions per loged user','@editions_per_logged'),
	('Pages per loged user','@pages_per_logged')

	]

	users_tab = Panel(child = gridplot([p,users_table],[user_ratios]),title="Users")







	top_pages = dh.top_pages(wiki_id)
	sorted_top = sorted(top_pages,key = lambda x:x[1], reverse = True)
	array_top = np.array(sorted_top,dtype="object")
	page_id = array_top[:,0]
	page_editions = array_top[:,1]
	page_contributors = array_top[:,2]
	page_creation = array_top[:,3]
	top_pages_source = ColumnDataSource(data = dict(
			page_id = page_id,
			page_editions = page_editions,
			page_contributors = page_contributors,
			page_creation= page_creation

			))
	columns = [
			TableColumn(field="page_id",title="Page ID"),
			TableColumn(field="page_creation",title="Creation date"),
			TableColumn(field="page_editions",title="Editions"),
			TableColumn(field="page_contributors",title="Contributors")

	]
	pages_table = widgetbox(DataTable(height = 300,source = top_pages_source, columns = columns,width = 400))



	data = dh.get_classified_pages(wiki_id)
	df = {}
	df['values'] = data
	df['color']=['Green','Red','Blue','GoldenRod']
	df['legend'] = ["Editions>1000","1000>editions>100","100>editions>10","10>editions"]
	classified_pages = Bar(df,xscale="categorical",values = 'values', label=CatAttr(columns=['legend'], sort=False), ylabel = "Pages", color = 'color',legend=None,width =500,height=300, title =dh.get_name(wiki_id))


	d= dh.ns_info(wiki_id)
	dsorted = sorted(d.items(),key = lambda x:x[0])
	darray = np.array(dsorted,dtype="object")
	dates = darray[:,0]
	ns = {}
	namespace={}
	pages={}
	editions={}
	editions_per_page={}
	users ={}
	logged = {}
	anonymous = {}
	sources = {}
	cont = 1
	all_colors = {}
	colors = {}
	all_ns = np.array(sorted(darray[-1][1]),dtype="object")[:,0]
	min_color =0x0 
	max_color = 0xFFFFFF
	interval = int((max_color - min_color)/len(all_ns))
	for idx,element in enumerate(all_ns):
		all_colors[element]= str("#%06x" % (min_color+idx*interval))
	for date,elements in darray:
		elements = np.array(elements,dtype="object")
		ns[date] =[str(element) for element in elements[:,0]]
		namespace[date] = [NAMESPACES[element] if element in NAMESPACES else element for element in elements[:,0]]
		pages[date]= elements[:,1]
		editions[date] = elements[:,2]
		editions_per_page[date] = elements[:,2] / elements[:,1]
		users[date] = elements[:,3]
		logged[date] = elements[:,4]
		anonymous[date] = elements[:,5]
		colors[date] = [all_colors[element[0]] for element in elements]
		sources['source'+str(cont)] = ColumnDataSource(
			data=dict(
				values = editions[date],
				label = ns[date],
				editions = editions[date],
				ns = ns[date],
				pages = pages[date],
				editions_per_page = editions_per_page[date],
				users = users[date],
				logged = logged[date],
				anonymous = anonymous[date],
				color = colors[date],
				namespace=namespace[date]
				)
		)
		cont = cont+1
	sources["current"] = sources["source" + str(len(sources)-1)]
	pages_by_ns = figure(width=1400,height=300,title="Pages by namespace",x_range = sources["current"].data['label'],tools="hover,pan,reset,save,wheel_zoom,box_zoom")
	pages_by_ns.vbar('label',0.5,'values', source= sources["current"],color='color')
	hover = pages_by_ns.select(dict(type=HoverTool))
	hover.tooltips = [
	('Namespace','@namespace'),
	('Pages','@pages'),

	]

	pages_ratios = figure(width = 400, height= 300,x_axis_type = "datetime",tools="hover,pan,reset,save,wheel_zoom,box_zoom")
	pages_ratios.line(x="dates",y='editions_per_page',source = wiki_status_source, color = "DarkGreen",line_width=4)
	hover = pages_ratios.select(dict(type=HoverTool))
	hover.tooltips = [
	('Date','@time'),
	('Editions per page','@editions_per_page'),

	]



	pages_tab = Panel(child = gridplot([classified_pages,pages_ratios,pages_table],[pages_by_ns]),title="Pages")


	'''	editions_tab = Panel(child=figures[5],title="Editions")
	pages_tab = Panel(child=figures[5],title="Pages")'''
	output_file("Dashboard.html", title="Dashboard")
	show(Tabs(tabs = [main_tab,users_tab,pages_tab]))

'''
dh.reset_db()
wiki_id = dh.load_data("eszelda_pages_full.txt")
print(wiki_id)
dashboard(wiki_id)
'''
if __name__ == "__main__":
	if(sys.argv):
		
		dh.reset_db()
		wiki_id = dh.load_data(sys.argv[1])
		print(wiki_id)
		dashboard(wiki_id)
