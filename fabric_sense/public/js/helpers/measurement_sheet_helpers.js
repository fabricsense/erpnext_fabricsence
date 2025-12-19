frappe.provide("fabric_sense.measurement_sheet");

(function (ns) {
	const ITEM_GROUPS = {
		FABRIC: ["Main Fabric", "Sheer Fabric"],
		LINING: ["Basic Linings", "Heavy Linings"],
		LEAD_ROPE: "Lead Rope Items",
		TRACK_ROD: ["Tracks", "Rods"],
		BLINDS: "Blinds",
		STITCHING: "Stitching",
		FITTING: "Fitting",
	};

	const itemRateCache = {};
	const stockCache = {};
	let totalsCalculationTimer = null;
	let calculationTimer = null;
	let stockCheckTimer = null;

	ns.ITEM_GROUPS = ITEM_GROUPS;

	// Helper function to round up to nearest 0.5
	// Examples: 11.1 -> 11.5, 11.5 -> 11.5, 11.6 -> 12, 12 -> 12
	function roundToNearestHalf(value) {
		return Math.ceil(value * 2) / 2;
	}

	ns.clearItemRateCache = function clearItemRateCache() {
		Object.keys(itemRateCache).forEach((key) => delete itemRateCache[key]);
	};

	ns.clearStockCache = function clearStockCache() {
		Object.keys(stockCache).forEach((key) => delete stockCache[key]);
	};

	ns.apply_item_filters = function apply_item_filters(frm) {
		if (!frm) return;

		const filters = {
			selection: { item_group: ITEM_GROUPS.BLINDS },
		};

		// Apply standard filters
		Object.entries(filters).forEach(([field, filter]) => {
			frm.set_query(field, "measurement_details", function() {
				return { filters: [filter] };
			});
		});

		// Special handling for fabric_selected to include all items under Window Furnishings parent group
		frm.set_query("fabric_selected", "measurement_details", function () {
			return {
				query: "fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.get_fabric_items",
			};
		});

		// Special handling for lining to include all items under Linings parent group
		frm.set_query("lining", "measurement_details", function () {
			return {
				query: "fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.get_lining_items_by_parent",
			};
		});

		// Special handling for track_rod to include all items under Tracks & Rods parent group
		frm.set_query("track_rod", "measurement_details", function () {
			return {
				query: "fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.get_track_rod_items",
			};
		});

		// Special handling for lead_rope to include all items under Stitching Accessories parent group
		frm.set_query("lead_rope", "measurement_details", function () {
			return {
				query: "fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.get_lead_rope_items",
			};
		});

		// Special handling for stitching_pattern to include all items under Stitching parent group
		frm.set_query("stitching_pattern", "measurement_details", function () {
			return {
				query: "fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.get_stitching_items",
			};
		});

		// Special handling for fitting_type to include all items under Labour parent group
		frm.set_query("fitting_type", "measurement_details", function () {
			return {
				query: "fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.get_fitting_items",
			};
		});
	};

	ns.setup_custom_actions = function setup_custom_actions(frm) {
		if (!frm || frm.is_new()) return;
		frm.add_custom_button(__("Check Stock Availability"), () =>
			ns.check_all_stock_availability(frm)
		);
	};

	// Constants
	const STATUS_APPROVED = "Approved";

	// Add this to your measurement_sheet_helpers.js file

	ns.create_sales_order_from_measurement_sheet = function (frm) {
		// Only show button if document is saved and approved
		if (!frm || frm.is_new() || frm.doc.status !== "Approved") {
			return;
		}

		frm.add_custom_button(
			__("Create Sales Order"),
			function () {
				frappe.call({
					method: "fabric_sense.fabric_sense.doctype.measurement_sheet.measurement_sheet.get_sales_order_data_from_measurement_sheet",
					args: { measurement_sheet_name: frm.doc.name },
					freeze: true,
					freeze_message: __("Preparing Sales Order data..."),
					callback: function (r) {
						if (!r.message) {
							frappe.msgprint({
								title: __("Error"),
								message: __("Failed to load Sales Order data"),
								indicator: "red",
							});
							return;
						}

						const data = r.message;

						// Create new Sales Order
						frappe.model.with_doctype("Sales Order", function () {
							let so = frappe.model.get_new_doc("Sales Order");
							so.customer = data.customer;
							so.company = data.company || frappe.defaults.get_default("Company");
							so.transaction_date =
								data.transaction_date || frappe.datetime.get_today();
							so.measurement_sheet = frm.doc.name;

							// Add project if available
							if (data.project) {
								so.project = data.project;
							}

							// Navigate to the new Sales Order
							frappe.set_route("Form", "Sales Order", so.name);

							// Add items after form is loaded to ensure field triggers work
							setTimeout(function () {
								if (
									cur_frm &&
									cur_frm.doctype === "Sales Order" &&
									cur_frm.doc.name === so.name
								) {
									// Add items one by one to trigger all the field triggers
									(data.items || []).forEach(function (item, index) {
										let row = frappe.model.add_child(cur_frm.doc, "items");
										frappe.model
											.set_value(
												row.doctype,
												row.name,
												"item_code",
												item.item_code
											)
											.then(() => {
												frappe.model.set_value(
													row.doctype,
													row.name,
													"qty",
													item.qty || 1
												);
												frappe.model.set_value(
													row.doctype,
													row.name,
													"rate",
													item.rate || 0
												);

												// Set UOM if available
												if (item.uom) {
													frappe.model.set_value(
														row.doctype,
														row.name,
														"uom",
														item.uom
													);
												}

												// Set description if available
												if (item.description) {
													frappe.model.set_value(
														row.doctype,
														row.name,
														"description",
														item.description
													);
												}
											});
									});

									// Refresh the items table after adding all items
									setTimeout(() => {
										if (cur_frm) {
											cur_frm.refresh_field("items");
											cur_frm.calculate_taxes_and_totals();
										}
									}, 500);
								}
							}, 500);
						});
					},
					error: function (r) {
						frappe.msgprint({
							title: __("Error"),
							message: r.message || __("Error creating Sales Order"),
							indicator: "red",
						});
					},
				});
			},
			__("Create")
		);

		frm.add_custom_button(
			__("Tailoring Sheet"),
			function () {
				frappe.new_doc("Tailoring Sheet", {
					measurement_sheet: frm.doc.name,
					// customer: frm.doc.customer,
					// customer_name: frm.doc.customer_name
				});
			},
			__("Create")
		);
	};

	ns.calculate_totals = function calculate_totals(frm) {
		if (!frm || !frm.doc) return;
		if (totalsCalculationTimer) {
			clearTimeout(totalsCalculationTimer);
		}
		totalsCalculationTimer = setTimeout(() => perform_calculate_totals(frm), 50);
	};

	function perform_calculate_totals(frm) {
		if (!frm.doc.measurement_details || frm.doc.measurement_details.length === 0) {
			const visiting_charge = parseFloat(frm.doc.visiting_charge) || 0;
			frm.set_value("total_amount", visiting_charge);
			return;
		}

		const visiting_charge = parseFloat(frm.doc.visiting_charge) || 0;
		const total_amount = (frm.doc.measurement_details || []).reduce((acc, row) => {
			return acc + (parseFloat(row.amount) || 0);
		}, 0);
		frm.set_value("total_amount", total_amount + visiting_charge);
	}

	ns.batch_calculate_row = function batch_calculate_row(frm, cdt, cdn) {
		if (calculationTimer) {
			clearTimeout(calculationTimer);
		}

		calculationTimer = setTimeout(async () => {
			const row = locals[cdt][cdn];
			calculate_square_feet(row);
			await ns.calculate_fabric_qty(frm, cdt, cdn);

			if (row.product_type === "Window Curtains") {
				if (row.panels !== null && row.panels !== undefined && row.panels !== "") {
					await ns.calculate_lead_rope_qty(frm, cdt, cdn);
				}
				await ns.calculate_track_rod_qty(frm, cdt, cdn);
			} else if (row.product_type === "Tracks/Rods") {
				await ns.calculate_track_rod_qty(frm, cdt, cdn);
			}

			await ns.calculate_row_amounts(frm, cdt, cdn);
		}, 50);
	};

	function calculate_square_feet(row) {
		if (!row) return;
		if (row.product_type === "Roman Blinds") {
			const calculated_sqft = row.width && row.height ? (row.width * row.height) / 144 : 0;
			// Round to nearest 0.5
			row.square_feet = roundToNearestHalf(calculated_sqft);
		} else if (row.product_type === "Blinds") {
			const calculated_sqft =
				row.width && row.height ? ((row.height + 6) * row.width) / 144 : 0;
			// Round to nearest 0.5
			row.square_feet = roundToNearestHalf(calculated_sqft);
		} else {
			row.square_feet = 0;
		}
	}

	ns.reset_fields_for_product_type = function reset_fields_for_product_type(row) {
		if (!row) return;

		if (row.product_type !== "Window Curtains") {
			row.lead_rope = "";
			row.lead_rope_qty = 0;
			row.lead_rope_rate = 0;
			row.lead_rope_amount = 0;
			row.track_rod = "";
			row.track_rod_qty = 0;
			row.track_rod_rate = 0;
			row.track_rod_amount = 0;
		}

		if (row.product_type !== "Blinds") {
			row.selection = "";
			row.selection_rate = 0;
		}

		if (!["Window Curtains", "Roman Blinds"].includes(row.product_type)) {
			row.layer = "";
			row.pattern = "";
			// Don't set panels to 0 - leave it empty/null to prevent invalid default values
			row.panels = null;
			row.adjust = 0;
			row.fabric_selected = "";
			row.fabric_qty = 0;
			row.fabric_rate = 0;
			row.fabric_amount = 0;
			row.lining = "";
			row.lining_qty = 0;
			row.lining_rate = 0;
			row.lining_amount = 0;
			row.stitching_pattern = "";
			row.stitching_charge = 0;
		}

		if (row.product_type === "Tracks/Rods") {
			row.height = 0;
			row.fabric_selected = "";
			row.lining = "";
		}
	};

	/**
	 * Get price list from customer by following the chain:
	 * Customer → customer_group → default_price_list
	 *
	 * @param {string} customer - Customer name
	 * @returns {Promise<string|null>} Price list name or null if not found
	 */
	ns.get_price_list_from_customer = async function get_price_list_from_customer(customer) {
		if (!customer) return null;

		try {
			// Get customer_group from Customer
			const customer_data = await frappe.db.get_value(
				"Customer",
				customer,
				"customer_group"
			);
			if (
				!customer_data ||
				!customer_data.message ||
				!customer_data.message.customer_group
			) {
				return null;
			}

			const customer_group = customer_data.message.customer_group;

			// Get default_price_list from Customer Group
			const customer_group_data = await frappe.db.get_value(
				"Customer Group",
				customer_group,
				"default_price_list"
			);
			if (
				!customer_group_data ||
				!customer_group_data.message ||
				!customer_group_data.message.default_price_list
			) {
				return null;
			}

			return customer_group_data.message.default_price_list;
		} catch (error) {
			console.error(`Error getting price list from customer ${customer}:`, error);
			return null;
		}
	};

	/**
	 * Get default selling price list from Selling Settings
	 *
	 * @returns {Promise<string|null>} Default selling price list name or null if not found
	 */
	ns.get_default_selling_price_list = async function get_default_selling_price_list() {
		try {
			const selling_settings = await frappe.db.get_value(
				"Selling Settings",
				"Selling Settings",
				"selling_price_list"
			);
			if (
				selling_settings &&
				selling_settings.message &&
				selling_settings.message.selling_price_list
			) {
				return selling_settings.message.selling_price_list;
			}
			return null;
		} catch (error) {
			console.error("Error getting default selling price list:", error);
			return null;
		}
	};

	ns.fetch_item_rate = async function fetch_item_rate(item_code, price_list = null, frm = null) {
		if (!item_code) return Promise.resolve(null);

		// If price_list is not provided but frm is available, try to derive it from customer
		if (!price_list && frm && frm.doc && frm.doc.customer) {
			price_list = await ns.get_price_list_from_customer(frm.doc.customer);
		}

		console.log(`[Item Selection] Selected Item: ${item_code}, Price List: ${price_list || 'None'}`);

		// Create cache key that includes both item_code and price_list
		const cacheKey = price_list ? `${item_code}::${price_list}` : `${item_code}::default`;

		// Only use cache for positive rates, never cache zero/null rates
		if (itemRateCache[cacheKey] !== undefined && itemRateCache[cacheKey] > 0) {
			console.log(`[Item Selection] Selection Rate (from cache): ${itemRateCache[cacheKey]}`);
			return Promise.resolve(itemRateCache[cacheKey]);
		}

		try {
			// First, try to get price from the specific price_list (if provided)
			if (price_list) {
				const prices = await frappe.db.get_list("Item Price", {
					filters: { item_code, selling: 1, price_list: price_list },
					fields: ["price_list_rate"],
					order_by: "modified desc",
					limit: 1,
				});

				if (prices && prices.length > 0 && prices[0].price_list_rate != null) {
					const rate = parseFloat(prices[0].price_list_rate);
					if (!isNaN(rate)) {
						// Only cache positive rates
						if (rate > 0) {
							itemRateCache[cacheKey] = rate;
						}
						console.log(`[Item Selection] Selection Rate (from customer price list '${price_list}'): ${rate}`);
						return rate;
					}
				}
			}

			// Fallback: Try to get price from default selling price list (from Selling Settings)
			const default_price_list = await ns.get_default_selling_price_list();
			console.log(`[Item Selection] Trying default price list: ${default_price_list || 'None'}`);
			
			if (default_price_list && default_price_list !== price_list) {
				const defaultPrices = await frappe.db.get_list("Item Price", {
					filters: { item_code, selling: 1, price_list: default_price_list },
					fields: ["price_list_rate"],
					order_by: "modified desc",
					limit: 1,
				});

				if (
					defaultPrices &&
					defaultPrices.length > 0 &&
					defaultPrices[0].price_list_rate != null
				) {
					const rate = parseFloat(defaultPrices[0].price_list_rate);
					if (!isNaN(rate)) {
						// Only cache positive rates
						if (rate > 0) {
							itemRateCache[cacheKey] = rate;
						}
						console.log(`[Item Selection] Selection Rate (from default price list '${default_price_list}'): ${rate}`);
						return rate;
					}
				}
			}

			// No price found in any price list - return 0
			itemRateCache[cacheKey] = 0;
			console.log(`[Item Selection] Selection Rate: 0 (no price found in any price list)`);
			return 0;
		} catch (error) {
			itemRateCache[cacheKey] = 0;
			console.log(`[Item Selection] Selection Rate: 0 (error occurred)`);
			return 0;
		}
	};

	ns.calculate_fabric_qty = async function calculate_fabric_qty(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row || !row.product_type) return;

		let qty = 0;
		if (row.product_type === "Window Curtains" || row.product_type === "Roman Blinds") {
			const height = parseFloat(row.height) || 0;
			const panels = parseFloat(row.panels) || 0;
			const adjust = parseFloat(row.adjust) || 0;
			qty = ((height + 16) * panels) / 38 + adjust;
		} else if (row.product_type === "Blinds") {
			qty = row.square_feet && row.square_feet > 0 ? row.square_feet : 0;
		}

		// Round to nearest 0.5 for display and calculations
		const rounded_qty = roundToNearestHalf(qty);
		await frappe.model.set_value(cdt, cdn, {
			fabric_qty: rounded_qty,
			lining_qty: rounded_qty,
		});
		if (frm && frm.refresh_field) {
			frm.refresh_field("measurement_details");
		}
		await ns.calculate_row_amounts(frm, cdt, cdn);

		// Check stock availability after fabric_qty is calculated
		if (row.fabric_selected) {
			// Debounce stock check to avoid too many queries
			if (stockCheckTimer) {
				clearTimeout(stockCheckTimer);
			}
			stockCheckTimer = setTimeout(async () => {
				const stock_result = await ns.check_fabric_stock_availability(frm, cdt, cdn);
				if (!stock_result.is_available) {
					ns.highlight_fabric_field(frm, cdt, cdn, true);
					ns.show_fabric_stock_warning(
						frm,
						cdt,
						cdn,
						stock_result.available_qty,
						stock_result.required_qty,
						stock_result.fabric_name
					);
				} else {
					ns.highlight_fabric_field(frm, cdt, cdn, false);
				}
			}, 300);
		}
	};

	ns.calculate_lead_rope_qty = async function calculate_lead_rope_qty(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		let qty = 0;

		if (row.product_type === "Window Curtains") {
			const panels = parseFloat(row.panels) || 0;
			qty = panels > 0 ? panels * 1.5 : 0;
		}

		// Round to nearest 0.5
		const rounded_lr_qty = roundToNearestHalf(qty);
		await frappe.model.set_value(cdt, cdn, "lead_rope_qty", rounded_lr_qty);
		if (frm && frm.refresh_field) {
			frm.refresh_field("measurement_details");
		}
		await ns.calculate_row_amounts(frm, cdt, cdn);
	};

	ns.calculate_track_rod_qty = async function calculate_track_rod_qty(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		let qty = 0;

		if (
			(row.product_type === "Window Curtains" || row.product_type === "Tracks/Rods") &&
			row.width != null &&
			row.width !== ""
		) {
			const width = parseFloat(row.width) || 0;

			// Determine multiplier based on track_rod_type
			// Default to 2 (Double Glide) for backward compatibility
			let multiplier = 2;
			if (row.track_rod_type) {
				if (row.track_rod_type === "Single Glide") {
					multiplier = 1;
				} else if (row.track_rod_type === "Double Glide") {
					multiplier = 2;
				} else if (row.track_rod_type === "Triple Glide") {
					multiplier = 3;
				}
			}

			qty = width > 0 ? (width / 12) * multiplier : 0;
		}

		// Round to nearest 0.5
		const rounded_tr_qty = roundToNearestHalf(qty);
		await frappe.model.set_value(cdt, cdn, "track_rod_qty", rounded_tr_qty);
		if (frm && frm.refresh_field) {
			frm.refresh_field("measurement_details");
		}
		await ns.calculate_row_amounts(frm, cdt, cdn);
	};

	function compute_row_totals(row) {
		// Use rounded quantities (to nearest 0.5) for amount calculations
		const fabric_qty = roundToNearestHalf(parseFloat(row.fabric_qty) || 0);
		const lining_qty = roundToNearestHalf(parseFloat(row.lining_qty) || 0);
		// lead_rope_qty is already rounded when stored, use it directly to avoid precision issues
		const lead_rope_qty = parseFloat(row.lead_rope_qty) || 0;
		const track_rod_qty = roundToNearestHalf(parseFloat(row.track_rod_qty) || 0);

		const fabric_amount = fabric_qty * (parseFloat(row.fabric_rate) || 0);
		const lining_amount = lining_qty * (parseFloat(row.lining_rate) || 0);
		const lead_rope_amount = lead_rope_qty * (parseFloat(row.lead_rope_rate) || 0);
		const track_rod_amount = track_rod_qty * (parseFloat(row.track_rod_rate) || 0);
		const stitching_charge = parseFloat(row.stitching_charge) || 0;
		const fitting_charge = parseFloat(row.fitting_charge) || 0;

		const subtotal =
			fabric_amount +
			lining_amount +
			lead_rope_amount +
			track_rod_amount +
			stitching_charge +
			fitting_charge;
		return {
			fabric_amount,
			lining_amount,
			lead_rope_amount,
			track_rod_amount,
			total: subtotal,
		};
	}

	ns.calculate_row_amounts = async function calculate_row_amounts(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row) return;

		// For Blinds: Use square_feet × base_rate + fitting_charge calculation
		if (row.product_type === "Blinds") {
			let blinds_amount = 0;
			if (row.selection && row.square_feet) {
				const rate = await ns.fetch_item_rate(row.selection, null, frm);
				const base_rate = rate ? parseFloat(rate) : 0;
				const square_feet = parseFloat(row.square_feet) || 0;
				const fitting_charge = parseFloat(row.fitting_charge) || 0;
				blinds_amount = square_feet * base_rate + fitting_charge;
			} else {
				// If no selection or square_feet, still include fitting_charge if present
				const fitting_charge = parseFloat(row.fitting_charge) || 0;
				blinds_amount = fitting_charge;
			}

			await frappe.model.set_value(cdt, cdn, {
				fabric_amount: 0,
				lining_amount: 0,
				lead_rope_amount: 0,
				track_rod_amount: 0,
				amount: blinds_amount,
			});

			if (frm && frm.refresh_field) {
				frm.refresh_field("measurement_details");
			}
			ns.calculate_totals(frm);
			return;
		}

		// For other product types: Use existing calculation
		const totals = compute_row_totals(row);

		// Handle selection surcharge for other product types if needed
		let selection_amount = 0;
		if (row.selection) {
			const rate = await ns.fetch_item_rate(row.selection, null, frm);
			selection_amount = rate ? parseFloat(rate) : 0;
		}

		await frappe.model.set_value(cdt, cdn, {
			fabric_amount: totals.fabric_amount,
			lining_amount: totals.lining_amount,
			lead_rope_amount: totals.lead_rope_amount,
			track_rod_amount: totals.track_rod_amount,
			amount: totals.total + selection_amount,
		});

		if (frm && frm.refresh_field) {
			frm.refresh_field("measurement_details");
		}
		ns.calculate_totals(frm);
	};

	/**
	 * Check stock availability for a single fabric item
	 * @param {Object} frm - Form object
	 * @param {string} cdt - Child doctype name
	 * @param {string} cdn - Child document name
	 * @returns {Promise<Object>} Object with is_available, available_qty, required_qty, fabric_name
	 */
	ns.check_fabric_stock_availability = async function check_fabric_stock_availability(
		frm,
		cdt,
		cdn
	) {
		const row = locals[cdt][cdn];
		if (!row || !row.fabric_selected) {
			return { is_available: true, available_qty: 0, required_qty: 0, fabric_name: null };
		}

		const fabric_code = row.fabric_selected;
		const required_qty = parseFloat(row.fabric_qty) || 0;

		// If quantity is not yet calculated, check if any stock exists
		if (required_qty === 0) {
			// Check cache first
			if (stockCache[fabric_code] !== undefined) {
				const cached_stock = stockCache[fabric_code];
				return {
					is_available: cached_stock > 0,
					available_qty: cached_stock,
					required_qty: 0,
					fabric_name: fabric_code,
				};
			}

			try {
				const bins = await frappe.db.get_list("Bin", {
					filters: { item_code: fabric_code },
					fields: ["item_code", "actual_qty"],
				});

				const total_stock = (bins || []).reduce(
					(sum, bin) => sum + (parseFloat(bin.actual_qty) || 0),
					0
				);
				stockCache[fabric_code] = total_stock;

				return {
					is_available: total_stock > 0,
					available_qty: total_stock,
					required_qty: 0,
					fabric_name: fabric_code,
				};
			} catch (error) {
				console.error(`Error checking stock for ${fabric_code}:`, error);
				return {
					is_available: true,
					available_qty: 0,
					required_qty: 0,
					fabric_name: fabric_code,
				};
			}
		}

		// Check cache first - use fabric_code as key since stock doesn't change based on required_qty
		if (stockCache[fabric_code] !== undefined) {
			const cached_stock = stockCache[fabric_code];
			return {
				is_available: cached_stock >= required_qty,
				available_qty: cached_stock,
				required_qty: required_qty,
				fabric_name: fabric_code,
			};
		}

		try {
			const bins = await frappe.db.get_list("Bin", {
				filters: { item_code: fabric_code },
				fields: ["item_code", "actual_qty"],
			});

			const total_stock = (bins || []).reduce(
				(sum, bin) => sum + (parseFloat(bin.actual_qty) || 0),
				0
			);
			const is_available = total_stock >= required_qty;

			// Cache the total stock for this fabric
			stockCache[fabric_code] = total_stock;

			return {
				is_available: is_available,
				available_qty: total_stock,
				required_qty: required_qty,
				fabric_name: fabric_code,
			};
		} catch (error) {
			console.error(`Error checking stock for ${fabric_code}:`, error);
			return {
				is_available: true,
				available_qty: 0,
				required_qty: required_qty,
				fabric_name: fabric_code,
			};
		}
	};

	/**
	 * Highlight or unhighlight the fabric_selected field based on stock availability
	 * @param {Object} frm - Form object
	 * @param {string} cdt - Child doctype name
	 * @param {string} cdn - Child document name
	 * @param {boolean} is_insufficient - Whether stock is insufficient
	 */
	ns.highlight_fabric_field = function highlight_fabric_field(frm, cdt, cdn, is_insufficient) {
		if (!frm || !frm.fields_dict || !frm.fields_dict.measurement_details) return;

		// Use setTimeout to ensure DOM is ready after field refresh
		setTimeout(() => {
			try {
				const grid = frm.fields_dict.measurement_details.grid;
				if (!grid) {
					console.warn("Grid not found for measurement_details");
					return;
				}

				const grid_row = grid.get_row(cdn);
				if (!grid_row) {
					console.warn("Grid row not found for cdn:", cdn);
					return;
				}

				// Try to get the field control using Frappe's grid API first
				let field_control = null;
				try {
					const field = grid.get_field(cdn, "fabric_selected");
					if (field && field.$wrapper) {
						field_control = field.$wrapper[0] || field.$wrapper;
					}
				} catch (e) {
					// Fallback to DOM query
				}

				// If Frappe API didn't work, try DOM selectors
				if (!field_control) {
					// Try multiple selectors to find the fabric_selected field
					field_control =
						grid_row.querySelector('[data-fieldname="fabric_selected"]') ||
						grid_row.querySelector('.link-field[data-fieldname="fabric_selected"]') ||
						grid_row.querySelector('td[data-fieldname="fabric_selected"]');

					if (!field_control) {
						// Try finding by input element and get its parent
						const input_field = grid_row.querySelector(
							'input[data-fieldname="fabric_selected"]'
						);
						if (input_field) {
							field_control =
								input_field.closest('[data-fieldname="fabric_selected"]') ||
								input_field.closest(".link-field") ||
								input_field.closest(".control-input-wrapper") ||
								input_field.closest("td") ||
								input_field.parentElement;
						}
					}
				}

				if (field_control) {
					if (is_insufficient) {
						field_control.classList.add("fabric-stock-warning");
						field_control.style.border = "2px solid #ef4444";
						field_control.style.backgroundColor = "#fef2f2";
						field_control.style.borderRadius = "4px";
						field_control.style.padding = "2px";

						// Also try to style the input element inside if it exists
						const input_elem =
							field_control.querySelector("input") ||
							field_control.querySelector(".link-value");
						if (input_elem) {
							input_elem.style.border = "1px solid #ef4444";
							input_elem.style.backgroundColor = "#fef2f2";
						}
					} else {
						field_control.classList.remove("fabric-stock-warning");
						field_control.style.border = "";
						field_control.style.backgroundColor = "";
						field_control.style.borderRadius = "";
						field_control.style.padding = "";

						// Remove styles from input element
						const input_elem =
							field_control.querySelector("input") ||
							field_control.querySelector(".link-value");
						if (input_elem) {
							input_elem.style.border = "";
							input_elem.style.backgroundColor = "";
						}
					}
				} else {
					console.warn("Could not find fabric_selected field element for highlighting");
				}
			} catch (error) {
				// Log error for debugging
				console.error("Error highlighting fabric field:", error);
			}
		}, 200); // Increased timeout to 200ms for better reliability
	};

	/**
	 * Show warning message for insufficient stock
	 * @param {Object} frm - Form object
	 * @param {string} cdt - Child doctype name
	 * @param {string} cdn - Child document name
	 * @param {number} available_qty - Available stock quantity
	 * @param {number} required_qty - Required stock quantity
	 * @param {string} fabric_name - Fabric item name
	 */
	ns.show_fabric_stock_warning = function show_fabric_stock_warning(
		frm,
		cdt,
		cdn,
		available_qty,
		required_qty,
		fabric_name
	) {
		const row = locals[cdt][cdn];
		const row_idx = row ? row.idx : "";

		let message;
		if (required_qty > 0) {
			message = __("Insufficient stock for {0}. Required: {1}, Available: {2}", [
				fabric_name,
				required_qty.toFixed(1),
				available_qty.toFixed(1),
			]);
		} else {
			message = __("No stock available for {0}", [fabric_name]);
		}

		if (row_idx) {
			message = __("Row {0}: {1}", [row_idx, message]);
		}

		frappe.show_alert(
			{
				message: message,
				indicator: "orange",
			},
			15
		);
	};

	ns.check_all_stock_availability = function check_all_stock_availability(frm) {
		if (!frm.doc.measurement_details || frm.doc.measurement_details.length === 0) {
			frappe.msgprint(__("No measurement details to check"));
			return;
		}

		const items_to_check = [];
		(frm.doc.measurement_details || []).forEach((row) => {
			if (row.fabric_selected && row.fabric_qty) {
				items_to_check.push({
					item: row.fabric_selected,
					qty: row.fabric_qty,
					row_idx: row.idx,
				});
			}
			if (row.lining && row.lining_qty) {
				items_to_check.push({ item: row.lining, qty: row.lining_qty, row_idx: row.idx });
			}
			if (row.lead_rope && row.lead_rope_qty) {
				items_to_check.push({
					item: row.lead_rope,
					qty: row.lead_rope_qty,
					row_idx: row.idx,
				});
			}
			if (row.track_rod && row.track_rod_qty) {
				items_to_check.push({
					item: row.track_rod,
					qty: row.track_rod_qty,
					row_idx: row.idx,
				});
			}
			if (row.selection) {
				items_to_check.push({ item: row.selection, qty: 1, row_idx: row.idx });
			}
		});

		if (items_to_check.length === 0) {
			frappe.msgprint(__("No items to check"));
			return;
		}

		const item_codes = [...new Set(items_to_check.map((i) => i.item))];
		frappe.db
			.get_list("Bin", {
				filters: { item_code: ["in", item_codes] },
				fields: ["item_code", "actual_qty"],
			})
			.then((bins) => {
				const stock_map = {};
				(bins || []).forEach((bin) => {
					if (!stock_map[bin.item_code]) {
						stock_map[bin.item_code] = 0;
					}
					stock_map[bin.item_code] += parseFloat(bin.actual_qty) || 0;
				});

				// Group items by item code and aggregate required quantities
				const item_totals = {};
				items_to_check.forEach((item_data) => {
					if (!item_totals[item_data.item]) {
						item_totals[item_data.item] = 0;
					}
					item_totals[item_data.item] += parseFloat(item_data.qty) || 0;
				});

				// Check stock against totals and calculate shortage
				const insufficient = [];
				Object.keys(item_totals).forEach((item_code) => {
					const total_required = item_totals[item_code];
					const available_qty = stock_map[item_code] || 0;
					if (available_qty < total_required) {
						const shortage = total_required - available_qty;
						insufficient.push({
							item: item_code,
							required: total_required,
							available: available_qty,
							shortage: shortage,
						});
					}
				});

				if (insufficient.length > 0) {
					let message = "<b>Insufficient Stock:</b><br><br>";
					insufficient.forEach((item) => {
						message += `${item.item} - Required: ${item.required}, Available: ${item.available}, Shortage: ${item.shortage}<br>`;
					});
					frappe.msgprint({ title: __("Stock Check"), message, indicator: "red" });
				} else {
					frappe.msgprint({
						title: __("Stock Check"),
						message: __("All items have sufficient stock"),
						indicator: "green",
					});
				}
			})
			.catch((error) => {
				frappe.msgprint({
					title: __("Error"),
					message: __("Error checking stock: {0}", [error.message]),
					indicator: "red",
				});
			});
	};

	/**
	 * Validate all mandatory fields before save
	 * Returns array of error objects with fieldname and message
	 */
	ns.validate_mandatory_fields = function validate_mandatory_fields(frm) {
		const errors = [];
		
		// Always required fields
		if (!frm.doc.measurement_method) {
			errors.push({
				fieldname: "measurement_method",
				label: "Measurement Method",
				message: "Measurement Method is required"
			});
		}
		
		// Conditionally required fields based on order_type
		// Project is only required when order_type is explicitly "Fitting"
		// If order_type is "Delivery", null, undefined, or empty, project is NOT required
		const order_type = frm.doc.order_type;
		
		// Debug: Log order_type value (remove after testing)
		// console.log("Order Type:", order_type, "Project:", frm.doc.project);
		
		// Only require project if order_type is explicitly "Fitting"
		// For "Delivery" or any other value (including null/undefined), project is NOT required
		if (order_type === "Fitting") {
			if (!frm.doc.project) {
				errors.push({
					fieldname: "project",
					label: "Project",
					message: "Project is required when Order Type is 'Fitting'"
				});
			}
		}
		// For "Delivery" or any other value, project is NOT required - no validation needed
		
		// Conditionally required fields based on measurement_method
		if (frm.doc.measurement_method === "Contractor Assigned") {
			if (!frm.doc.assigned_contractor) {
				errors.push({
					fieldname: "assigned_contractor",
					label: "Assigned Contractor",
					message: "Assigned Contractor is required when Measurement Method is 'Contractor Assigned'"
				});
			}
			
			if (!frm.doc.expected_measurement_date) {
				errors.push({
					fieldname: "expected_measurement_date",
					label: "Expected Measurement Date",
					message: "Expected Measurement Date is required when Measurement Method is 'Contractor Assigned'"
				});
			}
			
			// Visiting charge is required if site visit is required
			if (frm.doc.site_visit_required && (!frm.doc.visiting_charge || frm.doc.visiting_charge === 0)) {
				errors.push({
					fieldname: "visiting_charge",
					label: "Visiting Charge",
					message: "Visiting Charge is required when Site Visit Required is checked"
				});
			}
		}
		
		// Status-based requirements
		if (frm.doc.status === "Rejected" && !frm.doc.rejection_reason) {
			errors.push({
				fieldname: "rejection_reason",
				label: "Rejection Reason",
				message: "Rejection Reason is required when Status is 'Rejected'"
			});
		}
		
		return errors;
	};

	/**
	 * Highlight fields with errors (red border and error message)
	 */
	ns.highlight_field_errors = function highlight_field_errors(frm, errors) {
		errors.forEach((error) => {
			const field = frm.get_field(error.fieldname);
			if (field) {
				// Try multiple ways to get the field wrapper
				let $wrapper = null;
				if (field.$wrapper) {
					$wrapper = $(field.$wrapper);
				} else if (field.wrapper) {
					$wrapper = $(field.wrapper);
				} else if (field.df) {
					// Try to find by fieldname attribute
					$wrapper = $(`[data-fieldname="${error.fieldname}"]`);
				}
				
				if ($wrapper && $wrapper.length) {
					$wrapper.addClass("error");
					
					// Add error message below the field
					let $errorMsg = $wrapper.find(".field-error-message");
					if ($errorMsg.length === 0) {
						$errorMsg = $(`<div class="field-error-message text-danger" style="margin-top: 5px; font-size: 12px;">
							<i class="fa fa-exclamation-circle"></i> ${frappe.utils.escape_html(error.message)}
						</div>`);
						$wrapper.append($errorMsg);
					} else {
						$errorMsg.html(`<i class="fa fa-exclamation-circle"></i> ${frappe.utils.escape_html(error.message)}`);
					}
					
					// Add red border to input
					const $input = $wrapper.find("input, select, textarea, .control-input");
					if ($input && $input.length) {
						$input.css("border-color", "#e74c3c");
						$input.css("box-shadow", "0 0 0 0.2rem rgba(231, 76, 60, 0.25)");
					}
					
					// Also try to highlight the control input wrapper
					const $controlInput = $wrapper.find(".control-input-wrapper");
					if ($controlInput && $controlInput.length) {
						$controlInput.css("border-color", "#e74c3c");
					}
				}
			}
		});
	};

	/**
	 * Clear all field error highlights
	 */
	ns.clear_field_errors = function clear_field_errors(frm) {
		// Remove error classes and messages from all fields
		frm.fields.forEach((field) => {
			if (field && field.wrapper) {
				const $wrapper = $(field.wrapper || field.$wrapper);
				if ($wrapper && $wrapper.length) {
					$wrapper.removeClass("error");
					$wrapper.find(".field-error-message").remove();
					
					// Reset input styling
					const $input = $wrapper.find("input, select, textarea");
					if ($input && $input.length) {
						$input.css("border-color", "");
						$input.css("box-shadow", "");
					}
				}
			}
		});
	};

	/**
	 * Clear error highlight for a specific field
	 */
	ns.clear_field_error = function clear_field_error(frm, fieldname) {
		const field = frm.get_field(fieldname);
		if (field) {
			// Try multiple ways to get the field wrapper
			let $wrapper = null;
			if (field.$wrapper) {
				$wrapper = $(field.$wrapper);
			} else if (field.wrapper) {
				$wrapper = $(field.wrapper);
			} else {
				// Try to find by fieldname attribute
				$wrapper = $(`[data-fieldname="${fieldname}"]`);
			}
			
			if ($wrapper && $wrapper.length) {
				$wrapper.removeClass("error");
				$wrapper.find(".field-error-message").remove();
				
				// Reset input styling
				const $input = $wrapper.find("input, select, textarea, .control-input");
				if ($input && $input.length) {
					$input.css("border-color", "");
					$input.css("box-shadow", "");
				}
				
				// Reset control input wrapper
				const $controlInput = $wrapper.find(".control-input-wrapper");
				if ($controlInput && $controlInput.length) {
					$controlInput.css("border-color", "");
				}
			}
		}
	};

	/**
	 * Scroll to the first error field
	 */
	ns.scroll_to_first_error = function scroll_to_first_error(frm, errors) {
		if (errors.length === 0) return;
		
		const firstError = errors[0];
		const field = frm.get_field(firstError.fieldname);
		
		if (field) {
			// Try multiple ways to get the field wrapper
			let $wrapper = null;
			if (field.$wrapper) {
				$wrapper = $(field.$wrapper);
			} else if (field.wrapper) {
				$wrapper = $(field.wrapper);
			} else {
				// Try to find by fieldname attribute
				$wrapper = $(`[data-fieldname="${firstError.fieldname}"]`);
			}
			
			if ($wrapper && $wrapper.length) {
				// Scroll to field with smooth animation
				$wrapper[0].scrollIntoView({ 
					behavior: "smooth", 
					block: "center" 
				});
				
				// Focus on the input field after a short delay
				setTimeout(() => {
					const $input = $wrapper.find("input, select, textarea, .control-input").first();
					if ($input && $input.length) {
						$input.focus();
					}
				}, 300);
			}
		}
	};

	/**
	 * Show validation errors in a user-friendly way
	 */
	ns.show_validation_errors = function show_validation_errors(frm, errors) {
		if (errors.length === 0) return;
		
		// Build error message with field names
		let message = "<div style='text-align: left;'>";
		message += "<p style='margin-bottom: 10px;'><strong>Please fill in the following required fields:</strong></p>";
		message += "<ul style='margin-left: 20px; margin-bottom: 0;'>";
		
		errors.forEach((error) => {
			message += `<li style='margin-bottom: 5px;'><strong>${error.label}</strong>: ${error.message}</li>`;
		});
		
		// Show message with indicator
		frappe.msgprint({
			title: __("Missing Required Fields"),
			message: message,
			indicator: "red",
			alert: true
		});
	};
})(fabric_sense.measurement_sheet);
