def str_indent(s:str, n_ident:int):
    return '\t'*n_ident+s

def str_newline(s:str, end_of_string:bool=True):
    if end_of_string:
        return s+'\n'
    else:
        return '\n'+s

def list_indent(string_list:list, n_ident:int):
    return [str_indent(s,n_ident) for s in string_list]


def list_newline(string_list:list, end_of_string:bool=True ):
    return [str_newline(s,end_of_string) for s in string_list]


def numpy_string(array):
    # convert numpy array in array of string
    return list(map(str,array))
