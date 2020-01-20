# vivochallenge
Vivo Challenge - The Bot API

1 - Run the DDL to create the tables in a mySql database
2 - Change the connection string in views.py lines 27, 28 e 29.
      27 - user, password = 'root', '123456'
      28 - host = 'localhost'
      29 - dbase = 'vivochallenge'
      30 - app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{0}:{1}@{2}/{3}'.format(user, password, host, dbase)
      31 - db = SQLAlchemy(app)
3 - Be happy!
