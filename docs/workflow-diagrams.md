# Workflow Diagrams and Process Flows

## Overview

This document provides visual representations of all workflows in the Fabric Sense system.

---

## Case I: Raw Fabric Sales - Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CASE I: RAW FABRIC SALES                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│ Customer Inquiry │
│ (Walk-in/Phone/  │
│   WhatsApp)      │
└────────┬─────────┘
         │
         ▼
┌────────────────┐
│  Create Lead   │
│  - Name        │
│  - Contact     │
│  - Requirements│
└────────┬───────┘
         │
         ▼
┌─────────────────────┐
│ Convert to Customer │
└─────────┬───────────┘
          │
          ▼
┌──────────────────────────┐
│  Create Measurement      │
│  Sheet                   │
│  - Window Curtains       │
│  - Roman Blinds          │
│  - Blinds                │
│  - Tracks/Rods           │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Auto Calculate          │
│  - Quantities            │
│  - Amounts               │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Send for Customer       │
│  Approval                │
│  (WhatsApp/Email)        │
└──────────┬───────────────┘
           │
           ▼
      ┌────┴────┐
      │Approved?│
      └────┬────┘
           │
    ┌──────┴──────┐
    │             │
    NO            YES
    │             │
    ▼             ▼
┌────────┐   ┌──────────────────┐
│ Revise │   │ Create Sales     │
│ & Re-  │   │ Order            │
│ send   │   │  
└────────┘   └────────┬─────────┘
                      │
                      ▼
             ┌────────────────────┐
             │ Submit for Manager │
             │ Approval           │
             └────────┬───────────┘
                      │
                      ▼
                 ┌────┴────┐
                 │Approved?│
                 └────┬────┘
                      │
               ┌──────┴──────┐
               │             │
               NO            YES
               │             │
               ▼             ▼
          ┌────────┐   ┌──────────────────┐
          │ Reject │   │ Notify Customer  │
          │ & Send │   │ (WhatsApp/Email) │
          │ Back   │   └────────┬─────────┘
          └────────┘            │
                                ▼
                       ┌────────────────────┐
                       │ Check Stock        │
                       │ Availability       │
                       └────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
         ┌──────────────────┐    ┌──────────────────┐
         │ In Stock Items   │    │ Out of Stock     │
         │                  │    │ Items            │
         └────────┬─────────┘    └────────┬─────────┘
                  │                       │
                  ▼                       ▼
         ┌──────────────────┐    ┌──────────────────┐
         │ Material Request │    │ Material Request │
         │ (Issue)          │    │ (Purchase)       │
         └────────┬─────────┘    └────────┬─────────┘
                  │                       │
                  │                       ▼
                  │              ┌──────────────────┐
                  │              │ Create Purchase  │
                  │              │ Order            │
                  │              └────────┬─────────┘
                  │                       │
                  │                       ▼
                  │              ┌──────────────────┐
                  │              │ Notify Vendor    │
                  │              │ (WhatsApp/Email) │
                  │              └────────┬─────────┘
                  │                       │
                  │                       ▼
                  │              ┌──────────────────┐
                  │              │ Vendor Delivers  │
                  │              └────────┬─────────┘
                  │                       │
                  │                       ▼
                  │              ┌──────────────────┐
                  │              │ Purchase Receipt │
                  │              │ (Update Stock)   │
                  │              └────────┬─────────┘
                  │                       │
                  └───────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Create Sales       │
                     │ Invoice            │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Notify Customer    │
                     │ (WhatsApp/Email)   │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Order Ready        │
                     │ Notification       │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Create Delivery    │
                     │ Note               │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Notify Customer    │
                     │ (WhatsApp/Email)   │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Create Payment     │
                     │ Entry              │
                     └────────┬───────────┘
                              │
                              ▼
                        ┌─────┴─────┐
                        │ Discount? │
                        └─────┬─────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    YES                 NO
                    │                   │
                    ▼                   ▼
         ┌──────────────────┐  ┌──────────────────┐
         │ Manager Approves │  │ Manager Approves │
         │ Discount         │  │ Payment          │
         └────────┬─────────┘  └────────┬─────────┘
                  │                     │
                  ▼                     │
         ┌──────────────────┐          │
         │ Manager Approves │          │
         │ Payment          │          │
         └────────┬─────────┘          │
                  │                     │
                  └──────────┬──────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │ Post to Accounts   │
                    └────────┬───────────┘
                             │
                             ▼
                    ┌────────────────────┐
                    │ Order Complete     │
                    └────────────────────┘
```

---

## Case II: Stitched Curtains - Complete Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                  CASE II: STITCHED CURTAINS                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│ Customer Inquiry │
└────────┬─────────┘
         │
         ▼
┌────────────────┐
│  Create Lead   │
└────────┬───────┘
         │
         ▼
┌──────────────────────────┐
│ Convert to Customer      │
│ + Create Project         │
└──────────┬───────────────┘
           │
           ▼
      ┌────┴────────────┐
      │ Measurement     │
      │ Method?         │
      └────┬────────────┘
           │
    ┌──────┴──────┐
    │             │
    Direct        Tailor Visit
    │             │
    ▼             ▼
┌────────┐   ┌──────────────────┐
│Customer│   │ Assign Tailor    │
│Provides│   │ + Visit Charge   │
│Measure-│   └────────┬─────────┘
│ments   │            │
└────┬───┘            ▼
     │       ┌──────────────────┐
     │       │ Notify Tailor    │
     │       │ (WhatsApp)       │
     │       └────────┬─────────┘
     │                │
     │                ▼
     │       ┌──────────────────┐
     │       │ Tailor Site      │
     │       │ Visit            │
     │       └────────┬─────────┘
     │                │
     └────────┬───────┘
              │
              ▼
┌──────────────────────────┐
│ Create Measurement       │
│ Sheet                    │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Send for Customer        │
│ Approval                 │
└──────────┬───────────────┘
           │
           ▼
      ┌────┴────┐
      │Approved?│
      └────┬────┘
           │
    ┌──────┴──────┐
    │             │
    NO            YES
    │             │
    ▼             ▼
┌────────┐   ┌──────────────────┐
│ Revise │   │ Mark Measurement │
│        │   │ Task Complete    │
└────────┘   └────────┬─────────┘
                      │
                      ▼
             ┌────────────────────┐
             │ Create Sales Order │
             └────────┬───────────┘
                      │
                      ▼
             ┌────────────────────┐
             │ Manager Approval   │
             └────────┬───────────┘
                      │
                      ▼
                 ┌────┴────┐
                 │Approved?│
                 └────┬────┘
                      │
               ┌──────┴──────┐
               │             │
               NO            YES
               │             │
               ▼             ▼
          ┌────────┐   ┌──────────────────┐
          │ Reject │   │ Notify Customer  │
          └────────┘   └────────┬─────────┘
                                │
                                ▼
                       ┌────────────────────┐
                       │ Create Tailoring   │
                       │ Sheet              │
                       │ (Copy + Adjust)    │
                       └────────┬───────────┘
                                │
                                ▼
                       ┌────────────────────┐
                       │ Add Adjustments    │
                       │ (if needed)        │
                       └────────┬───────────┘
                                │
                                ▼
                       ┌────────────────────┐
                       │ Create Material    │
                       │ Request            │
                       └────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
         ┌──────────────────┐    ┌──────────────────┐
         │ Material Request │    │ Material Request │
         │ (Issue)          │    │ (Purchase)       │
         └────────┬─────────┘    └────────┬─────────┘
                  │                       │
                  │                       ▼
                  │              ┌──────────────────┐
                  │              │ Purchase Order   │
                  │              └────────┬─────────┘
                  │                       │
                  │                       ▼
                  │              ┌──────────────────┐
                  │              │ Notify Vendor    │
                  │              └────────┬─────────┘
                  │                       │
                  │                       ▼
                  │              ┌──────────────────┐
                  │              │ Purchase Receipt │
                  │              └────────┬─────────┘
                  │                       │
                  └───────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Create Tailoring   │
                     │ Job Card           │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Assign Tailor      │
                     │ - Name             │
                     │ - Charge           │
                     │ - Travel Charge    │
                     │ - Dates            │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Notify Tailor      │
                     │ (WhatsApp)         │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Start Date Reached │
                     │ Status: Started    │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Consume Materials  │
                     │ (Stock Entry)      │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Tailoring Work     │
                     │ In Progress        │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ End Date Reached   │
                     │ Status: Completed  │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Calculate Costs    │
                     │ - Tailoring Charge │
                     │ - Travel Charge    │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Create Tailor      │
                     │ Payment            │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Create Sales       │
                     │ Invoice            │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Notify Customer    │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Order Ready        │
                     │ Notification       │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Create Delivery    │
                     │ Note               │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Notify Customer    │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Payment Entry      │
                     │ + Manager Approval │
                     └────────┬───────────┘
                              │
                              ▼
                     ┌────────────────────┐
                     │ Order Complete     │
                     └────────────────────┘
```

---

## Approval Workflows

### Sales Order Approval Workflow

```
┌────────────────────────────────────────────────┐
│         SALES ORDER APPROVAL WORKFLOW          │
└────────────────────────────────────────────────┘

┌──────────────────┐
│ Salesperson      │
│ Creates SO       │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Status: Draft    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Salesperson      │
│ Submits for      │
│ Approval         │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│ Status: Pending      │
│ Manager Approval     │
└────────┬─────────────┘
         │
         ▼
┌──────────────────┐
│ Notify Manager   │
└────────┬─────────┘
         │
         ▼
    ┌────┴────────┐
    │   Manager   │
    │   Reviews   │
    └────┬────────┘
         │
    ┌────┴────┐
    │Decision?│
    └────┬────┘
         │
  ┌──────┴──────┐
  │             │
Reject        Approve
  │             │
  ▼             ▼
┌──────┐   ┌──────────────────┐
│Status│   │ Status: Approved │
│Reject│   └────────┬─────────┘
└──┬───┘            │
                   ▼
          ┌──────────────────┐
          │ Submit SO        │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Notify Customer  │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Proceed to       │
          │ Material Request │
          └──────────────────┘
   

```

---

### Payment Approval Workflow

```
┌────────────────────────────────────────────────┐
│         PAYMENT APPROVAL WORKFLOW              │
└────────────────────────────────────────────────┘

┌──────────────────┐
│ Salesperson      │
│ Creates Payment  │
│ Entry            │
└────────┬─────────┘
         │
         ▼
    ┌────┴────────┐
    │  Discount?  │
    └────┬────────┘
         │
  ┌──────┴──────┐
  │             │
  NO            YES
  │             │
  ▼             ▼
┌──────┐   ┌──────────────────┐
│Submit│   │ Enter Discount   │
│for   │   │ Amount & Reason  │
│Appro-│   └────────┬─────────┘
│val   │            │
└──┬───┘            ▼
   │       ┌──────────────────┐
   │       │ Submit for       │
   │       │ Approval         │
   │       └────────┬─────────┘
   │                │
   │                ▼
   │       ┌──────────────────┐
   │       │ Notify Manager   │
   │       │ (Discount        │
   │       │  Approval)       │
   │       └────────┬─────────┘
   │                │
   │                ▼
   │           ┌────┴────┐
   │           │Manager  │
   │           │Reviews  │
   │           │Discount │
   │           └────┬────┘
   │                │
   │         ┌──────┴──────┐
   │         │             │
   │       Reject        Approve
   │         │             │
   │         ▼             ▼
   │    ┌────────┐   ┌──────────┐
   │    │ Reject │   │ Discount │
   │    │ Payment│   │ Approved │
   │    └────────┘   └─────┬────┘
   │                       │
   └───────────┬───────────┘
               │
               ▼
      ┌──────────────────┐
      │ Notify Manager   │
      │ (Payment         │
      │  Approval)       │
      └────────┬─────────┘
               │
               ▼
          ┌────┴────┐
          │Manager  │
          │Reviews  │
          │Payment  │
          └────┬────┘
               │
        ┌──────┴──────┐
        │             │
      Reject        Approve
        │             │
        ▼             ▼
   ┌────────┐   ┌──────────────┐
   │ Reject │   │ Approve &    │
   │ Payment│   │ Submit       │
   └────────┘   └──────┬───────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Post to Accounts │
              └──────────────────┘
```

---

### Material Request Approval (Additional)

```
┌────────────────────────────────────────────────┐
│    ADDITIONAL MATERIAL REQUEST APPROVAL        │
└────────────────────────────────────────────────┘

┌──────────────────┐
│ Check if First   │
│ Material Request │
│ for Sales Order  │
└────────┬─────────┘
         │
    ┌────┴────┐
    │ First?  │
    └────┬────┘
         │
  ┌──────┴──────┐
  │             │
  YES           NO
  │             │
  ▼             ▼
┌──────┐   ┌──────────────────┐
│Create│   │ Mark as          │
│& Sub-│   │ Additional       │
│mit   │   │ Request          │
│Auto  │   └────────┬─────────┘
└──────┘            │
                    ▼
           ┌──────────────────┐
           │ Enter Reason:    │
           │ - Additional     │
           │   Items          │
           │ - Damaged        │
           │   Replacement    │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Submit for       │
           │ Manager Approval │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Notify Manager   │
           └────────┬─────────┘
                    │
                    ▼
               ┌────┴────┐
               │Manager  │
               │Reviews  │
               └────┬────┘
                    │
             ┌──────┴──────┐
             │             │
           Reject        Approve
             │             │
             ▼             ▼
        ┌────────┐   ┌──────────────┐
        │ Reject │   │ Approve &    │
        │ Request│   │ Submit       │
        └────────┘   └──────┬───────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Update Stock     │
                   │ (if Issue)       │
                   │ OR               │
                   │ Create PO        │
                   │ (if Purchase)    │
                   └──────────────────┘
```

---

## Notification Flow

```
┌────────────────────────────────────────────────┐
│           NOTIFICATION FLOW CHART              │
└────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│                 TRIGGER EVENTS                   │
└──────────────────────────────────────────────────┘


---

## Stock Management Flow

```
┌────────────────────────────────────────────────┐
│           STOCK MANAGEMENT FLOW                │
└────────────────────────────────────────────────┘

┌──────────────────┐
│ Sales Order      │
│ Created          │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Check Stock      │
│ Availability     │
└────────┬─────────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌────────────┐      ┌────────────┐
│ In Stock   │      │ Out of     │
│ Items      │      │ Stock      │
└─────┬──────┘      └─────┬──────┘
      │                   │
      ▼                   ▼
┌────────────┐      ┌────────────┐
│ Material   │      │ Material   │
│ Request    │      │ Request    │
│ (Issue)    │      │ (Purchase) │
└─────┬──────┘      └─────┬──────┘
      │                   │
      │                   ▼
      │            ┌────────────┐
      │            │ Purchase   │
      │            │ Order      │
      │            └─────┬──────┘
      │                  │
      │                  ▼
      │            ┌────────────┐
      │            │ Vendor     │
      │            │ Delivers   │
      │            └─────┬──────┘
      │                  │
      │                  ▼
      │            ┌────────────┐
      │            │ Purchase   │
      │            │ Receipt    │
      │            └─────┬──────┘
      │                  │
      └──────┬───────────┘
             │
             ▼
    ┌────────────────┐
    │ Stock Updated  │
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │ Ready for      │
    │ Delivery       │
    └────────────────┘

CASE II VARIATION:
    ┌────────────────┐
    │ Tailoring      │
    │ Job Starts     │
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │ Stock Entry    │
    │ (Material      │
    │  Consumption)  │
    └────────┬───────┘
             │
             ▼
    ┌────────────────┐
    │ Stock Updated  │
    │ Immediately    │
    └────────────────┘
```

---

## User Role Flow

```
┌────────────────────────────────────────────────┐
│              USER ROLE FLOW                    │
└────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│                 SALESPERSON                      │
└──────────────────────────────────────────────────┘

Can:
✓ Create Leads
✓ Convert Leads to Customers
✓ Create Measurement Sheets
✓ Create Sales Orders
✓ Submit SO for Approval
✓ Create Material Requests
✓ Create Purchase Orders
✓ Create Sales Invoices
✓ Create Delivery Notes
✓ Create Payment Entries
✓ Submit Payment for Approval

Cannot:
✗ Approve Sales Orders
✗ Approve Material Requests (additional)
✗ Approve Payments
✗ Approve Discounts

┌──────────────────────────────────────────────────┐
│                   MANAGER                        │
└──────────────────────────────────────────────────┘

Can:
✓ All Salesperson permissions
✓ Approve Sales Orders
✓ Reject Sales Orders
✓ Approve Additional Material Requests
✓ Approve Discounts
✓ Approve Payments
✓ View All Reports
✓ Manage System Settings

Special Powers:
★ Final approval authority
★ Override permissions
★ Access to financial data
```

---

## Data Flow Diagram

```
┌────────────────────────────────────────────────┐
│              DATA FLOW DIAGRAM                 │
└────────────────────────────────────────────────┘

┌─────────┐
│  Lead   │
└────┬────┘
     │
     ▼
┌──────────┐      ┌──────────────┐
│ Customer │◄─────│   Project    │ (Case II)
└────┬─────┘      └──────────────┘
     │
     ▼
┌──────────────────┐
│ Measurement      │
│ Sheet            │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐      ┌──────────────┐
│ Sales Order      │◄─────│  Tailoring   │ (Case II)
└────┬─────────────┘      │  Sheet       │
     │                    └──────────────┘
     │                           │
     ▼                           ▼
┌──────────────────┐      ┌──────────────┐
│ Material         │      │  Tailoring   │ (Case II)
│ Request          │      │  Job Card    │
└────┬─────────────┘      └──────────────┘
     │
     ▼
┌──────────────────┐
│ Purchase Order   │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Purchase Receipt │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Stock Entry      │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Sales Invoice    │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Delivery Note    │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ Payment Entry    │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│ GL Entry         │
│ (Accounts)       │
└──────────────────┘
```

---

## Summary

These workflow diagrams provide visual representations of:

1. **Complete Business Processes** - End-to-end workflows for both cases
2. **Approval Workflows** - Multi-level approval processes
3. **Notification Flows** - Communication triggers and channels
4. **Stock Management** - Inventory tracking and updates
5. **User Roles** - Permission and access control
6. **Data Flow** - Document relationships and dependencies


Use these diagrams as reference during:
- System design and development
- User training and onboarding
- Process documentation
- Troubleshooting and debugging
- System optimization

---

For implementation details, refer to `technical-implementation.md`
