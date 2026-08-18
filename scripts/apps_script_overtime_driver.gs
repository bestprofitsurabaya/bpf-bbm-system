/**
 * BPF WorkHub — Bridge Google Apps Script untuk sheet Overtime DRIVER.
 *
 * MASALAH:
 *   Sheet overtime Driver (1L-7Z…p48gVZEbDJS-azMqpGobmvmqCDB9J6sAB3DGM)
 *   PRIVATE — hanya bisa dibaca akun yang diberi akses (mis. view saja).
 *   Server BPF WorkHub tidak bisa login ke Google, jadi tombol "Refresh"
 *   tidak bisa membaca CSV-nya langsung (401).
 *
 * SOLUSI (TIDAK perlu akses ke akun PEMILIK):
 *   Cukup salah satu akun Google yang SUDAH punya akses ke sheet — termasuk
 *   akses VIEW (read-only) — membuat script standalone ini lalu di-deploy
 *   sebagai "Web App" dengan akses "Anyone". Karena script dieksekusi
 *   sebagai akun tersebut (yang punya akses baca), ia bisa membaca sheet
 *   private, lalu hasilnya dikembalikan sebagai JSON publik. Sheet TIDAK
 *   perlu diubah pengaturannya, pemilik tidak perlu dilibatkan.
 *
 * LANGKAH DEPLOY (sekali saja, di akun Google mana pun yang punya akses):
 *   1. Buka https://script.google.com → "New project" (proyek STANDALONE,
 *      jangan lewat menu sheet — menu itu butuh akses edit).
 *   2. Hapus isi Code.gs, tempel SEMUA kode di bawah, lalu simpan (Ctrl+S).
 *   3. Klik "Deploy" → "New deployment" → pilih type "Web app".
 *   4. Atur:
 *        - Execute as:  Me (akun Anda yang punya akses ke sheet)
 *        - Who has access: Anyone
 *   5. Saat diminta izin (Authorization): pilih akun yang sama, klik
 *      "Advanced" → "Go to <proyek> (unsafe)" → Allow. Izin "view" ke
 *      spreadsheet cukup — script hanya MEMBACA, tidak menulis.
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
