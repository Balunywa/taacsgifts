import urllib.parse

params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};SERVER=devwe.database.windows.net;DATABASE=DevMixitLife;UID=balunlu;PWD=Luq#123450;Connection Timeout=60")
conn_str = 'mssql+pyodbc:///?odbc_connect={}'.format(params)
