
import os
import pickle
import threading


# to initialize all the required resources
def init():
    global maxMetaDataSize, metaData, stored_data_structure, voids, pwd, metas, lock

    maxMetaDataSize = 2 ** 10

    # to load directory structure
    if os.path.exists('samp.data'):
        stored_data_structure = open('samp.data', 'rb+')
        metaData = pickle.loads(stored_data_structure.read(maxMetaDataSize))
    else:
        stored_data_structure = open('samp.data', 'wb+')
        metaData = {
            0: [],
            1: {
                '.': None,
            }
        }
        metaData[1]['~'] = metaData[1]
        save()

    # here to setup root and present working directory structure
    voids = metaData[0]
    pwd = metaData[1]
    metas = ('~', '.')
    lock = threading.Lock()


# creating all the required low level functionalities


# print current working directory
def path_(current_directory):
    if current_directory['.'] is None: return '~'

    for name in current_directory['.']:
        if current_directory['.'][name] is current_directory:
            return path_(current_directory['.']) + f'/{name}'
# to print directory with sub directories     
def list_(current_directory):
    return [name for name in current_directory if name not in metas]





# to make new directory in cd
def create_(current_directory, name, isdir):
    if name in metas: return

    current_directory[name] = {
        '~': dir_(current_directory, '~'),
        '.': current_directory,

    } if isdir else []

def dir_(current_directory, path):
        for name in path.split('/'): current_directory = current_directory[name]
        assert type(current_directory) is dict, f'{path}: no such directory exists'

        return current_directory


# to serialize all the objects and save them
def save():
    stored_data_structure.seek(0)
    stored_data_structure.write(b' ' * maxMetaDataSize)
    stored_data_structure.seek(0)
    stored_data_structure.write(pickle.dumps(metaData))
    stored_data_structure.seek(maxMetaDataSize)

# prints menu for usage help
def help():
    print('''
        
COMMAND	        ARGUMENTS                                  FUNCTIONALITY
----------------------------------------------------------------------------------------------------------------------

cfile   	[file path]         	                   Creating a text file
move      	[source directory] [target directory]	   Move a file
write     	[file path] [input data]       	           Writing text to a file
cd      	[path]              	                   Change working directory
remove      	[file/folder path]  	                   Removes file or directory
append		[file path]	                           Appends text in a text file 
mkdir   	[directory name]    	                   Creates directory
read     	[file path]         	                   Read a text file
ls              -               	                   Lists files and folders in current_directory
trun  		[file path]/[trunc size]                   Shows Truncated file with specified size.
path            -         		                   Present working directory
dump		-			                   Show all string data
help		-			                   Print all commands and their description
memory_mapped	-			                   Trees representation like hierarchical structure
quit            -         		                   Save and exit

        
        ''')



# creating tree structure
def tree_(current_directory, depth=0):
    r = '~'
    if type(current_directory) is list:  print(': ', current_directory, end=''); return
    # return f': {current_directory}'

    for name in list_(current_directory):
        print('\n', '    ' * depth, name, end='')
        tree_(current_directory[name], depth + 1)

    return r

def dealloc_(name, current_directory):
    if type(current_directory) is list:
        voids.extend(current_directory)
        return

    for name in list_(current_directory): dealloc_(name, current_directory[name])


# all the file system functionalities


def chdir(path):
    global pwd

    current_directory = dir_(pwd, path)
    pwd = current_directory


def create1(name):
    create_(pwd, name, False)


def create2(name):
    create_(pwd, name, True)



def delete(name): 

    assert name in pwd, f'{name}: no such directory'
    dealloc_(name, pwd[name])
    del pwd[name]

def read(path, start=0, size=-1):
    start = int(start)
    size = int(size)

    f = File(path)
    f.seek(start)
    print('\n>', f.read(size), end='\n\n')
    f.close()

def move(name, path): 

    current_directory = dir_(pwd, path)
    assert name in pwd, f'{name}: no such directory'
    current_directory[name] = pwd[name]
    del pwd[name]


def quit():
    save();
    print();
    exit()


def tree():
    print('~', end='')
    tree_(dir_(pwd, '~'))
    print()


def path():
    print(path_(pwd))
    


def lis():
    print(*list_(pwd), sep='   ')
    

def append(path, data, at=-1):
    at = int(at)

    f = File(path)
    f.seek(at)
    f.write(data, overwrite=False)
    f.close()



def write(path, data, at=0):
    at = int(at)

    f = File(path)
    f.seek(at)
    f.write(data)
    f.close()


def truncate(path, trunc_size, at=0):
    at = int(at)
    trunc_size = int(trunc_size)

    f = File(path)
    f.seek(at)
    

    
    f.truncate(trunc_size)
    f.close()

# File Class Implementation

class File():

    def __init__(self, path):

        tmp = path.rsplit('/', 1)

        self.name = tmp[-1]
        self.dir = pwd if len(tmp) == 1 else dir_(pwd, tmp[0])
        self.ptr = 0
        self.data = b''
        self.ptrs = self.dir[self.name]

        assert type(self.ptrs) is list, f'{self.name}, is not a file'  

        tmp = self.ptrs.copy()[::-1]
        while tmp:
            i = tmp.pop()
            s = tmp.pop()

            stored_data_structure.seek(i)
            self.data += stored_data_structure.read(s)

    def tell(self):
        return self.ptr


    def seek(self, pos):

        if not ~pos: pos = self.size()
        assert 0 <= pos <= self.size(), f'File pointer out of range. File size is {self.size()}'  
        self.ptr = pos

    def append(self, data):

        data = data.encode()
        self.data = self.data[:self.ptr] \
                    + data \
                    + self.data[self.ptr:]

    def size(self):
        return len(self.data)

    def read(self, size=-1):

        i = self.ptr
        j = self.ptr + size

        if not ~size: j = self.size()

        self.seek(j)
        return self.data[i: j].decode()

    def write(self, data, overwrite=True):

        end = min(self.size(), self.ptr + len(data))  

        data = data.encode()
        self.data = self.data[:self.ptr] \
                    + data \
                    + self.data[end:]
                    
    def truncate(self, truc_size):
	
        new_data = self.read(truc_size)
        print(new_data)
	
	

    def close(self):

        ptrs = self.ptrs
        data = self.data
        temp = []

        j = 0
        while data:

            i = stored_data_structure.seek(0, 2)
            m = len(data)

            if voids:
                i = voids.pop(0)
                m = voids.pop(0)

            elif ptrs:
                i = ptrs.pop(0)
                m = ptrs.pop(0)

            d = data[:m]
            data = data[m:]

            j = stored_data_structure.seek(i)
            n = stored_data_structure.write(d)
            temp.extend([j, n])

            if n < m: voids.extend([i, m - n])

        self.dir[self.name] = temp
        del self


# to debug and check errors

def dump():
    stored_data_structure.seek(maxMetaDataSize)
    print(stored_data_structure.read())
    print(metaData[0])


# interface for user
prog_notation = '>>> '

switch = {
    '': lambda: '',
    'help': help,
    'dump': dump,
    'remove': delete,
    'ls': lis,
    'path': path,
    'cd': chdir,
    'write': write,
    'append': append,
    'memory_mapped': tree,
    'cfile': create1,
    'mkdir': create2,
    'move': move,
    'read': read,
    'trun': truncate,
    'quit': quit,


}

if __name__ == '__main__':
 # calling the initializing code
    init()
    help()
    while True:
	# saving the state
        save()
        commands = input(prog_notation).split(' ')
        case = commands[0]
        args = commands[1:]

        try:
            assert case in switch, f'{case}: command not found'
            switch[case](*args)

        except (KeyboardInterrupt, EOFError):
            quit()
        except AssertionError as e:
            print(e)
     


