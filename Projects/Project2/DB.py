import pandas as pd
import numpy as np
import pymysql

class Database:
    __instance = None
      
      
    @classmethod
    def __getInstance(cls):
        return cls.__instance


    @classmethod
    def instance(cls, *args, **kargs):
        cls.__instance = cls(*args, **kargs)
        cls.instance = cls.__getInstance
        return cls.__instance
    

    def __init__(self) -> None:
        self.connection = pymysql.connect(
            host='astronaut.snu.ac.kr',
            port=7000,
            user='DB2019_14355',
            password='DB2019_14355',
            db='DB2019-14355',
            charset='utf8')
        
    
    def loading_csv(self) -> None:
        pass