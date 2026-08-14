/**
 * BPF WorkHub — Bridge Google Apps Script untuk sheet Overtime DRIVER.
 *
 * MASALAH:
 *   Sheet overtime Driver (1L-7Z…p48gVZEbDJS-azMqpGobmvmqCDB9J6sAB3DGM)
 *   PRIVATE — hanya bisa dibaca akun bestprofitsurabaya@gmail.com.
 *   Server BPF WorkHub tidak bisa login ke Google, jadi tombol "Refresh"
 *   tidak bisa membaca CSV-nya langsung (401).
 *
 * SOLUSI:
 *   Script ini dijalankan OLEH akun pemilik (bestprofitsurabaya@gmail.com)
 *   dan di-deploy sebagai "Web App" dengan akses "Anyone". Karena script
 *   dieksekusi sebagai pemilik, ia bisa membaca sheet private, lalu hasilnya
 *   dikembalikan sebagai JSON publik. Sheet TIDAK perlu diubah pengaturannya.
 *
 * LANGKAH DEPLOY (sekali saja, di akun Google):
 *   1. Buka sheet Driver: https://docs.google.com/spreadsheets/d/1L-7ZT0p48gVZEbDJS-azMqpGobmvmqCDB9J6sAB3DGM
 *   2. Menu: Ekstensi (Extensions) → Apps Script
 *   3. Hapus isi Code.gs, tempel SEMUA kode di bawah, lalu simpan (Ctrl+S).
 *   4. Klik "Deploy" → "New deployment" → pilih type "Web app".
 *   5. Atur:
 *        - Execute as:  Me (bestprofitsurabaya@gmail.com)
 *        - Who has access: Anyone
 *   6. Klik Deploy → salin URL Web App (https://script.google.com/macros/s/…/exec)
 *   7. Tempel URL itu di dashboard GA HR → tombol ⚙️ Sumber Data → Simpan.
 *      Tombol 🔄 Refresh kini menarik data dari sheet (tetap private).
 */

function doGet(e) {
  // Ganti ID ini bila sheet Driver diganti.
  var SHEET_ID = '1L-7ZT0p48gVZEbDJS-azMqpGobmvmqCDB9J6sAB3DGM';

  try {
    var ss = SpreadsheetApp.openById(SHEET_ID);
    var sheet = ss.getSheets()[0];
    var values = sheet.getDataRange().getValues();
    var out = [];

    if (values.length < 2) {
      return json_({ rows: [], total: 0 });
    }

    var headers = values[0].map(function (h) { return String(h || '').trim(); });
    for (var i = 1; i < values.length; i++) {
      var row = {};
      for (var j = 0; j < headers.length; j++) {
        row[headers[j]] = values[i][j];
      }
      out.push(row);
    }

    return json_({ rows: out, total: out.length });
  } catch (err) {
    return json_({ error: String(err), rows: [] });
  }
}

function json_(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// Opsional: versi POST (anti-cache tambahan) — sama outputnya dengan doGet.
function doPost(e) {
  return doGet(e);
}
