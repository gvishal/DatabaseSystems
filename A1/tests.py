import engine
import sys

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
  sqlSelected = ['select * from table1',
                  'select * from table2',
                  'select * from table1,table2',
                  'select* from table1',
                  'select*from table1',
                  'select* fromtable1',
                  'select sum(A) from table1',
                  'select sum(A) from table1, table2',
                  'select sum(B) from table1, table2',
                  'select avg(A) from table1',
                  'select min(A) from table',
                  'select max(A) from table1',
                  'select min(A) from table1',
                  'select distinct(A) from table1',
                  'select distinct(B) from table1, table2',
                  'select distinct(table1.B) from table1, table2',
                  'select A,B from table1',
                  'select A, table2.B from table1, table2',
                  'select distinct(A), B from table1',
                  'select distinct(table2.B), table2.B from table1, table2',
                  'select * from table1 where A = 922',
                  'select A from table1 where B = 158',
                  'select A from table1, table2 where B = 158',
                  'select A from table1, table2 where table2.B = 158',
                  'select A from table1, table2 where B = 158 and C = 5727',
                  'select A from table1, table2 where table2.B = 158 and C = 5727',
                  'select A from table1, table2 where B = 158 or C = 5727'                

                ]
  tests = sqlSelected
  totalTests = len(tests)
  testsFail = []
  testsExit = []
  for i in tests:
    print 
    try:
      print i
      q = query.Q(i)
      # print q.__dict__
      DB = table.initializeTables()
      DB['new-table'] = table.Table(name='new-table')
      pr = process(q, DB)
    except SystemExit as e:
      testsExit.append(i)
      print 'sys.exit called'
      pass
    # except:
    #   print sys.exc_type, sys.exc_value, sys.exc_traceback.__dict__
    #   testsFail.append(i)
  print
  print 'Total Tests: ', totalTests
  print 'Tests Pass:', totalTests - len(testsFail)
  print
  print 'Tests Exited:', len(testsExit)
  print '\n'.join([i for i in testsExit])
  print
  print 'Tests Fail:', len(testsFail)
  print '\n'.join([i for i in testsFail])
  