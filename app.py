from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def send_reset_request(username_or_email):
    """
    Instagram şifre sıfırlama isteğini gönderir.
    Dönen Response objesini geri döner.
    """
    url = "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/"

    # CSRF token alabilmek için önce reset sayfasını çağırıyoruz
    session = requests.Session()
    session.get("https://www.instagram.com/accounts/password/reset/")
    csrf_token = session.cookies.get_dict().get("csrftoken", "missing")

    headers = {
        "authority": "www.instagram.com",
        "method": "POST",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://www.instagram.com",
        "referer": "https://www.instagram.com/accounts/password/reset/?source=fxcal",
        "sec-ch-ua": '"Not-A.Brand";v="99", "Chromium";v="124"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Linux; Android 10; M2101K786) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "x-asbd-id": "129477",
        "x-csrftoken": csrf_token,
        "x-ig-app-id": "1217981644879628",
        "x-ig-www-claim": "0",
        "x-instagram-ajax": "1015181662",
        "x-requested-with": "XMLHttpRequest"
    }

    data = {
        "email_or_username": username_or_email,
        "flow": "fxcal"
    }

    response = session.post(url, headers=headers, data=data)
    return response

@app.route("/", methods=["GET"])
def reset_route():
    """
    GET /?user=<kullanıcı_adı_veya_email> formatında çağrıldığında:
    - Eğer 'user' parametresi eksikse özel hata mesajı döner.
    - Başarılıysa "TAMAM RESET LİNKİNİ ATTIN KNK" mesajı döner.
    - Başarısızsa önce "RESET ISTEĞİ BAŞARISIZ" mesajı, altta da Instagram API yanıtı yer alır.
    """
    username_or_email = request.args.get("user")
    if not username_or_email:
        return jsonify({"message": "HANI KIME RESET ATAYIM YARRAM"}), 400

    try:
        resp = send_reset_request(username_or_email)
    except Exception as e:
        return jsonify({
            "message": "RESET ISTEĞI BAŞARISIZ",
            "details": str(e)
        }), 500

    # İstek başarılıysa
    if resp.status_code == 200:
        return jsonify({"message": "TAMAM RESET LINKINI ATTIM KNK"}), 200

    # İstek başarısızsa
    try:
        api_body = resp.json()
    except ValueError:
        api_body = {"raw_text": resp.text}

    return jsonify({
        "message": "RESET ISTEĞI BAŞARISIZ KNK ",
        "api_response": api_body
    }), resp.status_code

if __name__ == "__main__":
    # Production'da Gunicorn kullanacağız; bu satır sadece development içindir.
    app.run(debug=True, host="0.0.0.0", port=5000)
