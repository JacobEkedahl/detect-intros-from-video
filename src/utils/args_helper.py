# Returns a value after key1 or key2 where key to should be a abbreviation of key1. Example: k1="-input" and k2="-i"
def get_value_after_key(argv, key1, key2):
    if key2 == "":
        key2 = key1 
    for i in range(1, len(argv)):
        if (argv[i] == key1 or argv[i] == key2) and i + 1 < len(argv):
            return argv[i + 1]
    return ""

# Returns true if a key is present inside the argument list
def is_key_present(argv, key):
    for i in range(1, len(argv)):    
        if (argv[i] == key):
            return True 
    return False 

# Returns true if any [key] is present inside the argument list 
def is_any_key_present(argv, keys):
    for i in range(1, len(argv)):
        for key in keys: 
            if (argv[i] == key):
                return True 
    return False 
