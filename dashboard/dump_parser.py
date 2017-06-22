
import xml.etree.ElementTree as ET
import xml.parsers.expat
import sys

Debug = True

def xml_to_text(source, target = ""):
    print("Opening file: " + source )
    if target:
        target= open(target,'w',encoding = 'utf-8')
    else:
        target= open(source[0:-3]+"txt",'w',encoding = 'utf-8')
    print("Processing...")
    target.write(";".join(["page_id","page_title","page_ns","revision_id","timestamp","contributor_id","contributor_name","bytes"]))
    target.write("\n")
    for event, elem in ET.iterparse(source, events=("start", "end")):

        if event=="start" and elem.tag.split('}')[1] =="sitename":
            target.write(elem.text)
            target.write("\n")
            prefix = elem.tag.split('}')[0] + '}'

        if event =="end" and elem.tag.split('}')[1] == "page":
            page_id = elem.find(prefix+'id').text
            page_title= elem.find(prefix+'title').text.replace(";",'')
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
                target.write(";".join([page_id,page_title,page_ns,revision_id,revision_timestamp,revision_contributor_id,revision_contributor_name,revision_bytes]))
                target.write("\n")
    print("Closing file...")
    target.close()
    print("Process completed!")


def xml_to_txt(filename):
    

    ### BEGIN xmt_to_txt var declarations ###
    # Shared variables for parser subfunctions:
    ## output_txt, _current_tag, _parent
    ## page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,bytes_var
    
    output_txt = None
    _parent = None
    _current_tag = ''
    page_id = -1
    page_title = ''
    page_ns = -1
    revision_id = -1
    timestamp = ''
    contributor_id = -1
    contributor_name = ''
    bytes_var = -1
        

    def start_tag(tag, attrs):
        nonlocal output_txt, _current_tag, _parent
        nonlocal bytes_var
        
        _current_tag = tag
        
        if tag == 'text':
            bytes_var = attrs['bytes']
        elif tag == 'page' or tag == 'revision' or tag == 'contributor':
            _parent = tag

    def data_handler(data):
        nonlocal output_txt, _current_tag, _parent
        nonlocal page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name
        
        if _current_tag == '': # Don't process blank "orphan" data between tags!! 
            return
        
        if _current_tag == 'sitename':
            output_txt.write(data + '\n')
        elif _parent:
            if _parent == 'page':
                if _current_tag == 'title':
                    page_title = data
                elif _current_tag == 'id':
                    page_id = data
                elif _current_tag == 'ns':
                    page_ns = data
            elif _parent == 'revision':
                if _current_tag == 'id':
                    revision_id = data
                elif _current_tag == 'timestamp':
                    timestamp = str(data)
            elif _parent == 'contributor':
                if _current_tag == 'id':
                    contributor_id = data
                elif _current_tag == 'username':
                    contributor_name = data
                elif _current_tag == 'ip':
                    contributor_id = data
                    contributor_name = 'Anonymous'

    def end_tag(tag):
        nonlocal output_txt, _current_tag, _parent
        nonlocal page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,bytes_var
        
        # uploading one level of parent if any of these tags close
        if tag == 'page':
            _parent = None
        elif tag == 'revision':
            _parent = 'page'
        elif tag == 'contributor':
            _parent = 'revision'
        
        # print revision to revision output txt
        if tag == 'revision':
            #revision_row = list(map(str,[page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,bytes_var]))
            revision_row = [page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,bytes_var]
            output_txt.write(";".join(revision_row) + '\n')
            if Debug:
                print(";".join(revision_row) + '\n')
            # Cleaning data that has to be recalculated for hygiene and better debugging:
            revision_id = timestamp = contributor_id = contributor_name = bytes_var = ''
            
        _current_tag = '' # Very important!!! Otherwise blank "orphan" data between tags remain in _current_tag and trigger data_handler!! >:(
        

    ### BEGIN xml_to_txt body ###
        
    # Initializing xml parser
    parser = xml.parsers.expat.ParserCreate()
    input_file = open(filename, 'rb')
    
    #~ x = 0
    #~ for l in input_file:
        #~ print l
        #~ x = x +1
        #~ if x > 10:
            #~ 0/0

    parser.StartElementHandler = start_tag
    parser.EndElementHandler = end_tag
    parser.CharacterDataHandler = data_handler
    
    # writing header for output txt file
    output_txt = open(filename[0:-3]+"txt",'w')
    output_txt.write(";".join(["page_id","page_title","page_ns","revision_id","timestamp","contributor_id","contributor_name","bytes"]))
    output_txt.write("\n")

    # Parsing xml and writting proccesed data to output txt
    print("Processing...")
    parser.ParseFile(input_file)
    print("Done processing")

    input_file.close()
    output_txt.close()

    return True


if __name__ == "__main__":
    print (sys.argv)
    if(len(sys.argv)) == 2:
        print("Starting to parse file " + sys.argv[1])
        if xml_to_txt(sys.argv[1]):
            print("Data dump parsed succesfully")
    else:
        print("Error: Invalid number of arguments. Please specify a .xml file to parse")
