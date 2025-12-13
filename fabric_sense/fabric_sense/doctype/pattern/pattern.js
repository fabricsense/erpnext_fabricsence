frappe.ui.form.on("Pattern", {
	onload(frm) {
		frm.set_query("item_group", function() {
			return {
				filters: [
					['Item Group', 'parent_item_group', '=', 'Stitching']
				]
			};
		});
	},

	refresh(frm) {

	},
});
