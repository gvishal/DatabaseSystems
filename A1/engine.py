'''
Will work even for 'select * from table1 where x=','select * from table1 where x=2 and y=2'
 i.e partial where clauses.
'''

import sqlparse
import table
import query
import sys
import operator as op

newTableName = 'new-table'

class process:

  def __init__(self, procSql, DB):
    self.ops = {'<': op.lt, '<=': op.le, '=': op.eq, '!=': op.ne, '>': op.gt, '>=': op.ge}
    self.colPrint = []
    self.processFrom(procSql, DB)
    self.processWhere(procSql, DB)
    self.processSelect(procSql, DB)
    self.printNewTable(procSql, DB)

  def processFrom(self, procSql, DB):
    newTable = DB['new-table']
    if len(procSql.tables) == 1:
      newTable.copyTable(DB[procSql.tables[0]])
    if len(procSql.tables) == 2:
      # Take cross product
      newTable.crossProduct(DB[procSql.tables[0]], DB[procSql.tables[1]])
    # print newTable.header
    # print DB['new-table'].__dict__

  def processWhere(self, procSql, DB):
    if not procSql.where or len(procSql.tempConditions) is 0:
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
      # print hd
      for row in DB[newTableName].rows:
        if ( (self.ops[op1](row[hd.index(col1)], col2 if query.is_number(col2) else row[hd.index(col2)])) ):
          newRows.append(row)
      DB[newTableName].rows = newRows

  def processSelect(self, procSql, DB):
    if len(procSql.columns) == 1 and procSql.allColumns:
      self.colPrint = DB[newTableName].headerWthTblName
      # print self.colPrint
      return
    for col in procSql.columns:
      self.colPrint.append(col)
      if col.find('(') != -1:
        DB[newTableName].headerWthTblName.append(col)
        # Need to add additional cols in every row for given fn
        colFn = col[ :col.find('(')]
        col = col[col.find('(')+1:col.find(')')]
        colIdx = DB[newTableName].headerWthTblName.index(col)
        
        if colFn == 'max':
          maxCol = -1111111111
          for col in DB[newTableName].columns[colIdx]:
            maxCol = col if col > maxCol else maxCol
          DB[newTableName].rows[0].append(maxCol)
        elif colFn == 'min':
          minCol = 1111111111
          for col in DB[newTableName].columns[colIdx]:
            minCol = col if int(col) < minCol else minCol
          DB[newTableName].rows[0].append(minCol)
        elif colFn == 'sum':
          sumCol = 0
          for col in DB[newTableName].columns[colIdx]:
            sumCol += int(col)
          DB[newTableName].rows[0].append(sumCol)
        elif colFn == 'avg':
          avgCol = 0
          ln = len(DB[newTableName].columns[colIdx])
          for col in DB[newTableName].columns[colIdx]:
            avgCol += int(col)
          DB[newTableName].rows[0].append(avgCol/ln)
        elif colFn == 'distinct':
          distinctCols = []
          for col in DB[newTableName].columns[colIdx]:
            if col in distinctCols:
              continue
            else:
              distinctCols.append(col)
          for index, d in enumerate(distinctCols):
            DB[newTableName].rows[index].append(d)
    

  def printNewTable(self, procSql, DB):
    col_width = max(len(word) for word in self.colPrint) + 2

    print "".join(word.ljust(col_width) for word in self.colPrint)
    hd = DB[newTableName].headerWthTblName
    for row in DB[newTableName].rows:
      words = []
      if len(row) < len(hd):
        break
      for index, word in enumerate(row):
        for col in self.colPrint:
          if index == hd.index(col):
            words.append(word)
      print "".join(str(word).ljust(col_width) for word in words)

def test():
  sql = ['select max(col1), distinct(col2), col3, * from foo, bar where col1 >= col2 and col2 <= 20;',
          'select * from foo, bar where foo.col1 = bar.col2;',
          'select max(col1),min(col2),col3 from foo,bar where col1>=col2 or col2<=30;',
          'select max(col1),col2 from foo',
          'select * from table1 where A = 10;',
          'select * from table1, table2 where A = 10;',
          'select * from table1 where D = 20',
          'select * from table3 where A = 10',
          'select * from table1, table2 where A = 10 and E = 20',
          'select * from table1, table2 where E = 20',
          'select * from table1, table2 where B = 10',
          'select * from table1, table2 where table1.A = 10 and table1.B = 20',
          'select * from table1 where ',
          'select * from table1 where x=2 and y=2',
          'select * from table1 where x=2 and y=',
          'select * from table1 where x=2',
          'select A from table1',
          'select A,B from table1, table2',
          'select A,table2.B from table1, table2', #Need to make select parser accept table2.B type queries
          'select max(A) from table1'
          ]
  for i in sql:
    print 
    try:
      print i
      q = query.Q(i)
      print q.__dict__
      DB = table.initializeTables()
      DB['new-table'] = table.Table(name='new-table')
      pr = process(q, DB)
    except SystemExit as e:
      print 'sys.exit called'
      pass

def main():
  # print sys.argv
  if len(sys.argv) == 1:
    print 'Please enter a sql statement'
    sys.exit(0)
  
  if sys.argv[1] == 'test':
    test()
    sys.exit(0)

  sql = sys.argv[1]
  # print 'Youre sql is:', sql
  procSql = query.Q(sql)
  print procSql.__dict__
  DB = table.initializeTables()
  DB['new-table'] = table.Table(name='new-table')
  # print DB
  pr = process(procSql, DB)

if __name__ == '__main__':
	main()