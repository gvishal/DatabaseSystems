import sqlparse
import table
import query
import sys
import operator as op

newTableName = 'new-table'

class process:

  def __init__(self, procSql, DB):
    self.ops = {'<': op.lt, '<=': op.le, '=': op.eq, '!=': op.ne, '>': op.gt, '>=': op.ge}
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
      # No where to go!
      print 'No where conditions'
      return

    if procSql.twoWhere:
      # Two conditionals
      pickCond = ''
      if len(procSql.andConditions) > 0:
        pickCond = procSql.andConditions
      elif len(procSql.orConditions) > 0:
        pickCond = procSql.orConditions

      newRows = []
      col1 = pickCond[0][0]
      col2 = pickCond[0][2]
      col3 = pickCond[1][0]
      col4 = pickCond[1][2]
      op1 = pickCond[0][1]
      op2 = pickCond[1][1]
      hd = DB[newTableName].headerWthTblName
      for row in DB[newTableName].rows:
        if ( (self.ops[op1](row[hd.index(col1)], col2 if query.is_number(col2) else row[hd.index(col2)])) and
              (self.ops[op2](row[hd.index(col3)], col4 if query.is_number(col4) else row[hd.index(col4)])) ):
          newRows.append(row)
      DB[newTableName].rows = newRows
    else:
      # Only one conditional, present in andConditions
      pickCond = procSql.andConditions
      newRows = []
      col1 = pickCond[0][0]
      col2 = pickCond[0][2]
      op1 = pickCond[0][1]
      hd = DB[newTableName].headerWthTblName
      for row in DB[newTableName].rows:
        if ( (self.ops[op1](row[hd.index(col1)], col2 if query.is_number(col2) else row[hd.index(col2)])) ):
          newRows.append(row)
      DB[newTableName].rows = newRows

  def processSelect(self, procSql, DB):
    if len(procSql.columns) == 1 and procSql.allColumns:
      return
    output = []

  def printNewTable(self, procSql, DB):
    col_width = max(len(word) for word in DB[newTableName].headerWthTblName) + 2

    print "".join(word.ljust(col_width) for word in DB[newTableName].headerWthTblName)

    for row in DB[newTableName].rows:
      print "".join(word.ljust(col_width) for word in row)


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