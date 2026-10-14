from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Aviator Analyzer</title>
    <style>
        body {
            background: #101820;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 25px;
        }
        .box {
            background: #1c2b36;
            padding: 25px;
            border-radius: 15px;
            max-width: 400px;
            margin: 30px auto;
        }
        input, button {
            padding: 12px;
            margin: 8px;
            border-radius: 8px;
            border: none;
            font-size: 17px;
        }
        button {
            background: #e63946;
            color: white;
            cursor: pointer;
        }
        #result {
            font-size: 22px;
            color: #ffd166;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>✈️ AVIATOR</h1>
    <div class="box">
        <h3>محلل نتائج اللعبة</h3>
        <p>أدخل المضاعفات السابقة، مفصولة بفواصل</p>
        <input id="history" placeholder="1.2, 2.5, 1.1, 4.3">
        <br>
        <button onclick="analyze()">تحليل النتائج</button>
        <div id="result"></div>
        <p>التحليل لا يضمن التنبؤ بالجولة التالية.</p>
    </div>
    <script>
        function analyze() {
            const values = document.getElementById('history')
                .value.split(',')
                .map(x => Number(x.trim()))
                .filter(x => Number.isFinite(x) && x >= 1);

            const result = document.getElementById('result');

            if (values.length < 3) {
                result.textContent = 'أدخل 3 مضاعفات صحيحة على الأقل.';
                return;
            }

            const average = values.reduce((a, b) => a + b, 0)
                / values.length;

            result.textContent =
                'متوسط النتائج السابقة: ' + average.toFixed(2) + 'x';
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
