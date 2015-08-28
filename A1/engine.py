import sqlparse
import table
import query
import sys

tableName = 'new-table'

class process:

  def __init__(self, procSql, DB):
    self.processFrom(procSql, DB)
    self.processWhere(procSql, DB)
    self.processSelect(procSql, DB)
    self.printNewTable(procSql, DB)

  def processFrom(self, procSql, DB):
    newTable = DB['new-table']
    if len(procSql.tables) == 1:
      DB[procSql.tables[0]].copyTable(newTable)
    if len(procSql.tables) == 2:
      # Take cross product
      newTable.crossProduct(DB[procSql.tables[0]], DB[procSql.tables[1]])
    # print newTable.header
    # print DB['new-table'].__dict__

  def processWhere(self, procSql, DB):
    if not procSql.where:
      print 'No where conditions'
      return

  def processSelect(self, procSql, DB):
    if len(procSql.columns) == 1 and procSql.allColumns:
      return
    output = []

  def printNewTable(self, procSql, DB):
    


def main():
  # print sys.argv
  if len(sys.argv) == 1:
    print 'Please enter a sql statement'
    sys.exit(0)
  sql = sys.argv[1]
  procSql = query.Q(sql)
  DB = table.initializeTables()
  DB['new-table'] = table.Table(name='new-table')
  # print DB
  pr = process(procSql, DB)



if __name__ == '__main__':
	main()