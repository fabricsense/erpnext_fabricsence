# Fabric Sense - Project Overview

## Executive Summary

**Fabric Sense** is a comprehensive ERP solution built on Frappe/ERPNext for a fabric and curtain retail business. The system manages the complete sales lifecycle from customer inquiry to final payment, supporting two distinct business models:

1. **Raw Fabric Sales** - Selling fabric materials by measurement
2. **Stitched Curtains** - Custom-made curtains with tailoring services

## Business Context

Fabric Sense operates a showroom where customers can:
- Purchase fabric materials (curtains, blinds, accessories) by measurement
- Order custom-stitched curtains with professional tailoring services

The system handles multi-channel customer inquiries (walk-in, WhatsApp, phone) and manages the entire order fulfillment process including inventory, purchasing, tailoring, invoicing, and payments.

## Key Features

### 1. Customer Management
- **Lead Capture**: Record customer inquiries from multiple channels
- **Lead Conversion**: Convert qualified leads to customers
- **Project Tracking**: Track custom tailoring projects per customer

### 2. Measurement & Estimation
- **Measurement Sheet**: Comprehensive measurement recording system
  - Window Curtains (with patterns, layers, fabric types)
  - Roman Blinds (with square footage calculations)
  - Blinds (with area calculations)
  - Tracks/Rods (with design options)
- **Multi-Product Support**: Multiple window treatments per area
- **Automatic Calculations**: Fabric quantity and pricing auto-calculation
- **Customer Approval Workflow**: Send measurements for customer review

### 3. Sales Order Management
- **Estimation to Order**: Convert approved measurements to sales orders
- **Manager Approval Workflow**: Two-tier approval system
- **Customer Notifications**: WhatsApp/Email notifications on approval
- **Order Modifications**: Handle additional items and damaged replacements

### 4. Inventory & Procurement
- **Stock Availability Check**: Real-time inventory verification
- **Material Request Types**:
  - Issue Purpose (in-stock items)
  - Purchase Purpose (on-order items)
- **Manager Approval**: Required for multiple material requests
- **Purchase Orders**: Automated PO generation to vendors
- **Vendor Notifications**: WhatsApp/Email alerts to suppliers
- **Stock Updates**: Automatic inventory adjustments

### 5. Tailoring Management (Case II)
- **Tailoring Sheet**: Copy of measurement sheet with adjustments
- **Tailor Assignment**: Assign tailors with job cards
- **Job Tracking**:
  - Start/End dates
  - Automatic status updates (Started/Ended)
  - Tailoring charges and travel costs
- **Material Consumption**: Stock updates at job start
- **Payment Tracking**: Monitor tailor payments

### 6. Invoicing & Delivery
- **Sales Invoice**: Generate invoices from sales orders
- **Customer Notifications**: WhatsApp/Email invoice delivery
- **Order Ready Alerts**: Notify customers when ready
- **Delivery Notes**: Generate and send delivery documentation

### 7. Payment Processing
- **Flexible Payment Options**:
  - With discount
  - Without discount
- **Manager Approval**: Required for all payments
- **Discount Approval**: Additional approval for discounted payments
- **Account Posting**: Automatic accounting entries

### 8. SKU Management
- **Automatic SKU Generation**: Format: `CATEGORY-VENDOR-RUNNINGNUMBER`
- **Sequential Numbering**: Auto-incrementing unique identifiers
- **Inventory Tracking**: Use SKUs across all documents

## User Roles

### Salesperson
- Create and manage leads
- Record measurements
- Create sales orders
- Generate material requests
- Create invoices and delivery notes
- Process payments (pending manager approval)
- Manage customer communications

### Manager
- Approve sales orders
- Approve material requests (for multiple requests)
- Approve payments and discounts
- Oversee project progress
- Review financial transactions

## Business Workflows

### Case I: Raw Fabric Sales

```
Customer Inquiry → Lead Creation → Lead to Customer Conversion
    ↓
Measurement Recording → Customer Approval
    ↓
Sales Order Creation → Manager Approval → Customer Notification
    ↓
Stock Check → Material Request (Issue/Purchase)
    ↓
[If Purchase] → Purchase Order → Vendor Notification → Purchase Receipt
    ↓
Sales Invoice → Customer Notification
    ↓
Delivery Note → Customer Notification
    ↓
Payment Entry → Manager Approval → Account Posting
```

### Case II: Stitched Curtains

```
Customer Inquiry → Lead Creation → Lead to Customer + Project
    ↓
Measurement (Direct/Tailor Visit) → Customer Approval
    ↓
Sales Order → Manager Approval → Customer Notification
    ↓
Tailoring Sheet Creation (with Adjustments)
    ↓
Material Request → [If Purchase] → Purchase Order → Vendor Notification
    ↓
Tailor Assignment → Job Card Creation → Tailor Notification
    ↓
Tailoring Start → Stock Update (Material Consumption)
    ↓
Tailoring Complete → Cost Calculation → Tailor Payment
    ↓
Sales Invoice → Customer Notification
    ↓
Order Ready Notification
    ↓
Delivery Note → Customer Notification
    ↓
Payment Entry → Manager Approval → Account Posting
```

## Key Business Rules

### Approval Requirements
1. **Sales Orders**: Manager approval required before proceeding
2. **Multiple Material Requests**: Manager approval needed for repeat requests
3. **Payments**: Manager approval mandatory for all payments
4. **Discounts**: Additional manager approval for discounted payments

### Notification Triggers
1. **Sales Order Approval**: Notify customer via WhatsApp/Email
2. **Purchase Order Creation**: Notify vendor via WhatsApp/Email
3. **Sales Invoice**: Notify customer via WhatsApp/Email
4. **Order Ready**: Notify customer via WhatsApp/Email
5. **Delivery Note**: Notify customer via WhatsApp/Email
6. **Tailor Assignment**: Notify tailor via WhatsApp

### Stock Management
1. **Material Request (Issue)**: For in-stock items
2. **Material Request (Purchase)**: For items to be ordered
3. **Tailoring Start**: Immediate stock consumption
4. **Delivery**: Stock update for non-tailoring items

### Special Scenarios
1. **Additional Items**: Update sales order, create material request, require manager approval
2. **Damaged Items**: Create material request without updating sales order, require manager approval
3. **Measurement Adjustments**: Tailoring sheet allows corrections to original measurements

## Technical Architecture

### Platform
- **Framework**: Frappe Framework
- **ERP**: ERPNext
- **Language**: Python (Backend), JavaScript (Frontend)
- **Database**: MariaDB

### Integrations
- **WhatsApp API**: Customer and vendor notifications
- **Email**: Automated email notifications
- **Accounting**: Integration with ERPNext Chart of Accounts

## Implementation Phases

### Phase 1: Core Setup
- User roles and permissions
- Basic DocTypes (Lead, Customer, Sales Order)
- SKU generation system

### Phase 2: Measurement System
- Measurement Sheet DocType
- Calculation formulas
- Multi-product support

### Phase 3: Inventory & Procurement
- Material Request workflows
- Purchase Order automation
- Stock management

### Phase 4: Tailoring Module
- Tailoring Sheet DocType
- Job Card system
- Tailor management

### Phase 5: Approvals & Notifications
- Manager approval workflows
- WhatsApp integration
- Email notifications

### Phase 6: Payment & Accounting
- Payment entry workflows
- Discount approval system
- Accounting integration

## Document Structure

This documentation is organized as follows:

1. **overview.md** (this document) - High-level project overview
2. **case-i-implementation.md** - Detailed implementation guide for raw fabric sales
3. **case-ii-implementation.md** - Detailed implementation guide for stitched curtains
4. **measurement-sheet-guide.md** - Comprehensive measurement sheet implementation
5. **technical-implementation.md** - Technical specifications and code guidelines
6. **workflow-diagrams.md** - Visual workflow representations
7. **api-integration.md** - WhatsApp and Email integration guide
8. **user-manual.md** - End-user documentation

## Getting Started

For developers implementing this system:
1. Review this overview to understand the business context
2. Read the relevant case implementation guide (Case I or Case II)
3. Follow the technical implementation guide for coding standards
4. Refer to specific feature guides as needed

For business users:
1. Review this overview to understand system capabilities
2. Refer to the user manual for step-by-step instructions
3. Contact your system administrator for access and training


