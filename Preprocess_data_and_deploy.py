import pandas as pd
import re
from flask import Flask,jsonify
from flask import request
from flasgger import Swagger,LazyString,LazyJSONEncoder
from flasgger import swag_from
import csv
import json
import tempfile
import os

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

# Upload directory
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = {'csv', 'txt', 'json'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    text=request.form.get('text')
    json_response={
        'status_code':200,
        'description':'Text Yang Sudah Di Process',
        'data':preprocess(text)
    }
    response_data=jsonify(json_response)
    return response_data

@swag_from("docs/tampilkan_text.yml")
@app.route('/tampilkan-text',methods=['GET'])
def tampilkanText():
    json_response={
        'status_code':200,
        'description':'Text Asli',
        'data':text
    }
    response_data=jsonify(json_response)
    return response_data

@swag_from('docs/upload_csv.yml')
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    # memeriksa apakah file CSV diunggah
    if 'file' not in request.files:
        return jsonify({'error': 'File tidak ditemukan.'})
    
    file = request.files['file']
    
    # memeriksa apakah file CSV kosong
    if file.filename == '':
        return jsonify({'error': 'File kosong.'})
    
    # memeriksa apakah file memiliki ekstensi .csv
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File harus memiliki ekstensi .csv.'})
    
    # membaca file CSV menggunakan Pandas
    try:
        data = pd.read_csv(file)
    except Exception as e:
        return jsonify({'error': 'Gagal membaca file CSV: ' + str(e)})
    
    # mengembalikan data dalam format JSON
    return jsonify({'data': data.to_dict(orient='records')})

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
    app.run()