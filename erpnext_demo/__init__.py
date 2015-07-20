# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

settings = frappe.local("demo_settings")

def get_settings(demo_type=None):
	if not demo_type:
		demo_type = frappe.flags.demo_type or "Standard"

	if not getattr(frappe.local, "demo_settings", None):
		settings = frappe._dict(
			country = "United States",
			currency = "USD",
			time_zone = "America/New_York",
			bank_name = "Citibank",
			prob = {
				"default": { "make": 0.6, "qty": (1,5) },
				"Sales Order": { "make": 0.4, "qty": (1,3) },
				"Purchase Order": { "make": 0.7, "qty": (1,15) },
				"Purchase Receipt": { "make": 0.7, "qty": (1,15) },
				"Project": { "make": 0.05 },
				"Task": { "make": 0.5 },
				"Stock Reconciliation": { "make": 0.05 },
				"Subcontract": { "make": 0.05 }
			}
		)

		data = get_demo_type_data(demo_type)
		for fieldname in ("company", "company_abbr", "company_tagline"):
			settings[fieldname] = data[fieldname]

		frappe.local.demo_settings = settings

	return frappe.local.demo_settings

def get_demo_type_data(demo_type):
	for data in demo_types:
		if data["name"] == demo_type:
			return data


demo_types = [
	{
		"name": "Standard",
		"company": "Wind Power LLC",
		"company_abbr": "WP",
		"company_tagline": "Wind Mills for a Better Tomorrow"
	},
	{
		"name": "Manufacturing",
		"company": "Wabi-Sabi Furnitures",
		"company_abbr": "WSF",
		"company_tagline": "Furnitures for the Imperfect World"
	},
	{
		"name": "Retail",
		"company": "Mobile Mart",
		"company_abbr": "MM",
		"company_tagline": "Curated Offerings of Phones and Tablets"
	},
	{
		"name": "Distribution",
		"company": "The Ice Cream Vendor",
		"company_abbr": "ICV",
		"company_tagline": "Distributors of EatMore® Ice Creams"
	},
	{
		"name": "Maintenance Services",
		"company": "The Mechanics Inc.",
		"company_abbr": "MI",
		"company_tagline": "We Service and Repair Any Kind of Industrial Machines"
	},
	{
		"name": "IT Services",
		"company": "PyFirm LLC",
		"company_abbr": "PF",
		"company_tagline": "Everything Pythonic"
	}
]
