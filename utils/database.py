import psycopg2




class DatabaseUtils:
    def __init__(self,db_config):
        self.db_config = db_config


        
        try:
            self.connection = psycopg2.connect(**db_config)


        except Exception as e:
            print(f"error conecting to the database : {e}")
            self.connection = None

    def schema_details(self,schema_name="public",sample_limit=5): 

        """ Schema ---> Tables -----> columns ----> dummy data """
        if not self.connection :
            return "No database connection available"



        schema_info_context = ""
        cursor = None
        try:

            connection = self.connection
            cursor = connection.cursor()

            schema_info_context = f"Schema: {schema_name}\n" + "=" * 40 + "\n"



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
                    schema_info_context += f" Column : {column_name} , Type : {data_type}\n"
                # ADDING SAMPLE DATA
                cursor.execute(f"SELECT * FROM {table_name} LIMIT {sample_limit};")
                sample_data = cursor.fetchall()
                schema_info_context += " Sample Data:\n"
                for row in sample_data:
                    schema_info_context += f"  {row}\n"
            return schema_info_context

        except Exception as e:
            print(f"Error fetching schema details: {e}")
            return f"Error: {e}"

        finally:
            if cursor:
                cursor.close()


    




            
            


if __name__ == "__main__":
    db_config = {
        "host" : "localhost",
        "port" : "5432",
        "user" : "postgres",
        "password" : "1234",
        "database" : "postgres"}
    db = DatabaseUtils(db_config)
    print(db.schema_details("public"))
    with open(  "context_info.txt" , "w" ) as file:
        file.write(db.schema_details("public"))       
        



        
  
  