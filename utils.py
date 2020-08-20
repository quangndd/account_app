from decimal import Decimal
import mysql.connector
import datetime as dt
import xlsxwriter
import os

# Global variables
inc_cat = {
	1 : "Payroll",
	2 : "Sales",
	3 : "Active Investment", 
	4 : "Passive Cashflow",} 
exp_cat = {
	1 : "Foods & Drinks", 
	2 : "Gasoline",
	3 : "Repairs",
	4 : "Charity",
	5 : "Shoppings",
	6 : "Memberships",
	7 : "Entertainments",
	8 : "Personal Savings",
	9 : "Loans Repayment",
	10 : "Mics",}
itypes = {"Income" : inc_cat, "Expense" : exp_cat}
today = dt.date.today()

def conn_db():
	""" Return db connection and cursor make them 
		globally available
	"""
	global conn, curs
	conn = mysql.connector.connect(
		host='db4free.net',
		port=3306,
		user='quangpro',
		password='quangpro',
		database='persfin')
	curs = conn.cursor(buffered=True)
	return conn, curs

def disconn_db():
	""" Close db connection
	"""
	global conn, curs
	curs.close()
	conn.close()
	return

def make_item(*values):
	"""	Receive *data as all specified data of an item
		Return a dict containing data of an item
	"""
	keys = ("id", "date", "type", "category", "description", "amount")
	if len(values):
		item = dict(zip(keys, values))
		return item
	else:
		return {key : None for key in keys}

def add_new(*args):
	""" *args should be a tuple containing item data with no ID
		ex: args = (date,type, category, description, amount)
	"""
	try:
		global conn, curs
		sql = "INSERT INTO tbl_inc_exp VALUES ('{0}','{1}','{2}','{3}','{4}','{5}');"\
				.format(*args)
		curs.execute(sql)
		conn.commit()
		added_item = select_wID(args[0])
		if not added_item:
			raise
		return True
	except:
		return False

def get_lastID():
	""" Return id of last item, if none return 1
	"""
	try:
		global conn, curs
		sql = "SELECT id FROM tbl_inc_exp ORDER BY id DESC LIMIT 1"
		curs.execute(sql)
		lastID = curs.fetchone()[0]
		return lastID
	except:
		return 1000001

def select_wID(iid):
	""" Return item data with specified id
	"""
	try:
		global conn, curs
		sql = "SELECT * FROM tbl_inc_exp WHERE id={}".format(iid)
		curs.execute(sql)
		item = curs.fetchone()
		return item
	except:
		return None

def edit_byID(*args):
	""" Edit all data of item by ID
		*args should be a tuple containing item data
		ex: args = (id, date,type, category, description, amount)
	"""
	global conn, curs
	try:
		sql = "UPDATE tbl_inc_exp SET date='{1}', type='{2}', category='{3}', "\
				"description='{4}', amount='{5}' WHERE id='{0}';".format(*args)
		print(sql)
		curs.execute(sql)
		conn.commit()
		return True
	except:
		return False

def delete_byID(iid):
	""" Delete an item by ID
	"""
	global conn, curs
	try:
		sql = "DELETE FROM tbl_inc_exp WHERE id={}".format(iid)
		curs.execute(sql)
		conn.commit()
		return True
	except:
		return False

def select_items(cstr="1"):
	""" Returns items (all by default) based on a specified condition string
	"""
	global conn, curs
	sql = "SELECT * FROM tbl_inc_exp;"
	sql = sql.rstrip(";") + " WHERE {};".format(cstr)
	curs.execute(sql)
	return curs

if __name__ == "__main__":
	dates = {
	"Today" : (today, today),
	"All"	: (today - dt.timedelta(weeks=24), today),} # at most 6 month
	conn_db()

	idata = (1000030, "2020-07-15", "Income", itypes["Income"][3], \
					"DESCRIPTION", 99.99)
	added = add_new(*idata)
	print(added)
	disconn_db()