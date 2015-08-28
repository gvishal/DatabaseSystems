import csv
import glob
import sys
import copy

metadataFile = 'metadata.txt'
DB = {}

Row = []
# class Row:

#   def __init__(self, value=[]):
#     if type(value) != list:
#       print 'Invalid row type, should be list got: ', type(value)
#       sys.exit(0)
#     self.value = value

#   def __repr__(self):
#     return ' '.join(self.value)

#   def append(self, value):
#     self.value.append(value)

class Table:

  def __init__(self, filename = None, name=''):
    self.header = []
    self.headerWthTblName = []
    self.rows = []
    self.name = name

    if filename != None:
      self.name = filename.split('.')[0]

      self.header, self.headerWthTblName = extractMetadata(metadataFile , self.name)

      with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for r in reader:
          self.rows.append(r)

  def __str__(self):
    return self.name + ' contains: ' +  ' '.join(self.header)

  def __repr__(self):
    return self.__str__()

  def addHeader(self, v):
    self.header.append(v)
    self.headerWthTblName.append(v)

  def addRow(self, r):
    self.rows.append(r)

  def copyTable(self, newTable):
    # newTable = Table(name=newTableName)
    newTable.header = copy.deepcopy(self.header)
    newTable.rows = copy.deepcopy(self.rows)
    # return newTable

  def crossProduct(self, firstTable, secondTable):
    for h in firstTable.headerWthTblName:
      self.addHeader(h)
    for h in secondTable.headerWthTblName:
      self.addHeader(h)
    for r1 in firstTable.rows:
      for r2 in secondTable.rows:
        self.addRow(r1 + r2)

def listCSV():
  csvFiles = []
  for file in glob.glob('*.csv'):
    csvFiles.append(file)
  return csvFiles

def extractMetadata(filename, tablename):
  begin = '<begin_table>'
  end = '<end_table>'
  start = False
  tableHeaders = []
  tableHeadersWithTableName = []
  try:
    with open(filename, 'r') as f:
      for line in f.readlines():
        line = line.rstrip()
        if start and line == end:
          return tableHeaders, tableHeadersWithTableName
        if line == tablename:
          start = True
        elif start:
          tableHeaders.append(line)
          tableHeadersWithTableName.append(tablename + '.' + line)
  except IOError as e:
    print e
  return [], []

def initializeTables():
  DB = {}
  csvFiles = listCSV()
  for fileName in csvFiles:
    tableName = fileName.split('.')[0]
    DB[tableName] = Table(fileName)
  return DB

def main():
  DB = initializeTables()
  print DB['table1'].__dict__


if __name__ == '__main__':
    main()