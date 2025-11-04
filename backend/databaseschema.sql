-- Solar Panel Site Analyzer - Database Schema
-- MySQL Database Setup Script

-- Create database
CREATE DATABASE IF NOT EXISTS solar_site_analyzer;
USE solar_site_analyzer;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS analysis_results;
DROP TABLE IF EXISTS sites;
DROP TABLE IF EXISTS analysis_parameters;

-- Sites table: Stores spatial data for potential solar panel installation sites
CREATE TABLE sites (
    site_id INT PRIMARY KEY AUTO_INCREMENT,
    site_name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    area_sqm INT NOT NULL,
    solar_irradiance_kwh DECIMAL(4, 2) NOT NULL COMMENT 'Average daily solar irradiance in kWh/m²/day',
    grid_distance_km DECIMAL(5, 2) NOT NULL COMMENT 'Distance to nearest power grid in kilometers',
    slope_degrees DECIMAL(4, 2) NOT NULL COMMENT 'Terrain slope in degrees',
    road_distance_km DECIMAL(5, 2) NOT NULL COMMENT 'Distance to nearest road in kilometers',
    elevation_m INT NOT NULL COMMENT 'Elevation above sea level in meters',
    land_type VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_latitude (latitude),
    INDEX idx_longitude (longitude),
    INDEX idx_region (region),
    INDEX idx_land_type (land_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Analysis Parameters table: Stores configurable weights for suitability calculation
CREATE TABLE analysis_parameters (
    param_id INT PRIMARY KEY AUTO_INCREMENT,
    parameter_name VARCHAR(100) NOT NULL UNIQUE,
    weight_value DECIMAL(4, 3) NOT NULL COMMENT 'Weight value between 0 and 1',
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (weight_value >= 0 AND weight_value <= 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Analysis Results table: Stores calculated suitability scores
CREATE TABLE analysis_results (
    result_id INT PRIMARY KEY AUTO_INCREMENT,
    site_id INT NOT NULL,
    solar_irradiance_score DECIMAL(5, 2) NOT NULL,
    area_score DECIMAL(5, 2) NOT NULL,
    grid_distance_score DECIMAL(5, 2) NOT NULL,
    slope_score DECIMAL(5, 2) NOT NULL,
    infrastructure_score DECIMAL(5, 2) NOT NULL,
    total_suitability_score DECIMAL(5, 2) NOT NULL COMMENT 'Final weighted score out of 100',
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parameters_snapshot JSON COMMENT 'JSON snapshot of weights used for this analysis',
    FOREIGN KEY (site_id) REFERENCES sites(site_id) ON DELETE CASCADE,
    INDEX idx_total_score (total_suitability_score),
    INDEX idx_site_id (site_id),
    INDEX idx_analysis_timestamp (analysis_timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default analysis parameters (weights)
INSERT INTO analysis_parameters (parameter_name, weight_value, description, is_active) VALUES
('solar_irradiance_weight', 0.35, 'Weight for solar irradiance in suitability calculation', TRUE),
('area_weight', 0.25, 'Weight for available land area in suitability calculation', TRUE),
('grid_distance_weight', 0.20, 'Weight for distance to power grid in suitability calculation', TRUE),
('slope_weight', 0.15, 'Weight for terrain slope in suitability calculation', TRUE),
('infrastructure_weight', 0.05, 'Weight for road/infrastructure proximity in suitability calculation', TRUE);

-- Create a view for easy access to sites with latest analysis results
CREATE OR REPLACE VIEW sites_with_scores AS
SELECT 
    s.site_id,
    s.site_name,
    s.latitude,
    s.longitude,
    s.area_sqm,
    s.solar_irradiance_kwh,
    s.grid_distance_km,
    s.slope_degrees,
    s.road_distance_km,
    s.elevation_m,
    s.land_type,
    s.region,
    ar.solar_irradiance_score,
    ar.area_score,
    ar.grid_distance_score,
    ar.slope_score,
    ar.infrastructure_score,
    ar.total_suitability_score,
    ar.analysis_timestamp
FROM sites s
LEFT JOIN (
    SELECT site_id, 
           solar_irradiance_score,
           area_score,
           grid_distance_score,
           slope_score,
           infrastructure_score,
           total_suitability_score,
           analysis_timestamp,
           ROW_NUMBER() OVER (PARTITION BY site_id ORDER BY analysis_timestamp DESC) as rn
    FROM analysis_results
) ar ON s.site_id = ar.site_id AND ar.rn = 1;

-- Create stored procedure for calculating individual scores
DELIMITER //

CREATE PROCEDURE calculate_suitability_scores()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_site_id INT;
    DECLARE v_solar_irr DECIMAL(4, 2);
    DECLARE v_area INT;
    DECLARE v_grid_dist DECIMAL(5, 2);
    DECLARE v_slope DECIMAL(4, 2);
    DECLARE v_road_dist DECIMAL(5, 2);
    
    DECLARE v_solar_score DECIMAL(5, 2);
    DECLARE v_area_score DECIMAL(5, 2);
    DECLARE v_grid_score DECIMAL(5, 2);
    DECLARE v_slope_score DECIMAL(5, 2);
    DECLARE v_infra_score DECIMAL(5, 2);
    DECLARE v_total_score DECIMAL(5, 2);
    
    DECLARE v_solar_weight DECIMAL(4, 3);
    DECLARE v_area_weight DECIMAL(4, 3);
    DECLARE v_grid_weight DECIMAL(4, 3);
    DECLARE v_slope_weight DECIMAL(4, 3);
    DECLARE v_infra_weight DECIMAL(4, 3);
    
    DECLARE site_cursor CURSOR FOR 
        SELECT site_id, solar_irradiance_kwh, area_sqm, grid_distance_km, 
               slope_degrees, road_distance_km 
        FROM sites;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    -- Get current weights
    SELECT weight_value INTO v_solar_weight FROM analysis_parameters WHERE parameter_name = 'solar_irradiance_weight';
    SELECT weight_value INTO v_area_weight FROM analysis_parameters WHERE parameter_name = 'area_weight';
    SELECT weight_value INTO v_grid_weight FROM analysis_parameters WHERE parameter_name = 'grid_distance_weight';
    SELECT weight_value INTO v_slope_weight FROM analysis_parameters WHERE parameter_name = 'slope_weight';
    SELECT weight_value INTO v_infra_weight FROM analysis_parameters WHERE parameter_name = 'infrastructure_weight';
    
    OPEN site_cursor;
    
    read_loop: LOOP
        FETCH site_cursor INTO v_site_id, v_solar_irr, v_area, v_grid_dist, v_slope, v_road_dist;
        
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Calculate solar irradiance score (0-100)
        SET v_solar_score = CASE
            WHEN v_solar_irr >= 5.5 THEN 100
            WHEN v_solar_irr < 3.0 THEN 0
            ELSE ((v_solar_irr - 3.0) / 2.5) * 100
        END;
        
        -- Calculate area score (0-100)
        SET v_area_score = CASE
            WHEN v_area >= 50000 THEN 100
            WHEN v_area < 5000 THEN 0
            ELSE ((v_area - 5000) / 45000) * 100
        END;
        
        -- Calculate grid distance score (0-100, inverse relationship)
        SET v_grid_score = CASE
            WHEN v_grid_dist <= 1 THEN 100
            WHEN v_grid_dist >= 20 THEN 0
            ELSE 100 - ((v_grid_dist - 1) / 19) * 100
        END;
        
        -- Calculate slope score (0-100)
        SET v_slope_score = CASE
            WHEN v_slope <= 5 THEN 100
            WHEN v_slope > 20 THEN 0
            WHEN v_slope <= 15 THEN 100 - ((v_slope - 5) / 10) * 50
            ELSE 50 - ((v_slope - 15) / 5) * 50
        END;
        
        -- Calculate infrastructure score (0-100, based on road proximity)
        SET v_infra_score = CASE
            WHEN v_road_dist <= 0.5 THEN 100
            WHEN v_road_dist >= 5 THEN 0
            ELSE 100 - ((v_road_dist - 0.5) / 4.5) * 100
        END;
        
        -- Calculate total weighted score
        SET v_total_score = (
            v_solar_score * v_solar_weight +
            v_area_score * v_area_weight +
            v_grid_score * v_grid_weight +
            v_slope_score * v_slope_weight +
            v_infra_score * v_infra_weight
        );
        
        -- Insert results
        INSERT INTO analysis_results (
            site_id, 
            solar_irradiance_score, 
            area_score, 
            grid_distance_score, 
            slope_score, 
            infrastructure_score, 
            total_suitability_score,
            parameters_snapshot
        ) VALUES (
            v_site_id,
            v_solar_score,
            v_area_score,
            v_grid_score,
            v_slope_score,
            v_infra_score,
            v_total_score,
            JSON_OBJECT(
                'solar_weight', v_solar_weight,
                'area_weight', v_area_weight,
                'grid_weight', v_grid_weight,
                'slope_weight', v_slope_weight,
                'infra_weight', v_infra_weight
            )
        );
        
    END LOOP;
    
    CLOSE site_cursor;
END //

DELIMITER ;

-- Create function to get site rank by score
DELIMITER //

CREATE FUNCTION get_site_rank(p_site_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_rank INT;
    
    SELECT COUNT(*) + 1 INTO v_rank
    FROM (
        SELECT site_id, total_suitability_score
        FROM analysis_results ar1
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) 
            FROM analysis_results ar2 
            WHERE ar2.site_id = ar1.site_id
        )
    ) latest_scores
    WHERE total_suitability_score > (
        SELECT total_suitability_score
        FROM analysis_results
        WHERE site_id = p_site_id
        ORDER BY analysis_timestamp DESC
        LIMIT 1
    );
    
    RETURN v_rank;
END //

DELIMITER ;

-- Sample queries for testing

-- Query 1: Get top 10 sites by suitability score
-- SELECT * FROM sites_with_scores ORDER BY total_suitability_score DESC LIMIT 10;

-- Query 2: Get sites within a specific region with score > 70
-- SELECT * FROM sites_with_scores WHERE region = 'Tamil Nadu' AND total_suitability_score > 70;

-- Query 3: Get statistical summary
-- SELECT 
--     COUNT(*) as total_sites,
--     AVG(total_suitability_score) as avg_score,
--     MIN(total_suitability_score) as min_score,
--     MAX(total_suitability_score) as max_score,
--     STDDEV(total_suitability_score) as std_dev
-- FROM sites_with_scores;

-- Query 4: Get score distribution by land type
-- SELECT 
--     land_type,
--     COUNT(*) as site_count,
--     AVG(total_suitability_score) as avg_score,
--     MAX(total_suitability_score) as max_score
-- FROM sites_with_scores
-- GROUP BY land_type
-- ORDER BY avg_score DESC;
