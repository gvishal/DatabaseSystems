import sqlparse
import sys
import re
import table

class Q:
  def __init__(self, query):
    self.query = query
    self.columns = []
    self.allColumns = False
    self.tables = []
    self.where = False
    self.twoWhere = False
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
    self.parseQuery()
    self.checkQuery()
    # Check if table is present in DB
    self.improveQuery()
    # Also improve query such as do tablename.colname, remove asterix and do tablename.colname for all

  def improveQuery(self):
    if len(self.tables) == 1:
      if not self.allColumns:
        for index,col in enumerate(self.columns):
          self.columns[index] = self.tables[0] + '.' + col
          print 'In improveQuery: '
          print col, self.columns[index]
    self.improveWhere()

  def improveWhere(self):
    if not self.where:
      return
    
    if not self.checkColsPresentUnique([self.andConditions[0][0], self.andConditions[0][2]], self.tables):
      print 'Ambigous or absent columns in where clause'
      sys.exit(0)
    if not is_number(self.andConditions[0][0]):
      self.andConditions[0][0] = self.appTblName(colInTable(self.andConditions[0][0]), self.andConditions[0][0])
    if not is_number(self.andConditions[0][2]):
      self.andConditions[0][2] = self.appTblName(colInTable(self.andConditions[0][2]), self.andConditions[0][2])

    if self.twoWhere:
      if not self.checkColsPresentUnique([self.andConditions[1][0], self.andConditions[1][2]], self.tables):
        print 'Ambigous or absent columns in where clause'
        sys.exit(0)
      if not is_number(self.andConditions[1][0]):
        self.andConditions[1][0] = self.appTblName(colInTable(self.andConditions[1][0]), self.andConditions[1][0])
      if not is_number(self.andConditions[1][2]):
        self.andConditions[1][2] = self.appTblName(colInTable(self.andConditions[1][2]), self.andConditions[1][2])


  def colInTable(self, colName):
    # returns tablename for colName
    for table in self.tables:
      if colName in self.DB[table].header or col in self.DB[table].headerWthTblName:
        return table
    print 'Some error occurred in colInTable() method'
    sys.exit(0)

  def tablesPresent(self):
    for table in self.tables:
      if table not in self.DB:
        return False
    return True

  def checkColsPresentUnique(self, checkCols, tables):
    # Checks if checkCols are present in the loaded tables
    colMap = {}
    for col in checkCols:
      if is_number(col):
        continue
      colMap[col] = 0
    for col in colMap:
      for table in tables:
        if col in self.DB[table].header or col in self.DB[table].headerWthTblName:
          colMap[col] += 1
    print colMap
    for col in colMap:
      if colMap[col] != 1:
        return False
    return True


  def appTblName(self, tableName, dest):
    if dest.find('.') == -1:
      dest = tableName + '.' + dest
    return dest

  def checkQuery(self):
    if self.stmt.token_first().value != 'select':
      print 'Invalid sql'
      sys.exit(0)

    if not self.checkValidWhitespace():
      print 'Invalid sql'
      sys.exit(0)

    if not self.tablesPresent():
      print 'Table not present'
      sys.exit(0)

    print 'Sql valid'

  def checkValidWhitespace(self):
      for i in range(0, len(self.stmt.tokens)):
        if i%2:
          if not (self.stmt.tokens[i].is_whitespace()):
            print 'Invalid sql'
            return False
      return True

  def parseQuery(self):
    self.parseSelect(self.stmt.tokens[2])
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

    for t in item.tokens:
      self.parseSelect(t)

  def parseFrom(self, item):
    # print 'item: ', item
    if item.ttype == sqlparse.tokens.Token.Punctuation:
      return
    if item.ttype == sqlparse.tokens.Token.Text.Whitespace:
      return
    if len(item.tokens) == 1:
      self.tables.append(item.value)
      return

    for t in item.tokens:
      self.parseFrom(t)

  def parseWhere(self, item):
    # print 'item: ', item
    if item.ttype == sqlparse.tokens.Token.Punctuation:
      return
    if item.ttype == sqlparse.tokens.Token.Text.Whitespace:
      return
    if item.value == 'where' and item.ttype == sqlparse.tokens.Token.Keyword:
      return
    if item.value in ['and', 'or'] and item.ttype == sqlparse.tokens.Token.Keyword:
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
      self.parseWhere(t)

  def processTempConditions(self):
    # Process tempConditions
    andOr = False
    if len(self.tempConditions) > 3:
      andOr = self.tempConditions[3]
      self.twoWhere = True
      if andOr == 'and':
        self.andConditions.append([self.tempConditions[0], self.tempConditions[1], self.tempConditions[2]])
        self.andConditions.append([self.tempConditions[4], self.tempConditions[5], self.tempConditions[6]])
      elif andOr == 'or':
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
          'select * from table3 where A = 10'
          ]

  # for i in sql:
  #   q = Q(i)
  #   print q.query, q.__dict__
  q = Q(sql[-2])
  print q.query, q.__dict__
  # q.parseQuery()
  pass

if __name__ == '__main__':
  main()