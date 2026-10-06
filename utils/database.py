import psycopg2




class DatabaseUtils:
    def __init__(self,db_config):
        self.db_config = db_config


        
        try:
            self.connection = psycopg2.connect(**db_config)


        except Exception as e:
            print(f"error conecting to the database : {e}")
            self.connection = None

    def schema_details(self,schema_name): 

        """ Schema ---> Tables -----> columns ----> dummy data """
        if not self.connection :
            return "No database connection available"



        schema_info_context = ""

        connection = self.connection
        cursor = connection.cursor()

        schema_info_context = f"Schema:{schema_name}\n"



        cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{schema_name}'")


        table_list=cursor.fetchall()    


        schema_info_context += f"Tables:{table_list}\n"

        for table in table_list:
            table_name = table[0] # only the names

            schema_info_context = f"{schema_info_context}\n Table : {table_name}\n"

            # ADDING COLUMNS AND DATA TYPES
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'")
            columns = cursor.fetchall()
            for column in columns:
                column_name = column[0]
                data_type = column[1]
            schema_info_context = f"{schema_info_context} Column : {column_name} , Type : {data_type}\n"
    




            
            


if __name__ == "__main__":
    db_config = {
        "host" : "localhost",
        "port" : "5432",
        "user" : "postgres",
        "password" : "1234",
        "database" : "postgres"}
    db = DatabaseUtils(db_config)
    print(db.schema_details("public"))
        



        
  
  