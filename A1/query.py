import sqlparse
import sys
import re

class Q:
  def __init__(self, query):
    self.columns = []
    self.allColumns = False
    self.tables = []
    self.andConditions = []
    self.orConditions = []
    self.tempConditions = []
    self.aggFn = []
    self.aggCol = []
    self.keywords = ['select', 'from', 'where', 'distinct', 'sum', 'avg', 'max', 'min', 'and', 'or']
    self.aggKeywords = ['max', 'min', 'sum', 'avg', 'distinct']
    self.stmt = None
    try:
      parsed = sqlparse.parse(query)
    except:
      print 'Parse error occurred.'
      sys.exit(0)
    self.stmt = parsed[0]
    self.parseQuery()

  def checkQuery(self):
    if self.stmt.token_first().value != 'select':
      print 'Invalid sql'
      sys.exit(0)

    checkValidWhitespace()

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
    if len(self.stmt.tokens) > 6:
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
    print 'item: ', item
    if item.ttype == sqlparse.tokens.Token.Punctuation:
      return
    if item.ttype == sqlparse.tokens.Token.Text.Whitespace:
      return
    if item.value == 'where' and item.ttype == sqlparse.tokens.Token.Keyword:
      return
    if item.value == 'and' and item.ttype == sqlparse.tokens.Token.Keyword:
      self.tempConditions.append(item.value)
      return
    if item.ttype == sqlparse.tokens.Token.Operator.Comparison:
      self.tempConditions.append(item.value)
      return
    if item.ttype == sqlparse.tokens.Token.Literal.Number.Integer:
      self.tempConditions.append(item.value)
      return

    if len(item.tokens) == 1:
      self.tempConditions.append(item.value)
      return

    for t in item.tokens:
      self.parseWhere(t)

  def processTempConditions(self):
    # Process tempConditions
    if len(self.tempConditions) > 3:
      andOr = self.tempConditions[3]

    # print andOr
    if andOr == 'and':
      self.andConditions.append([self.tempConditions[0], self.tempConditions[1], self.tempConditions[2]])
      self.andConditions.append([self.tempConditions[4], self.tempConditions[5], self.tempConditions[6]])
    else:
      self.orConditions.append([self.tempConditions[0], self.tempConditions[1], self.tempConditions[2]])
      self.orConditions.append([self.tempConditions[4], self.tempConditions[5], self.tempConditions[6]])

def main():
  sql = 'select max(col1), distinct(col2), col3, * from foo, bar where col1 >= col2 and col2 <= 20;'
  sql1 = 'select * from foo, bar where foo.col1 = bar.col2;'
  q = Q(sql)
  print q.__dict__
  # q.parseQuery()
  pass

if __name__ == '__main__':
  main()