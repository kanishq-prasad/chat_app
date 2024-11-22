from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:Kanishq1210%40MySQL@127.0.0.1/chatapp')
connection = engine.connect()
print("Connection successful!")
connection.close()