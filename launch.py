#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
   launch.py

   Descp: Command-line launcher of the wiki dashboard

   Created on: 30-jun-2017

   Copyright 2017 Abel 'Akronix' Serrano Juste <akronix5@gmail.com>
"""

import sys
import os
import subprocess
import fcntl

if not os.path.isfile('ports'):
  open('ports', 'a').close()

def read_used_ports(ports_f):
  ports = ports_f.readlines()
  return [int(port) for port in ports]


def main():
    # Loading databases available in databases/
  databases_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard/databases')

  if len(sys.argv) < 2:
    print("Please specify a database to load from:")
    # Listing all files ending in .sqlite in the databases dir
    db_list = os.listdir(databases_dir)
    for f in db_list:
      if f[-7:] == ".sqlite":
        print('\t- ' + f[:-7])
    sys.exit(0)

  db_name = sys.argv[1]
  db_path = os.path.join(databases_dir, db_name + ".sqlite")

  if not os.path.isfile(db_path):
    print(db_name + ' not found in databases directory' , file=sys.stderr)
    sys.exit(1)

  ports_f = open('ports', mode='r')

  used_ports = read_used_ports(ports_f)
  ports_f.close()

  #~ print(used_ports)

  nport = 8000
  while nport in used_ports:
    nport = nport + 1

  #~ print (nport)

  ports_f = open('ports', mode='a')
  ports_f.write(str(nport) + '\n')

  fcntl.flock(ports_f, fcntl.LOCK_UN)
  ports_f.close()

  port = '--port=' + str(nport)
  args = '--args=' + db_name
  cmd = ['bokeh', 'serve', '--show', 'dashboard', port, args]
  #~ print(cmd)
  bokeh_prc = subprocess.run(cmd)

  if (bokeh_prc.returncode == 1):
    ports_f = open('ports',mode='a')
    ports_f.write(str(nport) + '\n')
    ports_f.close()

  return 0

if __name__ == '__main__':
  main()

