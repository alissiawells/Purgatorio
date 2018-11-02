# Purgatorio
Daemon with Flask API that sends your deviant files to the Purgatorio

 ```sh
$ git clone https://github.com/alissiawells/Purgatorio.git
$ cd Purgatorio
$ pip install pipenv
$ pipenv shell
$ pipenv install
$ sudo python daemon.py start
```
Open http://localhost:5000 in browser or use curl:

Upload a file:
  
 ```sh
$ curl -i -X POST -F "file=@filename.txt" http://localhost:5000/
```
Download a file:
  
 ```sh
$ curl -O http://localhost:5000/store/fiilehash
```
Delete a file:
  
 ```sh
$ curl -i -X DELETE http://localhost:5000/store/filehash
```

Other commands:
 ```sh
$ sudo python daemon.py 
```
Run tests:
 ```sh
$ cd tests
$ python tests.py 
```


