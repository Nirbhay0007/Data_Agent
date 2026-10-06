import psycopg2

connection = psycopg2.connect(
    host="localhost",
    port=5432,
    user="postgres",
    password="1234",
    database="postgres"
)


cursor = connection.cursor()
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
print(cursor.fetchall()) 




cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users'")
columns = cursor.fetchall()
for column in columns:
    column_name = column[0]
    data_type = column[1]
    schema_info_context = f" Column : {column_name} , Type : {data_type}\n"

cursor.execute(f"SELECT * FROM users LIMIT 5;")

data= cursor.fetchall()
for row in data:
    print(row)

print(data[0][0])
