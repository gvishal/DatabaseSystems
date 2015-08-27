import csv
import glob
import sys

metadataFile = 'metadata.txt'
DB = {}

class Row:

  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return ' '.join(self.value)

class Table:

  def __init__(self, filename):
    self.header = None
    self.rows = []
    self.name = filename.split('.')[0]

    self.header = extractMetadata(metadataFile , self.name).value

    with open(filename, 'r') as csvfile:
      reader = csv.reader(csvfile, delimiter=',')
      for r in reader:
        self.rows.append(Row(r))

  def __str__(self):
    return self.name + ' contains: ' +  ' '.join(self.header)

  def __repr__(self):
    return self.__str__()

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
  try:
    with open(filename, 'r') as f:
      for line in f.readlines():
        line = line.rstrip()
        if start and line == end:
          return Row(tableHeaders)
        if line == tablename:
          start = True
        elif start:
          tableHeaders.append(line)
  except IOError as e:
    print e
  return Row([])

def initializeTables():
  DB = {}
  csvFiles = listCSV()
  for fileName in csvFiles:
    tableName = fileName.split('.')[0]
    DB[tableName] = Table(fileName)
  return DB

def main():
  DB = initializeTables()
  print DB['table1'].header


if __name__ == '__main__':
    main()