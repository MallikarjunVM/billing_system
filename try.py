#this is to check the html inheritance with two pages

from flask import Flask, render_template, request, redirect
import pymysql.cursors
app = Flask(__name__)

connection = pymysql.connect(host='localhost',
                            user='root',
                            password='Hope@123',
                            db='madhu',
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
container = []

@app.route("/")
def home():
	return redirect('/market')
    
@app.route("/market")
def market():
    return render_template('market.html')
 
@app.route("/new", methods=['GET', 'POST'])
def new():
    if request.method == "POST":
        details = request.form
        name = details['mark']
        place= details['place']
        mobile_number = details['number']
        cur = connection.cursor()
        cur.execute("INSERT INTO Users(mark, number, place) VALUES (%s, %s,%s)", (name, mobile_number, place))
        connection.commit()
        cur.close()
        return show()
    return render_template('NewAccount.html')
 
@app.route("/arrivals", methods=['GET','POST'])
def arrivals():
    render_template("awaka.html")
    if request.method == "POST":
        details = request.form
        name = details['name']
        place= details['place']
        bag = details['bag']
        lot = details['lot']
        advance = details['advance']
        rent = details['rent']  
        cur = connection.cursor()
        cur.execute("INSERT INTO arrivals(name,place,bag,lot,advance,rent) VALUES (%s,%s,%s,%s,%s,%s)", (name,place,bag,lot,advance,rent))
        connection.commit()
        cur.close()
        return redirect('/lot_number')
    return render_template('awaka.html')

@app.route("/lot_number", methods = ['GET','POST'])
def lot_number():
    if request.method == "POST":
        details = request.form
        lot = details['lot']
        if lot in container:    
            return render_template("lot_number.html", data = "Lot number exits")
        else:
            container.append(lot)
            return redirect("/arrivals")
    return render_template("lot_number.html", data = "Enter the LOT number")
    
@app.route("/farmer_patti", methods=['GET','POST'])
def farmer_patti():
    return render_template('farmer_patti.html')
    
@app.route("/add_fp", methods=['GET','POST'])
def add_patti():
    if request.method == 'POST':
        details = request.form
        variable = details['lot']
        str(variable)
        cur = connection.cursor()
        cur.execute("SELECT bag FROM arrivals where lot = "+variable)
        data = cur.fetchall()
        cur.close()
        return redirect('/add_fp_details')
    return render_template('add_fp.html')

@app.route("/add_fp_details", methods=['GET','POST'])
def add_details():
    if request.method == 'POST':
        details = request.form
        lot = details['lot']
        bag = details['jkl']
        mark = details['mark']
        rate = details['rate']
        weight = details['weight']
        total = cal_total(weight)
        cur = connection.cursor()
        cur.execute("INSERT INTO farmer_patti(lot,bag,code,rate,weight,total,sysdate) VALUES (%s,%s,%s,%s,%s,%s,curdate())", (lot,bag,mark,rate,weight,total))
        connection.commit()
        cur.close()
        return redirect('/add_fp')
    return render_template('add_fp_details.html')
 
@app.route("/trader_bill", methods=['GET','POST'])
def trader_bill():
    return ("<h1>Under maintaince</h1>")
 
@app.route("/akada", methods=['GET','POST'])
def akada():
    if request.method == 'POST':
        details = request.form     
        variable = details['code']
        cur = connection.cursor()
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'madhu'  AND TABLE_NAME = 'farmer_patti'")
        col = cur.fetchall()
        cur.execute("SELECT lot,bag,rate,weight FROM farmer_patti WHERE code = %s",(variable))
        data = cur.fetchall()
        return render_template('akada.html', data=data, col = col)
    return render_template("enter.html")
 
@app.route("/nond_register")
def nond_register():
    cur = connection.cursor()
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'madhu'  AND TABLE_NAME = 'farmer_patti'")
    col = cur.fetchall()
    cur.execute('select arrivals.lot,arrivals.bag,arrivals.bag*rate "Farmer",farmer_patti.lot,farmer_patti.bag,farmer_patti.bag*rate "Trader" from farmer_patti inner join arrivals on farmer_patti.lot = arrivals.lot;')
    data = cur.fetchall()
    cur.close()
    return render_template('nond.html', col = col,data = data)
    
@app.route("/sale_details")
def sale_details():
    cur = connection.cursor()
    cur.execute('SELECT code, sum(bag) from farmer_patti group by code')
    data = cur.fetchall()
    cur.close()
    return render_template('sales.html', data = data)
    
@app.route("/show")
def show():
    cur = connection.cursor()
    cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'madhu'  AND TABLE_NAME = 'users'")
    col = cur.fetchall()
    cur.execute("SELECT * FROM users")
    data = cur.fetchall()
    return render_template('results.html', data=data, col = col)

@app.route("/edit_bfr", methods=['GET','POST'])
def edit_bfr():
    if request.method == 'POST':
        details = request.form     
        variable = details['lot']
        str(variable)
        cur = connection.cursor()
        cur.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'madhu'  AND TABLE_NAME = 'farmer_patti'")
        col = cur.fetchall()
        cur.execute("SELECT * FROM farmer_patti WHERE lot = "+variable)
        data = cur.fetchall()
        return data
    return render_template('add_fp.html')

@app.route("/edit",methods=['GET','POST'])
def edit():
    edit_bfr()
    if request.method == 'POST':
        details = request.form
        lot = details['lot']
        bag = details['jkl']
        mark = details['mark']
        rate = details['rate']
        weight = details['weight']
        cur = connection.cursor()
        query = """UPDATE farmer_patti SET bag = %s , code = %s, rate = %s , weight = %s WHERE lot = %s;"""
        inputs = (bag,mark,rate,weight,lot)
        cur.execute(query,inputs)
        connection.commit()
        cur.close()
        return redirect('/farmer_patti')
    return render_template('edit.html', data =data)
    
@app.route('/delete', methods = ['GET','POST'])
def delete_account():
    if request.method == 'POST':
        details = request.form     
        variable = details['lot']
        str(variable)
        cur = connection.cursor()
        cur.execute("DELETE FROM farmer_patti where lot = "+variable)
        connection.commit()
        cur.close()
        return redirect('/')
    return render_template('add_fp.html')
    
def cal_total(weight):
    total_list = weight.split(",")
    total = []
    for x in total_list:
        i = int(x)
        total.append(i)
    p = tuple(total)
    return sum(p)
    
@app.route("/chopda", methods=['GET','POST'])
def chopda():
    if request.method == 'POST':
        details = request.form     
        variable = details['lot']
        cur = connection.cursor()
        cur.execute("select lot, name, bag from arrivals WHERE lot=%s",(variable))
        data = cur.fetchall()
        return render_template('chopda.html', data=data)
    return render_template("lot_number.html")
           
if __name__ == "__main__":
    app.debug = True
    app.run()