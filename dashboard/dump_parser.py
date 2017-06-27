#!/usr/bin/python3
# -*- coding: utf-8 -*-

import xml.parsers.expat
import sys

Debug = False


def has_empty_field(l):
  field_empty = False;
  i = 0
  while (not field_empty and i<len(l)):
    field_empty = (l[i] == '');
    i = i + 1
  return field_empty


def xml_to_txt(filename):

  ### BEGIN xmt_to_txt var declarations ###
  # Shared variables for parser subfunctions:
  ## output_txt, _current_tag, _parent
  ## page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,bytes_var

  output_txt = None
  _parent = None
  _current_tag = ''
  page_id = page_title = page_ns = revision_id = timestamp = contributor_id = contributor_name = bytes_var = ''
  site_name = None
  
  def start_tag(tag, attrs):
    nonlocal output_txt, _current_tag, _parent
    nonlocal bytes_var

    _current_tag = tag

    if tag == 'text':
      if 'bytes' in attrs:
        bytes_var = attrs['bytes']
      else: # There's a 'deleted' flag or no info about bytes of the edition
        bytes_var = '-1'
    elif tag == 'page' or tag == 'revision' or tag == 'contributor':
      _parent = tag
    
    if tag == 'upload':
      print("!! Warning: '<upload>' element not being handled", file=sys.stderr)

  def data_handler(data):
    nonlocal output_txt, _current_tag, _parent
    nonlocal page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name
    nonlocal site_name

    if _current_tag == '': # Don't process blank "orphan" data between tags!!
      return

    if site_name == None and _current_tag == 'sitename':
      site_name = data
      output_txt.write(data + '\n')
    elif _parent:
      if _parent == 'page':
        if _current_tag == 'title':
          page_title = '|' + data + '|'
        elif _current_tag == 'id':
          page_id = data
          if Debug:
            print("Parsing page " + page_id )
        elif _current_tag == 'ns':
          page_ns = data
      elif _parent == 'revision':
        if _current_tag == 'id':
          revision_id = data
        elif _current_tag == 'timestamp':
          timestamp = data
      elif _parent == 'contributor':
        if _current_tag == 'id':
          contributor_id = data
        elif _current_tag == 'username':
          contributor_name = '|' + data + '|'
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

    # print revision to revision output csv
    if tag == 'revision':
      
      revision_row = [page_id,page_title,page_ns,revision_id,timestamp,contributor_id,contributor_name,bytes_var]
      
      # Do not print (skip) revisions that has any of the fields not available
      if not has_empty_field(revision_row):
        output_txt.write(";".join(revision_row) + '\n')
      else:
        print("The following line has imcomplete info and therefore it's been removed from the dataset:")
        print(revision_row)
      
      # Debug lines to standard output
      if Debug:
        print(";".join(revision_row))
      
      # Clearing data that has to be recalculated for every row:
      revision_id = timestamp = contributor_id = contributor_name = bytes_var = ''

    _current_tag = '' # Very important!!! Otherwise blank "orphan" data between tags remain in _current_tag and trigger data_handler!! >:(


  ### BEGIN xml_to_txt body ###

  # Initializing xml parser
  parser = xml.parsers.expat.ParserCreate()
  input_file = open(filename, 'rb')

  parser.StartElementHandler = start_tag
  parser.EndElementHandler = end_tag
  parser.CharacterDataHandler = data_handler
  parser.buffer_text = True
  parser.buffer_size = 1024

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
