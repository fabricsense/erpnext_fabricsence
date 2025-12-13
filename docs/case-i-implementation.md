# Case I: Raw Fabric Sales - Implementation Guide

## Overview

This guide provides detailed implementation instructions for the **Raw Fabric Sales** workflow, where customers purchase fabric materials (curtains, blinds, accessories) by measurement without tailoring services.

---

## Implementation Sections

### 1. Lead Management
- Lead creation from multiple channels
- Lead to Customer conversion
- Custom fields and validations

### 2. Measurement Sheet System
- Multi-product measurement recording
- Automatic calculations for quantities and amounts
- Customer approval workflow

### 3. Sales Order Management
- Convert measurement sheet to sales order
- Manager approval workflow
- Customer notifications

### 4. Material Request & Procurement
- Stock availability checking
- Material Request (Issue/Purchase)
- Additional material request approval
- Purchase Order generation
- Vendor notifications

### 5. Invoicing & Delivery
- Sales Invoice generation
- Order ready notifications
- Delivery Note creation
- Customer notifications

### 6. Payment Processing
- Payment entry with manager approval
- Discount approval workflow
- Account posting

### 7. SKU Management
- Automatic SKU generation
- Format: CATEGORY-VENDOR-RUNNINGNUMBER

### 8. Special Scenarios
- Additional items handling
- Damaged item replacement

---


## Quick Reference

### Key DocTypes
1. **Lead** (Standard + Custom Fields)
2. **Customer** (Standard)
3. **Estimation** (Custom)
4. **Measurement Sheet Item** (Custom Child Table)
5. **Sales Order** (Standard + Custom Fields)
6. **Material Request** (Standard + Custom Fields)
7. **Purchase Order** (Standard)
8. **Sales Invoice** (Standard)
9. **Delivery Note** (Standard)
10. **Payment Entry** (Standard + Custom Fields)

### Key Workflows
1. Lead → Customer
2. Measurement Sheet → Sales Order
3. Sales Order Approval (Manager)
4. Material Request Approval (for additional requests)
5. Payment Approval (Manager + Discount)

### Key Notifications
1. Sales Order Approval → Customer (WhatsApp/Email)
2. Purchase Order → Vendor (WhatsApp/Email)
3. Sales Invoice → Customer (WhatsApp/Email)
4. Order Ready → Customer (WhatsApp/Email)
5. Delivery Note → Customer (WhatsApp/Email)

---

## Implementation Checklist

- [ ] Setup user roles (Salesperson, Manager)
- [ ] Add custom fields to standard DocTypes
- [ ] Implement calculation logic
- [ ] Setup approval workflows
- [ ] Configure notification integrations
- [ ] Implement SKU generation
- [ ] Test complete workflow end-to-end
- [ ] Setup permissions and access controls
- [ ] Create user training materials

---

See `technical-implementation.md` for detailed code and configuration.
