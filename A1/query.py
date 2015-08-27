import sqlparse
import sys

class Q:
  def __init__(self, query):
    self.columns = []
    self.tables = []
    self.conditions = []
    self.agg = []
    self.parseQuery(query)

  def parseQuery(self, query):
    try:
      parsed = sqlparse.parse(query)
    except:
      print 'Parse error occurred.'
      sys.exit(0)
    stmt = parsed[0]
    print stmt.tokens


def main():
  sql = 'select max(col1) from foo where col1 = 10 and col2 = 20;'
  q = Q(sql)
  pass

if __name__ == '__main__':
  main()