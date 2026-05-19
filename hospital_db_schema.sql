-- ============================================================
--  HOSPITAL MANAGEMENT SYSTEM - MySQL Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS hospital_db;
USE hospital_db;

-- ─────────────────────────────────────────────
--  1. WARDS / ROOMS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wards (
    ward_id       INT AUTO_INCREMENT PRIMARY KEY,
    ward_name     VARCHAR(100) NOT NULL,
    ward_type     ENUM('General','ICU','Emergency','Pediatric','Maternity','Surgery','Orthopedic','Cardiology') NOT NULL,
    total_beds    INT NOT NULL DEFAULT 10,
    available_beds INT NOT NULL DEFAULT 10,
    floor_number  INT NOT NULL DEFAULT 1,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rooms (
    room_id       INT AUTO_INCREMENT PRIMARY KEY,
    ward_id       INT NOT NULL,
    room_number   VARCHAR(20) NOT NULL UNIQUE,
    room_type     ENUM('Single','Double','Triple','General') NOT NULL DEFAULT 'General',
    status        ENUM('Available','Occupied','Maintenance') NOT NULL DEFAULT 'Available',
    daily_charge  DECIMAL(10,2) NOT NULL DEFAULT 500.00,
    FOREIGN KEY (ward_id) REFERENCES wards(ward_id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  2. DOCTORS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id        INT AUTO_INCREMENT PRIMARY KEY,
    first_name       VARCHAR(50) NOT NULL,
    last_name        VARCHAR(50) NOT NULL,
    specialization   VARCHAR(100) NOT NULL,
    phone            VARCHAR(20) NOT NULL,
    email            VARCHAR(100) UNIQUE,
    qualification    VARCHAR(150),
    experience_years INT DEFAULT 0,
    schedule_days    VARCHAR(100) DEFAULT 'Mon-Fri',
    consultation_fee DECIMAL(10,2) DEFAULT 500.00,
    status           ENUM('Active','Inactive','On Leave') DEFAULT 'Active',
    joined_date      DATE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────────
--  3. PATIENTS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS patients (
    patient_id    INT AUTO_INCREMENT PRIMARY KEY,
    first_name    VARCHAR(50) NOT NULL,
    last_name     VARCHAR(50) NOT NULL,
    dob           DATE,
    gender        ENUM('Male','Female','Other') NOT NULL,
    blood_group   ENUM('A+','A-','B+','B-','AB+','AB-','O+','O-','Unknown') DEFAULT 'Unknown',
    phone         VARCHAR(20) NOT NULL,
    email         VARCHAR(100),
    address       TEXT,
    emergency_contact_name  VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    assigned_room INT,
    admission_status ENUM('Outpatient','Inpatient','Discharged') DEFAULT 'Outpatient',
    admitted_at   TIMESTAMP NULL,
    discharged_at TIMESTAMP NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_room) REFERENCES rooms(room_id) ON DELETE SET NULL
);

-- ─────────────────────────────────────────────
--  4. APPOINTMENTS
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id   INT AUTO_INCREMENT PRIMARY KEY,
    patient_id       INT NOT NULL,
    doctor_id        INT NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    reason           VARCHAR(255),
    status           ENUM('Scheduled','Completed','Cancelled','No-Show') DEFAULT 'Scheduled',
    notes            TEXT,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(doctor_id)  ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  5. PHARMACY / MEDICINE
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id   INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(150) NOT NULL,
    category      ENUM('Tablet','Syrup','Injection','Capsule','Cream','Drops','Other') NOT NULL,
    manufacturer  VARCHAR(100),
    unit_price    DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    stock_qty     INT NOT NULL DEFAULT 0,
    reorder_level INT NOT NULL DEFAULT 10,
    expiry_date   DATE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id      INT NOT NULL,
    doctor_id       INT NOT NULL,
    medicine_id     INT NOT NULL,
    dosage          VARCHAR(100),
    duration_days   INT DEFAULT 7,
    quantity        INT NOT NULL DEFAULT 1,
    prescribed_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id)  REFERENCES patients(patient_id)  ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)   REFERENCES doctors(doctor_id)    ON DELETE CASCADE,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  6. BILLING
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS bills (
    bill_id           INT AUTO_INCREMENT PRIMARY KEY,
    patient_id        INT NOT NULL,
    consultation_fee  DECIMAL(10,2) DEFAULT 0.00,
    room_charges      DECIMAL(10,2) DEFAULT 0.00,
    medicine_charges  DECIMAL(10,2) DEFAULT 0.00,
    test_charges      DECIMAL(10,2) DEFAULT 0.00,
    other_charges     DECIMAL(10,2) DEFAULT 0.00,
    total_amount      DECIMAL(10,2) DEFAULT 0.00,
    paid_amount       DECIMAL(10,2) DEFAULT 0.00,
    payment_status    ENUM('Pending','Partial','Paid') DEFAULT 'Pending',
    payment_method    ENUM('Cash','Card','Online','Insurance') DEFAULT 'Cash',
    bill_date         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE
);

-- ─────────────────────────────────────────────
--  SEED DATA (Sample Records)
-- ─────────────────────────────────────────────

-- Wards
INSERT INTO wards (ward_name, ward_type, total_beds, available_beds, floor_number) VALUES
('General Ward A',   'General',    20, 15, 1),
('ICU',              'ICU',         10,  8, 2),
('Emergency Ward',   'Emergency',   15, 10, 1),
('Maternity Ward',   'Maternity',   12, 10, 3),
('Cardiology Ward',  'Cardiology',  10,  7, 2);

-- Rooms
INSERT INTO rooms (ward_id, room_number, room_type, status, daily_charge) VALUES
(1, '101', 'General', 'Available', 800.00),
(1, '102', 'Double',  'Available', 1200.00),
(1, '103', 'Single',  'Occupied',  2000.00),
(2, '201', 'Single',  'Available', 5000.00),
(2, '202', 'Single',  'Occupied',  5000.00),
(3, '301', 'General', 'Available', 1500.00),
(4, '401', 'Single',  'Available', 2500.00),
(5, '501', 'Single',  'Available', 3000.00);

-- Doctors
INSERT INTO doctors (first_name, last_name, specialization, phone, email, qualification, experience_years, consultation_fee, joined_date) VALUES
('Ahmed',   'Khan',    'Cardiology',       '0300-1234567', 'ahmed.khan@hospital.com',    'MBBS, MD Cardiology',  15, 1500.00, '2010-03-15'),
('Sara',    'Ahmed',   'Gynecology',       '0301-2345678', 'sara.ahmed@hospital.com',    'MBBS, FCPS Gynae',     12, 1200.00, '2012-06-01'),
('Usman',   'Ali',     'Orthopedics',      '0302-3456789', 'usman.ali@hospital.com',     'MBBS, MS Ortho',       10, 1300.00, '2014-01-10'),
('Fatima',  'Malik',   'Pediatrics',       '0303-4567890', 'fatima.malik@hospital.com',  'MBBS, FCPS Pediatrics', 8, 1000.00, '2016-09-20'),
('Hassan',  'Raza',    'General Surgery',  '0304-5678901', 'hassan.raza@hospital.com',   'MBBS, FRCS',           20, 2000.00, '2004-11-05'),
('Ayesha',  'Siddiqui','Neurology',        '0305-6789012', 'ayesha.s@hospital.com',      'MBBS, MD Neurology',   11, 1800.00, '2013-04-22');

-- Patients
INSERT INTO patients (first_name, last_name, dob, gender, blood_group, phone, address, admission_status) VALUES
('Muhammad', 'Tariq',   '1985-04-12', 'Male',   'B+', '0311-1111111', 'House 12, Block A, Sukkur', 'Outpatient'),
('Zainab',   'Hussain', '1992-07-23', 'Female', 'A+', '0312-2222222', 'Street 5, Rohri',           'Inpatient'),
('Ali',      'Hassan',  '1970-01-30', 'Male',   'O+', '0313-3333333', 'Flat 3, Model Colony',      'Outpatient'),
('Sana',     'Bibi',    '2000-11-15', 'Female', 'AB+','0314-4444444', 'Village Pano Aqil',         'Discharged'),
('Imran',    'Shaikh',  '1988-08-08', 'Male',   'B-', '0315-5555555', 'Kotri Road, Sukkur',        'Inpatient');

-- Medicines
INSERT INTO medicines (name, category, manufacturer, unit_price, stock_qty, reorder_level, expiry_date) VALUES
('Paracetamol 500mg', 'Tablet',    'GSK',         5.00,  500, 50, '2026-12-31'),
('Amoxicillin 250mg', 'Capsule',   'Pfizer',      15.00, 300, 30, '2026-06-30'),
('ORS Sachet',        'Other',     'Oralife',      8.00, 200, 20, '2026-09-30'),
('Insulin 100IU',     'Injection', 'Novo Nordisk', 350.00, 100, 10, '2025-12-31'),
('Azithromycin Syrup','Syrup',     'Abbott',       95.00,  80, 15, '2026-03-31'),
('Omeprazole 20mg',   'Capsule',   'Hilton Pharma',12.00, 250, 25, '2027-01-31'),
('Metformin 500mg',   'Tablet',    'ICI',          8.00,  400, 40, '2026-11-30');
