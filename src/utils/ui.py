import sys

def force_query_yes_or_no(): 
    yes = {'yes','y', 'ye', ''}
    no = {'no','n'}

    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")
        return force_query_yes_or_no()