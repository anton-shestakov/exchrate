import pymssql


def connect_db(servername, userid, password, dbname):

    return pymssql.connect(server=servername, user=userid, password=password
                           ,database=dbname)

def execute_query(conn, sql):

    cursor = conn.cursor()
    cursor.execute(sql)
    ret_value = []
    for row in cursor:
        ret_value.append(row)
    conn.commit()
    return ret_value

def execute_proc(conn, proc_name, params):
    
    cursor = conn.cursor()
    cursor.callproc(proc_name, params)
    ret_value = []
    for row in cursor:
        ret_value.append(row)
    conn.commit()
    return ret_value

def execute_proc_return_value(conn, proc_name, params):

    cursor = conn.cursor()
    output = cursor.callproc(proc_name, params)
    conn.commit()
    out = []
    out_params = (i for i, p in enumerate(params) if isinstance(p, pymssql.output)) # only output parameters will be returned
    for param in out_params:
        out.append(output[param])
    return out

def output_param(param_type):
	return pymssql.output(param_type)


