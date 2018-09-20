import os
import sys
import subprocess as sp
import datetime as dt

from getpass import getuser as gethostname

def split_argv(argv):
    files = []
    args = []

    for arg in argv:
        if len(arg) > 0:
            if arg[0] == '-':
                args.append(arg)
            else:
                files.append(arg)

    return files,args

def make_properties(address,port):
    with open('properties.json','w+') as json:
        json.write('{\n\t"host":"127.0.0.1",\n\t"port":"1337"\n}')

def get_includes(express=False):

    includes = ["const path = require('path');\n",
                "const fs = require('fs');\n\n",
                "const properties = JSON.parse(fs.readFileSync('properties.json','utf8'));\n\n",
                "const port = properties.port;\n",
                "const host = properties.host;\n\n"]

    if express:
        includes.append("const express = require('express');\n")
        includes.append("const bodyParser = require('body-parser');\n")
        includes.append("const cors = require('cors');\n\n")
        includes.append("const corsOptions = {\n\torigin:host+':'+port,\n\toptionsSuccessStatus: 200\n}\n")
        includes.append("const app = express();\n")
        includes.append("const http = require('http').Server(app);\n\n")
        includes.append("app.use(express.static(path.join(__dirname,'www')));\n\n")
        includes.append("app.use(bodyParser.urlencoded({extended:false}));\n")
        includes.append("app.use(bodyParser.json());\n\n")
        includes.append("const get = require('./get.js');\n")
        includes.append("const post = require('./post.js');\n\n")
        includes.append("const server = http.listen(port,host,function()\n{\n\tconsole.log('Server is listening on '+ host + ':' + port);\n});\n\n")

    return includes

def get_header(filename,filetype):
    if filetype == 'js':
        return ["// filename: '"+str(filename)+".js'\n",
                "// author: '"+gethostname()+"'\n",
                "// date: '"+dt.datetime.now().strftime("%Y-%m-%d %H:%M")+"'\n",
                "// description: '"+filename+" javascript source file'\n",
                "\n"]

    if filetype == 'html':
        return ["<!-- filename: '"+str(filename)+".html'!>\n",
                "<!-- author: '"+gethostname()+"'!>\n",
                "<!-- date: '"+dt.datetime.now().strftime("%Y-%m-%d %H:%M")+"'!>\n",
                "<!-- description: '" + filename + " html source file'!>\n",
                "<!DOCTYPE html>",
                "<html>\n",
                "\t<head>\n",
                "\t\t<title> "+str(filename)+" </title>",
                "\t</head>\n",
                "\t<body>\n",
                "\t\t<p>" + str(filename) + " works! <\p>"
                "\t\t<div id='script'><script src='jquery-3.3.1.min.js'></script><script src = '"+str(filename)+".js'></script></div>",
                "\t</body>\n",
                "</html>\n",
                "\n"]

    if filetype == 'css':
        return ["/*\n",
                "// filename: '"+str(filename)+".css'\n",
                "// author: '"+gethostname()+"'\n",
                "// date: '"+dt.datetime.now().strftime("%Y-%m-%d %H:%M")+"'\n",
                "// description: '"+filename+" css source file'\n",
                "*/\n",
                "\n"]

def new_project(argv):
    if len(argv) < 1:
        print("Not enough arguments for 'project', usage instructions: https://github.com/SirScrubbington/njs")
    else:
        if os.path.exists(argv[0]):
            print("Cannot create project: Directory '", argv[0], "' already exists!")
        else:
            os.makedirs(argv[0])
            os.chdir(argv[0])

            try:
                sp.call(['npm','init','-y'],shell=True)
                sp.call(['npm','i','fs'],shell=True)
                sp.call(['npm','i','path'],shell=True)

                make_properties('127.0.0.1','1337')

            except Exception as e:
                print(e)

            files,args = split_argv(argv[1:])

            new_javascript(files)

            if '-e' in args:
                try:
                    sp.call(['npm','i','express'],shell=True)
                    sp.call(['npm','i','body-parser'],shell=True)
                    sp.call(['npm','i','cors'],shell=True)

                    new_javascript(['get','post'])

                except Exception as e:
                    print(e)

            new_javascript(['index','-e','-i',files])

            if '-g' in args:
                try:
                    with open('.gitignore','w+') as f:
                        f.write('node_modules')

                    sp.call(['git','init'],shell=True)
                    sp.call(['git','add','.'],shell=True)
                    sp.call(['git','commit','-m','"Initial commit"'],shell=True)
                except Exception as e:
                    print(e)

            if '-t' in args:
                try:
                    sp.call(['node','.'],shell=True)

                except Exception as e:
                    print(e)

            os.makedirs('www')



def new_javascript(argv):
    if len(argv) < 1:
        print("Not enough arguments for 'javascript', usage instructions: https://github.com/SirScrubbington/njs")
    else:

        files, args = split_argv(argv)

        for file in files:
                if isinstance(file,str):
                    with open(file+'.js','w+') as f:
                        for line in get_header(file,'js'):
                            f.write(line)

                        if file == 'index':
                            for line in get_includes('-e' in args):
                                f.write(line)

                            for item in files:
                                if not isinstance(item,str):
                                    for i in item:
                                        f.write("const "+ i +" = require('./"+ i +".js');\n")
                                    f.write("\n")
                        else:
                             f.write('module.exports = {}\n')

def new_html(argv):
    if len(argv) < 1:
        print("Not enough arguments for 'html', usage instructions: https://github.com/SirScrubbington/njs")
    else:
        if os.path.exists(argv[0]):
            print("Cannot create project: Directory '",argv[0],"' already exists!")
        else:

            files, args = split_argv(argv)

            if os.path.isdir('www'):
                os.chdir('www')

                for file in files:
                    with open(file+".js",'w+') as f:
                        for line in get_header(file,'js'):
                            f.write(line)

                    with open(file+".html",'w+') as f:
                        for line in get_header(file,'html'):
                            f.write(line)

                    with open(file+".css",'w+') as f:
                        for line in get_header(file,'html'):
                            f.write(line)

            else:
                print("Error: no 'www' directory")

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print('usage instructions: https://github.com/SirScrubbington/njs')

    else:
        if sys.argv[1] in ('p','project'):
            new_project(sys.argv[2:])
            exit(0)

        if sys.argv[1] in ('j','js','javascript'):
            new_javascript(sys.argv[2:])
            exit(0)

        if sys.argv[1] in ('h','html','page'):
            new_html(sys.argv[2:])
            exit(0)

        print('Unrecognised command! usage instructions: https://github.com/SirScrubbington/njs')