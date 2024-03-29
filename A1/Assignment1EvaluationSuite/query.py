import sqlparse
import sys
import re
import table

class Q:
  def __init__(self, query):
    while query[-1] in [' ', ';']:
      query = query[:-1]
    # query = query.lower()
    self.query = query
    self.columns = []
    self.allColumns = False
    self.tables = []
    self.where = False
    self.twoWhere = False
    self.joinPresent = False
    self.andConditions = []
    self.orConditions = []
    self.tempConditions = []
    self.aggFn = []
    self.aggCol = []
    # self.keywords = ['select', 'from', 'where', 'distinct', 'sum', 'avg', 'max', 'min', 'and', 'or']
    # self.aggKeywords = ['max', 'min', 'sum', 'avg', 'distinct']
    self.stmt = None
    # To check consistency
    self.DB = table.initializeTables()
    try:
      parsed = sqlparse.parse(query)
    except:
      print 'Parse error occurred.'
      sys.exit(0)
    self.stmt = parsed[0]
    self.checkQuery()
    self.parseQuery()
    self.checkParsedQuery()
    # Check if table is present in DB
    self.improveQuery()
    # Also improve query such as do tablename.colname, remove asterix and do tablename.colname for all

  def improveQuery(self):
    self.improveSelect()
    self.improveWhere()

  def improveSelect(self):
    for index, col in enumerate(self.columns):
      colReal = col
      colFn = ''
      if col == '*':
        continue

      if col.find('(') != -1:
        colFn = col[:col.find('(')]
        colReal = col[col.find('(')+1:col.find(')')]

      if not self.checkColsPresentUnique([colReal], self.tables):
        print 'Ambigous or absent columns in select clause'
        sys.exit(0)
      if colFn:
        self.columns[index] = colFn + '(' + self.appTblName(self.colInTable(colReal), colReal) + ')'
      else:
        self.columns[index] = self.appTblName(self.colInTable(colReal), colReal)

  def improveWhere(self):
    if not self.where:
      return
    
    pickCond = ''
    if len(self.andConditions) > 0:
      pickCond = self.andConditions
    elif len(self.orConditions) > 0:
      pickCond = self.orConditions

    # If only one where condition
    if not self.checkColsPresentUnique([pickCond[0][0], pickCond[0][2]], self.tables):
      print 'Ambigous or absent columns in where clause'
      sys.exit(0)
    if not is_number(pickCond[0][0]):
      pickCond[0][0] = self.appTblName(self.colInTable(pickCond[0][0]), pickCond[0][0])
    if not is_number(pickCond[0][2]):
      pickCond[0][2] = self.appTblName(self.colInTable(pickCond[0][2]), pickCond[0][2])

    if self.twoWhere:
      if not self.checkColsPresentUnique([pickCond[1][0], pickCond[1][2]], self.tables):
        print 'Ambigous or absent columns in where clause'
        sys.exit(0)
      if not is_number(pickCond[1][0]):
        pickCond[1][0] = self.appTblName(self.colInTable(pickCond[1][0]), pickCond[1][0])
      if not is_number(pickCond[1][2]):
        pickCond[1][2] = self.appTblName(self.colInTable(pickCond[1][2]), pickCond[1][2])


  def colInTable(self, colName):
    # returns tablename for colName
    for table in self.tables:
      if colName in self.DB[table].header or colName in self.DB[table].headerWthTblName:
        return table
    print 'Some error occurred in colInTable() method'
    sys.exit(0)

  def tablesPresent(self):
    if len(self.tables) == 0:
      return False
    for table in self.tables:
      if table not in self.DB:
        return False
    return True

  def checkColsPresentUnique(self, checkCols, tables):
    # Checks if checkCols[] are present in the loaded tables
    colMap = {}
    for col in checkCols:
      if is_number(col):
        continue
      # if col == '*':
      #   continue
      colMap[col] = 0
    for col in colMap:
      for table in tables:
        if col in self.DB[table].header or col in self.DB[table].headerWthTblName:
          colMap[col] += 1
    # print colMap
    for col in colMap:
      if colMap[col] != 1:
        return False
    return True


  def appTblName(self, tableName, dest):
    if dest.find('.') == -1:
      dest = tableName + '.' + dest
    return dest

  def checkParsedQuery(self):
    if not self.tablesPresent():
      print 'Table not present'
      sys.exit(0)

  def checkQuery(self):

    if self.stmt.token_first().value != 'select':
      print 'Invalid sql'
      sys.exit(0)

    if not self.checkValidWhitespace():
      print 'Invalid sql'
      sys.exit(0)

  def checkValidWhitespace(self):
      for i in range(0, len(self.stmt.tokens)):
        if i%2:
          # print self.stmt.tokens[i] 
          if self.stmt.tokens[i] == ';':
            continue
          if not (self.stmt.tokens[i].is_whitespace()):
            print 'Invalid sql'
            return False
      return True

  def parseQuery(self):
    # print len(self.stmt.tokens)
    if len(self.stmt.tokens) < 7:
      print 'Invalid sql'
      sys.exit(0)
    self.parseSelect(self.stmt.tokens[2])
    if len(self.stmt.tokens) < 7:
      print 'Invalid sql'
      sys.exit(0)
    self.parseFrom(self.stmt.tokens[6])
    if len(self.stmt.tokens) > 7 and self.stmt.tokens[7].value != ';':
      self.where = True
      self.parseWhere(self.stmt.tokens[8])
      self.processTempConditions()

  def parseSelect(self, item):
    # print 'item: ', item
    if item.value == '*' and item.ttype == sqlparse.tokens.Token.Wildcard:
      self.allColumns = True
      self.columns.append('*')
      return
    if item.ttype == sqlparse.tokens.Token.Punctuation:
      return
    if item.ttype == sqlparse.tokens.Token.Text.Whitespace:
      return
    if len(item.tokens) == 1:
      self.columns.append(item.value)
      return
    if len(item.tokens) == 2:
      # print item.to_unicode()
      self.columns.append(item.to_unicode())
      # print item.tokens[0].to_unicode()
      self.aggFn.append(item.tokens[0].to_unicode())
      # print item.tokens[1].to_unicode()[1:-1]
      self.aggCol.append(item.tokens[1].to_unicode()[1:-1])
      return
    if len(item.tokens) == 3:
      if (item.tokens[0].ttype == sqlparse.tokens.Token.Name and item.tokens[1].value == '.' and
          item.tokens[2].ttype == sqlparse.tokens.Token.Name):
        self.columns.append(item.to_unicode())
        return

    for t in item.tokens:
      self.parseSelect(t)

  def parseFrom(self, item):
    # print 'item: ', item
    if item.ttype == sqlparse.tokens.Token.Punctuation:
      return
    if item.ttype == sqlparse.tokens.Token.Text.Whitespace:
      return
    if item.ttype == sqlparse.tokens.Token.Keyword:
      return
    if len(item.tokens) == 1:
      self.tables.append(item.value)
      return

    for t in item.tokens:
      self.parseFrom(t)

  def parseWhere(self, item):
    # print 'item: ', item, item.value
    if item.ttype == sqlparse.tokens.Token.Punctuation:
      return
    if item.ttype == sqlparse.tokens.Token.Text.Whitespace:
      return
    if item.value == 'where' and item.ttype == sqlparse.tokens.Token.Keyword:
      return
    if item.value in ['and', 'or', 'AND', 'OR'] and item.ttype == sqlparse.tokens.Token.Keyword:
      self.tempConditions.append(item.value)
      return
    if item.ttype == sqlparse.tokens.Token.Operator.Comparison:
      self.tempConditions.append(item.value)
      return
    if item.ttype == sqlparse.tokens.Token.Literal.Number.Integer:
      self.tempConditions.append(item.value)
      return

    if len(item.tokens) == 3:
      if (item.tokens[0].ttype == sqlparse.tokens.Token.Name and item.tokens[1].value == '.' and
          item.tokens[2].ttype == sqlparse.tokens.Token.Name):
        self.tempConditions.append(item.to_unicode())
        return

    if len(item.tokens) == 1:
      self.tempConditions.append(item.value)
      return

    for t in item.tokens:
      # print 'herere'
      self.parseWhere(t)

  def processTempConditions(self):
    # Process tempConditions
    # print self.tempConditions
    if len(self.tempConditions) not in [3, 7]:
      # No need to exit
      self.where = False
      # return
      print 'Invalid where conditions'
      sys.exit(0)
    andOr = False
    if len(self.tempConditions) > 3:
      andOr = self.tempConditions[3]
      self.twoWhere = True
      if andOr.lower() == 'and':
        self.andConditions.append([self.tempConditions[0], self.tempConditions[1], self.tempConditions[2]])
        self.andConditions.append([self.tempConditions[4], self.tempConditions[5], self.tempConditions[6]])
      elif andOr.lower() == 'or':
        self.orConditions.append([self.tempConditions[0], self.tempConditions[1], self.tempConditions[2]])
        self.orConditions.append([self.tempConditions[4], self.tempConditions[5], self.tempConditions[6]])
    else:
      self.andConditions.append([self.tempConditions[0], self.tempConditions[1], self.tempConditions[2]])
    # print andOr

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    pass

  try:
    import unicodedata
    unicodedata.numeric(s)
    return True
  except (TypeError, ValueError):
    pass
  return False

def main():
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
      q = Q(i)
      print q.__dict__
    except SystemExit as e:
      print 'sys.exit called'
      pass
  # q = Q(sql[-2])
  # print q.query, q.__dict__

  # q.parseQuery()
  pass

if __name__ == '__main__':
  main()