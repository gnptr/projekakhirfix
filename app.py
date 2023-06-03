from flask import Flask, render_template, request, jsonify
from flask_ngrok import run_with_ngrok
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import load_model

app = Flask(__name__, static_url_path='/static')

app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.JPG', '.png', '.PNG']
app.config['UPLOAD_PATH'] = './static/images/uploads/'

model = None

NUM_CLASSES = 5
kelas = ["Acne", "Flek Hitam", "Healthy", "Rosacea", "Panu"]


    # Data penyakit wajah

mengatasi = {
    "jerawat": {
        "cara_atasi": "1.	Membersihkan kulit secara teratur: Rajin membersihkan kulit wajah dua kali sehari dengan pembersih yang lembut dapat membantu menghilangkan minyak berlebih, kotoran, dan bakteri yang dapat menyebabkan jerawat.\n 2.	Hindari menyentuh wajah dengan tangan yang kotor: Tangan yang kotor dapat mengandung kuman dan bakteri yang dapat memperburuk jerawat. Hindarilah menyentuh wajah secara berlebihan dan pastikan tangan dalam keadaan bersih saat menyentuh wajah.\n 3.	Gunakan produk perawatan kulit yang sesuai: Pilih produk perawatan kulit yang cocok untuk jenis kulit Anda. Hindari produk yang mengandung bahan iritan atau komedogenik yang dapat menyumbat pori-pori dan memperburuk jerawat. \n 4.	Hindari memencet atau menggaruk jerawat: Memencet atau menggaruk jerawat dapat menyebabkan peradangan yang lebih parah, meninggalkan bekas luka, dan memperluas infeksi.\n 5.	Gunakan produk yang mengandung bahan aktif seperti asam salisilat atau benzoyl peroxide: Bahan-bahan ini dapat membantu mengurangi produksi minyak berlebih, mengurangi peradangan, dan membunuh bakteri penyebab jerawat. \n 6.	Jaga pola makan sehat: Konsumsi makanan yang seimbang, kaya akan nutrisi, dan rendah gula serta makanan berlemak dapat membantu menjaga kesehatan kulit. \n 7.	Hindari paparan sinar matahari berlebih: Paparan sinar matahari berlebih dapat meningkatkan produksi minyak dan peradangan kulit. Gunakan tabir surya dengan SPF yang sesuai dan hindari terlalu lama berada di bawah sinar matahari langsung. \n 8.	Kurangi stres: Stres dapat memicu produksi hormon yang dapat meningkatkan produksi minyak dan menyebabkan jerawat. Cari cara untuk mengelola stres, seperti dengan olahraga, meditasi, atau kegiatan yang menenangkan \n 9.	Jaga kebersihan benda yang sering bersentuhan dengan wajah: Benda-benda seperti handuk, bantal, atau telepon seluler dapat menjadi sarang bakteri yang dapat memperburuk jerawat. Pastikan untuk menjaga kebersihan benda-benda ini secara teratur. \n 10.	Konsultasikan dengan dokter atau ahli dermatologi: Jika jerawat Anda parah atau tidak kunjung membaik dengan perawatan mandiri, sebaiknya konsultasikan dengan dokter atau ahli dermatologi. Mereka dapat memberikan saran dan perawatan yang lebih khusus sesuai dengan kondisi kulit Anda."
    },
    "flek hitam": {
        "cara_atasi": "1.	Gunakan tabir surya: Flek hitam seringkali disebabkan oleh paparan sinar matahari yang berlebihan. Menggunakan tabir surya dengan SPF yang cukup setiap hari dapat membantu melindungi kulit dari sinar UV dan mencegah munculnya flek hitam. \n 2.	Hindari paparan sinar matahari secara langsung: Selain menggunakan tabir surya, hindari paparan sinar matahari langsung terutama pada jam-jam matahari paling terik, yaitu antara pukul 10 pagi hingga 4 sore. \n 3.	Gunakan krim pemutih: Krim pemutih yang mengandung bahan seperti hydroquinone, kojic acid, asam azelaic, atau asam retinoat dapat membantu mengurangi flek hitam dengan menghambat produksi melanin. \n 4.	Perawatan laser: Terapi laser seperti laser pigmentasi atau laser CO2 fraksional dapat membantu menghilangkan flek hitam pada wajah. Namun, perlu konsultasi dengan dokter atau ahli dermatologi untuk menentukan jenis perawatan yang sesuai untuk kondisi Anda. \n 5.	Menggunakan peeling kimia: Peeling kimia dengan asam glikolat, asam salisilat, atau asam mandelat dapat membantu mengelupas lapisan kulit yang terkena flek hitam dan merangsang pertumbuhan sel kulit baru yang lebih cerah. \n 6.	Rutin membersihkan wajah: Membersihkan wajah secara teratur dan menyeluruh dapat membantu menghilangkan kotoran, minyak, dan sel kulit mati yang dapat memperburuk penampilan flek hitam.  \n 7.	Menggunakan serum atau krim dengan vitamin C: Vitamin C memiliki sifat antioksidan dan dapat membantu mencerahkan kulit serta mengurangi tampilan flek hitam. Gunakan serum atau krim yang mengandung vitamin C secara teratur.  \n 8.	Menggunakan masker wajah alami: Beberapa bahan alami seperti jus lemon, yogurt, madu, atau lidah buaya memiliki sifat pemutih alami dan dapat membantu mengurangi flek hitam. Gunakan masker wajah alami ini secara teratur.  \n 9.	Hindari penggunaan kosmetik yang berat: Penggunaan kosmetik yang berat, terutama yang mengandung bahan berbahaya atau iritan, dapat memperburuk kondisi flek hitam. Pilihlah kosmetik yang ringan dan bebas minyak.  \n 10.	Gaya hidup sehat: Gaya hidup sehat, termasuk konsumsi makanan bergizi, tidur yang cukup, dan mengelola stres, dapat membantu menjaga kesehatan kulit dan mengurangi risiko munculnya flek hitam."
    },
    "sehat": {
        "cara_atasi": "1.	Rutin membersihkan wajah: Cuci wajah secara teratur, setidaknya dua kali sehari, menggunakan pembersih yang lembut dan sesuai dengan jenis kulit Anda. Ini akan membantu menghilangkan kotoran, minyak berlebih, dan sisa-sisa makeup yang dapat menyumbat pori-pori. \n 2.	Menjaga kelembapan kulit: Gunakan pelembap yang cocok untuk jenis kulit Anda setelah mencuci wajah. Ini akan membantu menjaga kelembapan alami kulit dan mencegah kulit menjadi kering dan kusam. \n 3.	Melindungi kulit dari sinar matahari: Gunakan tabir surya dengan SPF yang cukup setiap kali Anda berada di luar ruangan, bahkan saat cuaca mendung. Paparan sinar matahari yang berlebihan dapat menyebabkan penuaan dini, flek hitam, dan kerusakan kulit lainnya. \n 4.	Hindari merokok dan konsumsi alkohol berlebihan: Merokok dan konsumsi alkohol berlebihan dapat merusak kesehatan kulit, menyebabkan keriput, garis-garis halus, dan penampilan kusam. Hindari kebiasaan ini untuk menjaga kondisi kulit yang sehat. \n  5.	Konsumsi makanan sehat: Pola makan yang seimbang dengan asupan nutrisi yang cukup dapat berdampak positif pada kondisi kulit. Konsumsilah makanan yang kaya akan vitamin, mineral, dan antioksidan seperti buah-buahan, sayuran, biji-bijian, dan ikan berlemak. \n 6.	Minum cukup air: Pastikan Anda terhidrasi dengan baik dengan meminum cukup air setiap hari. Air membantu menjaga kelembapan kulit dan menghilangkan racun dari tubuh. \n  7.	Hindari stres berlebihan: Stres dapat mempengaruhi kesehatan kulit. Cari cara untuk mengelola stres seperti dengan berolahraga, meditasi, atau aktivitas relaksasi lainnya. \n 8.	Tidur yang cukup: Pastikan Anda mendapatkan tidur yang cukup setiap malam. Tidur yang cukup membantu regenerasi sel-sel kulit dan memperbaiki kerusakan yang terjadi selama hari.\n 9.	Hindari sentuhan berlebih pada wajah: Hindari menyentuh wajah secara berlebihan, terutama dengan tangan yang kotor. Tangan dapat mengandung kuman dan bakteri yang dapat menyebabkan infeksi kulit. \n 10.	Rutin kunjungi ahli dermatologi: Konsultasikan dengan ahli dermatologi secara rutin untuk pemeriksaan kulit dan perawatan yang sesuai. Ahli dermatologi dapat memberikan saran dan perawatan khusus untuk menjaga kondisi kulit yang sehat."
    },
    "rosacea": {
        "cara_atasi": "1.	Konsultasi dengan dokter atau ahli dermatologi: Jika Anda mengalami gejala rosacea pada wajah, sangat penting untuk berkonsultasi dengan dokter atau ahli dermatologi. Mereka dapat mendiagnosis kondisi dengan tepat dan memberikan penanganan yang sesuai. \n 2.	Hindari pemicu rosacea: Identifikasi faktor pemicu yang memicu flare-up rosacea pada wajah Anda, seperti paparan sinar matahari, makanan pedas, alkohol, stres, atau perubahan suhu. Upayakan untuk menghindari atau mengurangi paparan terhadap pemicu-pemicu ini.  \n 3.	Gunakan tabir surya dengan SPF: Paparan sinar matahari dapat memperburuk gejala rosacea. Gunakan tabir surya dengan SPF yang tinggi dan lindungi wajah Anda dari sinar matahari dengan menggunakan topi atau payung saat berada di luar ruangan.  \n 4.	Gunakan produk perawatan kulit yang lembut: Pilih produk perawatan kulit yang dirancang khusus untuk kulit sensitif atau rosacea. Hindari penggunaan produk yang mengandung bahan iritan seperti alkohol, pewangi, atau detergen yang keras. \n 5.	Gunakan pelembap yang lembut: Menggunakan pelembap yang cocok untuk kulit sensitif dapat membantu menjaga hidrasi kulit dan mengurangi gejala kemerahan dan kering pada rosacea. \n 6.	Hindari penggunaan produk perawatan yang mengandung scrub atau eksfolian yang kasar: Penggunaan produk perawatan yang agresif dapat memperburuk iritasi pada kulit rosacea. Pilih produk yang lembut dan tidak mengandung partikel-partikel kasar. \n 7.	Gunakan make-up yang sesuai: Jika Anda menggunakan make-up, pilihlah produk yang dirancang khusus untuk kulit sensitif atau rosacea. Gunakan foundation yang ringan, hindari produk yang mengandung pewarna atau bahan iritan, dan bersihkan make-up secara menyeluruh setelah digunakan. \n 8.	Hindari penggunaan air panas: Air panas dapat memicu flare-up pada rosacea. Cuci wajah Anda dengan air hangat atau suhu yang nyaman, dan hindari air yang terlalu panas saat mandi atau mencuci wajah. \n 9.	Gunakan kompres dingin: Jika kulit Anda sedang meradang atau terasa panas, gunakan kompres dingin atau handuk yang dibasahi dengan air dingin untuk meredakan peradangan dan kemerahan. \n 10.	Terapi laser atau fotodinamik: Dalam beberapa kasus yang lebih parah, dokter atau ahli dermatologi mungkin merekomendasikan terapi laser atau fotodinamik untuk mengurangi gejala rosacea. Terapi ini dapat membantu mengurangi kemerahan, pembuluh darah yang terlihat, dan peradangan pada kulit."  
    },
    "panu": {
        "cara_atasi": "1.	Konsultasi dengan dokter: Jika Anda mengalami panu pada wajah, sangat disarankan untuk berkonsultasi dengan dokter atau ahli dermatologi. Mereka dapat mendiagnosis kondisi dengan tepat dan memberikan penanganan yang sesuai. \n 2.	Obat antifungal topikal: Dokter dapat meresepkan obat antifungal topikal seperti krim atau salep yang mengandung bahan aktif seperti ketoconazole, miconazole, atau clotrimazole. Obat ini dapat membantu menghilangkan infeksi jamur penyebab panu.  \n 3.	Penggunaan sampo antifungal: Jika panu juga ada di area kulit kepala atau di sekitar rambut, dokter mungkin merekomendasikan penggunaan sampo antifungal yang mengandung bahan seperti selenium sulfida atau ketoconazole.  \n 4.	Perawatan sistemik: Jika infeksi panu cukup luas atau tidak merespon terhadap pengobatan topikal, dokter dapat meresepkan obat antifungal dalam bentuk tablet atau kapsul. Pengobatan sistemik ini seringkali digunakan dalam kasus-kasus yang lebih parah.  \n 5.	Hindari faktor pemicu: Beberapa faktor seperti kelembaban, panas, atau penggunaan kosmetik yang berat dapat memperburuk panu. Dokter mungkin menyarankan untuk menghindari faktor-faktor ini untuk membantu mengatasi panu dengan lebih baik.  \n 6.	Kebersihan dan perawatan kulit: Menjaga kebersihan kulit wajah dan menjaga kelembapan kulit dapat membantu mengurangi risiko infeksi dan mempercepat pemulihan. Gunakan pembersih wajah yang lembut dan hindari menggosok atau menggaruk kulit yang terinfeksi.  \n 7.	Jangan berbagi barang-barang pribadi: Untuk mencegah penyebaran infeksi jamur, hindari berbagi barang-barang pribadi seperti handuk, pakaian, atau peralatan makeup dengan orang lain.  \n 8.	Perhatikan kebersihan pakaian dan seprai: Cuci pakaian, seprai, dan handuk secara teratur dengan air panas untuk membunuh jamur yang mungkin ada di dalamnya. \n 9.	Hindari perawatan wajah yang agresif: Penggunaan bahan atau perawatan wajah yang agresif seperti scrub atau astringen yang keras dapat memperburuk iritasi dan peradangan. Gunakan produk perawatan yang lembut dan sesuai dengan kulit Anda.  \n 10.	Patuhi petunjuk pengobatan: Pastikan untuk mengikuti petunjuk dan rekomendasi pengobatan yang diberikan oleh dokter atau ahli dermatologi. Gunakan obat sesuai dengan dosis dan durasi yang ditentukan untuk memastikan pengobatan yang efektif."
    }    
}



# Load model saat aplikasi Flask dijalankan
@app.before_first_request
def load_model_():
    global model
    model = load_model("modelkulitwajah94.h5")

# Routing untuk halaman utama atau home
@app.route("/")
def beranda():
    return render_template('index.html')

# Routing untuk API deteksi
@app.route("/api/deteksi", methods=['POST'])
def apiDeteksi():
    # Set nilai default untuk hasil prediksi dan gambar yang diprediksi
    hasil_prediksi = '(none)'
    gambar_prediksi = '(none)'

    # Get File Gambar yang telah diupload oleh pengguna
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)

    # Periksa apakah ada file yang dipilih untuk diupload
    if filename != '':
        # Set / mendapatkan extension dan path dari file yang diupload
        file_ext = os.path.splitext(filename)[1]
        gambar_prediksi = '/static/images/uploads/' + filename

        # Periksa apakah extension file yang diupload sesuai (jpg)
        if file_ext in app.config['UPLOAD_EXTENSIONS']:
            # Simpan gambar
            uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

            # Memuat gambar
            test_image = Image.open('.' + gambar_prediksi)

            # Mengubah ukuran gambar
            test_image_resized = test_image.resize((224, 224))

            # Konversi gambar ke array
            image_array = np.array(test_image_resized)
            test_image_x = (image_array / 255)
            test_image_x = np.expand_dims(test_image_x, axis=0)

            # Prediksi gambar
            y_pred_test_single = model.predict(test_image_x)
            y_pred_test_classes_single = np.argmax(y_pred_test_single, axis=1)

            hasil_prediksi = kelas[y_pred_test_classes_single[0]]

        # Return hasil prediksi dengan format JSON
        return jsonify({
            "prediksi": hasil_prediksi,
            "gambar_prediksi": gambar_prediksi
        })
         

# Menjalankan aplikasi Flask
if __name__ == '__main__':
    
    run_with_ngrok(app)
    app.run(host="localhost", port=5001, debug=True)
