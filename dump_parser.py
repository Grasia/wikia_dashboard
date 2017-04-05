
import xml.etree.ElementTree as ET
import sys

def xml_to_text(source,target = ""):
	print("Opening file: " + source )
	if target:
		target= open(target,'w',encoding = 'utf-8')
	else:
		target= open(source[0:-3]+"txt",'w',encoding = 'utf-8')
	print("Processing...")
	target.write(";".join(["page_id","page_ns","revision_id","timestamp","contributor_id","contributor_name","bytes"]))
	target.write("\n")
	for event, elem in ET.iterparse(source, events=("start", "end")):

		if event=="start" and elem.tag.split('}')[1] =="sitename":
			print(elem.text)
			prefix = elem.tag.split('}')[0] + '}'

		if event =="end" and elem.tag.split('}')[1] == "page":
			page_id = elem.find(prefix+'id').text
			page_ns = elem.find(prefix+'ns').text
			print("Parsing page " + page_id )
			for revision in elem.findall(prefix+'revision'):
				revision_id = revision.find(prefix+'id').text
				revision_timestamp = revision.find(prefix+'timestamp').text
		
				revision_bytes = (revision.find(prefix+'text').get('bytes') if revision.find(prefix+'text').get('deleted') != 'deleted' else '-1')
				contributor = revision.find(prefix+'contributor')
				if contributor.find(prefix+'id') != None:		
					revision_contributor_id = contributor.find(prefix+'id').text
					revision_contributor_name = contributor.find(prefix+'username').text.replace(";",'')
				else:
					revision_contributor_id = (contributor.find(prefix+'ip').text if contributor.find(prefix+'ip') != None else 'null')
					revision_contributor_name = ('Anonymous' if contributor.find(prefix+'ip') != None else 'null')
				target.write(";".join([page_id,page_ns,revision_id,revision_timestamp,revision_contributor_id,revision_contributor_name,revision_bytes]))
				target.write("\n")
	print("Closing file...")
	target.close()
	print("Process completed!")

if __name__ == "__main__":
	if(sys.argv):
		print("Parsing file " + sys.argv[1])
		xml_to_text(sys.argv[1])