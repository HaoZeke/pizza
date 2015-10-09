# Pizza.py toolkit, www.cs.sandia.gov/~sjplimp/pizza.html
# Steve Plimpton, sjplimp@sandia.gov, Sandia National Laboratories
#
# Copyright (2005) Sandia Corporation.  Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains
# certain rights in this software.  This software is distributed under 
# the GNU General Public License.

# vtk tool

oneline = "Convert LAMMPS snapshots to VTK format"

docstr = """
v = vtk(d)	        d = object containing atom coords (dump, data)

v.one()                 write all snapshots to tmp.vtk
v.one("new")            write all snapshots to new.vtk
v.many()                write snapshots to tmp0000.vtk, tmp0001.vtk, etc
v.many("new")           write snapshots to new0000.vtk, new0001.vtk, etc
v.single(N)             write snapshot for timestep N to tmp.vtk 
v.single(N,"file")      write snapshot for timestep N to file.vtk

  surfaces in snapshot will be written to SURF1.vtk, SURF2.vtk, etc
    where each surface (triangle type) is in a different file
"""

# History
#   8/05, Steve Plimpton (SNL): original version

# ToDo list

# Variables
#   data = data file to read from

# Imports and external programs

import sys

# Class definition

class vtk:
  
  # --------------------------------------------------------------------

  def __init__(self,data):
    self.data = data
  
  # --------------------------------------------------------------------

  def one(self,*args):
    if len(args) == 0: file = "tmp.vtk"
    elif args[0][-4:] == ".vtk": file = args[0]
    else: file = args[0] + ".vtk"

    n = flag = 0
    which,time,flag = self.data.iterator(flag)
    time,box,atoms,bonds,tris,lines = self.data.viz(which)
    print time,
    sys.stdout.flush()

    if len(tris): surface(tris)
    
    allatoms = []
    for atom in atoms:
      allatoms.append(atom)
    
    while 1:
      which,time,flag = self.data.iterator(flag)
      if flag == -1: break
      time,box,atoms,bonds,tris,lines = self.data.viz(which)
      
      for atom in atoms: allatoms.append(atom)
      print time,
      sys.stdout.flush()
      n += 1

    particle(file,allatoms)
    print "\nwrote %d snapshots to %s in VTK format" % (n,file)

  # --------------------------------------------------------------------

  def many(self,*args):
    if len(args) == 0: root = "tmp"
    else: root = args[0]

    surfflag = 0
    n = flag = 0
    while 1:
      which,time,flag = self.data.iterator(flag)
      if flag == -1: break
      time,box,atoms,bonds,tris,lines = self.data.viz(which)

      if surfflag == 0 and len(tris):
        surfflag = 1
        surface(tris)
        
      if n < 10:
        file = root + "000" + str(n) + ".vtk"
      elif n < 100:
        file = root + "00" + str(n) + ".vtk"
      elif n < 1000:
        file = root + "0" + str(n) + ".vtk"
      else:
        file = root + str(n) + ".vtk"

      particle(file,atoms)
      
      print time,
      sys.stdout.flush()
      n += 1
      
    print "\nwrote %s snapshots in VTK format" % n

  # --------------------------------------------------------------------

  def single(self,time,*args):
    if len(args) == 0: file = "tmp.vtk"
    elif args[0][-4:] == ".vtk": file = args[0]
    else: file = args[0] + ".vtk"

    which = self.data.findtime(time)
    time,box,atoms,bonds,tris,lines = self.data.viz(which)
    if len(tris): surface(tris)
    particle(file,atoms)

# --------------------------------------------------------------------
# write list of triangles into VTK surface files: SURF1.vtk, SURF2.vtk, ...
# all triangles of one type constitute 1 surface = 1 file
# create list of unique vertices (via dictionary) from triangle list

def surface(tris):
  ntypes = tris[-1][1]
  
  for i in xrange(ntypes):
    itype = i+1
    v = {}
    nvert = ntri = 0
    for tri in tris:
      if tri[1] == itype:
        ntri += 1
        vert = (tri[2],tri[3],tri[4])
        if not v.has_key(vert):
          v[vert] = nvert
          nvert += 1
        vert = (tri[5],tri[6],tri[7])
        if not v.has_key(vert):
          v[vert] = nvert
          nvert += 1
        vert = (tri[8],tri[9],tri[10])
        if not v.has_key(vert):
          v[vert] = nvert
          nvert += 1

    keys = v.keys()
    vinverse = {}
    for key in keys:
      vinverse[v[key]] = key
      
    filename = "SURF" + str(itype) + ".vtk"
    f = open(filename,"w")
  
    print >>f,"# vtk DataFile Version 3.0"
    print >>f,"Generated by pizza.py"
    print >>f,"ASCII"
    print >>f,"DATASET POLYDATA"
    print >>f,"POINTS %d float" % nvert
    for i in xrange(nvert):
      tuple = vinverse[i]
      print >>f,tuple[0],tuple[1],tuple[2]
    print >>f,"POLYGONS",ntri,4*ntri
    for tri in tris:
      if tri[1] == itype:
        vert = (tri[2],tri[3],tri[4])
        ivert1 = v[vert]
        vert = (tri[5],tri[6],tri[7])
        ivert2 = v[vert]
        vert = (tri[8],tri[9],tri[10])
        ivert3 = v[vert]
        print >>f,3,ivert1,ivert2,ivert3
    print >>f
    print >>f,"CELL_DATA",ntri
    print >>f,"POINT_DATA",nvert

    f.close()

# --------------------------------------------------------------------
# write atoms from one snapshot into file in VTK format

def particle(file,atoms):
  f = open(file,"w")
  
  print >>f,"# vtk DataFile Version 2.0"
  print >>f,"Generated by pizza.py"
  print >>f,"ASCII"
  print >>f,"DATASET POLYDATA"
  print >>f,"POINTS %d float" % len(atoms)
  for atom in atoms:
    print >>f,atom[2],atom[3],atom[4]
  print >>f,"VERTICES",len(atoms),2*len(atoms)
  for i in xrange(len(atoms)):
    print >>f,1,i
  print >>f,"POINT_DATA",len(atoms)
  print >>f,"SCALARS atom_type int 1"
  print >>f,"LOOKUP_TABLE default"
  for atom in atoms:
    itype = int(atom[1])
    print >>f,itype,
  print >>f
  
  f.close()