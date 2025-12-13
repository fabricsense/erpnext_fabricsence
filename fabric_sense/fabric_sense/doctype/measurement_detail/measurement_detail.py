# Copyright (c) 2025, innogenio and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import math


class MeasurementDetail(Document):
	"""
	Child table doctype for Measurement Sheet.
	Handles calculations for fabric quantities, amounts, and square feet.
	"""
	
	def validate(self):
		"""Validate and calculate fields before saving"""
		self.validate_mandatory_fields()
		self.calculate_amounts()
		self.calculate_square_feet()
		self.calculate_fabric_quantities()
		self.calculate_lead_rope_quantities()
		self.calculate_track_rod_quantities()
	
	def validate_mandatory_fields(self):
		"""Validate mandatory fields based on product type"""
		if self.product_type in ["Window Curtains", "Roman Blinds"]:
			if not self.fabric_selected:
				frappe.throw(
					f"Fabric Selected is mandatory for {self.product_type}",
					title="Missing Required Field"
				)
			# Validate panels field: must be > 0
			if not self.panels or int(self.panels) <= 0:
				frappe.throw(
					f"Panel must be greater than 0 for {self.product_type}. Please enter a valid quantity.",
					title="Invalid Panel Value"
				)
	
	def calculate_square_feet(self):
		"""Calculate square feet for Roman Blinds and Blinds"""
		if self.product_type == "Roman Blinds":
			if self.width and self.height:
				calculated_sqft = (self.width * self.height) / 144
				# Round to nearest 0.5
				self.square_feet = self.round_to_nearest_half(calculated_sqft)
			else:
				self.square_feet = 0
		elif self.product_type == "Blinds":
			if self.width and self.height:
				calculated_sqft = ((self.height + 6) * self.width) / 144
				# Round to nearest 0.5
				self.square_feet = self.round_to_nearest_half(calculated_sqft)
			else:
				self.square_feet = 0
	
	def round_to_nearest_half(self, value):
		"""Round value to nearest 0.5
		Examples: 11.1 -> 11.5, 11.5 -> 11.5, 11.6 -> 12, 12 -> 12
		"""
		return math.ceil(value * 2) / 2
	
	def calculate_fabric_quantities(self):
		"""Calculate fabric quantity based on product type"""
		if self.product_type == "Window Curtains":
			# Formula: quantity = (height + 16) * panels / 38 + adjust
			# Use explicit None checks to handle zero values correctly
			if self.height is not None and self.panels is not None:
				height_val = float(self.height) if self.height else 0
				panels_val = float(self.panels) if self.panels else 0
				adjust_val = float(self.adjust) if self.adjust else 0
				
				calculated_qty = ((height_val + 16) * panels_val) / 38
				if adjust_val:
					calculated_qty += adjust_val
				
				# Round to nearest 0.5
				self.fabric_qty = self.round_to_nearest_half(calculated_qty)
				# Copy the same value to lining quantity
				self.lining_qty = self.round_to_nearest_half(calculated_qty)
			else:
				# If height or panels is missing, set to 0
				self.fabric_qty = 0
				self.lining_qty = 0
		
		elif self.product_type in ["Roman Blinds", "Blinds"]:
			# For Roman Blinds and Blinds, use square_feet
			if self.square_feet is not None and self.square_feet > 0:
				# Round to nearest 0.5
				self.fabric_qty = self.round_to_nearest_half(self.square_feet)
				self.lining_qty = self.round_to_nearest_half(self.square_feet)
			else:
				self.fabric_qty = 0
				self.lining_qty = 0
	
	def calculate_lead_rope_quantities(self):
		"""Calculate lead rope quantity for Window Curtains"""
		if self.product_type == "Window Curtains":
			# Formula: lead_rope_qty = panels * 1.5
			if self.panels is not None:
				panels_val = float(self.panels) if self.panels else 0
				if panels_val > 0:
					# Round to nearest 0.5
					self.lead_rope_qty = self.round_to_nearest_half(panels_val * 1.5)
				else:
					self.lead_rope_qty = 0
			else:
				self.lead_rope_qty = 0
		else:
			# Not Window Curtains, set to 0
			self.lead_rope_qty = 0
	
	def calculate_track_rod_quantities(self):
		"""Calculate track/rod quantity for Window Curtains and Tracks/Rods"""
		if self.product_type in ["Window Curtains", "Tracks/Rods"]:
			# Determine multiplier based on track_rod_type
			# Default to 2 (Double Glide) for backward compatibility
			multiplier = 2
			if self.track_rod_type:
				if self.track_rod_type == "Single Glide":
					multiplier = 1
				elif self.track_rod_type == "Double Glide":
					multiplier = 2
				elif self.track_rod_type == "Triple Glide":
					multiplier = 3
			
			# Formula: track_rod_qty = (width / 12) * multiplier
			if self.width is not None:
				width_val = float(self.width) if self.width else 0
				if width_val > 0:
					# Round to nearest 0.5
					self.track_rod_qty = self.round_to_nearest_half((width_val / 12) * multiplier)
				else:
					self.track_rod_qty = 0
			else:
				self.track_rod_qty = 0
		else:
			# Not Window Curtains or Tracks/Rods, set to 0
			self.track_rod_qty = 0
	
	def calculate_amounts(self):
		"""Calculate all amount fields and total row amount"""
		# Calculate fabric amount
		if self.fabric_qty and self.fabric_rate:
			self.fabric_amount = self.fabric_qty * self.fabric_rate
		else:
			self.fabric_amount = 0
		
		# Calculate lining amount
		if self.lining_qty and self.lining_rate:
			self.lining_amount = self.lining_qty * self.lining_rate
		else:
			self.lining_amount = 0
		
		# Calculate lead rope amount
		if self.lead_rope_qty and self.lead_rope_rate:
			self.lead_rope_amount = self.lead_rope_qty * self.lead_rope_rate
		else:
			self.lead_rope_amount = 0
		
		# Calculate track/rod amount
		if self.track_rod_qty and self.track_rod_rate:
			self.track_rod_amount = self.track_rod_qty * self.track_rod_rate
		else:
			self.track_rod_amount = 0
		
		# Get service charges (stitching and fitting)
		stitching_charge = float(self.stitching_charge) if self.stitching_charge else 0
		fitting_charge = float(self.fitting_charge) if self.fitting_charge else 0
		
		# Calculate total row amount
		self.amount = (
			self.fabric_amount +
			self.lining_amount +
			self.lead_rope_amount +
			self.track_rod_amount +
			stitching_charge +
			fitting_charge
		)
		
		# For Blinds: Calculate amount as square_feet × selection_rate + fitting_charge
		if self.product_type == "Blinds":
			# Reset amount to 0 first (since fabric_amount, lining_amount, etc. are not used for Blinds)
			self.amount = 0
			
			# Add selection amount (square_feet × rate) if selection has rate
			if self.selection and self.square_feet:
				# Get item rate from Item Price table first, fallback to standard_rate
				try:
					# Try to get price from Item Price table (selling prices)
					item_price = frappe.db.get_value("Item Price", 
						{"item_code": self.selection, "selling": 1}, 
						"price_list_rate",
						order_by="modified desc"
					)
					
					if item_price:
						rate = float(item_price) or 0
					else:
						# Fallback to standard_rate from Item table
						rate = frappe.db.get_value("Item", self.selection, "standard_rate") or 0
					
					if rate and self.square_feet:
						# For Blinds: amount = square_feet × rate
						self.amount += float(self.square_feet) * float(rate)
				except frappe.DoesNotExistError:
					# Item doesn't exist, skip
					pass
				except Exception as e:
					# Log other errors but don't fail validation
					frappe.log_error(f"Error fetching item rate for {self.selection}: {str(e)}")
			
			# Add fitting_charge to the total amount
			self.amount += fitting_charge

