import numpy as np
import re
import pandas as pd

def buat_semua_huruf_jadi_kecil(text):
    return text.lower()

def hapus_kata_tidak_penting(text):
    return text


def hello():
    df_abusive = pd.read_csv("Asset Challenge/abusive.csv")
    df_kamusalay = pd.read_csv("Asset Challenge/new_kamusalay.csv",encoding = 'latin1')
    df_data = pd.read_csv("Asset Challenge/data.csv",encoding = 'latin1')
    print(df_abusive)
    print("----------------------------------------")
    print(df_kamusalay)
    print("----------------------------------------")
    #print(df_data)
    print(hapus_kata_tidak_penting("Hello \n Saya Raihan"))
    df_data['Tweet']=df_data['Tweet'].replace('\n',' ',regex=True)
    print(df_data['Tweet'])


if __name__=="__main__":
    hello()
