# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt
from __future__ import unicode_literals

import frappe, os
import frappe.utils

from frappe.core.page.data_import_tool.data_import_tool import import_doc
from erpnext_demo.simulate import simulate
from erpnext_demo.make_demo_docs import get_json_path
from erpnext_demo import get_settings

# fix price list
# fix fiscal year

def make(demo_type="Standard"):
	frappe.flags.mute_emails = True
	frappe.flags.demo_type = demo_type
	setup()
	frappe.set_user("Administrator")
	simulate()

def setup():
	complete_setup()
	make_customers_suppliers_contacts()
	show_item_groups_in_website()
	make_warehouses()
	make_items()
	make_price_lists()
	make_users_and_employees()
	make_bank_account()
	# make_opening_stock()
	# make_opening_accounts()

	make_tax_masters()
	make_shipping_rules()
	if "shopping_cart" in frappe.get_installed_apps():
		enable_shopping_cart()

	frappe.clear_cache()

def install():
	print "Creating Fresh Database..."
	from frappe.install_lib.install import Installer
	from frappe import conf
	inst = Installer('root')
	inst.install(conf.demo_db_name, verbose=1, force=1)

def complete_setup():
	print "Complete Setup..."
	from erpnext.setup.page.setup_wizard.setup_wizard import setup_account
	settings = get_settings(frappe.flags.demo_type)

	setup_account({
		"first_name": "Test",
		"last_name": "User",
		"email": "test_demo@erpnext.com",
		"password": "test",
		"fy_start_date": "2015-01-01",
		"fy_end_date": "2015-12-31",
		"industry": "Manufacturing",
		"company_name": settings.company,
		"chart_of_accounts": "Standard",
		"company_abbr": settings.company_abbr,
		"company_tagline": settings.company_tagline,
		"currency": settings.currency,
		"timezone": settings.time_zone,
		"country": settings.country,
		"language": "english"
	})

	# home page should always be "start"
	website_settings = frappe.get_doc("Website Settings", "Website Settings")
	website_settings.home_page = "start"
	website_settings.save()

	import_data("Fiscal Year")
	import_data("Holiday List")

	frappe.clear_cache()

def show_item_groups_in_website():
	"""set show_in_website=1 for Item Groups"""
	products = frappe.get_doc("Item Group", "Products")
	products.show_in_website = 1
	products.save()

def make_warehouses():
	settings = get_settings()

	for w in [{"warehouse_name": "Supplier", "create_account_under": "Stock Assets"}]:
		warehouse = frappe.new_doc("Warehouse")
		warehouse.company = settings.company
		warehouse.warehouse_name = w["warehouse_name"]
		warehouse.create_account_under = w["create_account_under"] + " - " + settings.company_abbr
		warehouse.insert()

def make_items():
	import_data("Item")
	import_data("Product Bundle")
	import_data("Workstation")
	import_data("Operation")
	import_data("BOM", submit=True)

def make_price_lists():
	import_data("Currency Exchange")
	import_data("Item Price", overwrite=True)

def make_customers_suppliers_contacts():
	import_data(["Customer", "Supplier", "Contact", "Address", "Lead"])

def make_users_and_employees():
	frappe.db.set_value("HR Settings", None, "emp_created_by", "Naming Series")
	frappe.db.commit()

	import_data(["User", "Employee", "Salary Structure"])

def make_bank_account():
	settings = get_settings(frappe.flags.demo_type)

	ba = frappe.get_doc({
		"doctype": "Account",
		"account_name": settings.bank_name,
		"account_type": "Bank",
		"is_group": 0,
		"parent_account": "Bank Accounts - " + settings.company_abbr,
		"company": settings.company
	}).insert()

	frappe.set_value("Company", settings.company, "default_bank_account", ba.name)
	frappe.db.commit()

def make_tax_masters():
	import_data("Sales Taxes and Charges Template")
	import_data("Purchase Taxes and Charges Template")

def make_shipping_rules():
	import_data("Shipping Rule")

def enable_shopping_cart():
	# import
	path = os.path.join(os.path.dirname(__file__), "demo_docs", frappe.flags.demo_type, "Shopping Cart Settings.json")
	import_doc(path)

	# enable
	settings = frappe.get_doc("Shopping Cart Settings")
	settings.enabled = 1
	settings.save()

def import_data(dt, submit=False, overwrite=False):
	if not isinstance(dt, (tuple, list)):
		dt = [dt]

	settings = get_settings(frappe.flags.demo_type)
	def pre_process(doc):
		if doc.meta.get_field("company"):
			doc.set("company", settings.company)

		for key, val in doc.as_dict().items():
			if isinstance(val, basestring) and val.endswith(" - WP"):
				doc.set(key, val.replace(" - WP", " - {0}".format(settings.company_abbr)))

	for doctype in dt:
		path = get_json_path(doctype, frappe.flags.demo_type)
		if not os.path.exists(path):
			path = get_json_path(doctype, "Standard")

		import_doc(path, submit=submit, overwrite=overwrite, pre_process=pre_process)
