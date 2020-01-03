### 1.environment:
> macOS: `Catalina 10.15.2`
> 
> pycharm: `Community 2019.3`
> 
> python: `python 3.7.5`


### 2. install libraries:
> pip install scrapy
> pip install pillow
> pip install mysqlclient


### 3. problem & solution
> Problem 1: pip install mysqlclient failed
```
export PATH="$PATH:$HOME/.rvm/bin:/usr/local/mysql/bin"
```

> Problem 2: Library not loaded: @rpath/libmysqlclient.21.dylib
```
copy /usr/local/mysql/lib/libmysqlclient.18.dylib to /usr/local/lib/libmysqlclient.18.dylib
```

> Problem 3: Can't initialize character set utf-8 (path: /usr/local/mysql/share/charsets/
```
change charset='utf-8’ to charset='utf8’
```

> Problem 4: 1062, "Duplicate entry 'd335db26ecd8e7e2a6ac7ef7973b2bcf' for key 'PRIMARY'"

change
```
    sql = """
        insert into article(title, title_id, content)
        values(%s, %s, %s)
    """
```
to
```
    sql = """
        insert into article(title, title_id, content)
        values(%s, %s, %s) ON DUPLICATE KEY UPDATE content=values(content)
    """
```




