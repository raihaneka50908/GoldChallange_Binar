import pandas as pd
import re
from flask import Flask,jsonify
from flask import request
from flasgger import Swagger,LazyString,LazyJSONEncoder
from flasgger import swag_from
import sqlite3

app=Flask(__name__)
app.json_encoder=LazyJSONEncoder
swagger_template=dict(
    info={
        'title':LazyString(lambda:'Dokumentasi API Untuk Cleansing Data Menggunakan RegEx'),
        'version':LazyString(lambda:'1.0.0'),
        'description':LazyString(lambda:'Dokumentasi API'),
    },
    host=LazyString(lambda:request.host)
)

swagger_config={
    'headers':[],
    'specs':[
        {
            'endpoint':'docs',
            'route':'/docs.json',
        }
    ],
    'static_url_path':'/flasgger_static',
    'swagger_ui':True,
    'specs_route':'/docs/'
}

swagger=Swagger(app,template=swagger_template,config=swagger_config)

#Membaca semua dataset yang ada
alay_dict=pd.read_csv("Asset Challenge/new_kamusalay.csv",encoding='latin1',header=None)
alay_dict=alay_dict.rename(columns={0:'Original',1:'Baku'})

kasar_dict=pd.read_csv("Asset Challenge/abusive.csv",encoding='latin1')
kasar_dict['Kata_Sensor']="disensor" #Inisiasi kata ganti untuk kata-kata yang kasar dengan kata "disensor"

print(kasar_dict)

alay_dict_map = dict(zip(alay_dict['Original'], alay_dict['Baku']))
kasar_dict_map = dict(zip(kasar_dict['ABUSIVE'],kasar_dict['Kata_Sensor']))

@swag_from("docs/hello_world.yml",methods=['GET'])
@app.route('/',methods=['GET'])
def Hello_world():
    json_response={
        'status_code':200,
        'description':"Menyapa",
        'data':'Hello World',
    }
    response_data=jsonify(json_response)
    return response_data

@swag_from("docs/text_processing.yml")
@app.route('/text-processing',methods=['POST'])
def text_processing():
    global text
    conn=sqlite3.connect('Database_Challange.db')
    cursor=conn.cursor()
    text=request.form.get('text')
    text1=text
    text1=str(text1)
    text2=preprocess(text1)
    text2=str(text2)
    json_response={
        'status_code':200,
        'description':'Text Yang Sudah Di Process',
        'data_before_cleansing':text1,
        'data_after_cleansing':text2
    }
    response_data=jsonify(json_response)
    conn.execute("INSERT INTO Kata_Kata (id,kata_sebelum_cleansing,kata_setelah_cleansing) VALUES(NULL,?,?)",(text1,text2))
    conn.commit()
    conn.close()
    return response_data

@swag_from("docs/tampilkan_text.yml")
@app.route('/tampilkan-text',methods=['GET'])
def tampilkanText():
    json_response={
        'status_code':200,
        'description':'Text Asli dan Text Cleansing',
        'data_before_cleansing':text,
        'data_after_cleansing':preprocess(text)
    }
    response_data=jsonify(json_response)
    return response_data

@swag_from('docs/upload_csv.yml')
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    
    file = request.files.getlist('file')[0]
    df = pd.read_csv(file,encoding='latin-1')
    texts_kotor=df['Tweet']
    texts_kotor=texts_kotor.to_list()
    df['Tweet']=df['Tweet'].apply(preprocess)

    texts=df['Tweet'].to_list()

    json_response={
        'status_code':200,
        'description':'Tweet Yang Sudah Di Cleansing',
        'data_before_cleansing':texts_kotor,
        'data_after_cleansing':texts
    }
    kumpulan_kata=list(zip(texts_kotor,texts))
    response_data=jsonify(json_response)

    conn=sqlite3.connect('Database_Challange.db')
    cursor=conn.cursor()
    cursor.executemany("INSERT INTO Kata_Kata (id,kata_sebelum_cleansing, kata_setelah_cleansing) VALUES (NULL,?, ?)",kumpulan_kata)
    
    conn.commit()
    conn.close()
    
    return response_data
    

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

    conn=sqlite3.connect('Database_Challange.db')
    cursor=conn.cursor()
    try:
        cursor.execute('''CREATE TABLE Kata_Kata (id INTEGER PRIMARY KEY AUTOINCREMENT, kata_sebelum_cleansing TEXT, kata_setelah_cleansing TEXT)''')
        print("Tabel Berhasil Dibuat")
    except sqlite3.OperationalError:
        print("Tabel Telah Dibuat")
    conn.commit()
    conn.close()
    

if __name__=="__main__":
    program()
    app.run()