/**
 * シートが編集されるたびに呼ばれ、外部の Python サーバへ通知を送信する。
 */
function onEdit(e) {
  // ※Add endpoint URL(ex. ngrok)
  var url = "https://<EXAMPLE>.ngrok-free.app/update";
  // 必要に応じ、編集されたセルの情報などを payload に含める
  var payload = {
    range: e.range.getA1Notation(),
    value: e.value,
    time: new Date().toISOString()
  };
  
  var options = {
    'method': 'post',
    'contentType': 'application/json',
    'payload': JSON.stringify(payload)
  };
  
  try {
    UrlFetchApp.fetch(url, options);
  } catch (error) {
    Logger.log("Webhook送信エラー: " + error);
  }
}
