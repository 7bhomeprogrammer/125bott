from flask import Flask, render_template, redirect, url_for
import database as db
import config as cfg

app = Flask(__name__)
app.secret_key = cfg.SECRET_KEY

@app.route('/')
def index():
    return redirect(url_for('stats_dashboard'))

@app.route('/stats')
def stats_dashboard():
    # 1. Барлық пайдаланушыларды (Users) және шоттарды (Invoices) алыңыз
    all_users = db.get_all_users_sync()    # Міндетті түрде Users кестесінен алу керек
    all_invoices = db.get_all_invoices_sync() # Бұл шоттардың тарихы үшін

    # 2. total_debt тек Users кестесінде бар. 
    # Сонымен қатар 'total_debt' кілтінің бар екеніне көз жеткіземіз.
    total_shop_debt = sum(user.get('total_debt', 0) for user in all_users)

    # 3. Диаграмма үшін деректерді дайындау
    chart_data = {'Наличка': 0, 'Карта': 0, 'Перечисление': 0}
    for inv in all_invoices:
        p_type = inv.get('payment_type')
        if p_type in chart_data:
            chart_data[p_type] += inv.get('amount', 0)

    # 4. Тек қарызы бар пайдаланушыларды сүзу
    debtors = [user for user in all_users if user.get('total_debt', 0) > 0]

    return render_template('stats.html', total_debt=total_shop_debt, debtors=debtors, chart_data=chart_data)           
if __name__ == '__main__':
    app.run(debug=True)