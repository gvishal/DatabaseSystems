    select = stmt.tokens[0]
    selectStart = False
    fromStart = False
    whereStart = False
    for item in stmt.tokens:
      if item.value == 'select' and item.ttype == sqlparse.tokens.Token.Keyword.DML:
        selectStart = True
      elif item.value == 'from' and item.ttype == sqlparse.tokens.Token.Keyword:
        fromStart = True 
      elif item.value[0:4] == 'where':
        whereStart = True

      if selectStart and not fromStart :
        if item.value == ' ' and item.ttype == sqlparse.tokens.Token.Text.Whitespace:
          continue
        elif item.value == '*' and item.ttype == sqlparse.tokens.Token.Wildcard:
          self.allColumns = True
          self.columns.append('*')
        elif len(item.tokens) == 1:
          self.columns.append(item.value)
        elif len(item.tokens) > 1:
          items = item.tokens