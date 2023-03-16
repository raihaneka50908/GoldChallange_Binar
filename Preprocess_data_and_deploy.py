import pandas as pd
import re

#Membaca semua dataset yang ada
alay_dict=pd.read_csv("Asset Challenge/new_kamusalay.csv",encoding='latin1',header=None)
alay_dict=alay_dict.rename(columns={0:'Original',1:'Baku'})

kasar_dict=pd.read_csv("Asset Challenge/abusive.csv",encoding='latin1')
kasar_dict['Kata_Sensor']="disensor" #Inisiasi kata ganti untuk kata-kata yang kasar dengan kata "disensor"

print(kasar_dict)

alay_dict_map = dict(zip(alay_dict['Original'], alay_dict['Baku']))
kasar_dict_map = dict(zip(kasar_dict['ABUSIVE'],kasar_dict['Kata_Sensor']))
def normalize_alay(text):
    return ' '.join([alay_dict_map[word] if word in alay_dict_map else word for word in text.split(' ')])


def sensor_kata_kasar(text):
    return ' '.join([kasar_dict_map[word] if word in kasar_dict_map else word for word in text.split(' ')])


def preprocess(TextYangInginDiPreProcess):

    """
    #Pada fungsi ini, kata-kata alay yang digunakan sebagai referensi adalah kata-kata alay pada
    data "new_kamusalay.csv"
    #Pada fungsi ini, kata kasar yang digunakan sebagai referensi adalah kata-kata kasar pada data
    abusive.csv
    """
    #Tahap Pertama Adalah Membuat semua huruf menjadi huruf kecil atau lower
    text = TextYangInginDiPreProcess.lower()

    #Tahap Kedua adalah menghilangkan non alpha numeric character pada text
    text = re.sub('[^0-9a-zA-Z]+',' ',text)

    #Tahap Ketiga adalah menghilangkan char tidak penting
    text=re.sub('\n',' ',text) #Menghilangkan new line pada data
    text=re.sub('rt',' ',text) #Menghilangkan kata-kata retweet 
    text=re.sub('user',' ',text) #Menghilangkan kata-kata user
    text=re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) #Menghilangkan  URL
    text=re.sub(' +',' ',text) #Menghilangkan ekstra spasi

    #Tahap keempat adalah membuat map terhadap kata-kata "alay" dan mengubah nya menjadi kata yang baku
    text=normalize_alay(text)

    #Tahap kelima adalah mensensor kata kasar dengan kata "disensor"
    text=sensor_kata_kasar(text)
    return text



#Keluaran dari fungsi ini adalah sebuah file csv yang nanti akan diolah dengan menggunakann jupyter notebook untuk analisis lebih lanjut
def program():
    df_data = pd.read_csv("Asset Challenge/data.csv",encoding='latin1')
    print("Jumlah Data Terduplikasi Saat Ini : " + str(df_data.duplicated().sum()))
    df_data=df_data.drop_duplicates()
    print("Jumlah Data Terduplikasi Sekarang Adalah : "+str(df_data.duplicated().sum()))

    print("Jumlah Elemen NaN Pada Data : "+str(df_data.isna().sum()))
    
    df_data['Tweet']=df_data['Tweet'].apply(preprocess)
    print(df_data)

    df_data.to_csv("Tweet_berbahasa_indonesia_yang_telah__dipreprocess_dan_disensor.csv")
    

if __name__=="__main__":
    program()