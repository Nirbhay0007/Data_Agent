from urllib3 import response
import os
import requests
import pandas





class ETLTools:


    def __init__(self):
        pass



    def extract_load(self,url:str, output_folder:str,format:str ):


        """
        This tool extracts the data from the API url and load 
        it into the desired loaction

        Args:
            url (str): The URL from which to extract the data
            data_path (str): The path to the location where the data should be loaded
            
        Returns:
            str: The path to the location where the data was loaded
        """


       

        project_root = os.path. abspath(os.path. join(os.path.dirname(_file_), ' .. '))
        output_folder = os.path. join(project_root, output_folder)

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()



            filename = os.path.join(output_folder, f"extracted_data.{format}")

            os.makedirs(output_folder, exist_ok=True)


            df = pd.json_normalize(data)
            
            if format == "csv":
                df.to_csv(filename,index=False)
            elif format == "json":
                df.to_json(filename,indent=4)
            elif format == "parquet":
                df.to_parquet(filename,index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
                

            return f"data extracted successfully and loaded to {filename}"


        except Exception as e:
            return f"Error extracting data: {e}"

            
                