from utils import *
class Items:
	"""	A collection of income/expense items

	Attributes:
	-----------
	self.date_range: 
		specified date range (from/to) for selecting

	self.type_group: 
		specified type for selecting

	self.order_by: 
		specified sorting condition

	self.num_items: 
		first [num_items]th items to be selected

	self.items:
		a generator of selected items

	*Followings are optional (dev later)
	id_range
	cat_group
	descr_group
	amount_range

	Methods:
	--------
	select_wcond
	cal_net_amount
	make_statement

	"""
	def __init__(self, **kwargs):
		""" Receive **kwargs: date_range, type_group, order_by, num_items, ...
			Return condition string for SQL query
			ex: ___get_cstr(self, [date_range, type_group, order_by, num_items])
		"""
		self.date_range = kwargs.get("date_range")
		self.type_group = kwargs.get("type_group")
		self.order_by = kwargs.get("order_by")
		self.num_items = kwargs.get("num_items")
		self.items = self.__get_items_wcond()

		# for k, v in kwargs.items():
		# 	setattr(self, k, v)

	@staticmethod
	def date_to_string(items):
		""" Receive tuple of item data and then convert date object to string
			Return a generator object containing item data
		"""
		for item in items:
			item["date"] = item["date"].strftime("%Y-%m-%d") 
			yield item

	def __get_cstr(self, **c):
		""" Receive **c args: date_range, type_group, order_by, num_items, ...
			Return condition string for SQL query
			ex: ___get_cstr(self, [date_range, type_group, order_by, num_items])
		"""
		# Get strings
		date_range = "date >= '{}' AND date <= '{}'".format(*c.get("date_range"))
		type_group = "type = {}".format(c.get("type_group"))
		order_by = "ORDER BY id {}".format(c.get("order_by"))
		num_items = "LIMIT {}".format(c.get("num_items"))
		full_cstr = date_range + " AND " + type_group + " " + order_by + " " + num_items
		return full_cstr

	def __get_items_wcond(self):
		""" Receive **c as condition arguments
			ex: (self, [date_range, type_group, order_by, num_items])
			Return self.items all selected items or None if no item is found
		"""
		cstr = self.__get_cstr(date_range=self.date_range, type_group=self.type_group, \
				order_by=self.order_by, num_items=self.num_items)
		test = select_items(cstr).fetchone()
		if test:
			items = (make_item(*item) for item in select_items(cstr))
			return items
		else:
			return None

	def cal_net_amount(self):
		""" Return net amount by subtracting all expenses from incomes
		"""
		net_amount = float()
		items = self.__get_items_wcond()
		for item in items:
			if item["type"] == "Income":
				net_amount += float(item["amount"])
			elif item["type"] == "Expense":
				net_amount -= float(item["amount"])
			else:
				pass
		return net_amount

	def __prepare_stmnt_file(self):
		""" Prepare path to new statement file and delete the old file
			Return path to the statement file
		"""
		fpath = "./temp/" + self.date_range[0].strftime("%d%m%Y") + "-" \
				+ self.date_range[-1].strftime("%d%m%Y") + ".xlsx"
		if os.path.exists(fpath):
			os.remove(fpath)
		return fpath

	def write_statement(self):
		""" Write data of all selected items into a .xlsx file
				also including a bottom-line states net amount of all items
			Return path to the file
		""" 
		fpath = self.__prepare_stmnt_file()
		sheet = "Account Statement"
		statement = xlsxwriter.Workbook(fpath)
		statement_sheet = statement.add_worksheet(sheet)
		# Write header
		header = ("ID", "Date", "Type", "Category", "Description", "Amount(VND)")
		for i, h in enumerate(header):
			statement_sheet.write(0, i, h)
		if self.items:		# Check if is there is no item
			items = Items.date_to_string(self.items)
			# Write item data
			for row, item in enumerate(items):	
				for col, val in enumerate(item.values()):
					statement_sheet.write(row + 1, col, val)
			# Write bottom-line containing net amount
			bottom_line = row + 2		# Count for header and enumerate index  
			net_amount = self.cal_net_amount()
			statement_sheet.write(bottom_line, col, net_amount)
			mrange = f"A{bottom_line+1}:D{bottom_line+1}"
			statement_sheet.merge_range(mrange, "Net Amount")
		else:
			mrange = f"A2:F2"
			statement_sheet.merge_range(mrange, "No item to show.")
		statement.close()
		return fpath

if __name__ == "__main__":
	from mysqlutils import *
	# User friendly inputs and default values
	dfrom, dto = today,today
	dates = {
		"Today" : (today, today),
		"All"	: (today - dt.timedelta(weeks=24), today),	# at most 6 months 
		"Other" : (dfrom, dto),}
	types = {
		"All" : "type", 
		"Income" : "'Income'", 
		"Expense" : "'Expense'",}
	orders = {
		"Latest" : "DESC",
		"Oldest" : "ASC",}

	conn_db()
	a = Items(date_range=dates["All"], type_group=types["All"], order_by=orders["Oldest"], num_items=2000)
	print(a.write_statement())
	disconn_db()