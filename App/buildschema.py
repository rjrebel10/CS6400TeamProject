import pymysql.cursors

def run_sql_schema(FILE,HOST,ADMIN_USER,ADMIN_PASSWORD):
    error_str=''
    try:
        conn = pymysql.connect(host=HOST,
                             user=ADMIN_USER,
                             password=ADMIN_PASSWORD)
        cursor = conn.cursor()
        
        sql_fd = open(FILE, 'r')
        sql_file = sql_fd.read()
        sql_cmds = sql_file.split(';')
        
        for command in sql_cmds:
            try:
                if command.strip() != '':
                    command = command +';'
                    print(command)
                    cursor.execute(command)
            except Exception as err:
                error_str += "\nFailed inserting: {} {}".format(err,command)
                print(error_str)

        conn.commit()
        sql_fd.close()
        cursor.close()
        conn.close()
        
    except Exception as err:
        print("Failed connecting to database: {}".format(err))
    return error_str

if __name__ == "__main__":
    
    FILE='team06_p3_schema.txt'
    HOST='127.0.0.1'
    ADMIN_USER='admin'
    ADMIN_PASSWORD='password'
    error_str=run_sql_schema(FILE,HOST,ADMIN_USER,ADMIN_PASSWORD)
