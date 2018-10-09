
names=[{'id' : 1,'name':'Olya',},
      {'id' : 2,'name':'Masha',},
      {'id' : 3,'name':'Katya',},
      {'id' : 4,'name':'Sasha',},
      {'id' : 5,'name':'Dasha'}]


courses=[{'id':1,'name':'Course1'},
        {'id':2,'name':'Course2'}]

def get_names():
    return names

def get_name_by_id(id):
    n=[name['name'] for name in names if name['id'] == id]
    if n:
        return n[0]

def get_courses():
    return courses

def get_course_by_id(id):
    n=[name['name'] for name in names if name['id'] == id]
    if n:
        return n[0]
