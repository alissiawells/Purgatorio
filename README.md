# Purgatorio

SHA-2 checksum-based storage, accessible by REST API REST API endpoints.

To call Daemon that will keep your deviant files in the Purgatorio:

 ```sh
$ git clone https://github.com/alissiawells/Purgatorio.git
$ cd Purgatorio
$ mkvirtualenv Purgatorio
$ pip install -r requirements.txt
$ sudo python daemon.py start
```
Open http://localhost:5000 in browser or use curl:
  
 ```sh
$ curl -i -F "file=@filename.txt" localhost:5000/
```
Download a file:
  
 ```sh
$ curl -O localhost:5000/store/filehash
```
Delete a file:
  
 ```sh
$ curl -i -X DELETE localhost:5000/store/filehash
```

Other commands:
 ```sh
$ sudo python daemon.py 
```
       

