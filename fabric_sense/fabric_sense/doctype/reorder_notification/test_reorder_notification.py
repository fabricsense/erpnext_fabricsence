# Copyright (c) 2025, innogenio and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from fabric_sense.fabric_sense.py.reorder_monitoring import (
    get_reorder_level,
    get_current_stock_balance,
    create_reorder_notification
)


class TestReorderNotification(FrappeTestCase):
    def setUp(self):
        """Set up test data"""
        # Create test item if it doesn't exist
        if not frappe.db.exists("Item", "TEST-REORDER-ITEM"):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "TEST-REORDER-ITEM",
                "item_name": "Test Reorder Item",
                "item_group": "All Item Groups",
                "stock_uom": "Nos",
                "is_stock_item": 1
            })
            item.insert(ignore_permissions=True)
            
        # Create test warehouse if it doesn't exist
        if not frappe.db.exists("Warehouse", "TEST-WAREHOUSE"):
            warehouse = frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": "Test Warehouse",
                "company": frappe.defaults.get_global_default("company") or "Test Company"
            })
            warehouse.insert(ignore_permissions=True)
    
    def test_get_reorder_level(self):
        """Test getting reorder level for item-warehouse combination"""
        # This will return None if no reorder level is set
        reorder_level = get_reorder_level("TEST-REORDER-ITEM", "TEST-WAREHOUSE")
        # Should be None initially as no reorder level is set
        self.assertIsNone(reorder_level)
    
    def test_get_current_stock_balance(self):
        """Test getting current stock balance"""
        stock_balance = get_current_stock_balance("TEST-REORDER-ITEM", "TEST-WAREHOUSE")
        # Should return a float value (could be 0)
        self.assertIsInstance(stock_balance, float)
    
    def test_create_reorder_notification(self):
        """Test creating reorder notification"""
        # Clean up any existing notifications
        frappe.db.delete("Reorder Notification", {
            "item": "TEST-REORDER-ITEM",
            "warehouse": "TEST-WAREHOUSE"
        })
        
        # Create a reorder notification
        create_reorder_notification(
            item_code="TEST-REORDER-ITEM",
            warehouse="TEST-WAREHOUSE", 
            reorder_level=10.0,
            current_quantity=5.0
        )
        
        # Check if notification was created
        notification = frappe.db.exists("Reorder Notification", {
            "item": "TEST-REORDER-ITEM",
            "warehouse": "TEST-WAREHOUSE",
            "status": "Pending"
        })
        
        self.assertIsNotNone(notification)
        
        # Clean up
        if notification:
            frappe.delete_doc("Reorder Notification", notification, ignore_permissions=True)
    
    def tearDown(self):
        """Clean up test data"""
        # Clean up test notifications
        notifications = frappe.get_all("Reorder Notification", {
            "item": "TEST-REORDER-ITEM"
        })
        for notification in notifications:
            frappe.delete_doc("Reorder Notification", notification.name, ignore_permissions=True)
