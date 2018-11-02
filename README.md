# Purgatorio
a storage for deviant files
 ```sh
$ git clone https://github.com/alissiawells/Purgatorio.git
$ cd Purgatorio
$ python server.py
```
Open http://localhost:8000 in browser or use curl:

Upload a file
  
 ```sh
$ curl -i -X POST -F "file=@filename.txt" http://localhost:8000/
```
Download a file
  
 ```sh
$ curl -O http://localhost:8000/store/fiilehash
```
DELETE a file
  
 ```sh
$ curl -i -X DELETE http://localhost:8000/store/filehash
```


