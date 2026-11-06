-- ========================================================================
-- IIT Delhi Virtual Labs - Smart Feedback Portal
-- Database Schema for MySQL 8.0+ / MariaDB 10.4+
-- ========================================================================

CREATE DATABASE IF NOT EXISTS iitd_feedback 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE iitd_feedback;

-- Drop table if exists during fresh setups
DROP TABLE IF EXISTS virtual_labs_feedback;

CREATE TABLE virtual_labs_feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    reference_id VARCHAR(32) NOT NULL UNIQUE,
    full_name VARCHAR(150) NULL,
    email VARCHAR(150) NULL,
    mobile_number VARCHAR(30) NULL,
    user_type ENUM('Student', 'Faculty', 'Researcher', 'Other') NOT NULL DEFAULT 'Student',
    subject VARCHAR(100) NOT NULL,
    experiment_name VARCHAR(255) NOT NULL,
    experiment_url VARCHAR(500) NULL,
    device ENUM('Desktop', 'Laptop', 'Tablet', 'Mobile') NOT NULL DEFAULT 'Laptop',
    browser VARCHAR(50) NOT NULL DEFAULT 'Chrome',
    overall_rating TINYINT UNSIGNED NOT NULL CHECK (overall_rating BETWEEN 1 AND 5),
    experiment_rating TINYINT UNSIGNED NOT NULL CHECK (experiment_rating BETWEEN 1 AND 5),
    navigation_rating TINYINT UNSIGNED NOT NULL CHECK (navigation_rating BETWEEN 1 AND 5),
    technical_rating TINYINT UNSIGNED NOT NULL CHECK (technical_rating BETWEEN 1 AND 5),
    selected_issues JSON NULL COMMENT 'Array of selected issue descriptions',
    technical_details TEXT NULL COMMENT 'Smart conditional details for technical problems',
    experience_description TEXT NOT NULL,
    positive_experience TEXT NULL,
    improvement_suggestions TEXT NULL,
    recommendation ENUM('Yes', 'No', 'Maybe') NOT NULL DEFAULT 'Yes',
    anonymous_status TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 if anonymous, 0 otherwise',
    screenshot_paths JSON NULL COMMENT 'Array of stored screenshot filenames/paths',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_reference (reference_id),
    INDEX idx_subject (subject),
    INDEX idx_overall_rating (overall_rating),
    INDEX idx_created_at (created_at),
    INDEX idx_user_type (user_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================================================
-- Demonstration Sample Data (Clearly identified as demo records)
-- ========================================================================

INSERT INTO virtual_labs_feedback (
    reference_id, full_name, email, mobile_number, user_type,
    subject, experiment_name, experiment_url, device, browser,
    overall_rating, experiment_rating, navigation_rating, technical_rating,
    selected_issues, technical_details, experience_description,
    positive_experience, improvement_suggestions, recommendation,
    anonymous_status, screenshot_paths, created_at
) VALUES 
(
    'IITD-VL-2026-DEMO01',
    'Aarav Sharma',
    'aarav.sharma@example.edu',
    '+91 9876543210',
    'Student',
    'Computer Science',
    'Binary Search Tree Visualization',
    'https://vlabs.iitd.ac.in/cse/bst',
    'Laptop',
    'Chrome',
    5, 5, 4, 5,
    '[]',
    NULL,
    'The step-by-step traversal animation helped clarify node rotation concepts exceptionally well before our semester midterms.',
    'Clear visual representation of node balancing and re-coloring.',
    'Add an option to export step trace as PDF.',
    'Yes',
    0,
    '[]',
    NOW() - INTERVAL 3 DAY
),
(
    'IITD-VL-2026-DEMO02',
    'Prof. Sunita Raman',
    's.raman@iitd.ac.in',
    '+91 9811122334',
    'Faculty',
    'Electrical Engineering',
    'Three-Phase Induction Motor Speed Control',
    'https://vlabs.iitd.ac.in/ee/induction-motor',
    'Desktop',
    'Firefox',
    4, 4, 3, 4,
    '["Simulation is not working", "Mobile responsiveness problem"]',
    'V/f controller slider lagged during peak load setting.',
    'Conducted virtual practical sessions with 70 undergraduates. The waveform analysis matched real laboratory dyno readings closely.',
    'Real-time oscillogram plotting is accurate.',
    'Make slider controls easier to manipulate on touch displays.',
    'Yes',
    0,
    '[]',
    NOW() - INTERVAL 2 DAY
),
(
    'IITD-VL-2026-DEMO03',
    NULL,
    NULL,
    NULL,
    'Researcher',
    'Physics',
    'Michelson Interferometer Fringe Analysis',
    'https://vlabs.iitd.ac.in/phy/interferometer',
    'Laptop',
    'Edge',
    3, 3, 4, 2,
    '["Website is loading slowly", "Display or layout issues"]',
    'Canvas WebGL context lost after 10 minutes of inactivity.',
    'The monochromatic light fringe shifts were mathematically consistent, but the simulation crashed when toggling sodium D-lines.',
    'Good theoretical background notes included in the tab.',
    'Optimize WebGL canvas memory usage for older graphics drivers.',
    'Maybe',
    1,
    '[]',
    NOW() - INTERVAL 1 DAY
);

