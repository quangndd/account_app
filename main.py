from flask import Flask, render_template, request, send_file, g
from utils import *
from Items import *
import glob

# Global variables
func = {"add" : "New Income/Expense",
		"show_history" : "Show History",}

# User friendly inputs and default values for query strings
types = {
	"All" : "type", 
	"Income" : "'Income'", 
	"Expense" : "'Expense'",}
orders = {
	"Latest" : "DESC",
	"Oldest" : "ASC",}

def get_db():
    if not hasattr(g, 'db'):
        g.db = conn_db()
    return g.db

def create_app():
    app = Flask(__name__)
    with app.app_context():
        conn = get_db()
    return app

app = create_app()

# close db at end of each request
@app.teardown_appcontext
def close_db(error):
    disconn_db()

@app.before_request
def db_connect():
	conn_db()

@app.route("/")
@app.route("/home")
def home():
	return render_template("home.html", func=func)


@app.route("/add")
def add():
	item = make_item()
	nextid = get_lastID() + 1
	return render_template("add.html", title="Add", nextid=nextid, today=today, \
		inc_cat=inc_cat, exp_cat=exp_cat, item=item)

@app.route("/add/send", methods=["GET", "POST"])
def add_send():
	today = dt.date.today()
	if request.method == "POST":
		aid = request.form["aid"]
		adate = request.form["adate"]
		atype = request.form["atype"]
		acategory = request.form["acategory"]
		adescription = request.form["adescr"]
		aamount = request.form["aamount"]
		try:
			idata= (int(aid), adate, atype, itypes[atype][int(acategory)], \
					adescription, float(aamount))
			added = add_new(*idata) 
			if not added:
				raise Exception
			item = make_item(*idata)
			return render_template("add.html", title="Add New Item", today=today, inc_cat=inc_cat, \
						exp_cat=exp_cat, nextid=aid, added=added, item=item)
		except Exception as e:
			added = False
			item = make_item()
			return render_template("add.html", title="Add New Item", today=today, inc_cat=inc_cat, \
					exp_cat=exp_cat, nextid=aid, added=added, item=item)

def init_var():
	global date_range, select_type, order_by
	date_range = (today, today)
	select_type = "All"
	order_by = "Latest"

init_var()
@app.route("/history")
def history():
	init_var()
	items_ = Items(date_range=date_range, type_group=types["All"], \
			order_by=orders["Latest"], num_items=2000)
	if not items_.items:
		items_.items = (make_item(),)
	return render_template("history.html", title="history", date_range=date_range, \
			select_type=select_type, order_by=order_by, items=items_.items)

@app.route("/history/send", methods=["GET", "POST"])
def history_get():
	global date_range, select_type, order_by
	if request.method == "POST":
		date_range = (request.form["fromdate"], request.form["todate"])
		select_type = request.form["selecttype"]
		order_by = request.form["orderby"]
		items_ = Items(date_range=date_range, type_group=types[select_type], \
				order_by=orders[order_by], num_items=2000)
		if not items_.items:
			items_.items = (make_item(),)
		return render_template("history.html", title="history", date_range=date_range, \
			select_type=select_type, order_by=order_by, items=items_.items)

@app.route("/history/edit", methods=["GET", "POST"])
def history_edit():
	if request.method == "POST":
		eid = request.form["eid"]
		edate = request.form["edate"]
		etype = request.form["etype"]
		ecategory = request.form["ecategory"]
		edescr = request.form["edescr"]
		eamount = request.form["eamount"]
		try:
			edited = edit_byID(int(eid), edate, etype, itypes[etype][int(ecategory)], \
				edescr, float(eamount))
		except:
			edited = False
		items_ = Items(date_range=date_range, type_group=types[select_type], \
				order_by=orders[order_by], num_items=2000)
		if not items_.items:
			items_.items = (make_item(),)
		else:
			pass
		return render_template("history.html", title="history", edited=edited, date_range=date_range, \
				select_type=select_type, order_by=order_by, items=items_.items)

@app.route("/history/delete", methods=["GET", "POST"])
def history_delete():
	if request.method == "POST":
		did = request.form["did"]
		try:
			deleted = delete_byID(int(did))
		except:
			deleted = False
		items_ = Items(date_range=date_range, type_group=types[select_type], \
				order_by=orders[order_by], num_items=2000)
		if not items_.items:
			items_.items = (make_item(),)
		return render_template("history.html", title="history", deleted=deleted, date_range=date_range, \
				select_type=select_type, order_by=order_by, items=items_.items)

@app.route("/history/download", methods=["GET", "POST"])
def statement_download():
	global date_range
	if request.method == "POST":
		try:#if request.form["dfrom"] and request.form["dto"]:
			dfrom = dt.datetime.strptime(request.form["dfrom"], "%Y-%m-%d")
			dto = dt.datetime.strptime(request.form["dto"], "%Y-%m-%d")
			date_range = (dfrom, dto)
			items_ = Items(date_range=date_range, type_group=types[select_type], \
				order_by=orders[order_by], num_items=2000)
			fpath = items_.write_statement()
			downloaded = True
			return send_file(fpath, as_attachment=True)
		except Exception as err:#else:
			downloaded = False
			items_ = Items(date_range=date_range, type_group=types[select_type], \
				order_by=orders[order_by], num_items=2000)
			if not items_.items:
				items_.items = (make_item(),)
			return render_template("history.html", title="history", downloaded=downloaded, date_range=date_range, \
					select_type=select_type, order_by=order_by, items=items_.items)

if __name__ == "__main__":
	statements_path = glob.glob("./temp/*.xlsx")
	for f in statements_path:
		os.remove(f)
	app.run(debug=True)
