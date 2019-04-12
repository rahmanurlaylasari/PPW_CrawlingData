from math import log10
import requests
from bs4 import BeautifulSoup
import sqlite3
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import csv
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_samples,silhouette_score
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from math import log10


src = "https://www.visitkorea.or.id/category/informasi-umum/"

page = requests.get(src)


soup = BeautifulSoup(page.content, 'html.parser')

artikel = soup.find(class_='row tag-page')
artikel = artikel.findAll(class_='col-md-6 col-xl-4')
   
koneksi = sqlite3.connect('DB_korea.db')
koneksi.execute(''' CREATE TABLE if not exists VisitKorea
            (judul TEXT NOT NULL,
             isi TEXT NOT NULL);''')

for i in range(len(artikel)):
    link = artikel[i].find('a')['href']
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')
    judul = soup.find(class_='title mb-3 text-center').getText()
    isi = soup.find(class_='entry-page')
    paragraf = isi.findAll('p')
    p = ''
    for s in paragraf:
        p+=s.getText() +' '

    cek = koneksi.execute("SELECT * FROM VisitKorea WHERE judul=?", (judul,))
    cek = cek.fetchall()
    if (len(cek) == 0):
        koneksi.execute('INSERT INTO VisitKorea values (?,?)', (judul, p));

koneksi.commit()
tampil = koneksi.execute("SELECT * FROM VisitKorea")
with open ('data_crawler.csv', newline='', mode='w')as employee_file :
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for i in tampil:
        employee_writer.writerow(i)

def write_csv(nama_file, isi, tipe='w'):
    'tipe=w; write; tipe=a; append;'
    with open(nama_file, mode=tipe) as tbl:
        tbl_writer = csv.writer(tbl, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in isi:
            tbl_writer.writerow(row)

tampil = koneksi.execute("SELECT * FROM VisitKorea")
isi = []
for row in tampil:
    isi.append(row[1])
    #print(row)
    

#vsm
factory = StopWordRemoverFactory()
stopword = factory.create_stop_word_remover ()

factory = StemmerFactory ()
stemmer = factory.create_stemmer ()

tmp = ''
for i in isi:
    tmp = tmp + ' ' +i

hasil = []
for i in tmp.split():
    if i.isalpha() and not i in hasil:
        # Menghilangkan Kata tidak penting
        stop = stopword.remove(i)
        stem = stemmer.stem(stop)
        hasil.append((stem  + ' '))
katadasar = hasil
#(katadasar)


matrix = []
for row in isi :
    tamp_isi=[]
    for a in katadasar:
        tamp_isi.append(row.lower().count(a))
    matrix.append(tamp_isi)

#print(katadasar)
#for m in matrix:
 #   print(m)

#cursor = conn.execute("SELECT* from VisitKorea")
for row in tampil:
    tampung = []
    for i in katadasar:
        tampung.append(row[2].lower().count(i))
    matrix.append(tampung)

print(katadasar)

 #import csv kata yg sesuai dengan KBI
conn = sqlite3.connect('KBI.db')
cur_kbi = conn.execute("SELECT* from KATA")
    
def LinearSearch (kbi,kata):
    found=False
    posisi=0
    while posisi < len (kata) and not found :
        if kata[posisi]==kbi:
            found=True
        posisi=posisi+1
    return found

berhasil=[]
berhasil2=''
for kata in cur_kbi :
    ketemu=LinearSearch(kata[0],katadasar)
    if ketemu :
        kata = kata[0]
        berhasil.append(kata)
        berhasil2=berhasil2+' '+kata
print(berhasil)

conn = sqlite3.connect('DB_korea.db')
matrix2=[]
cursor = conn.execute("SELECT* from VisitKOrea")
for row in cursor:
    tampung = []
    for i in berhasil:
        tampung.append(row[2].lower().count(i))
        #print(tampung)
        #print(row[2])
    matrix2.append(tampung)
print(matrix2)

with open ('data_matrix.csv', newline='', mode='w')as employee_file :
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    employee_writer.writerow(katadasar)
    for i in matrix :
        employee_writer.writerow(i)

#tf-idf
df = list()
for d in range (len(matrix[0])):
    total = 0
    for i in range(len(matrix)):
        if matrix[i][d] !=0:
            total += 1
    df.append(total)

idf = list()
for i in df:
    tmp = 1 + log10(len(matrix)/(1+i))
    idf.append(tmp)

tf = matrix
tfidf = []
for baris in range(len(matrix)):
    tampungBaris = []
    for kolom in range(len(matrix[0])):
        tmp = tf[baris][kolom] * idf[kolom]
        tampungBaris.append(tmp)
    tfidf.append(tampungBaris)


with open('tf-idf.csv', newline='', mode='w') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    employee_writer.writerow(katadasar)
    for i in tfidf:
        employee_writer.writerow(i)


def pearsonCalculate(data, u,v):
    "i, j is an index"
    atas=0; bawah_kiri=0; bawah_kanan = 0
    for k in range(len(data)):
        atas += (data[k,u] - meanFitur[u]) * (data[k,v] - meanFitur[v])
        bawah_kiri += (data[k,u] - meanFitur[u])**2
        bawah_kanan += (data[k,v] - meanFitur[v])**2
    bawah_kiri = bawah_kiri ** 0.5
    bawah_kanan = bawah_kanan ** 0.5
    return atas/(bawah_kiri * bawah_kanan)
def meanF(data):
    meanFitur=[]
    for i in range(len(data[0])):
        meanFitur.append(sum(data[:,i])/len(data))
    return np.array(meanFitur)
def seleksiFiturPearson(katadasar, data, threshold):
    global meanFitur
    data = np.array(data)
    meanFitur = meanF(data)
    u=0
    while u < len(data[0]):
        dataBaru=data[:, :u+1]
        meanBaru=meanFitur[:u+1]
        katadasarBaru=katadasar[:u+1]
        v = u
        while v < len(data[0]):
            if u != v:
                value = pearsonCalculate(data, u,v)
                if value < threshold:
                    dataBaru = np.hstack((dataBaru, data[:, v].reshape(data.shape[0],1)))
                    meanBaru = np.hstack((meanBaru, meanFitur[v]))
                    katadasarBaru = np.hstack((katadasarBaru, katadasar[v]))
            v+=1
        data = dataBaru
        meanFitur=meanBaru
        katadasar = katadasarBaru
        if u%50 == 0 : print("proses : ", u, data.shape)
        u+=1
    return katadasar, data


katadasarBaru, fiturBaru = seleksiFiturPearson(katadasar, tfidf,0.783);
kmeans = KMeans(n_clusters=3, random_state=0).fit(tfidf);
print(kmeans.labels_)
classnya = kmeans.labels_
s_avg = silhouette_score(fiturBaru, classnya, random_state=0)
print (s_avg)
print("selesai, the end, bye")
with open('Anggota_cluster.csv', newline='', mode='w') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for i in classnya.reshape(-1,1):
        employee_writer.writerow(i)

with open('Seleksi_Fitur.csv', newline='', mode='w') as employee_file:
    employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    employee_writer.writerow([katadasarBaru.tolist()])
    for i in fiturBaru:
        employee_writer.writerow(i)
